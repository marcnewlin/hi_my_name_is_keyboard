import logging
import re
import subprocess
import sys

logging.basicConfig(
  level=logging.DEBUG,
  format='[%(asctime)s.%(msecs)03d] %(message)s',
  datefmt="%Y-%m-%d %H:%M:%S"
)

class Log:
  def status(self, msg):
    logging.info("\033[0;96m%s\033[0m" % msg)
  def success(self, msg):
    logging.info("\033[0;92m%s\033[0m" % msg)
  def error(self, msg):
    logging.error("\033[0m%s\033[0m" % msg)
  def debug(self, msg):
    logging.debug("\033[0m%s\033[0m" % msg)
  def notice(self, msg):
    logging.info("\033[0;93m%s\033[0m" % msg)
  def info(self, msg):
    logging.info(msg)
    
log = Log()

def run(command):
  assert(isinstance(command, list))
  log.debug("executing '%s'" % " ".join(command))
  return subprocess.check_output(command, stderr=subprocess.PIPE)

def assert_address(addr):
  if not re.match(r"^([a-fA-F0-9]{2}:{0,1}){5}[a-fA-F0-9]{2}$", addr):
    log.error("Error! This not look like a Bluetooth address: '%s'" % addr)
    sys.exit(1)
