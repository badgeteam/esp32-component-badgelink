
// SPDX-Copyright-Text: 2025 Julian Scheffers
// SPDX-License-Identifier: MIT

#include "badgelink_startapp.h"
#include "appfs.h"
#include "esp_log.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "sdkconfig.h"

#ifdef CONFIG_BADGELINK_HOST_TANMATSU_LAUNCHER
// Provided by the Tanmatsu launcher (main/menu/apps.c). Puts the device
// into a known state (USB flash/monitor mode, radio off) before launch.
extern void prepare_device_for_app_launch(void);
#endif

static char const TAG[] = "badgelink_startapp";

// Handle a start app request.
void badgelink_startapp_handle() {
    badgelink_StartAppReq* req = &badgelink_packet.packet.request.req.start_app;

    // Try to find the file to start.
    appfs_handle_t fd = appfsOpen(req->slug);
    if (fd == APPFS_INVALID_FD) {
        badgelink_status_not_found();
        return;
    }

    if (!appfsBootSelect(fd, req->arg)) {
        // Failed to set boot select.
        ESP_LOGE(TAG, "Failed to set boot select");
        badgelink_status_int_err();
        return;
    }

    // Boot select set successfully.
    badgelink_status_ok();

    // Way a bit restarting so the response has time to get back to the host.
    vTaskDelay(pdMS_TO_TICKS(200));

#ifdef CONFIG_BADGELINK_HOST_TANMATSU_LAUNCHER
    prepare_device_for_app_launch();
#endif

    esp_restart();
}
