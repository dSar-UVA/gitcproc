import sys
import os
import copy
from git import *

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'..','util'))

import Util
import LanguageSwitcherFactory
from ghLogDb import ghLogDb
from Config import Config

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
        all_extn += " \\*"  + e
        all_extn += " \\*"  + e.upper()

    with Util.cd(projPath):
        
      if patch == 'False':
             LOG_FILE = ["no_merge_log.txt","no_stat_log.txt"]
             git_cmd1 = "git log --no-merges --numstat --pretty=\">>>>>>>>>>>> %H <<|>> " \
                    + projPath + " <<|>> %cn <<|>> %cd <<|>> %an <<|>> %ad <<|>>\"" \
                    + " --diff-filter=M -- " + all_extn + " >  no_merge_log.txt"
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

           


def getGitLog(project, languages, repo_file=None, patch=True):

    projects = os.listdir(project)
    repos = set()
    
    if not repo_file is None:
      f = open(repo_file, 'r')
      for line in f:
        repo_url = line.strip()
        _, repo = repo_url.split(os.sep) 
        repos.add(repo)

    count = 0
    for p in projects:
        if (len(repos) != 0 and p in repos) or (len(repos) == 0):
          count += 1      
          proj_path = os.path.join(project, p)
          dumpLog(proj_path, languages, patch)


def main():
    print "==== Utility to process Github logs ==="
    #subprocess.call(["python", "getGitLog.py", repo_config['repo_locations'], config_file])
    
    if len(sys.argv) < 3:
      print "!!! Usage: python getGitLog.py project config_file"
      sys.exit()

    project = sys.argv[1]
    config_file = sys.argv[2]        

    cfg = Config(config_file)
    log_config  = cfg.ConfigSectionMap("Log")
    repo_config = cfg.ConfigSectionMap("Repos")
    
    try:
        repo_file = repo_config['repo_url_file']
    except:
        repo_file = None
            
    try:
        langs = log_config['languages'].split(",")
    except:
        langs = [] #Treat empty as showing all supported languages.

    try:
        patch = log_config['patch']
    except:
        patch = True

    print "Patch Mode : %s" % (patch)
 

    if not os.path.isdir(project):
        print("!!== Please provide a valid directory: given %s" % project)
        return


    getGitLog(project, langs, repo_file, patch)

    print "Done!!"


if __name__ == '__main__':
    main()








