import os
import sys
import sqlite3
print(str(sys.argv))

#1st Arg username, 2nd Arg pasword
email = sys.argv[1]
password = sys.argv[2]

f=open('ipAddress','r')
ipAddress = f.readline()
ipAddress = ipAddress.rstrip()

networkCall = "curl -i -H \"Content-Type: application/json\" http://%s:5000/newPlayer/%s/%s"%(ipAddress,email,password)
print(networkCall)
os.system(networkCall)
