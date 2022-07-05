#!/usr/bin/env python3

import hashlib

# custom value should be defined in config.py
import requests
import os.path
import pathlib
import argparse
import json

parser = argparse.ArgumentParser(description="Asking CloudFlare's API to help you. For more details, please check https://github.com/chrischan514/Cloudflare-API/blob/main/README.md")
parser.add_argument('-m', dest="meth", action='store', default="dnsrec", help="specifying the method you wanna use. e.g. ddns update, check id only, etc.", choices=["dnsrec", "nameonly", "ddns", "id"])
parser.add_argument("-z", "--zone", dest="zone", action="store", help="input zone id", metavar="Zone ID")
parser.add_argument("-k", "--token", dest="token", action="store", help="input token", metavar="Token")
parser.add_argument("-s", "--subdomain",dest="subdomain", action="store", default="", help="input subdomain", metavar="Subdomain")
parser.add_argument("-t", "--type", dest="type", action="store", default="", help="type of record (A/AAAA/both)", metavar="Record TYPE")
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="verbose mode")
parser.add_argument("--disable-auto-update", dest="disableautoupdate", action="store_true", help="disable the automatic update feature")
parser.add_argument("-D", "--debug", dest="debug", action="store_true")
parser.add_argument("--without-proxy", dest="proxystatus",action="store_false", help="disable CF's proxy while creating record")
parser.add_argument("--provider", dest="provider", action="store", help="try choosing another provider set if it fails", default=2, type=int, choices=range(1,7))
parser.add_argument("-V","--version", dest="printversion",action="store_true", help="version detail")
args = parser.parse_args()
path = os.path.dirname(os.path.realpath(__file__))
config_loc = path + '/config.py'
zone = ""
token = ""
type = ""
subdomain = ""
idtype=type

if os.path.exists(path+"/scriptmode"):
    scriptmode=True
else:
    scriptmode = False

metadata = {
    "version": "1.0.0",
    "buildnum": "2022070501"
}

def checkInternetConnection():
    try:
    	request = requests.get("https://www.google.com/", timeout=5)
    except (requests.ConnectionError, requests.Timeout) as exception:
    	raise Exception("No internet connection.")

def checkUpdate():
    print("Verifying updates...")
    if metadata["buildnum"] != requests.get("https://raw.githubusercontent.com/chrischan514/Cloudflare-API/main/metadata.json",headers={'Cache-Control': 'no-cache'}).json()["buildnum"]:
        print("Update available")
        try:
            print("Trying to update the script automatically...")
            open(path + '/cf.py', "w").write(requests.get("https://raw.githubusercontent.com/chrischan514/Cloudflare-API/main/cf.py",headers={'Cache-Control': 'no-cache'}).text)
        except:
            print("Unable to update the script automatically")
        else:
            import platform
            print("Updated Successfully\n")
            if platform.system() == "Windows":
                "Automatically restarting the scipt is currenly not supported on Windows, please launch the script again manually"
            else:
                try:
                    print("Restarting the script...")
                except:
                    print("Unable to restart the script, please restart manually")
                else:
                    import sys
                    os.execl(sys.executable, *([sys.executable]+sys.argv))

if args.meth != "dnsrec" and args.meth != "nameonly" and args.meth != "ddns" and args.meth != "id":
    raise ValueError("Unknown selected method")

if os.path.exists(config_loc): #import custom config
    import config
    if args.debug is True:
        print("Found configuration file")
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
        subdomain = input('Subdomain which you wanna check (Blank if all, @ for root domain): ')
    if subdomain != "":
        if subdomain == "@":
            subdomain1 = domain
        else:
            subdomain1 = ".".join([subdomain, domain])
    else:
        subdomain1=""

def dnsDetail():
    fetchDomainName()
    defSubdomain()
    if args.debug is True:
        print(idtype)
    def dnsDetailCore(subdomain, type):
        namequerydata = {"name": subdomain}
        namequerydata['type'] = idtype
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
    if type is not None and type != "":
        if args.debug is True:
            print(type)
        if args.meth == "dnsrec":
            print(dnsDetailCore(subdomain1, type))
    else:
        if args.debug is True:
            print(type)
        if args.meth == "dnsrec":
            dnsDetailCore(subdomain1, "A")
            dnsDetailCore(subdomain1, "AAAA")
    if dnsDetailCore(subdomain1, "A")['result_info']['count']==0 and dnsDetailCore(subdomain1, "AAAA")['result_info']['count']==0:
        return False
    else:
        return True

def dnsrec():
    dnsDetail()

def showDomainName():
    print(fetchDomainName())

def ddns():
    import json
    fetchDomainName()
    defSubdomain()
    def ddnsCore(type, subdomain):
        global idtype
        idtype = type
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

        def checkIPCache(type,ip):
            iplist = ["",""]
            if args.debug is True:
                print(ip)

            if os.path.exists(path + '/ipcache.txt') and len(open(path + '/ipcache.txt', "r").readlines())>0:
                iplist = [open(path + '/ipcache.txt', "r").read().splitlines()[0],open(path + '/ipcache.txt', "r").read().splitlines()[-1]]

            if type == "A":
                cacheip = iplist[0]
            elif type == "AAAA":
                cacheip = iplist[1]

            def updateIPCache():
                nonlocal iplist
                if type == "A" or type == "AAAA":
                    if args.debug is True:
                        print(iplist)
                    if type == "A":
                        iplist[0]=ip
                    elif type == "AAAA":
                        iplist[1]=ip
                    open(path + '/ipcache.txt', 'w').writelines(iplist[0]+"\n"+iplist[1])

            if os.path.exists(path + '/ipcache.txt') and cacheip == ip:
                return False
            else:
                updateIPCache()
                return True

        if checkIPCache(type, ip) == True:
            updateparam = json.dumps({"type": type, "name": subdomain, "content": ip, "ttl": 1})
            if dnsDetail() is True:
                try:
                    if args.verbose is True:
                        print("Trying to update record")
                    update = requests.put("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records/" + fetchID(), headers=option, data=updateparam) #calling CloudFlare API
                except:
                    print("Errors occurred! Unable to update record")
                    if os.path.exists(path + '/ipcache.txt'):
                        os.remove(path + '/ipcache.txt')
                else:
                    if args.verbose is True or args.debug is True:
                        print(update.text)
            else:
                if args.proxystatus is not False:
                    updateparam=json.loads(updateparam)
                    updateparam["proxied"] = True
                    updateparam = json.dumps(updateparam)
                try:
                    if args.verbose is True:
                        print("Trying to create record")
                    update = requests.post("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records/", headers=option, data=updateparam) #calling CloudFlare API

                except:
                    print("Errors occurred! Unable to create record")
                    if os.path.exists(path + '/ipcache.txt'):
                        os.remove(path + '/ipcache.txt')
                else:
                    if args.verbose is True:
                        print(update.text)
        else:
            print("IP address remain unchanged, no action needed")

    if type == "A" or type == "AAAA":
        ddnsCore(type, subdomain1)
    elif type=="" or type.lower()=="both":
        ddnsCore("A", subdomain)
        ddnsCore("AAAA", subdomain)
    else:
        raise ValueError

def fetchID():
    fetchDomainName()
    defSubdomain()
    namequerydata = {"name": subdomain1}
    if idtype == "" or idtype is None:
        if type == "" or type is None:
            namequerydata['type'] = "A"
        else:
            namequerydata['type'] = type
    else:
        namequerydata['type'] = idtype
    try:
        http = requests.get("https://api.cloudflare.com/client/v4/zones/" + zone + "/dns_records", headers=option, params=namequerydata) #calling CloudFlare API
    except:
        print("Errors occurred! Unable to get DNS record ID")
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

def printVersion():
    print("Installed Version: "+metadata["version"]+" (Build Number: "+metadata["buildnum"]+")\nFor more detailed information please check out on the github repo page\n\nhttps://github.com/chrischan514/Cloudflare-API/")

methods = {"dnsrec": dnsrec, "nameonly": showDomainName, "ddns": ddns, "id": IDonly}
start = methods[args.meth]



if args.debug is True:
    print(os.path.dirname(os.path.realpath(__file__)))
if scriptmode == False:
    if hashlib.sha256(open(path + '/cf.py', "rb").read()).hexdigest() != requests.get("https://raw.githubusercontent.com/chrischan514/Cloudflare-API/main/sha256.json",headers={'Cache-Control': 'no-cache'}).json()[buildnum]:
        print("Failed integrity check, a new copy will be downloaded")
        metadata["buildnum"] = "0"
        checkUpdate()
    checkInternetConnection()
    if args.disableautoupdate is False:
            checkUpdate()
    if args.printversion is True:
        printVersion()
    else:
        start()
