# BadgeLink Protocol Changes

## Protocol Version Negotiation (Version 2)

This update adds protocol version negotiation to BadgeLink. The previous protocol without version negotiation is considered version 1.

### New Message Types

#### VersionReq (Request tag 7)

Sent by the client to negotiate the protocol version.

| Field | Tag | Type | Description |
|-------|-----|------|-------------|
| client_version | 1 | uint16 | Highest protocol version supported by the client |

#### VersionResp (Response tag 6)

Sent by the server in response to a VersionReq.

| Field | Tag | Type | Description |
|-------|-----|------|-------------|
| server_version | 1 | uint16 | Highest protocol version supported by the server |
| negotiated_version | 2 | uint16 | Protocol version to use for this session |

### Negotiation Algorithm

The server calculates the negotiated version as:
```
negotiated_version = min(client_version, server_version)
```

The server stores this negotiated version and uses it for the remainder of the session.

**Important**: The server resets the negotiated version to 1 when a sync packet is received. This ensures each new connection starts fresh with v1 behavior until version negotiation occurs.

### Backwards Compatibility

- **Old server (v1) + New client**: The server responds with `StatusNotSupported`. The client should fall back to version 1 behavior.
- **New server (v2) + Old client**: The client never sends a VersionReq. The server defaults to version 1.
- **New server + New client**: Full version negotiation occurs.

### Client Implementation

Recommended flow for new clients:

```
1. After sync, send VersionReq with client_version = 2
2. If response is StatusNotSupported:
   - Server is version 1, use legacy behavior
3. If response is VersionResp:
   - Use negotiated_version for session behavior
   - server_version indicates what features the server supports
```

### Server API

The server exposes `badgelink_get_protocol_version()` which returns the currently negotiated protocol version (defaults to 1 if no VersionReq was received).

---

## Streaming CRC for Downloads (Version 2)

Version 2 changes how file downloads work to improve performance for large files.

### Version 1 Behavior (Legacy)

1. Client sends download request
2. Server reads **entire file** to calculate CRC32
3. Server responds with `size` and `crc32`
4. Client requests chunks with `XferContinue`
5. Server sends `download_chunk` responses
6. Client sends `XferFinish`
7. Server responds with `StatusOk`

**Problem**: For large files, the server must read the entire file before sending the first byte. This causes significant delays.

### Version 2 Behavior (Streaming CRC)

1. Client sends download request
2. Server uses `stat()` to get file size (no file read)
3. Server responds with `size` and `crc32 = 0`
4. Client requests chunks with `XferContinue`
5. Server sends `download_chunk` responses, computing CRC incrementally
6. Client sends `XferFinish`
7. Server responds with `FsActionResp` or `AppfsActionResp` containing the final `crc32`

**Benefit**: Download starts immediately without reading the entire file first.

### Client Implementation for Downloads

```
1. Send download request
2. Receive initial response with size (and crc32)
3. If protocol version >= 2:
   - Ignore crc32 field (it will be 0)
   - Initialize local running_crc = 0
4. Request chunks with XferContinue
5. For each chunk received:
   - Update local running_crc
6. Send XferFinish
7. If protocol version >= 2:
   - Receive FsActionResp/AppfsActionResp with final crc32
   - Compare with local running_crc
8. If protocol version 1:
   - Receive StatusOk
   - Compare local running_crc with crc32 from step 2
```

### Response Differences

| Event | Version 1 | Version 2 |
|-------|-----------|-----------|
| Download start | `crc32` = actual CRC | `crc32` = 0 |
| XferFinish (FS) | `StatusOk` | `FsActionResp` with `crc32` |
| XferFinish (AppFS) | `StatusOk` | `AppfsActionResp` with `crc32` |

---

## Python Client Updates

The Python client (`badgelink.py`) has been updated to support protocol version 2.

### New Features

- **Automatic version negotiation**: The client automatically negotiates the protocol version with the server on connection.
- **Streaming CRC for downloads**: Downloads use streaming CRC verification for v2 servers.

### Command Line Options

```
--version1    Force protocol version 1 (legacy mode, skip version negotiation)
```

Use `--version1` when you need to connect using the legacy protocol, for example when testing v1 compatibility or connecting to a known v1 server.

### Example Usage

```bash
# Normal usage (auto-negotiates version)
./badgelink.sh fs download /sd/file.bin local_file.bin

# Force version 1 protocol
./badgelink.sh --version1 fs download /sd/file.bin local_file.bin
```
