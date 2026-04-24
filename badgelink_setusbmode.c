
// SPDX-Copyright-Text: 2026 Nicolai Electronics
// SPDX-License-Identifier: MIT

#include "badgelink_setusbmode.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

#ifdef CONFIG_BADGELINK_HOST_TANMATSU_LAUNCHER
// Provided by the Tanmatsu launcher (main/usb_device.c).
typedef enum {
    LAUNCHER_USB_DEBUG    = 0,
    LAUNCHER_USB_DEVICE   = 1,
    LAUNCHER_USB_DISABLED = 2,
} launcher_usb_mode_t;
extern void usb_mode_set(launcher_usb_mode_t mode);
#endif

static char const TAG[] = "badgelink_setusbmode";

void badgelink_setusbmode_handle(void) {
#ifdef CONFIG_BADGELINK_HOST_TANMATSU_LAUNCHER
    badgelink_SetUsbModeReq* req = &badgelink_packet.packet.request.req.set_usb_mode;

    launcher_usb_mode_t target;
    switch (req->mode) {
        case badgelink_UsbMode_UsbModeDebug:
            target = LAUNCHER_USB_DEBUG;
            break;
        case badgelink_UsbMode_UsbModeDevice:
            target = LAUNCHER_USB_DEVICE;
            break;
        default:
            badgelink_status_malformed();
            return;
    }

    // Reply OK before switching: once we leave USB_DEVICE mode the TinyUSB
    // PHY is off the bus and the host can no longer read from badgelink.
    badgelink_status_ok();
    vTaskDelay(pdMS_TO_TICKS(200));

    ESP_LOGI(TAG, "Switching USB mode via badgelink: %d", (int)req->mode);
    usb_mode_set(target);
#else
    // Not built into a host we know how to drive.
    badgelink_status_unsupported();
#endif
}
