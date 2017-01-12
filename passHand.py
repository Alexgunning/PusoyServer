import os
import sys
import sqlite3
print(str(sys.argv))

#1st Arg player num, 2nd Arg num cards to play
playerNum = sys.argv[1]

f=open('ipAddress','r')
ipAddress = f.readline()
ipAddress = ipAddress.rstrip()

DATABASE = '/var/www/FlaskApp/FlaskApp/pusoyDB'

db = sqlite3.connect(DATABASE)
cur = db.cursor()
queryStr = "SELECT player%s, gameID FROM masterGame where gameFull = 1 ORDER BY gameID DESC LIMIT 1"%playerNum
cur.execute(queryStr)
queryResult = cur.fetchall()
playerID = queryResult[0][0]
gameID = queryResult[0][1]


networkCall = "curl -i -H \"Content-Type: application/json\" -X POST -d '{\"gameID\":\"%s\",\"playerID\":\"%d\"}' http://%s:5000/passHand"%(gameID, playerID, ipAddress)
print(networkCall)
os.system(networkCall)
