#!/usr/bin/env python3

# custom value should be defined in config.py
import requests
import os.path
import pathlib
import argparse

parser = argparse.ArgumentParser(description="Asking CloudFlare's API to help you.")
parser.add_argument('-m', dest="meth", action='store', default="dnsrec")
parser.add_argument("--zone", dest="zone", action="store")
parser.add_argument("--token", dest="token", action="store")
parser.add_argument("-s", dest="subdomain", action="store", default="")
parser.add_argument("--type", dest="type", action="store", default="")
args = parser.parse_args()

zone = args.zone
token = args.token
type = args.type
subdomain = args.subdomain

if os.path.isfile(str(pathlib.Path(__file__).parent) + '/config.py'): #import custom config
    from config import *

try: #check is defined
    zone
except NameError:
    zone = input("Zone ID:")
    pass
else:
    if zone is None:
        zone = input("Zone ID:")

try:
    token
except NameError:
    token = input("Token:")
    pass
else:
    if token is None:
        token = input("Token:")

option = {"Content-Type": "application/json", "Authorization": "Bearer "+token} #HTTP Headers required in CloudFlare API

def fetchDomainName():
    try:
        domainquery = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone, headers=option)
    except:
        print("Errors occurred!")
    else:
        global domain
        domain = domainquery.json()["result"]["name"]
        return domain

def dnsrec():
    fetchDomainName()
    subdomain = input('Subdomain which you wanna check (Blank if all): ')
    if subdomain != "":
        subdomain = subdomain + "." + domain


    namequerydata = {"name": subdomain}
    if type != "":
        namequerydata['type'] = type
    try:
        http = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records", params=namequerydata, headers=option) #calling CloudFlare API
    except:
        print("Errors occurred!")
    else:
        print(http.json())

def showDomainName():
    print(fetchDomainName())

def ddns():
    import json
    fetchDomainName()
    if type == "A":
        site = "http://ipv4.ident.me"
    elif type == "AAAA":
        site = "http://ipv6.ident.me"
    else:
        raise ValueError
    if args.subdomain == "":
        subdomain = input("Subdomain you wanna update: ")
    else:
        subdomain = args.subdomain
    subdomain1 = subdomain + "." + domain
    http = requests.get(site)
    ip = http.text
    updateparam = {"type": type, "name": subdomain1, "content": ip, "ttl": 1}
    updateparam = json.dumps(updateparam)
    try:
        update = requests.put("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records/" + fetchID(), headers=option, data=updateparam) #calling CloudFlare API
    except:
        print("Errors occurred!")

def fetchID():
    fetchDomainName()
    subdomain1 = subdomain + "." + domain
    namequerydata = {"name": subdomain1}
    if type != "":
        namequerydata['type'] = type
    try:
        http = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records", headers=option, params=namequerydata) #calling CloudFlare API
    except:
        print("Errors occurred!")
    else:
        return(http.json()['result'][0]['id'])

def IDonly():
    print(fetchID())

methods = {"dnsrec": dnsrec, "nameonly": showDomainName, "ddns": ddns, "id": IDonly}
start = methods[args.meth]
start()
