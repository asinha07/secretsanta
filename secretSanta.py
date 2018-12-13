import MySQLdb
import smtplib
import time
import imaplib
import email
import time
from smspy import Way2sms


ORG_EMAIL   = "@gmail.com"
FROM_EMAIL  = "XYZ" + ORG_EMAIL
FROM_PWD    = "PASSWORD"
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993

import requests
import json

URL = 'http://www.way2sms.com/api/v1/sendCampaign'

# post request
def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
  req_params = {
  'apikey':apiKey,
  'secret':secretKey,
  'usetype':useType,
  'phone': phoneNo,
  'message':textMessage,
  'senderid':senderId
  }
  return requests.post(reqUrl, req_params)

def sendemail(from_addr, to_addr_list,
              subject, message,
              login, password):
    smtpserver='smtp.gmail.com:587'
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = str(header) + str(message)
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()

def createConnection():
	db = MySQLdb.connect("localhost","user","password","secretsanta" )
	return db

def closeConnection(db):
	db.close()

def getChild(cursor,currId):
	sql = "Select id,name,email,phone from secretsantausers where child_allocated = 0 and id != "+str(currId)+" order by rand() limit 1;";
	cursor.execute(sql)
	results = cursor.fetchall()
	return results[0];

def allocateChild():
	db = createConnection()
	cursor = db.cursor()
	sql = "select * from secretsantausers;"
	cursor.execute(sql)
	results = cursor.fetchall()
	for row in results:
		userId = row[0]
		name = row[1]
		email = row[2]
		phone = row[3]
		child = getChild(cursor,userId);
		message = "Hello "+name+"! Welcome to Secret Santa."+'\n'+"Your child for the game would be: "+child[1]+"."+'\n'+ "Gifts would be exchanged on the 21st of this month."+'\n'+"Make sure that you bring the gift along with you. "+'\n'+"Merry Christmas!"
		print message
		sendemail(FROM_EMAIL,[email],"Secret Santa is Here!",message,FROM_EMAIL,FROM_PWD)
		response = sendPostRequest(URL, 'app-key', 'app-secret', 'stage', phone, '', message )
		updateChild(userId,child[0],cursor,db)
		upadteAlreadyAllocated(child[0],cursor,db)


def updateChild(userId,childId,cursor,db):
	sql = 'Update secretsantausers set child_id = '+str(childId)+' where id = '+str(userId);
	cursor.execute(sql)
	db.commit()

def upadteAlreadyAllocated(userId,cursor,db):
	sql = 'Update secretsantausers set child_allocated = 1 where id = '+str(userId);
	cursor.execute(sql)
	db.commit()


if __name__ == '__main__':
	allocateChild()
