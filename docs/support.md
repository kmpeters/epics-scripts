# support.sh
A script that makes it easy to clone (and maintain) the EPICS modules that are required/useful for motor development and testing.

## Justifcation

### Need

The [assemble_synApps.sh](https://github.com/EPICS-synApps/support/blob/master/assemble_synApps.sh) script is the right tool for deploying a static collection of EPICS modules that are known to work well together.

There is often a need to deploy the master branches of a subset of synApps modules, and minimize the effort required to keep them up-to-date.  ``support.sh`` is one tool for accomplishing this.

### Location

The script to clone EPICS modules shouldn't reside in one of the EPICS modules.  You should be able to delete the support dir and not have to re-download the script.

## Usage
```
$ ./support.sh 
Usage: support.sh <clone|fetch|status|stat|rebase|auto-rebase>
```
Note: this script needs to be called from the support directory where the EPICS modules reside (or will reside).

### clone
The **clone** argument will clone EPICS modules in the current working directory.

The ``maste`` branch of each EPICS module's github repo will be cloned into the current working directory.  If ``wget`` is on the PATH, the script will also download ``seq-2.2.7``.

### fetch
The **fetch** argument will run ``git fetch`` in each of the directories of the EPICS modules that were cloned from github.  This needs to be run before the **status** output will be useful.

### status
The **status** argument will run ``git status`` in each of the directories of the EPICS modules that were cloned from github.  This will show local modifications to files.  If the last fetch retrieved changes from github, status will tell you how far your clone is behind origin (if you're on the master branch).

### stat
The **stat** argument will run ``git status`` in each of the directories of the EPICS modules that were cloned from github, however, it greps the output for fast-forward messages and doesn't show you any of the local modifications to files.  Running **stat** after **fetch** will make it easier to see how far from the bleeding edge you are.

### rebase
The **rebase** argument will run ``git status`` in each of the directories of the EPICS modules that were cloned from github and if it sees that a rebase is necessary, it will spawn a new bash shell with a custom prompt so that you can rebase manually.  

Manual rebasing is necessary when local changes break automatic rebasing. "make release" will modify the RELEASE file of almost every EPICS module, which requires a "git stash" before rebasing and a "git stash apply" after rebasing.  Merge conflicts occur when "git stash apply" reapplies changes to a file that was updated during the rebase. 

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
In the ``???`` scenario a judgement call needs to be made.  The git-stash approach can be used, which may result in merge conflicts.  The risk of merge conflicts can be reduced by renaming local-modified files, checking out clean versions, rebasing, then manually copying the locally-modified files back.

### auto-rebase
The **auto-rebase** command will run ``git stash && git rebase origin/master && git stash apply`` in each of the directories fo the EPICS modules that were cloned from github.  It should only be used when ``status`` reports only changes that can be fast-fowarded AND the chance of merge conflicts is minimal.

## Supported platforms
* RHEL6
* RHEL7
* OS X 10.11.6
* Windows 7 64-bit (using git bash)
