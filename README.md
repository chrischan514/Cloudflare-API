# Quick Tools using CloudFlare's API

# Immediate Use
macOS only: If you do not need a separate file to contain all your frequently used (token and zone id), instead you will enter each time on your own, you can just download the "start.command" and run.
# System requirements
I'm using macOS, dunno about Windows.  
Python is needed.
## Tested Setup
macOS 11.2 (20D64), Python 3.9.0
## Modules Required
- `requests`

To install, type:  
```bash
pip3 install requests
```
## FreeNAS/ TrueNAS environment
FreeNAS/ TrueNAS host's python has already installed `request` module, no extra steps have to be done. Can be executed in host cron job as ddns service.

Clone the repository in order to use.
```
git clone https://github.com/chrischan514/Cloudflare-API
```

# Features
## DDNS
No record ID input is needed, the ID will be automatically fetched for you.  
If no existing record is found, a new record will be created.  
If no record type specified, `A` record will be chosen by default.

# Usage
```bash
python3 cf.py -h
```
```
usage: cf.py [-h] [-m {dnsrec,nameonly,ddns,id}] [-z Zone ID] [-k Token] [-s Subdomain] [-t Record TYPE] [-v] [--without-proxy] [--provider {1,2,3,4,5,6}]

Asking CloudFlare's API to help you. For more details, please check https://github.com/chrischan514/Cloudflare-API/blob/main/README.md

optional arguments:
  -h, --help            show this help message and exit
  -m {dnsrec,nameonly,ddns,id}
                        specifying the method you wanna use. e.g. ddns update, check id only, etc.
  -z Zone ID, --zone Zone ID
                        input zone id
  -k Token, --token Token
                        input token
  -s Subdomain, --subdomain Subdomain
                        input subdomain
  -t Record TYPE, --type Record TYPE
                        type of record (A/AAAA/both)
  -v, --verbose         verbose mode
  --without-proxy       disable CF's proxy while creating record
  --provider {1,2,3,4,5,6}
                        try choosing another provider set if it fails

```

## Methods
```
dnsrec    list json response from CF  
nameonly  return domain name only
ddns      update record as ddns
id        show record ID (first record)
```

For ddns, if record type is not specified, then the default will be updating both IPv4 and IPv6 record (if available).

## Configuraton File
This script can access to a preset of parameters in order to reduce the manual input while using the script.
The configuration file should be named ```config.py```, can be created by ```cp config_sample.py config.py``` on UNIX systems.
The configuration file looks like this, all the parameters are optional to define in the file.
```
zone = "" #Zone ID
token = "" #API Token (requires DNS modification permission)
subdomain = "" #Subdomain preset for updating (without the domain name, only the subdomain part)
type = "" #Subdomain preset for updating (without the domain name, only the subdomain part)
```

## Provider Sets
| Set |                                                |
| --- | ---------------------------------------------- |
| 1   | ident.me (No HTTPS supported, not recommended) |
| 2   | ipify.org (default)                            |
| 3   | my-ip.io                                       |
| 4   | seeip.org                                      |
| 5   | whatismyipaddress.com                          |
| 6   | ip.sb                                          |

## Remarks
For your convenience, you can store the Zone ID and token into config.py according to config_sample.py  
DO NOT ADD your domain name in the subdomain field

# Example
Cron Job in FreeNAS Jail
```bash
iocage exec jail "python3 cf.py --zone ZONEID --token TOKEN -m ddns -s nas --type AAAA"
```

# New Functions Suggestions/ Errors Reporting
Raising issues are welcomed
