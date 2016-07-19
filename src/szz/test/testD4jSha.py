import sys
import csv



def testSha(inputProject,d4jShaFile,changeFile):
    
    file_bugfix_edits = set()
    file_nonbugfix_edits = set()
    
    with open(changeFile, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            csvreader.next()
            for row in csvreader:
                project, sha, language, file_name, is_test, committer, \
                commit_date, author, author_date, is_bug, total_add, total_del = row[:]
                #print (',').join((project, file_name, sha, commit_date, is_bug, is_test))
                if project != inputProject:
                    print "!! project %s does not match with input project %s" % (project, inputProject)
                    continue
                #print (',').join((project, file_name, sha, commit_date, is_bug, is_test))
                if is_bug == 'True':
                    file_bugfix_edits.add(sha)
                else:
                    file_nonbugfix_edits.add(sha)
               

    alRight = True
    
    with open(d4jShaFile, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            csvreader.next()
            for row in csvreader:
                bug_no,buggy_sha,bugfix_sha,project = row[:] 
                if project != inputProject:
                    continue     
                if bugfix_sha in file_bugfix_edits:
                    continue
                elif bugfix_sha in file_nonbugfix_edits:
                    print "\t %s not found as bugfix " % bugfix_sha
                    alRight = False
                    #continue
                else:
                    print "\t %s not found " % bugfix_sha
                    alRight = False

    if alRight == True:
      print "Looks Good"
                         
                
    
def projTest():
    
    d4jShaFile = 'C:\\Users\\br8jr\\Repository\\github\\repoMiner\\d4j\\all_common-db.csv'
    for proj in ['closure-compiler','commons-lang','commons-math','jfreechart','joda-time']:
    #for proj in ['jfreechart']:
        print ">>>>>> " , proj
        project = proj
        changeFile = 'C:\\Users\\br8jr\\Repository\\github\\repoMiner\\d4j\\projects\\' + project + '\\FileChanges.csv'
        testSha(project,d4jShaFile,changeFile)
    
def main():
    project    = sys.argv[1]
    d4jShaFile = sys.argv[2]
    changeFile = sys.argv[3] 
    testSha(project,d4jShaFile,changeFile)

if __name__ == "__main__":
    
    #main()
    projTest()


