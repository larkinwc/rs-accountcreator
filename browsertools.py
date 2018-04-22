from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask, ImageToTextTask
from pyvirtualdisplay import Display 
import random, time, email, imaplib, string, os, datetime

def wait(min=1, max=3):
	if min > max:
		max = min + 1
	time.sleep(round(random.uniform(min, max), 2))
	
def generateData(length=10, digits=True, letters=True, characters=False, upper=True, lower=True):
	source = ""
	if digits == True:
		source += string.digits
	if letters == True:
		if upper == True:
			source += string.ascii_uppercase
		if lower == True:
			source += string.ascii_lowercase
	if characters == True:
		source += """!@#$%^&*()_+-="'[],./;':"""
	output = ""
	for i in range(length):
		output += random.choice(source)
	return output
		

class Browser:
	def __init__(self):
		self.profile = None
		self.browserType = 'firefox'
		self.driver = None
		self.prefs = {}
		self.captchaAPI = {"text": "", "recaptcha": ""}
		self.auth = ""
		self.size = ""
		self.display = None #used for virtual frame buffer
		
	def startDriver(self, browser='Firefox', profile=None, exec_path = './chromedriver'):
		browser = browser.lower()
		self.browserType = browser
		if browser == 'firefox':
			if self.profile == None:
				self.profile = webdriver.FirefoxProfile()
			if profile == None:
				profile = self.profile
			self.driver = webdriver.Firefox(profile)
		if self.auth:
			self.setProxyAuth(self.auth)
		if self.size:
			self.driver.set_window_size(self.size[0], self.size[1]) 
		self.driver.implicitly_wait(10)
		return self.driver

	def startDriverChrome(self, exec_path = "./chromedriver"):
		self.browserType = 'chrome'
		if self.profile == None:
			self.profile = webdriver.ChromeOptions()
		self.profile.add_argument("--disable-dev-tools")
		self.profile.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36")
		self.driver = webdriver.Chrome(chrome_options = self.profile, executable_path = exec_path)
		if self.size:
			self.driver.set_window_size(self.size[0], self.size[1]) 
		self.driver.implicitly_wait(10)
		return self.driver
	
	def setPref(self, target, value):
		if self.driver == None and self.profile != None:
			self.profile.set_preference(target, value)
		elif self.driver != None:
			ac = ActionChains(self.driver)
			ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
			ac.send_keys('pref set {} {}'.format(target, str(value))).perform()
			ac.send_keys(Keys.ENTER).perform()
			ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
			ac.key_down(Keys.SHIFT).send_keys(Keys.F2).key_up(Keys.SHIFT).perform()
		else:
			return False
		self.prefs[str(target)] = value
	
	def setProxy(self, proxy, auth="", types=["http", "https", "ftp", "socks", "ssl"]):
		if "@" in proxy:
			auth, proxy = proxy.split('@')
		self.proxy, self.proxyp = proxy.split(':')
		self.setPref("network.proxy.type", 1)
		self.auth = auth
		for eachType in types:
			proxystring = 'network.proxy.' + eachType
			self.setPref(proxystring, self.proxy)
			self.setPref(proxystring + '_port', int(self.proxyp))
		if self.driver and auth:
			self.setProxyAuth(auth)

	def setProxyChrome(self, proxy):
		if self.profile == None:
			self.profile = webdriver.ChromeOptions()
		self.proxy, self.proxyp = proxy.split(':')
		print(self.proxy, self.proxyp)
		self.profile.add_argument("--proxy-server=" + self.proxy + ':' + self.proxyp)
		
			
	def setProxyAuth(self, auth):
		auth = self.auth.split(":")
		time.sleep(1)
		while True:
			try:
				alert = self.driver.switch_to_alert()
				alert.send_keys(auth[0])
				break
			except:
				time.sleep(0.5)
		alert.send_keys(Keys.TAB + auth[1])
		alert.accept() 
		self.auth = auth
	
	def getScrollPosition(self, axis='y'):
		return self.driver.execute_script("return window.page{}Offset;".format(axis.upper()))
	
	def getSiteKey(self):
		try:
			sitekey = self.driver.find_element_by_class_name("g-recaptcha").get_attribute('data-sitekey')
		except:
			sitekey = self.driver.find_element_by_class_name("NoCaptcha").get_attribute('data-sitekey')
		return sitekey
	
	def solveTextCaptcha(self, captcha, min_length=None, max_length=None, digits=True, letters=True, characters=True, lower=True, upper=True, language="en", retries=3):
		captchafile = generateData(16) + ".png"
		self.savePic(captcha, captchafile)
		captcha_fp = open(captchafile, 'rb')
		client = AnticaptchaClient(self.captchaAPI['text'])
		task = ImageToTextTask(captcha_fp, min_length=min_length, max_length=max_length)
		job = client.createTask(task)
		job.join()        
		captchatxt = job.get_captcha_text()
		t = 0
		#if length and length != len(captchatxt):
		 #   t = 1
		if t != 1:
			for everyChar in captchatxt:
				if digits == False and everyChar in string.digits:
					t = 1
					break
				if language == "en":
					if letters == False and everyChar in string.ascii_letters:
						t = 1
						break
					if lower == False and everyChar in string.ascii_lowercase:
						t = 1
						break
					if upper == False and everyChar in string.ascii_uppercase:
						t = 1
						break
				
		if t == 1:
			return self.solveTextCaptcha(captcha, min_length, max_length, digits, letters, characters, lower, upper, language, retries)
		return captchatxt
	
	def solveReCaptcha(self, api, sitekey = None):
		if sitekey == None:
			sitekey = self.getSiteKey()
		client = AnticaptchaClient(api)
		task = NoCaptchaTaskProxylessTask(self.driver.current_url, sitekey)
		job = client.createTask(task)
		job.join()
		code = job.get_solution_response()
		#self.inject("g-recaptcha-response", code, "id") #for me, right now this is unreliabily injecting
		return code
		
	def setUseragent(self, value):
		self.setPref('general.useragent.override', value)
		self.useragent = value

	def randomType(self, target, value, min=0.1, max=1.1):
		for eachChar in value:
			target.send_keys(eachChar)
			wait(min, max)
			
	def setWindowSize(self, sizes=["1920x1080", "1366x768", "1280x1024", "1280x800", "1024x768"], handle='current'):
		t = random.choice(sizes).split('x')
		if self.driver == None:
			self.size = t
		else:
			self.driver.set_window_size(t[0], t[1], handle)
			  
	def get(self, url):
		finished = 0
		i = 0
		while finished == 0:
			if i > 5:
				return False
			try:
				self.driver.get(url)
				finished = 1
			except:
				wait()
				i += 1
		return True
	
	def savePic(self, elem, output):
		location = elem.location
		size = elem.size
		offset = self.getScrollPosition()
		location['y'] += offset
		self.driver.save_screenshot(output)
		image = Image.open(output)
		left = location['x']
		top = location['y']
		right = location['x'] + size['width']
		bottom = location['y'] + size['height']
		image = image.crop((left, top, right, bottom))
		image.save(output, 'png')        
		
	def select(self, elem, by, value):
		t = Select(elem)
		if by == 'value':
			t.select_by_value(value)
		elif by == 'index':
			t.select_by_index(value)
	
	def scrollTo(self, elem='', y='', x=''):
		if elem:
			self.driver.execute_script("return arguments[0].scrollIntoView();", elem)
			self.driver.execute_script("window.scrollBy(0, -150);")
		if y:
			self.driver.execute_script("window.scrollTo(" + str(y) + ", Y)")
		if x:
			self.driver.execute_script("window.scrollTo(" + str(x) + ", X)")
	
	def hide(self):
		self.driver.set_window_position(-3000, 0)
		self.hidden = True
	
	def unhide(self):
		self.driver.set_window_position(0, 0)
		self.hidden = False
		
	def startHidden(self):
		if(not self.size):
			self.setWindowSize()
		self.display = Display(visible=0, size=(self.size[0], self.size[1])).start() 

	def inject(self, target, value, elemtype='id'):
		print('value',value)
		elemtype = elemtype.lower()
		getelemstring = "getElementBy{}"
		if elemtype == 'id':
			getelemstring.format('Id')
		self.driver.execute_script('document.' + getelemstring + '(' + target + ').value = "' + value + '"')

if __name__ == "__main__":
	b = Browser()
	b.startDriver()
