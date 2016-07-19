#!/usr/bin/python

import argparse
import os, sys, inspect
import os.path
import shutil
import logging
import datetime
import csv



from DbEdits import DbEdits
from DbEdits import edit
from GitRepo import GitRepo
from OutDir import OutDir
from SnapShot import SnapShot

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'../../','util'))
sys.path.append(os.path.join(dirname(__file__),'..','changes'))
sys.path.append(os.path.join(dirname(__file__),'..','.'))

#from OutDir import OutDir
from ConfigInfoSZZ import ConfigInfoSZZ
import Log
from Util import cd
import Util



class Corpus:

    def __init__(self, projectPath, language, outDir, configInfo, debug=True):

        self.src_path = projectPath
        self.language = language
        self.out_path = outDir
        self.cfg_info = configInfo
        self.debug    = debug

        proj_path = self.src_path.rstrip(os.sep)
        self.project_name = proj_path.split(os.sep)[-1]
        logging.info("project = %s\n", self.project_name)

        self.snapshots = []
        self.changed_files_per_date = {} #commit_date -> set(file_name)
        self.edit_to_snapshot = {}
        self.snapshot2edit = {}
        self.initEdits()
        self.initSnapshots()

    def __str__(self):
        retStr = "project : " + self.project_name + "\n"
        retStr += "SnapShots : \n"

        for s in self.snapshots:
            retStr += str(s) + " "

        return retStr

    def printSnapshots(self):

        for s in self.snapshots:
            print s

    def initEdits(self):

        if self.cfg_info.DATABASE == True:
            self.edits = self.fetchEdits()
        else:
            self.edits = self.fetchEditsFromCsv()


    def fetchEditsFromCsv(self):
        print "fetchEditsFromCsv"
        proj_loc = self.cfg_info.getProjectLocation(self.project_name)
        change_db_csv = os.path.join(proj_loc,'FileChanges.csv')
        if not os.path.isfile(change_db_csv):
            print "!!! %s does not exist, first dump the changes" % (change_db_csv)
        else:
            print "Going to process change db: %s" % (change_db_csv)

        csv_edits = []
        with open(change_db_csv, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            csvreader.next()
            for row in csvreader:
                project, sha, language, file_name, is_test, committer, \
                commit_date, author, author_date, is_bug, total_add, total_del = row[:]
                #print (',').join((project, file_name, sha, commit_date, is_bug, is_test))
                e = edit(project, file_name, is_test, sha, commit_date, is_bug)
                csv_edits.append(e)

        return csv_edits


    def fetchEdits(self):

        logging.info("Going to fetch edits for project : %s", self.project_name)
        
        db_config = self.cfg_info.config_db

        logging.debug("Database configuration = %r\n", self.cfg_info.config_db)

        db_edits = DbEdits(self.project_name, self.language)
        db_edits.connectDb(db_config['database'], db_config['user'], db_config['host'], db_config['port'])
        db_edits.fetchEditsFromTable(db_config['table'])

        #logging.debug(db_edits)

        return db_edits.edits

    @staticmethod
    def minKey(commitDate, snapshotDate):

        if commitDate >= snapshotDate:
            return (commitDate - snapshotDate).days
        else:
            return 9999

    def mapEditToSnapshot(self):

        for e in self.edits:
            cd = e.commit_date
            cd = cd.split(" ")[0]

            cd = datetime.datetime.strptime(cd, '%Y-%m-%d').date()

            #snap = min(self.snapshots, key=lambda sd : self.minKey(cd,sd))
            snap = min(self.date2snapshot.keys(), key=lambda sd: self.minKey(cd, sd))
            if cd < snap:
                logging.info("!!! skipping: commit_date %s: snapshot %s" % (cd, snap))
                continue

            self.edit_to_snapshot[e] = snap

            for s in self.date2snapshot[snap]:
                s.addEdit(e)

        for s in self.snapshots:

            #print "%s:%s" % (s.name, s.date)
            edit_dates = set()
            for e in s.edits:
                td =  "%s" % e.commit_date
                edit_dates.add(td.split(" ")[0])

            #print edit_dates
            edit_dates = sorted(edit_dates)
            edit_str = (",".join(edit_dates))
            #print "\t", edit_str


    def initSnapshots(self):

        snaps = [snap for snap in os.listdir(self.src_path)]
        # 'ss_sha_info.txt' is not a snapshot directory, hence can be removed
        # ...it actually contains some metadata about the commit SHAs of each snapshot
        # ...which is used by `src/generate_asts_and_type_data/gather_typedata_into_csv.py`
        #snaps.remove('ss_sha_info.txt')

        snaps.sort()
       
      
        self.date2snapshot = {}

        for snap in snaps:
            
            s = SnapShot(self.src_path, snap, self.out_path, self.cfg_info)
           
            if not self.date2snapshot.has_key(s.date):
                self.date2snapshot[s.date] = []

            self.date2snapshot[s.date].append(s)
            self.snapshots.append(s)

        self.mapEditToSnapshot()
        
       


    def dump(self):

        temp_path = os.path.join(self.out_path, '*')
        Util.cleanup(temp_path)

        for snap in self.snapshots:
            snap.dumpTestFiles()
            '''
            For bugfix model, I think the training data will be at snapshot
            So no need to dump the training data?
            '''
            
            snap.dumpTrainFiles()
