import os
import sys
import sqlite3

f=open('ipAddress','r')
ipAddress = f.readline()
ipAddress = ipAddress.rstrip()

DATABASE = '/var/www/FlaskApp/FlaskApp/pusoyDB'
db = sqlite3.connect(DATABASE)
cur = db.cursor()

handNum = sys.argv[1] 

gameIDQueryString = "SELECT gameID FROM masterGame where gameFull = 1 ORDER BY gameID DESC LIMIT 1"
cur.execute(gameIDQueryString)
gameIDFetch = cur.fetchall()
gameID = gameIDFetch[0][0]

networkCall = "curl -i -H \"Content-Type: application/json\" http://%s:5000/getGameStatus/%s/%s"%(ipAddress,gameID,handNum)
print(networkCall)
os.system(networkCall)
