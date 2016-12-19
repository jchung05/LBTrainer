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
	### SET YOUR OWN BASIC AND HIGH RISK LEVEL LIMITS HERE ###
	### THE SCRIPT WILL NOT FIGHT ANYONE HIGHER THAN THOSE LEVELS ###
	levelLimit = 400
	highLimit = 500
	### SET HOW MANY FIGHTS YOU WANT ME TO DO ###
	goal = 50
	###################################	
	totalFights = 0
	timeOut = 0
	
	def __init__(self):
		self.li = LogIn.LogIn()
		self.duelLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
		self.itemLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
		self.deckLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
		
		#Run one instance to check for your win streak prior to starting
		s = self.li.session.get(self.getLink())
		soup = BeautifulSoup(s.text)
		self.setStreak(soup)
		streakString = 'You have ' + str(self.getStreak()) + ' wins before starting' if self.getStreak() is not 1 else 'You have ' + str(self.getStreak()) + ' win before starting'
		print streakString
		self.li.timestamp(self.li.myfile, streakString)
		#self.promotion = False
		
	def loadLBPage(self,link):
		#Remove your team before you generate the arena
		self.unsetTeam()
		s = self.li.session.get(self.getLink())
		soup = BeautifulSoup(s.text)
		divsoup = soup.find('div', { 'class' : 'duel-select-duelists-tab' })
		
		self.killYourself()
		
		SP = self.li.getSP(self.li.session.get(self.li.url))
		print 'Current SP: ' + str(SP)
		if int(SP) < 20:
			self.recoverSP()
		
		#Checks if you are currently fighting a promotion battle
		promo = self.isPromo(divsoup)
		msg = ''
		if promo:
			msg = 'Preparing for a promotion battle'
			print msg
			self.li.timestamp(self.li.myfile, msg)
			
			#Start your promotion battle here
			self.fightDuelist(promo,'promo')
			
			#Checks if you won your promotion battle
			self.didIWinPromo(divsoup)
		else:
			before = self.getStreak()
			duelist = self.analyzeDuelists(divsoup)
			
			if duelist.getLevel() < self.getLimit():
				msg = 'Preparing to fight ' + duelist.getName() + ': Level ' + str(duelist.getLevel()) + '...'
				print msg
				self.setTeam()
				self.li.timestamp(self.li.myfile, msg)
				
				self.fightDuelist(duelist.getLink())
				
				self.setStreak(soup)
				after = self.getStreak()
				self.winOrLose(before,after,duelist.getName())
			else:
				if self.getTO() < 10:
					msg = 'No viable candidates from this roster. Waiting 1 minute before continuing'
					print msg
					self.li.timestamp(self.li.myfile, msg)
					time.sleep(60)
					print 'Continuing'
					self.setTO(self.getTO() + 1)
				else:
					msg = 'I couldn\'t find a reasonable opponent within the last 10 minutes. Consider changing your level limits. Exiting...'
					self.defaultExit(msg)
			
	#Check if you won then inc totalFights if there was no error in connection
	def winOrLose(self,b,a,name):
		msg = ''
		if b < a:
			msg = '    WIN: You won against ' + name + '! Currently at a ' + str(a) + ' win streak'
			self.li.timestamp(self.li.myfile, msg)
			self.setTotal()
		elif b > a or (a is 0 and b is 0):
			msg = '    LOSE: You lost against ' + name
			self.li.timestamp(self.li.myfile, msg)
			self.setTotal()
		else:
			msg = '    ERROR: An error occurred attempting to fight ' + name
			self.li.timestamp(self.li.myfile, msg)
		print msg
		print '    This script ran ' + str(self.getTotal()) + ' fights so far'
			
	#Check if it is currently a promotion match
	def isPromo(self,s):
		promo1 = s.find('a', href=re.compile('Ask me for the link'))
		promo2 = s.find('a', href=re.compile('Ask me for the link'))
		
		promo = None
		if promo1:
			promo = promo1['href']
		elif promo2:
			promo = promo2['href']
		return promo
	
	#Check for a win in promo battle and sleep for an hour if you did to avoid promoting
	def didIWinPromo(self,s):
		didI = s.find('div', { 'class' : 'duel-select-duelists-box duel-layout-box-blue' }).text
		
		msg = ''
		
		if '2' in str(didI):
			msg = 'You lost a promotion battle'
			print msg
			self.li.timestamp(self.li.myfile, msg)
		else:
			msg = 'Won a promotion battle, will sleep for an hour before continuing'
			print msg
			self.li.timestamp(self.li.myfile, msg)
			time.sleep(3600)
			print 'Continuing'
		
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
	def fightDuelist(self,url,type='fight'):
		time.sleep(.4)
		s = self.li.session.get(url)
		soup = BeautifulSoup(s.text)
		
		fightLink = soup.find('a', href=re.compile('^Ask me for the link']
		
		#Execute here
		time.sleep(.4)
		self.li.session.get(fightLink)
		self.setTO(0)
		
	
	def getStreak(self):
		return self.currentStreak
	
	#Retrieve the poorly encoded win streak value you need to check for a 100 streak
	def setStreak(self,soup):
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
		self.currentStreak = int(taC.find('span', {'class' : 'fc-red'}).text) if taC else 0
		
		#return streak

	#Recover SP if you have less than 20 SP	
	#Exits program if you don't have any full SP pots
	def recoverSP(self):
		time.sleep(.4)
		s = self.li.session.get(self.getILink())
		soup = BeautifulSoup(s.text)
		
		regex = re.compile('Ask me for the link')
		
		m = regex.search(s.text).group(0)
		
		if m:
			print '    Recovering SP'
			self.li.timestamp(self.li.myfile, 'Recovering SP')
			self.li.session.get('http://' + str(m))
		else:
			print '    You\'re out of SP pots, dummy! Exiting...'
			msg = 'Exiting due to lack of full SP pots. The script fought a total of ' + self.getTotal() + ' matches and the current streak is ' + self.getStreak() 
			self.li.timestamp(self.li.myfile, msg)
			
	def killYourself(self):
		if self.getStreak() >= 100:
			message = 'Exiting out as you\'ve reached 100 wins. Don\'t forget to kill yourself!'
			self.defaultExit(message)
			
	#A method for exiting out of the program after meeting your limit or timing out
	def defaultExit(self,message):
		print message
		self.li.timestamp(self.li.myfile, message)
		exit()
		
		
	#The set of methods to set your units after you've won against lots of lower levels
	def hrSetTeam(self):
		pass
		
	def hrUnsetTeam(self):
		pass
		
	#The default set of methods to set your units when you start the script
	def setTeam(self):
		s = self.li.session.get( self.deckLink )
		soup = BeautifulSoup(s.text)
		LIVE = soup.body.find('a', href = re.compile('Ask me for the link']
		time.sleep(.4)
		
		s = self.li.session.get(LIVE)
		soup = BeautifulSoup(s.text)
		balanced = soup.body.findAll('form')[1].get('action')
		
		payload = {
			'sort_1':'1'
		}
		s = self.li.session.post(balanced, params=payload)
		print 'Fixed your team!'
		time.sleep(.4)
		
	
	def unsetTeam(self):
		s = self.li.session.get( self.deckLink )
		soup = BeautifulSoup(s.text)
		LIVE = soup.body.find('a', href = re.compile('Ask me for the link']
		time.sleep(.4)
		
		s = self.li.session.get(LIVE)
		soup = BeautifulSoup(s.text)
		removeAll = soup.find('a', href = re.compile( 'Ask me for the link'))
		
		#If it doesn't exist, that means the team is already stripped
		if removeAll:
			s = self.li.session.get(removeAll['href'])
			time.sleep(.4)
			print 'Removed your team!'
			
		
	def getGoal(self):
		return self.goal
		
	def getLink(self):
		return self.duelLink
		
	def getILink(self):
		return self.itemLink
		
	def getTO(self):
		return self.timeOut
		
	def setTO(self,value):
		self.timeOut = value
		
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
while duel.getTotal() < duel.getGoal():
	duel.loadLBPage(duel.duelLink)