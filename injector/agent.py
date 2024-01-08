import dbus
import dbus.service
import dbus.mainloop.glib
import time
from gi.repository import GLib
from multiprocessing import Process
from .helpers import log

class Agent(dbus.service.Object):
  @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
  def Cancel(self):
    log.debug("Agent.Cancel")

def agent_loop(target_path):
  dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
  loop = GLib.MainLoop()
  bus = dbus.SystemBus()
  path = "/test/agent"
  agent = Agent(bus, path)
  agent.target_path = target_path
  obj = bus.get_object("org.bluez", "/org/bluez")
  manager = dbus.Interface(obj, "org.bluez.AgentManager1")
  manager.RegisterAgent(path, "NoInputNoOutput")
  manager.RequestDefaultAgent(path)
  log.debug("'NoInputNoOutput' pairing-agent is running")
  loop.run()

class PairingAgent:
  def __init__(self, iface, target_addr):
    self.iface = iface
    self.target_addr = target_addr
    dev_name = "dev_%s" % target_addr.upper().replace(":", "_")
    self.target_path = "/org/bluez/%s/%s" % (iface, dev_name)

  def __enter__(self):
    self.agent = Process(target=agent_loop, args=(self.target_path,))
    self.agent.start()
    time.sleep(0.25)

  def __exit__(self, a, b, c):
    self.agent.kill()
    time.sleep(0.25)
