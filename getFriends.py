import os
import sys
import sqlite3
print(str(sys.argv))

#1st Arg playerID
playerID = sys.argv[1]

f=open('ipAddress','r')
ipAddress = f.readline()
ipAddress = ipAddress.rstrip()

networkCall = "curl -i -H \"Content-Type: application/json\" http://%s:5000/getFriends/%s"%(ipAddress,playerID)
print(networkCall)
os.system(networkCall)
