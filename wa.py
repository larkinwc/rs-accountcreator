import sys,string, random, time, os, platform, datetime, json

from selenium import webdriver
from random import randint
from pyvirtualdisplay import Display #used for virtual X environment
from browsertools import Browser
systeminforma = sys.platform

def pass_gen(size=8, chars=string.ascii_lowercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def register(email, username, password, proxy, key):
	print("ok\n attempting registration of", email, "password is:", password)

	b = Browser()
	#b.startHidden()
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
	try:
		b.get("https://secure.runescape.com/m=account-creation/g=oldscape/create_account")
		time.sleep(3)
		try:
			b.driver.find_elements_by_class_name('cc_btn_accept_all')[0].click()
		except:
			pass
		time.sleep(2)
		b.driver.find_element_by_id('create-email').send_keys(email)
		time.sleep(2)
		b.driver.find_element_by_id('create-password').send_keys(password)
		time.sleep(2)
		b.driver.find_element_by_id('display-name').send_keys(username)
		time.sleep(2)
		b.driver.find_element_by_id('create-age').send_keys(str(randint(22, 55)))
		time.sleep(2)
		try:
			login_button = b.driver.find_element_by_id('create-submit')
		except:
			print('play button not found')
		time.sleep(2)
		try:
			b.driver.execute_script("arguments[0].scrollIntoView()", login_button)
		except:
			print('cannot scroll')
		time.sleep(1)
		val = None
		try:
			b.driver.find_element_by_id('google-recaptcha') #if there is a captcha so solve
			val = b.solveReCaptcha(key, '6LccFA0TAAAAAHEwUJx_c1TfTBWMTAOIphwTtd1b') #runescape account creation sitekey, issue is they hide it with script AFAIK
			b.driver.execute_script('document.getElementById("g-recaptcha-response").value = "' + val + '"')
			print('value inside try', val)
		except:
			print('error solving captcha')
		login_button.click()
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
		print('meme')
		info = i.split(',')
		password = pass_gen()
		proxy = input_p.readline().rstrip()
		register(info[0], info[1].strip(), password, proxy, key)
		output.write(str (info[0]) + ',' + str(info[1].strip()) + ',' + password + ',' +  str(proxy))

if __name__ == "__main__":
	main()