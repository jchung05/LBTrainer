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
'''

class Duel(object):
	### SET YOUR OWN BASIC AND HIGH RISK LEVEL LIMITS HERE ###
	### THE SCRIPT WILL NOT FIGHT ANYONE HIGHER THAN THOSE LEVELS ###
	levelLimit = 500
	highLimit = 500
	
	### I AM CURRENTLY SET TO EXIT OUT AFTER YOU WIN 100 IN A ROW 
	### CHANGE ME IF YOU WANT ME TO DO MORE THAN 1 FULL STREAK AT A TIME
	multipleStreaks = False
	
	### Is this the first time you ran the script today?
	firstRun = True
	
	### SET HOW MANY FIGHTS YOU WANT ME TO DO ###
	goal = 300
	###################################	
	totalFights = 0
	timeOut = 0
	wins = 0
	losses = 0
	
	def __init__(self):
		self.li = LogIn.LogIn()
		self.duelLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
		self.itemLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
		self.deckLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
		
		# Run one instance to check for your win streak prior to starting
		s = self.li.session.get(self.getLink())
		soup = BeautifulSoup(s.text)
		self.setStreak(soup)
		streakString = 'You have ' + str(self.getStreak()) + ' wins before starting' if self.getStreak() is not 1 else 'You have ' + str(self.getStreak()) + ' win before starting'
		print(streakString)
		self.li.timestamp(self.li.myfile, streakString)
		
	def loadLBPage(self,link):
		before = self.getStreak()
		# Remove your team before you generate the arena
		self.unsetTeam() if before < 100 else self.setTeam()
		s = self.li.session.get(self.getLink())
		soup = BeautifulSoup(s.text)
		divsoup = soup.find('div', { 'class' : 'duel-select-duelists-tab' })
		
		SP = self.li.getSP(self.li.session.get(self.li.url))
		print('Current SP: ' + str(SP))
		if int(SP) < 20:
			self.recoverSP()
		
		# Checks if you are currently fighting a promotion battle
		promo = self.isPromo(divsoup)
		# Checks if you won your last promotion battle
		if promo:
			if self.didIWinPromo(divsoup):	
				self.promoStrip()
				self.fightDuelist(promo,'promo')
				self.setTeam()
		elif before >= 100:
			#self.exit100()# if not self.multipleStreaks else 
			self.killYourself(divsoup)
			self.setStreak(soup)
		else:
			duelist = self.analyzeDuelists(divsoup)
			
			limit = 850 if (self.firstRun and self.totalFights < 15) else self.getLimit()
			
			if duelist and duelist.getLevel() < limit:
				msg = 'Preparing to fight ' + duelist.getName() + ': Level ' + str(duelist.getLevel()) + '...'
				print(msg)
				self.setTeam()
				self.li.timestamp(self.li.myfile, msg)
				
				self.fightDuelist(duelist.getLink())
				
				self.setStreak(soup)
				after = self.getStreak()
				self.winOrLose(before,after,duelist.getName())
			elif self.getTO() < 20:
				msg = 'No viable candidates from this roster. Waiting 30 seconds before continuing'
				print(msg)
				self.li.timestamp(self.li.myfile, msg)
				time.sleep(30)
				print('Continuing')
				self.setTO(self.getTO() + 1)
			else:
				msg = 'I couldn\'t find a reasonable opponent within the last 10 minutes. Consider changing your level limits. Exiting...'
				self.defaultExit(msg)
			
	# Check if you won then inc totalFights if there was no error in connection
	def winOrLose(self,b,a,name):
		msg = ''
		if b < a:
			self.wins += 1
			msg = '    WIN: You won against ' + name + '! Currently at a ' + str(a) + ' win streak'
			self.li.timestamp(self.li.myfile, msg)
			self.setTotal()
		elif b > a or a is 0:
			self.losses += 1
			msg = '    LOSE: You lost against ' + name
			self.li.timestamp(self.li.myfile, msg)
			self.setTotal()
		else:
			msg = '    ERROR: An error occurred attempting to fight ' + name
			self.li.timestamp(self.li.myfile, msg)
		print(msg)
		print('    This script ran ' + str(self.getTotal()) + ' fights so far' + ' (' + str(self.wins) + '-' + str(self.losses) + ')')
			
	# Check if it is currently a promotion match
	def isPromo(self,s):
		links = s.findAll('a', href=re.compile('Ask me for the link'))
		promo1 = [x for x in links if 'create_matching' in x['href']]
		promo2 = [x for x in links if 'matching' in x['href']]
		
		promo = None
		if promo1:
			promo = promo1[0]['href']
		elif promo2:
			promo = promo2[0]['href']
		return promo
	
	# Check for a win in promo battle and sleep for an hour if you did to avoid promoting
	def didIWinPromo(self,s):
		didI = s.find('div', { 'class' : 'duel-select-duelists-box duel-layout-box-blue' }).text
		
		msg = ''
		
		if '2' in str(didI):
			msg = 'Preparing for a promotion battle'
			print(msg)
			self.li.timestamp(self.li.myfile, msg)
			return True
		else:
			msg = 'Won a promotion battle, will sleep for an hour before continuing'
			print(msg)
			self.li.timestamp(self.li.myfile, msg)
			time.sleep(3600)
			print('Continuing')
			return False
			
	# Take the very last units as your leaders for promotional battles to reduce the risk of winning
	def promoStrip(self):
		s = self.li.session.get( self.deckLink )
		soup = BeautifulSoup(s.text)
		LIVE = soup.body.find('a', href=re.compile('Ask me for the link'))
		time.sleep(.2)
		
		s = self.li.session.get(LIVE['href'])
		soup = BeautifulSoup(s.text)
		ranks = soup.body.findAll('a', href=re.compile('Ask me for the link'))[2:]
		ranks.insert(0,LIVE)
		
		for rank in ranks:
			s = self.li.session.get( rank['href'] )
			soup = BeautifulSoup(s.text)
			leader = soup.find('a', href=re.compile('Ask me for the link'))
			time.sleep(.2)
			
			# Select which unit you want
			s = self.li.session.get(leader['href'])
			soup = BeautifulSoup(s.text)
			ul = soup.find('ul', {'class':'pc-pager-blue'})
			last = ul.findAll('li')[-1].find('a')
			time.sleep(.2)
			
			# Go to last page and extract the last unit as leaders
			s = self.li.session.get(last['href'])
			soup = BeautifulSoup(s.text)
			lastUnit = soup.findAll('div', {'class':'image-card card-column-7 deck-table-cell'})[-1]
			lastUnit = lastUnit.find('a', href=re.compile('Ask me for the link'))
			time.sleep(.2)
			
			s = self.li.session.get(lastUnit['href'])
			
		print('Removed your team leaders for promo!')
			
		
	# Parse the list of fighters to determine the lowest leveled one
	def analyzeDuelists(self,s,lowest=True):
		soup = s.findAll('div', {'class' : 'duel-select-duelists-box duel-layout-box-blue'})
		
		# Return None type if no units populate the roster
		if not soup or 'There are not opponents' in soup[0].text:
			return None
		
		levels = []
		players = []
		links = []
		
		for x in soup:			
			levels.append(int(x.find('dd', {'class' : 'fc-red' }).text))
			players.append(str(x.find('p', { 'class' : 'fc-red bold' }).text))
			links.append(str(x.find('a', { 'class' : 'duel-select-duelist-battle-btn' })['href']))
		
		# Returns weakest otherwise returns strongest for killing yourself
		weakest = levels.index(min(levels)) if lowest is True else levels.index(max(levels))
		
		return self.Duelist(levels[weakest],players[weakest],links[weakest])
	
	# Take the link of a duelist and go to execute the fight link in the next page
	def fightDuelist(self,url,promo=False):
		time.sleep(.4)
		s = self.li.session.get(url)
		soup = BeautifulSoup(s.text)
		
		fightLink = soup.find('a', href=re.compile('^Ask me for the link']
		
		# Execute fight here
		time.sleep(.2)
		self.li.session.get(fightLink)
		self.setTO(0)

	
	def getStreak(self):
		return self.currentStreak
	
	# Retrieve the poorly encoded win streak value you need to check for a 100 streak
	def setStreak(self,soup):
		btns = soup.body.findAll('a', { 'class' : 'btn-common-02' })
		link = btns[1]['href']
		
		# Find the Win Streaks Reward Page
		g = self.li.session.get(link)
		soup = BeautifulSoup(g.text)
		btns = soup.body.find('ul', {'class' : 'tab'}).findAll('li')
		link = btns[2].find('a')['href']
		
		# Find the win streak value if it exists (otherwise you don't have a streak :P)
		g = self.li.session.get(link)
		soup = BeautifulSoup(g.text)
		taC = soup.find('p', {'class' : 'taC'})
		self.currentStreak = int(taC.find('span', {'class' : 'fc-red'}).text) if taC else 0

	# Recover SP if you have less than 20 SP	
	# Exits program if you don't have any full SP pots
	def recoverSP(self):
		time.sleep(.2)
		s = self.li.session.get(self.getILink())
		soup = BeautifulSoup(s.text)
		
		regex = re.compile('Ask me for the link')
		
		m = regex.search(s.text).group(0)
		
		if m:
			print('    Recovering SP')
			self.li.timestamp(self.li.myfile, 'Recovering SP')
			self.li.session.get('Ask me for the link' + str(m))
		else:
			print('    You\'re out of SP pots, baka! Exiting...')
			msg = 'Exiting due to lack of full SP pots. The script fought a total of ' + self.getTotal() + ' matches and the current streak is ' + self.getStreak() 
			self.li.timestamp(self.li.myfile, msg)
			
	def exit100(self):
	#def killYourself(self):
		if self.getStreak() >= 100:
			message = 'Exiting out as you\'ve reached 100 wins. Don\'t forget to kill yourself!'
			self.defaultExit(message)

	# A method which checks for streaks over 100 and attempts to kill you to reset it			
	def killYourself(self,soup):
		duelist = self.analyzeDuelists(soup,False)
		
		msg = 'This is a streak killing match. Preparing to fight ' + duelist.getName() + ': Level ' + str(duelist.getLevel()) + '...'
		print(msg)
		self.unsetTeam()
		self.li.timestamp(self.li.myfile, msg)
		
		self.fightDuelist(duelist.getLink())
			
	# A method for exiting out of the program after meeting your limit or timing out
	def defaultExit(self,message):
		print(message)
		self.li.timestamp(self.li.myfile, message)
		exit()
		
		
	# The set of methods to set your units after you've won against lots of lower levels
	def hrSetTeam(self):
		pass
		
	def hrUnsetTeam(self):
		pass
		
	# The default set of methods to set your units when you start the script
	def setTeam(self):
		s = self.li.session.get( self.deckLink )
		soup = BeautifulSoup(s.text)
		LIVE = soup.body.find('a', href = re.compile('Ask me for the link']
		time.sleep(.2)
		
		s = self.li.session.get(LIVE)
		soup = BeautifulSoup(s.text)
		balanced = soup.body.findAll('form')[1].get('action')
		
		payload = {
			'sort_1':'1'
		}
		s = self.li.session.post(balanced, params=payload)
		print('Fixed your team!')
		time.sleep(.2)
		
	
	def unsetTeam(self):
		s = self.li.session.get( self.deckLink )
		soup = BeautifulSoup(s.text)
		LIVE = soup.body.find('a', href = re.compile('Ask me for the link']
		time.sleep(.2)
		
		s = self.li.session.get(LIVE)
		soup = BeautifulSoup(s.text)
		removeAll = soup.find('a', href = re.compile( 'Ask me for the link'))
		
		# If it doesn't exist, that means the team is already stripped
		if removeAll:
			s = self.li.session.get(removeAll['href'])
			time.sleep(.2)
			print('Removed your team!')
			
		
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