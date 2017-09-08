# coding=UTF-8

import bs4
import sys
from selenium.webdriver.support.ui import Select
from selenium import webdriver
import logging
import MySQLdb
import os
import time
import unicodedata

login_email = "xxxxxx@xxx.xxx" #ogame email
login_account = "xxxxxx"  #ogame account
login_password = "xxxxxx" #ogame password

server_name = 'Orion'
server_value = 's115-tw.ogame.gameforge.com'

sql_db_ip = "127.0.0.1"
sql_db = "ogame_data"
sql_db_table = "light_data"
sql_db_user = "xxxxxx"
sql_db_password = "xxxxxxxxx"

ogame_url = 'https://tw.ogame.gameforge.com/'

target_coordinate = ["1.2.3", "1.3.5"] #target coordinate


def check_login(title):#check login success or not

	#logging.info("Web Title : " + title)
	if title.find(server_name) > -1: # if login success, title will be "server_name OGame",or title will be "OGame銀河帝國 首頁"		
		return 0 #login success
	else:
		return 1 #login fail

def login_ogame(driver): #login
	
	driver.get(ogame_url) #go to ogame website
	'''new version (53 and up) firefox btn click() not work'''
	
	#driver.get(ogame_url + '/main/loginError/?kid=&error=2') #go to ogame website with open login form
	
	driver.find_element_by_id('loginBtn').click() #click login button
	#driver.find_element_by_link_text(u'登入').click() #click login button by text ## in this version firefox, click element can't work, it's a exist bug
	#driver.find_element_by_id('loginBtn').enter()
	
	account = driver.find_element_by_id('usernameLogin') #find account element and key in
	#account.send_keys(login_account)
	account.send_keys(login_email) #ogame new rule : only use email to login


	password = driver.find_element_by_id('passwordLogin') #find password element and key in
	password.send_keys(login_password)
	
	select = Select(driver.find_element_by_id('serverLogin')) #find server element and select server
	select.select_by_value(server_value)

	driver.find_element_by_id('loginSubmit').click() #click submit button

	return driver

def go_galaxy_page(driver,payload): #Get galaxy page

	url = 'https://' + server_value + '/game/index.php' #basic url
	
	temp_url = ""

	for item in payload: #format url with GET method
		temp_url += item + "=" + payload[item] + "&"

	temp_url = "?" + temp_url[:-1] #remove last "&" and add "?" at thr first

	driver.get(url + temp_url)

	return driver
	
def go_galaxy_page_with_api(driver,payload): #Get galaxy page (new one : use galaxy api address)

	url = 'https://' + server_value + '/game/index.php' #basic url
	
	temp_url = ""

	#for galaxy api address params
	payload['page'] = 'galaxyContent'
	payload['ajax'] = '1'
	
	for item in payload: #format url with GET method
		temp_url += item + "=" + payload[item] + "&"

	temp_url = "?" + temp_url[:-1] #remove last "&" and add "?" at thr first

	driver.get(url + temp_url)

	return driver

def get_planet_min(col): #input cols and get planet mins #0 mean online,15~59 mean minute, 60 mean offline(no min)

	if col.find("div",{"class":"activity minute15 tooltip js_hideTipOnMobile"}): #is online
		#print "online"
		return 0
	elif col.find("div",{"class":"activity showMinutes tooltip js_hideTipOnMobile"}): #is minutes
		#print "mins is",cols[1].find("div",{"class":"activity showMinutes tooltip js_hideTipOnMobile"}).text.strip()
		return int(col.find("div",{"class":"activity showMinutes tooltip js_hideTipOnMobile"}).text.strip())
	else: #offline
		#print "offline"
		return 60	

def check_moon_exit(col): #check moon exist or not

	if len(col['class']) < 4:#no moon exist
		return 0 #no exist
	else:
		return 1 #exist

def get_userID(col): #get userID ###can only get active ID

	#return col.find('span',{"class":"status_abbr_strong"}).string.strip()
	return col.a.span.text.strip()

def get_OGame_Clock(soup): #get OGame Clock

	return soup.find('li',{'class':'OGameClock'}).text.strip()

def send_log_to_mysql(item): #insert log to mysql

	db = MySQLdb.connect(host = sql_db_ip, user = sql_db_user, passwd = sql_db_password, db = sql_db)
	cursor = db.cursor()	
	sql = "INSERT INTO `"+ sql_db_table +"` (`Ogame_Clock`,`userID`,`galaxy`,`system`,`position`,`moon_min`,`planet_min`) VALUES (\'"+item['time']+"\',\'"+item['user_ID']+"\',\'"+item['galaxy']+"\',\'"+item['system']+"\',\'"+item['position']+"\',"+str(item['moon_min'])+","+str(item['planet_min'])+")"
	try:
		cursor.execute(sql)
		db.commit()
		logging.info("Log To Mysql success (" + item['user_ID'] + ")")
	except:
		db.rollback()
		logging.warning("Log To Mysql ERROR")
		#print "error"
	cursor.close()
	db.close()

def trans_coordinate(item): #trans "1.1.1" to dict format (payload = {'page' : 'galaxy','galaxy' : '1','system' : '1','position':'1'})

	item = item.split('.')

	payload = {}
	payload['page'] = 'galaxy'
	payload['galaxy'] = item[0]
	payload['system'] = item[1]
	payload['position'] = item[2]

	return payload	

def parsing_each_target_data(driver, item): #each target will pasing and collect result

	result_dict = {}
	
	#params (coordinate)
	payload = trans_coordinate(item)

	#--------------------
	logging.info("------------------------------------")

	
	#go to galaxy page
	driver = go_galaxy_page(driver,payload)
	#driver = go_galaxy_page_with_api(driver,payload)
	logging.info("Go To Galaxy Page [" + item + "]")

	#wait for 2 second(test)
	time.sleep(2) 
	#get galaxy data
	soup = bs4.BeautifulSoup(driver.page_source, 'html.parser') 
	logging.info("Get Galaxy Data!")
	
	#get galaxy table
	rows = soup.find("table",{"id":"galaxytable"}).tbody.find_all('tr')
	
	#target row data  cols = |No.|planet|planet_name|moon|debris|userID|ally|someItem
	cols = rows[int(payload["position"])-1].find_all('td') 

	#parsing planet data
	result_dict["planet_min"] = get_planet_min(cols[1]) #cols[1] is planet field
	logging.info("["+payload['galaxy']+","+payload['system']+","+payload['position']+"] planet min is "+str(result_dict["planet_min"]))
	
	#parsing monn data
	if check_moon_exit(cols[3]) == 0: #cols[3] is moon field
		logging.info("no moon exist")
		result_dict["moon_min"] = -1
	else:
		result_dict["moon_min"] = get_planet_min(cols[3]) #cols[3] is moon field
		logging.info("["+payload['galaxy']+","+payload['system']+","+payload['position']+"] moon exist, min is "+str(result_dict["moon_min"]))

	#get userID
	result_dict['user_ID'] = get_userID(cols[5]) #cols[5] is userID field
	logging.info("userID : "+result_dict['user_ID'])

	#get other infomation
	result_dict['galaxy'] = payload['galaxy']
	result_dict['system'] = payload['system']
	result_dict['position'] = payload['position']

	#get time
	result_dict['time'] = get_OGame_Clock(soup) 
	logging.info("Ogame Clock: "+result_dict['time'])

	#--------------------
	logging.info("------------------------------------")

	return driver,result_dict
	

if __name__ == '__main__':
	
	start = time.time()
	
	#set logging lecel
	logging.basicConfig(level=logging.INFO)
	
	#open firefox
	logging.info('Open Firefox...')
	driver = webdriver.Firefox() 
	
	#hide window
	#driver.set_window_position(-3000, 0)
	#driver.set_window_size(640,480)
	
	#login
	logging.info('Login Ogame...')
	driver = login_ogame(driver) 
	
	time.sleep(5)
	#put to soup
	soup = bs4.BeautifulSoup(driver.page_source, 'html.parser') 

	#check login success or not
	if check_login(soup.title.text) == 1: 
		logging.warning("Login Fail")
		driver.close()
		sys.exit()
	else:
		logging.info("Login Success")

	#parsing data
	result = []
	
	for item in target_coordinate: #per target run once
		driver,result_dict = parsing_each_target_data(driver, item)
		
		#collcct result
		result.append(result_dict)

	#send data to mysqldb
	for item in result:
		send_log_to_mysql(item)

		
	end = time.time()
	elapsed = end - start
	print "Time taken: ", elapsed, "seconds."	
	
	driver.close()
	os.system('taskkill /F /IM geckodriver.exe')
	os.system('taskkill /F /IM firefox.exe')
	sys.exit()
	
	

	
	
	
	
	





	
	
	
