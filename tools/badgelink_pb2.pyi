from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StatusCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    StatusOk: _ClassVar[StatusCode]
    StatusNotSupported: _ClassVar[StatusCode]
    StatusNotFound: _ClassVar[StatusCode]
    StatusMalformed: _ClassVar[StatusCode]
    StatusInternalError: _ClassVar[StatusCode]
    StatusIllegalState: _ClassVar[StatusCode]
    StatusNoSpace: _ClassVar[StatusCode]
    StatusNotEmpty: _ClassVar[StatusCode]
    StatusIsFile: _ClassVar[StatusCode]
    StatusIsDir: _ClassVar[StatusCode]
    StatusExists: _ClassVar[StatusCode]

class XferReq(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    XferContinue: _ClassVar[XferReq]
    XferAbort: _ClassVar[XferReq]
    XferFinish: _ClassVar[XferReq]

class FsActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FsActionList: _ClassVar[FsActionType]
    FsActionDelete: _ClassVar[FsActionType]
    FsActionMkdir: _ClassVar[FsActionType]
    FsActionUpload: _ClassVar[FsActionType]
    FsActionDownload: _ClassVar[FsActionType]
    FsActionStat: _ClassVar[FsActionType]
    FsActionCrc23: _ClassVar[FsActionType]
    FsActionGetUsage: _ClassVar[FsActionType]
    FsActionRmdir: _ClassVar[FsActionType]

class NvsActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NvsActionList: _ClassVar[NvsActionType]
    NvsActionRead: _ClassVar[NvsActionType]
    NvsActionWrite: _ClassVar[NvsActionType]
    NvsActionDelete: _ClassVar[NvsActionType]

class NvsValueType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NvsValueUint8: _ClassVar[NvsValueType]
    NvsValueInt8: _ClassVar[NvsValueType]
    NvsValueUint16: _ClassVar[NvsValueType]
    NvsValueInt16: _ClassVar[NvsValueType]
    NvsValueUint32: _ClassVar[NvsValueType]
    NvsValueInt32: _ClassVar[NvsValueType]
    NvsValueUint64: _ClassVar[NvsValueType]
    NvsValueInt64: _ClassVar[NvsValueType]
    NvsValueString: _ClassVar[NvsValueType]
    NvsValueBlob: _ClassVar[NvsValueType]
StatusOk: StatusCode
StatusNotSupported: StatusCode
StatusNotFound: StatusCode
StatusMalformed: StatusCode
StatusInternalError: StatusCode
StatusIllegalState: StatusCode
StatusNoSpace: StatusCode
StatusNotEmpty: StatusCode
StatusIsFile: StatusCode
StatusIsDir: StatusCode
StatusExists: StatusCode
XferContinue: XferReq
XferAbort: XferReq
XferFinish: XferReq
FsActionList: FsActionType
FsActionDelete: FsActionType
FsActionMkdir: FsActionType
FsActionUpload: FsActionType
FsActionDownload: FsActionType
FsActionStat: FsActionType
FsActionCrc23: FsActionType
FsActionGetUsage: FsActionType
FsActionRmdir: FsActionType
NvsActionList: NvsActionType
NvsActionRead: NvsActionType
NvsActionWrite: NvsActionType
NvsActionDelete: NvsActionType
NvsValueUint8: NvsValueType
NvsValueInt8: NvsValueType
NvsValueUint16: NvsValueType
NvsValueInt16: NvsValueType
NvsValueUint32: NvsValueType
NvsValueInt32: NvsValueType
NvsValueUint64: NvsValueType
NvsValueInt64: NvsValueType
NvsValueString: NvsValueType
NvsValueBlob: NvsValueType

class Packet(_message.Message):
    __slots__ = ("serial", "request", "response", "sync")
    SERIAL_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SYNC_FIELD_NUMBER: _ClassVar[int]
    serial: int
    request: Request
    response: Response
    sync: bool
    def __init__(self, serial: _Optional[int] = ..., request: _Optional[_Union[Request, _Mapping]] = ..., response: _Optional[_Union[Response, _Mapping]] = ..., sync: bool = ...) -> None: ...

class Request(_message.Message):
    __slots__ = ("upload_chunk", "appfs_action", "fs_action", "nvs_action", "start_app", "xfer_ctrl")
    UPLOAD_CHUNK_FIELD_NUMBER: _ClassVar[int]
    APPFS_ACTION_FIELD_NUMBER: _ClassVar[int]
    FS_ACTION_FIELD_NUMBER: _ClassVar[int]
    NVS_ACTION_FIELD_NUMBER: _ClassVar[int]
    START_APP_FIELD_NUMBER: _ClassVar[int]
    XFER_CTRL_FIELD_NUMBER: _ClassVar[int]
    upload_chunk: Chunk
    appfs_action: AppfsActionReq
    fs_action: FsActionReq
    nvs_action: NvsActionReq
    start_app: StartAppReq
    xfer_ctrl: XferReq
    def __init__(self, upload_chunk: _Optional[_Union[Chunk, _Mapping]] = ..., appfs_action: _Optional[_Union[AppfsActionReq, _Mapping]] = ..., fs_action: _Optional[_Union[FsActionReq, _Mapping]] = ..., nvs_action: _Optional[_Union[NvsActionReq, _Mapping]] = ..., start_app: _Optional[_Union[StartAppReq, _Mapping]] = ..., xfer_ctrl: _Optional[_Union[XferReq, str]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("status_code", "download_chunk", "appfs_resp", "fs_resp", "nvs_resp")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_CHUNK_FIELD_NUMBER: _ClassVar[int]
    APPFS_RESP_FIELD_NUMBER: _ClassVar[int]
    FS_RESP_FIELD_NUMBER: _ClassVar[int]
    NVS_RESP_FIELD_NUMBER: _ClassVar[int]
    status_code: StatusCode
    download_chunk: Chunk
    appfs_resp: AppfsActionResp
    fs_resp: FsActionResp
    nvs_resp: NvsActionResp
    def __init__(self, status_code: _Optional[_Union[StatusCode, str]] = ..., download_chunk: _Optional[_Union[Chunk, _Mapping]] = ..., appfs_resp: _Optional[_Union[AppfsActionResp, _Mapping]] = ..., fs_resp: _Optional[_Union[FsActionResp, _Mapping]] = ..., nvs_resp: _Optional[_Union[NvsActionResp, _Mapping]] = ...) -> None: ...

class StartAppReq(_message.Message):
    __slots__ = ("slug", "arg")
    SLUG_FIELD_NUMBER: _ClassVar[int]
    ARG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    arg: str
    def __init__(self, slug: _Optional[str] = ..., arg: _Optional[str] = ...) -> None: ...

class Chunk(_message.Message):
    __slots__ = ("position", "data")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    position: int
    data: bytes
    def __init__(self, position: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class FsUsage(_message.Message):
    __slots__ = ("size", "used")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    USED_FIELD_NUMBER: _ClassVar[int]
    size: int
    used: int
    def __init__(self, size: _Optional[int] = ..., used: _Optional[int] = ...) -> None: ...

class AppfsMetadata(_message.Message):
    __slots__ = ("slug", "title", "version", "size")
    SLUG_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    slug: str
    title: str
    version: int
    size: int
    def __init__(self, slug: _Optional[str] = ..., title: _Optional[str] = ..., version: _Optional[int] = ..., size: _Optional[int] = ...) -> None: ...

class AppfsActionReq(_message.Message):
    __slots__ = ("type", "metadata", "slug", "crc32", "list_offset")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_NUMBER: _ClassVar[int]
    CRC32_FIELD_NUMBER: _ClassVar[int]
    LIST_OFFSET_FIELD_NUMBER: _ClassVar[int]
    type: FsActionType
    metadata: AppfsMetadata
    slug: str
    crc32: int
    list_offset: int
    def __init__(self, type: _Optional[_Union[FsActionType, str]] = ..., metadata: _Optional[_Union[AppfsMetadata, _Mapping]] = ..., slug: _Optional[str] = ..., crc32: _Optional[int] = ..., list_offset: _Optional[int] = ...) -> None: ...

class AppfsList(_message.Message):
    __slots__ = ("list", "total_size")
    LIST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[AppfsMetadata]
    total_size: int
    def __init__(self, list: _Optional[_Iterable[_Union[AppfsMetadata, _Mapping]]] = ..., total_size: _Optional[int] = ...) -> None: ...

class AppfsActionResp(_message.Message):
    __slots__ = ("metadata", "crc32", "list", "usage", "size")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CRC32_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    metadata: AppfsMetadata
    crc32: int
    list: AppfsList
    usage: FsUsage
    size: int
    def __init__(self, metadata: _Optional[_Union[AppfsMetadata, _Mapping]] = ..., crc32: _Optional[int] = ..., list: _Optional[_Union[AppfsList, _Mapping]] = ..., usage: _Optional[_Union[FsUsage, _Mapping]] = ..., size: _Optional[int] = ...) -> None: ...

class FsStat(_message.Message):
    __slots__ = ("size", "mtime", "ctime", "atime", "is_dir")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    MTIME_FIELD_NUMBER: _ClassVar[int]
    CTIME_FIELD_NUMBER: _ClassVar[int]
    ATIME_FIELD_NUMBER: _ClassVar[int]
    IS_DIR_FIELD_NUMBER: _ClassVar[int]
    size: int
    mtime: int
    ctime: int
    atime: int
    is_dir: bool
    def __init__(self, size: _Optional[int] = ..., mtime: _Optional[int] = ..., ctime: _Optional[int] = ..., atime: _Optional[int] = ..., is_dir: bool = ...) -> None: ...

class FsActionReq(_message.Message):
    __slots__ = ("type", "path", "crc32", "list_offset", "size")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    CRC32_FIELD_NUMBER: _ClassVar[int]
    LIST_OFFSET_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    type: FsActionType
    path: str
    crc32: int
    list_offset: int
    size: int
    def __init__(self, type: _Optional[_Union[FsActionType, str]] = ..., path: _Optional[str] = ..., crc32: _Optional[int] = ..., list_offset: _Optional[int] = ..., size: _Optional[int] = ...) -> None: ...

class FsDirent(_message.Message):
    __slots__ = ("name", "is_dir")
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_DIR_FIELD_NUMBER: _ClassVar[int]
    name: str
    is_dir: bool
    def __init__(self, name: _Optional[str] = ..., is_dir: bool = ...) -> None: ...

class FsDirentList(_message.Message):
    __slots__ = ("list", "total_size")
    LIST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[FsDirent]
    total_size: int
    def __init__(self, list: _Optional[_Iterable[_Union[FsDirent, _Mapping]]] = ..., total_size: _Optional[int] = ...) -> None: ...

class FsActionResp(_message.Message):
    __slots__ = ("stat", "crc32", "list", "usage", "size")
    STAT_FIELD_NUMBER: _ClassVar[int]
    CRC32_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    stat: FsStat
    crc32: int
    list: FsDirentList
    usage: FsUsage
    size: int
    def __init__(self, stat: _Optional[_Union[FsStat, _Mapping]] = ..., crc32: _Optional[int] = ..., list: _Optional[_Union[FsDirentList, _Mapping]] = ..., usage: _Optional[_Union[FsUsage, _Mapping]] = ..., size: _Optional[int] = ...) -> None: ...

class NvsValue(_message.Message):
    __slots__ = ("type", "numericval", "stringval", "blobval")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMERICVAL_FIELD_NUMBER: _ClassVar[int]
    STRINGVAL_FIELD_NUMBER: _ClassVar[int]
    BLOBVAL_FIELD_NUMBER: _ClassVar[int]
    type: NvsValueType
    numericval: int
    stringval: str
    blobval: bytes
    def __init__(self, type: _Optional[_Union[NvsValueType, str]] = ..., numericval: _Optional[int] = ..., stringval: _Optional[str] = ..., blobval: _Optional[bytes] = ...) -> None: ...

class NvsEntry(_message.Message):
    __slots__ = ("type", "namespc", "key")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAMESPC_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    type: NvsValueType
    namespc: str
    key: str
    def __init__(self, type: _Optional[_Union[NvsValueType, str]] = ..., namespc: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class NvsActionReq(_message.Message):
    __slots__ = ("type", "namespc", "key", "wdata", "list_offset", "read_type")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    NAMESPC_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    WDATA_FIELD_NUMBER: _ClassVar[int]
    LIST_OFFSET_FIELD_NUMBER: _ClassVar[int]
    READ_TYPE_FIELD_NUMBER: _ClassVar[int]
    type: NvsActionType
    namespc: str
    key: str
    wdata: NvsValue
    list_offset: int
    read_type: NvsValueType
    def __init__(self, type: _Optional[_Union[NvsActionType, str]] = ..., namespc: _Optional[str] = ..., key: _Optional[str] = ..., wdata: _Optional[_Union[NvsValue, _Mapping]] = ..., list_offset: _Optional[int] = ..., read_type: _Optional[_Union[NvsValueType, str]] = ...) -> None: ...

class NvsEntriesList(_message.Message):
    __slots__ = ("entries", "total_entries")
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[NvsEntry]
    total_entries: int
    def __init__(self, entries: _Optional[_Iterable[_Union[NvsEntry, _Mapping]]] = ..., total_entries: _Optional[int] = ...) -> None: ...

class NvsActionResp(_message.Message):
    __slots__ = ("rdata", "entries")
    RDATA_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    rdata: NvsValue
    entries: NvsEntriesList
    def __init__(self, rdata: _Optional[_Union[NvsValue, _Mapping]] = ..., entries: _Optional[_Union[NvsEntriesList, _Mapping]] = ...) -> None: ...
