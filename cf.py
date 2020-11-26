#!/usr/bin/env python3



# custom value should be defined in config.py
import requests
import os.path
import pathlib
import argparse
parser = argparse.ArgumentParser(description="Asking CloudFlare's API to help you. For more details, please check https://github.com/chrischan514/Cloudflare-API/blob/main/README.md")
parser.add_argument('-m', dest="meth", action='store', default="dnsrec", help="specifying the method you wanna use. e.g. ddns update, check id only, etc.", choices=["dnsrec", "nameonly", "ddns", "id"])
parser.add_argument("--zone", dest="zone", action="store", help="input zone id", metavar="Zone ID")
parser.add_argument("--token", dest="token", action="store", help="input token", metavar="Token")
parser.add_argument("-s", dest="subdomain", action="store", default="", help="input subdomain", metavar="Subdomain")
parser.add_argument("--type", dest="type", action="store", default="", help="type of record (A/AAAA)", metavar="Record TYPE")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="verbose mode")
parser.add_argument("--without-proxy", dest="proxystatus",action="store_false", help="disable CF's proxy while creating record")
parser.add_argument("--provider", dest="provider", action="store", help="try choosing another provider set if it fails", default=2, type=int, choices=range(1,7))
args = parser.parse_args()

zone, token, type, subdomain = args.zone, args.token, args.type, args.subdomain

if os.path.isfile(str(pathlib.Path(__file__).parent) + '/config.py'): #import custom config
    from config import *


if zone=="" or zone is None:
    zone = input("Zone ID: ")

if token=="" or token is None:
    token = input("Token: ")

option = {"Content-Type": "application/json", "Authorization": "Bearer "+str(token)} #HTTP Headers required in CloudFlare API

def fetchDomainName():
    try:
        domainquery = requests.get("https://api.cloudflare.com/client/v4/zones/" + str(zone), headers=option)
    except:
        print("Errors occurred!")
    else:
        global domain
        domain = domainquery.json()["result"]["name"]
        return domain

def dnsDetail():
    fetchDomainName()
    if args.subdomain=="":
        subdomain = input('Subdomain which you wanna check (Blank if all): ')
    else:
        subdomain = args.subdomain
    if subdomain != "":
        subdomain1 = ".".join([subdomain, domain])
    else:
        subdomain1=""
    namequerydata = {"name": subdomain1}
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
    ipv6, ipv4 = requests.get("https://raw.githubusercontent.com/chrischan514/Cloudflare-API/main/provider.json").json()["set"][args.provider-1]["ipv6"], requests.get("https://raw.githubusercontent.com/chrischan514/Cloudflare-API/main/provider.json").json()["set"][args.provider-1]["ipv4"]
    if type == "A":
        site = ipv4
    elif type == "AAAA":
        site = ipv6
    elif type=="":
        site, type = ipv4, "A"
    else:
        raise ValueError
    if subdomain =="":
        subdomain1 = input("Subdomain you wanna update: ")
    else:
        subdomain1 = args.subdomain
    subdomain1 = ".".join([subdomain, domain])
    try:
        http = requests.get(site)
    except ConnectionError:
        print("Error! Probably this connection type is not supported in your network, or the query sites have been blocked!")
    else:
        ip = http.text
    updateparam = json.dumps({"type": type, "name": subdomain, "content": ip, "ttl": 1})
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
    subdomain1 = ".".join([subdomain, domain])
    namequerydata = {"name": subdomain1}
    if type != "":
        namequerydata['type'] = type
    else:
        namequerydata['type'] = "A"
    try:
        http = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records", headers=option, params=namequerydata) #calling CloudFlare API
    except:
        print("Errors occurred!")
    else:
        return(http.json()['result'][0]['id'])

def IDonly():
    print(fetchID())

def debug():
    print(checkExist())

methods = {"dnsrec": dnsrec, "nameonly": showDomainName, "ddns": ddns, "id": IDonly, "debug": debug}
start = methods[args.meth]
start()
