import subprocess
import sys
from pydbus import SystemBus
from .helpers import log

def run(command):
  assert(isinstance(command, list))
  log.debug("executing '%s'" % " ".join(command))
  return subprocess.check_output(command, stderr=subprocess.PIPE)

class Adapter:
  def __init__(self, iface):
    self.iface = iface
    self.bus = SystemBus()
    try:
      self.adapter = self.bus.get("org.bluez", "/org/bluez/%s" % iface)
    except KeyError:
      log.error("Unable to find adapter '%s', aborting." % iface)
      sys.exit(1)
    self.reset()

  def enable_ssp(self):
    run(["sudo", "btmgmt", "--index", self.iface, "io-cap", "1"])
    run(["sudo", "btmgmt", "--index", self.iface, "ssp", "1"])

  def disable_ssp(self):
    run(["sudo", "btmgmt", "--index", self.iface, "ssp", "0"])

  def set_name(self, name):
    if self.adapter.Name != name:
      run(["sudo", "hciconfig", self.iface, "name", name])
      if name not in run(["hciconfig", self.iface, "name"]).decode():
        log.error("Unable to set adapter name, aborting.")
        sys.exit(1)

  def set_class(self, adapter_class):
    class_hex = "0x%06x" % adapter_class
    if self.adapter.Class != class_hex:
      run(["sudo", "hciconfig", self.iface, "class", class_hex])
      if class_hex not in run(["hciconfig", self.iface, "class"]).decode():
        log.error("Unable to set adapter class, aborting.")
        sys.exit(1)

  def set_address(self, address):
    run(["sudo", "bdaddr", "-i", self.iface, address])
    self.reset()
    if address.upper() not in run(["hciconfig", self.iface]).decode():
      log.error("Unable to set adapter address, aborting.")
      sys.exit(1)

  def down(self):
    self.adapter.Powered = False

  def up(self):
    self.adapter.Powered = True

  def reset(self):
    self.down()
    self.up()
