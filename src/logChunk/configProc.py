'''
  Common script to process configuration file
'''


import sys
import os

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'..','util'))

import Util
from Util import ConfigInfo
from Config import Config


def getRepos(repo_config):

  repos = set() 
  
  
  
  try:
    repo_file = repo_config['repo_url_file']
    f = open(repo_file, 'r')
    for line in f:
      repo_url = line.strip()
      _, repo = repo_url.split(os.sep) 
      repos.add(repo)
  except IOError:
    print "!! Repo url file \"%s\" does not exist." % repo_file
    print "... Going to process all the repositories in the directory : \"%s\"." % repo_config['repo_locations']
    repo_file = None
    
  return repos
  

