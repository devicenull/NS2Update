# Default config:
#<options>
#    <mapName>ns2_rockdown</mapName>
#    <address></address>
#    <playerLimit>10</playerLimit>
#    <webadminActive>false</webadminActive>
#    <webadminPort>8080</webadminPort>
#    <game></game>
#    <lanGame>false</lanGame>
#    <password></password>
#    <port>27015</port>
#    <serverName>NS2 Dedicated Server</serverName>
#    <webadminDirectory>./web</webadminDirectory>
#    <webadminDomain>localhost</webadminDomain>
#</options>

import argparse, os
from logging import debug, info, warning, error, critical
from xml.dom.minidom import parse

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

class NS2Config(dict):
	def __init__(self,cmdline,serverdir):
		self.serverdir = serverdir
		self.config = {
			'mapName': 'ns2_mineshaft'
			,'address': '127.0.0.1'
			,'playerLimit': 10
			,'webadminActive': 0
			,'webadminPort': 8080
			,'game': ''
			,'lanGame': 0
			,'password': ''
			,'port': 27015
			,'serverName': 'NS2 Dedicated Server'
			,'webadminDirectory': './web'
			,'webadminDomain': 'localhost'
			,'file': 'server.xml'
		}
		self.parseCmdLine(cmdline)

		configfilepath = {
			os.path.join('.',self.config['file'])
			,os.path.join(serverdir,'server.xml')
			,os.path.join(os.environ['APPDATA'], 'Natural Selection 2', 'server.xml')
		}

		configloaded = False
		for configfile in configfilepath:
			if os.path.exists(configfile):
				info("Checking NS2 server config file %s" % configfile)
				self.parseConfig(configfile)
				configloaded = True
				break
			else:
				error("Checking NS2 server config file %s: file does not exist" % configfile)

		if not configloaded:
			error("No NS2 server configuration could be found.")
			info("Please specify the path to the NS2 server config file with the parameter -file #Filepath#.")
			info("Using default config settings %s" % self.config)

	def parseCmdLine(self,cmdline):
		argParser = argparse.ArgumentParser(prog='NS2')
		argParser.add_argument('-file',default='server.xml')
		argParser.add_argument('-name',default='NS2 Dedicated Server')
		argParser.add_argument('-map',default='ns2_rockdown')
		argParser.add_argument('-ip',default='127.0.0.1')
		argParser.add_argument('-port',default=27015)
		argParser.add_argument('-limit',default=10)
		argParser.add_argument('-lan',default=0)
		argParser.add_argument('-password',default='')
		argParser.add_argument('-game',default='')
		argParser.add_argument('-save',default=0)

		try:
			parsed,otherargs = argParser.parse_known_args(cmdline.split(' '))
			self.config['file'] = parsed.file
			self.config['serverName'] = parsed.name
			self.config['mapName'] = parsed.map
			self.config['address'] = parsed.ip
			self.config['port'] = parsed.port
			self.config['playerLimit'] = parsed.limit
			self.config['lanGame'] = parsed.lan
			self.config['password'] = parsed.password
			self.config['game'] = parsed.game
			self.config['save'] = parsed.save
		except:
			pass

	def parseConfig(self,configFile):
		dom = parse(configFile)
		options = dom.getElementsByTagName('options')[0]
		options.normalize()
		for node in options.childNodes:
			if node.nodeName == '#text':
				continue
			data = getText(node.childNodes).encode('ascii')
			#print node.nodeName, getText(node.childNodes)
			if data != "":
				self.config[node.nodeName] = data

	def __getitem__(self,name):
		return self.config[name]

	def __contains__(self,name):
		return self.config.contains(name)

	def has_key(self,name):
		return self.config.has_key(name)

#test = NS2Config('-ip 192.168.5.3 -file server.xml -map whatthefuck',os.getcwd())
