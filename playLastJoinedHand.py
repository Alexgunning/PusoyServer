import os
f = open('curPlayerNetworkCall', 'r')

gameID = f.readline()
gameID = gameID.strip()
print(gameID)
handStrings = f.readline()
fullHand = eval(handStrings)
playHand = fullHand[8:]
playHandStr = str(playHand)
print(playHandStr)


playerIDStr = f.readline()

playerID = eval(playerIDStr)

networkCall = "curl -i -H \"Content-Type: application/json\" -X POST -d '{\"gameID\":\"%s\",\"playerID\":\"%d\",\"cards\":\"%s\"}' http://192.168.0.104:5000/playHand"%(gameID, playerID, playHandStr)
print(networkCall)
print(os.system(networkCall))
