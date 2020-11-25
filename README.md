Quick Tools using CloudFlare's API
# Immediate Use
If you do not need a separate file to contain all your frequently used (token and zone id), instead you will enter each time on your own, you can just download the "start.command" and run.
# System requirements
I'm using macOS, dunno about Windows.
# Coming Features
Maybe a DDNS applet
# Usage
```bash
python3 cf.py [-h] [-m METH] [--zone ZONE] [--token TOKEN] [-s SUBDOMAIN] [--type TYPE] [-v] [--without-proxy]

optional arguments:
  -h, --help       show this help message and exit
  -m METH          specifying the method you wanna use. e.g. ddns update, check id only, etc.
  --zone ZONE      input zone id
  --token TOKEN    input token
  -s SUBDOMAIN     input subdomain
  --type TYPE      type of record (A/AAAA)
  -v               verbose mode
  --without-proxy  disable CF\'s proxy while creating record
```

## Methods
```
dnsrec    list json response from CF  
nameonly  return domain name only
ddns      update record as ddns
id        show record ID (first record)
```

## Remarks
For your convenience, you can store the Zone ID and token into config.py according to config_sample.py  
DO NOT ADD your domain name in the subdomain field
