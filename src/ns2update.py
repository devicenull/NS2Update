#!/bin/python

import urllib2, subprocess, sys, os, time, logging, signal
from xml.etree.ElementTree import parse
from logging import debug, info, warning, error, critical
from threading import Thread
from Queue import Queue, Empty
from time import strftime


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='ns2update.log',
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('[NS2Update] %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(console)

versionURL = "http://ns2update.devicenull.org/ns2update/ns2version.txt"
serverDir = os.getcwd()

def enqueue_output(out, queue, logFile):
	for line in iter(out.readline,''):
		queue.put(line)
		logFile.write(line)
		logFile.flush()
	out.close()

# if checkHash is set to 1, we will try to update until the hash of Server.exe changes
def update(serverDir,checkHash):
	info("Starting server update")
	update = subprocess.Popen("../hldsupdatetool.exe -command update -game naturalselection2 -dir %s" % serverDir)
	if update:
		while update.returncode == None:
			time.sleep(5)
			update.poll()
	info("Server update complete!")

def startServer(args):
	# Actualyl start the server process
	serverProc = subprocess.Popen("Server.exe %s" % args, stdin=None, stdout=subprocess.PIPE)
	info("Server started, pid %i" % (serverProc.pid))

	# Open up the log file
	logName = strftime("%Y.%m.%d.%H%M.log")
	debug("Logging to %s" % logName)
	logFile = open("serverlogs/%s" % logName,"a")

	# Setup everything we need to capture the server output
	outQueue = Queue()
	outThread = Thread(target=enqueue_output, args=(serverProc.stdout, outQueue, logFile))
	outThread.daemon = True
	outThread.start()

	return (outThread, outQueue, serverProc, logFile)

def stopServer(serverProc, outThread, logFile):
	if serverProc != None:
		info("Killing server")
		serverProc.kill()
		cleanupServer(serverProc, outThread, logFile)

def cleanupServer(serverProc, outThread, logFile):
	if outThread != None:
		outThread.join()
	if logFile != None:
		logFile.close()

def exitHandler(signalType, stack):
	global serverProc
	info("Got signal %s" % (signalType))
	serverProc.kill()

outQueue = Queue()
serverArgs = " ".join(sys.argv[1:])
debug("Command line args: %s" % (serverArgs))

currentVersion = lastCheck = checkDelay = 0
serverProc = outThread = outQueue = logFile = None

signal.signal(signal.SIGINT, exitHandler)
try:
	os.mkdir("serverlogs")
except WindowsError:
	pass

try:
	while 1==1:
		if time.time() - lastCheck > checkDelay:
			debug("Checking for server update...")
			data = urllib2.urlopen(versionURL)

			temp = data.read(100).split(",")
			if temp[0] > 0 and temp[1] > 60:
				desiredVersion = temp[0]
				if checkDelay != int(temp[1]):
					checkDelay = int(temp[1])
					debug("Setting update check delay to %i" % checkDelay)

			if desiredVersion > currentVersion:
				info("Server is out of date: current: %s desired: %s" % (currentVersion,desiredVersion))
				if serverProc != None:
					stopServer(serverProc, outThread, logFile)

				if currentVersion == 0:
					update(serverDir,0)
					debug("Latest server version is %s" % (desiredVersion))
				else:
					update(serverDir,1)

				currentVersion = desiredVersion
				outThread, outQueue, serverProc, logFile = startServer(serverArgs)
			lastCheck = time.time()

		serverProc.poll()
		if serverProc.returncode != None:
			critical("Server has died, restarting!")
			cleanupServer(serverProc, outThread, logFile)
			outThread, outQueue, serverProc, logFile = startServer(serverArgs)

		# Use this to read console output without blocking
		#try:
		#	while 1==1:
		#		line = outQueue.get_nowait()
		#except Empty:
		#	pass

		time.sleep(5)
except KeyboardInterrupt:
	stopServer(serverProc, outThread, logFile)
	sys.exit(0)
except IOError:
	stopServer(serverProc, outThread, logFile)
	sys.exit(0)
