from logging import handlers, debug, info, warning, error, critical
import cherrypy, atexit, time, json, os, logging
from jinja2 import Environment, FileSystemLoader


from authcontroller import AuthController
from serverlog import ServerLogUpdater
from serverinfo import ServerInfo
from serverrcon import ServerRcon
from servercontroller import ServerController
from perfinfo import PerfInfo

class WebServer:
	updater = None

	def __init__(self, updater):
		self.template_env = Environment(loader=FileSystemLoader('ns2update/templates'))

		self.updater = updater
		cherrypy.config.update({"global": {"server.thread_pool": 10, "tools.sessions.on": True, "tools.auth.on": True}})
		config = {
			'/css':
				{ 'tools.staticdir.on': True,
				'tools.staticdir.dir': os.path.join(os.getcwd(),'ns2update/css/')
				}
			, '/img':
				{ 'tools.staticdir.on': True,
				'tools.staticdir.dir': os.path.join(os.getcwd(),'ns2update/img/')
				}
			,'/js':
				{ 'tools.staticdir.on': True,
				'tools.staticdir.dir': os.path.join(os.getcwd(),'ns2update/js/')
				}
			,'/ns2server.png':
				{
				'tools.staticfile.on': True,
				'tools.staticfile.filename': os.path.join(os.getcwd(),'ns2server.png')
				}
		}

		cherrypy.log.error_log.setLevel(logging.WARNING)
		cherrypy.log.access_log.setLevel(logging.WARNING)
		cherrypy.tree.mount(AuthController(webserver=self),'/auth')
		cherrypy.tree.mount(ServerLogUpdater(webserver=self,updater=updater), '/serverlog')
		cherrypy.tree.mount(ServerInfo(webserver=self,updater=updater), '/info')
		cherrypy.tree.mount(PerfInfo(webserver=self,updater=updater), '/perf')
		app = cherrypy.tree.mount(ServerController(webserver=self,updater=updater),'/',config)
		app.log.access_log.setLevel(logging.WARNING)
		app.log.error_log.setLevel(logging.WARNING)


		if updater.serverConfig['webadminActive'] == 'true':
			cherrypy.tree.mount(ServerRcon(webserver=self,updater=updater), '/rcon')
			cherrypy.tree.apps['/rcon'].log.access_log.setLevel(logging.WARNING)
			cherrypy.tree.apps['/rcon'].log.error_log.setLevel(logging.WARNING)

		cherrypy.server.socket_host = updater.serverConfig['webadminDomain']
		cherrypy.server.socket_port = int(updater.serverConfig['webadminPort'])+1

		cherrypy.tree.apps['/serverlog'].log.access_log.setLevel(logging.WARNING)
		cherrypy.tree.apps['/serverlog'].log.error_log.setLevel(logging.WARNING)
		cherrypy.tree.apps['/info'].log.access_log.setLevel(logging.WARNING)
		cherrypy.tree.apps['/info'].log.error_log.setLevel(logging.WARNING)
		cherrypy.tree.apps['/perf'].log.access_log.setLevel(logging.WARNING)
		cherrypy.tree.apps['/perf'].log.error_log.setLevel(logging.WARNING)

		cherrypy.engine.start()
		atexit.register(cherrypy.engine.stop)

	def getLogin(self):
		return cherrypy.session.get('_cp_username')