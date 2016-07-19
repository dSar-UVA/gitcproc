'''
  Common script to process configuration file
'''


import sys
import os
from distutils import util

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'..','util'))

#import Util
from ConfigInfo import ConfigInfo


class ConfigInfoSZZ(ConfigInfo):
    
    def __init__(self, newFile):
        ConfigInfo.__init__(self, newFile)    
        self.config_szz    = self.cfg.ConfigSectionMap('SZZ')
        
    def getSnapshotInterval(self):
        
        self.interval_option = bool(util.strtobool(self.config_szz['interval_option']))
        self.snapshot_interval = int(self.config_szz['snapshot_interval'])
            
        return (self.interval_option,self.snapshot_interval)
    
    def getShaFiles(self):
        self.snapshot_sha_files = self.config_szz['snapshot_sha_file']
        return self.snapshot_sha_files
    
    def getCorpusLocation(self):
        self.corpus_locations = self.config_szz['corpus_locations']
        return self.corpus_locations
    
    def getSnapshotLocation(self):
        self.snapshot_locations = self.config_szz['snapshot_locations']
        return self.snapshot_locations
    
    def getProjectCorpus(self, projName):
        return os.path.join(self.getCorpusLocation(),projName)
    
    def getProjectSnapshot(self, projName):
        return os.path.join(self.getSnapshotLocation(),projName)


      
    
    
  

