import string, os, urllib2, urllib
from random import choice
from logging import debug, info, warning, error, critical
from bs4 import BeautifulSoup
from ns2authmanager import NS2AuthManager


class NS2Rcon:
	def __init__(self,updater,serverDirectory):
		self.updater = updater
		self.serverDirectory = serverDirectory
		self.mypassword = ''.join([choice(string.letters + string.digits) for i in range(16)])
		debug("My password: %s" % self.mypassword)

		am = NS2AuthManager(os.path.join(self.updater.serverConfig['webadminDirectory'],'.htpasswd'))
		am.updateUser('ns2update',self.updater.serverConfig['webadminDomain'],self.mypassword)

		self.weburl = "http://%s:%s/" % (self.updater.serverConfig['webadminDomain'],self.updater.serverConfig['webadminPort'])

		self.passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
		self.passwd_mgr.add_password(None,self.weburl,'ns2update',self.mypassword)
		#opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1),urllib2.HTTPDigestAuthHandler(self.passwd_mgr))
		opener = urllib2.build_opener(urllib2.HTTPDigestAuthHandler(self.passwd_mgr))
		urllib2.install_opener(opener)

	def sendCommand(self,command):
		urllib2.urlopen(self.weburl,urllib.urlencode({'rcon':command,'command':'Send'}))

	def getPlayers(self):
		result = urllib2.urlopen(self.weburl)
		soup = BeautifulSoup(result.read())
		if soup.prettify() == '' or soup.body == None:
			return []

		players = []
		playertable = soup.body.find_all('table')[1]
		for row in playertable.find_all('tr'):
			columns = row.find_all('td')
			if columns[0].text == 'Player Name':
				continue

			steamid = int(columns[6].text)
			if steamid % 2 == 0:
				steamid = "STEAM_0:1:%i" % (steamid/2)
			else:
				steamid = "STEAM_0:0:%i" % (steamid/2)

			players.append({
				'name': columns[0].text
				,'team': columns[1].text
				,'score': columns[2].text
				,'kills': columns[3].text
				,'deaths': columns[4].text
				,'resources': columns[5].text
				,'steamid': steamid
				,'ping': columns[7].text
				,'ns2steamid': columns[6].text
			})

		return players