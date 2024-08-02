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
    global quiet
    if os.path.isfile(path):
        vprint("> git rm -f {}".format(path))
        if quiet:
            os.system("git rm -qf {}".format(path))
        else:
            os.system("git rm -f {}".format(path))
    else:
        vprint("{} is not a file".format(path))

def remove_files(fileList):
    for fp in fileList:
        remove_file(fp)

def remove_dir(path, saveList=None):
    global quiet
    deleteEntireDir = True
    
    if saveList != None:
        for fp in saveList:
            if path == os.path.dirname(fp):    
                deleteEntireDir = False
                break
    
    if deleteEntireDir:
        if os.path.isdir(path):
            vprint("> git rm -rf {}".format(path))
            if quiet:
                os.system("git rm -qrf {}".format(path))
            else:
                os.system("git rm -rf {}".format(path))
        else:
            vprint("{} is not a dir".format(path))
    else:
        for fn in os.listdir(path):
            fp = "{}/{}".format(path, fn)
            if fp in saveList:
                vprint("saving {}".format(fp))
            else:
                remove_file(fp)

def remove_dirs(dirList, saveList=None):
    for dp in dirList:
        remove_dir(dp, saveList)

def make_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def modifyFile(inFileName, outFileName=None, patternsToExclude=None, lineSubstitutions=None):
    if os.path.exists(inFileName):
        if outFileName == None:
            # Overwrite the input file if no output file is specified
            outFileName = inFileName
            # Use a .new extension for testing
            #outFileName = "{}.new".format(inFileName)

        # Read the contents of the file
        with open(inFileName, 'r') as fh:
            contents = fh.readlines()

        # Determine which lines need to be replaced
        if lineSubstitutions == None:
            linesToReplace = None
        else:
            linesToReplace = lineSubstitutions.keys()
        
        # Write the modified contents to the output file
        with open(outFileName, 'w') as fh:
            for line in contents:
                if linesToReplace != None and line in linesToReplace:
                    if type(lineSubstitutions[line]) == list:
                        fh.write("".join(lineSubstitutions[line]))
                    else:
                        fh.write(lineSubstitutions[line])
                else:
                    ignore = False
                    if patternsToExclude != None:
                        for pattern in patternsToExclude:
                            if pattern in line:
                                ignore = True
                                break
                    if not ignore:
                        fh.write(line)

        # Stage the modified file to be committed
        vprint('> git add {}'.format(outFileName))
        os.system('git add {}'.format(outFileName))

    else:
        vprint("{} does not exist".format(inFileName))

def createMotorIocsh(iocName):
    #
    newDir = 'iocBoot/ioc{}/iocsh'.format(iocName)
    make_dir(newDir)
    
    inFileName = 'iocBoot/ioc{}/examples/motors.iocsh'.format(iocName)
    outFileName = '{}/motors.iocsh'.format(newDir)
    patternsToExclude = ['traj', 'pseudo']
    lineSubstitutions = {'dbLoadTemplate("substitutions/motor.substitutions", "P=$(PREFIX)")\n': '#dbLoadTemplate("substitutions/motor.substitutions", "P=$(PREFIX)")\n'}
    modifyFile(inFileName, outFileName, patternsToExclude, lineSubstitutions)
    
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
    
    remove_files(filesToDelete)
    remove_dirs(dirsToDelete, filesToKeep)

def patchCommonIocsh(iocName):
    #
    inFileName = 'iocBoot/ioc{}/common.iocsh'.format(iocName)
    lineSubstitutions = {
        'iocshLoad("$(AUTOSAVE)/iocsh/autosave_settings.iocsh", "PREFIX=$(PREFIX), SAVE_PATH=$(TOP)/iocBoot/$(IOC)")\n' : 'iocshLoad("$(AUTOSAVE)/iocsh/autosave_settings.iocsh", "PREFIX=$(PREFIX), SAVE_PATH=$(TOP)/iocBoot/$(IOC), NUM_SEQ=12, SEQ_PERIOD=43200")\n',
        'set_requestfile_path("$(TOP)/db")\n' : [ 'set_requestfile_path("$(TOP)/db")\n', 'set_requestfile_path("$(TOP)/{}App/Db")\n'.format(iocName)],
        'dbLoadRecords("$(ALIVE)/aliveApp/Db/aliveMSGCalc.db", "P=$(PREFIX)")\n' : ['dbLoadRecords("$(ALIVE)/aliveApp/Db/aliveMSGCalc.db", "P=$(PREFIX)")\n',
                                                                                    '\n',
                                                                                    '# Miscellaneous PV\'s, such as burtResult\n',
                                                                                    'dbLoadRecords("$(STD)/stdApp/Db/misc.db","P=$(PREFIX)")\n',
                                                                                    '\n']
    }
    
    modifyFile(inFileName, lineSubstitutions=lineSubstitutions)
    
def configureLinux(iocName):
    #
    filesToDelete = [ 'iocBoot/nfsCommands', 
                      'iocBoot/ioc{}/cdCommands.vxWorks-ppc32'.format(iocName),
                      'iocBoot/ioc{}/cdCommands.vxWorks-ppc32sf'.format(iocName),
                      'iocBoot/ioc{}/st.cmd.Win32'.format(iocName), 
                      'iocBoot/ioc{}/st.cmd.Win64'.format(iocName),
                      'iocBoot/ioc{}/st.cmd.vxWorks'.format(iocName),
                      'iocBoot/ioc{}/st.cmd.vxWorks-local'.format(iocName),
        ]

    remove_files(filesToDelete)

    inFileName = 'iocBoot/ioc{}/Makefile'.format(iocName)
    patternsToExclude = ['win', 'vxWorks']
    lineSubstitutions = {'ARCH = linux-x86_64\n' : ['ARCH = linux-x86_64\n', '#ARCH = linux-x86_64-debug\n'],
                         'TARGETS = cdCommands envPaths dllPath.bat modules.lua\n' : 'TARGETS = envPaths modules.lua\n',
    }
    modifyFile(inFileName, patternsToExclude=patternsToExclude, lineSubstitutions=lineSubstitutions)

    inFileName = 'configure/CONFIG_SITE'
    lineSubstitutions = {'#CROSS_COMPILER_TARGET_ARCHS = vxWorks-68040\n' : 'CROSS_COMPILER_TARGET_ARCHS = \n'}
    modifyFile(inFileName, lineSubstitutions=lineSubstitutions)

def configureVxWorks(iocName):
    #
    filesToDelete = [ 'iocBoot/ioc{}/st.cmd.Win32'.format(iocName), 
                      'iocBoot/ioc{}/st.cmd.Win64'.format(iocName),
                      'iocBoot/ioc{}/st.cmd.Linux'.format(iocName),
        ]

    dirsToDelete = ['iocBoot/ioc{}/softioc'.format(iocName), ]

    #
    remove_files(filesToDelete)
    remove_dirs(dirsToDelete)

    # Re-enable building for Vxworks
    inFileName = 'configure/CONFIG_SITE'
    lineSubstitutions = {'#CROSS_COMPILER_TARGET_ARCHS = vxWorks-68040\n' : 'CROSS_COMPILER_TARGET_ARCHS = vxWorks-ppc32 vxWorks-ppc32-debug vxWorks-ppc32sf vxWorks-ppc32sf-debug\n'}
    modifyFile(inFileName, lineSubstitutions=lineSubstitutions)
    
    # Update nfsCommands
    inFileName = 'iocBoot/nfsCommands'
    patternsToExclude = ['oxygen', 'mooney']
    lineSubstitutions = { 'nfsMount("s100dserv","/APSshare","/APSshare")\n' : [ 
                   'nfsMount("s100dserv","/APSshare","/APSshare")\n',
                   'nfsMount("s100dserv","/xorApps","/xorApps")\n',
                   'nfsMount("s100dserv","/xorApps","/net/s100dserv/xorApps")\n',
                   '#!nfsMount("s100dserv","/export/beams","/home/beams")\n',
                   '\n',
                   '#!hostAdd(("aquila","164.54.100.16")\n',
                   '#!nfsMount("aquila","/export/beams3","/home/beams3")\n']
    }
    modifyFile(inFileName, patternsToExclude=patternsToExclude, lineSubstitutions=lineSubstitutions)

    # Update Makefile
    inFileName = 'iocBoot/ioc{}/Makefile'.format(iocName)
    patternsToExclude = ['win', 'linux', 'rhel']
    lineSubstitutions = { '#ARCH = vxWorks-ppc32\n' : ['ARCH = vxWorks-ppc32\n', '#ARCH = vxWorks-ppc32-debug\n'],
                       '#TARGETS = cdCommands\n' : 'TARGETS = cdCommands\n',
                       'TARGETS = envPaths\n' : '#TARGETS = envPaths\n',
                       'TARGETS = cdCommands envPaths dllPath.bat modules.lua\n' : 'TARGETS = cdCommands modules.lua\n',
    }
    modifyFile(inFileName, patternsToExclude=patternsToExclude, lineSubstitutions=lineSubstitutions)
    
    # Update st.cmd.vxWorks
    inFileName = 'iocBoot/ioc{}/st.cmd.vxWorks'.format(iocName)
    patternsToExclude = []
    lineSubstitutions = { '< cdCommands.vxWorks-ppc32sf\n' : ['#-< cdCommands.vxWorks-ppc32sf\n', '< cdCommands\n'],
                       'local_startup = "/enter/startup/directory/here/"\n' : '#-local_startup = "/enter/startup/directory/here/"\n',
                       'cd local_startup\n' : 'cd startup\n',
                       'epicsEnvSet("STARTUP", local_startup)\n' : '#-epicsEnvSet("STARTUP", local_startup)\n',
                       'epicsEnvSet("TOP", "$(STARTUP)/../..")\n' : '#-epicsEnvSet("TOP", "$(STARTUP)/../..")\n',
    }
    modifyFile(inFileName, patternsToExclude=patternsToExclude, lineSubstitutions=lineSubstitutions)
    
    
    # Undo changes that allow running from the xxx build on APSshare
    os.system("sed -i -e 's/xxxbin/topbin/g' -e 's/XXX/TOP/g' -e 's/xxx/{}/g' iocBoot/ioc{}/st.cmd.vxWorks".format(iocName, iocName))

def configureWindows(iocName):
    #
    filesToDelete = [ 'iocBoot/nfsCommands'.format(iocName), 
                      'iocBoot/ioc{}/cdCommands.vxWorks-ppc32'.format(iocName),
                      'iocBoot/ioc{}/cdCommands.vxWorks-ppc32sf'.format(iocName),
                      'iocBoot/ioc{}/st.cmd.vxWorks'.format(iocName),
                      'iocBoot/ioc{}/st.cmd.Linux'.format(iocName),
                      'iocBoot/ioc{}/st.cmd.vxWorks-local'.format(iocName),
        ]

    dirsToDelete = ['iocBoot/ioc{}/softioc'.format(iocName), ]

    #
    remove_files(filesToDelete)
    remove_dirs(dirsToDelete)

    # Create batch files
    batchFileSkeleton = """@echo OFF

SETLOCAL

REM This should match an existing subdirectory of the IOC's bin dir
set EPICS_HOST_ARCH={}

REM set EPICS_CA_MAX_ARRAY_BYTES=100000000

REM Add caRepeater to the PATH
REM set PATH=%PATH%;D:/epics/base-3.15.5/bin/%EPICS_HOST_ARCH%

REM Go to the startup directory
cd %~dp0

REM dlls to the PATH
call dllPath.bat

REM start the IOC
..\\..\\bin\\%EPICS_HOST_ARCH%\\xxx st.cmd.{}

pause

ENDLOCAL"""

    fn = 'iocBoot/ioc{}/start_ioc.Win32.bat'.format(iocName)
    with open(fn, 'w') as fh:
        fh.write(batchFileSkeleton.format("win32-x86-static", "Win32"))
    vprint('> git add {}'.format(fn))
    os.system('git add {}'.format(fn))

    fn = 'iocBoot/ioc{}/start_ioc.Win64.bat'.format(iocName)
    with open(fn, 'w') as fh:
        fh.write(batchFileSkeleton.format("windows-x64-static", "Win64"))
    vprint('> git add {}'.format(fn))
    os.system('git add {}'.format(fn))

    # Modify Makefile
    inFileName = 'iocBoot/ioc{}/Makefile'.format(iocName)
    patternsToExclude = ['vxWorks', 'linux', 'rhel', 'cyg' ]
    lineSubstitutions = { '#ARCH = windows-x64-static\n' : 'ARCH = windows-x64-static\n',
                       '#ARCH = win32-x86\n' : ['#ARCH = win32-x86-static\n',
                                                '#ARCH = win32-x86-debug\n',
                                                '#ARCH = win32-x86\n'],
                       'TARGETS = envPaths\n' : '#TARGETS = envPaths\n',
                       '#TARGETS = envPaths dllPath.bat\n' : 'TARGETS = envPaths dllPath.bat\n',
                       'TARGETS = cdCommands envPaths dllPath.bat modules.lua\n' : 'TARGETS = envPaths dllPath.bat modules.lua\n',
    }
    modifyFile(inFileName, patternsToExclude=patternsToExclude, lineSubstitutions=lineSubstitutions)

def includeMotorIocsh(iocName):
    #
    lineSubstitutions = { '< common.iocsh\n' : ['< common.iocsh\n',
                                                '\n',
                                                '< iocsh/motors.iocsh\n']}
    startupDir = 'iocBoot/ioc{}'.format(iocName)

    for fn in os.listdir(startupDir):
        if 'st.cmd' in fn:
            inFileName = "{}/{}".format(startupDir, fn)
            modifyFile(inFileName, lineSubstitutions=lineSubstitutions)

def vprint(message):
    global verbose
    if verbose == True:
        print(message)

verbose = None
quiet = None

def main(options):
    global verbose
    verbose = options.verbose
    global quiet
    quiet = options.quiet
    vprint(options)
    
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

        #
        includeMotorIocsh(iocName)

        #
        vprint('> git commit -m "Configured {} for {} with configIOC.py"'.format(iocName, options.os))
        if quiet:
            os.system('git commit -q -m "Configured {} for {} with configIOC.py"'.format(iocName, options.os))
        else:
            os.system('git commit -m "Configured {} for {} with configIOC.py"'.format(iocName, options.os))
    else:
        print("Error: {} is not an IOC dir".format(cwd))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser("configIOC.py")
    
    parser.add_argument('os', choices=('linux', 'vxWorks', 'windows'))
    parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", help="Print commands that are executed")
    parser.add_argument('-q', '--quiet', dest='quiet', action="store_true", help="Pass the quiet flag to git commands")
    
    options = parser.parse_args(sys.argv[1:])
    
    main(options)
