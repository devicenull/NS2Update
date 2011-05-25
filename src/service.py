import win32serviceutil, win32service, win32event
import logging, sys, time, signal, os
from logging import debug, info, warning, error, critical
from ns2update import NS2Update

class NS2UpdateService(win32serviceutil.ServiceFramework):
	_svc_name_ = 'NS2Update'
	_svc_display_name_ = 'NS2 Update'

	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		self.stop_event = win32event.CreateEvent(None, 0, 0, None)
		logging.basicConfig(level=logging.DEBUG,
							format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
							datefmt='%m-%d %H:%M',
							filename='ns2update.log',
							filemode='a')
		console = logging.StreamHandler()
		console.setLevel(logging.DEBUG)
		console.setFormatter(logging.Formatter('[NS2Update] %(levelname)-8s %(message)s'))
		logging.getLogger('').addHandler(console)
		self.logger = logging.getLogger('')

		serverArgs = " ".join(sys.argv[1:])
		serverDir = os.getcwd()
		debug("Command line args: %s" % (serverArgs))
		
		try:
			os.mkdir("serverlogs")
		except WindowsError:
			pass

		updatePath = ''
		if os.path.exists("%s/ns2update.cfg" % (serverDir)):
			debug("Found ns2update.cfg file, loading hldsupdatetool path")
			cfg = open("%s/ns2update.cfg" % (serverDir),"r")
			updatePath = cfg.readline()
			cfg.close()
			
		self.updater = NS2Update(logger=self.logger,UpdateToolPath=updatePath,serverDirectory = serverDir,serverArgs=serverArgs)

	def SvcDoRun(self):
		self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
		self.ReportServiceStatus(win32service.SERVICE_RUNNING)
		
		while win32event.WaitForSingleObject(self.stop_event, 5000) != win32event.WAIT_TIMEOUT:
			self.updater.think()
			
		self.updater.stopServer()			
		
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)
		pass

	def SvcStop(self):
		# Uhh, close more shit here
		win32event.SetEvent(self.stop_event)

if __name__ == '__main__':
	win32serviceutil.HandleCommandLine(NS2UpdateService)
