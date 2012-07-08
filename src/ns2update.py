import subprocess, os, time
from time import strftime

class NS2Update:
	# Handle to the process where the server is running
	serverProc = None
	# Time of the last update check
	lastCheck = 0
	# What version of the software is the server currently running
	currentVersion = 0

	def __init__(self, logger, config):
		self.logger = logger
		self.config = config

		self.findUpdateTool()


	def get(self,key):
		return self.config.get('ns2update',key,'')

	def getBool(self,key):
		return self.config.getboolean('ns2update',key)

	def findUpdateTool(self):
		if self.getBool('noUpdateCheck'):
			self.logger.info("Update checking disabled, not looking for steamcmd")
			return

		paths = [ "../steamcmd.exe", "steamcmd.exe", self.get('steamcmd_binary') ]

		steamCmd = '';
		for cur in paths:
			if os.path.exists(cur):
				steamCmd = cur

		if steamCmd == "":
			self.logger.critical("Unable to find steamcmd.exe, please copy to server directory or see README")
			raise NameError("Unable to find steamcmd.exe")

		self.config.set('ns2update','steamcmd_binary',steamCmd)

	def doUpdate(self):
		self.logger.info("Starting server update")

		update = subprocess.Popen("%s +login %s %s +force_install_dir %s +app_update %s verify +quit" % (self.get('steamcmd_binary'),self.get('steamcmd_user'),self.get('steamcmd_password'),self.get('server_directory'),self.get('steamcmd_appid')))
		if update:
			while update.returncode == None:
				time.sleep(5)
				update.poll()

		self.logger.info("Server update complete!")

	def startServer(self):
		# If we are starting the server, it must be empty
		self.serverEmptyCount = 0
		self.hasHadPlayers = False

		# Actually start the server process
		self.serverProc = subprocess.Popen("Server.exe %s" % self.get('server_args'), shell=True)
		self.logger.info("Server started, pid %i version %s" % (self.serverProc.pid,self.currentVersion))

	def stopServer(self):
		if self.serverProc != None:
			self.logger.info("Killing server")
			self.serverProc.kill()
			self.cleanupServer()

	def cleanupServer(self):
		self.serverProc = None

	def think(self):
		if not self.getBool('noUpdateCheck') and time.time() - self.lastCheck > 300:
			desiredVersion = self.getCurrentSteamVersion()

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

		if self.serverProc == None:
			self.startServer()

		self.serverProc.poll()
		if self.serverProc.returncode != None:
			self.logger.critical("Server has died, restarting!")
			self.cleanupServer()
			self.startServer()

	def getCurrentSteamVersion(self):
		self.logger.debug("Checking for server update...")
		return 1
