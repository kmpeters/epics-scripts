# synApps.sh
A script that makes it easy to clone (and maintain) the synApps modules from their git repos.

## Justifcation

### Need

The ([synApps/support](https://github.com/EPICS-synApps/support) dir has historically contained scripts to checkout and update synApps modules from subversion.  It has clone scripts for github, but there aren't any scripts to keep the clones up-to-date. 

### Location

The script to clone synApps modules shouldn't reside in one of the synApps modules.  You should be able to delete the synApps dir and not have to re-download the script.

## Usage
```
$ ./synApps.sh 
Usage: synApps.sh <clone|fetch|status|stat|rebase>
```
Note: this script needs to be called from the parent of the synApps directory.

### clone
The **clone** argument will create a directory named "synApps" in the current working directory.  This directory name is hard-coded at the start of [synApps.sh](synApps.sh) and is easy to change.

The "master" branch of each synApps module's github repo will be checked out into the support directory.  If "wget" is on the PATH, the script will also download seq-2.2.3 and allenBradley-2.3.

### fetch
The **fetch** argument will run "git fetch" in each of the directories of the synApps modules that were cloned from github.  This needs to be run before the **status** argument will be useful.

### status
The **status** argument will run "git status" in each of the directories of the synApps modules that were cloned from github.  This will show local modifications to files.  If the last fetch retrieved changes from github, status will tell you how far your clone is behind origin.

### stat
The **stat** argument will run "git status" in each of the directories of the synApps modules that were cloned from github, however, it greps the output for fast-forward messages and doesn't show you any of the local modifications to files.  Running **stat** after **fetch** will make it easier to see how far from the bleeding edge you are.

### rebase
The **rebase** argument will run "git status" in each of the directories of the synApps modules that were cloned from github and if it sees that a rebase is necessary, it will spawn a new bash shell with a custom prompt so that you can rebase manually.  

Manual rebasing is necessary because there will frequently be local changes that break automatic rebasing. "make release" will modify the RELEASE file of almost every synApps module, which requires a "git stash" before rebasing and a "git stash apply" after rebasing.  Merge conflicts occur when "git stash apply" reapplies changes to a file that was updated during the rebase. 

A typical rebase decision-making process looks like this:
```
IF "git status" shows no changes
THEN "git rebase"
ELIF "git status" shows minimal changes (usually just RELEASE)
THEN "git stash", "git rebase, "git stash apply"
ELSE "git status" shows non-trivial changes
THEN ???
"exit" # once the rebase is complete
```
In the ??? scenario a judgement call needs to be made.  The git-stash approach can be used, which may result in merge conflicts.  The risk of merge conflicts can be lessened by renaming modified files, checking out clean versions, rebasing, then manually copying the renamed files back.

## Supported platforms
* RHEL6
* RHEL7
* OS X 10.11.6
* Windows 7 64-bit (using git bash)
