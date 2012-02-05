import json, cherrypy
from logging import debug, info, warning, error, critical

class ServerController:
	def __init__(self, webserver, updater):
		self.webserver = webserver
		self.updater = updater

	@cherrypy.expose
	def index(self):
		tmpl = self.webserver.template_env.get_template('layout.html')
		return tmpl.render(rcon_available=self.updater.serverConfig['webadminActive'],page='index.html',username=self.webserver.getLogin())

	@cherrypy.expose
	def restart(self):
		self.updater.stopServer()
		self.updater.startServer()
		return json.dumps({'status':'OK'})
