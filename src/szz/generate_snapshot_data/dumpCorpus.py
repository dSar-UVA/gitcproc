#!/usr/bin/python

import argparse
import os, sys, inspect
import os.path
import shutil
import logging
import datetime

from shlex import split as format_cmd
from subprocess import Popen, PIPE, STDOUT, call

from Corpus import Corpus


from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'../../','util'))

from ConfigInfoSZZ import ConfigInfoSZZ

import Log
import Util


def downloadCorpus(snapshotDir, corpusDir, projectName, configInfo):

  # 2. Dump the snapshots for a project
  msg =  '---------------------------------------------------- \n'
  msg += ' Dump the corpus for project %s \n' % projectName
  msg += '---------------------------------------------------- \n'
  print(msg)
           
  project_snapshot_dir = os.path.join(snapshotDir, projectName)
  project_corpus_dir = os.path.join(corpusDir, projectName)
  
  if os.path.isdir(project_corpus_dir):
    print "!! %s already exists...returning \n" % project_corpus_dir
    #return
    
  corpus = Corpus(project_snapshot_dir, 'java', project_corpus_dir, configInfo)
  #logging.debug(corpus)
  #print corpus
  corpus.dump()

    

def downloadCorpuses(config_info):
  
  repo_config = config_info.config_repo
  
  #Check that the repo list file exists
  if(not os.path.isfile(repo_config['repo_url_file'])):
    print(repo_config['repo_url_file'] + ", the file containing the list of projects to download,")
    print("cannot be found.  Make sure your path and name are correct.")
    return
            
  snapshot_dir = config_info.config_szz['snapshot_locations']
  if(not os.path.isdir(snapshot_dir)):
    print(snapshot_dir + " is not found")
    print("Please give a valid directory containing the snapshots")
    return
  
  corpus_dir = config_info.getCorpusLocation()
  print ">>>>>>", corpus_dir
  if(not os.path.isdir(corpus_dir)):
    print "Going to create ", corpus_dir
    os.system('mkdir ' + corpus_dir)
      
  repos = config_info.getRepos()
  for r in repos:
    print r
    downloadCorpus(snapshot_dir, corpus_dir, r, config_info)
#=============================================================================================

def main():

    parser = argparse.ArgumentParser(description='Tool to dump commit history for given project')

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
    downloadCorpuses(config_info)



if __name__ == "__main__":
  main()



