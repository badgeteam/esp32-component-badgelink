#!/usr/bin/env python3

from badgelink_pb2 import *
from serial import Serial, SerialException
from cobs import cobs
from zlib import crc32
from device import BadgeUSB
from usb import USBError
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from typing import BinaryIO
import struct, time, os, sys, random


nvs_untypes = {
    NvsValueUint8: 'u8',
    NvsValueInt8: 'i8',
    NvsValueUint16: 'u16',
    NvsValueInt16: 'i16',
    NvsValueUint32: 'u32',
    NvsValueInt32: 'i32',
    NvsValueUint64: 'u64',
    NvsValueInt64: 'i64',
    NvsValueString: 'string',
    NvsValueBlob: 'blob',
}

nvs_types = {
    'u8': NvsValueUint8,
    'i8': NvsValueInt8,
    'u16': NvsValueUint16,
    'i16': NvsValueInt16,
    'u32': NvsValueUint32,
    'i32': NvsValueInt32,
    'u64': NvsValueUint64,
    'i64': NvsValueInt64,
    'str': NvsValueString,
    'string': NvsValueString,
    'blob': NvsValueBlob,
    'bytes': NvsValueBlob,
}


class BadgelinkError(Exception):
    """
    Superclass of all errors raised by Badgelink.
    """
    def __init__(self, *args):
        super().__init__(*args)

class BadgeError(BadgelinkError):
    """
    Superclass of errors raised by the badge.
    """
    def __init__(self, code: StatusCode, msg: str):
        self.code = code
        super().__init__(msg)

class CommunicationError(BadgelinkError):
    """
    Raised if some communications breakdown occurs, including:
    - CRC32 checksum mismatch;
    - Frame is impossibly short.
    """
    def __init__(self, reason):
        super().__init__(reason)

class DisconnectedError(BadgelinkError):
    """
    Raised if the badge has been disconnected and a request is made.
    """
    def __init__(self):
        super().__init__("Disconnected")

class MalformedResponseError(BadgelinkError):
    """
    Raised by the host when the response is malformed.
    """
    def __init__(self, reason: str = None):
        if reason != None:
            super().__init__("Malformed response: " + str(reason))
        else:
            super().__init__("Malformed response")

class MalformedRequestError(BadgeError):
    """
    Raised by the badge when the request is malformed.
    """
    def __init__(self):
        super().__init__(StatusCode.StatusMalformed, "Malformed request")

class BadgeInternalError(BadgeError):
    """
    Raised by the badge on internal error.
    """
    def __init__(self):
        super().__init__(StatusCode.StatusInternalError, "Badge internal error")

class NotSupportedError(BadgeError):
    """
    Raised by the badge if an unsupported request is made.
    """
    def __init__(self):
        super().__init__(StatusCode.StatusNotSupported, "Request not supported")

class NotFoundError(BadgeError):
    """
    Raised by the badge if a request requires something that was not found.
    """
    def __init__(self, thing: str = None):
        super().__init__(StatusCode.StatusNotFound, f"{thing or "Requested file/resource"} not found")

class IllegalStateError(BadgeError):
    """
    Raised by the badge if a request is illegal in the current state.
    """
    def __init__(self):
        super().__init__(StatusCode.StatusNotFound, "Illegal state")

class NoSpaceError(BadgeError):
    """
    Raised by the badge if out of FLASH space.
    """
    def __init__(self):
        super().__init__(StatusCode.StatusNoSpace, "Out of FLASH space")

class NotEmptyError(BadgeError):
    """
    Raised by the badge if a directory is not empty when the `FsActionRmdir` is used.
    """
    def __init__(self):
        super().__init__(StatusCode.StatusNotEmpty, "Directory not empty")

class IsFileError(BadgeError):
    """
    Raised by the badge if a directory operation is performed on a file.
    """
    def __init__(self):
        super().__init__(StatusCode.StatusIsFile, "Is a file")

class IsDirError(BadgeError):
    """
    Raised by the badge if a file operation is performed on a directory.
    """
    def __init__(self):
        super().__init__(StatusCode.StatusIsDir, "Is a directory")

class ExistsError(BadgeError):
    """
    Raised by the badge if a file or directory already exists.
    """
    def __init__(self):
        super().__init__(StatusCode.StatusExists, "File/directory already exists")


class DualPipeConnection:
    def __init__(self, infd: BinaryIO, outfd: BinaryIO):
        self.infd  = infd
        self.outfd = outfd
    
    def flush(self):
        self.outfd.flush()

    def write(self, data: bytes):
        self.outfd.write(data)

    def read_all(self) -> bytes:
        return self.infd.read()


class BadgelinkConnection:
    """
    Helper class that deals with sending and receiving packets over Badgelink.
    """
    
    def __init__(self, conn: Serial|BadgeUSB|DualPipeConnection):
        # Underlying serial bus connection.
        self.conn       = conn
        # Received data buffer.
        self.rxbuf      = b""
        # Serial number counter for requests.
        self.serial_no  = 0
        # Do not dump raw bytes by default.
        self.dump_raw   = False
        
        # Send a zero byte to deliminate from any previous data the badge might have seen.
        self.conn.write(b'\0')
        self.conn.flush()
        # Discard all the bytes previously sent by the badge.
        self.conn.read_all()
        
        # Send the initial sync packet.
        self.sync()
    
    def sync(self, tries = 3):
        """
        Synchronize the serial number between the host and badge.
        """
        self.serial_no = random.randint(0, (1 << 32) - 1)
        last_err = None
        
        for _ in range(tries):
            self.send_packet(Packet(serial=self.serial_no, sync=True))
            try:
                sync_resp = self.recv_packet(0.5)
                if not sync_resp.sync or sync_resp.serial != self.serial_no:
                    raise CommunicationError("Invalid sync")
                return
            except TimeoutError as e:
                last_err = e
        
        raise last_err
    
    def send_frame(self, payload: bytes):
        """
        Encode and send a Badgelink frame.
        
        Raises an error if:
        - `DisconnectedError` if the badge has been disconnected.
        """
        ecc = struct.pack("<I", crc32(payload) & 0xffffffff)
        if self.dump_raw:
            print("TX payload: " + (payload + ecc).hex(' '))
            print("TX frame: " + cobs.encode(payload + ecc).hex(' '))
        try:
            self.conn.write(cobs.encode(payload + ecc))
            self.conn.write(b'\0')
            self.conn.flush()
        except SerialException:
            raise DisconnectedError()
        except USBError:
            raise DisconnectedError()
    
    def send_packet(self, packet: Packet):
        """
        Encode and send a single packet to the badge.
        
        Raises an error if:
        - `ValueError` if the packet is malformed or contains strings that are too long;
        - `DisconnectedError` if the badge has been disconnected.
        """
        self.send_frame(packet.SerializeToString())
    
    def recv_frame(self, timeout = 3) -> bytes:
        """
        Wait to receive a single Badgelink frame.
        
        Raises an error if:
        - `TimeoutError` if the timeout expired;
        - `CommunicationError` if the frame is too short, COBS decoding failed or the CRC32 is incorrect;
        - `DisconnectedError` if the badge has been disconnected.
        """
        # Wait for a frame to be received.
        timeout += time.time()
        while time.time() < timeout:
            self.rxbuf += self.conn.read_all()
            zero = self.rxbuf.find(b'\0')
            if zero != -1:
                break
        if zero == -1:
            raise TimeoutError("Receive timed out")
        buffer = self.rxbuf[:zero]
        self.rxbuf = self.rxbuf[zero+1:]
        
        if self.dump_raw:
            print("RX frame: " + buffer.hex(' '))
        
        # Try to decode the frame.
        if len(buffer) < 7:
            raise CommunicationError("Frame is too short")
        try:
            buffer = cobs.decode(buffer)
        except cobs.DecodeError:
            raise CommunicationError("Failed to decode COBS")
        payload = buffer[:-4]
        
        if self.dump_raw:
            print("RX payload: " + buffer.hex(' '))
        
        # Check the frame's CRC32 checksum.
        ecc_msg    = struct.unpack("<I", buffer[-4:])[0] & 0xffffffff
        ecc_calc   = crc32(payload)
        if ecc_msg != ecc_calc:
            raise CommunicationError(f"CRC32 mismatch; received 0x{ecc_msg:08x}, calculated 0x{ecc_calc:08x}")
        
        return payload
    
    def recv_packet(self, timeout = 3) -> Packet:
        """
        Wait to receive a single packet.
        
        Raises an error if:
        - `TimeoutError` if the timeout expired;
        - `CommunicationError` if the frame is too short, COBS decoding failed or the CRC32 is incorrect;
        - `DisconnectedError` if the badge has been disconnected.
        """
        payload = self.recv_frame(timeout)
        packet = Packet()
        packet.ParseFromString(payload)
        return packet
    
    def simple_request(self, request: Request|FsActionReq|AppfsActionReq|NvsActionReq|Chunk, to_find: str = None, timeout = 1, tries = 3) -> Response:
        """
        Perform a simple request; send one request packet and wait for its response.
        Returns the response data on success.
        
        Raises an error if:
        - `MalformedResponseError` if the response is missing;
        - `BadgeInternalError` if the badge indicated an internal error;
        - `MalformedRequestError` if (the badge indicated that) the request was malformed;
        - `NotSupportedError` if the badge indicated it doesn't support the request;
        - `NotFoundError` if the badge indicated it couldn't find the resource.
        
        If `to_find` is not `None` when `NotFoundError` is raised, the exception message will report `to_find` as the thing that was not found.
        """
        
        # Implicitly convert request type.
        if type(request) == FsActionReq:
            request = Request(fs_action=request)
        elif type(request) == AppfsActionReq:
            request = Request(appfs_action=request)
        elif type(request) == NvsActionReq:
            request = Request(nvs_action=request)
        elif type(request) == Chunk:
            request = Request(upload_chunk=request)
        elif type(request) == StartAppReq:
            request = Request(start_app=request)
        elif type(request) != Request:
            raise TypeError("Invalid request type")
        
        # Send request packet and wait for response.
        self.serial_no = (self.serial_no + 1) % (1 << 32)
        last_err = None
        for _ in range(tries):
            req_packet = Packet(request=request, serial=self.serial_no)
            self.send_packet(req_packet)
            try:
                resp_packet = self.recv_packet(timeout)
                if resp_packet.sync:
                    self.sync()
                else:
                    last_err = None
                    break
            except TimeoutError as e:
                last_err = e
        
        if last_err:
            raise last_err
        
        # Check for response error conditions.
        if req_packet.serial != resp_packet.serial:
            raise CommunicationError(f"Serial mismatch; received {resp_packet.serial}, expected {req_packet.serial}")
        elif not resp_packet.response:
            raise MalformedResponseError("Packet is missing response")
        match resp_packet.response.status_code:
            case StatusCode.StatusOk: pass
            case StatusCode.StatusInternalError: raise BadgeInternalError()
            case StatusCode.StatusMalformed: raise MalformedRequestError()
            case StatusCode.StatusNotSupported: raise NotSupportedError()
            case StatusCode.StatusNotFound: raise NotFoundError(to_find)
            case StatusCode.StatusIllegalState: raise IllegalStateError()
            case StatusCode.StatusNoSpace: raise NoSpaceError()
            case StatusCode.StatusNotEmpty: raise NotEmptyError()
            case StatusCode.StatusIsFile: raise IsFileError()
            case StatusCode.StatusIsDir: raise IsDirError()
            case StatusCode.StatusExists: raise ExistsError()
            
        return resp_packet.response


class Badgelink:
    CHUNK_MAX_SIZE = 4096
    
    def __init__(self, conn: BadgelinkConnection|BadgeUSB|Serial):
        if type(conn) != BadgelinkConnection:
            conn = BadgelinkConnection(conn)
        self.conn = conn
        self.def_timeout = 0.25
        self.chunk_timeout = 0.5
        self.xfer_timeout = 10
    
    def start_app(self, slug: str, app_arg: str):
        """
        Start an app that is installed on the badge.
        
        Raises `NotFoundError` if the requested app does not exist.
        """
        self.conn.simple_request(StartAppReq(slug=slug, arg=app_arg), f"App `{slug}`", timeout=self.def_timeout)
    
    def nvs_read(self, namespace: str, key: str, nvs_type: NvsValueType) -> NvsValue:
        """
        Read a value from the badge's NVS (Non-Volatile Storage).
        
        Raises `ValueError` if `namespace` and/or `key` are longer than 16 bytes.
        """
        if type(namespace) != str:
            namespace = str(namespace)
        if type(key) != str:
            key = str(key)
            
        request = NvsActionReq(type=NvsActionRead, namespc=namespace, key=key, read_type=nvs_type)
        
        return self.conn.simple_request(request, f"{nvs_untypes[nvs_type]} entry {repr(namespace)}:{repr(key)}", timeout=self.def_timeout).nvs_resp.rdata
    
    def nvs_write(self, namespace: str, key: str, wdata: NvsValue):
        """
        Write a value to the badge's NVS (Non-Volatile Storage).
        
        Raises `ValueError` if `namespace` and/or `key` are longer than 16 bytes or if `wdata` is a string or blob longer than 4096 bytes.
        """
        if type(namespace) != str:
            namespace = str(namespace)
        if type(key) != str:
            key = str(key)
        
        request = NvsActionReq(type=NvsActionWrite, namespc=namespace, key=key, wdata=wdata)
        self.conn.simple_request(request, timeout=self.def_timeout)
    
    def nvs_list(self, namespace: str = None) -> list[NvsEntry]:
        """
        List the entries in the badge's NVS (Non-Volatile Storage), optionally filtering by namespace.
        
        Raises `ValueError` if `namespace` is longer than 16 bytes.
        """
        if namespace and type(namespace) != str:
            namespace = str(namespace)
        
        offset = 0
        out = []
        
        while True:
            resp = self.conn.simple_request(NvsActionReq(type=NvsActionList, namespc=namespace, list_offset=offset), timeout=self.def_timeout).nvs_resp
            out += list(resp.entries.entries)
            offset += len(resp.entries.entries)
            if offset >= resp.entries.total_entries:
                break
        
        return out
    
    def nvs_delete(self, namespace: str, key: str) -> bool:
        """
        Delete a key/value pair from the badge's NVS (Non-Volatile Storage).
        
        Raises `ValueError` if `namespace` and/or `key` are longer than 16 bytes.
        """
        if type(namespace) != str:
            namespace = str(namespace)
        if type(key) != str:
            key = str(key)
            
        request = Request(nvs_action=NvsActionReq(type=NvsActionDelete, namespc=namespace, key=key))
        self.conn.simple_request(request, f"NVS entry {repr(namespace)}:{repr(key)}", timeout=self.def_timeout) != None
    
    def appfs_list(self) -> list[AppfsMetadata]:
        """
        List all AppFS files as an array of file descriptors.
        """
        resp = self.conn.simple_request(AppfsActionReq(type=FsActionList))
        all_meta = list(resp.appfs_resp.list.list)
        while len(all_meta) < resp.appfs_resp.list.total_size:
            resp = self.conn.simple_request(AppfsActionReq(type=FsActionList, list_offset=len(all_meta)), timeout=self.def_timeout)
            all_meta += list(resp.appfs_resp.list.list)
        return all_meta
    
    def appfs_stat(self, slug: str) -> AppfsMetadata:
        """
        Get AppFS file metadata.
        
        Raises `NotFoundError` if the file does not exist.
        """
        return self.conn.simple_request(AppfsActionReq(type=FsActionStat, slug=slug), timeout=self.def_timeout).appfs_resp.metadata
    
    def appfs_crc32(self, slug: str) -> int:
        """
        Get AppFS file CRC32 checksum.
        
        Raises `NotFoundError` if the file does not exist.
        """
        return self.conn.simple_request(AppfsActionReq(type=FsActionCrc23, slug=slug), timeout=self.def_timeout).appfs_resp.crc32
    
    def appfs_delete(self, slug: str):
        """
        Delete an AppFS file.
        
        Raises `NotFoundError` if the file does not exist.
        """
        self.conn.simple_request(AppfsActionReq(type=FsActionDelete, slug=slug), timeout=self.def_timeout)
    
    def appfs_upload(self, metadata: AppfsMetadata, path: str):
        """
        Upload an AppFS executable.
        """
        with open(path, "rb") as fd:
            # Get size and calculate checksum.
            ecc = 0
            while True:
                chunk = fd.read(1024 * 1024)
                if not len(chunk):
                    break
                ecc = crc32(chunk, ecc)
            size = fd.tell()
            
            # Send initial request.
            metadata.size = size
            print("Erasing...")
            self.conn.simple_request(AppfsActionReq(type=FsActionUpload, metadata=metadata, crc32=ecc), timeout=self.xfer_timeout)
            
            # Initial request succeeded; send remainder of transfer.
            fd.seek(0, os.SEEK_SET)
            progress = -1
            for pos in range(0, size, Badgelink.CHUNK_MAX_SIZE):
                assert pos == fd.tell()
                if self.conn.dump_raw:
                    print(f"Uploading at {pos} ({pos * 100 // size}%)")
                elif pos * 100 // size > progress:
                    progress = pos * 100 // size
                    print(f"\033[1GUploading {progress}%", end='')
                    sys.stdout.flush()
                self.conn.simple_request(Chunk(position=pos, data=fd.read(Badgelink.CHUNK_MAX_SIZE)), timeout=self.chunk_timeout)
            if not self.conn.dump_raw:
                print()
            
            # Finalize the transfer.
            self.conn.simple_request(Request(xfer_ctrl=XferFinish), timeout=self.xfer_timeout)
            print("Done!")
    
    def appfs_download(self, slug: str, path: str):
        """
        Download an AppFS executable.
        """
        with open(path, "wb") as fd:
            # Send initial request.
            meta = self.conn.simple_request(AppfsActionReq(type=FsActionDownload, slug=slug), timeout=self.xfer_timeout).appfs_resp
            
            # Initial request succeeded; receive remainder of transfer.
            fd.seek(0, os.SEEK_SET)
            progress = -1
            pos = 0
            while pos < meta.size:
                assert pos == fd.tell()
                if pos * 100 // meta.size > progress:
                    progress = pos * 100 // meta.size
                    print(f"\033[1GDownloading {progress}%", end='')
                    sys.stdout.flush()
                chunk = self.conn.simple_request(Request(xfer_ctrl=XferContinue), timeout=self.chunk_timeout).download_chunk
                if chunk.position != pos:
                    print()
                    raise MalformedResponseError("Incorrect chunk position")
                fd.write(chunk.data)
                pos += len(chunk.data)
            print()
            
            # Finalize the transfer.
            self.conn.simple_request(Request(xfer_ctrl=XferFinish), timeout=self.def_timeout)
            print("Done!")
    
    def appfs_usage(self) -> FsUsage:
        """
        Get AppFS usage statistics.
        """
        return self.conn.simple_request(AppfsActionReq(type=FsActionGetUsage), timeout=self.def_timeout).appfs_resp.usage

    def fs_list(self, path: str) -> list[FsDirent]:
        """
        List a directory.
        """
        offset = 0
        out = []
        
        while True:
            resp = self.conn.simple_request(FsActionReq(type=FsActionList, path=path, list_offset=offset), timeout=self.chunk_timeout).fs_resp
            out += list(resp.list.list)
            offset += len(resp.list.list)
            if offset >= resp.list.total_size:
                break
        
        return out
    
    def fs_stat(self, path: str) -> FsStat:
        """
        Get file metadata.
        """
        return self.conn.simple_request(FsActionReq(type=FsActionStat, path=path), timeout=self.def_timeout).fs_resp.stat
    
    def fs_crc32(self, path: str) -> int:
        """
        Get the CRC32 checksum of a file on the badge.
        """
        return self.conn.simple_request(FsActionReq(type=FsActionCrc23, path=path), timeout=self.def_timeout).fs_resp.crc32
    
    def fs_delete(self, path: str):
        """
        Delete a file on the badge.
        """
        self.conn.simple_request(FsActionReq(type=FsActionDelete, path=path), timeout=self.def_timeout)
    
    def fs_usage(self) -> FsUsage:
        """
        Get the badge's filesystem usage statistics.
        """
        return self.conn.simple_request(FsActionReq(type=FsActionGetUsage), timeout=self.def_timeout).fs_resp.usage
    
    def fs_upload(self, badge_path: str, host_path: str):
        """
        Upload a file to the badge.
        """
        with open(host_path, "rb") as fd:
            # Get size and calculate checksum.
            ecc = 0
            while True:
                chunk = fd.read(1024 * 1024)
                if not len(chunk):
                    break
                ecc = crc32(chunk, ecc)
            size = fd.tell()
            
            # Send initial request.
            self.conn.simple_request(FsActionReq(type=FsActionUpload, path=badge_path, crc32=ecc, size=size), timeout=self.xfer_timeout)
            
            # Initial request succeeded; send remainder of transfer.
            fd.seek(0, os.SEEK_SET)
            progress = -1
            for pos in range(0, size, Badgelink.CHUNK_MAX_SIZE):
                assert pos == fd.tell()
                if pos * 100 // size > progress:
                    progress = pos * 100 // size
                    print(f"\033[1GUploading {progress}%", end='')
                    sys.stdout.flush()
                self.conn.simple_request(Chunk(position=pos, data=fd.read(Badgelink.CHUNK_MAX_SIZE)), timeout=self.chunk_timeout)
            print()
            
            # Finalize the transfer.
            self.conn.simple_request(Request(xfer_ctrl=XferFinish), timeout=self.xfer_timeout)
            print("Done!")
    
    def fs_download(self, badge_path: str, host_path: str):
        """
        Download a file from the badge.
        """
        with open(host_path, "wb") as fd:
            # Send initial request.
            meta = self.conn.simple_request(FsActionReq(type=FsActionDownload, path=badge_path), timeout=self.xfer_timeout).fs_resp
            
            # Initial request succeeded; receive remainder of transfer.
            fd.seek(0, os.SEEK_SET)
            progress = -1
            pos = 0
            while pos < meta.size:
                assert pos == fd.tell()
                if pos * 100 // meta.size > progress:
                    progress = pos * 100 // meta.size
                    print(f"\033[1GDownloading {progress}%", end='')
                    sys.stdout.flush()
                chunk = self.conn.simple_request(Request(xfer_ctrl=XferContinue), timeout=self.chunk_timeout).download_chunk
                if chunk.position != pos:
                    print()
                    raise MalformedResponseError("Incorrect chunk position")
                fd.write(chunk.data)
                pos += len(chunk.data)
            print()
            
            # Finalize the transfer.
            self.conn.simple_request(Request(xfer_ctrl=XferFinish), timeout=self.xfer_timeout)
            print("Done!")
    
    def fs_mkdir(self, path: str):
        """
        Create a directory on the badge.
        """
        self.conn.simple_request(FsActionReq(type=FsActionMkdir, path=path), timeout=self.def_timeout)
    
    def fs_rmdir(self, path: str):
        """
        Remove a directory on the badge.
        """
        self.conn.simple_request(FsActionReq(type=FsActionRmdir, path=path), timeout=self.def_timeout)


if __name__ == "__main__":
    def todo():
        print("Not supported by this script yet")
        sys.exit(33)
    
    def nvs_ns(val: str):
        if not val:
            raise ArgumentTypeError("NVS namespace/key cannot be empty")
        elif len(val.encode()) > 15:
            raise ArgumentTypeError("NVS namespace/key cannot be longer than 15 bytes")
        elif '\0' in val:
            raise ArgumentTypeError("NVS namespace/key cannot contain null bytes")
        else:
            if not val.isprintable() or ' ' in val:
                print(f"Warning: NVS namespace/key {repr(val)} is suspicious")
            return val
    
    def app_arg(val: str):
        if not val:
            return None
        elif len(val.encode()) > 127:
            raise ArgumentTypeError("App argument cannot be longer than 127 bytes")
        elif '\0' in val:
            raise ArgumentTypeError("App argument cannot contain null bytes")
        else:
            if not val.isprintable() or ' ' in val:
                print(f"Warning: App argument {repr(val)} is suspicious")
            return val
    
    def appfs_slug(val: str):
        if not val:
            raise ArgumentTypeError("AppFS slug cannot be empty")
        elif len(val.encode()) > 47:
            raise ArgumentTypeError("AppFS slug cannot be longer than 47 bytes")
        elif '\0' in val:
            raise ArgumentTypeError("AppFS slug cannot contain null bytes")
        else:
            if not val.isprintable() or ' ' in val:
                print(f"Warning: AppFS slug {repr(val)} is suspicious")
            return val
    
    def appfs_title(val: str):
        if not val:
            raise ArgumentTypeError("AppFS title cannot be empty")
        elif len(val.encode()) > 63:
            raise ArgumentTypeError("AppFS title cannot be longer than 63 bytes")
        elif '\0' in val:
            raise ArgumentTypeError("AppFS title cannot contain null bytes")
        else:
            return val
    
    def appfs_ver(val: str):
        try:
            val = int(val)
            if val < 0 or val > 65535:
                raise ValueError()
            return val
        except ValueError:
            raise ArgumentTypeError("NVS version must be an integer from 0 to 65535")
    
    def fs_path(val: str):
        if '\0' in val:
            raise ArgumentTypeError("File path cannot contain null bytes")
        elif len(val.encode()) > 1023:
            raise ArgumentTypeError("File path cannot exceed 1023 bytes")
        else:
            return val
    
    def parse_nvs_value(type: str, value: str, file: bool) -> NvsValue:
        if nvs_types[type] == NvsValueBlob:
            # Blob / bytes value.
            if file:
                try:
                    fd = open(value, "rb")
                    val = NvsValueBlob(type=NvsValueBlob, blobval=fd.read())
                    fd.close()
                    return val
                except FileNotFoundError as e:
                    print(*e.args)
                    sys.exit(1)
            else:
                return NvsValue(type=NvsValueBlob, blobval=value.encode())
        
        if file:
            # Load from file for non-bytes.
            try:
                fd = open(value, "r")
                value = fd.read()
                fd.close()
            except FileNotFoundError as e:
                print(*e.args)
                sys.exit(1)
        
        if nvs_types[type] == NvsValueString:
            # String values.
            if len(value.encode()) > 4095:
                print("NVS strings can't be longer than 4095 bytes")
                sys.exit(1)
            return NvsValue(type=NvsValueString, stringval=value)
        
        try:
            # Numeric types.
            range = num_ranges[type]
            value = int(value)
            if value < range[0] or value > range[1]:
                raise ValueError()
            return NvsValue(type=nvs_types[type], numericval=value & ((1<<64)-1))
        except ValueError:
            print(f"NVS {type} must be an integer from {range[0]} to {range[1]}")
            sys.exit(1)
    
    def print_table(header: list[str], rows: list[list[str]]):
        max_width = [len(s) for s in header]
        
        # Calculate widths.
        for row in rows:
            for i in range(len(max_width)):
                max_width[i] = max(max_width[i], len(row[i]))
        
        def print_row(row: list[str]):
            print(" | ".join(row[i].ljust(max_width[i]) for i in range(len(row))))
        
        # Print header.
        print_row(header)
        print("-+-".join('-' * max_width[i] for i in range(len(max_width))))
        for row in rows:
            print_row(row)
    
    num_ranges = {
        'u8': (0, 255),
        'i8': (-128, 127),
        'u16': (0, 65535),
        'i16': (-32768, 32767),
        'u32': (0, 4294967295),
        'i32': (-2147483648, 2147483647),
        'u64': (0, 18446744073709551615),
        'i64': (-9223372036854775808, 9223372036854775807),
    }
    
    parser = ArgumentParser(description="Programming an maintenance tool for Badge.Team badges")
    parser.add_argument("--dump-raw-bytes", action="store_true", default=False)
    parser.add_argument("--port", action="store", default=None)
    parser.add_argument("--inpipe", action="store", default=None)
    parser.add_argument("--outpipe", action="store", default=None)
    parser.add_argument("--timeout", action="store", default=0.25, type=float)
    parser.add_argument("--chunk-timeout", action="store", default=0.5, type=float)
    parser.add_argument("--xfer-timeout", action="store", default=10, type=float)
    subparsers = parser.add_subparsers(required=True, dest="request")
    
    # ==== Help texts ==== #
    if 1:
        help_host_file  = "Path to a file on this computer"
        help_badge_file = "Path to a file on the badge"
        
        if 1:
            help_start              = "Start an app that is installed on the badge"
            help_start_slug         = "ID of the app to start"
            help_start_arg          = "Argument to pass to the app being started"
        
        if 1:
            help_nvs                = "Read or write the settings (ESP NVS)"
            help_nvs_read           = "Read a single value"
            help_nvs_read_file      = "Instead of printing, store the read data to this file"
            help_nvs_write          = "Write a single value"
            help_nvs_write_file     = "Interpret `value` as a file, parsing the file's contents"
            help_nvs_write_value    = "The value to write"
            help_nvs_list           = "List all entries or entries in a namespace"
            help_nvs_delete         = "Delete an entry"
            help_nvs_ns             = "Acts like a directory"
            help_nvs_key            = "The name associated with a setting"
            help_nvs_type           = "The type of the setting"
        
        if 1:
            help_appfs              = "Manage AppFS apps"
            help_appfs_list         = "List all AppFS apps"
            help_appfs_stat         = "Show details about an AppFS app"
            help_appfs_crc32        = "Show the CRC32 checksum of an AppFS app"
            help_appfs_delete       = "Delete an AppFS app from the badge"
            help_appfs_upload       = "Upload an AppFS app to the badge"
            help_appfs_download     = "Download an AppFS app from the badge"
            help_appfs_usage        = "Show usage statistics of AppFS"
            help_appfs_slug         = "ID of the AppFS app"
            help_appfs_title        = "Title of the AppFS app"
            help_appfs_version      = "Version number of the AppFS app"
        
        if 1:
            help_fs             = "Manage files on the badge"
            help_fs_list        = "List files in a directory on the badge"
            help_fs_stat        = "Show details about a file/directory on the badge"
            help_fs_crc32       = "Show the CRC32 checksum of a file on the badge"
            help_fs_delete      = "Delete a file from the badge"
            help_fs_mkdir       = "Make a directory on the badge"
            help_fs_rmdir       = "Remove an empty directory from the badge"
            help_fs_upload      = "Upload a file to the badge"
            help_fs_download    = "Download a file from the badge"
            help_fs_usage       = "Show filesystem usage statistics"
    
    # ==== Start app parser ==== #
    if 1:
        p_start = subparsers.add_parser("start", help=help_start)
        p_start.add_argument("slug", type=appfs_slug, help=help_start_slug)
        p_start.add_argument("app_arg", type=app_arg, nargs="?", default="", help=help_start_arg)
    
    # ==== NVS parsers ==== #
    if 1:
        p_nvs = subparsers.add_parser("nvs", help=help_nvs)
        sub_nvs = p_nvs.add_subparsers(required=True, dest="action")
        
        p_nvs_read = sub_nvs.add_parser("read", help=help_nvs_read)
        p_nvs_read.add_argument("namespace", type=nvs_ns)
        p_nvs_read.add_argument("key", type=nvs_ns)
        p_nvs_read.add_argument("type", choices=nvs_types.keys())
        
        p_nvs_write = sub_nvs.add_parser("write", help=help_nvs_write)
        p_nvs_write.add_argument("namespace", type=nvs_ns, help=help_nvs_ns)
        p_nvs_write.add_argument("key", type=nvs_ns, help=help_nvs_key)
        p_nvs_write.add_argument("type", choices=nvs_types.keys(), help=help_nvs_type)
        p_nvs_write.add_argument("value", help=help_nvs_write_value)
        p_nvs_write.add_argument("--file", action="store_true", help=help_nvs_write_file)
        
        p_nvs_list = sub_nvs.add_parser("list", help=help_nvs_list)
        p_nvs_list.add_argument("namespace", type=nvs_ns, nargs='?', help=help_nvs_ns)
        
        p_nvs_delete = sub_nvs.add_parser("delete", help=help_nvs_delete)
        p_nvs_delete.add_argument("namespace", type=nvs_ns, help=help_nvs_ns)
        p_nvs_delete.add_argument("key", type=nvs_ns, help=help_nvs_key)
    
    # ==== AppFS parsers ==== #
    if 1:
        p_appfs = subparsers.add_parser("appfs", help=help_appfs)
        sub_appfs = p_appfs.add_subparsers(required=True, dest="action")
        
        p_appfs_list = sub_appfs.add_parser("list", help=help_appfs_list)
        
        p_appfs_stat = sub_appfs.add_parser("stat", help=help_appfs_stat)
        p_appfs_stat.add_argument("slug", type=appfs_slug, help=help_appfs_slug)
        
        p_appfs_crc32 = sub_appfs.add_parser("crc32", help=help_appfs_crc32)
        p_appfs_crc32.add_argument("slug", type=appfs_slug, help=help_appfs_slug)
        
        p_appfs_delete = sub_appfs.add_parser("delete", help=help_appfs_delete)
        p_appfs_delete.add_argument("slug", type=appfs_slug, help=help_appfs_slug)
        
        p_appfs_upload = sub_appfs.add_parser("upload", help=help_appfs_upload)
        p_appfs_upload.add_argument("slug", type=appfs_slug, help=help_appfs_slug)
        p_appfs_upload.add_argument("title", type=appfs_title, help=help_appfs_title)
        p_appfs_upload.add_argument("version", type=appfs_ver, help=help_appfs_version)
        p_appfs_upload.add_argument("file", help=help_host_file)
        
        p_appfs_download = sub_appfs.add_parser("download", help=help_appfs_download)
        p_appfs_download.add_argument("slug", type=appfs_slug, help=help_appfs_slug)
        p_appfs_download.add_argument("file", help=help_host_file)
        
        p_appfs_usage = sub_appfs.add_parser("usage", help=help_appfs_usage)
    
    # ==== FS parsers ==== #
    if 1:
        p_fs = subparsers.add_parser("fs")
        sub_fs = p_fs.add_subparsers(required=True, dest="action")
        
        p_fs_list = sub_fs.add_parser("list", help=help_fs_list)
        p_fs_list.add_argument("file", type=fs_path, default='/', nargs='?', help=help_badge_file)
        
        p_fs_stat = sub_fs.add_parser("stat", help=help_fs_stat)
        p_fs_stat.add_argument("file", type=fs_path, help=help_badge_file)
        
        # p_fs_crc32 = sub_fs.add_parser("crc32", help=help_fs_crc32)
        # p_fs_crc32.add_argument("file", type=fs_path, help=help_badge_file)
        
        p_fs_delete = sub_fs.add_parser("delete", help=help_fs_delete)
        p_fs_delete.add_argument("file", type=fs_path, help=help_badge_file)
        
        p_fs_mkdir = sub_fs.add_parser("mkdir", help=help_fs_mkdir)
        p_fs_mkdir.add_argument("file", type=fs_path, help=help_badge_file)
        
        p_fs_mkdir = sub_fs.add_parser("rmdir", help=help_fs_rmdir)
        p_fs_mkdir.add_argument("file", type=fs_path, help=help_badge_file)
        
        p_fs_upload = sub_fs.add_parser("upload", help=help_fs_upload)
        p_fs_upload.add_argument("badge_file", type=fs_path, help=help_badge_file)
        p_fs_upload.add_argument("host_file", help=help_host_file)
        
        p_fs_download = sub_fs.add_parser("download", help=help_fs_download)
        p_fs_download.add_argument("badge_file", type=fs_path, help=help_badge_file)
        p_fs_download.add_argument("host_file", help=help_host_file)
        
        # p_fs_usage = sub_fs.add_parser("usage", help=help_fs_usage)
    
    # ==== Implementations ==== #
    args = parser.parse_args()
    
    if args.port != None and (args.inpipe != None or args.outpipe != None):
        print(f"{sys.argv[0]}: error: --port is mutually exclusive with --inpipe, --outpipe")
        sys.exit(1)
    elif args.inpipe != None and args.outpipe == None:
        print(f"{sys.argv[0]}: error: --inpipe without --outpipe")
        sys.exit(1)
    elif args.outpipe != None and args.inpipe == None:
        print(f"{sys.argv[0]}: error: --outpipe without --inpipe")
        sys.exit(1)
    
    try:
        if args.port:
            port = Serial(port=args.port, baudrate=115200)
        elif args.inpipe:
            infd = open(args.inpipe, "rb")
            outfd = open(args.outpipe, "wb")
            os.set_blocking(infd.fileno(), False)
            port = DualPipeConnection(infd, outfd)
        else:
            port = BadgeUSB()
    except FileNotFoundError:
        print("Badge not found")
        sys.exit(1)
    
    try:
        link = Badgelink(port)
        link.conn.dump_raw = args.dump_raw_bytes
        link.def_timeout = args.timeout
        link.chunk_timeout = args.chunk_timeout
        link.xfer_timeout = args.xfer_timeout
        
        if args.request == "start":
            link.start_app(args.slug, args.app_arg)
            
        elif args.request == "nvs":
            # ==== NVS implementations ==== #
            if args.action == "read":
                value = link.nvs_read(args.namespace, args.key, nvs_types[args.type])
                print(value)
                if value.type == NvsValueString:
                    print(repr(value.stringval))
                elif value.type == NvsValueBlob:
                    print(repr(value.blobval))
                elif int(value.type) & 1 and value.numericval & (1 << 63):
                    print(f"{nvs_untypes[value.type]}: -{(((1 << 64) - 1) ^ value.numericval) + 1}")
                else:
                    print(f"{nvs_untypes[value.type]}: {value.numericval}")
                
            elif args.action == "delete":
                link.nvs_delete(args.namespace, args.key)
                
            elif args.action == "write":
                link.nvs_write(args.namespace, args.key, parse_nvs_value(args.type, args.value, args.file))
                
            elif args.action == "list":
                entries = link.nvs_list(args.namespace)
                print_table(["namespace", "key", "type"], [[e.namespc, e.key, nvs_untypes[e.type]] for e in entries])
            
            else:
                todo()
        
        elif args.request == "appfs":
            # ==== AppFS implementations ==== #
            if args.action == "list":
                entries = link.appfs_list()
                if entries:
                    print_table(["slug", "title", "ver", "size"], [[e.slug, e.title, str(e.version), f"{e.size//1024}K"] for e in entries])
            
            elif args.action == "stat":
                metadata = link.appfs_stat(args.slug)
                print(f"Slug:    {metadata.slug}")
                print(f"Title:   {metadata.title}")
                print(f"Version: {metadata.version}")
                print(f"Size:    {metadata.size}")
            
            elif args.action == "crc32":
                print(f"0x{link.appfs_crc32(args.slug):08x}")
            
            elif args.action == "delete":
                link.appfs_delete(args.slug)
            
            elif args.action == "upload":
                link.appfs_upload(AppfsMetadata(slug=args.slug, title=args.title, version=args.version), args.file)
            
            elif args.action == "download":
                link.appfs_download(args.slug, args.file)
            
            elif args.action == "usage":
                usage = link.appfs_usage()
                print(f"Usage: {usage.used//1024}K / {usage.size//1024}K ({usage.used/usage.size*100:.1f}%)")
            
            else:
                todo()
        
        elif args.request == "fs":
            # ==== FS implementations ==== #
            if args.action == "list":
                entries = link.fs_list(args.file)
                if entries:
                    print_table(["type", "path"], [["dir" if e.is_dir else "file", e.name] for e in entries])
            
            elif args.action == "stat":
                stat = link.fs_stat(args.file)
                print(f"Type:     {"directory" if stat.is_dir else "file"}")
                print(f"Size:     {stat.size}")
                print(f"Created:  {datetime.fromtimestamp(stat.ctime / 1000)}")
                print(f"Modified: {datetime.fromtimestamp(stat.mtime / 1000)}")
                print(f"Accessed: {datetime.fromtimestamp(stat.atime / 1000)}")
            
            elif args.action == "crc32":
                print(f"0x{link.fs_crc32(args.file):08x}")
            
            elif args.action == "delete":
                link.fs_delete(args.file)
            
            elif args.action == "mkdir":
                link.fs_mkdir(args.file)
            
            elif args.action == "rmdir":
                link.fs_rmdir(args.file)
            
            elif args.action == "upload":
                link.fs_upload(args.badge_file, args.host_file)
            
            elif args.action == "download":
                link.fs_download(args.badge_file, args.host_file)
            
            elif args.action == "usage":
                todo()
            
            else:
                todo()
        
    except (BadgelinkError, FileNotFoundError) as e:
        print(*e.args)
        sys.exit(1)
