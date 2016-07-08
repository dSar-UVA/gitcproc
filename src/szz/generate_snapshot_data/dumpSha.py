#!/usr/bin/python

import argparse

import os, sys, inspect
import os.path
from os import listdir
from os.path import isfile, join

import shutil
import logging
import subprocess

import csv
from GitRepo import GitRepo



sys.path.append("src/util")
sys.path.append("src/changes")
from Config import Config
from OutDir import OutDir

import Log
from Util import cd
import Util
# from datetime import datetime
# from datetime import timedelta
# import ntpath, pickle

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
def dumpShas(srcPath, destPath, fileSha, isBlame=False):

  print srcPath, destPath, fileSha

  git_repo = GitRepo(srcPath)
  project_name = getProjName(srcPath)
  print project_name


  with open(fileSha, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
      proj, sha, file_name, commit_date = row[:]
      if proj != project_name:
        continue

      print (',').join((proj,sha,file_name,commit_date))

      fname, extension = os.path.splitext(file_name)
      fname = fname.replace(os.sep, Util.SEP)
      #print fname, extension

      #copy_file = destPath + os.sep + fname + sha + ".java"
      copy_file = fname + Util.SEP + sha + extension
      copy_file = os.path.join(destPath,copy_file)
      print copy_file
      if isBlame == True:
        git_repo.blameFile(file_name,sha,copy_file)
      else:
        #Todo: something else
        pass

    
  return

#--------------------------------------------------------------------------------------------------------------------------

def processOutput(outputStr):
  author_contribution = {}
  total_commit = 0
  for o in outputStr.split('\n'):
    o = o.strip()
    if o == '':
      continue
    o_arr = o.split(' ')
    if len(o_arr) > 1:
      total = o_arr[0]
      total_commit += int(total)

      author = o_arr[1]
      if len(o_arr) == 3:
        author += " " + o_arr[2]

      #print total, author
      #author_contribution.append((author,total))
      author_contribution[author] = total_commit
  return (author_contribution,total_commit)


#--------------------------------------------------------------------------------------------------------------------------
def processBlame(projectName, destPath, outFile):
  
  blame_dict = {} #(project,filename,sha,author)->(total,this_commit)

  
  blame_files = [f for f in listdir(destPath) if isfile(join(destPath, f))]
  
  for bf in blame_files:
    file_name = os.path.join(destPath,bf)
    fname, extension = os.path.splitext(bf)
    fname , sha = fname.rsplit(Util.SEP,1)
    fname = fname.replace(Util.SEP,os.sep) +  extension
    #print sha

    command1 = 'sed -n \'s/^author //p\' ' + \
              file_name + '| sort | uniq -c | sort -rn'
    proc = subprocess.Popen([command1], stdout=subprocess.PIPE, shell=True)
    (all_authors, err) = proc.communicate()

    all_commit, total = processOutput(all_authors)
    #print "all_commit : " , all_commit
    

    command2 = 'grep -A 3 ' + sha + " " + file_name + \
     '| sed -n \'s/^author //p\' | sort | uniq -c | sort -rn'
    proc = subprocess.Popen([command2], stdout=subprocess.PIPE, shell=True)
    (buggy_authors, err) = proc.communicate()
    this_commit, _ = processOutput(buggy_authors)
    #print "this_commit : " , this_commit

    for author, contrib in all_commit.iteritems():
      this_contrib = this_commit.get(author,0)
      key = (projectName,fname,sha,author)
   
      value = (contrib,this_contrib,total)
      #print author, value
      if not blame_dict.has_key(key):
        blame_dict[key] = value
      else:
        print "!! duplicate key"
        sys.exit()
  #print blame_dict

  of = open(outFile, "w")

  of.write('project,file,sha,author,author_commit,this_commit,total_commit\n')
  for key, value in blame_dict.iteritems():
    csv_str = (',').join((str(key[0]),str(key[1]),str(key[2]),\
          str(key[3]),str(value[0]),str(value[1]),str(value[2])))
    of.write(csv_str + '\n')
  
  of.close()
  
    

  








#=============================================================================================
#=============================================================================================


# Utility to take snapshots of git repositories at 6 months interval
# 1. First, retrieve the 1st commit date from SQL server
# 2. Copy the projects to directories: project_date1, project_date2, .... in each 6 months interval
# 3. For each copy checkout the dump upto that date

def main():

    parser = argparse.ArgumentParser(description='Utility to take snapshots of git repositories at specified sha')

    #project specific arguments
    parser.add_argument('-p',dest="proj_dir", help="the directory containing original src code")
    parser.add_argument('-d',dest="out_dir",  default='out_dir', help="directories to dump the snapshots")
    parser.add_argument('-o',dest="out_file", default='out_file', help="file to dump author stat")
    parser.add_argument('-l',dest="lang", default='java', help="languages to be processed")
    parser.add_argument('-i',dest="file_sha", default='file_sha.csv', help="csv file containing list of shas")

    #logging and config specific arguments
    parser.add_argument("-v", "--verbose", default = 'w', nargs="?", \
                            help="increase verbosity: d = debug, i = info, w = warnings, e = error, c = critical.  " \
                            "By default, we will log everything above warnings.")
    parser.add_argument("--log", dest="log_file", default='log.txt', \
    					help="file to store the logs, by default it will be stored at log.txt")
    parser.add_argument("--conf", dest="config_file", default='config.ini', help="configuration file, default is config.ini")



    args = parser.parse_args()

    if not os.path.isdir(args.proj_dir):
        print "!! Please provide a valid directory, given: %s" % (args.proj_dir)
    	sys.exit()

    print "Going to take snapshot for project %s" % (args.proj_dir)

    print "Output directory at %s" % (args.out_dir)


    Util.cleanup(args.log_file)

    Log.setLogger(args.verbose, args.log_file)

    cfg = Config(args.config_file)

    #2. Snapshot
    #dumpShas(args.proj_dir, args.out_dir, args.file_sha, isBlame=True)
    project_name = getProjName(args.proj_dir)
    
    processBlame(project_name,args.out_dir,args.out_file)

   

if __name__ == "__main__":
  main()
