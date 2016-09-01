import sqlite3
gameID = "game16235023543"
db = sqlite3.connect("pusoyDB")
cur = db.cursor()
searchQuery = "SELECT curPlayer,lastPlayedHand,gameFull FROM gameStatus WHERE gameID = '%s'"%gameID
cur.execute(searchQuery)
curPlayerStatus = cur.fetchall()
pArray = curPlayerStatus[0][1]
print("cur player array type")
print(type(pArray))
curNum = []
for i in range(len(pArray)):
	print(i)
	x = int(pArray(i))
	print(x)
