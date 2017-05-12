import urllib, re, requests, time, LogIn
from BeautifulSoup import BeautifulSoup

class ThankYouGacha(object):
	def __init__(self):
		self.li = LogIn.LogIn()
		self.gachaLink = filter( lambda x: 'Ask me for the link'
		self.number = -1
		
		s = self.li.session.get( self.gachaLink )
		soup = BeautifulSoup( s.text ).body
		self.toolbar = self.getFirstToolbar(soup)
	
	def getFirstToolbar(self,soup):
		ul = soup.find('ul', {'class':'tab-list three'})
		li = ul.findAll('div')[1:]
		
		self.findSpecialIndex(li)
	
		return li
		
	def getToolbar(self):
		return self.toolbar
		
	def setToolbar(self,soup):
		ul = soup.find('ul', {'class':'tab-list three'})
		li = ul.findAll('div')[1:]
	
		self.toolbar = li
		
	# Set the index for the Special page
	def findSpecialIndex(self,arr):
		for idx,x in enumerate(arr):
			if x.find(text='Special'):
				self.spec_idx = idx
		
	# Retrieve the salted URL to the Special page and go to it
	def getSpecialUrl(self):
		url = self.getToolbar()[self.spec_idx].find('a')['href']
		s = self.li.session.get(url)
		soup = BeautifulSoup(s.text).body
		#print soup
		#self.setToolbar(soup)
		return soup
		
	# Find the class container for the gacha pull and the tickets left info
	def findClass(self,soup):
		gachaDiv = soup.find('div', {'class':'gacha-button-container'})
		return gachaDiv
	
	# Search for initial Gacha link with provided soup string and execute the first pull
	# Due to poor design, only one pull can be done at a time
	# Search for a recursive link in modular reuse
	def pullGacha(self,soup):
		url = soup.find('a', href=re.compile('Ask me for the link'
		#print url
		s = self.li.session.get(url)
		soup = BeautifulSoup(s.text).body
		return soup
		
	# Determine how many tickets are left and set number value to that amount
	def ticketsLeft(self,soup):
		leftText = soup.find('p', {'class':'fc-blue'}).text
		print leftText
		number = int(leftText[leftText.index(':')+1:])
		self.number = number
		
tyg = ThankYouGacha()
soup = tyg.getSpecialUrl()
tyg.ticketsLeft(soup)
while tyg.number > 1:
	soup = tyg.pullGacha(soup)
	soup = tyg.li.session.get(tyg.gachaLink)
	soup = tyg.getSpecialUrl()
	tyg.ticketsLeft(soup)
	
tyg.pullGacha(soup)