import os
import sys
import os.path
import errno
import shutil

from distutils import util
from Config import Config


supportedLanguages = ["C", "C++", "Java", "Python"]

import shlex
from subprocess import Popen, PIPE

def runCmd(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)

    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode
    #
    return exitcode, out, err

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)



#Generic create directory function
def create_dir(path):

    try:
        print path
        os.makedirs(path)
    
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    
def copy_dir(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: 
            raise

def cleanup(path):

    if os.path.isdir(path):
        print "!!! Cleaning up " , path
        shutil.rmtree(path)        
    elif os.path.isfile(path):
        print "!!! Removing " , path
        os.remove(path)
        
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

all_extension = ['.c', '.cc', '.cpp', '.c++', '.cp', '.cxx', '.h', '.ic', \
#                 '.cpp_' , '.cpp1' , '.cpp2' , '.cppclean' , \
#                 '.cpp_NvidiaAPI_sample' , '.cpp-s8inyu' , '.cpp-woains' , \
                 '.cs' , '.csharp' , '.m' , \
                 '.java' , '.scala' , '.scla' , \
                 '.go' , '.javascript' , '.js' , '.coffee' , '.coffeescript' , \
                 '.rb'  , '.php' , '.pl' ,  '.py' , \
                 '.cljx' , '.cljscm' , '.clj' , '.cljc' , '.cljs' , \
                 '.erl' , '.hs' ]

#cpp_extension = [ '.c', '.cc', '.cpp', '.c++', '.cp', '.cxx', '.h', '.ic']
cpp_extension = [ '.c', '.cc', '.cpp', '.c++', '.cp', '.cxx']


ERR_STR  = '\\berror\\b|\\bbug\\b|\\bfix\\b|\\bfixing\\b|\\bfixups\\b|\\bfixed\\b|\\bissue\\b|\\bmistake\\b|\\bblunder\\b|' \
            + '\\bincorrect\\b|\\bfault\\b|\\bdefect\\b|\\bflaw\\b|\\bglitch\\b|\\bgremlin\\b|\\btypo\\b|\\berroneous\\b|'\
            + '\\bcorrect\\b|\\bcorrectly\\b|'
            
            
