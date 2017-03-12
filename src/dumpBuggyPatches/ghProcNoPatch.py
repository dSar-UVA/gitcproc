import sys
import re
import os
import ntpath

import csv
from datetime import datetime, timedelta


from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords



from commit import commit
from dumpLogs import dumpLogs

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'..','util'))


import Util
from ConfigInfo import ConfigInfo
from Util import cd



#----------------------------------------------------#

DEL_MIN = 0
DEL_MAX = 3
ADD_MIN = 0
ADD_MAX = 3

delim = '<<|>>'

extn2tag = { '.c' : 'c', \
        '.cpp' : 'cpp', '.cpp_' : 'cpp', '.cpp1' : 'cpp', '.cpp2' : 'cpp', '.cppclean' : 'cpp', '.cpp_NvidiaAPI_sample' : 'cpp', '.cpp-s8inyu' : 'cpp', '.cpp-woains' : 'cpp', \
        '.cs' : 'csharp', '.csharp' : 'csharp',  \
        '.m' : 'objc', \
        '.java' : 'java', \
        '.scala' : 'scala', '.scla' : 'scala', \
        '.go' : 'go', \
        '.javascript' : 'javascript', '.js' : 'javascript', \
        '.coffee' : 'coffeescript', '.coffeescript' : 'coffeescript', \
        '.ts' : 'typescript', '.typescript' : 'typescript', \
        '.rb'  : 'ruby', \
        '.php' : 'php', \
        '.pl' : 'perl', \
        '.py' : 'python', \
        '.sh' : 'shell', '.SH' : 'shell', '.ksh' : 'shell', '.bash' : 'shell', '.bat' : 'shell',  '.bats' : 'shell', \
        '.cljx' : 'clojure', '.cljscm' : 'clojure', '.clj' : 'clojure', '.cljc': 'clojure', '.cljs' : 'clojure', \
        '.css' : 'css', \
        '.erl' : 'erlang', \
        '.hs' : 'haskell'
        }


def toStr(text):
    try:
        text1 = str(text).encode('iso-8859-1')
        temp_text = text1.replace("\'","\"")
        temp_text = temp_text.strip()
        return "\'" + str(temp_text) + "\'"
    except:
        print type(text)
        return "\'NA\'"

#----------------------------------------------------#


lmtzr = WordNetLemmatizer()
stoplist = stopwords.words('english')

def if_bug(text):
    global lmtzr
    global stoplist

    isBug = False

    text = text.lower()

    text = text.replace('error handl','')

    imp_words = [lmtzr.lemmatize(word) for word in text.lower().split() \
            if ((word not in stoplist)) ]
    bug_desc = ' '.join([str(x) for x in imp_words])
    
    found = re.search(Util.ERR_STR, '\b'+bug_desc+'\b', re.IGNORECASE)
    
    if found:
        isBug = True
    

    return isBug

#----------------------------------------------------#

def get_time(commit_date):

    if len(commit_date.strip().rsplit(" ",1)) != 2:
        return ""
    d, t = commit_date.strip().rsplit(" ",1)
    date_object = datetime.strptime(d, '%a %b %d %H:%M:%S %Y')
    h = int(t[1:3])
    m = int(t[4:6])
    if t[0]=='-':
        delta = date_object + timedelta(hours=h, minutes=m)
    else:
        delta = date_object - timedelta(hours=h, minutes=m)

    return str(delta)

#----------------------------------------------------#

class ghProcNoPatch:

    def __init__(self, project, no_merge_log, no_stat_log, 
        config_file, password='', bug_db=None):
     
        self.noMergeLog = no_merge_log
        self.noStatLog = no_stat_log
        self.configInfo = ConfigInfo(config_file) 
        
        self.dbPass = password

        self.project = project
        self.sha2commit = {}

        if self.configInfo.SZZ is False:
            self.extBugDb = None
        else:
            self.extBugDb = self.getExtBugDb(bug_db)
        
        
    def getExtBugDb(self,bug_db):
      
        if not bug_db is None:
            return bug_db
        
        #Following is for D4j
        _ , project_name = ntpath.split(self.project)
        #print ">>>>>> " , project_name
         
        sha_list = {}
        
        config_szz  = self.configInfo.cfg.ConfigSectionMap('Szz')
        d4_sha_file = config_szz['snapshot_sha_file']
        
        with open(d4_sha_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            csvreader.next()
            for row in csvreader:
                bug_no,buggy_sha,bugfix_sha,project = row[:]       
                  
                if project.strip("\"") == project:
                    #print bug_no,buggy_sha,bugfix_sha,project
                    bugfix_sha = bugfix_sha.strip("\"")
                    sha_list[(project,bugfix_sha)] = 'Bug'
        
        return sha_list


    def parse(self, bug_only=False):

        self.parse_no_merge()
        self.parse_no_stat(bug_only)
        self.dump(bug_only)


    def dump(self, bug_only):
      if self.configInfo.CSV:
        self.dump2csv(bug_only)
        self.dumpPatches(bug_only)
        
      if self.configInfo.DATABASE:
        self.dump2db(bug_only)
      
      
    def dumpPatches(self, bug_only=True):
        
        patch_folder = os.path.join(self.project,'patches')
        Util.create_dir(patch_folder)

        for sha, co in self.sha2commit.iteritems():
          if bug_only == False or co.isbug == False:
            continue

          for ch in co.changes:
            insertion, deletion, file_name, language = ch.get()
            
            #print insertion, deletion
            if int(deletion) > DEL_MAX or int(insertion) > ADD_MAX:
              continue
            if int(deletion) == DEL_MIN or int(insertion) == ADD_MIN:
              continue

            fname = file_name.replace(os.sep, self.configInfo.SEP)
            #print fname
            _ , project_name = ntpath.split(self.project)


            patch_name = project_name \
                + self.configInfo.SEP + co.getAuthorDate() \
                + self.configInfo.SEP + fname \
                + self.configInfo.SEP + co.sha \
                + '.patch'


            patch_path = os.path.join('patches', patch_name)
            #out_str = ('git diff -U10 -w %s{\^,} -- %s >%s' % \
            #    (co.sha, file_name, patch_path))
            '''
            out_str = ('git diff -U10 -w %s^ %s -- %s >%s' % \
                (co.sha, co.sha, file_name, patch_path))
            '''

            out_str = ('git diff -U10 -w %s^ %s -- %s' % \
                (co.sha, co.sha, file_name))
            
            with cd(self.project):
              #print self.project
              #print ">>>>>"
              #os.system('pwd')
              print out_str
              #os.system(out_str)
              exitcode, out, err = Util.runCmd(out_str)
              if exitcode != 0:
                print "!!Error Git Diff", err
              else:
                with open(patch_path, 'w') as patch_file:
                    patch_file.write("%s"%out)

            #sys.exit(0)
      
    def dump2csv(self, bug_only):

        if self.configInfo.CSV is False:
            return
            
        out_file = os.path.join(self.project, "FileChanges.csv")
        print out_file
        
        of=open(out_file,'w')
        
        out_str = "project, sha, language, file_name, is_test, committer, commit_date, author, author_date, is_bug, total_add, total_del"
        of.write(out_str + '\n')
        
        for sha, co in self.sha2commit.iteritems():
          for ch in co.changes:
            insertion, deletion, file_name, language = ch.get() 
            if "test" in file_name:
              is_test = "True"
            else:
              is_test = "False"
              
            out_str = (',').join((co.project, co.sha, \
                language, file_name, is_test, \
                co.committer, co.commit_date, co.author, co.author_date, \
                str(co.isbug),insertion,deletion))
            of.write(out_str + '\n')
            
            
    def dump2db(self, bug_only):

        if self.configInfo.DATABASE is False:
            return
            
        dl = dumpLogs(self.dbPass, self.configInfo)
        dl.createFileChangesTable()
        
        for sha, co in self.sha2commit.iteritems():
          for ch in co.changes:
            insertion, deletion, file_name, language = ch.get() 
            if "test" in file_name:
              is_test = "True"
            else:
              is_test = "False"
              
            out_str = (',').join((toStr(co.project), toStr(co.sha), \
                toStr(language), toStr(file_name), toStr(is_test), \
                toStr(co.committer), toStr(co.commit_date), toStr(co.author), toStr(co.author_date), \
                toStr(co.isbug),toStr(insertion),toStr(deletion)))
            dl.dumpFileChanges(out_str)
            
        dl.close()
        

            
        
    


    def dumpLog(self, sha, committer, commit_date, author, author_date, change_files):

        if sha is None:
            return False

        if self.sha2commit.has_key(sha):
            print "!!! sould not have this key"

        project = self.project.split(os.sep)[-1]
        co  = commit(project, sha)
        co.committer = committer
        co.commit_date = commit_date
        co.author = author
        co.author_date = author_date

        for ch in change_files:
            insertion, deletion, file_name = ch[0], ch[1], ch[2]
            lang_extension = os.path.splitext(file_name)[1].strip().lower()
            tag = extn2tag.get(lang_extension, None)

            if not tag is None:
                co.addChange(insertion, deletion, file_name, tag)
                
        self.sha2commit[sha] = co


    def parse_no_merge(self):

        global delim

        sha         = None
        committer   = None
        commit_date = None
        author      = None
        author_date = None
        is_dump = False

        change_files = []

        for line in open(self.noMergeLog, 'r'):

            line = line.strip()

            if line.startswith('>>>>>>>>>>>> '):
                line = line.split('>>>>>>>>>>>> ')[1]

                self.dumpLog(sha, committer, commit_date, author, author_date, change_files)

                del change_files[:]

                line_split = line.split(delim)

                sha, project, committer, commit_date, author, author_date = line_split[0:6]

                sha = sha.strip()

                commit_date = get_time(commit_date)
                author_date = get_time(author_date)

                author = author.decode('ascii', 'ignore').strip()
                committer = committer.decode('ascii', 'ignore').strip()


            elif re.match(r'\d+\t\d+\t', line) and (len(line.split('\t')) == 3):
                insertion, deletion, file_name = line.split('\t')
                extension = os.path.splitext(file_name)[1].strip().lower()
                change_files.append((insertion, deletion, file_name))

            else:
                pass

        self.dumpLog(sha, committer, commit_date, author, author_date, change_files)


    def dumpMssg(self, sha, subject, body, bug_only):

        if sha is None:
            return False
        #print '------\n', subject
        #print body
        co = self.sha2commit.get(sha)
        if co is None:
            print "!!! sould have this sha"
            return

        is_bug = False

        proj  = self.project.split(os.sep)[-1]
        
        issue = None
        
        if not self.extBugDb is None:
          issue = self.extBugDb.get((proj,sha))
          #print ">>>>" , issue, is_bug
          
        if issue == 'Bug':
            #print "XXXXXXXX"
            is_bug = True
        else:
            #print "YYYYYYYYYY"
            is_bug |= if_bug(subject)
            is_bug |= if_bug(body)
            
        
        #print is_bug
        co.subject = subject
        co.body    = body
        co.isbug   = is_bug

        

    def parse_no_stat(self, bug_only):

        global delim

        sha         = None
        subject     = None
        body        = None
        is_dump = False

        change_files = []

        for line in open(self.noStatLog, 'r'):

            line = line.strip()

            if line.startswith('>>>>>>>>>>>> '):
                line = line.split('>>>>>>>>>>>> ')[1]

                self.dumpMssg(sha, subject, body, bug_only)
                #is_dump |= self.dumpLog(sha, committer, commit_date, author, author_date, change_files)

                del change_files[:]

                line_split = line.split(delim)

                sha, project, subject, body = line_split[0:4]

                sha = sha.strip()

                body = body.decode('ascii', 'ignore').strip()

                if 'Signed-off-by:' in body:
                    body = body.partition('Signed-off-by:')[0]

                subject = subject.decode('ascii', 'ignore').strip()
                if 'Signed-off-by:' in subject:
                    subject = subject.partition('Signed-off-by:')[0]

                body = body.decode('ascii', 'ignore').strip()
                subject = subject.decode('ascii', 'ignore').strip()

            else:
                b = line.decode('ascii', 'ignore')
                b = b.rstrip(delim)
                if 'Signed-off-by:' in b:
                    #print "body : " , b.partition('Signed-off-by:')
                    b = b.partition('Signed-off-by:')[0]
                body += " " + b

        self.dumpMssg(sha, subject, body, bug_only)



# ---------------------------------------------------------------- #

def test():
    print "ghProcNoPatch"

    project = "/localtmp/feng/defects4j_origRepos/joda-time"
    no_merge = os.path.join(project,'no_merge_log.txt')
    no_stat = os.path.join(project,'no_stat_log.txt')
    config_file = 'test_conf.ini'
    pl = ghProcNoPatch(project, no_merge, no_stat, config_file)
    pl.parse(False)
    
    

if __name__ == "__main__":
  test()
