
// SPDX-Copyright-Text: 2025 Julian Scheffers
// SPDX-License-Identifier: MIT

#include "badgelink_fs.h"
#include "dirent.h"
#include "errno.h"
#include "esp_crc.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "fcntl.h"
#include "stdio.h"
#include "string.h"
#include "sys/stat.h"
#include "sys/types.h"
#include "unistd.h"

static char const TAG[] = "badgelink_fs";

// Fast SD I/O helpers - use internal DMA RAM for stdio buffers
#ifdef CONFIG_FATFS_USE_FASTOPEN
#ifndef CONFIG_FATFS_STDIO_BUF_SIZE
#define CONFIG_FATFS_STDIO_BUF_SIZE 8192
#endif
#define BADGELINK_STDIO_BUF_SIZE CONFIG_FATFS_STDIO_BUF_SIZE

static FILE*  bl_fast_file   = NULL;
static void*  bl_fast_buffer = NULL;

static FILE* bl_sd_fopen(const char* path, const char* mode) {
    FILE* f = fopen(path, mode);
    if (f == NULL) return NULL;

    // Allocate stdio buffer in internal DMA-capable RAM for fast SD card access
    void* buf = heap_caps_malloc(BADGELINK_STDIO_BUF_SIZE, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
    if (buf != NULL) {
        setvbuf(f, buf, _IOFBF, BADGELINK_STDIO_BUF_SIZE);
        bl_fast_file   = f;
        bl_fast_buffer = buf;
    }
    return f;
}

static void bl_sd_fclose(FILE* f) {
    if (f == NULL) return;

    // Check if this file has a tracked fast buffer
    if (bl_fast_file == f && bl_fast_buffer != NULL) {
        fclose(f);
        free(bl_fast_buffer);
        bl_fast_file   = NULL;
        bl_fast_buffer = NULL;
        return;
    }
    fclose(f);
}
#else
// Fallback: just use regular fopen/fclose
static inline FILE* bl_sd_fopen(const char* path, const char* mode) {
    return fopen(path, mode);
}

static inline void bl_sd_fclose(FILE* f) {
    if (f != NULL) fclose(f);
}
#endif

static char     xfer_path[256];
static FILE*    xfer_fd;
static bool     xfer_is_sd;
static uint32_t xfer_crc32;
static uint32_t running_crc;

// Handle a FS request packet.
void badgelink_fs_handle() {
    switch (badgelink_packet.packet.request.req.fs_action.type) {
        case badgelink_FsActionType_FsActionList:
            badgelink_fs_list();
            break;
        case badgelink_FsActionType_FsActionDelete:
            badgelink_fs_delete();
            break;
        case badgelink_FsActionType_FsActionMkdir:
            badgelink_fs_mkdir();
            break;
        case badgelink_FsActionType_FsActionUpload:
            badgelink_fs_upload();
            break;
        case badgelink_FsActionType_FsActionDownload:
            badgelink_fs_download();
            break;
        case badgelink_FsActionType_FsActionStat:
            badgelink_fs_stat();
            break;
        // case badgelink_FsActionType_FsActionCrc23:
        //     badgelink_fs_crc32();
        //     break;
        // case badgelink_FsActionType_FsActionGetUsage:
        //     badgelink_fs_usage();
        //     break;
        case badgelink_FsActionType_FsActionRmdir:
            badgelink_fs_rmdir();
            break;
        default:
            badgelink_status_unsupported();
            break;
    }
}

// Handle a FS upload (host->badge) transfer.
void badgelink_fs_xfer_upload() {
    badgelink_Chunk* chunk = &badgelink_packet.packet.request.req.upload_chunk;

    size_t len = fwrite(chunk->data.bytes, 1, chunk->data.size, xfer_fd);
    if (len < chunk->data.size) {
        if (errno == ENOSPC) {
            badgelink_status_no_space();
        } else {
            ESP_LOGE(TAG, "%s: Unknown errno %d", __FUNCTION__, errno);
            badgelink_status_int_err();
        }
    } else {
        running_crc = esp_crc32_le(running_crc, chunk->data.bytes, chunk->data.size);
        badgelink_status_ok();
    }
}

// Handle a FS download (badge->host) transfer.
void badgelink_fs_xfer_download() {
    badgelink_packet.which_packet                = badgelink_Packet_response_tag;
    badgelink_packet.packet.response.status_code = badgelink_StatusCode_StatusOk;
    badgelink_packet.packet.response.which_resp  = badgelink_Response_download_chunk_tag;
    badgelink_Chunk* chunk                       = &badgelink_packet.packet.response.resp.download_chunk;

    chunk->position  = badgelink_xfer_pos;
    chunk->data.size = fread(chunk->data.bytes, 1, sizeof(chunk->data.bytes), xfer_fd);
    if (ferror(xfer_fd)) {
        ESP_LOGE(TAG, "%s: Unknown errno %d", __FUNCTION__, errno);
        badgelink_status_int_err();
    } else {
        // For protocol version 2+, compute streaming CRC during download.
        if (badgelink_get_protocol_version() >= 2) {
            running_crc = esp_crc32_le(running_crc, chunk->data.bytes, chunk->data.size);
        }
        badgelink_send_packet();
    }
}

// Finish a FS transfer.
void badgelink_fs_xfer_stop(bool abnormal) {
    if (abnormal) {
        if (xfer_is_sd) {
            bl_sd_fclose(xfer_fd);
        } else {
            fclose(xfer_fd);
        }
        if (badgelink_xfer_is_upload) {
            ESP_LOGE(TAG, "FS upload aborted");
            unlink(xfer_path);
        } else {
            ESP_LOGE(TAG, "FS download aborted");
        }

    } else if (badgelink_xfer_is_upload) {
        if (xfer_is_sd) {
            bl_sd_fclose(xfer_fd);
        } else {
            fclose(xfer_fd);
        }

        if (running_crc != xfer_crc32) {
            ESP_LOGE(TAG, "FS upload CRC32 mismatch; expected %08" PRIx32 ", actual %08" PRIx32, xfer_crc32,
                     running_crc);
            unlink(xfer_path);
            badgelink_status_int_err();
        } else {
            ESP_LOGI(TAG, "FS upload finished");
            badgelink_status_ok();
        }

    } else {
        ESP_LOGI(TAG, "FS download finished");
        if (xfer_is_sd) {
            bl_sd_fclose(xfer_fd);
        } else {
            fclose(xfer_fd);
        }

        // For protocol version 2+, send the final CRC.
        if (badgelink_get_protocol_version() >= 2) {
            badgelink_packet.which_packet                = badgelink_Packet_response_tag;
            badgelink_packet.packet.response.status_code = badgelink_StatusCode_StatusOk;
            badgelink_packet.packet.response.which_resp  = badgelink_Response_fs_resp_tag;
            badgelink_FsActionResp* resp                 = &badgelink_packet.packet.response.resp.fs_resp;
            resp->which_val                              = badgelink_FsActionResp_crc32_tag;
            resp->val.crc32                              = running_crc;
            resp->size                                   = badgelink_xfer_size;
            badgelink_send_packet();
        } else {
            badgelink_status_ok();
        }
    }
}

// Handle a FS list request.
void badgelink_fs_list() {
    badgelink_FsActionReq* req = &badgelink_packet.packet.request.req.fs_action;

    // Open directory.
    DIR* dp = opendir(req->path);
    if (!dp && errno == ENOENT) {
        badgelink_status_not_found();
        return;
    } else if (!dp) {
        ESP_LOGE(TAG, "%s: Unknown errno %d", __FUNCTION__, errno);
        badgelink_status_int_err();
        return;
    }

    uint32_t skip = req->list_offset;

    // Format response.
    badgelink_packet.which_packet                           = badgelink_Packet_response_tag;
    badgelink_packet.packet.response.status_code            = badgelink_StatusCode_StatusOk;
    badgelink_packet.packet.response.which_resp             = badgelink_Response_fs_resp_tag;
    badgelink_packet.packet.response.resp.fs_resp.which_val = badgelink_FsActionResp_list_tag;
    badgelink_FsDirentList* resp                            = &badgelink_packet.packet.response.resp.fs_resp.val.list;
    resp->list_count                                        = 0;
    resp->total_size                                        = 0;

    // Read all the dirents.
    struct dirent* ent       = readdir(dp);
    size_t const   max_count = sizeof(resp->list) / sizeof(badgelink_FsDirent);
    while (ent) {
        if (strcmp(ent->d_name, ".") || strcmp(ent->d_name, "..")) {
            // Only count entries that are not the `.` nor `..` entries.
            resp->total_size++;

            if (skip) {
                // Skip the first entries until the specified offset is reached.
                skip--;
            } else if (resp->list_count < max_count) {
                // Add entries until the array is full.
                strlcpy(resp->list[resp->list_count].name, ent->d_name, sizeof(resp->list->name));
                resp->list[resp->list_count].is_dir = ent->d_type == DT_DIR;
                resp->list_count++;
            }
        }
        ent = readdir(dp);
    }

    badgelink_send_packet();
}

// Handle a FS delete request.
void badgelink_fs_delete() {
    badgelink_FsActionReq* req = &badgelink_packet.packet.request.req.fs_action;

    if (unlink(req->path)) {
        if (errno == ENOENT) {
            badgelink_status_not_found();
        } else if (errno == EISDIR) {
            badgelink_status_is_dir();
        } else {
            ESP_LOGE(TAG, "%s: Unknown errno %d", __FUNCTION__, errno);
            badgelink_status_int_err();
        }
    } else {
        badgelink_status_ok();
    }
}

// Handle a FS mkdir request.
void badgelink_fs_mkdir() {
    badgelink_FsActionReq* req = &badgelink_packet.packet.request.req.fs_action;

    if (mkdir(req->path, 0777)) {
        if (errno == EEXIST) {
            badgelink_status_exists();
        } else if (errno == ENOENT) {
            badgelink_status_not_found();
        } else {
            ESP_LOGE(TAG, "%s: Unknown errno %d", __FUNCTION__, errno);
            badgelink_status_int_err();
        }
    } else {
        badgelink_status_ok();
    }
}

// Handle a FS upload request.
void badgelink_fs_upload() {
    badgelink_FsActionReq* req = &badgelink_packet.packet.request.req.fs_action;

    if (badgelink_xfer_type != BADGELINK_XFER_NONE) {
        badgelink_status_ill_state();
        return;
    }

    // Open target file for writing.
    strlcpy(xfer_path, req->path, sizeof(xfer_path));
    xfer_is_sd = (strncmp(req->path, "/sd", 3) == 0);
    xfer_fd    = xfer_is_sd ? bl_sd_fopen(req->path, "w+b") : fopen(req->path, "w+b");
    if (!xfer_fd) {
        if (errno == ENOENT) {
            badgelink_status_not_found();
        } else if (errno == EISDIR) {
            badgelink_status_is_dir();
        } else {
            ESP_LOGE(TAG, "%s: Unknown errno %d", __FUNCTION__, errno);
            badgelink_status_int_err();
        }
        return;
    }

    // Set up transfer.
    badgelink_xfer_type      = BADGELINK_XFER_FS;
    badgelink_xfer_is_upload = true;
    badgelink_xfer_size      = req->size;
    badgelink_xfer_pos       = 0;
    xfer_crc32               = req->crc32;
    running_crc              = 0;

    // This OK response officially starts the transfer.
    ESP_LOGI(TAG, "FS upload started");
    badgelink_status_ok();
}

// Handle a FS download request.
void badgelink_fs_download() {
    badgelink_FsActionReq* req = &badgelink_packet.packet.request.req.fs_action;

    if (badgelink_xfer_type != BADGELINK_XFER_NONE) {
        badgelink_status_ill_state();
        return;
    }

    // Open target file for reading.
    strlcpy(xfer_path, req->path, sizeof(xfer_path));
    xfer_is_sd = (strncmp(req->path, "/sd", 3) == 0);
    xfer_fd    = xfer_is_sd ? bl_sd_fopen(req->path, "rb") : fopen(req->path, "rb");
    if (!xfer_fd) {
        if (errno == ENOENT) {
            badgelink_status_not_found();
        } else if (errno == EISDIR) {
            badgelink_status_is_dir();
        } else {
            ESP_LOGE(TAG, "%s: Unknown errno %d", __FUNCTION__, errno);
            badgelink_status_int_err();
        }
        return;
    }

    uint32_t crc  = 0;
    uint32_t size = 0;

    if (badgelink_get_protocol_version() >= 2) {
        // Protocol version 2+: use stat() for size, CRC will be computed during transfer.
        struct stat statbuf;
        if (fstat(fileno(xfer_fd), &statbuf)) {
            ESP_LOGE(TAG, "%s: fstat failed, errno %d", __FUNCTION__, errno);
            if (xfer_is_sd) {
                bl_sd_fclose(xfer_fd);
            } else {
                fclose(xfer_fd);
            }
            badgelink_status_int_err();
            return;
        }
        size        = statbuf.st_size;
        running_crc = 0;
    } else {
        // Protocol version 1: calculate CRC32 upfront by reading entire file.
        uint8_t  tmp[128];
        uint32_t rcount = 1;
        while (rcount) {
            rcount = fread(tmp, 1, sizeof(tmp), xfer_fd);
            crc    = esp_crc32_le(crc, tmp, rcount);
            size  += rcount;
        }
        fseek(xfer_fd, 0, SEEK_SET);
    }

    // Set up transfer.
    badgelink_xfer_type      = BADGELINK_XFER_FS;
    badgelink_xfer_is_upload = false;
    badgelink_xfer_pos       = 0;
    badgelink_xfer_size      = size;

    // Format response.
    badgelink_packet.which_packet                = badgelink_Packet_response_tag;
    badgelink_packet.packet.response.which_resp  = badgelink_Response_fs_resp_tag;
    badgelink_packet.packet.response.status_code = badgelink_StatusCode_StatusOk;
    badgelink_FsActionResp* resp                 = &badgelink_packet.packet.response.resp.fs_resp;
    resp->which_val                              = badgelink_FsActionResp_crc32_tag;
    resp->val.crc32                              = crc;
    resp->size                                   = size;

    ESP_LOGI(TAG, "FS download started");
    badgelink_send_packet();
}

// Handle a FS stat request.
void badgelink_fs_stat() {
    badgelink_FsActionReq* req = &badgelink_packet.packet.request.req.fs_action;

    // Stat the file.
    struct stat statbuf;
    if (stat(req->path, &statbuf)) {
        if (errno == ENOENT) {
            badgelink_status_not_found();
        } else {
            ESP_LOGE(TAG, "%s: Unknown errno %d", __FUNCTION__, errno);
            badgelink_status_int_err();
        }
        return;
    }

    // Format response.
    badgelink_packet.which_packet                           = badgelink_Packet_response_tag;
    badgelink_packet.packet.response.status_code            = badgelink_StatusCode_StatusOk;
    badgelink_packet.packet.response.which_resp             = badgelink_Response_fs_resp_tag;
    badgelink_packet.packet.response.resp.fs_resp.which_val = badgelink_FsActionResp_stat_tag;
    badgelink_FsStat* resp                                  = &badgelink_packet.packet.response.resp.fs_resp.val.stat;

    // Convert stat.
    resp->size   = statbuf.st_size;
    resp->mtime  = statbuf.st_mtim.tv_sec * 1000 + statbuf.st_mtim.tv_nsec / 1000000l;
    resp->ctime  = statbuf.st_ctim.tv_sec * 1000 + statbuf.st_ctim.tv_nsec / 1000000l;
    resp->atime  = statbuf.st_atim.tv_sec * 1000 + statbuf.st_atim.tv_nsec / 1000000l;
    resp->is_dir = (statbuf.st_mode & S_IFMT) == S_IFDIR;

    badgelink_send_packet();
}

// Handle a FS crc32 request.
void badgelink_fs_crc32() {
}

// Handle a FS usage statistics request.
void badgelink_fs_usage() {
}

// Handle a FS rmdir request.
void badgelink_fs_rmdir() {
    badgelink_FsActionReq* req = &badgelink_packet.packet.request.req.fs_action;

    if (rmdir(req->path)) {
        if (errno == ENOENT) {
            badgelink_status_not_found();
        } else if (errno == ENOTEMPTY) {
            badgelink_status_not_empty();
        } else if (errno == ENOTDIR) {
            badgelink_status_is_file();
        } else if (errno == ENOENT) {
            badgelink_status_not_found();
        } else {
            ESP_LOGE(TAG, "%s: Unknown errno %d", __FUNCTION__, errno);
            badgelink_status_int_err();
        }
    } else {
        badgelink_status_ok();
    }
}
