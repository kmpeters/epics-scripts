#!/APSshare/anaconda3/x86_64/bin/python

import os
import sys
import argparse

import getLatestRelease as glr

module_dict = {
"SUPPORT"        :      ("EPICS-synApps",          "support"),
"ALIVE"          :      ("epics-modules",          "alive"),
"AREA_DETECTOR"  :      ("areaDetector",           "areaDetector"),
"ASYN"           :      ("epics-modules",          "asyn"),
"AUTOSAVE"       :      ("epics-modules",          "autosave"),
"BUSY"           :      ("epics-modules",          "busy"),
"CALC"           :      ("epics-modules",          "calc"),
"CAMAC"          :      ("epics-modules",          "camac"),
"CAPUTRECORDER"  :      ("epics-modules",          "caputRecorder"),
"DAC128V"        :      ("epics-modules",          "dac128V"),
"DELAYGEN"       :      ("epics-modules",          "delaygen"),
"DXP"            :      ("epics-modules",          "dxp"),
"DXPSITORO"      :      ("epics-modules",          "dxpSITORO"),
"DEVIOCSTATS"    :      ("epics-modules",          "iocStats"),
"ETHERIP"        :      ("EPICSTools",             "ether_ip"),
"GALIL"          :      ("motorapp",               "Galil-3-0"),
"IP"             :      ("epics-modules",          "ip"),
"IPAC"           :      ("epics-modules",          "ipac"),
"IP330"          :      ("epics-modules",          "ip330"),
"IPUNIDIG"       :      ("epics-modules",          "ipUnidig"),
"LOVE"           :      ("epics-modules",          "love"),
"LUA"            :      ("epics-modules",          "lua"),
"MCA"            :      ("epics-modules",          "mca"),
"MEASCOMP"       :      ("epics-modules",          "measComp"),
"MODBUS"         :      ("epics-modules",          "modbus"),
"MOTOR"          :      ("epics-modules",          "motor"),
"OPTICS"         :      ("epics-modules",          "optics"),
"QUADEM"         :      ("epics-modules",          "quadEM"),
"SOFTGLUE"       :      ("epics-modules",          "softGlue"),
"SOFTGLUEZYNQ"   :      ("epics-modules",          "softGlueZynq"),
"SSCAN"          :      ("epics-modules",          "sscan"),
"STD"            :      ("epics-modules",          "std"),
"STREAM"         :      ("paulscherrerinstitute",  "StreamDevice"),
"VAC"            :      ("epics-modules",          "vac"),
"VME"            :      ("epics-modules",          "vme"),
"XSPRESS3"       :      ("epics-modules",          "xspress3"),
"YOKOGAWA_DAS"   :      ("epics-modules",          "Yokogawa_DAS"),
"XXX"            :      ("epics-modules",          "xxx")
}

def make_config(filename):
  #
  with open(filename, 'r') as template:
    for line in template:
      # line has a newline on the end of it
      new_line = line.strip()
      if '=' in new_line:
        if new_line[-1] == '=':
          #
          key = new_line[:-1]
          user, repo = module_dict[key]
          latest_release = glr.get_latest_release(user, repo)
          new_line = "{}{}".format(new_line, latest_release)
      
      print(new_line)
  
def main(options):
  filename = options.filename
  
  if os.path.exists(filename):
    make_config(filename=filename)
  else:
    print("{} does not exist".format(filename))

if __name__ == '__main__':
  parser = argparse.ArgumentParser("makeConfig.py")
  
  parser.add_argument('filename', action="store", default=None)
  
  options = parser.parse_args(sys.argv[1:])
  #print(options)
  
  main(options)
 
