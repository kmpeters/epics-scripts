#!/APSshare/anaconda3/x86_64/bin/python
#
#  /APSshare/anaconda3/x86_64/bin/python -> python3.5*
#

import sys
import argparse
import os
import json
import urllib.request as urllib2

def doRequest(url, headers={"Accept": "application/vnd.github.v3+json"}):
  request = urllib2.Request(url, headers=headers)
  try:
    response = urllib2.urlopen(request).read().decode("utf-8")
    parsed = json.loads(response)
  except:
    parsed = {}
  return parsed

def pPrint(parsed):
  print(json.dumps(parsed, indent=2))

def getGithubToken():
  if "GITHUB_TOKEN" in os.environ:
    token = os.environ["GITHUB_TOKEN"]
  else:
    token = None
  return token

def isVersionNum(release):
  # Assume any release name that has 1-4 '.' or '-' in it and NO spaces is a valid version number
  return ((release.count('-') > 0 and release.count('-') < 5) or (release.count('.') > 0 and release.count('.'))) and (release.count(' ') == 0)

def get_latest_release(user=None, repo=None, tag=None, latest=False, token=None, quiet=False):
  #
  
  headers = {"Accept": "application/vnd.github.v3+json"}
  
  token = getGithubToken()
  if token != None:
    # Use authentication to raise rate limit from 60 req/hr to 5000 req/hr
    headers["Authorization"] = "token {0}".format(token)
  
  api_url = "https://api.github.com/repos"
  repo_url = "{0}/{1}/{2}".format(api_url, user, repo)
  releases_url = "{0}/releases".format(repo_url)
  tags_url = "{0}/tags".format(repo_url)
  
  print(releases_url)
  
  latest_release = None
  
  releases = doRequest(releases_url, headers)
  pPrint(releases)
  for release in releases:
    #!print_release_info(release, repo, save=False)
    
    # Assume the first release that starts with 'R' is the latest release 
    if isVersionNum(release["name"]):
      latest_release = release["name"]
      break
  
  if latest_release == None:
    tags = doRequest(tags_url, headers)
    #pPrint(tags)
    
    for tag in tags:
      # Assume the first tag that starts with 'R' is the latest release
      if isVersionNum(tag["name"]):
        latest_release = tag["name"]
        break

  print(latest_release)

def main(options):
  # Assume the user will always specify valid user and repo values
  user = options.github_user
  repo = options.github_repo
  
  # Do the stuff
  get_latest_release(user=user, repo=repo, quiet=False)

if __name__ == '__main__':
  parser = argparse.ArgumentParser("getReleases.py")
  
  parser.add_argument('github_user', action="store", default=None)
  parser.add_argument('github_repo', action="store", default=None)
  
  options = parser.parse_args(sys.argv[1:])
  #print(options)
  
  main(options)
 
