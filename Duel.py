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
		self.itemLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
		
		#Run one instance to check for your win streak prior to starting
		s = self.li.session.get(self.getLink())
		soup = BeautifulSoup(s.text)
		self.currentStreak = self.getStreak(soup)
		streakString = 'You have ' + str(self.currentStreak) + ' wins before starting' if self.currentStreak is not 1 else 'You have ' + str(self.currentStreak) + ' win before starting'
		print streakString
		self.li.timestamp(self.li.myfile, streakString)
		
		self.levelLimit = 120
		self.totalFights = 0
		#self.promotion = False
		
	def loadLBPage(self,link):
		s = self.li.session.get(self.getLink())
		soup = BeautifulSoup(s.text)
		divsoup = soup.find('div', { 'class' : 'duel-select-duelists-tab' })
		
		print self.getLink()
		
		if self.li.getSP(self.li.session.get(self.li.url)) < 20:
			self.recoverSP()
		
		#Checks if you are currently fighting a promotion battle
		promo = self.isPromo(divsoup)
		msg = ''
		if promo:
			msg = 'Preparing for a promotion battle'
			print msg
			self.li.timestamp(self.li.myfile, msg)
			
			#Start your promotion battle here
			self.fightDuelist(promo)
			
			#Checks if you won your promotion battle
			self.didIWinPromo(divsoup)
		else:
			before = self.getStreak(soup)
			duelist = self.analyzeDuelists(divsoup)
			
			if duelist.getLevel() < self.getLimit():
				msg = 'Preparing to fight ' + duelist.getName() + ': Level ' + str(duelist.getLevel()) + '...'
				print msg
				self.li.timestamp(self.li.myfile, msg)
				
				time.sleep(1)
				self.fightDuelist(duelist.getLink())
							
				after = self.getStreak(soup)
				self.winOrLose(before,after, duelist.getName())
			else:
				msg = 'No viable candidates from this roster. Waiting 1 minute before continuing'
				print msg
				self.li.timestamp(self.li.myfile, msg)
				time.sleep(60)
				print 'Continuing'
			
	#Check if you won then inc totalFights if there was no error in connection
	def winOrLose(self,b,a,name):
		msg = ''
		if b < a:
			msg = 'WIN: You won against ' + name + '! Currently at a ' + self.currentStreak + ' win streak'
			self.li.timestamp(self.li.myfile, msg)
			self.setTotal()
		elif b > a:
			msg = 'LOSE: You lost against ' + name
			self.li.timestamp(self.li.myfile, msg)
			self.setTotal()
		else:
			msg = 'ERROR: An error occurred attempting to fight ' + name
			self.li.timestamp(self.li.myfile, msg)
		print msg
		print 'This script ran ' + str(self.getTotal()) + ' fights so far'
			
	#Check if it is currently a promotion match
	def isPromo(self,s):	
		promo = s.find('a', { 'class' : 'duel-select-duelist-battle-btn' })['href']
		
		return str(promo) if 'create_matching' in promo else None
	
	#Check for a win in promo battle and sleep for an hour if you did to avoid promoting
	def didIWinPromo(self,s):
		didI = s.body.find('div', { 'class' : 'duel-select-duelists-box duel-layout-box-blue' }).text
		
		if '2' in str(didI):
			self.li.timestamp(self.li.myfile, 'You lost a promotion battle. Continuing script.')
		else:
			self.li.timestamp(self.li.myfile, 'Won a promotion battle, will sleep for an hour before continuing')
			time.sleep(3600)
		
	#Parse the list of fighters to determine the lowest leveled one
	def analyzeDuelists(self,s):
		soup = s.findAll('div', {'class' : 'duel-select-duelists-box duel-layout-box-blue'})
		
		levels = []
		players = []
		links = []
		
		for x in soup:			
			levels.append(int(x.find('dd', {'class' : 'fc-red' }).text))
			players.append(str(x.find('p', { 'class' : 'fc-red bold' }).text))
			links.append(str(x.find('a', { 'class' : 'duel-select-duelist-battle-btn' })['href']))
		
		weakest = levels.index(min(levels))
		
		return self.Duelist(levels[weakest],players[weakest],links[weakest])
	
	#Take the link of a duelist and go to execute the fight link in the next page
	def fightDuelist(self,url):
		#<a class="duel-conf-battle-btn p0" href='Ask me for the link');return false;"></a>
		time.sleep(1)
		#Execute here
		
		print url
		
	#This method is not needed if you just check streak count before and after a fight
	def battleResults(self):
		#href='Ask me for the link'
		pass
	
	#Retrieve the poorly encoded win streak value you need to check for a 100 streak
	def getStreak(self,soup):
		btns = soup.body.findAll('a', { 'class' : 'btn-common-02' })
		link = btns[1]['href']
		
		#Find the Win Streaks Reward Page
		g = self.li.session.get(link)
		soup = BeautifulSoup(g.text)
		btns = soup.body.find('ul', {'class' : 'tab'}).findAll('li')
		link = btns[2].find('a')['href']
		
		#Find the win streak value if it exists (otherwise you don't have a streak :P)
		g = self.li.session.get(link)
		soup = BeautifulSoup(g.text)
		taC = soup.find('p', {'class' : 'taC'})
		streak = int(taC.find('span', {'class' : 'fc-red'}).text) if taC else 0
		
		return streak	

	#Recover SP if you have less than 20 SP	
	#Exits program if you don't have any full SP pots
	def recoverSP(self):
		s = self.li.session.get(self.getILink())
		soup = BeautifulSoup(s.text)
		
		regex = re.compile('Ask me for the link')
		
		m = regex.search(s.text).group(0))
		
		if m:
			self.li.session.get('http://' + str(m))
		else:
			print 'You\'re out of SP pots, dummy! Exiting...'
			msg = 'Exiting due to lack of full SP pots. The script fought a total of ' + self.getTotal() + ' matches and the current streak is ' + self.getStreak() 
			self.li.timestamp(self.li.myfile, msg)
		
		
	#The set of methods to set your units after you've won against lots of lower levels
	def hrSetTeam(self):
		pass
		
	def hrUnsetTeam(self):
		pass
		
	#The default set of methods to set your units when you start the script
	def setTeam(self):
		pass
	
	def unsetTeam(self):
		pass
		
	def getLink(self):
		return self.duelLink
		
	def getILink(self):
		return self.itemLink
		
	def getLimit(self):
		return self.levelLimit
		
	def setLimit(self,value):
		self.levelLimit = value
		
	def getTotal(self):
		return self.totalFights
		
	def setTotal(self,value=1):
		self.totalFights += value
		
	class Duelist:
		def __init__(self,level,name,link):
			self.name = name
			self.level = level
			self.link = link
			
		def getName(self):
			return self.name
			
		def getLevel(self):
			return self.level
		
		def getLink(self):
			return self.link
		
duel = Duel()
#duel.loadLBPage(duel.duelLink)
duel.recoverSP()
#duel.getStreak(duel.duelLink)
'''
li = LogIn.LogIn()
len(li.menuUrls)
for url in li.menuUrls:
	print url'''
	
#members = [attr for attr in dir(Duel()) if not callable(attr) and not attr.startswith("__")]
#print members   