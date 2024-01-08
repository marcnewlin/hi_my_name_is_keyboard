#!/usr/bin/env python3

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
from .helpers import log

class Profile(dbus.service.Object):
  @dbus.service.method("org.bluez.Profile1", in_signature="", out_signature="")
  def Cancel(self):
    print("Profile.Cancel")

def register_hid_profile(iface, addr):
  dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
  bus = dbus.SystemBus()
  get_obj = lambda path, iface: dbus.Interface(bus.get_object("org.bluez", path), iface)
  addr_str = addr.replace(":", "_")
  path = "/org/bluez/%s/dev_%s" % (iface, addr_str)
  manager = get_obj("/org/bluez", "org.bluez.ProfileManager1")
  profile_path = "/test/profile"
  profile = Profile(bus, profile_path)
  hid_uuid = "00001124-0000-1000-8000-00805F9B34FB"
  with open("keyboard.xml", "r") as f:
    opts = { "ServiceRecord": f.read() }
  log.debug("calling RegisterProfile")
  manager.RegisterProfile(profile, hid_uuid, opts)
  loop = GLib.MainLoop()
  try:
    log.debug("running dbus loop")
    loop.run()
  except KeyboardInterrupt:
    log.debug("calling UnregisterProfile")
    manager.UnregisterProfile(profile)
