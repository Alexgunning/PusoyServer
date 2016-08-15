#!flask/bin/python
import MySQLdb
from flask import Flask, jsonify
from flask import request
from flask import make_response
from flask import abort
import json
import random
from time import gmtime, strftime

#timeStr = strftime("%H%M%S", gmtime())

db = MySQLdb.connect("localhost","root","KopitarTrout27","ALEX")
db.autocommit = 1
cur = db.cursor()

def initHands(timeStr):
	cards = range(52)
	random.shuffle(cards)
	p1 = cards[0:13]
	p2 = cards[14:27]
	p3 = cards[28:41]
	return [p1,p2,p3]

def createPlayerInsert(cardList,timeStr,playerNum):
	insertStart = "INSERT INTO game%s (`id`,`card1`,`card2`,`card3`,`card4`,`card5`,`card6`,`card7`,`card8`,`card9`,`card10`,`card11`,`card12`,`card13`) VALUES ('%d',"%(timeStr,-playerNum) 
        returnString = insertStart
        for card in range(13):
                 if card < len(cardList):
                         returnString = returnString +  "'%d',"%cardList[card]
                 else:
                         returnString = returnString + "'null',"
        returnString = returnString[:-1]
        returnString = returnString + ")"
        return returnString

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

def CreateGame():
	timeStr = strftime("%y%j%H%M%S", gmtime())
	players = initHands(timeStr)
	playerHand1 = createPlayerInsert(players[0],timeStr,0)
	playerHand2 = createPlayerInsert(players[1],timeStr,1)
	playerHand3 = createPlayerInsert(players[2],timeStr,2)
	rank52altSorted = rank52alt()
	startingData = findStartingPlayer(players)	
	gameStatusTableStr = "Insert into gameStatus (gameID,curplayer) VALUES ('game%s','%d')"%(timeStr,startingData[0])
	cur.execute(gameStatusTableStr)
	createTableStr = "CREATE TABLE game" + timeStr + " (id INT, card1 INT, card2 INT, card3 INT, card4 INT, card5 INT, card6 INT, card7 INT, card8 INT, card9 INT, card10 INT, card11 INT, card12 INT, card13 INT)"
	cur.execute(createTableStr)
	print(playerHand1)
        cur.execute(playerHand1)
        cur.execute(playerHand2)
        cur.execute(playerHand3)
	gameStr = "game" + timeStr
	queryStr = "INSERT INTO allGames (gameID,player0,player1,player2,gameFinished) VALUES('%s',null,null,null,FALSE)"%gameStr
	cur.execute(queryStr)
	db.commit()


def findPlayerGameID(ID):
	queryString = "SELECT gameID FROM allGames where (player0=%d || player1=%d || player2=%d) && gameFinished=FALSE"%(ID,ID,ID)
	if(cur.execute(queryString)):
		fetchGet = cur.fetchall()
		return fetchGet[0][0]
	else:
		return "fail"

def getPlayer(gameName,playerID):
	queryString = "SELECT * FROM %s WHERE id = %s"%(gameName,playerID)
	print(queryString)
	cur = db.cursor()
	cur.execute(queryString)
	queryResult = cur.fetchall()
	print("QUERY RESULT FETCHALL FOR CARDS")
	print(queryResult)
	cardListArr = []
	for xx in queryResult:
        	for i in range(1,14):
               		 if xx[i] is not None:
				cardListArr.append(xx[i])
	return cardListArr

def updateDB(card,gameID,playerID):
        cardList = getPlayer(gameID,playerID)
        cardIndex = cardList.index(card)
        cardIndex = cardIndex + 1
        updateTableStr = "UPDATE %s SET card%d=null WHERE id=%s"%(gameID,cardIndex,playerID)
        print(updateTableStr)
        cur.execute(updateTableStr)
        db.commit()

def joinRandomGameHelper(id,playerID,gameName):
                updateTableStr = "UPDATE allGames SET player%d=%d WHERE gameID ='%s'" %(id,playerID,gameName)
  		print(updateTableStr)
                cur.execute(updateTableStr)
                db.commit()
		updateTableStr = "UPDATE %s SET id=%d WHERE id=%d"%(gameName,playerID,-id)
		print(updateTableStr)
		cur.execute(updateTableStr)
                db.commit()


app = Flask(__name__)
@app.route('/joinRandomGame/<int:playerID>')
def joinRandomGame(playerID):
	cur.execute("SELECT player0,player1,player2,gameID FROM allGames ORDER BY gameID DESC LIMIT 1")
	playerStatus = cur.fetchall()
	gameName = playerStatus[0][3]
	playerNum = -1
	if playerStatus[0][0] is None:
        	joinRandomGameHelper(0,playerID,gameName)
		playerNum = 0
	elif playerStatus[0][1] is None:
		joinRandomGameHelper(1,playerID,gameName)
		playerNum = 1
	elif playerStatus[0][2] is None:
		joinRandomGameHelper(2,playerID,gameName)
		playerNum = 2
		CreateGame()
	hand = getPlayer(gameName,playerID)
	
	return jsonify(game=gameName,hand=hand,playerNum=playerNum,cardCount=len(hand))

@app.route('/checkGameStatus', methods=['POST'])
def gameStatus():
	if  not 'gameID' in request.json:
		return "BAD PARAMS"
	gameID = request.json['gameID']
	print(gameID)
	searchQuery = "SELECT curPlayer,lastPlayedHand FROM gameStatus WHERE gameID = '%s'"%gameID
	cur.execute(searchQuery)
	curPlayerStatus = cur.fetchall()
	return jsonify(curPlayer=curPlayerStatus[0][0],lastPlayedHand=curPlayerStatus[0][1])

@app.route('/login', methods=['POST'])
def login():
    if not request.json or not 'email' in request.json or not 'password' in request.json:
       # abort(400)
	return (jsonify(id=-3)) 
    email = request.json['email']
    password = request.json['password']
    password.encode('ascii','ignore')
    str(email)
    queryStr = "SELECT password from players where email = '%s'"%email
    isValidEmail = cur.execute(queryStr)
    if isValidEmail == 0:
    	return (jsonify(id=-2))
    queryResult = cur.fetchall()
    
    passwordSQL = queryResult[0][0]
    if password != passwordSQL:
    	return (jsonify(id=-1))
    else:
	queryStr = "SELECT id from players where email = '%s'"%email
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
	email = request.json['email']
	password = request.json['password']	
	queryStr = "SELECT * from players where email = '%s'"%email
	emailExists = cur.execute(queryStr)
	if emailExists != 0:
		return (jsonify(id=-1))
	queryStr = "INSERT INTO players (email, password) VALUES ('%s','%s')"%(email,password)
	cur.execute(queryStr)
	queryStr = "SELECT id from players where email = '%s'"%email
	cur.execute(queryStr)
	idArray = cur.fetchall()
	id = idArray[0][0]
	db.commit()
	print(id)
	return (jsonify(id=id))

@app.route('/playHand', methods=['POST'])
def create_task():
	if not request.json or not 'cardCount' in request.json or not 'cards' in request.json or not 'playerID' in request.json or not 'gameID' in request.json:
		return "Bad Params"
	else:
		cards = request.json['cards']
		arrayOfCards = json.loads(cards)
		for i in arrayOfCards:
			updateDB(i,request.json['gameID'],request.json['playerID'])
		updatedCards = getPlayer(request.json['gameID'],request.json['playerID'])
		return jsonify(cards=updatedCards)
                  

if __name__ == '__main__':
    app.run(debug = True)


@app.route('/')
def index():
    return "Hello, World!"
	
