import json, cherrypy

class ServerRcon:
	def __init__(self, webserver, updater):
		self.webserver = webserver
		self.updater = updater

	@cherrypy.expose
	def index(self,command=None):
		self.updater.serverRcon.sendCommand(command)

		return json.dumps({'status':'OK'})

	@cherrypy.expose
	def players(self):
		players = self.updater.serverRcon.getPlayers()

		cherrypy.response.headers['content-type'] = 'application/json'
		return json.dumps(players)