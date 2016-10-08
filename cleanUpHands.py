import sqlite3
from time import gmtime, strftime 

db = sqlite3.connect('/var/www/FlaskApp/FlaskApp/pusoyDB')
timeOutHours = 6

timeInt = int(strftime("%y%j%H%M%S", gmtime()))
timeStr = strftime("%y%j%H%M%S", gmtime())

cur = db.cursor()

#queryStr = "SELECT gameID FROM masterGame where gameFinished = 1" 
queryStr = "SELECT gameID FROM masterGame where gameFull = 1"
#queryStr = "SELECT gameID FROM masterGame"

cur.execute(queryStr) 

gameIDArrayFetch = cur.fetchall()

def timeComp(gameStr):
	gameYear = int(gameStr[0:2])
	gameDay = int(gameStr[2:5])
	gameTime = int(gameStr[5:])
	
	timeYear = int(timeStr[0:2])
	timeDay = int(timeStr[2:5])
	timeTime = int(timeStr[5:])
	#print("game time %d"%gameTime)	
	#print("time time %d"%timeTime)	
	cutOffTime = gameTime - timeOutHours*3600 
	#print("cutoff time %d"%cutOffTime)	
	if gameYear != timeYear:
		return True
	if gameDay != timeDay:
		return True
	return cutOffTime > gameTime	
#print(gameIDArrayFetch)

toBeRemoved  = False  
for i in range(len(gameIDArrayFetch)):
	gameStr = gameIDArrayFetch[i][0] 
	gameStrShort = gameStr[4:]
	gameInt = int(gameStrShort)
	timeComp(gameStrShort)	
	toBeRemoved = timeComp(gameStrShort)	
	if toBeRemoved:
		queryStr = "DROP TABLE %s"%gameStr
		cur.execute(queryStr)
		#print(queryStr)
		queryStr = "DELETE FROM TABLE masterGame where gameID = %s"%gameStr
		cur.execute(queryStr)
		#print(queryStr)
	else:
		print("TABLE OUTSIDE OF CUTOFF")
