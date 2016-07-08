'''
  Common script to process configuration file
'''


import sys
import os
from distutils import util

import Util
from Config import Config

class ConfigInfo:
  
  def __init__(self, newFile):
    self.configFile = newFile
    cfg = Config(self.configFile)
    
    self.config_db    = cfg.ConfigSectionMap("Database")
    self.config_repo  = cfg.ConfigSectionMap("Repos")
    self.config_key   = cfg.ConfigSectionMap("Keywords")
    self.config_log   = cfg.ConfigSectionMap("Log")    
    self.config_flags = cfg.ConfigSectionMap("Flags")
    
    self.setFlags()



  def setFlags(self):
    self.SEP          = self.config_flags['sep']
    self.DEBUG        = bool(util.strtobool(self.config_flags['debug']))
    self.DEBUGLITE    = bool(util.strtobool(self.config_flags['debuglite']))
    self.DATABASE     = bool(util.strtobool(self.config_flags['database']))
    self.CSV          = bool(util.strtobool(self.config_flags['csv']))
    self.LOGTIME      = bool(util.strtobool(self.config_flags['logtime']))
    

  def getRepos(self):

      repos = set() 
  
      try:
        repo_file = self.config_repo['repo_url_file']
        f = open(repo_file, 'r')
        for line in f:
          repo_url = line.strip()
          _, repo = repo_url.split(os.sep) 
          repos.add(repo)
      except IOError:
        print "!! Repo url file \"%s\" does not exist." % repo_file
        print "... Going to process all the repositories in the directory : \"%s\"." % self.getDumpLocation()
        repo_file = None
    
      return repos
  
  def getDumpLocation(self):
    return self.config_repo['repo_locations']
  
  def getPatchMode(self):
      try:
        patch = bool(util.strtobool(self.config_log['patch']))
        
      except:
        patch = True
      return patch
      
  def getLanguages(self):
     try:
       langs = self.config_log['languages'].split(",")
     except:
       langs = [] #Treat empty as showing all supported languages.
     return langs
      
    
    
  

