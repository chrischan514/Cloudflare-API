Quick Tools using CloudFlare's API
# Immediate Use
If you do not need a separate file to contain all your frequently used (token and zone id), instead you will enter each time on your own, you can just download the "start.command" and run.
# System requirements
I'm using macOS, dunno about Windows.
# Coming Features
Maybe a DDNS applet
# Usage
```bash
cf.py (-m method) (--zone ZoneID) (--token Token) (-s Subdomain (for DDNS update)) (--type A/AAAA)
```
## Methods
```
dnsrec    list json response from CF  
nameonly  return domain name only
ddns      update record as ddns
IDonly    show record ID (first record)
