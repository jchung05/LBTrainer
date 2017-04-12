import urllib, re, requests, time, LogIn
from BeautifulSoup import BeautifulSoup

class Roulette(object):
	def __init__(self):
		self.li = LogIn.LogIn()
		
	def findMaterialLink(self):
		s = self.li.session.get(self.li.myPageUrl)
		soup = BeautifulSoup(s.text).find(href=re.compile('Ask me for the link'))
		
		return soup['href']
		
	def getMaterialLink(self):
		link = self.findMaterialLink()
		s = self.li.session.get(link)
		soup = BeautifulSoup(s.text)
		print soup.text
		
	def findQuestLink(self):
		s = self.li.session.get(self.li.myPageUrl)
		soup = BeautifulSoup(s.text).find(href=re.compile('Ask me for the link'))
		print soup['href']
		return soup['href']
		
	def getQuestLink(self):
		link = self.findQuestLink()
		s = self.li.session.get(link)
		#soup = BeautifulSoup(s.text)
		#print soup.text
		script = BeautifulSoup(s.text).find(text=re.compile('!function'))
		#print script
		return script
		
	def createItemArr(self):
		script = self.getQuestLink()
		arr = re.findall('Ask me for the link',script)
		#arr = script.findAll(text=re.compile('Ask me for the link'))
		for x in arr:
			print x 
			
		print len(arr)
		
r = Roulette()
r.createItemArr()
