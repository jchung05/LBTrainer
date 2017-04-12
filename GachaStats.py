import urllib, re, requests, time, LogIn
from BeautifulSoup import BeautifulSoup
from collections import defaultdict

class GachaStats(object):
	def __init__(self):
		self.li = LogIn.LogIn()
		self.gacha_dict = defaultdict(list)
		self.rare_idx = -1
		self.spec_idx = -1
		self.last_val = self.Gacha("N/A","N/A","N/A","N/A")
#		self.timer = 0
		
		gachaLink = filter( lambda x: 'Ask me for the link'
		
		s = self.li.session.get( gachaLink )
		soup = BeautifulSoup( s.text ).body
		self.toolbar = self.getFirstToolbar(soup)
		
	def getFirstToolbar(self,soup):
		ul = soup.find('ul', {'class':'tab-list three'})
		li = ul.findAll('div')[1:]
		
		self.findRareIndex(li)
		self.findSpecialIndex(li)
	
		return li
		
	def getToolbar(self):
		return self.toolbar
		
	def setToolbar(self,soup):
		ul = soup.find('ul', {'class':'tab-list three'})
		li = ul.findAll('div')[1:]
	
		self.toolbar = li
		
	# Set the index for the Rare page
	def findRareIndex(self,arr):
		for idx,x in enumerate(arr):
			if x.find(text='Rare'):
				self.rare_idx = idx
	
	# Set the index for the Special page
	def findSpecialIndex(self,arr):
		for idx,x in enumerate(arr):
			if x.find(text='Special'):
				self.spec_idx = idx
		
	# Retrieve the salted URL to the Rare page and go to it
	def getRareUrl(self):
		url = self.getToolbar()[self.rare_idx].find('a')['href']
		s = self.li.session.get(url)
		soup = BeautifulSoup(s.text).body
		self.setToolbar(soup)
		self.dropScrape(soup)
		
	# Retrieve the salted URL to the Special page and go to it
	def getSpecialUrl(self):
		url = self.getToolbar()[self.spec_idx].find('a')['href']
		s = self.li.session.get(url)
		soup = BeautifulSoup(s.text).body
		self.setToolbar(soup)
		self.dropScrape(soup)
		
	# Scrape for the 5 drops on a page's list
	def dropScrape(self,soup):
		results = soup.find('section',{'class':'result-info'})
		articles = results.findAll('article')
		
		gachas = []
		for x in articles:
			info = x.findAll('p')
			owner = info[0].text
			time = info[1].text
			unit = info[2].text.split(" ")
			rarity = unit[0]
			name = (" ").join(unit[1:])
			
			gacha = self.Gacha(owner,time,rarity,name)
			gachas.append(gacha)
		
		# Search for the index of last occurring duplicate
		idx = self.dupeCheck(gachas)
		print idx
		
		for i in range(idx,5):
			self.gacha_dict[gachas[i].getTimestamp()].append(gachas[i])
			
	# Check for a duplicate item
	def dupeCheck(self,arr):
		for x in arr:
			# Return the index if a duplicate is found
			if (self.last_val.getOwner() == x.getOwner()) and (self.last_val.getTimestamp() == x.getTimestamp()) and (self.last_val.getName() == x.getName()):
				print "Duplicate found at " + str(arr.index(x))
				self.last_val = x
				return 5-arr.index(x)
			# Otherwise simply return 0 to hash the whole list
			else:
				self.last_val = x
				return 0
		return 0
		
	class Gacha:
		def __init__(self,owner,timestamp,rarity,name):
			self.owner = owner
			self.timestamp = timestamp
			self.rarity = rarity
			self.name = name
			
		def getName(self):
			return self.name
			
		def getRarity(self):
			return self.rarity
		
		def getTimestamp(self):
			return self.timestamp
		
		def getOwner(self):
			return self.owner
			
			
gs = GachaStats()
itr = 0
while itr < 5:
	gs.getRareUrl()
	time.sleep(3)
	gs.getSpecialUrl()
	time.sleep(3)
	itr += 1