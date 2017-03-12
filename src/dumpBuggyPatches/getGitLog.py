import sys
import os
import copy
from git import *


from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'..','util'))

import Util
from ConfigInfo import ConfigInfo
import LanguageSwitcherFactory
from ghLogDb import ghLogDb

LOG_FILE = "all_log.txt"

def runCmd(git_command, log_file):

  try:
    os.system("rm " + log_file)
  except:
    print("Rm failed.")
    pass
             
  os.system(git_command)


def dumpLog(projPath, languages, patch='True'):
  
    
    if not os.path.isdir(projPath):
        print("!! Please provide a valid directory, given %s" % projPath)
        return

    extSet = LanguageSwitcherFactory.LanguageSwitcherFactory.getExtensions(languages)
    #print(extSet)
    all_extn = ""

    for e in extSet:
        all_extn += " *"  + e
        all_extn += " *"  + e.upper()
        #all_extn += " \\*" + e
        #all_extn += " \\*" + e.upper()

    with Util.cd(projPath):
      print ">>>>" , os.getcwd()
        
      if patch == False:
             LOG_FILE = ["no_merge_log.txt","no_stat_log.txt"]
             git_cmd1 = "git log --no-merges --numstat --pretty=\">>>>>>>>>>>> %H <<|>> " \
                    + projPath + " <<|>> %cn <<|>> %cd <<|>> %an <<|>> %ad <<|>>\"" \
                    + " --diff-filter=M -- " + all_extn + " >  no_merge_log.txt"
             print git_cmd1
             runCmd(git_cmd1, "no_merge_log.txt")
             
             git_cmd2 = "git log --no-merges --pretty=\">>>>>>>>>>>> %H <<|>> " \
                    + projPath + " <<|>> %s <<|>> %b <<|>>\"" \
                    + " --diff-filter=M -- " + all_extn + " > no_stat_log.txt"
            
             runCmd(git_cmd2, "no_stat_log.txt")
             
             
      else:
            LOG_FILE = "all_log.txt"
            if(".c" in extSet or ".cpp" in extSet or ".py" in extSet):
                #This will still fail on really big files.... (could we see what the biggest file is and use that?)
                logCmd = "git log --date=short --no-merges -U99999 --function-context -- " + all_extn + " > " + LOG_FILE
            else: #Java
                logCmd = "git log --date=short --no-merges -U1 --function-context -- " + all_extn + " > " + LOG_FILE

            #os.system("git stash save --keep-index; git pull")
            runCmd(logCmd, LOG_FILE)

           


def getGitLog(dumpLocation, repos, languages, patchMode=True):

    projects = os.listdir(dumpLocation)

    count = 0
    for p in projects:
      #if (len(repos) != 0 and p in repos) or (len(repos) == 0):
          count += 1      
          proj_path = os.path.join(dumpLocation, p)
          print "===> Dumping log -- Location : %s,  Patch Mode : %s " % (proj_path, patchMode)
          dumpLog(proj_path, languages, patchMode)


def main():
    print "==== Utility to download Github logs ==="
    #subprocess.call(["python", "getGitLog.py", config_file])
    
    if len(sys.argv) < 2:
      print "!!! Usage: python getGitLog.py config_file"
      sys.exit()

    config_file = sys.argv[1]  
    config_info = ConfigInfo(config_file)         
    
    langs = config_info.getLanguages()
    patch_mode = config_info.getPatchMode()
    bug_patch_mode = config_info.getBugPatchMode()
    print bug_patch_mode
    dump_location = config_info.getDumpLocation()
    repos = config_info.getRepos()

    
    if not os.path.isdir(dump_location):
      print("!!== Please provide a valid directory: given %s" % dump_location)
      return


    getGitLog(dump_location, repos, langs, patch_mode)

    print "Done!!"


if __name__ == '__main__':
    main()








