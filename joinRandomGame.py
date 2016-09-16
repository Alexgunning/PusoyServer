import os
import sys
from random import randint

f=open('ipAddress','r')
ipAddress = f.readline()
ipAddress = ipAddress.rstrip()
randomNum = randint(0,1000) 
print(randomNum)

networkCall = "curl -i -H \"Content-Type: application/json\" http://%s:5000/joinRandomGame/%d"%(ipAddress,randomNum)
print(networkCall)
os.system(networkCall)
