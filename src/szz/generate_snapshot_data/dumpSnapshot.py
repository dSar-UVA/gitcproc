#!/usr/bin/python

import argparse
import os, sys, inspect
import os.path
import shutil
import logging
from git import *
import csv
from shlex import split as format_cmd
from subprocess import Popen, PIPE, STDOUT, call

from projDB import DbProj

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'../../','util'))
sys.path.append(os.path.join(dirname(__file__),'..','changes'))
sys.path.append(os.path.join(dirname(__file__),'..','.'))

#from OutDir import OutDir
from ConfigInfoSZZ import ConfigInfoSZZ

import Log
from Util import cd
import Util
from datetime import datetime
from datetime import timedelta
import ntpath, pickle
#--------------------------------------------------------------------------------------------------------------------------
def pathLeaf(path):
    """
    Returns the basename of the file/directory path in an _extremely_ robust way.
    
    For example, pathLeaf('/hame/saheel/git_repos/szz/abc.c/') will return 'abc.c'.
    
    Args
    ----
    path: string
        Path to some file or directory in the system

    Returns
    -------
    string
        Basename of the file or directory
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

#--------------------------------------------------------------------------------------------------------------------------
def getProjName(projectPath):

    proj_path = projectPath.rstrip(os.sep)
    project_name = proj_path.split(os.sep)[-1]

    return project_name
    
#--------------------------------------------------------------------------------------------------------------------------
def dumpSnapshotsBySha(srcPath, destPath, shaList):

    print srcPath, destPath
    print len(shaList)

    repo = Repo(srcPath)
    branch = repo.active_branch

    print branch

    project_name = getProjName(srcPath)
    
    for sha in shaList:
      print sha[0],sha[1]
      snapshot = os.path.join(destPath, sha[0])

      if not os.path.isdir(snapshot):
        Util.copy_dir(srcPath,snapshot)
        git_command = "git checkout " + sha[1] 
        print git_command
        with cd(snapshot):
          os.system("git reset --hard")
          #os.system("git checkout")
          os.system(git_command)
        
      
    
#--------------------------------------------------------------------------------------------------------------------------
def dumpSnapshotsByInterval(srcPath, destPath, ss_interval_len, commitDateMin, commitDateMax):

    print srcPath, destPath, commitDateMin, commitDateMax

    repo = Repo(srcPath)
    branch = repo.active_branch

    print branch

    project_name = getProjName(srcPath)

    start_date = commitDateMin + timedelta(days=1)

    while start_date <= commitDateMax:
        #snapshot = destPath + os.sep + project_name + os.sep + project_name + "_" + str(start_date)
        snapshot = destPath + os.sep + project_name + os.sep + str(start_date)
        print snapshot

        if not os.path.isdir(snapshot):
            Util.copy_dir(srcPath,snapshot)
            git_command = "git checkout `git rev-list -n 1 --no-merges --before=\"" + str(start_date) + "\" " +  str(branch) + "`"
            with cd(snapshot):
                os.system("git reset --hard")
                #os.system("git checkout")
                os.system(git_command)

        start_date = start_date + timedelta(days=ss_interval_len*30)

    #snapshot = destPath + os.sep + project_name + os.sep + project_name + "_" + str(commitDateMax)
    start_date = commitDateMax
    snapshot = destPath + os.sep + project_name + os.sep + str(start_date)

    print snapshot
    if not os.path.isdir(snapshot):
        Util.copy_dir(srcPath,snapshot)
        git_command = "git checkout `git rev-list -n 1 --no-merges --before=\"" + str(start_date) + "\" " +  str(branch) + "`"
        with cd(snapshot):
            os.system("git reset --hard")
            #os.system("git checkout")
            os.system(git_command)




#--------------------------------------------------------------------------------------------------------------------------
def fetchCommitDate(cfg, projectPath, languages):

    db_config = cfg.ConfigSectionMap("Database")
    logging.debug("Database configuration = %r\n", db_config)

    proj_path = projectPath.rstrip(os.sep)
    project_name = proj_path.split(os.sep)[-1]

    logging.debug("project = %r\n", project_name)

    proj = DbProj(project_name, language)
    proj.connectDb(db_config['database'], db_config['user'], db_config['host'], db_config['port'])
    proj.fetchDatesFromTable(db_config['table'])

    logging.debug(proj)

    print proj

    print proj.projects

    assert(len(proj.projects) == 1)

    _ , _ , commit_date_min, commit_date_max = proj.projects[0]

    return (commit_date_min, commit_date_max)
    
    
    
def fetchCommitDates(cfg, projectPath, languages):
    min_commit_date = []
    max_commit_date = []
    
    for l in languages:
      mind, maxd = fetchCommitDate(configInfo, projectPath, l)
      min_commit_date.append(mind)
      max_commit_date.append(maxd)

    return (min(min_commit_date), max(max_commit_date))




#=============================================================================================
def downloadSnapshot(snapshotDir, projectDir, projectName, configInfo):

  # 2. Dump the snapshots for a project
  msg =  '---------------------------------------------------- \n'
  msg += ' Dump the snapshots for project %s \n' % projectName
  msg += '---------------------------------------------------- \n'
  print(msg)
           
  project_snapshot_dir = os.path.join(snapshotDir, projectName)
  project_cur_clone = os.path.join(projectDir, projectName)
  
  if os.path.isdir(project_snapshot_dir):
    print "!! %s already exists...going to delete it \n" % project_snapshot_dir
    call(format_cmd("rm -rf " + project_snapshot_dir))
    
  interval = configInfo.getSnapshotInterval()
  
  if interval > 0:
    #1. First, retrieve the 1st commit date from SQL server
    langs = config_info.getLanguages()
    commit_dates = fetchCommitDates(configInfo, project_cur_clone, langs)

    #2. Snapshot
    dumpSnapshotsByInterval(project_cur_clone, project_snapshot_dir, interval, commit_dates[0], commit_dates[1])
    
  elif interval == -1:
    sha_list = []
    snapshot_sha_file = configInfo.getShaFiles()
    print snapshot_sha_file
    with open(snapshot_sha_file, 'rb') as csvfile:
      csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
      csvreader.next()
      for row in csvreader:
        bug_no,buggy_sha,bugfix_sha,project = row[:]
        if project.strip("\"") == projectName:
          #print bug_no,buggy_sha,bugfix_sha,project
          buggy_sha = buggy_sha.strip("\"")
          sha_list.append((bug_no,buggy_sha))
    dumpSnapshotsBySha(project_cur_clone, project_snapshot_dir, sha_list)
  
  else:
    print "!! No valid interval....not able to download snapshots"
  
    
    

def downloadSnapshots(config_info):
  
  repo_config = config_info.config_repo
  
  #Check that the repo list file exists
  if(not os.path.isfile(repo_config['repo_url_file'])):
    print(repo_config['repo_url_file'] + ", the file containing the list of projects to download,")
    print("cannot be found.  Make sure your path and name are correct.")
    return

  #Create the output directory if it doesn't exist yet.
  project_dir = repo_config['repo_locations']
  if(not os.path.isdir(project_dir)):
    print(project_dir + " is not found")
    print("Please give a valid directory containing the projects")
    print("Use repoMiner -dl to download projects")
    return
      
      
  snapshot_dir = config_info.config_szz['snapshot_locations']
  if(not os.path.isdir(snapshot_dir)):
    call(format_cmd('mkdir ' + snapshot_dir))
      
  repos = config_info.getRepos()
  for r in repos:
    print r
    downloadSnapshot(snapshot_dir, project_dir, r, config_info)
#=============================================================================================


# Utility to take snapshots of git repositories at 6 months interval
# 1. First, retrieve the 1st commit date from SQL server
# 2. Copy the projects to directories: project_date1, project_date2, .... in each 6 months interval
# 3. For each copy checkout the dump upto that date

def main():

    parser = argparse.ArgumentParser(description='Utility to take snapshots of git repositories at specified (in months) interval')

    #project specific arguments
    parser.add_argument("config_file", help = "This is the path to your configuration file.")

    #logging and config specific arguments
    parser.add_argument("-v", "--verbose", default = 'w', nargs="?", \
                            help="increase verbosity: d = debug, i = info, w = warnings, e = error, c = critical.  " \
                            "By default, we will log everything above warnings.")
    parser.add_argument("--log", dest="log_file", default='log.txt', \
    					help="file to store the logs, by default it will be stored at log.txt")
    



    args = parser.parse_args()

    Util.cleanup(args.log_file)

    Log.setLogger(args.verbose, args.log_file)
    
    config_info = ConfigInfoSZZ(args.config_file)  
    downloadSnapshots(config_info)
    



if __name__ == "__main__":
  main()