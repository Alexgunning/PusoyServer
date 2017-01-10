#!/bin/bash

ipAddrNew=$(ifconfig | grep 'inet addr:192' | sed 's/[[:blank:]]*inet addr://' | sed 's/\s.*$//') 

ipAddrOld=$(cat /home/alexgunning/flaskApp/ipAddress)

if [ "$ipAddrOld" != "$ipAddrNew" ]; then
	echo "$ipAddrNew" | mail -s "IP Address Changed" alexandergunning@gmail.com
#	echo "$ipAddrNew" > ipAddress
fi
