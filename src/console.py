#!/bin/python
import logging, sys, time, signal, os
from logging import debug, info, warning, error, critical
from ns2update import NS2Update

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

from webserver.webserver import WebServer

serverArgs = " ".join(sys.argv[1:])
serverDir = os.getcwd()
debug("Command line args: %s" % (serverArgs))

def exitHandler(signalType, stack):
	global updater
	info("Got signal %s" % (signalType))
	updater.stopServer()
	time.sleep(1)

try:
	os.mkdir("serverlogs")
except WindowsError:
	pass

updatePath = ''
if os.path.exists("%s/ns2update.cfg" % (serverDir)):
	debug("Found ns2update.cfg file, loading hldsupdatetool path")
	cfg = open("%s/ns2update.cfg" % (serverDir),"r")
	updatePath = cfg.readline()
	cfg.close()
	debug("Added path from config file: %s" % updatePath)

if not os.path.exists("%s/rrdtool.exe" % serverDir):
	warning("rrdtool.exe not found in %s.  Resource graphs will not be generated" % serverDir)

updater = NS2Update(logger=logging.getLogger(''),UpdateToolPath=updatePath,serverDirectory = serverDir,serverArgs=serverArgs)
ws = WebServer(updater=updater)

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
