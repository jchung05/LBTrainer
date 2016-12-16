import urllib, re, requests, time, LogIn
from BeautifulSoup import BeautifulSoup

'''
This module contains all battle data and aims to earn a 100 win battle streak. 
After 100 wins, you kill yourself and start again. Fights are determined by a 
level threshold set by the user; all candidates for duels will be below that 
threshold. There is a "High Risk" flag that activates on default after 200
wins that will change both the level threshold and how your team is stripped.
User can also determine whether to collect all their rewards after a completed
streak or not. If a user lacks enough SP pots the script will exit.

LOGS ARE NOT CSV FRIENDLY

Things you need to change on your own:
	Level threshold
	High Risk flag
	High Level threshold
	Flag to collect goodies after a streak

'''

class Duel(object):
	def __init__(self):
		self.li = LogIn.LogIn()
		self.duelLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
		
		#self.analyzeDuelists()
		#s = self.li.session.get(self.duelLink)
		#self.li.myfile.write(s.text.encode('utf-8'))
		self.totalFights = 0
		self.currentStreak = 0
		self.promotion = False
		
	def recoverSP():
		pass
		
	def isPromo():
		pass
		
	def analyzeDuelists(self):
		r = self.li.session.get(self.duelLink)
		soup = BeautifulSoup(r.text)
		
		levels = soup.findAll("dd", { "class" : "fc-red" })
		print levels
		#duelists = soup.body.p['fc-red bold']
		duelists = soup.findAll("p", { "class" : "fc-red bold" })
		print duelists
	
	def getStreak():
		pass
		
	def getTotal():
		pass
		
	class Duelist:
		name = ''
		level = 0