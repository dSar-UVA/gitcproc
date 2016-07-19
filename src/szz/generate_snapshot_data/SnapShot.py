#!/usr/bin/python

import argparse
import os, sys, inspect
import os.path
import shutil
import logging

from datetime import datetime
import ntpath
import codecs

from GitRepo import GitRepo
from OutDir import OutDir

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'../../','util'))
import Log
from Util import cd
import Util

# Given a path, returns the basename of the file/directory in an _extremely_ robust way
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

class SnapShot:

    def __init__(self, projPath, snapshotName, outDir, configInfo):

        self.name = snapshotName
        self.src_path = os.path.join(projPath, snapshotName)

        self.config_info = configInfo
        self.debug      = configInfo.DEBUG
        self.git_repo = GitRepo(self.src_path)
        self.date  = self.getSnapshotDate() #datetime.datetime.strptime(snapshot, '%Y-%m-%d').date
        self.out_path = os.path.join(outDir, snapshotName)

        self.out_dir = None
        self.edits = []
        self.test_files = set()
        self.train_files = set()

    def __str__(self):

        retStr = self.name + "\n"
        retStr += str(self.date) + "\n"
        retStr += "========\n"

        for e in self.edits:
            retStr += str(e)
        return retStr

    def getSnapshotDate(self):

        try:
            snapshot_date = datetime.strptime(self.name, '%Y-%m-%d').date()
        except:
            with Util.cd(self.src_path):
                print ">>>>>>> ", self.src_path
                
                git_show = Util.runCmd('git show --date=short')[1]
                for l in git_show.split('\n'):
                    if l.startswith('Date:'):
                        snapshot_date = l.split('Date: ')[1].strip()
                        snapshot_date = datetime.strptime(snapshot_date, '%Y-%m-%d').date()
                        

        return snapshot_date


    def addEdit(self, edit):

        if self.out_dir is None:
            self.out_dir = OutDir(self.out_path)
            self.out_dir.create_out_dir(self.out_path)

        self.edits.append(edit)


    def getTestFiles(self):

        for e in self.edits:
            self.test_files.add(e.file_name)
        return self.test_files


    def dumpTestFiles(self):


        if self.out_dir is None:
            # no edits corr to this snapshot
            return

        print('>>>> Dumping files in test dir for ' + path_leaf(self.src_path))
        test_dirs = self.out_dir.get_test_dirs()
        #print test_dirs


        for e in self.edits:
            print e
            if e.isbug is 'False':
                '''
                only considering bugfix files for time being
                '''
                print "XXXXXXXXXXXXXXXXXXXXXX"
                continue

            logging.debug(">>>>" , e.file_name, e.sha)

            file_versions = self.git_repo.fetchFiles(e.file_name, e.sha)

            for i, sha in enumerate(file_versions):
                print i, sha
                file_name = e.file_name.replace('/', self.config_info.SEP)
                file_name, extn = os.path.splitext(file_name)
                if extn.lower() not in ['.c', '.cpp', '.cc', '.java']:
                    continue
                file_name = file_name + self.config_info.SEP + e.sha + extn
                dest_file = os.path.join(test_dirs[i], file_name)
                #print file_name, dest_file
                self.git_repo.dumpFile(e.file_name, sha, dest_file)
                
    
    def dumpNonbugfixFiles(self):
        #dumping in change repo


        if self.out_dir is None:
            # no edits corr to this snapshot
            return

        print('>>>> Dumping non bugfix files in change dir for ' + path_leaf(self.src_path))
        change_dirs = self.out_dir.get_change_dir()

        for e in self.edits:

            if e.isbug is "False":
                '''
                only considering bugfix files for time being
                '''
                continue

            logging.debug(">>>>" , e.file_name, e.sha)

            file_versions = self.git_repo.fetchFiles(e.file_name, e.sha)

            for i, sha in enumerate(file_versions):
                print i, sha
                file_name = e.file_name.replace('/', self.config_info.SEP)
                file_name, extn = os.path.splitext(file_name)
                if extn.lower() not in ['.c', '.cpp', '.cc', '.java']:
                    continue
                file_name = file_name + self.config_info.SEP + e.sha + extn
                dest_file = os.path.join(test_dirs[i], file_name)
                #print file_name, dest_file
                self.git_repo.dumpFile(e.file_name, sha, dest_file)


    def getTrainFiles(self):

        return self.train_files


    def dumpTrainFiles(self):

        if self.out_dir is None:
            return

        print('Dumping files in learn and change dirs for ' + path_leaf(self.src_path))
        self.getTestFiles()
        # self.git_repo.git.stash('-u')

        #all files under snapshot except test files
        for root, dirs, files in os.walk(self.src_path):
            for f in files:
                src_file = os.path.join(root, f)
                file_name = src_file.split(self.src_path)#[1].strip(os.sep)

                if len(file_name) < 2:
                    logger.error(file_name)
                    continue

                file_name = file_name[1].strip(os.sep)

                # Condition to filter out all files except C source files. Added on 2014-09-25 1:32PM PDT by Saheel.
                # Changed on 2015-02-01 by Saheel to consider C++ files as well.
                file_name_without_extn, extn = os.path.splitext(file_name)
                if extn.lower() not in ['.c', '.cpp', '.cc', '.java']:
                    continue

                if file_name in self.test_files:
                    dest_file = self.out_dir.changed_dir + os.sep + file_name.replace(os.sep, self.config_info.SEP)
                    shutil.copyfile(src_file, dest_file)
                    continue

                self.train_files.add(file_name)

                dest_file = self.out_dir.learn_dir + os.sep + file_name.replace(os.sep, self.config_info.SEP)
                shutil.copyfile(src_file, dest_file)
