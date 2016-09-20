#flask/bin/python
from flask import Flask, jsonify
from flask import request
from flask import make_response
from flask import abort
from flask import g
import json
import random
import sqlite3
import logging
import sys
from time import gmtime, strftime

f=open('ipAddress','r')
ipAddress = f.readline()
ipAddress = ipAddress.rstrip()
print(ipAddress) 

#timeStr = strftime("%H%M%S", gmtime()) 
#db = MySQLdb.connect("localhost","root","KopitarTrout27","
#db = sqlite3.connect('pusoyDB')
#cur = db.cursor()

DATABASE = '/var/www/FlaskApp/FlaskApp/pusoyDB'

app = Flask(__name__)

def get_db():
    #db = getattr(g, '_database', None)
    db = None
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def findPlayerNum(gameID,playerID, db, cur):
	queryStr = "SELECT player0,player1,player2 FROM masterGame WHERE gameID = '%s'"%gameID
	cur.execute(queryStr)
	playerDB = cur.fetchall()
	print("PLAYER DB CALL RESULTS")
	print(playerDB)
	for i in range(3):
		if int(playerDB[0][i]) == int(playerID):
			return i
	#error player not found
	return -1 


def initHands(timeStr):
	cards = range(52)
	random.shuffle(cards)
	p1 = cards[0:13]
	p2 = cards[14:27]
	p3 = cards[28:41]
	return [p1,p2,p3]

def rank52alt():
        cards = [0]*52
        k = 0
        for i in range(13):
                for j in range(4):
                        cards[13*j+i] = k
                        k = k+1
        return cards

def findStartingPlayer(playerArray):
	playerIt = 0
	cardIt = 0
	lowCardIt = 0
	while 1:
		while playerIt < 3:
			while cardIt < 13:
				if playerArray[playerIt][cardIt] == lowCardIt:
					return (playerIt,lowCardIt) 
				cardIt = cardIt + 1
			playerIt = playerIt + 1
			cardIt = 0
		lowCardIt = lowCardIt + 1
		playerIt = 0

def updateTableWithStartingHand(playerID, timeStr, playerArray, db, cur):
	#TODO one sql statement for each would be faster
	for i in range(13):
		queryStr = "UPDATE game%s SET Card%d=%d WHERE id=%d"%(timeStr, i, playerArray[i], playerID)
		print(queryStr)
		cur.execute(queryStr)
		db.commit()

def CreateGame(db, cur):
	#db = get_db()
	#cur = db.cursor()	
	p0Const = 0
	p1Const = -1
	p2Const = -2
	timeStr = strftime("%y%j%H%M%S", gmtime())
	players = initHands(timeStr)
	rank52altSorted = rank52alt()
	startingData = findStartingPlayer(players)	
	
	createTableStr = "CREATE TABLE game%s (id INT, cardCount INT, Card0 INT, Card1 INT, Card2 INT, Card3 INT, Card4 INT, Card5 INT, Card6 INT, Card7 INT, Card8 INT, Card9 INT, Card10 INT, Card11 INT, Card12 INT )"%timeStr
	cur.execute(createTableStr)
	p0InsertStr = "INSERT INTO game%s (id,cardCount) VALUES ('%d','13')" %(timeStr,p0Const)
	p1InsertStr = "INSERT INTO game%s (id,cardCount) VALUES ('%d','13')" %(timeStr,p1Const)
	p2InsertStr = "INSERT INTO game%s (id,cardCount) VALUES ('%d','13')" %(timeStr,p2Const)
	cur.execute(p0InsertStr)	
	cur.execute(p1InsertStr)
	cur.execute(p2InsertStr)
	updateTableWithStartingHand(p0Const, timeStr, players[0], db, cur)
	updateTableWithStartingHand(p1Const, timeStr, players[1], db, cur)
	updateTableWithStartingHand(p2Const, timeStr, players[2], db, cur)
	masterGameStr = "INSERT INTO masterGame (gameID, curPlayer, gameFull, gameFinished, cardCount) VALUES ('game%s','%d','0','0','0')"%(timeStr, startingData[1]) 
	print(masterGameStr)
	cur.execute(masterGameStr)
	db.commit()

def CreateGameOutside():
	db  = sqlite3.connect(DATABASE)
        cur = db.cursor()
	CreateGame(db, cur)


#CreateGameOutside()
	
def findPlayerGameID(ID):
	queryString = "SELECT gameID FROM masterGame where (player0=%d || player1=%d || player2=%d) && gameFinished=FALSE"%(ID,ID,ID)
	if(cur.execute(queryString)):
		fetchGet = cur.fetchall()
		return fetchGet[0][0]
	else:
		return "fail"

def getPlayer(gameName,playerID):
	db = get_db()
        cur = db.cursor()
	queryString = "SELECT cardCount FROM %s WHERE id = %s"%(gameName,playerID)
	print(queryString)
	cur.execute(queryString)
	cardCount = cur.fetchall()
	print("THIS IS THE CARD COUNT")
	print(cardCount)
	count = cardCount[0][0]
	returnHand = []
	queryStr = "SELECT "
        if count != 0:
		for i in range(count):
        		 if i != 0 :
                		 queryStr = queryStr + ", "
                 	 queryStr = queryStr + "card%s"%i
        	queryStr = queryStr + " FROM %s WHERE id = '%s'"%(gameName, playerID)
		print(queryStr)
		cur.execute(queryStr)
		queryResult = cur.fetchall()
		print(queryResult)
		for i in range(count):
			returnHand.append(queryResult[0][i])	
	db.close()
	return returnHand

def joinRandomGameHelper(id,playerID,gameName, db, cur):
	    #db = get_db() 
	    #cur = db.cursor()
            updateTableStr = "UPDATE masterGame SET player%d=%d WHERE gameID ='%s'" %(id,playerID,gameName)
  	    print(updateTableStr)
            cur.execute(updateTableStr)
            db.commit()
            updateTableStr = "UPDATE %s SET id=%d WHERE id=%d"%(gameName,playerID,-id)
	    cur.execute(updateTableStr)
            db.commit()
	    #db.close()

app = Flask(__name__)
@app.route('/joinRandomGame/<int:playerID>')
def joinRandomGame(playerID):
	db = get_db() 
        cur = db.cursor()   
#	cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
#	print(cur.fetchall())
	cur.execute("SELECT player0,player1,player2,gameID FROM masterGame ORDER BY gameID DESC LIMIT 1")
	playerStatus = cur.fetchall()
	print("PLAYER STATUS")
	print(playerStatus)
	gameName = playerStatus[0][3]
	playerNum = -1
	f = open('curPlayerNetworkCall', 'w')
	print("0")
	if playerStatus[0][0] is None:
        	joinRandomGameHelper(0,playerID,gameName, db, cur)
		print("1")
		playerNum = 0
	elif playerStatus[0][1] is None:
		joinRandomGameHelper(1,playerID,gameName, db, cur)
		print("2")
		playerNum = 1
	elif playerStatus[0][2] is None:
		joinRandomGameHelper(2,playerID,gameName, db, cur)
		print("3")
		playerNum = 2
		db = sqlite3.connect('pusoyDB')
       		cur = db.cursor()
		queryStr = "UPDATE masterGame SET gameFull='1' where gameID='%s'"%gameName 
		print(queryStr)
		cur.execute(queryStr)
		#db.close()
		CreateGame(db, cur)
	hand = getPlayer(gameName,playerID)
 	f.write(gameName)
	f.write("\n")
	handStr = str(hand)
	f.write(handStr)
	f.write("\n")
	playerNumStr = str(playerID)
	f.write(playerNumStr)		
	return jsonify(game=gameName,hand=hand,playerNum=playerNum,cardCount=len(hand),playerID=playerID)

@app.route('/checkGameStatus/<string:gameID>')
def gameStatus(gameID):
	db = get_db()
	cur = db.cursor()
	searchQuery = "SELECT curPlayer,gameFull,cardCount FROM masterGame WHERE gameID = '%s'"%gameID
	cur.execute(searchQuery)
	curPlayerStatus = cur.fetchall()
	cardCount = curPlayerStatus[0][2]
	print(cardCount)
	returnHand = []
	if cardCount != 0: 
		queryStr = "SELECT "
		for i in range(cardCount):
			if i != 0 :
				queryStr = queryStr + ", "
			queryStr = queryStr + "card%s"%i
		queryStr = queryStr + " FROM masterGame WHERE gameID = '%s'"%gameID
		print(queryStr)
		cur.execute(queryStr)
		hand = cur.fetchall()	
		for i in range(cardCount):
			returnHand.append(hand[0][i])
	
	return jsonify(curPlayer=curPlayerStatus[0][0],lastPlayedHand=returnHand,gameFull=curPlayerStatus[0][1])

@app.route('/login', methods=['POST'])
def login():
    if not request.json or not 'email' in request.json or not 'password' in request.json:
       # abort(400)
	return (jsonify(id=-3)) 
    email = request.json['email']
    password = request.json['password']
    password.encode('ascii','ignore')
    str(email)
    queryStr = "SELECT password FROM players WHERE email = '%s'"%email
    isValidEmail = cur.execute(queryStr)
    if isValidEmail == 0:
    	return (jsonify(id=-2))
    queryResult = cur.fetchall()
    
    passwordSQL = queryResult[0][0]
    if password != passwordSQL:
    	return (jsonify(id=-1))
    else:
	queryStr = "SELECT id FROM players WHERE email = '%s'"%email
        cur.execute(queryStr)
        idArray = cur.fetchall()
        id = idArray[0][0]
        db.commit()
        print(id)
        return (jsonify(id=id))

@app.route('/newPlayer', methods=['POST'])
def newPlayer():
	if not request.json or not 'email' in request.json or not 'password' in request.json:
       		return "Bad Params"
	db = get_db()
	cur = db.cursor() 
	email = request.json['email']
	password = request.json['password']	
	queryStr = "SELECT * FROM players WHERE email = '%s'"%email
	emailExists = cur.execute(queryStr)
	if emailExists != 0:
		return (jsonify(id=-1))
	queryStr = "INSERT INTO players (email, password) VALUES ('%s','%s')"%(email,password)
	cur.execute(queryStr)
	queryStr = "SELECT id FROM players WHERE email = '%s'"%email
	cur.execute(queryStr)
	idArray = cur.fetchall()
	id = idArray[0][0]
	db.commit()
	print(id)
	return (jsonify(id=id))

@app.route('/playHand', methods=['POST'])
def create_task():
	print("THIS IS THE PLAY HAND REQUEST")
	print(request)
	print(request.json)
	if not 'cards' in request.json or not 'playerID' in request.json or not 'gameID' in request.json:
		return "Bad Params"
	else:
		print("IN RIGHT SECTION")
		db = get_db()
        	cur = db.cursor()
		cards = request.json['cards']
		playedCards = json.loads(cards)
		pass
		if len(playedCards) == 0:
			return "no cards"
		gameID = request.json['gameID']
		playerID = request.json['playerID']
		hand = getPlayer(gameID,playerID)
		rightCards = True
		cardFound = False
		gameStatusQuery = "cardCount=%d, "%len(playedCards)
		count = 0
		for playedCard in playedCards:
			comma = ""
			if count != 0:
				comma = ", "
			tempStr = comma + "card%d=%d"%(count, playedCard)
			gameStatusQuery = gameStatusQuery + tempStr
			for handCard in hand:
				if playedCard == handCard:
					cardFound = True
			if not cardFound:
				rightCards = False
			cardFound = False
			count = count + 1
		if not rightCards:
			return "Cards not found in hand"
		for playedCard in playedCards:
			hand.remove(playedCard)
		if len(hand) != 0:
			queryStr = "UPDATE %s SET cardCount=%d "%(gameID, len(hand))
			for i in range(13):
				if i < len(hand): 
                         		queryStr = queryStr + ",card%s=%d"%(i,hand[i])
                		else:
					queryStr = queryStr + ",card%s=NULL"%i
			queryStr = queryStr + " WHERE id = '%s'"%playerID
                	print(queryStr)
                	cur.execute(queryStr)
			print("ALEX YOU IDIOT")
		#updateTableStr = "UPDATE %s SET hand = '%s',cardCount=%d where id = %s"%(gameID,str(hand),len(hand),playerID)
		else:
			return "YOU HAVE WON"
        	db.commit()
		updatedCards = getPlayer(gameID,playerID)
	  	playerNum = findPlayerNum(gameID,playerID,db, cur)	
		playerNum = (playerNum+1)%3
		queryStr = "UPDATE masterGame SET %s,curPlayer='%d' WHERE gameID = '%s'"%(gameStatusQuery,playerNum,gameID)
		print("ALEX LOOK UPDATE QUERY")
		print(queryStr)
		cur.execute(queryStr)
		db.commit()	
		return jsonify(cardCount=len(updatedCards),cards=updatedCards)

@app.route('/passHand', methods=['POST'])
def playPassHand():
	if not 'playerID' in request.json or not 'gameID' in request.json:
        	return "Bad Params"
        else:
		gameID = request.json['gameID']
        	playerID = request.json['playerID']
		playerNum = findPlayerNum(gameID,playerID)
                playerNum = (playerNum+1)%3
		queryStr = "UPDATE masterGame SET lastPlayedHand=100,100,curPlayer='%s' WHERE gameID = '%s'"%(playerNum,gameID)
        	cur.execute(queryStr)
		db.commit() 
		return "Hand Passed"		
	

if __name__ == '__main__':
    app.run(debug='true',host=ipAddress)


@app.route('/')
def index():
    return "Hello, World!"
