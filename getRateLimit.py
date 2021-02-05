#!/APSshare/anaconda3/x86_64/bin/python
#
#  /APSshare/anaconda3/x86_64/bin/python -> python3.5*
#

import os
import json
import urllib.request as urllib2
from time import ctime

def doRequest(url, headers={"Accept": "application/vnd.github.v3+json"}):
  request = urllib2.Request(url, headers=headers)
  response = urllib2.urlopen(request).read().decode("utf-8")
  parsed = json.loads(response)
  return parsed

def pPrint(parsed):
  print(json.dumps(parsed, indent=2))

def getGithubToken():
  if "GITHUB_TOKEN" in os.environ:
    token = os.environ["GITHUB_TOKEN"]
  else:
    token = None
  return token

def main():
  #
  
  headers = {"Accept": "application/vnd.github.v3+json"}
  
  token = getGithubToken()
  if token != None:
    # Use authentication to raise rate limit from 60 req/hr to 5000 req/hr
    headers["Authorization"] = "token {0}".format(token)
  
  api_url = "https://api.github.com"
  rateLimit_url = "{0}/rate_limit".format(api_url)
  
  #!print(rateLimit_url)
  
  rateLimit = doRequest(rateLimit_url, headers)
  #!pPrint(rateLimit)
  remaining = rateLimit["rate"]["remaining"]
  limit = rateLimit["rate"]["limit"]
  reset = rateLimit["rate"]["reset"]
  resetStr = ctime(int(reset))
  print("Used {0} of {1} queries".format(remaining, limit))
  print("Current: {0}".format(ctime()))
  print("Reset @: {0}".format(resetStr))
  
main()
