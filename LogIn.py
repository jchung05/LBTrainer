import BeautifulSoup, urllib, urllib2, httplib, re, requests, time, datetime

class LogIn:
	### PUT EMAIL AND PASSWORD HERE AT OWN DISCRETION ###
	username = ''
	password = ''
	###################################

	def __init__(self):
		### Put a directory path here for a log of all the people you whoop on ###
		self.my_dir="c:\Users\User 1\Desktop\\"
		self.myfile = file( self.my_dir + "log.txt", 'w' )
		self.timestamp(self.myfile,'Start')
		###################################
		self.session = requests.Session()

		self._zz = self.tryLogIn()
		self._myPageUrl, self._menuUrls, self._openSocialId = self._myPage()
		
	_menuUrls = []
	
	def _myPage(self):
		s = self.session.get('Ask me for the link' + self._zz)
		
		sId = self._openSocialId(s)
		
		regex = re.compile('Ask me for the link')
		
		if not regex.findall(s.text) or not self._openSocialId:
			return False
		m = regex.findall(s.text)[0]
		g = self.session.get(m)
		
		regex = re.compile('Ask me for the link')
		
		myPageUrl = regex.findall(g.text)[0]
		if myPageUrl:
			self.timestamp(self.myfile,'MyPage URL Generated')
			print "Ready to run!"
		else:
			self.myfile.write('Could not generate MyPage URL\n')
		return myPageUrl, self._menuUrls(s,sId), sId
		
	def _menuUrls(self, s, id):
		#Menu Links regex
		regex = re.compile("javascript:iframeLink\('([^']+)'\);")
		
		#All matches are unicode strings and must be stringified
		menuUrls = [ str('Ask me for the link' + id) for x in regex.findall(s.text) ]
		return menuUrls
		
	
	def _openSocialId(self, s):
		#Open Social Viewer ID regex
		regex = re.compile('var opensocial_viewer_id\s*=\s*(\d+);')
		
		openSocialId = regex.findall(s.text)[0]
		if openSocialId:
			self.timestamp(self.myfile,'Social ID Established')
		else:
			self.myfile.write('Could not find Social ID\n')
		return openSocialId

		
	def tryLogIn(self):
		for i in range(10):
			zz = self._zzId()
			if zz:
				return zz
			self.timestamp(myfile,'Login' + i +' failed')
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
		self.session.post('Ask me for the link',params=payload)
		
		payload = {
			'url':'Ask me for the link',
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
			'gadget':'Ask me for the link',
			'container':'nutaku',
			'bypassSpecCache':'1',
			'getFullHeaders':'false',
			'oauthState':''
		}
		#Retrieve thrown file with MyPage zz token
		g = self.session.get('Ask me for the link',params=payload)
		
		regex = re.compile('\\\\"zz\\\\":\\\\"([\w|\d]+)')

		zz = regex.findall(g.text)[0]
		#zz = regex.findall(g.text)[0] if regex.findall(g.text) else None
		if zz:
			self.timestamp(self.myfile,'ZZ Token')
		else:
			self.myfile.write('Could not find zz token\n')
		return zz
		
	def _pageCode(self):
		response = self.session.get('Ask me for the link')

		regex = re.compile('<input type=\"hidden\" name=\"page\" value=\"([^\"]+)\"')
		
		page = regex.findall(response.text)[0]
		#page = regex.findall(response.text)[0] if regex.findall(response.text) else None
		if page:
			self.timestamp(self.myfile,'Page Code')
		else:
			self.myfile.write('Could not find page code\n')
		return page
		
	def _gadgetToken(self):
		#Open IWZ
		response = self.session.get('Ask me for the link')

		regex = re.compile('<iframe src=\"(Ask me for the link')
		
		link = regex.findall(response.text)[0].replace('&amp;','&')
		#link = regex.findall(response.text)[0].replace('&amp;','&') if regex.findall(response.text) else None
		idx = (link.index('&st=') + 4) if '&st=' in link else None
		idx2 = link[idx:].index('&') if '&' in link[idx:] else -1

		#Gadget Token needed to continue
		sub = urllib.unquote(link[idx2:]) if idx2 > 0 else link[idx:]
		if sub:
			self.timestamp(self.myfile,'Gadget Token')
		else:
			self.myfile.write('Could not find gadget token\n')
		return urllib.unquote(sub) #Convert stripped unicode chars

	def timestamp(self,file,str):
		sttime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S - ')
		file.write(str + ': ' + sttime + '\n')
