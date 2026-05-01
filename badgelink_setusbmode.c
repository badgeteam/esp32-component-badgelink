
// SPDX-Copyright-Text: 2026 Nicolai Electronics
// SPDX-License-Identifier: MIT

#include "badgelink_setusbmode.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static char const TAG[] = "badgelink_setusbmode";

void badgelink_setusbmode_handle(void) {
    badgelink_SetUsbModeReq* req = &badgelink_packet.packet.request.req.set_usb_mode;

    badgelink_usb_mode_t target;
    switch (req->mode) {
        case badgelink_UsbMode_UsbModeDebug:
            target = BADGELINK_USB_MODE_DEBUG;
            break;
        case badgelink_UsbMode_UsbModeDevice:
            target = BADGELINK_USB_MODE_DEVICE;
            break;
        default:
            badgelink_status_malformed();
            return;
    }

    if (!badgelink_has_set_usb_mode_callback()) {
        // No host registered a handler for USB mode switching.
        badgelink_status_unsupported();
        return;
    }

    // Reply OK before switching: once we leave USB_DEVICE mode the TinyUSB
    // PHY is off the bus and the host can no longer read from badgelink.
    badgelink_status_ok();
    vTaskDelay(pdMS_TO_TICKS(200));

    ESP_LOGI(TAG, "Switching USB mode via badgelink: %d", (int)req->mode);
    badgelink_call_set_usb_mode(target);
}
