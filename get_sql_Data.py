# coding=UTF-8

import MySQLdb
import time
import json
import os

sql_db_ip = "127.0.0.1"
sql_db = "ogame_data"
sql_db_table = "light_data"
sql_db_user = "xxxxx"
sql_db_password = "xxxxxxx"

day_control = '1' #how many days before (ex . yesterday is 1 )
project_name = 'xxxxxx.github.io' #folder name to put data and upload to github

def get_yesterday_userID(): ##get all userID(unique) data yesterday
	db = MySQLdb.connect(host = sql_db_ip, user = sql_db_user, passwd = sql_db_password, db = sql_db)
	cursor = db.cursor()	
	
	#get all userID(unique) data yesterday
	sql = 'select DISTINCT `userID` from `'+ sql_db_table +'` where to_days(now()) - to_days(date_format(str_to_date(`Ogame_Clock`, "%d.%m.%Y %H:%i:%s"),"%Y-%m-%d")) = ' + day_control
	
	cursor.execute(sql)
	db.commit()
	
	data = cursor.fetchall()	
	userID_list = []
	
	for item in data:#get userID to list
		userID_list.append(item[0])
		
	db.close()
	
	return userID_list #return ['name','name2']

def get_userID_coordinate(userID): #get specific useriD's all coordinate
		
	db = MySQLdb.connect(host = sql_db_ip, user = sql_db_user, passwd = sql_db_password, db = sql_db)
	cursor = db.cursor()	
	
	userID_list = get_yesterday_userID()
	
	sql = 'select DISTINCT `galaxy`,`system`,`position` from `'+ sql_db_table +'` WHERE to_days(now()) - to_days(date_format(str_to_date(`Ogame_Clock`, "%d.%m.%Y %H:%i:%s"),"%Y-%m-%d")) = 1 and `userID` = "' + userID + '"'
	
	cursor.execute(sql)
	db.commit()
	
	data = cursor.fetchall()
	
	db.close()
	
	#for item in data
	
	return data #return tuple (('1','2','3'),('1','2','4'))

def get_userID_coordinate_time_min_data(userID_coordinate,type): #get specific userID's specific coordinate time and min data
	db = MySQLdb.connect(host = sql_db_ip, user = sql_db_user, passwd = sql_db_password, db = sql_db)
	cursor = db.cursor()
	
	if type == 0: #planet
		temp = "planet_min"
	else : #moon
		temp = "moon_min"
	
	sql = 'select `Ogame_Clock`,`' + temp + '` from `'+ sql_db_table +'` WHERE to_days(now()) - to_days(date_format(str_to_date(`Ogame_Clock`, "%d.%m.%Y %H:%i:%s"),"%Y-%m-%d")) = ' + day_control + ' and `galaxy` = "' + userID_coordinate[0] + '" and `system` = "' + userID_coordinate[1] + '" and `position` = "' + userID_coordinate[2] + '"'
	
	cursor.execute(sql)
	db.commit()
	
	data = cursor.fetchall() #((time,min),(time,min))
	
	db.close()
	
	planet_json = []
	
	#put ((time,min),(time,min)) => [{x:time,y:min},{x:time,y:min}] 
	for item in data: 
		temp = {}
		temp['x'] = item[0] # x : time
		temp['y'] = int(item[1]) # y : planet_min
		planet_json.append(temp)
	
	return planet_json #return [{x:time,y:min},{x:time,y:min}]

def get_yestreday_date(): #get yesterday date

	db = MySQLdb.connect(host = sql_db_ip, user = sql_db_user, passwd = sql_db_password, db = sql_db)
	cursor = db.cursor()
	
	sql = 'SELECT date_sub(curdate(),interval ' + day_control + ' day)'
	
	cursor.execute(sql)
	db.commit()
	
	data = cursor.fetchall()
	
	return str(data[0][0])
	
def check_moon_exist(userID_coordinate): #check moon exist at that coordinate or not
	
	db = MySQLdb.connect(host = sql_db_ip, user = sql_db_user, passwd = sql_db_password, db = sql_db)
	cursor = db.cursor()
	sql = 'select `moon_min` from light_data where to_days(now()) - to_days(date_format(str_to_date(`Ogame_Clock`, "%d.%m.%Y %H:%i:%s"),"%Y-%m-%d")) = ' + day_control + ' and `galaxy` = "' + userID_coordinate[0] + '" and `system` = "' + userID_coordinate[1] + '" and `position` = "' + userID_coordinate[2] + '" limit 1'
	
	cursor.execute(sql)
	db.commit()
	
	data = cursor.fetchall() 
	
	db.close()
	
	if int(data[0][0]) == -1: #moon not exist
		return 1
	else:
		return 0
		
def write_json_file(userID,userID_coordinate,type,planet_json): #write json object to file
	yesterday_date = get_yestreday_date()
	
	planet_json = add_info_to_json(userID,userID_coordinate,type,planet_json,yesterday_date) #format [{},{}] => {info:info,data:[{},{}]}
	
	if not os.path.exists('./' + project_name + '/data/' + yesterday_date):
		os.makedirs('./' + project_name + '/data/' + yesterday_date) # create directory with date name
	
	f = open('./' + project_name + '/data/' + yesterday_date + '/' + userID + "_" + yesterday_date + "_" + userID_coordinate[0] + "-" + userID_coordinate[1] + "-" +userID_coordinate[2] + "_" + type + ".json",'w')
	
	f.write(json.dumps(planet_json))
	
	f.close()	
	
def add_info_to_json(userID,userID_coordinate,type,planet_json,yesterday_date): #format [{},{}] => {info:[{},{}]}
	
	str = yesterday_date + " " + userID + " " + type + " " + userID_coordinate[0] + "-" + userID_coordinate[1] + "-" +userID_coordinate[2] #format info
	temp = {}
	temp['info'] = str
	temp['data'] = planet_json
	return temp
	
def push_to_github():#use push command to push data to github

	''' befroe do this , need to add new folder, do "git init", pull the git, do "git remote add name url" .'''
	
	date = get_yestreday_date()
	
	#enter project folder
	os.chdir(project_name) 

	#add all changed file 
	os.system('git add --all') 
	
	#commit with date
	os.system('git commit -m "' + date + '"')
	
	#push to github (name:origin, branch_name:master)
	os.system('git push -u origin master')
	
if __name__ == '__main__': #get all data last day,and list how many user, and for each user upload planet and moon min data
	
	#get all userID
	userID_list = get_yesterday_userID() 
	for userID in userID_list: 
		#get specific userID's coordinate 
		userID_coordinate_list = get_userID_coordinate(userID)
		for userID_coordinate in userID_coordinate_list:
			#get specific userID's specific coordinate's planet time and min data 
			planet_json = get_userID_coordinate_time_min_data(userID_coordinate,0) #type = 0 means planet 	
			
			#write json file with specific name	
			write_json_file(userID,userID_coordinate,"planet",planet_json)
	
			#defense moon exist or not to decide add a moon json object
			if check_moon_exist(userID_coordinate) == 0: #moon exist
				#get specific userID's specific coordinate's moon time and min data
				moon_json = get_userID_coordinate_time_min_data(userID_coordinate,1) #type = 1 means moon
		
				#write json file with specific name	
				write_json_file(userID,userID_coordinate,"moon",moon_json)
				
	
	#upload file to git with git command
	push_to_github()
	
	
	
	
	
