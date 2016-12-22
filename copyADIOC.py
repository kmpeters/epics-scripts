#!/APSshare/anaconda3/x86_64/bin/python

import argparse
import os
#import os.path
import sys
import re

fullIgnorePattern = re.compile("bin|dbd|db|envPaths")
partialIgnorePattern = re.compile("O\.")

def ignoreCheck(name):
  if fullIgnorePattern.fullmatch(name):
    ignore = True
  elif partialIgnorePattern.match(name):
    ignore = True
  else:
    ignore = False
  return ignore

def traverse(path):
  for item in os.scandir(path):
    if item.is_dir():
      if ignoreCheck(item.name):
        continue
      else:
        #!print(item.name)
        print(item.path)
        traverse(item.path)
    else:
      if ignoreCheck(item.name):
        continue
      else:
        #!print(item.name)
        print(item.path)

parser = argparse.ArgumentParser(description='N/A')

parser.add_argument("source", action="store")
parser.add_argument("destination", action="store")

results = parser.parse_args()
#!print(results)

# Source directory must exist
if not os.path.isdir(results.source):
  print("Error:", os.path.abspath(results.source), "does not exist!")
  sys.exit(-1)

# Destination directory may not exist
if not os.path.isdir(results.destination):
  head, tail = os.path.split(results.destination)
  if not os.path.isdir(head):
    print("Error:", os.path.abspath(head), "does not exist!")
    sys.exit(-1)
  else:
    print(os.path.abspath(results.destination), "does not exist and will be created.")
    #!print(results.destination, "does not exist and will be created.")
    os.mkdir(results.destination)

print()
print("source      = ", results.source)
print("destination = ", results.destination)
print("cwd         = ", os.getcwd())
print()

# [fozzi ~/development/epics-scripts]$ ./copyADIOC.py =1/andor3IOC ioc/42idAND
# Namespace(destination='ioc/42idAND', source='/APSshare/epics/synApps_5_8/support/areaDetector-2-4/ADAndor3/iocs/andor3IOC')

traverse(results.source)

