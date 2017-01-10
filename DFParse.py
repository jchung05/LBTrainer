import urllib, re, requests, time, LogIn
from BeautifulSoup import BeautifulSoup


class DFParse:
	def __init__(self):
		### You'll need to provide the DF ID here for me to parse #########
		### Otherwise it does the most recent DF by default ###############
		self.id = 3283746
		###########################################
		
		self.li = LogIn.LogIn()
		self.myfile = file( self.li.my_dir + "DFLog.txt", 'w' )
		self.li.timestamp(self.myfile,'===============End of DF Log===============\n')
		
		self.arenaLink = filter( lambda x: 'Ask me for the link' in x, self.li.menuUrls )[0]
		
	def getUrl(self,id):
		s = self.li.session.get(self.arenaLink)
		soup = BeautifulSoup( s.text )
		
		# Move to the first page of DF history
		historyUrl = soup.find(href=re.compile('Ask me for the link'))
		#print historyUrl
		if not historyUrl:
			historyUrl = soup.find(href=re.compile('Ask me for the link'))
		#print historyUrl
		
		s = self.li.session.get(historyUrl['href'])
		soup = BeautifulSoup( s.text )
		
		self.url = soup.find(href=re.compile('Ask me for the link']
		
		
	def getPages(self,soup):		
		ul = soup.find('ul',{'class':'pc-pager largewide'})
		pNums = ul.findAll('li')
		return pNums
		
	def getNextPage(self,soupArr):
		#print soupArr
		for idx,item in enumerate(soupArr):
			try:
				if item['class']=='now' or item['class']=='now over-hundreds':
					print soupArr[idx+1].getText()
					return soupArr[idx+1].find('a')['href']
					break
				else:
					pass
			except KeyError: # element does not have a class
				pass
		return None
	
	def isNextPage(self):
		pass
		
	# Collect the ten divs for each page
	def getDivs(self,soup):
		section = soup.find({'section' : 'imglist battle-history nohead'})
		divs = section.findAll('div',{'class' : re.compile(r'(live-history|live-history  opponent)')})
		
		for div in divs:
			if 'live-history opponent' in div['class']:
				self.myfile.write( self.getPs(div) + '\n~~~~~~~~~ENEMY PROD~~~~~~~~~~' )
			else:
				self.myfile.write( self.getPs(div) + '\n---------YOUR PROD-----------' )
	
	# Parse for paragraphs and then reconcatenate them after stringify()
	def getPs(self,div):
		texts = div.findAll('p')
		
		str = ''
		
		for text in texts:
			str += self.stringify(text)
		return str
		
	# Strip all HTML out and correctly format the results into readable format
	def stringify(self,text):
		str = text.getText()
		str = re.sub(r'(\d)([A-Z])', r'\1 \2', str)
		str = re.sub(r'(!+)', r'\1\n', str)
		str = re.sub(r'^(\d+:)', r'\n\1', str)
		return str

dfp = DFParse()
dfp.getUrl(dfp.id)
soup = BeautifulSoup(dfp.li.session.get(dfp.url).text)
dfp.getDivs(soup)
next = dfp.getNextPage(dfp.getPages(soup))
while next:
	s = dfp.li.session.get(next)
	time.sleep(1)
	soup = BeautifulSoup(s.text)
	dfp.getDivs(soup)
	next = dfp.getNextPage(dfp.getPages(soup))