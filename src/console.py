#!/bin/python
import logging
import sys
import time
import signal
import os
import io
from logging import debug, info, warning, error, critical
from ns2update import NS2Update
from ConfigParser import SafeConfigParser


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='ns2update.log',
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('[NS2Update] %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(console)
logger = logging.getLogger('')

serverArgs = " ".join(sys.argv[1:])
serverDir = os.getcwd()
debug("Command line args: %s" % (serverArgs))

def exitHandler(signalType, stack):
	global updater
	info("Got signal %s" % (signalType))
	updater.stopServer()
	time.sleep(1)

default_config = """
[ns2update]
noUpdateCheck=false
steamcmd_binary=C:\\path\\to\\steamcmd.exe
steamcmd_user=server_username
steamcmd_password=server_password
steamcmd_appid_check=4920
steamcmd_depotid_check=4922
steamcmd_appid_download=4940
server_directory=serverDir
server_args=serverArgs
server_binary=server.exe
"""

config = SafeConfigParser()
config.readfp(io.BytesIO(default_config))

if not os.path.exists('ns2update.ini'):
	info("Unable to find ns2update.ini, creating default version")
	warning("Updates will not work until you configure ns2update.ini!")
	inifile = open('ns2update.ini','w')
	inifile.write(default_config)
	inifile.close()

debug("Loading config file...")
config.read('ns2update.ini')

config.set('ns2update','server_directory',serverDir)
config.set('ns2update','server_args',serverArgs)

updater = NS2Update(logger=logging.getLogger(''),config=config)

# Don't define the exit handler until after the updater object is available
signal.signal(signal.SIGINT, exitHandler)
signal.signal(signal.SIGABRT, exitHandler)
signal.signal(signal.SIGFPE, exitHandler)
signal.signal(signal.SIGILL, exitHandler)
signal.signal(signal.SIGSEGV, exitHandler)
signal.signal(signal.SIGTERM, exitHandler)

try:
	while 1==1:
		updater.think()
		time.sleep(60)
except KeyboardInterrupt:
	updater.stopServer()
	sys.exit(0)
except IOError:
	updater.stopServer()
	sys.exit(0)
