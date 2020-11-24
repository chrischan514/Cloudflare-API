#!/usr/bin/env python3

# custom value should be defined in config.py
import requests
import os.path
import pathlib

if os.path.isfile(str(pathlib.Path(__file__).parent) + '/config.py'): #import custom config
    from config import *

try: #check is defined
    zone
except NameError:
    zone = input("Zone ID:")
    pass

try:
    token
except NameError:
    token = input("Token:")
    pass

try:
    domain
except NameError:
    domain = input("Your Domain:")
    pass

subdomain = input('Subdomain which you wanna check (Blank if all): ')
option = {"Content-Type": "application/json", "Authorization": "Bearer "+token} #HTTP Headers required in CloudFlare API

if subdomain != "":
    subdomain = subdomain + "." + domain

querydata = {"name": subdomain}
try:
    http = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records", headers=option, params=querydata) #calling CloudFlare API
except:
    print("Errors occurred!")
else:
    print(http.json())
