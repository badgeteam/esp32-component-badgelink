
// SPDX-Copyright-Text: 2025 Julian Scheffers
// SPDX-License-Identifier: MIT

#pragma once

#include <stddef.h>
#include <stdint.h>

typedef void (*usb_callback_t)(uint8_t const* data, size_t len);

// Prepare the data for the BadgeLink service to start.
void badgelink_init();

// Start the badgelink service.
void badgelink_start(usb_callback_t usb_callback);

// Handle received data.
void badgelink_rxdata_cb(uint8_t const* data, size_t len);
