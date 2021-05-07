#!/usr/bin/env python3
#
# A script to configure an xxx IOC in the style of makeIOC.sh
#

import os
import sys
import argparse


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

def main(options):
    print(options)
    
    pwd = os.getcwd()
    
    # Assume the following:
    #  1. The name of the IOC's top-level directory is the name of the IOC
    iocName = os.path.basename(pwd)
    
    deleteCommonFiles(iocName)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser("configIOC.py")
    
    parser.add_argument('os', choices=('linux', 'vxWorks', 'windows'))
    
    options = parser.parse_args(sys.argv[1:])
    
    main(options)
