#!/usr/bin/env python3

import binascii
import usb.core

dev = usb.core.find(idVendor=0x05ac)
if dev is None:
  print("Error! Apple USB peripheral was not found.")
  quit()

for x in range(4):
  try:
    dev.detach_kernel_driver(x)
  except usb.core.USBError as ex:
    continue

# read serial number string descriptor
res = dev.ctrl_transfer(0x80, 0x06, 0x0303, 0x0000, 0x100)
serial_number = bytes(res[::2][1:]).decode()

# read HID report 0x34 (BT address of keyboard and the product name)
res = dev.ctrl_transfer(0xa1, 0x01, 0x0334, 0x0000, 0x100)
accessory_bt_addr = ":".join("%02x" % c for c in res[4:10])
accessory_model = bytes(res[13:]).decode().strip()

# read HID report 0x35 (BT address of Mac and the link key)
res = dev.ctrl_transfer(0xa1, 0x01, 0x0335, 0x0000, 0x100)
mac_bt_addr = ":".join("%02x" % c for c in res[3:9])
bt_link_key = binascii.hexlify(res[9:25][::-1]).decode()

print("Model          - %s" % accessory_model)
print("Serial Number  - %s" % serial_number)
print("BT Address     - %s" % accessory_bt_addr)
print("Mac BT Address - %s" % mac_bt_addr)
print("BT Link Key    - %s" % bt_link_key)

if bt_link_key == "00000000000000000000000000000000":
  print("\033[92mThe Bluetooth link-key was not found. Plug the accessory " \
        "into the Mac for a few seconds and try again.\033[0m")
