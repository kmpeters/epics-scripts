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
  response = urllib2.urlopen(request).read().decode("utf-8")
  parsed = json.loads(response)
  return parsed

def pPrint(parsed):
  print(json.dumps(parsed, indent=2))


def print_release_info(release_dict, repo, save=False):
  version = release_dict["name"].replace(".", "-")
  #!tarball_url = release_dict["tarball_url"]
  tarball_url = release_dict["zipball_url"]
  date, time = release_dict["published_at"].split("T")
  #!filename = "{0}-{1}.tar.gz".format(repo, version)
  filename = "{0}-{1}.zip".format(repo, version)
  print("{0}\t{1}\t{2}\t{3}\t{4}".format(date, time, version, tarball_url, filename))
  # Download the release
  #!urllib2.urlretrieve(tarball_url, filename)
  

def getReleaseInfo(releaseDict):
  version = releaseDict["name"]
  date = releaseDict["published_at"]
  rType = "Release"
  return (date, version, rType)

def getTagInfo(tagDict, commitsURL, headers):
  version = tagDict["name"]

  sha = tagDict["commit"]["sha"]
  curl = "{0}/{1}".format(commitsURL, sha)
  commitDict = doRequest(curl, headers)
  #!pPrint(commitDict)
  date = commitDict["commit"]["committer"]["date"]

  rType = "Tag"

  return (date, version, rType)

def getGithubToken():
  if "GITHUB_TOKEN" in os.environ:
    token = os.environ["GITHUB_TOKEN"]
  else:
    token = None
  return token

def download_releases(user=None, repo=None, tag=None, latest=False, token=None, quiet=False):
  #
  
  headers = {"Accept": "application/vnd.github.v3+json"}
  
  token = getGithubToken()
  if token != None:
    # Use authentication to raise rate limit from 60 req/hr to 5000 req/hr
    headers["Authorization"] = "token {0}".format(token)
  
  # user = user or "kmpeters"
  if not user:
    #!user = "kmpeters"
    user = "epics-modules"
  if not repo:
    #!repo = "ADPhotron"
    #!repo = "measComp"
    #!repo = "alive"
    repo = "motor"
  
  api_url = "https://api.github.com/repos"
  repo_url = "{0}/{1}/{2}".format(api_url, user, repo)
  releases_url = "{0}/releases".format(repo_url)
  tags_url = "{0}/tags".format(repo_url)
  commits_url = "{0}/commits".format(repo_url)
  download_url = "https://github.com/{0}/{1}/archive".format(user, repo)
  
  print(releases_url)
  
  releasesAndTags = []
  
  releases = doRequest(releases_url, headers)
  #!pPrint(releases)
  for release in releases:
    #!print_release_info(release, repo, save=False)
    
    # info = (date, version, rType)
    info = getReleaseInfo(release)
    releasesAndTags.append(info)
  
  tags = doRequest(tags_url, headers)
  #!pPrint(tags)
  for tag in tags:
    info = getTagInfo(tag, commits_url, headers)
    releasesAndTags.append(info)

  sortedReleasesAndTags = sorted(releasesAndTags, reverse=True)
  
  for date, version, rType in sortedReleasesAndTags:
    # Hard-code a tag width for now.  
    print("{0}\t{1:12}\t[{2}]".format(date, version, rType))

def main(options):
  #
  user = options.github_user
  repo = options.github_repo
  
  version = options.version
  latest = options.latest
  interactive = options.interactive
  
  listVersions = options.list
  ignoreTags = options.ignore_tags
  ignoreReleases = options.ignore_releases
  
  if ignoreTags == True and ignoreRelease == True:
    # The user doesn't want to see anything
    print("Doing nothing (ignoring both releases and tags")
    sys.exit(0)
    
  if interactive == True:
    # Listing the versions is required for interactive mode
    listVersions = True
  
  # Only download one version (version > interactive > latest)
  if version != None:
    # Download the version that the user specified on the command line
    latest = False
    interactive = False
  if interactive == True:
    # Ask the user which version they want
    latest = False
  # lastest only works if interactive and version are not specified
    
  

if __name__ == '__main__':
  parser = argparse.ArgumentParser("getReleases.py")
  
  parser.add_argument('-l', action="store_true", dest='list', default=False)
  parser.add_argument('--ignore-tags', action="store_true", default=False)
  parser.add_argument('--ignore-releases', action="store_true", default=False)
  parser.add_argument('--latest', action="store_true", default=False)
  parser.add_argument('-i', action="store_true", dest='interactive', default=False)
  parser.add_argument('github_user', action="store", default=None)
  parser.add_argument('github_repo', action="store", default=None)
  parser.add_argument('version', nargs='?', default=None)
  
  options = parser.parse_args(sys.argv[1:])
  print(options)
  
  main(options)
  
  #!download_releases()
