import urllib, re, requests, time, LogIn
from BeautifulSoup import BeautifulSoup

class Scouting(object):
	def __init__(self):
		self.li = LogIn.LogIn()
		self.scoutLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
	
	# Refresh the state of self.homeUrl to check for bosses	
	def getScouting(self):
		soup = BeautifulSoup(self.li.session.get(self.scoutLink).text)
		soup = soup.find(href=re.compile('Ask me for the link'))
		
		if soup:
			soup = self.getBossList(soup['href'])
		else:
			soup = None
			print 'No bosses available'
		
		time.sleep(2)
		return soup
		
	# Get the current list of bosses if possible
	def getBossList(self,url):
		s = self.li.session.get(url)
		time.sleep(.2)
		soup = BeautifulSoup(s.text).find('div',{'class':'sp-wrap'})
		soup = soup.findAll('div',{'class':'rewardframe-pink marB15'})
		soup = self.filterNew(soup)
		
		return soup
	
	# Take list of bosses and search for first [New] boss or return None
	def filterNew(self,soupArr):
		for soup in soupArr:
			if soup.span.text and ('[New]' in soup.span.text):
				soup = soup.find('div',{'class':'marT10 taR'})
				soup = soup.find('a')
				#print soup['href']
				return soup['href']
		print 'No new bosses'
		return None
		
	# Take the returned link and attack the boss if possible
	def attack(self,url):
		if url:
			s = self.li.session.get(url)
			soup = BeautifulSoup(s.text)
			soup = soup.find('div',{'class':'row taC'})
			soup = soup.find('a') if soup else None
			time.sleep(1)
			
			print 'Attempting to attack the boss...'
			if soup:
				s = self.li.session.get(soup['href'])
			else:
				print "    Too slow, the boss died"
		
			
sc = Scouting()
while True:
	scout = sc.getScouting()
	sc.attack(scout)
	

			