#!/usr/bin/env python3


# custom value should be defined in config.py
import requests
import os.path
import pathlib
import argparse
parser = argparse.ArgumentParser(description="Asking CloudFlare's API to help you. For more details, please check https://github.com/chrischan514/Cloudflare-API/blob/main/README.md")
parser.add_argument('-m', dest="meth", action='store', default="dnsrec", help="specifying the method you wanna use. e.g. ddns update, check id only, etc.", choices=["dnsrec", "nameonly", "ddns", "id"])
parser.add_argument("-z", "--zone", dest="zone", action="store", help="input zone id", metavar="Zone ID")
parser.add_argument("-k", "--token", dest="token", action="store", help="input token", metavar="Token")
parser.add_argument("-s", "--subdomain",dest="subdomain", action="store", default="", help="input subdomain", metavar="Subdomain")
parser.add_argument("-t", "--type", dest="type", action="store", default="", help="type of record (A/AAAA/both)", metavar="Record TYPE")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="verbose mode")
parser.add_argument("-D", "--debug", dest="debug", action="store_true")
parser.add_argument("--without-proxy", dest="proxystatus",action="store_false", help="disable CF's proxy while creating record")
parser.add_argument("--provider", dest="provider", action="store", help="try choosing another provider set if it fails", default=2, type=int, choices=range(1,7))
args = parser.parse_args()
path = os.path.dirname(os.path.realpath(__file__))
config_loc = path + '/config.py'
zone = ""
token = ""
type = ""
subdomain = ""
if os.path.exists(config_loc): #import custom config
    import config
    if args.debug is True:
        print("Found")
        print(config.zone)
        print(config.token)
    if hasattr(config, 'zone'):
        zone = config.zone
    if hasattr(config, 'token'):
        token = config.token
    if hasattr(config, 'type'):
        type = config.type
    if hasattr(config, 'subdomain'):
        subdomain = config.subdomain

if args.zone != "" and args.zone is not None:
    zone = args.zone

if args.token != "" and args.token is not None:
    token = args.token

if args.type != "" and args.type is not None:
    type = args.type

if args.subdomain != "" and args.subdomain is not None:
    subdomain = args.subdomain

if args.debug is True:
    print(os.path.dirname(os.path.realpath(__file__)))
    print(config_loc)
    print(zone)
    print(token)
    print(type)
    print(subdomain)

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

def defSubdomain():
    global subdomain
    global subdomain1
    if subdomain=="" or subdomain is None:
        subdomain = input('Subdomain which you wanna check (Blank if all): ')
    if subdomain != "":
        if subdomain == "@":
            subdomain1 = domain
        else:
            subdomain1 = ".".join([subdomain, domain])
    else:
        subdomain1=""

def dnsDetailCore(subdomain, type):
    namequerydata = {"name": subdomain}
    namequerydata['type'] = type
    if args.debug is True:
        print(namequerydata)
        print("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records")
        print(namequerydata)
        print(option)
    try:
        http = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records", params=namequerydata, headers=option) #calling CloudFlare API
    except:
        print("Errors occurred!")
    else:
        return(http.json())

def dnsDetail():
    fetchDomainName()
    defSubdomain()
    if args.debug is True:
        print(type)
    if type is not None and type != "":
        if args.debug is True:
            print(type)
        print(dnsDetailCore(subdomain1, type))
    else:
        if args.debug is True:
            print(type)
        print(dnsDetailCore(subdomain1, "A"))
        print(dnsDetailCore(subdomain1, "AAAA"))

def dnsrec():
    print(dnsDetail())

def showDomainName():
    print(fetchDomainName())

def ddnsCore(type, subdomain):
    if type == "AAAA":
        site = requests.get("https://raw.githubusercontent.com/chrischan514/Cloudflare-API/main/provider.json").json()["set"][args.provider-1]["ipv6"]
        conntype = "IPv6"
    elif type == "A":
        site = requests.get("https://raw.githubusercontent.com/chrischan514/Cloudflare-API/main/provider.json").json()["set"][args.provider-1]["ipv4"]
        conntype = "IPv4"
    else:
        raise ValueError
    try:
        http = requests.get(site)
    except ConnectionError:
        print(conntype + " connection was not able to establish")
    else:
        ip = http.text
    updateparam = json.dumps({"type": type, "name": subdomain, "content": ip, "ttl": 1})
    if checkExist() is True:
        try:
            update = requests.put("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records/" + fetchID(), headers=option, data=updateparam) #calling CloudFlare API
        except:
            print("Errors occurred!")
        else:
            if args.verbose is True or args.debug is True:
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

def ddns():
    import json
    fetchDomainName()
    global type
    defSubdomain()
    if type == "A":
        ddnsCore(type, subdomain1)
    elif type == "AAAA":
        ddnsCore(type, subdomain)
    elif type=="" or type.lower()=="both":
        ddnsCore("A", subdomain)
        ddnsCore("AAAA", subdomain)
    else:
        raise ValueError

def checkExist():
    if dnsDetail()['result_info']['count']==0:
        return False
    else:
        return True

def fetchID():
    fetchDomainName()
    if subdomain is None or subdomain == "":
        subdomain1 = domain
    else:
        subdomain1 = ".".join([subdomain, domain])
    namequerydata = {"name": subdomain1}
    if type == "" or type is None:
        namequerydata['type'] = "A"
    else:
        namequerydata['type'] = type
    try:
        http = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records", headers=option, params=namequerydata) #calling CloudFlare API
    except:
        print("Errors occurred!")
    else:
        return(http.json()['result'][0]['id'])

def IDonly():
        fetchDomainName()
        if subdomain is None or subdomain == "":
            subdomain1 = domain
        else:
            subdomain1 = ".".join([subdomain, domain])
        namequerydata = {"name": subdomain1}
        namequerydata['type'] = type
        try:
            http = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records", headers=option, params=namequerydata) #calling CloudFlare API
        except:
            print("Errors occurred!")
        else:
            for item in http.json()["result"]:
                print(item["type"] + ": " + item["id"])

def debug():
    print(checkExist())

methods = {"dnsrec": dnsrec, "nameonly": showDomainName, "ddns": ddns, "id": IDonly, "debug": debug}
start = methods[args.meth]
if args.debug is True:
    print(os.path.dirname(os.path.realpath(__file__)))
    print(config_loc)
    print(zone)
    print(token)
    print(type)
    print(subdomain)
start()
