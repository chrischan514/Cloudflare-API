#!/usr/bin/env python3

# custom value should be defined in config.py
import requests
import os.path
import pathlib
import argparse

parser = argparse.ArgumentParser(description="Asking CloudFlare's API to help you. For more details, please check https://github.com/chrischan514/Cloudflare-API/blob/main/README.md")
parser.add_argument('-m', dest="meth", action='store', default="dnsrec", help="specifying the method you wanna use. e.g. ddns update, check id only, etc.")
parser.add_argument("--zone", dest="zone", action="store", help="input zone id")
parser.add_argument("--token", dest="token", action="store", help="input token")
parser.add_argument("-s", dest="subdomain", action="store", default="", help="input subdomain")
parser.add_argument("--type", dest="type", action="store", default="", help="type of record (A/AAAA)")
parser.add_argument("-v", dest="verbose", action="store_true", help="verbose mode")
parser.add_argument("--without-proxy", dest="proxystatus",action="store_false", help="disable CF's proxy while creating record")
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

def dnsDetail():
    fetchDomainName()
    if args.subdomain is None:
        subdomain = input('Subdomain which you wanna check (Blank if all): ')
    else:
        subdomain = args.subdomain
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
        return(http.json())

def dnsrec():
    print(dnsDetail())

def showDomainName():
    print(fetchDomainName())

def ddns():
    import json
    fetchDomainName()
    global type
    global subdomain
    if type == "A":
        site = "http://ipv4.ident.me"
    elif type == "AAAA":
        site = "http://ipv6.ident.me"
    elif type=="":
        site = "http://ipv4.ident.me"
        type = "A"
    else:
        raise ValueError
    if args.subdomain is None:
        subdomain = input("Subdomain you wanna update: ")
    else:
        subdomain = args.subdomain
    subdomain = subdomain + "." + domain
    http = requests.get(site)
    ip = http.text
    updateparam = {"type": type, "name": subdomain, "content": ip, "ttl": 1}
    updateparam = json.dumps(updateparam)
    if checkExist() is True:
        try:
            update = requests.put("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records/" + fetchID(), headers=option, data=updateparam) #calling CloudFlare API
        except:
            print("Errors occurred!")
        else:
            if args.verbose is True:
                print(update.text)
    else:
        if args.proxystatus is not False:
            updateparam=json.loads(updateparam)
            updateparam["proxied"] = True
            updateparam = json.dumps(updateparam)
        try:
            update = requests.post("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records/", headers=option, data=updateparam) #calling CloudFlare API
        except:
            print("Errors occurred!")
        else:
            if args.verbose is True:
                print(update.text)

def checkExist():
    if dnsDetail()['result_info']['count']==0:
        return False
    else:
        return True

def fetchID():
    fetchDomainName()
    global subdomain
    subdomain = subdomain + "." + domain
    namequerydata = {"name": subdomain}
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
