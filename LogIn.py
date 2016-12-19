import urllib, re, requests, time, datetime

class LogIn(object):
	### PUT EMAIL AND PASSWORD HERE ###
	username = ''
	password = ''
	###################################

	def __init__(self):
		### Put a directory path here for a log of all the people you whoop on ###
		self.my_dir="c:\Users\User 1\Desktop\\"
		# Pick this if you want a new file every time you start the script
		#self.myfile = file( self.my_dir + "LBlog.txt", 'w' )
		# Pick this if you want to keep one gigantic log of all your attempts
		self.myfile = file( self.my_dir + "LBlog.txt", 'a' )
		self.myfile.write('===============Start of Script===============\n')
		self.myfile.write(datetime.datetime.now().strftime('%Y-%m-%d') + '\n')
		self.timestamp(self.myfile,'Start')
		###################################
		self.session = requests.Session()
		
		self._zz = self.tryLogIn()
		self.url = 'Ask me for the link' + self._zz
		self._myPage()
		
	_menuUrls = []
	
	def _myPage(self):
		s = self.session.get(self.url)
		
		self.QP = self.getQP(s)
		self.SP = self.getSP(s)
		self.maxQP = self._getMaxQP(s)
		self.maxSP = self._getMaxSP(s)		
		self.openSocialId = self._openSocialId(s)
		self.myPageUrl = self._myPageUrl(s)
		self.menuUrls = set(self._menuUrls(s,self.openSocialId))
		
	def _myPageUrl(self, s):
		regex = re.compile('Ask me for the link')
		
		m = regex.search(s.text).group(0)
		g = self.session.get(m)
		
		regex = re.compile('Ask me for the link')
		
		myPageUrl = regex.search(g.text).group(0)
		if myPageUrl:
			self.timestamp(self.myfile,'MyPage URL Generated')
			self.timestamp(self.myfile,('Current QP: ' + str(self.QP) + '/' + str(self.maxQP)))
			self.timestamp(self.myfile,('Current SP: ' + str(self.SP) + '/' + str(self.maxSP)))
			print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S - ') + 'Ready to run!'
			print 'Current QP: ' + str(self.QP) + '/' + str(self.maxQP)
			print 'Current SP: ' + str(self.SP) + '/' + str(self.maxSP)
		else:
			self.myfile.write('Could not generate MyPage URL\n')
		return myPageUrl
		
	def _menuUrls(self, s, id):
		#Menu Links regex
		regex = re.compile("javascript:iframeLink\('([^']+)'\);")
		
		#All matches are unicode strings and must be stringified
		menuUrls = [ str('Ask me for the link' + str(id)) for x in regex.findall(s.text) ]
		return menuUrls
		
	
	def _openSocialId(self, s):
		#Open Social Viewer ID regex
		regex = re.compile('var opensocial_viewer_id\s*=\s*(\d+);')
		
		openSocialId = regex.search(s.text).group(1)
		if openSocialId:
			self.timestamp(self.myfile,'Social ID Established')
		else:
			self.myfile.write('Could not find Social ID\n')
		return openSocialId

		
	def tryLogIn(self):
		maxAttempts = 10
		for i in range(maxAttempts):
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
		time.sleep(1)
		
		payload = {
			'url':'Ask me for the link',
			'Ask me for the link',
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
		time.sleep(1)
		
		regex = re.compile('\\\\"zz\\\\":\\\\"([\w|\d]+)')

		zz = regex.search(g.text).group(1)
		if zz:
			self.timestamp(self.myfile,'ZZ Token')
		else:
			self.myfile.write('Could not find zz token\n')
		return zz
		
	def _pageCode(self):
		response = self.session.get('Ask me for the link')

		regex = re.compile('<input type=\"hidden\" name=\"page\" value=\"([^\"]+)\"')
		
		page = regex.search(response.text).group(1)
		if page:
			self.timestamp(self.myfile,'Page Code')
		else:
			self.myfile.write('Could not find page code\n')
		return page
		
	def _gadgetToken(self):
		#Open IWZ
		response = self.session.get('Ask me for the link')

		regex = re.compile('<iframe src=\"(Ask me for the link')
		
		link = regex.search(response.text).group(1).replace('&amp;','&')
		idx = (link.index('&st=') + 4) if '&st=' in link else None
		idx2 = link[idx:].index('&') if '&' in link[idx:] else -1

		#Gadget Token needed to continue
		sub = urllib.unquote(link[idx2:]) if idx2 > 0 else link[idx:]
		if sub:
			self.timestamp(self.myfile,'Gadget Token')
		else:
			self.myfile.write('Could not find gadget token\n')
		return urllib.unquote(sub) #Convert stripped unicode chars
		
	def _getMaxQP(self,s):
		regex = re.compile('<span>QP\ (\d+)\/(\d+)')
		m = regex.search(s.text)
		return m.group(2)
	
	def getQP(self,s):
		regex = re.compile('<span>QP\ (\d+)\/')
		m = regex.search(s.text)
		return m.group(1)
	
	def _getMaxSP(self,s):
		regex = re.compile('<span>SP\ (\d+)\/(\d+)')
		m = regex.search(s.text)
		return m.group(2)
	
	def getSP(self,s):
		regex = re.compile('<span>SP\ (\d+)\/')
		m = regex.search(s.text)
		return m.group(1)
	
	def timestamp(self,file,str):
		sttime = datetime.datetime.now().strftime('%H:%M:%S')
		file.write(sttime + ': ' + str + '\n')
