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

networkCall = "curl -i -H \"Content-Type: application/json\" -X POST -d '{\"email\":\"%s\",\"password\":\"%s\"}' http://%s:5000/signUp"%(email, password, ipAddress)
print(networkCall)
os.system(networkCall)
