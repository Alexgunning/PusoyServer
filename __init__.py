#flask/bin/python
import MySQLdb
from flask import Flask, jsonify
from flask import request
from flask import make_response
from flask import abort
from flask import g
import json
import random
import sqlite3
from time import gmtime, strftime

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


def findPlayerNum(gameID,playerID):
	queryStr = "SELECT player0,player1,player2 FROM allGames WHERE gameID = '%s'"%gameID
	cur.execute(queryStr)
	playerDB = cur.fetchall()
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
	gameStatusTableStr = "INSERT INTO gameStatus (gameID,curPlayer,lastPlayedHand,gameFull) VALUES ('game%s','%d','100,100','0')"%(timeStr,startingData[0])
	cur.execute(gameStatusTableStr)
	createTableStr = "CREATE TABLE game%s (id INT, cardCount INT, hand VARCHAR(60))"%timeStr
	cur.execute(createTableStr)
	p0InsertStr = "INSERT INTO game%s (id,cardCount,hand) VALUES ('%d','13','%s')" %(timeStr,p0Const,str(players[0]))
	p1InsertStr = "INSERT INTO game%s (id,cardCount,hand) VALUES ('%d','13','%s')" %(timeStr,p1Const,str(players[1]))
	p2InsertStr = "INSERT INTO game%s (id,cardCount,hand) VALUES ('%d','13','%s')" %(timeStr,p2Const,str(players[2]))
	cur.execute(p0InsertStr)	
	cur.execute(p1InsertStr)
	cur.execute(p2InsertStr)
	gameStr = "game" + timeStr
	queryStr = "INSERT INTO allGames (gameID,player0,player1,player2,gameFinished) VALUES('%s',null,null,null,0)"%gameStr
	print(queryStr)
	cur.execute(queryStr)
	db.commit()
def CreateGameOutside():
	db  = sqlite3.connect(DATABASE)
        cur = db.cursor()
	CreateGame(db, cur)

CreateGameOutside()
	
def findPlayerGameID(ID):
	queryString = "SELECT gameID FROM allGames where (player0=%d || player1=%d || player2=%d) && gameFinished=FALSE"%(ID,ID,ID)
	if(cur.execute(queryString)):
		fetchGet = cur.fetchall()
		return fetchGet[0][0]
	else:
		return "fail"

def getPlayer(gameName,playerID):
	db = get_db()
        cur = db.cursor()
	queryString = "SELECT hand FROM %s WHERE id = %s"%(gameName,playerID)
	print(queryString)
	cur.execute(queryString)
	queryResult = cur.fetchall()
	print(queryResult)
	db.close()
	return eval(queryResult[0][0])

def joinRandomGameHelper(id,playerID,gameName, db, cur):
	    #db = get_db() 
	    #cur = db.cursor()    
            updateTableStr = "UPDATE allGames SET player%d=%d WHERE gameID ='%s'" %(id,playerID,gameName)
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
	cur.execute("SELECT player0,player1,player2,gameID FROM allGames ORDER BY gameID DESC LIMIT 1")
	playerStatus = cur.fetchall()
	gameName = playerStatus[0][3]
	playerNum = -1
	#db.close()
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
		queryStr = "UPDATE gameStatus SET gameFull='1' where gameID='%s'"%gameName 
		print(queryStr)
		cur.execute(queryStr)
		#db.close()
		CreateGame(db, cur)
	hand = getPlayer(gameName,playerID)
	print(hand)
	print(type(hand))	
	return jsonify(game=gameName,hand=hand,playerNum=playerNum,cardCount=len(hand))

@app.route('/checkGameStatus/<string:gameID>')
def gameStatus(gameID):
	db = get_db()
	cur = db.cursor()
	searchQuery = "SELECT curPlayer,lastPlayedHand,gameFull FROM gameStatus WHERE gameID = '%s'"%gameID
	cur.execute(searchQuery)
	curPlayerStatus = cur.fetchall()
	curPlayerArray = curPlayerStatus[0][1]
	print("cur player array")
	print(curPlayerArray)
	curplayerArray = curPlayerArray.split
	print("cur player array split")
	print(curPlayerArray)
	#curPlayerArray = curPlayerArray.split(',')
	#print(curPlayerArray)
	print(type(curPlayerArray))
	curPlayerArray= int(curPlayerArray)
	print("cur player array new")
	print(type(curPlayerArray))
	return jsonify(curPlayer=curPlayerStatus[0][0],lastPlayedHand=curPlayerArray,gameFull=curPlayerStatus[0][2])

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
	if not 'cards' in request.json or not 'playerID' in request.json or not 'gameID' in request.json:
		return "Bad Params"
	else:
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
		for playedCard in playedCards:
			for handCard in hand:
				if playedCard == handCard:
					cardFound = True
			if not cardFound:
				rightCards = False
			cardFound = False
		if not rightCards:
			return "Cards not found in hand"
		for playedCard in playedCards:
			hand.remove(playedCard)
		updateTableStr = "UPDATE %s SET hand = '%s',cardCount=%d where id = %s"%(gameID,str(hand),len(hand),playerID)
		print(updateTableStr)
		cur.execute(updateTableStr)
		
        	db.commit()
		updatedCards = getPlayer(gameID,playerID)
	  	playerNum = findPlayerNum(gameID,playerID)	
		playerNum = (playerNum+1)%3
		queryStr = "UPDATE gameStatus SET lastPlayedHand='%s',curPlayer='%d' WHERE gameID = '%s'"%(str(playedCards),playerNum,gameID)
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
		queryStr = "UPDATE gameStatus SET lastPlayedHand=100,100,curPlayer='%s' WHERE gameID = '%s'"%(playerNum,gameID)
        	cur.execute(queryStr)
		db.commit() 
		return "Hand Passed"		
	

if __name__ == '__main__':
    app.run(host = '192.168.0.110')


@app.route('/')
def index():
    return "Hello, World!"
