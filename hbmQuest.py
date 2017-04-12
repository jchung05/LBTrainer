import urllib, re, requests, datetime, time, LogIn, AbstractQuest
from BeautifulSoup import BeautifulSoup

class hbmQuest(AbstractQuest.AbstractQuest):
	potItr = 0
	expLimit = 160
	
	def __init__(self):
		self.li = LogIn.LogIn()
	
	def returnSoup(self,url):
		s = self.li.session.get(url)
		soup = BeautifulSoup(s.text).body
		return soup
		
	def returnHome(self,url):
		self.questLink = self.findLink(self.returnSoup(url),'Ask me for the link')
	
	# Gets the new hashed Stage link and returns the exec link
	def enterStage(self,url):
		try:
			#First character's link
			self.execLink = self.findLink(self.returnSoup(url),'Ask me for the link')
			#Second character's link
			#self.execLink = self.findLink(self.returnSoup(url),'Ask me for the link')
		except:
			print("Unexpected error, moving on")
			pass
		
	# Gets the new hashed Stage exec link
	def questExec(self,url):
		try:
			s = self.li.session.get(url)
			soup = BeautifulSoup(s.text).body
			
			# Place all your logical checks here
			check = self.expCheck(soup)
			if check and check > self.expLimit:
				self.recoverQP(soup)
			elif check and check < self.expLimit:
				print 'You\'re very close to leveling. Recover your own pot and run this again.'
				exit()
			self.cheerCheck(soup)
		except:
			print("Unexpected error, moving on")
			pass
		
	def cheerCheck(self,soup):
		cheer = soup.find(href=re.compile('Ask me for the link'))
		if cheer:
			self.li.session.get(cheer['href'])
			print 'I cheered!'
		else:
			None
		
	def findLink(self,soup,reStr):
		link = soup.find(href=re.compile(reStr))
		link = link['href'] if link else None
		return link
		
	def expCheck(self,soup):
		outOfQP = soup.findAll('p',{'class':'taC'})
		if outOfQP:
			exp = outOfQP[1].find('span',{'class':'fc-red'})
			return int(exp.text)
		else:
			return None
	
	# A new developer started working on this segment. Instead of a GET with the variables embedded in the URL, they changed it to a POST with hidden values.
	def recoverQP(self,soup):		
		pot = soup.findAll(action=re.compile('Ask me for the link'))
		
		payload = {
			'item_id':'1',
			'use_num':'1',
			#'item_id':'2',
			#'use_num':'3'
		}
		#self.enterStage(url) with the posted url
		if pot and self.potItr < 10:
			time.sleep(.2)
			print('    Recovering QP...')
			self.potItr += 1
			#s = self.li.session.post(pot[0]['action'],params=payload)
			s = self.li.session.post(pot[2]['action'],params=payload)
			soup = BeautifulSoup(s.text).body
			
			#First character's link
			self.execLink = self.findLink(soup,'Ask me for the link')
			#Second character's link
			#self.execLink = self.findLink(soup,'Ask me for the link')
			
			self.enterStage(self.execLink)
		else:
			print('    You\'re out of QP pots, baka! Exiting...')
			exit()
		
		
hbmQ = hbmQuest()

while hbmQ.potItr < 10:
	hbmQ.returnHome(hbmQ.li.myPageUrl)
	time.sleep(.2)
		
	hbmQ.enterStage(hbmQ.questLink)
	time.sleep(.2)
	
	hbmQ.questExec(hbmQ.execLink)
	time.sleep(.2)
	
	print datetime.datetime.now().strftime('%H:%M:%S') + ': ' + 'Success?'
	
print('I ran ' + str(hbmQ.potItr) + ' times and now I\'m exiting.')
exit()