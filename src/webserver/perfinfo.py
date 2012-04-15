import json, cherrypy
from authcontroller import require

class PerfInfo:
	def __init__(self, webserver, updater):
		self.webserver = webserver
		self.updater = updater

	@cherrypy.expose
	def index(self):
		cherrypy.response.headers['content-type'] = 'application/json'
		return json.dumps({
			'cpu': self.updater.lastCPU
			,'memory': int(self.updater.lastMemory)
			,'tickrate': self.updater.lastTickrate
		})
