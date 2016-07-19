#!/usr/bin/python

import argparse
import os, sys
import os.path
import logging
import csv

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'../../','util'))
sys.path.append(os.path.join(dirname(__file__),'..','.'))

from ConfigInfoSZZ import ConfigInfoSZZ

from szz import szz

import Log
import Util


def getBugFixShas(dumpDir, projectName):
    
    proj_loc = os.path.join(dumpDir, projectName)
    
    change_db_csv = os.path.join(proj_loc,'FileChanges.csv')
    bugfix_db_csv = os.path.join(proj_loc,'BugFixShas.csv')
    
    if not os.path.isfile(change_db_csv):
        print "!!! %s does not exist, first dump the changes..returning" % (change_db_csv)
        return -1
    else:
        print "Going to process change db: %s" % (change_db_csv)

    of = open(bugfix_db_csv, 'w')
    bugfix_shas = []
    
    with open(change_db_csv, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        csvreader.next()
        count = 0
        for row in csvreader:
            count = count + 1
            project, sha, language, file_name, is_test, committer, \
            commit_date, author, author_date, is_bugfix, total_add, total_del = row[:]
            
            if Util.str2bool(is_bugfix) == True:
                bugfix_shas.append(sha)
                of.write(sha + '\n')

    logging.debug("%s: total commit : %d, bugfix commit : %d, percentage: %f" \
                  % (projectName, count, len(bugfix_shas)  , (len(bugfix_shas) * 100.0/count)))
    
    of.close()
    return bugfix_shas
    
def mapBugPerProj(configInfo,projName):
    
    project_snapshots_path = configInfo.getProjectSnapshot(projName)
    project_corpus_path    = configInfo.getProjectCorpus(projName)
    project_path           = configInfo.getProjectLocation(projName)
    bugfix_SHAs_filename   = os.path.join(project_path , 'BugFixShas.csv')
    num_of_cores = 4
    
    szz(project_corpus_path, project_snapshots_path, bugfix_SHAs_filename, num_of_cores)
    
    
def mapBugs(config_info):
    
    #First check whether everything is alright!!
    repo_config = config_info.config_repo
    
    #Check that the repo list file exists
    if(not os.path.isfile(repo_config['repo_url_file'])):
        print(repo_config['repo_url_file'] + ", the file containing the list of projects to download,")
        print("cannot be found.  Make sure your path and name are correct.")
        return
    
    project_dir = config_info.getDumpLocation()
    if(not project_dir):
        print(project_dir + " is not found")
        print("Please give a valid directory containing all the projects")
        return     
            
    if(not config_info.getSnapshotLocation()):
        print(config_info.getSnapshotLocation() + " is not found")
        print("Please give a valid directory containing the snapshots")
        return
    
    if(not config_info.getCorpusLocation()):
        print(config_info.getCorpusLocation() + " is not found")
        print("Please give a valid corpus of changes")
        return
  

    repos = config_info.getRepos()
    for r in repos:
        print r
        bf_shas = getBugFixShas(project_dir,r)
        mapBugPerProj(config_info,r)
        #szz()
#=============================================================================================

def main():

    parser = argparse.ArgumentParser(description='Tool to map bugs to snapshot')

    #project specific arguments
    parser.add_argument("config_file", help = "This is the path to your configuration file.")
    
    #logging and config specific arguments
    parser.add_argument("-v", "--verbose", default = 'd', nargs="?", \
                            help="increase verbosity: d = debug, i = info, w = warnings, e = error, c = critical.  " \
                            "By default, we will log everything above warnings.")
    
    parser.add_argument("--log", dest="log_file", default='log.txt', \
    					help="file to store the logs, by default it will be stored at log.txt")
    
    args = parser.parse_args()

    Util.cleanup(args.log_file)

    Log.setLogger(args.verbose, args.log_file)
    
    config_info = ConfigInfoSZZ(args.config_file)  
    mapBugs(config_info)



if __name__ == "__main__":
  main()



