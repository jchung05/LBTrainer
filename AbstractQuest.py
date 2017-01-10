#Questing abstraction needs
#QP Recovery
#Exp check
#Quest execute
#Maybe roulette check/execute


from abc import ABCMeta, abstractmethod

class AbstractQuest(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def returnHome(self,url):
		pass
		
	@abstractmethod
	def findLink(self,url):
		pass
		
	@abstractmethod
	def enterStage(self,url):
		pass
		
	@abstractmethod
	def questExec(self,url):
		pass
		
	@abstractmethod
	def recoverQP(self,soup):
		pass
	
	@abstractmethod
	def expCheck(self,soup):
		pass