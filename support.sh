#!/bin/bash
#
# A script to create & maintain a support directory for motor development
#

# Stuff to customize
EPICS_BASE=/APSshare/epics/base-3.15.6
SEQ_VER=seq-2.2.7
EPICS_HOST_ARCH=linux-x86_64

setup() {

  # Overwrite the default RELEASE file until the synApps build system improves
  RELEASE_FILE=configure/RELEASE

  GITHUB=https://github.com

  SYNAPPS_MODULES=
  EPICS_MODULES=
  AREADETECTOR_MODULES=

  SUPPORT=$(pwd)

  ### Use the synApps build system to simplify the process of updating RELEASE files
  SYNAPPS_MODULES+=" support"
  SYNAPPS_MODULES+=" configure"
  SYNAPPS_MODULES+=" utils"		# necessary for 'make release to succeed'
  #!EPICS_MODULES+=" alive"		# generally useful
  EPICS_MODULES+=" asyn"		# required by motor
  EPICS_MODULES+=" autosave"	# required for tests in busy ; generally useful
  EPICS_MODULES+=" busy"		# required by motor
  EPICS_MODULES+=" calc"		# generally useful
  EPICS_MODULES+=" ipac"		# required for motorHytec
  #!EPICS_MODULES+=" iocStats"	# generally useful
  EPICS_MODULES+=" lua"			# required for motorScriptMotor
  EPICS_MODULES+=" modbus"		# required for motorAMCI
  EPICS_MODULES+=" sscan"		# generally useful
  EPICS_MODULES+=" std"			# generally useful
  ### motor
  EPICS_MODULES+=" motor"
  ### driver submodules
  MOTOR_SUBMODULES+=" motorMotorSim"
  #!MOTOR_SUBMODULES+=" motorScriptMotor"
  ### stand-alone driver modules
  MOTOR_MODULES+=" motorVMC"
}

#
enterDirIfExists() {
  directory=${1}
  echo "> ${directory}"
  
  if [ "${directory}" == "support" ]
  then
    directory=.
  fi
  
  if [ -d "${directory}" ]
  then
    cd ${directory}
  else
    echo "\"${directory}\" directory doesn't exist"
    exit 1
  fi
}

#
exitDir() {
  if [[ ${1} == *"/"* ]]
  then
    # We're in the motor submodules dir
    cd ../..
  elif [[ "${1}" != "support" && "${1}" != "motor" ]]
  then
    # We're in a module directory
    cd ..
  fi
}

#
status() {
  enterDirIfExists ${1}
  
  if [[ ${FULL_STATUS} == "False" ]]
  then
    #!git status | grep "Your branch"
    STATUS=`git status | grep "Your branch"`
    if [[ "${STATUS}" != "" ]]; then
      echo ${STATUS}
    else
      # Old versions of git lack this message, so simulate it
      echo "Your branch is up-to-date with 'origin/master'."
    fi  
  else
    git status
  fi
  
  exitDir ${1}
}

#
fetch() {
  enterDirIfExists ${1}
  
  git fetch
  
  exitDir ${1}
}

# rebase is a windows program, so function had to have a different name
update() {
  enterDirIfExists ${1}
  
  STATUS=`git status | grep "Your branch"`
  if [[ "${STATUS}" != "" ]]; then
    echo ${STATUS}
  else
    # Old versions of git lack this message, so simulate it
    echo "Your branch is up-to-date with 'origin/master'."
  fi
  
  if [[ "${STATUS}" =~ "can be fast-forwarded" ]]
  then
    # Auto stashing and applying changes frequently causes merge conflicts
    #!echo "- Rebasing ${1}"
    #!git stash
    #!git rebase origin/master
    #!git stash apply
    
    if [[ ${MANUAL_REBASE} == "True" ]]
    then
      ### Manually rebase instead
      echo "- Rebasing ${1} manually. Type \"exit\" when done."
      echo "$ git status"
      git status
      
      # Change the prompt so the user knows they're in a different shell
      if [[ "${OS}" == "Windows_NT" ]]
      then
        OLD_MSYSTEM=${MSYSTEM}
        export MSYSTEM="Rebasing ${1}"
        
        # Run a new bash instance for interactive rebasing
        bash
        
        # Restore the original prompt
        export MSYSTEM=${OLD_MSYSTEM}
      else
        # Run a new bash instance for interactive rebasing
        # Note --rcfile also works
        bash --init-file <(echo "PS1='Rebasing ${1} $ '") -i
      fi
    else
      ### Automatically rebase
      echo "- Automatically rebasing ${1}"
      git stash && git rebase origin/master && git stash apply
      echo "$ git status"
      git status
    fi
  fi
  
  exitDir ${1}
}

extraSpace() {
  if [ "${FUNC}" == "status" ]; then
    echo ""
  fi
}

# The main routine of the script
main() {
  # Create module lists
  setup
  
  ### synApps modules
  for module in ${SYNAPPS_MODULES}; do
    extraSpace
    ${FUNC} ${module}
  done

  ### EPICS modules
  for module in ${EPICS_MODULES}; do
    extraSpace
    ${FUNC} ${module}
    
    #
    if [ "${module}" == "motor" ]; then
      # Only include driver submodules when fetching or displaying the status
      if [ "${FUNC}" != "update" ]; then
        # submodules
        for submodule in ${MOTOR_SUBMODULES}; do
          extraSpace
          ${FUNC} modules/${submodule}
        done
      fi
      # We need to manually exit the motor dir
      cd ..
    fi
  done

  ### stand-alone motor modules
  for motor_module in ${MOTOR_MODULES}; do
    extraSpace
    ${FUNC} ${motor_module}
  done
  
}

# The cloning function is very similar to main(), but not similar enough to be combined
clone() {
  # Create module lists
  setup
  
  ### synApps modules
  for module in ${SYNAPPS_MODULES}; do
    if [ "${module}" == "support" ]; then
      # Assume the script is being called from the support dir
      if [ -d ".git" ]; then
        echo ".git already exists; refusing to clone ${module}"
      else
        echo "cloning support"
        git clone --quiet ${GITHUB}/EPICS-synApps/support.git .
      fi 
    elif [ -d "${module}" ]; then
      echo "${module} already exists"
    else
      echo "cloning ${module}"
      git clone --quiet ${GITHUB}/EPICS-synApps/${module}.git
    fi
  done
  
  ### EPICS modules
  for module in ${EPICS_MODULES}; do
    if [ -d "${module}" ]; then
      echo "${module} already exists"
    else
      echo "cloning ${module}"
      git clone --quiet ${GITHUB}/epics-modules/${module}.git
      
      # Handle special cases
      if [ "${module}" == "stream" ]; then
        # stream is just a wrapper; update the submodule
        cd stream
        echo "initializing StreamDevice submodule"
        git submodule --quiet init
        # the --quiet flag appears to be ignored when doing the update with git v1.7.1
        git submodule --quiet update
        cd ..
      fi
      
      if [ "${module}" == "motor" ]; then
        cd ${module}
        echo "initializing motor submodules"
        git submodule --quiet init
        # the --quiet flag appears to be ignored when doing the update with git v1.7.1
        for submodule in ${MOTOR_SUBMODULES}; do
          if [ -d "modules/${submodule}" ]; then
            # Only clone into an existing directory if it is empty
            if [ "$(ls -A modules/${submodule})" ]; then
              echo "${submodule} is not empty"
            else
              echo "updating ${submodule}"
              git submodule --quiet update modules/${submodule}
            fi
          fi
        cd ..
        done
        
        exitDir ${module}
      fi
    fi
  done
  
  # Stand-alone motor modules
  for motor_module in ${MOTOR_MODULES}; do
    if [ -d "${motor_module}" ]; then
      echo "${motor_module} already exists"
    else
      echo "cloning ${motor_module}"
      git clone --quiet ${GITHUB}/epics-motor/${motor_module}.git
    fi
  done
  
  if [[ "${WGET_NOT_FOUND}" == "0" ]]
  then
    mkdir tar

    SEQ_DIR=${SEQ_VER//./-}
    echo ${SEQ_DIR} ${SEQ_VER}
    if [ -d ${SEQ_DIR} ]; then
      echo "${SEQ_DIR} already exists"
    else
      echo "fetching & extracting ${SEQ_DIR}"
      # http://www-csr.bessy.de/control/SoftDist/sequencer/Installation.html#download
      ${WGET} --no-check-certificate --quiet -O tar/${SEQ_VER}.tar.gz http://www-csr.bessy.de/control/SoftDist/sequencer/releases/${SEQ_VER}.tar.gz
      
      # The synApps build can't handle "."
      #!tar xzvf tar/${SEQ_VER}.tar.gz
      tar xzf tar/${SEQ_VER}.tar.gz
      mv ${SEQ_VER} ${SEQ_DIR}
    fi
    
    rm -rf tar/
  fi

  echo "done cloning modules"
  
  # this only needs to be done once, but patterns will be appended to .gitignore every time clone is run
  echo "updating ignores"
  for module in asyn cfg ipac lua ${SEQ_DIR}; do
    echo "${module}/" >> .gitignore
  done
  for motor_module in in ${MOTOR_MODULES}; do
    echo "${motor_module}/" >> .gitignore
  done
  
  echo "Creating ${RELEASE_FILE}"
  #
  echo "EPICS_BASE=${EPICS_BASE}" > ${RELEASE_FILE}
  echo "SUPPORT=${SUPPORT}" >> ${RELEASE_FILE}
  echo "" >> ${RELEASE_FILE}
  #
  ### EPICS modules
  for module in ${EPICS_MODULES}; do
    echo "${module^^}=\$(SUPPORT)/${module}" >> ${RELEASE_FILE}
  done
  if [[ "${WGET_NOT_FOUND}" == "0" ]]; then
    echo "SNCSEQ=\$(SUPPORT)/seq-2-2-7" >> ${RELEASE_FILE}
  fi
  ###
  for motor_module in ${MOTOR_MODULES}; do
    # Append to the support/configure/RELEASE file
    release_name="${motor_module:0:5}_${motor_module:5}"
    echo "${release_name^^}=\$(SUPPORT)/${motor_module}" >> ${RELEASE_FILE}
    # Create a RELEASE.local in the driver module
    echo "SUPPORT=${SUPPORT}" > ${motor_module}/configure/RELEASE.local
    echo "include \$(SUPPORT)/configure/RELEASE" >> ${motor_module}/configure/RELEASE.local
  done
  echo "" >> ${RELEASE_FILE}
  
  # Update the release files of all the modules (until the synApps build system improves)
  make release
  # Use a global RELEASE.local file in the support dir--this should work but it doesn't due to circular dependencies
  #!echo "SUPPORT=${SUPPORT}" > RELEASE.local
  #!echo "include \$(SUPPORT)/configure/RELEASE" >> RELEASE.local
}

#!echo ${#}
# Parse command-line arg
if [[ ${#} -eq 1 ]]
then
  OPT=${1}
  
  case ${OPT} in 
    "clone")
      echo "-> clone"
      WGET=`which wget`
      WGET_NOT_FOUND=$?
      
      if [[ ${WGET_NOT_FOUND} == "1" ]]
      then
        echo ""
        echo "Error: wget not found. wget is required for cloning"
      else
        echo "Found wget: ${WGET}"
      fi
      ;;
    
    "fetch")
      echo "-> fetch"
      FUNC=fetch
      ;;
    
    "stat")
      echo "-> status"
      FULL_STATUS=False
      FUNC=status
      ;;
    
    "status")
      echo "-> status-full"
      FULL_STATUS=True
      FUNC=status
      ;;
    
    "rebase")
      echo "-> rebase"
      MANUAL_REBASE=True
      FUNC=update
      ;;
    
    "auto-rebase")
      echo "-> auto-rebase"
      MANUAL_REBASE=False
      FUNC=update
      ;;
    
    *)
      echo "Error: ${OPT} is not a valid option"
      exit 1
      ;;
  esac
  
else
  echo "Usage: support.sh <clone|fetch|status|stat|rebase|auto-rebase>"
  exit 1
fi

# Do whatever was requested
if [[ "${OPT}" == "clone" ]]
then
  clone
else
  main
fi
