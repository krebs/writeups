#!/usr/bin/pyhon
import requests

s = requests.session()
ret = s.get("http://41.231.53.44:9393/",stream=True)
# avoid loading the whole file
arr=ret.raw.read()[4880:4912]

pwd=""
for c in arr:
    if c != 0:
        pwd+=(chr(c^1))

i=s.get('http://41.231.53.44:9393/check.php?p=%s'%pwd)
print(i.content)
