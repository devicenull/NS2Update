import subprocess
import os
import time
import sys
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

		update = subprocess.Popen("%s +login %s %s +force_install_dir %s +app_update %s verify +quit" % (self.get('steamcmd_binary'),self.get('steamcmd_user'),self.get('steamcmd_password'),self.get('server_directory'),self.get('steamcmd_appid_download')))
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

			if desiredVersion != self.currentVersion:
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
		update = subprocess.Popen("%s +login %s %s +app_info_print %s +quit" % (self.get('steamcmd_binary'),self.get('steamcmd_user'),self.get('steamcmd_password'),self.get('steamcmd_appid_check')), stdout=subprocess.PIPE)

		PARSER_IN_UNKNOWN = 0
		PARSER_IN_APPINFO = 1
		PARSER_IN_DEPOTINFO = 2

		parserState = PARSER_IN_UNKNOWN
		currentVersion = ""
		for line in update.stdout:
			self.logger.debug(line.strip())
			if parserState == PARSER_IN_UNKNOWN:
				if line.startswith("\"%s\"" % (self.get('steamcmd_appid_check'))):
					parserState = PARSER_IN_APPINFO
			elif parserState == PARSER_IN_APPINFO:
				if line.strip().startswith("\"%s\"" % (self.get('steamcmd_depotid_check'))):
					parserState = PARSER_IN_DEPOTINFO
				elif line.startswith("}"):
					break
			elif parserState == PARSER_IN_DEPOTINFO:
				# Something like this:
				# "Public"                "7762996058298320329"
				if line.strip().startswith("\"Public\""):
					revLine = line[::-1].strip()
					# becomes:
					# "9230238928506992677"           "cilbuP"
					tabPos = revLine.find("\t")
					revVersion = revLine[1:tabPos-1]
					# now:
					# 9230238928506992677
					currentVersion = revVersion[::-1]
					# finally returning:
					# 7762996058298320329
					break

		try:
			update.kill()
		except WindowsError:
			pass

		return currentVersion
