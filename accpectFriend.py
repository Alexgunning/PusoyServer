import os
import sys
import sqlite3
print(str(sys.argv))

#1st Arg username, 2nd Arg pasword
origFriendID = sys.argv[1]
newFriendEmail = sys.argv[2]

print(origFriendID)
print(newFriendEmail)

f=open('ipAddress','r')
ipAddress = f.readline()
ipAddress = ipAddress.rstrip()

networkCall = "curl -i -H \"Content-Type: application/json\" -X POST -d '{\"origFriendID\":\"%s\",\"newFriendEmail\":\"%s\"}' http://%s:5000/addFriend"%(origFriendID, newFriendEmail, ipAddress)
print(networkCall)
os.system(networkCall)
