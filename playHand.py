import os
import sys 
import sqlite3
print(str(sys.argv))

#1st Arg player num, 2nd Arg num cards to play
playerNum = sys.argv[1] 
numCardsToPlay = sys.argv[2]

DATABASE = '/var/www/FlaskApp/FlaskApp/pusoyDB'

db = sqlite3.connect(DATABASE)
cur = db.cursor()
queryStr = "SELECT player%s, gameID FROM allGames ORDER BY gameID DESC LIMIT 1"%playerNum
cur.execute(queryStr)
queryResult = cur.fetchall()
playerID = queryResult[0][0] 
gameID = queryResult[0][1]

def getPlayer():
	queryString = "SELECT cardCount FROM %s WHERE id = %s AND gameFull "%(gameID,playerID)
        print(queryString)
	cur.execute(queryString)
        cardCount = cur.fetchall()
        count = cardCount[0][0]
        returnHand = []
        queryStr = "SELECT "
        if count != 0:
                for i in range(count):
                         if i != 0 :
                                 queryStr = queryStr + ", "
                         queryStr = queryStr + "card%s"%i
                queryStr = queryStr + " FROM %s WHERE id = '%s'"%(gameID, playerID)
                print(queryStr)
                cur.execute(queryStr)
                queryResult = cur.fetchall()
                print(queryResult)
                for i in range(count):
                        returnHand.append(queryResult[0][i])
	return returnHand

fullHand = getPlayer()

#TODO add support for second card

playHand = [fullHand[0]]
playHandStr = str(playHand)

networkCall = "curl -i -H \"Content-Type: application/json\" -X POST -d '{\"gameID\":\"%s\",\"playerID\":\"%d\",\"cards\":\"%s\"}' http://192.168.0.104:5000/playHand"%(gameID, playerID, playHandStr)
print(networkCall)
os.system(networkCall)
