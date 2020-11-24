#!/bin/bash
python3 -c 'import requests' > /dev/null 2>&1
if [ $? == 0 ]; then
	echo "Initialised"
else
	echo "installing necessary component"
	pip3 install requests -y
fi
clear

python3 <(curl -s https://raw.githubusercontent.com/chrischan514/Cloudflare-API/main/cf.py)
