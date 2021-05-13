# configIOC.py
A script that makes it easy to prune unneeded files from an IOC created with [mkioc](https://github.com/BCDA-APS/mkioc)

## Usage
```
$ ./configIOC.py -h
usage: configIOC.py [-h] [-v] [-q] {linux,vxWorks,windows}

positional arguments:
  {linux,vxWorks,windows}

  optional arguments:
    -h, --help            show this help message and exit
    -v, --verbose         Print commands that are executed
    -q, --quiet           Pass the quiet flag to git commands
```
The command needs to be run from the top-level directory of an IOC.  It is assumed that the name of the top-level directory is the IOC's name.  The script will warn you if the pwd is not an IOC dir.

NOTE: Only run the script once per IOC; the script doesn't protect against being run multiple times on the same IOC directory.

## Supported platforms

This script was tested on:
* RHEL7

