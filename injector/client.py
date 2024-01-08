import binascii
import bluetooth
import time
from threading import Thread
from injector.hid import keyboard_report, ascii_to_hid
from .helpers import log


class L2CAPClient:
  def __init__(self, addr, port):
    self.addr = addr
    self.port = port
    self.connected = False
    self.sock = None

  def close(self):
    if self.connected:
      self.sock.close()
    self.connected = False
    self.sock = None

  def send(self, data):
    timeout = 0.1
    start = time.time()
    while (time.time() - start) < timeout:
      try:
        self.sock.send(data)
        log.debug("[TX-%d] %s" % (self.port, binascii.hexlify(data).decode()))
        return
      except bluetooth.btcommon.BluetoothError as ex:
        if ex.errno != 11: # no data available
          raise ex
        time.sleep(0.001)
      except Exception as ex:
        log.error("[TX-%d] ERROR! %s" % ex)
        self.connected = False
    log.error("[TX-%d] ERROR! timed out sending %s" % (self.port, binascii.hexlify(data).decode()))

  def recv(self, timeout=0):
    start = time.time()
    while True:
      raw = None
      if not self.connected:
        return None
      if self.sock is None:
        return None
      try:
        raw = self.sock.recv(64)
        if len(raw) == 0:
          self.connected = False
          return None
        log.debug("[RX-%d] %s" % (self.port, binascii.hexlify(raw).decode()))
      except bluetooth.btcommon.BluetoothError as ex:
        if ex.errno != 11: # no data available
          raise ex
        else:
          if (time.time() - start) < timeout:
            continue
      return raw

  def connect(self, timeout=None):
    log.debug("connecting to %s on port %d" % (self.addr, self.port))
    sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    sock.settimeout(timeout)
    try:
      sock.connect((self.addr, self.port))
      sock.setblocking(0)
      self.sock = sock
      self.connected = True
      log.debug("SUCCESS! connected on port %d" % self.port)
    except Exception as ex:
      self.connected = False
      log.error("ERROR connecting on port %d: %s" % (self.port, ex))
    return self.connected

class KeyboardClient:
  def __init__(self, host_addr, auto_ack=False):
    self.host_addr = host_addr
    self.auto_ack = auto_ack
    self.c1 = L2CAPClient(host_addr, 1)
    self.c17 = L2CAPClient(host_addr, 17)
    self.c19 = L2CAPClient(host_addr, 19)
    self.thread = Thread(target=self.loop)
    self.exit = False
    self.hid_ready = False
    self.thread.start()

  def connect_sdp(self, timeout=5):
    self.c1.connect(timeout=timeout)
    return self.c1.connected

  def connect_hid_control(self, timeout=2):
    self.c17.connect(timeout=timeout)
    return self.c17.connected

  def connect_hid_interrupt(self, timeout=2):
    self.c19.connect(timeout=timeout)
    return self.c19.connected

  def close(self):
    self.exit = True
    self.thread.join()

  def connect(self, port, timeout=None):
    log.debug("connecting to %s on port %d" % (self.host_addr, port))
    sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    sock.settimeout(timeout)
    try:
      sock.connect((self.host_addr, port))
      log.debug("SUCCESS! connected on port %d" % port)
    except Exception as ex:
      log.error("ERROR connecting on port %d: %s" % (port, ex))
      return None
    sock.setblocking(0)
    sock.port = port
    return sock

  def send_keyboard_report(self, *args):
    self.c19.send(keyboard_report(*args))

  def send_keypress(self, *args, delay=0.004):
    self.send_keyboard_report(*args)
    time.sleep(0.004)
    self.send_keyboard_report()
    time.sleep(0.004)

  def send_ascii(self, s):
    for c in s:
      self.send_keypress(*ascii_to_hid(c))

  def loop(self):
    while not self.exit:
      time.sleep(0.001)

      raw = self.c1.recv()

      raw = self.c19.recv()
      if raw in [b"\xa2\xf1\x01\x00", b"\xa2\x01\x01"]:
        self.hid_ready = True

      raw = self.c17.recv()
      if raw is not None:
        if raw == b"\x15":
          self.c17.close()
        elif self.auto_ack:
          self.c17.send(b"\x00")

    self.c1.close()
    self.c17.close()
    self.c19.close()
