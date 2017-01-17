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
#print(ipAddress) 

DATABASE = '/var/www/FlaskApp/FlaskApp/pusoyDB'

app = Flask(__name__)

OUTGOING_FRIEND__REGUEST = 0
INCOMING_FRIEND_REGUEST = 1
FRIENDS = 2


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
	#print("PLAYER DB CALL RESULTS")
	#print(playerDB)
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

def findStartingPlayer(playerArray, rank52Alt):
	playerIt = 0
	cardIt = 0
	lowCardIt = 0
	lowCardRank52 = 0
	#print(playerArray)
	return (0,playerArray[0][0])	
	while 1:
		while playerIt < 3:
			while cardIt < 13:
				#print(playerIt)
				#print(cardIt)
				#print(lowCardRank52)
				if playerArray[playerIt][cardIt] == lowCardRank52:
					#print("RETURNING")
					#print(playerIt)
					#print(lowCardIt)
					return (playerIt,lowCardIt) 
				cardIt = cardIt + 1
			playerIt = playerIt + 1
			cardIt = 0
		#print("LOW CARD IT")
		lowCardRank52 = rank52Alt[lowCardIt + 1]
		#print(lowCardRank52)
		playerIt = 0

def updateTableWithStartingHand(playerID, timeStr, playerArray, db, cur):
	for i in range(13):
		queryStr = "UPDATE game%s SET Card%d=%d WHERE id=%d"%(timeStr, i, playerArray[i], playerID)
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
	startingData = findStartingPlayer(players, rank52altSorted)	
	
	createTableStr = "CREATE TABLE game%s (id INT, cardCount INT, Card0 INT, Card1 INT, Card2 INT, Card3 INT, Card4 INT, Card5 INT, Card6 INT, Card7 INT, Card8 INT, Card9 INT, Card10 INT, Card11 INT, Card12 INT )"%timeStr
	cur.execute(createTableStr)
	createGameStr = "CREATE TABLE hand%s (handID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, playerID INT NOT NULL, cardCount INT NOT NULL, Card0 INT, Card1 INT, Card2 INT, Card3 INT, Card4 INT)"%timeStr 
	cur.execute(createGameStr)
	p0InsertStr = "INSERT INTO game%s (id,cardCount) VALUES ('%d','13')" %(timeStr,p0Const)
	p1InsertStr = "INSERT INTO game%s (id,cardCount) VALUES ('%d','13')" %(timeStr,p1Const)
	p2InsertStr = "INSERT INTO game%s (id,cardCount) VALUES ('%d','13')" %(timeStr,p2Const)
	cur.execute(p0InsertStr)	
	cur.execute(p1InsertStr)
	cur.execute(p2InsertStr)
	updateTableWithStartingHand(p0Const, timeStr, players[0], db, cur)
	updateTableWithStartingHand(p1Const, timeStr, players[1], db, cur)
	updateTableWithStartingHand(p2Const, timeStr, players[2], db, cur)
	masterGameStr = "INSERT INTO masterGame (gameID, curPlayer, gameFull, gameFinished, cardCount) VALUES ('game%s','%d','0','0','0')"%(timeStr, startingData[0]) 
	#print(masterGameStr)
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
	#print(queryString)
	cur.execute(queryString)
	cardCount = cur.fetchall()
	#print("THIS IS THE CARD COUNT")
	#print(cardCount)
	count = cardCount[0][0]
	returnHand = []
	queryStr = "SELECT "
        if count != 0:
		for i in range(count):
        		 if i != 0 :
                		 queryStr = queryStr + ", "
                 	 queryStr = queryStr + "card%s"%i
        	queryStr = queryStr + " FROM %s WHERE id = '%s'"%(gameName, playerID)
		#print(queryStr)
		cur.execute(queryStr)
		queryResult = cur.fetchall()
		#print(queryResult)
		for i in range(count):
			returnHand.append(queryResult[0][i])	
	db.close()
	return returnHand

def joinRandomGameHelper(id,playerID,gameName, db, cur):
	    #db = get_db() 
	    #cur = db.cursor()
            updateTableStr = "UPDATE masterGame SET player%d=%d WHERE gameID ='%s'" %(id,playerID,gameName)
  	    #print(updateTableStr)
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
	#print("PLAYER STATUS")
	#print(playerStatus)
	gameName = playerStatus[0][3]
	playerNum = -1
	f = open('curPlayerNetworkCall', 'w')
	if playerStatus[0][0] is None:
        	joinRandomGameHelper(0,playerID,gameName, db, cur)
		playerNum = 0
	elif playerStatus[0][1] is None:
		joinRandomGameHelper(1,playerID,gameName, db, cur)
		playerNum = 1
	elif playerStatus[0][2] is None:
		joinRandomGameHelper(2,playerID,gameName, db, cur)
		playerNum = 2
		db = sqlite3.connect('pusoyDB')
       		cur = db.cursor()
		queryStr = "UPDATE masterGame SET gameFull='1' where gameID='%s'"%gameName 
		#print(queryStr)
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
	searchQuery = "SELECT curPlayer,gameFull,cardCount,gameFinished FROM masterGame WHERE gameID = '%s'"%gameID
	cur.execute(searchQuery)
	curPlayerStatus = cur.fetchall()
	cardCount = curPlayerStatus[0][2]
	returnHand = []
	if cardCount != 0: 
		queryStr = "SELECT "
		for i in range(cardCount):
			if i != 0 :
				queryStr = queryStr + ", "
			queryStr = queryStr + "card%s"%i
		queryStr = queryStr + " FROM masterGame WHERE gameID = '%s'"%gameID
		#print(queryStr)
		cur.execute(queryStr)
		hand = cur.fetchall()	
		for i in range(cardCount):
			returnHand.append(hand[0][i])
	
	return jsonify(curPlayer=curPlayerStatus[0][0],lastPlayedHand=returnHand,gameFull=curPlayerStatus[0][1],gameWon=curPlayerStatus[0][3])

@app.route('/getGameStatus/<string:gameID>/<int:lastHandID>')
def getGameStatus(gameID,lastHandID):
        db = get_db()
        cur = db.cursor()
	gameName = gameID
	gameID = gameID[4:]
        searchQuery = "SELECT handID FROM hand%s ORDER BY handID DESC LIMIT 1"%gameID
        #print(searchQuery)
	cur.execute(searchQuery)
	handIDs = cur.fetchall()
	curPlayer = -1
	if lastHandID == 0:
		fullQuery = "SELECT gameFull,curPlayer FROM masterGame WHERE gameID= '%s'"%gameName
		#print(fullQuery)
		cur.execute(fullQuery)
		vals = cur.fetchall()
		curPlayer = vals[0][1]
		if vals[0][0] == 0:
			return jsonify(gameFull=0)

        #curPlayerStatus = cur.fetchall()
        #print(handIDs)
	if not handIDs:
		return jsonify(curPlayer=curPlayer)
	maxHand = handIDs[0][0]
	numHands = maxHand  - lastHandID
	#print(numHands)
	returnHands = []
	turnIDs = []
	cardCounts = []
	playerIDs = []
	if numHands == 0:
		return jsonify(noNewHands=1)
	else:
		for i in range(numHands):
                        handID = lastHandID+i+1
			queryStr = "SELECT cardCount, playerID FROM hand%s where handID =%d"%(gameID, handID)
			cur.execute(queryStr)
			vals = cur.fetchall()
			cardCount = vals[0][0]
			playerID = vals[0][1]
			returnHand = []
                        if cardCount != 0:
                            queryStr = "SELECT "
                            for i in range(cardCount):
                                    if i != 0 :
                                            queryStr = queryStr + ", "
                                    queryStr = queryStr + "card%s"%i
                            queryStr = queryStr + " FROM hand%s  WHERE handID = '%s'"%(gameID, handID)
                            #print(queryStr)
                            cur.execute(queryStr)
                            hand = cur.fetchall()
                            for i in range(cardCount):
                                    returnHand.append(hand[0][i])
			playerIDs.append(playerID)
			cardCounts.append(cardCount)
                        returnHands.append(returnHand)
			turnIDs.append(handID)
		return jsonify(playerIDs=playerIDs,cardCounts=cardCounts,returnHands=returnHands,turnIDs=turnIDs)


@app.route('/login', methods=['POST'])
def login():
    if not request.json or not 'email' in request.json or not 'password' in request.json:
       # abort(400)
	return (jsonify(id=-3))
    db = get_db()
    cur = db.cursor()
    email = request.json['email']
    password = request.json['password']
    password.encode('ascii','ignore')
    str(email)
    queryStr = "SELECT password FROM players WHERE email = '%s'"%email
    isValidEmail = cur.execute(queryStr)
    queryResult = cur.fetchall()
    #alex fix
    if len(queryResult) ==  0:
        return (jsonify(id=-2))
    print("rowcount = %s"%cur.rowcount)
    print(queryResult)
    passwordSQL = queryResult[0][0]
    if password != passwordSQL:
        return (jsonify(id=-1))
    else:
	queryStr = "SELECT id FROM players WHERE email = '%s'"%email
        cur.execute(queryStr)
        idArray = cur.fetchall()
        id = idArray[0][0]
        db.commit()
        #print(id)
        return (jsonify(id=id))

@app.route('/signUp', methods=['POST'])
def newPlayer():
	if not request.json or not 'email' in request.json or not 'password' in request.json:
       		return "Bad Params"
	db = get_db()
	cur = db.cursor() 
	email = request.json['email']
	password = request.json['password']	
	queryStr = "SELECT * FROM players WHERE email = '%s'"%email
        print(queryStr)
	emailExists = cur.execute(queryStr)
        queryResult = cur.fetchall()
        #alex fix
        if len(queryResult) !=  0:
            print("shouldnt be here")
            return (jsonify(id=-1))
	queryStr = "INSERT INTO players (email, password) VALUES ('%s','%s')"%(email,password)
	cur.execute(queryStr)
	queryStr = "SELECT id FROM players WHERE email = '%s'"%email
	cur.execute(queryStr)
	idArray = cur.fetchall()
	id = idArray[0][0]
        queryStr = 'CREATE TABLE player%d(playerID INT PRIMARY KEY NOT NULL, friendStatus INT NOT NULL)'%id
        cur.execute(queryStr)
	db.commit()
	#print(id)
	return (jsonify(id=id))

@app.route('/playHand', methods=['POST'])
def create_task():
	#print("THIS IS THE PLAY HAND REQUEST")
	#print(request)
	#print(request.json)
	if not 'cards' in request.json or not 'playerID' in request.json or not 'gameID' in request.json:
		return "Bad Params"
	else:
		#print("IN RIGHT SECTION")
		db = get_db()
        	cur = db.cursor()
		cards = request.json['cards']
		playedCards = json.loads(cards)
		pass
		if len(playedCards) == 0:
			return "no cards"
		gameID = request.json['gameID']
		gameNum = gameID[4:]
		playerID = request.json['playerID']
		hand = getPlayer(gameID,playerID)
		rightCards = True
		cardFound = False
		gameStatusQuery = "cardCount=%d, "%len(playedCards)
		handQuery1 = ""
		handQuery2 = ""
		count = 0
		for playedCard in playedCards:
			comma = ""
			if count != 0:
				comma = ", "
			tempStr = comma + "card%d=%d"%(count, playedCard)
			tempHand1Str = comma + "card%d"%count
			tempHand2Str = comma + "%d"%playedCard
			gameStatusQuery = gameStatusQuery + tempStr
			handQuery1 = handQuery1 + tempHand1Str
			handQuery2 = handQuery2 + tempHand2Str
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
                	#print(queryStr)
                	cur.execute(queryStr)
		#updateTableStr = "UPDATE %s SET hand = '%s',cardCount=%d where id = %s"%(gameID,str(hand),len(hand),playerID)
		else:
			#print("You Have Won")	
			queryStr = "UPDATE masterGame SET gameFinished=1 where gameID=%s"%gameID
			return jsonify(gameWon=1)
        	db.commit()
		updatedCards = getPlayer(gameID,playerID)
	  	playerNum = findPlayerNum(gameID,playerID,db, cur)	
		playerNum = (playerNum)%3
		handQueryStr = "INSERT INTO hand%s ( playerID, cardCount, %s) VALUES (%d,%d,%s )"%(gameNum, handQuery1, playerNum, len(playedCards),handQuery2)
		#print("HAND QUERY STRING")
		#print(handQueryStr)
		cur.execute(handQueryStr)
		queryStr = "UPDATE masterGame SET %s,curPlayer='%d' WHERE gameID = '%s'"%(gameStatusQuery,playerNum,gameID)
		#print("ALEX LOOK UPDATE QUERY")
		#print(queryStr)
		cur.execute(queryStr)
		db.commit()	
		return jsonify(cardCount=len(updatedCards),cards=updatedCards)

@app.route('/passHand', methods=['POST'])
def playPassHand():
	if not 'playerID' in request.json or not 'gameID' in request.json:
        	return "Bad Params"
        else:
		db = get_db()
                cur = db.cursor()
		gameID = request.json['gameID']
		gameNum = gameID[4:]
        	playerID = request.json['playerID']
		playerNum = findPlayerNum(gameID,playerID, db, cur)
                playerNum = (playerNum)%3
		queryStr = "UPDATE masterGame SET cardCount=0,curPlayer='%s' WHERE gameID = '%s'"%(playerNum,gameID)
		handQueryStr = "INSERT INTO hand%s (playerID, cardCount) VALUES (%d,0 )"%(gameNum, playerNum)
		#print("PASS QUERY")
		#print(queryStr)
                cur.execute(queryStr)
		cur.execute(handQueryStr)
		db.commit() 
		return jsonify(passSuccess=1)
#Friend Status Codes 
#Orig Requesting 0
#Asked by other 1
#Friends 2
@app.route('/addFriend', methods=['POST'])
def addFriend():
    if not request.json or not 'origFriendID' in request.json or not 'newFriendEmail' in request.json:
       # abort(400)
	return (jsonify(id=-3))
    db = get_db()
    cur = db.cursor()
    origFriendID = request.json['origFriendID']
    newFriendEmail = request.json['newFriendEmail']
    queryStr = "SELECT ID FROM players WHERE email = '%s'"%newFriendEmail
    print(queryStr)
    cur.execute(queryStr)
    emailFetch = cur.fetchall()
    newFriendID = emailFetch[0][0]
    queryStr = "INSERT INTO player%s (playerID, friendStatus) VALUES (%s, OUTGOING_FRIEND__REGUEST)"%(origFriendID, newFriendID)
    cur.execute(queryStr)
    queryStr = "INSERT INTO player%s (playerID, friendStatus) VALUES (%s, INCOMING_FRIEND_REGUEST)"%(newFriendID, origFriendID)
    cur.execute(queryStr)
    db.commit()
    return jsonify(addFriend=1)

@app.route('/acceptFriend', methods=['POST'])
def accpetFriend():
    if not request.json or not 'origFriendID' in request.json or not 'newFriendEmail' in request.json:
       # abort(400)
	return (jsonify(id=-3))
    db = get_db()
    cur = db.cursor()
    origFriendID = request.json['origFriendID']
    newFriendEmail = request.json['newFriendEmail']
    queryStr = "SELECT ID FROM players WHERE email = '%s'"%newFriendEmail
    print(queryStr)
    cur.execute(queryStr)
    emailFetch = cur.fetchall()
    newFriendID = emailFetch[0][0]
    queryStr = "UPDATE player%s SET friendStatus=FRIENDS WHERE playerID=%s"%(origFriendID, newFriendID)
    cur.execute(queryStr)
    queryStr = "UPDATE player%s SET friendStatus=FRIENDS WHERE playerID=%s"%(newFriendID, origFriendID)
    cur.execute(queryStr)
    db.commit()
    return jsonify(acceptFriend=1)

@app.route('/getFriends/<int:playerID>')
def getFriends(playerID):
    db = get_db()
    cur = db.cursor()
    queryStr = "SELECT * FROM player%d"%playerID
    print(queryStr)
    cur.execute(queryStr)
    playerIDFetch = cur.fetchall()
    incomingFriendRequest = []
    outgoingFriendRequest = []
    friends = []
    for player in playerIDFetch:
        if player[1] == INCOMING_FRIEND_REGUEST:
            incomingFriendRequest.append(player[0])
        if player[1] == OUTGOING_FRIEND__REGUEST:
            outgoingFriendRequest.append(player[0])
        if player[1] == FRIENDS:
            friends.append(player[0])
    return jsonify(incomingFR=incomingFriendRequest, outgoingFR=outgoingFriendRequest, friends=friends)


if __name__ == '__main__':
        app.run(debug='true',host=ipAddress)
	#app.run()


@app.route('/')
def index():
    return "Hello, World!"
