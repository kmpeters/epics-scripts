# makeIOC.sh
A script that makes it easy to quickly generate a clean vxWorks or Linux IOC.

## Usage
```
$ ./makeIOC.sh 
Usage: makeIOC.sh <vxWorks|Linux> <ioc_name>

```
Running the command will create a directory named <ioc_name> based on [Kevin's fork of xxx](https://github.com/kmpeters/xxx) in your current working directory. The script will warn you and do nothing if the <ioc_name> directory already exists.

## Good things to know

* IOCs based on the script build all of the support into the IOC that xxx does; adding support that has been removed should only require copying some startup files (recompiling the IOC shouldn't be necessary)
* The IOC that created is under local git control by default
  * The "deployed" branch contains the <ioc_name> IOC
  * The "vxWorks" or "Linux" branch contains the pruned xxx directory on which the <ioc_name> is based
  * The "master" branch tracks [epics-modules/xxx](https://github.com/epics-modules/xxx) and contains many of the files that have been deleted
* If another revision control program will be used, the .git* files & directories in the <ioc_name> dir should be deleted

## Supported platforms

This script was tested on:
* RHEL6
* RHEL7
