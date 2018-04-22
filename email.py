import sys,string, random, time, os, platform, datetime, json

from selenium import webdriver
from random import randint
#from pyvirtualdisplay import Display #used for virtual X environment
from browsertools import Browser

systeminforma = sys.platform

def pass_gen(size=8, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits + '!'):
	return ''.join(random.choice(chars) for _ in range(size))

def register(email, password, proxy, key):
	print("ok\n attempting registration of", email, "password is:", password)

	b = Browser()
	b.size = ["1600", "900"]
	if proxy == "none":
		proxy = ""
		print("[NTWK] Using local IP.") 
	else: 
		b.setProxyChrome(proxy)
		print("[NTWK] Using proxy " + proxy)
	if 'linux' in systeminforma:
		b.startHidden()
		b.startDriverChrome()
	else:
		b.startDriverChrome('res/chromedriver.exe')
		#b.hide()
	try:
		#b.driver.get("http://service.mail.com/registration.html")
		time.sleep(3)
		b.driver.find_element_by_id("id11f").click()
		b.driver.find_element_by_id("id121").click()
		b.driver.find_element_by_id("id128").click()
		#Select(b.driver.find_element_by_id("id128")).select_by_visible_text("Jan")
		b.driver.find_element_by_id("id128").click()
		b.driver.find_element_by_id("id125").click()
		#Select(b.driver.find_element_by_id("id125")).select_by_visible_text(str(randint(1,26)))
		b.driver.find_element_by_id("id125").click()
		b.driver.find_element_by_id("id129").click()
		#Select(b.driver.find_element_by_id("id129")).select_by_visible_text(str(randint(1960,1995)))
		b.driver.find_element_by_id("id129").click()
		b.driver.find_element_by_id("id132").click()
		b.driver.find_element_by_id("id132").clear()
		b.driver.find_element_by_id("id132").send_keys(email)
		b.driver.find_element_by_id("id13c").click()
		b.driver.find_element_by_id("id13c").clear()
		b.driver.find_element_by_id("id13c").send_keys(password)
		b.driver.find_element_by_id("id13f").click()
		b.driver.find_element_by_id("id13f").clear()
		b.driver.find_element_by_id("id13f").send_keys(password)
		b.driver.find_element_by_id("id144").click()
		try:
			b.driver.execute_script("arguments[0].scrollIntoView()", b.driver.find_element_by_id("id147"))
		except:
			print('cannot scroll')
		b.driver.find_element_by_id("id147").click()
		b.driver.find_element_by_id("id147").click()
		b.driver.find_element_by_xpath("//a[@id='id134']/span").click()
		b.driver.find_element_by_id("id147").click()
		time.sleep(1)
		#Select(b.driver.find_element_by_id("id147")).select_by_visible_text("What was the make of your first car?")
		b.driver.find_element_by_id("id147").click()
		b.driver.find_element_by_id("id149").click()
		b.driver.find_element_by_id("id149").clear()
		b.driver.find_element_by_id("id149").send_keys("security answer")

		val = None
		try:
			b.driver.find_element_by_id('google-recaptcha') #if there is a captcha so solve
			val = b.solveReCaptcha(key)
			b.driver.execute_script('document.getElementById("g-recaptcha-response").value = "' + val + '"')
			print('value inside try', val)
		except:
			print('error solving captcha')

		b.driver.find_element_by_id("id14e").click()
		time.sleep(3)
		print("account registered \n")
	except:
		print("error, restart please. Could not find assets or page crashed.")
		sys.exit(1)
	b = None

def main():
	try: emails = sys.argv[1] #get first argument
	except IndexError:
					print(" [!] Your input file is written improperly!")
					print("  Format: (program name) input.extension proxies.extension (key)\n")
					print("  Example: rsacc.py input.txt proxies.txt (key)")
					time.sleep(2)
					sys.exit(1)
					
	try: proxy = sys.argv[2] #get second argument
	except IndexError: 
		pass
		print("[!] No proxy servers detected")
		
	try: key = sys.argv[3] #get third argument
	except IndexError: 
		print("No anti-captcha key. Please add it after your proxy.")
		time.sleep(2)
		sys.exit(1)

	print("\n\n\n\n\n\n\n\n\n\n\n")
	print("  ===========================================================================")
	print("                                Runescape Account Creator")
	print("                                v.01 -------- headless edition")
	print("                                running on " + systeminforma)
	print("  ===========================================================================")
	print("\n\n\n\n\n\n\n\n")
	input_e = open(emails, 'r')
	input_p = open(proxy, 'r')
	output = open('output.txt', 'w')
	for i in input_e:
		info = i.split(',')
		password = pass_gen()
		proxy = input_p.readline().rstrip()
		register(info[0].strip(), password, proxy, key)
		output.write(str (info[0]) + ',' + str(info[1].strip()) + ',' + password + ',' +  str(proxy))

if __name__ == "__main__":
	main()