import json, time, cherrypy
from Queue import Empty
from threading import Thread
from authcontroller import require

def updateLogList(slu):
	while 1==1:
		logUpdated = False
		if slu.updater.outputQueue != None:
			try:
				line = slu.updater.outputQueue.get_nowait()
				#print "Assign '%s' to %i" % (line,slu.currentpos)
				slu.loglist[slu.currentpos] = line+"\n"
				slu.currentpos = (slu.currentpos+1) % slu.MAXLOGENTRIES
				logUpdated = True
			except Empty:
				pass
		if slu.updater.chatQueue != None:
			try:
				line = slu.updater.chatQueue.get_nowait()
				#print "Assign '%s' to %i" % (line,slu.currentpos)
				slu.chatlist[slu.currentchatpos] = line+"\n"
				slu.currentchatpos = (slu.currentchatpos+1) % slu.MAXLOGENTRIES
				logUpdated = True
			except Empty:
				pass
		# If we found any data in the logs, immediately try to get more
		# If we didn't find any, delay for a second before we check again
		# This ensures that we dont delay for 1s between printing every line in a stack trace
		if not logUpdated:
			time.sleep(1)

class ServerLogUpdater:
	def __init__(self, webserver, updater):
		self.webserver = webserver
		self.updater = updater
		self.currentpos = 0
		self.currentchatpos = 0
		self.MAXLOGENTRIES = 1000
		self.loglist = ['']*self.MAXLOGENTRIES
		self.chatlist = ['']*self.MAXLOGENTRIES
		self.logThread = Thread(target=updateLogList, args=(self,))
		self.logThread.daemon = True
		self.logThread.start()

	@require()
	@cherrypy.expose
	def index(self,logpos=None):
		if logpos == None:
			logpos = self.currentpos
		else:
			logpos = int(logpos)

		newentries = ''
		if logpos < self.currentpos:
			newentries = ''.join(self.loglist[logpos:self.currentpos])
			logpos = self.currentpos

		if logpos > self.currentpos:
			# we've wrapped around the end!
			newentries = ''.join(self.loglist[logpos:self.MAXLOGENTRIES]) + ''.join(self.loglist[0:self.currentpos])
			logpos = self.currentpos

		cherrypy.response.headers['content-type'] = 'application/json'
		return json.dumps({'pos':logpos,'entries':newentries})

	@require()
	@cherrypy.expose
	def chat(self,logpos=None):
		if logpos == None:
			logpos = self.currentchatpos
		else:
			logpos = int(logpos)

		newentries = ''
		if logpos < self.currentchatpos:
			newentries = ''.join(self.chatlist[logpos:self.currentchatpos])
			logpos = self.currentchatpos

		if logpos > self.currentpos:
			# we've wrapped around the end!
			newentries = ''.join(self.chatlist[logpos:self.MAXLOGENTRIES]) + ''.join(self.chatlist[0:self.currentchatpos])
			logpos = self.currentchatpos

		cherrypy.response.headers['content-type'] = 'application/json'
		return json.dumps({'pos':logpos,'entries':newentries})