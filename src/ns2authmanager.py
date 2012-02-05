import os, hashlib

class NS2AuthManager:

	def __init__(self,filename):
		self.filename = filename

	def getUsers(self):
		if not os.path.exists(self.filename):
			return []

		users = []
		passwdfile = os.path.join(self.filename)
		f = open(passwdfile,'r')
		for line in f:
			data = line.strip().split(':')
			if len(data) != 3:
				continue;
			users.append({
				'username': data[0]
				,'domain': data[1]
				,'password': data[2]
			})
		f.close()
		print users
		return users

	# For the given username, domain entry: add the user if it is not present, or update it's password if it is
	def updateUser(self,username,domain,password):
		username = username.strip()
		domain = domain.strip()
		password = password.strip()

		users = self.getUsers()
		for key, user in enumerate(users):
			if user['username'] == username and user['domain'] == domain:
				users[key]['password'] = hashlib.md5("%s:%s:%s" % (username,domain,password)).hexdigest()
				self.saveUsers(users)
				return

		users.append({
			'username': username
			,'domain': domain
			,'password': hashlib.md5("%s:%s:%s" % (username,domain,password)).hexdigest()
		})

		self.saveUsers(users)

	def saveUsers(self,users):
		newContents = ""
		for user in users:
			newContents += "%s:%s:%s\n" % (user['username'],user['domain'],user['password'])

		f = open(self.filename,'w')
		f.write(newContents)
		f.close()

	def hasUser(self,username,domain,password):
		username = username.strip()
		domain = domain.strip()
		password = password.strip()
		hashedpw = hashlib.md5("%s:%s:%s" % (username,domain,password)).hexdigest()

		users = self.getUsers()
		for user in users:
			if user['username'] == username and user['domain'] == domain and user['password'] == hashedpw:
				return True

		return False