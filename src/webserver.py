import cherrypy, atexit, time, json, os
from Queue import Empty
from threading import Thread
from jinja2 import Environment, FileSystemLoader

template_env = Environment(loader=FileSystemLoader('ns2update/templates'))

def updateLogList(slu):
	while 1==1:
		try:
			line = slu.updater.outputQueue.get_nowait()
			print "Assign '%s' to %i" % (line,slu.currentpos)
			slu.loglist[slu.currentpos] = line
			slu.currentpos = (slu.currentpos+1) % slu.MAXLOGENTRIES
		except Empty:
			time.sleep(1)

class ServerLogUpdater:
	updater = None
	loglist = None

	def __init__(self, updater):
		self.updater = updater
		self.logThread = None
		self.currentpos = 0
		self.MAXLOGENTRIES = 1000
		self.loglist = ['']*self.MAXLOGENTRIES

	@cherrypy.expose
	def index(self,logpos=None):
		if self.logThread == None:
			self.logThread = Thread(target=updateLogList, args=(self,))
			self.logThread.daemon = True
			self.logThread.start()

		if logpos == None:
			logpos = self.currentpos
		else:
			logpos = int(logpos)

		print "Logpos: %i Currentpos: %i" % (logpos,self.currentpos)
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

class ServerRcon:
	updater = None

	def __init__(self, updater):
		self.updater = updater

	@cherrypy.expose
	def index(self,command=None):
		self.updater.sendCommand(command)

		return json.dumps({'status':'OK'})

class ServerInfo:
	updater = None

	def __init__(self, updater):
		self.updater = updater

	@cherrypy.expose
	def index(self):
		details = self.updater.queryObject.details()

		cherrypy.response.headers['content-type'] = 'application/json'
		return json.dumps({
			'current_players': details['current_playercount']
			,'max_players': details['max_players']
			,'server_name': details['server_name']
			,'map': details['current_map']
		})

class ServerController:
	updater = None

	def __init__(self, updater):
		self.updater = updater

	@cherrypy.expose
	def index(self):
		tmpl = template_env.get_template('index.html')
		return tmpl.render(test1="hello",test2="world")


class WebServer:
	updater = None

	def __init__(self, updater):
		self.updater = updater
		cherrypy.config.update({"global": {"server.thread_pool": 10}})
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
		}
		cherrypy.tree.mount(ServerLogUpdater(updater=updater), '/serverlog')
		cherrypy.tree.mount(ServerRcon(updater=updater), '/rcon')
		cherrypy.tree.mount(ServerInfo(updater=updater), '/info')
		cherrypy.tree.mount(ServerController(updater=updater),'/',config)
		cherrypy.engine.start()
		atexit.register(cherrypy.engine.stop)
