from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
from pprint import pprint
import threading
import argparse
import re
import cgi
import json
import os


class Validate(object):
	@staticmethod
	def validateUserZoneAP(zoneID,apID=None,userID=None):
		dbFileName = '/usr/src/OpenYuma/dataBase.json'
		foundZoneandAP = False
		foundUser = False
		with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)
				for zone in dbJson['zones']:
					for ap in zone['accessPoints']:
						if (ap['accessPointId'] == apID and zone['zoneId'] == zoneID)	or (apID ==None and zone['zoneId'] == zoneID):
							foundZoneandAP = True
						for usr in ap['users']:
							if usr['address'] == userID or userID==None:
								foundUser = True
		return (foundZoneandAP and foundUser)

class HTTPRequestHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		if None != re.search('exampleAPI/location/v1/movetozoneId=zone\d+\&accessPointId=\d+user=*', self.path):
			#change dataBase file
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			user = {}
			usrAdd = self.path.split('=')[-1].replace('%3A',':')
			zoneNum = (self.path.split('=')[-3]).split('&')[-2]
			apID =  (self.path.split('=')[-2])[:-4]
			sourceZoneNum = 0
			
			if Validate.validateUserZoneAP(zoneNum,apID,usrAdd) == False:
				self.send_response(204)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				return
				
			with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)
				for zone in dbJson['zones']:
					for ap in zone['accessPoints']:
						counter = -1
						for usr in ap['users']:
							counter+=1
							if usr['address'] == usrAdd:
								sourceZoneNum = zone['zoneId']
								user = usr
								del ap['users'][counter]

				for zone in dbJson['zones']:
					if zone['zoneId'] == zoneNum: 
						for ap in zone['accessPoints']:
							if ap['accessPointId'] == apID:
								user['zoneId'] = zoneNum
								user['accessPointId'] = apID
								(ap['users']).append(user)

			with open(dbFileName, 'w') as db:
				json.dump(dbJson, db)
			
			#change alarmTable file				
			alarmFileName = '/usr/src/OpenYuma/alarmTable.json'
			with open(alarmFileName,'r') as json_data: 
				alarmJson = json.load(json_data)
				alarmJson[zoneNum]['isChanged'] = "1"
				alarmJson[zoneNum]['lastEvent'] = str(usrAdd) + " was added"
				alarmJson[sourceZoneNum]['isChanged'] = "1"
				alarmJson[sourceZoneNum]['lastEvent'] = str(usrAdd) + " was removed"
				if usrAdd in alarmJson[sourceZoneNum]['users']:
					del alarmJson[sourceZoneNum]['users'][usrAdd]
					alarmJson[zoneNum]['users'][usrAdd]="1"
						
			with open(alarmFileName, 'w') as json_data:
				json.dump(alarmJson, json_data)
							
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			
		elif  None != re.search('exampleAPI/location/v1/removeUser=*', self.path):
			#change dataBase file
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			user = {}
			usrAdd = self.path.split('=')[-1].replace('%3A',':')
			sourceZoneNum = 0
				
			with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)
				for zone in dbJson['zones']:
					for ap in zone['accessPoints']:
						counter = -1
						for usr in ap['users']:
							counter+=1
							if usr['address'] == usrAdd:
								sourceZoneNum = zone['zoneId']
								os.system('echo anna > anna.txt')
								user = usr
								del ap['users'][counter]

			if user == {}:
				self.send_response(204)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				
			with open(dbFileName, 'w') as db:
				json.dump(dbJson, db)
			
			os.system('echo anna > anna1.txt')
			
			#change alarmTable file				
			alarmFileName = '/usr/src/OpenYuma/alarmTable.json'
			with open(alarmFileName,'r') as json_data: 
				alarmJson = json.load(json_data)
				alarmJson[sourceZoneNum]['isChanged'] = "1"
				alarmJson[sourceZoneNum]['lastEvent'] = str(usrAdd) + " was removed"
				if usrAdd in alarmJson[sourceZoneNum]['users']:
					del alarmJson[sourceZoneNum]['users'][usrAdd]
						
			with open(alarmFileName, 'w') as json_data:
				json.dump(alarmJson, json_data)
							
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
						
		
		elif None != re.search('exampleAPI/location/v1/addUser', self.path):
			body = self.rfile.read(int(self.headers['Content-Length']))
			data = json.loads(body)
			os.system('echo %s > anna.txt' % data)
			
			#change dataBase file
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			user = {}
			if Validate.validateUserZoneAP(data['zoneId'],data['accessPointId']) == False:
				self.send_response(204)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				return
				
			with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)
				for zone in dbJson['zones']:
					if zone['zoneId'] == data['zoneId']: 
						for ap in zone['accessPoints']:
							if ap['accessPointId'] == data['accessPointId']:
								os.system('echo anna > anna1.txt')
								(ap['users']).append(data)

			with open(dbFileName, 'w') as db:
				json.dump(dbJson, db)
			
			#change alarmTable file				
			alarmFileName = '/usr/src/OpenYuma/alarmTable.json'
			with open(alarmFileName,'r') as json_data: 
				alarmJson = json.load(json_data)
				alarmJson[data['zoneId']]['isChanged'] = "1"
				alarmJson[data['zoneId']]['lastEvent'] = str(data['address']) + " was added"
				alarmJson[data['zoneId']]['users'][data['address']]="1"
						
			with open(alarmFileName, 'w') as json_data:
				json.dump(alarmJson, json_data)
							
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()

		else:
			self.send_response(403)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
	
	def do_GET(self):
		if None != re.search('exampleAPI/location/v1/users$', self.path):
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			dict1 = {}	
			users = []
			with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)
				for zone in dbJson['zones']:
					for ap in zone['accessPoints']:
						for usr in ap['users']:
							users.append(usr) 			
				dict1['user'] = users
				dict2 = {}
				dict2['userList'] = dict1  
				if users:
					self.send_response(200)
					self.send_header('Content-Type', 'application/json')
					self.end_headers()
					dict2['resourceURL'] = users[0]['resourceURL'].rsplit('/',1)[0]
					value = json.dumps(dict2)
					self.wfile.write(value.encode())
				else:
					self.send_response(204)
					self.send_header('Content-Type', 'application/json')
					self.end_headers()
	
		elif None != re.search('exampleAPI/location/v1/users\?zoneId=zone\d+$', self.path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			dict1 = {}	
			users = []
			zoneNum = self.path.split('=')[-1]
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)        
				for zone in dbJson['zones']:
					if zone['zoneId'] == zoneNum:
						for ap in zone['accessPoints']:
							for usr in ap['users']:
								users.append(usr)
		
				dict1['user'] = users
				dict2 = {}
				dict2['userList'] = dict1
				if users:
					dict2['resourceURL'] = users[0]['resourceURL'].rsplit('/',1)[0]
				value = json.dumps(dict2)
				self.wfile.write(value.encode())
					
		elif  None != re.search('exampleAPI/location/v1/users\?zoneId=zone\d+\&accessPointId=\d+',self.path):					
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers() 
			dict1 = {}	
			users = []
			apID = self.path.split('=')[-1]
			zoneNum = self.path.split('=')[-2].split('&')[-2]
			os.system("echo %s > anna.txt" % zoneNum)
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)
				for zone in dbJson['zones']:
					if zone['zoneId'] == zoneNum:
						for ap in zone['accessPoints']:
							if ap['accessPointId'] == apID:
								for usr in ap['users']:
									users.append(usr)
				dict1['user'] = users
				dict2 = {}
				dict2['userList'] = dict1
				if users:
					dict2['resourceURL'] = users[0]['resourceURL'].rsplit('/',1)[0]
				value = json.dumps(dict2)
				self.wfile.write(value.encode())
		
		elif None != re.search('exampleAPI/location/v1/users/*', self.path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			usrAdd = self.path.split('/')[-1]
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)        
				for zone in dbJson['zones']:
					for ap in zone['accessPoints']:
						for usr in ap['users']:
							if usr['address'] == usrAdd.replace('%3A',':'):
								dict2 = {}
								dict2['userInfo'] = usr
								value = json.dumps(dict2)
								self.wfile.write(value.encode())
								
		elif None != re.search('exampleAPI/location/v1/zones/zone\d+/accessPoints$',self.path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			dict1 = {}
			aps = []
			zoneNum = self.path.split('/')[-2]
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)
				for zone in dbJson['zones']:
					if zone['zoneId'] == zoneNum:
						for ap in zone['accessPoints']:
							del ap['users']
							aps.append(ap)
				os.system("echo %s > anna345.txt" % aps)
				dict1['accessPoint'] = aps
				dict2 = {}
				dict2['accessPointList'] = dict1
				dict2['zoneId'] = zoneNum
				if aps:
					dict2['resourceURL'] = aps[0]['resourceURL'].rsplit('/',1)[0]
				value = json.dumps(dict2)
				self.wfile.write(value.encode())
							
		elif None != re.search('exampleAPI/location/v1/zones/zone\d+/accessPoints/*',self.path):
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			apID = self.path.split('/')[-1]
			zoneNum = self.path.split('/')[-3]
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			with open(dbFileName,'r') as json_data: 
				dbJson = json.load(json_data)
				for zone in dbJson['zones']:
					if zone['zoneId'] == zoneNum:
						for ap in zone['accessPoints']:
							if ap['accessPointId'] == apID:
								dict2 = {}
								del ap['users']
								dict2['accessPointInfo'] = ap
								value = json.dumps(dict2)
								self.wfile.write(value.encode())
							
		#implement events
		elif None != re.search('exampleAPI/location/v1/userEvent/userAddress=*',self.path):
			userAdd = self.path.split('=')[-1].replace('%3A',':')
			alarmFileName = '/usr/src/OpenYuma/alarmTable.json'
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			with open(alarmFileName,'r') as json_data: 
				alarmJson = json.load(json_data)
				for zone in alarmJson:
					if userAdd in alarmJson[zone]['users']:
						if alarmJson[zone]['users'][userAdd] == "0":
							self.send_response(204)
							self.send_header('Content-Type', 'application/json')
							self.end_headers()	
							return
						else:
							alarmJson[zone]['users'][userAdd] = "0"

			with open(alarmFileName, 'w') as json_data:
				json.dump(alarmJson, json_data)
					
			with open(dbFileName,'r') as json_data_2: 
				dbJson = json.load(json_data_2)
				for zone in dbJson['zones']:
					for ap in zone['accessPoints']:
						for usr in ap['users']:
							if usr['address'] == userAdd:
								self.send_response(200)
								self.send_header('Content-Type', 'application/json')
								self.end_headers()
								dict2 = {}
								#dict2['userInfo'] = usr
								event = str(usr['address']) + " moved to " + str(usr['zoneId'])
								dict2['event'] = event
								value = json.dumps(dict2)
								#value = json.dumps(dict2)
								self.wfile.write(value.encode())
								return 

				self.send_response(204)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()	
				
		elif None != re.search('exampleAPI/location/v1/userEvent/zone=zone\d+',self.path):
			zoneNum = self.path.split('=')[-1]
			
			if Validate.validateUserZoneAP(zoneNum) == False:
				self.send_response(204)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				return
			
			alarmFileName = '/usr/src/OpenYuma/alarmTable.json'
			dbFileName = '/usr/src/OpenYuma/dataBase.json'
			with open(alarmFileName,'r') as json_data: 
				alarmJson = json.load(json_data)
				os.system("echo %s > anna.txt" % alarmJson[zoneNum]['isChanged'] )
				if alarmJson[zoneNum]['isChanged'] == "0":
					self.send_response(204)
					self.send_header('Content-Type', 'application/json')
					self.end_headers()	
					return
					
			alarmJson[zoneNum]['isChanged'] = "0"
			event = alarmJson[zoneNum]['lastEvent'] 
			with open(alarmFileName, 'w') as json_data:
				json.dump(alarmJson, json_data)
		
			with open(dbFileName,'r') as json_data_2: 
				dbJson = json.load(json_data_2)
				for zone in dbJson['zones']:
					if zone['zoneId'] == zoneNum:
						self.send_response(200)
						self.send_header('Content-Type', 'application/json')
						self.end_headers()
						dict2 = {}
						dict2['event'] = event
						#dict2['zoneInfo'] = zone
						value = json.dumps(dict2)
						self.wfile.write(value.encode())
						return 
						
				self.send_response(204)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()	
				
				
		else:
			self.send_response(403)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
		return
		

 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
  allow_reuse_address = True
 
  def shutdown(self):
    self.socket.close()
    HTTPServer.__class_.shutdown(self)
 

class SimpleHttpServer():
  def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip,port),HTTPRequestHandler)

  def start(self):
    self.server_thread = threading.Thread(target=self.server.serve_forever)
    self.server_thread.daemon = True
    self.server_thread.start()
 
  def waitForThread(self):
    self.server_thread.join()
 
  def addRecord(self, recordID, jsonEncodedRecord):
    LocalData.records[recordID] = jsonEncodedRecord

  def stop(self):
    self.server.shutdown()
    self.waitForThread()

if __name__=='__main__':

  server_address = ('', 700)
  server_class=HTTPServer

  httpd = server_class(server_address, HTTPRequestHandler)
  httpd.serve_forever()

