import BeautifulSoup, cookielib, urllib, urllib2, httplib, re, requests, time, datetime

class LogIn:
	### PUT EMAIL AND PASSWORD HERE AT OWN DISCRETION ###
	username = ''
	password = ''
	###################################

	def __init__(self):
		### Put a directory path here for a log of all the people you whoop on ###
		self.my_dir="c:\Users\User 1\Desktop\\"
		self.myfile = file( self.my_dir + "log.txt", 'w' )
		timestamp(self.myfile,'Start')
		###################################
		self.session = requests.Session()

		#This should be tryLogIn()
		#self._zz = self._zzId()
		self._zz = self.tryLogIn()
		
		
	# Not complete yet
	def getMyPage(s):
		zz = tryLogIn(s)
		'''g = s.get(url + str(zz))
		print g'''
		
		
	def tryLogIn(self):
		for i in range(10):
			zz = self._zzId()
			if zz:
				return zz
			timestamp(myfile,'Login' + i +' failed')
			time.sleep(5)
		return None
		exit()
		
	def _zzId(self):
		payload = {
			'mailAddress':self.username,
			'password':self.password,
			'autoLogin':'1',
			'page':self._pageCode(),
			'submit':'Login'
			}
		self.session.post('Ask me',params=payload)
		
		payload = {
			'url':'Ask me',
			'httpMethod':'GET',
			'headers':'',
			'postData':'',
			'authz':'signed',
			'st':self._gadgetToken(),
			'contentType':'JSON',
			'numEntries':'3',
			'getSummaries':'false',
			'signOwner':'true',
			'signViewer':'true',
			'gadget':'Ask me',
			'container':'nutaku',
			'bypassSpecCache':'1',
			'getFullHeaders':'false',
			'oauthState':''
		}
		#Retrieve thrown file with MyPage zz token
		g = self.session.get('Ask me',params=payload)
		
		regex = re.compile('\\\\"zz\\\\":\\\\"([\w|\d]+)')

		play = regex.findall(g.text)[0] if regex.findall(g.text) else None
		if play:
			timestamp(self.myfile,'ZZ Token')
		else:
			self.myfile.write('Could not find zz token\n')
		return play
		
	def _pageCode(self):
		response = self.session.get('Ask me')

		regex = re.compile('<input type=\"hidden\" name=\"page\" value=\"([^\"]+)\"')
		page = str(regex.findall(response.text)[0]) if regex.findall(response.text) else None
		if page:
			timestamp(self.myfile,'Page Code')
		else:
			self.myfile.write('Could not find page code\n')
		return str(page) #Unstrip all unicode
		
	def _gadgetToken(self):
		#Open IWZ
		response = self.session.get('Ask me')

		regex = re.compile('<iframe src=\"(http://Ask me/gadgets/ifr?[^\"]+)\"')
		link = regex.findall(response.text)[0].replace('&amp;','&') if regex.findall(response.text) else None
		idx = (link.index('&st=') + 4) if '&st=' in link else None
		idx2 = link[idx:].index('&') if '&' in link[idx:] else -1

		#Gadget Token needed to continue
		sub = urllib.unquote(link[idx2:]) if idx2 > 0 else link[idx:]
		if sub:
			timestamp(self.myfile,'Gadget Token')
		else:
			self.myfile.write('Could not find gadget token\n')
		return urllib.unquote(sub) #Convert stripped unicode chars

def timestamp(file,str):
	sttime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S - ')
	file.write(str + ': ' + sttime + '\n')
