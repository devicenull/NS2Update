import urllib2, subprocess, sys, os, time
from threading import Thread
from Queue import Queue, Empty
from time import strftime


def enqueue_output(out, queue, logFile):
	for line in iter(out.readline,''):
		queue.put(line)
		logFile.write(line)
		logFile.flush()
	out.close()

class NS2Update:
	# Handle to the process where the server is running
	serverProc = None
	# outputThread will be a seperate thread that is spawned to grab all the output from the server
	# It will push it all into outputQueue, as well as to serverLogFile
	# outputQueue is currently unused, but will ultimately allow actions to be taken based on log events
	outputQueue = None
	outputThread = None
	serverLogFile = None
	# Time of the last update check
	lastCheck = 0
	# How often we should check for updates.  This is set by the update server
	checkDelay = 300
	# What URL to grab the latest version from.  Ideally we would grab this from the CDR on the fly
	# but that's not terribly resource-friendly to do
	versionURL = "http://ns2update.devicenull.org/ns2update/ns2version.txt"
	# What version of the software is the server currently running
	currentVersion = 0
	# What arguments should we pass to the server on startup
	serverArgs = ''

	def __init__(self, logger, UpdateToolPath, serverDirectory, serverArgs):
		self.logger = logger
		self.findUpdateTool(UpdateToolPath)
		self.serverDir = serverDirectory
		self.serverArgs = serverArgs

	def findUpdateTool(self,extraPath):
		paths = [ "../hldsupdatetool.exe", "hldsupdatetool.exe" ]

		if extraPath != None and extraPath != '':
			paths.append(extraPath)

		self.updatePath = ""
		for cur in paths:
			if os.path.exists(cur):
				self.updatePath = cur

		if self.updatePath == "":
			self.logger.critical("Unable to find hldsupdatetool.exe, please copy to server directory or see README")
			raise NameError("Unable to find hldsupdatetool.exe")

	def doUpdate(self):
		self.logger.info("Starting server update")

		update = subprocess.Popen("%s -command update -game naturalselection2 -dir %s" % (self.updatePath,self.serverDir))
		if update:
			while update.returncode == None:
				time.sleep(5)
				update.poll()

		self.logger.info("Server update complete!")

	def startServer(self):
		# Actually start the server process
		self.serverProc = subprocess.Popen("Server.exe %s" % self.serverArgs, stdin=None, stdout=subprocess.PIPE)
		self.logger.info("Server started, pid %i" % (self.serverProc.pid))

		# Open up the log file
		logName = strftime("%Y.%m.%d.%H%M.log")
		self.logger.debug("Logging to %s" % logName)
		self.serverLogFile = open("serverlogs/%s" % logName,"a")

		# Setup everything we need to capture the server output
		self.outputQueue = Queue()
		self.outputThread = Thread(target=enqueue_output, args=(self.serverProc.stdout, self.outputQueue, self.serverLogFile))
		self.outputThread.daemon = True
		self.outputThread.start()

	def stopServer(self):
		if self.serverProc != None:
			self.logger.info("Killing server")
			self.serverProc.kill()
			self.cleanupServer()

	def cleanupServer(self):
		if self.outputThread != None:
			self.outputThread.join()
		if self.serverLogFile != None:
			self.serverLogFile.close()
		self.outputThread = None
		self.serverLogFile = None
		self.serverProc = None

	def think(self):
		if time.time() - self.lastCheck > self.checkDelay:
			self.logger.debug("Checking for server update...")
			data = urllib2.urlopen(self.versionURL)

			temp = data.read(100).split(",")
			if temp[0] > 0 and temp[1] > 60:
				desiredVersion = temp[0]
				if self.checkDelay != int(temp[1]):
					self.checkDelay = int(temp[1])
					self.logger.debug("Setting update check delay to %i" % self.checkDelay)

			if desiredVersion > self.currentVersion:
				self.logger.info("Server is out of date: current: %s desired: %s" % (self.currentVersion,desiredVersion))
				if self.serverProc != None:
					self.stopServer()

				if self.currentVersion == 0:
					self.logger.info("Performing inital server update")
					self.doUpdate()
				else:
					self.doUpdate()

				self.currentVersion = desiredVersion
				self.startServer()
			self.lastCheck = time.time()

		self.serverProc.poll()
		if self.serverProc.returncode != None:
			self.logger.critical("Server has died, restarting!")
			self.cleanupServer()
			self.startServer()

		# Use this to read console output without blocking
		#try:
		#	while 1==1:
		#		line = outQueue.get_nowait()
		#except Empty:
		#	pass
