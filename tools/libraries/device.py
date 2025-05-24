
import os
import usb.core
import usb.util
import time

class BadgeUSB:
    # These requests are supported by both MCH2022 badge and Tanmatsu
    REQUEST_STATE          = 0x22
    REQUEST_RESET          = 0x23
    REQUEST_BAUDRATE       = 0x24
    REQUEST_MODE           = 0x25
    REQUEST_MODE_GET       = 0x26
    REQUEST_FW_VERSION_GET = 0x27

    def __init__(self):
        device = "tanmatsu"

        if os.name == 'nt':
            from usb.backend import libusb1
            be = libusb1.get_backend(find_library=lambda x: os.path.dirname(__file__) + "\\libusb-1.0.dll")
            self.device = usb.core.find(idVendor=0x16d0, idProduct=0x0f9a, backend=be)
        else:
            self.device = usb.core.find(idVendor=0x16d0, idProduct=0x0f9a)

        if self.device is None:
            raise FileNotFoundError("Badge not found")

        configuration = self.device.get_active_configuration()

        self.webusb = configuration[(0 if device == "tanmatsu" else 4, 0)]

        self.ep_out = usb.util.find_descriptor(self.webusb, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        self.ep_in  = usb.util.find_descriptor(self.webusb, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)

        self.request_type_in = usb.util.build_request_type(usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)
        self.request_type_out = usb.util.build_request_type(usb.util.CTRL_OUT, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)

    def flush(self):
        pass

    def write(self, data = bytes([])):
        while len(data):
            sent = self.ep_out.write(data)
            data = data[sent:]
            time.sleep(0.01)

    def read_all(self):
        data = b''
        while True:
            try:
                new_data = bytes(self.ep_in.read(self.ep_in.wMaxPacketSize, 5))
                data += new_data
            except usb.USBError as e:
                break
        return data
