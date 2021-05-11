#!/usr/bin/env python3
#
# A script to configure an xxx IOC in the style of makeIOC.sh
#

import os
import sys
import argparse


def iocDirCheck(pwd, iocName):
    iocDir = True
    
    shouldExist = ('configure', '{}App'.format(iocName),
        'iocBoot', 'Makefile')
    
    for thing in shouldExist:
        path = "{}/{}".format(pwd, thing)
        if not os.path.exists(thing):
            iocDir = False
    
    return iocDir

def remove_file(path):
    if os.path.isfile(path):
        #!os.system("git rm -f {}".format(path))
        print("git rm -f {}".format(path))
    else:
        print("{} is not a file".format(path))

def remove_dir(path, save=None):
    deleteEntireDir = True
    
    if save != None:
        for fp in save:
            if path == os.path.dirname(fp):    
                deleteEntireDir = False
                break
    
    if deleteEntireDir:
        if os.path.isdir(path):
            #!os.system("git rm -rf {}".format(path))
            print("git rm -rf {}".format(path))
        else:
            print("{} is not a dir".format(path))
    else:
        for fn in os.listdir(path):
            fp = "{}/{}".format(path, fn)
            if fp in save:
                print("saving {}".format(fp))
            else:
                remove_file(fp)

def createMotorIocsh(iocName):
    #
    newDir = 'iocBoot/ioc{}/iocsh'.format(iocName)
    if not os.path.exists(newDir):
        os.mkdir(newDir)
    
    if os.path.exists('iocBoot/ioc{}/examples/motors.iocsh'.format(iocName)):
        #
        os.system('grep -v "traj\|pseudo" iocBoot/ioc{}/examples/motors.iocsh | sed -e "s/^dbLoad/#dbLoad/g" > {}/motors.iocsh'.format(iocName, newDir, iocName))
        #!os.system('git add {}'.format(newDir))
        print('git add {}'.format(newDir))

    # This should eventually move to after deleteCommonFiles()
    for fn in os.listdir("iocBoot/ioc{}".format(iocName)):
        if 'st.cmd' in fn:
            print(fn)

def deleteCommonFiles(iocName):
    filesToDelete = ['LICENSE', 'README', 'README.md', 'start_putrecorder',
        'iocBoot/accessSecurity.acf',
        'iocBoot/ioc{}/README'.format(iocName),
        'iocBoot/ioc{}/SGMenu.req'.format(iocName),
        'iocBoot/ioc{}/bootParms'.format(iocName),
        'iocBoot/ioc{}/softioc/in-screen.sh'.format(iocName),
        'iocBoot/ioc{}/softioc/run'.format(iocName),
        'iocBoot/ioc{}/st.cmd.Cygwin'.format(iocName),
        '{}App/Db/Security_Control.db'.format(iocName),
        '{}App/Db/Security_Control_settings.req'.format(iocName),
        '{}App/Db/streamExample.db'.format(iocName),
    ]
    
    dirsToDelete = ['documentation', 
        'iocBoot/ioc{}/examples'.format(iocName), 
        'iocBoot/ioc{}/substitutions'.format(iocName),
        '{}App/op/bob/autoconvert'.format(iocName),
        '{}App/op/edl/autoconvert'.format(iocName),
        '{}App/op/opi'.format(iocName),
        '{}App/op/python'.format(iocName),
        '{}App/op/burt'.format(iocName),
        ]
    
    filesToKeep = ['iocBoot/ioc{}/substitutions/motor.substitutions'.format(iocName),
        'iocBoot/ioc{}/substitutions/motorSim.substitutions'.format(iocName),
        'iocBoot/ioc{}/substitutions/softMotor.substitutions'.format(iocName),
    
    ]
    
    for fp in filesToDelete:
        remove_file(fp)
    
    for dp in dirsToDelete:
        remove_dir(dp, filesToKeep)

def patchCommonIocsh(iocName):
    #
    lineSubstitutions = {
        'iocshLoad("$(AUTOSAVE)/iocsh/autosave_settings.iocsh", "PREFIX=$(PREFIX), SAVE_PATH=$(TOP)/iocBoot/$(IOC)")\n' : 'iocshLoad("$(AUTOSAVE)/iocsh/autosave_settings.iocsh", "PREFIX=$(PREFIX), SAVE_PATH=$(TOP)/iocBoot/$(IOC), NUM_SEQ=12, SEQ_PERIOD=43200")\n',
        'set_requestfile_path("$(TOP)/db")\n' : 'set_requestfile_path("$(TOP)/db")\nset_requestfile_path("$(TOP)/xxxApp/Db")\n',
        'dbLoadRecords("$(ALIVE)/aliveApp/Db/aliveMSGCalc.db", "P=$(PREFIX)")\n' : 'dbLoadRecords("$(ALIVE)/aliveApp/Db/aliveMSGCalc.db", "P=$(PREFIX)")\n\n# Miscellaneous PV\'s, such as burtResult\ndbLoadRecords("$(STD)/stdApp/Db/misc.db","P=$(PREFIX)")\n\n'
    }
    linesToSub = lineSubstitutions.keys()
    
    with open('iocBoot/ioc{}/common.iocsh'.format(iocName), 'r') as fh:
        contents = fh.readlines()
        print(contents)
    
    # TODO: overwrite the original file
    with open('iocBoot/ioc{}/common.iocsh.new'.format(iocName), 'w') as fh:
        for line in contents:
            if line in linesToSub:
                fh.write(lineSubstitutions[line])
            else:
                fh.write(line)

def configureLinux(iocName):
    #
    filesToDelete = [ 'iocBoot/nfsCommands', 
                      'iocBoot/ioc{}/st.cmd.Win32'.format(iocName), 
                      'iocBoot/ioc{}/st.cmd.Win64'.format(iocName),
                      'iocBoot/ioc{}/st.cmd.vxWorks'.format(iocName),
        ]

    #
    for fp in filesToDelete:
        remove_file(fp)

    if os.path.exists('iocBoot/ioc{}/Makefile'.format(iocName)):
        #
        os.system("grep -v 'win\|vxWorks\|cdCommands\|dllPath' iocBoot/ioc{}/Makefile | sed -e 's/^ARCH = linux-x86_64/ARCH = linux-x86_64\\\n#ARCH = linux-x86_64-debug/g' > iocBoot/ioc{}/Makefile.new".format(iocName, iocName))
        #!os.system('git add iocBoot/ioc{}/Makefile'.format(iocName))
        print('git add iocBoot/ioc{}/Makefile'.format(iocName))

    #
    if os.path.exists('configure/CONFIG_SITE'):
        #
        os.system("sed -e 's/^#CROSS_COMPILER_TARGET_ARCHS = vxWorks-68040/CROSS_COMPILER_TARGET_ARCHS = /g' configure/CONFIG_SITE > configure/CONFIG_SITE.new")
        #!os.system('git add configure/CONFIG_SITE')
        print('git add configure/CONFIG_SITE')

def patchStCmd(iocName):
    #
    pass

def main(options):
    print(options)
    
    cwd = os.getcwd()
    
    # Assume the following:
    #  1. The name of the IOC's top-level directory is the name of the IOC
    iocName = os.path.basename(cwd)
    
    if iocDirCheck(cwd, iocName):
        #
        createMotorIocsh(iocName)
        
        #
        deleteCommonFiles(iocName)
        
        #
        patchCommonIocsh(iocName)
        
        #
        if (options.os == 'linux'):
            configureLinux(iocName)
        elif (options.os == 'windows'):
            configureWindows(iocName)
        elif (options.os == 'vxWorks'):
            configureVxWorks(iocName)
    else:
        print("{} is not an IOC dir".format(cwd))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser("configIOC.py")
    
    parser.add_argument('os', choices=('linux', 'vxWorks', 'windows'))
    
    options = parser.parse_args(sys.argv[1:])
    
    main(options)
