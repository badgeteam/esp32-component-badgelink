
// SPDX-Copyright-Text: 2025 Julian Scheffers
// SPDX-License-Identifier: MIT

#pragma once

#include <stddef.h>
#include <stdint.h>

typedef void (*usb_callback_t)(uint8_t const* data, size_t len);

// Callback invoked just before badgelink causes the host device to reboot
// into a launched app. Host should put hardware (USB, radio, etc.) into a
// known state. If no callback is registered, no action is taken.
typedef void (*badgelink_prepare_device_cb_t)(void);

// USB mode requested by a connected badgelink host. Translates protobuf
// values into a host-agnostic enum so badgelink doesn't depend on
// launcher-side type definitions.
typedef enum {
    BADGELINK_USB_MODE_DEBUG  = 0,
    BADGELINK_USB_MODE_DEVICE = 1,
} badgelink_usb_mode_t;

// Callback invoked when a host requests a USB mode switch via the
// SetUsbMode request. If no callback is registered, the request is
// answered with StatusNotSupported.
typedef void (*badgelink_set_usb_mode_cb_t)(badgelink_usb_mode_t mode);

// Register the prepare-device-for-app-launch callback. Pass NULL to clear.
void badgelink_set_prepare_device_callback(badgelink_prepare_device_cb_t cb);

// Register the set-USB-mode callback. Pass NULL to clear.
void badgelink_set_usb_mode_callback(badgelink_set_usb_mode_cb_t cb);

// Prepare the data for the BadgeLink service to start.
void badgelink_init();

// Start the badgelink service.
void badgelink_start(usb_callback_t usb_callback);

// Handle received data.
void badgelink_rxdata_cb(uint8_t const* data, size_t len);

// Get the negotiated protocol version.
uint16_t badgelink_get_protocol_version();
