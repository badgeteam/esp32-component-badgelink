from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
FsActionCopy: FsActionType
FsActionCrc23: FsActionType
FsActionDelete: FsActionType
FsActionDownload: FsActionType
FsActionGetUsage: FsActionType
FsActionList: FsActionType
FsActionMkdir: FsActionType
FsActionRename: FsActionType
FsActionRmdir: FsActionType
FsActionStat: FsActionType
FsActionUpload: FsActionType
NvsActionDelete: NvsActionType
NvsActionList: NvsActionType
NvsActionRead: NvsActionType
NvsActionWrite: NvsActionType
NvsValueBlob: NvsValueType
NvsValueInt16: NvsValueType
NvsValueInt32: NvsValueType
NvsValueInt64: NvsValueType
NvsValueInt8: NvsValueType
NvsValueString: NvsValueType
NvsValueUint16: NvsValueType
NvsValueUint32: NvsValueType
NvsValueUint64: NvsValueType
NvsValueUint8: NvsValueType
StatusExists: StatusCode
StatusIllegalState: StatusCode
StatusInternalError: StatusCode
StatusIsDir: StatusCode
StatusIsFile: StatusCode
StatusMalformed: StatusCode
StatusNoSpace: StatusCode
StatusNotEmpty: StatusCode
StatusNotFound: StatusCode
StatusNotSupported: StatusCode
StatusOk: StatusCode
UsbModeDebug: UsbMode
UsbModeDevice: UsbMode
XferAbort: XferReq
XferContinue: XferReq
XferFinish: XferReq

class AppfsActionReq(_message.Message):
    __slots__ = ["crc32", "list_offset", "metadata", "slug", "type"]
    CRC32_FIELD_NUMBER: _ClassVar[int]
    LIST_OFFSET_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    crc32: int
    list_offset: int
    metadata: AppfsMetadata
    slug: str
    type: FsActionType
    def __init__(self, metadata: _Optional[_Union[AppfsMetadata, _Mapping]] = ..., slug: _Optional[str] = ..., type: _Optional[_Union[FsActionType, str]] = ..., crc32: _Optional[int] = ..., list_offset: _Optional[int] = ...) -> None: ...

class AppfsActionResp(_message.Message):
    __slots__ = ["crc32", "list", "metadata", "size", "usage"]
    CRC32_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    crc32: int
    list: AppfsList
    metadata: AppfsMetadata
    size: int
    usage: FsUsage
    def __init__(self, metadata: _Optional[_Union[AppfsMetadata, _Mapping]] = ..., crc32: _Optional[int] = ..., list: _Optional[_Union[AppfsList, _Mapping]] = ..., usage: _Optional[_Union[FsUsage, _Mapping]] = ..., size: _Optional[int] = ...) -> None: ...

class AppfsList(_message.Message):
    __slots__ = ["list", "total_size"]
    LIST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[AppfsMetadata]
    total_size: int
    def __init__(self, list: _Optional[_Iterable[_Union[AppfsMetadata, _Mapping]]] = ..., total_size: _Optional[int] = ...) -> None: ...

class AppfsMetadata(_message.Message):
    __slots__ = ["size", "slug", "title", "version"]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    size: int
    slug: str
    title: str
    version: int
    def __init__(self, slug: _Optional[str] = ..., title: _Optional[str] = ..., version: _Optional[int] = ..., size: _Optional[int] = ...) -> None: ...

class Chunk(_message.Message):
    __slots__ = ["data", "position"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    position: int
    def __init__(self, position: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class FsActionReq(_message.Message):
    __slots__ = ["crc32", "dest_path", "list_offset", "path", "size", "type"]
    CRC32_FIELD_NUMBER: _ClassVar[int]
    DEST_PATH_FIELD_NUMBER: _ClassVar[int]
    LIST_OFFSET_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    crc32: int
    dest_path: str
    list_offset: int
    path: str
    size: int
    type: FsActionType
    def __init__(self, type: _Optional[_Union[FsActionType, str]] = ..., path: _Optional[str] = ..., crc32: _Optional[int] = ..., list_offset: _Optional[int] = ..., size: _Optional[int] = ..., dest_path: _Optional[str] = ...) -> None: ...

class FsActionResp(_message.Message):
    __slots__ = ["crc32", "list", "size", "stat", "usage"]
    CRC32_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    STAT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    crc32: int
    list: FsDirentList
    size: int
    stat: FsStat
    usage: FsUsage
    def __init__(self, stat: _Optional[_Union[FsStat, _Mapping]] = ..., crc32: _Optional[int] = ..., list: _Optional[_Union[FsDirentList, _Mapping]] = ..., usage: _Optional[_Union[FsUsage, _Mapping]] = ..., size: _Optional[int] = ...) -> None: ...

class FsDirent(_message.Message):
    __slots__ = ["is_dir", "name"]
    IS_DIR_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    is_dir: bool
    name: str
    def __init__(self, name: _Optional[str] = ..., is_dir: bool = ...) -> None: ...

class FsDirentList(_message.Message):
    __slots__ = ["list", "total_size"]
    LIST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[FsDirent]
    total_size: int
    def __init__(self, list: _Optional[_Iterable[_Union[FsDirent, _Mapping]]] = ..., total_size: _Optional[int] = ...) -> None: ...

class FsStat(_message.Message):
    __slots__ = ["atime", "ctime", "is_dir", "mtime", "size"]
    ATIME_FIELD_NUMBER: _ClassVar[int]
    CTIME_FIELD_NUMBER: _ClassVar[int]
    IS_DIR_FIELD_NUMBER: _ClassVar[int]
    MTIME_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    atime: int
    ctime: int
    is_dir: bool
    mtime: int
    size: int
    def __init__(self, size: _Optional[int] = ..., mtime: _Optional[int] = ..., ctime: _Optional[int] = ..., atime: _Optional[int] = ..., is_dir: bool = ...) -> None: ...

class FsUsage(_message.Message):
    __slots__ = ["size", "used"]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    USED_FIELD_NUMBER: _ClassVar[int]
    size: int
    used: int
    def __init__(self, size: _Optional[int] = ..., used: _Optional[int] = ...) -> None: ...

class NvsActionReq(_message.Message):
    __slots__ = ["key", "list_offset", "namespc", "read_type", "type", "wdata"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    LIST_OFFSET_FIELD_NUMBER: _ClassVar[int]
    NAMESPC_FIELD_NUMBER: _ClassVar[int]
    READ_TYPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WDATA_FIELD_NUMBER: _ClassVar[int]
    key: str
    list_offset: int
    namespc: str
    read_type: NvsValueType
    type: NvsActionType
    wdata: NvsValue
    def __init__(self, type: _Optional[_Union[NvsActionType, str]] = ..., namespc: _Optional[str] = ..., key: _Optional[str] = ..., wdata: _Optional[_Union[NvsValue, _Mapping]] = ..., list_offset: _Optional[int] = ..., read_type: _Optional[_Union[NvsValueType, str]] = ...) -> None: ...

class NvsActionResp(_message.Message):
    __slots__ = ["entries", "rdata"]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    RDATA_FIELD_NUMBER: _ClassVar[int]
    entries: NvsEntriesList
    rdata: NvsValue
    def __init__(self, rdata: _Optional[_Union[NvsValue, _Mapping]] = ..., entries: _Optional[_Union[NvsEntriesList, _Mapping]] = ...) -> None: ...

class NvsEntriesList(_message.Message):
    __slots__ = ["entries", "total_entries"]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[NvsEntry]
    total_entries: int
    def __init__(self, entries: _Optional[_Iterable[_Union[NvsEntry, _Mapping]]] = ..., total_entries: _Optional[int] = ...) -> None: ...

class NvsEntry(_message.Message):
    __slots__ = ["key", "namespc", "type"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    NAMESPC_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    key: str
    namespc: str
    type: NvsValueType
    def __init__(self, type: _Optional[_Union[NvsValueType, str]] = ..., namespc: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class NvsValue(_message.Message):
    __slots__ = ["blobval", "numericval", "stringval", "type"]
    BLOBVAL_FIELD_NUMBER: _ClassVar[int]
    NUMERICVAL_FIELD_NUMBER: _ClassVar[int]
    STRINGVAL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    blobval: bytes
    numericval: int
    stringval: str
    type: NvsValueType
    def __init__(self, numericval: _Optional[int] = ..., stringval: _Optional[str] = ..., blobval: _Optional[bytes] = ..., type: _Optional[_Union[NvsValueType, str]] = ...) -> None: ...

class Packet(_message.Message):
    __slots__ = ["request", "response", "serial", "sync"]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SERIAL_FIELD_NUMBER: _ClassVar[int]
    SYNC_FIELD_NUMBER: _ClassVar[int]
    request: Request
    response: Response
    serial: int
    sync: bool
    def __init__(self, request: _Optional[_Union[Request, _Mapping]] = ..., response: _Optional[_Union[Response, _Mapping]] = ..., sync: bool = ..., serial: _Optional[int] = ...) -> None: ...

class Request(_message.Message):
    __slots__ = ["appfs_action", "fs_action", "nvs_action", "set_usb_mode", "start_app", "upload_chunk", "version_req", "xfer_ctrl"]
    APPFS_ACTION_FIELD_NUMBER: _ClassVar[int]
    FS_ACTION_FIELD_NUMBER: _ClassVar[int]
    NVS_ACTION_FIELD_NUMBER: _ClassVar[int]
    SET_USB_MODE_FIELD_NUMBER: _ClassVar[int]
    START_APP_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_CHUNK_FIELD_NUMBER: _ClassVar[int]
    VERSION_REQ_FIELD_NUMBER: _ClassVar[int]
    XFER_CTRL_FIELD_NUMBER: _ClassVar[int]
    appfs_action: AppfsActionReq
    fs_action: FsActionReq
    nvs_action: NvsActionReq
    set_usb_mode: SetUsbModeReq
    start_app: StartAppReq
    upload_chunk: Chunk
    version_req: VersionReq
    xfer_ctrl: XferReq
    def __init__(self, upload_chunk: _Optional[_Union[Chunk, _Mapping]] = ..., appfs_action: _Optional[_Union[AppfsActionReq, _Mapping]] = ..., fs_action: _Optional[_Union[FsActionReq, _Mapping]] = ..., nvs_action: _Optional[_Union[NvsActionReq, _Mapping]] = ..., start_app: _Optional[_Union[StartAppReq, _Mapping]] = ..., xfer_ctrl: _Optional[_Union[XferReq, str]] = ..., version_req: _Optional[_Union[VersionReq, _Mapping]] = ..., set_usb_mode: _Optional[_Union[SetUsbModeReq, _Mapping]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["appfs_resp", "download_chunk", "fs_resp", "nvs_resp", "status_code", "version_resp"]
    APPFS_RESP_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_CHUNK_FIELD_NUMBER: _ClassVar[int]
    FS_RESP_FIELD_NUMBER: _ClassVar[int]
    NVS_RESP_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    VERSION_RESP_FIELD_NUMBER: _ClassVar[int]
    appfs_resp: AppfsActionResp
    download_chunk: Chunk
    fs_resp: FsActionResp
    nvs_resp: NvsActionResp
    status_code: StatusCode
    version_resp: VersionResp
    def __init__(self, download_chunk: _Optional[_Union[Chunk, _Mapping]] = ..., appfs_resp: _Optional[_Union[AppfsActionResp, _Mapping]] = ..., fs_resp: _Optional[_Union[FsActionResp, _Mapping]] = ..., nvs_resp: _Optional[_Union[NvsActionResp, _Mapping]] = ..., version_resp: _Optional[_Union[VersionResp, _Mapping]] = ..., status_code: _Optional[_Union[StatusCode, str]] = ...) -> None: ...

class SetUsbModeReq(_message.Message):
    __slots__ = ["mode"]
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: UsbMode
    def __init__(self, mode: _Optional[_Union[UsbMode, str]] = ...) -> None: ...

class StartAppReq(_message.Message):
    __slots__ = ["arg", "slug"]
    ARG_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    arg: str
    slug: str
    def __init__(self, slug: _Optional[str] = ..., arg: _Optional[str] = ...) -> None: ...

class VersionReq(_message.Message):
    __slots__ = ["client_version"]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    client_version: int
    def __init__(self, client_version: _Optional[int] = ...) -> None: ...

class VersionResp(_message.Message):
    __slots__ = ["negotiated_version", "server_version"]
    NEGOTIATED_VERSION_FIELD_NUMBER: _ClassVar[int]
    SERVER_VERSION_FIELD_NUMBER: _ClassVar[int]
    negotiated_version: int
    server_version: int
    def __init__(self, server_version: _Optional[int] = ..., negotiated_version: _Optional[int] = ...) -> None: ...

class FsActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class NvsActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class NvsValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class StatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class UsbMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class XferReq(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
