#----------------------------------------------------------------------------------
import os, sys, shutil
from shlex import split as format_cmd
from subprocess import Popen, PIPE, STDOUT, call
import argparse
import getpass

from os.path import dirname
sys.path.append(os.path.join(dirname(__file__),'..','util'))

import Util
from ConfigInfo import ConfigInfo


#----------------------------------------------------------------------------------
def printPopenOutput(process):
    stdout, stderr = process.communicate()
    if stdout:
        sys.stdout.write(stdout)

    if stderr:
        sys.stderr.write(stderr)

#----------------------------------------------------------------------------------
def printUsage():
    '''
    Usage: python main.py <path_to_output_data_dir> 
                      <project_name> 
                      <github_clone_url> 
                      <project_language>
                      <interval_between_ss_in_months> 
                      <num_of_parallel_cores>
                      [--steps <N1> <N2> <N3>...]

    If the optional `--steps` arg is provided, the numbers after `--steps` indicate steps that will be executed.
    If `--steps` is not provided, all the steps will be executed. Your options for those numbers are:
    
    2. Dump the snapshots (aka snapshot data)
    3. Dump the history of all commit changes (aka changes or corpus data)
    4. Get list of bug-fixing commits from PostgreSQL
    5. Generate bug data (SZZ)
    6. Dump the CSV files with bug data into PostgreSQL tables
    
        
    For example: python main.py data/ libgit2 https://github.com/libgit2/libgit2.git c 3 16 --steps 1 2 3 4 5
    Above command will generate CSV files with bug data for the libgit2 project.

    Another example: python main.py data/ bitcoin https://github.com/bitcoin/bitcoin.git cpp 3 16 --steps 5 6 7 8
    Above command will generate CSV files with bug data, CSV files with type data, dump all of them in PostgreSQL, and merge the dumped tables. 
    It will NOT modify the snapshots and history of commit changes

    Read README.md to know the formats of all the generated CSV files and PostgreSQL tables.
    '''
    print(printUsage.__doc__)
    
#----------------------------------------------------------------------------------
def downloadSnapshot(snapshotDir, projectDir, projectName):

  # 2. Dump the snapshots for a project
  msg =  '---------------------------------------------------- \n'
  msg += ' Dump the snapshots for project %s \n' % projectName
  msg += '---------------------------------------------------- \n'
  print(msg)
           
  project_snapshot_dir = os.path.join(snapshotDir, projectName)
  project_cur_clone = os.path.join(projectDir, projectName)
  
  if os.path.isdir(project_snapshot_dir):
    print "!! %s already exists...going to delete it \n" % project_snapshot_dir
    call(format_cmd("rm -rf " + project_snapshot_dir))
  
  cmd = format_cmd('python generate_snapshot_data/dump.py -p ' + project_cur_clone + ' -v d -d ' + snapshotDir + ' --conf src/generate_snapshot_data/config.ini -l java -m 3')# + LANGUAGE + ' -m ' + str(INTERVAL))
  print cmd
  call(cmd)


   
def downloadSnapshots(config_info):
  
  repo_config = config_info.config_repo
  
  #Check that the repo list file exists
  if(not os.path.isfile(repo_config['repo_url_file'])):
    print(repo_config['repo_url_file'] + ", the file containing the list of projects to download,")
    print("cannot be found.  Make sure your path and name are correct.")
    return

  #Create the output directory if it doesn't exist yet.
  project_dir = repo_config['repo_locations']
  if(not os.path.isdir(project_dir)):
    print(project_dir + " is not found")
    print("Please give a valid directory containing the projects")
    print("Use repoMiner -dl to download projects")
    return
      
      
  snapshot_dir = repo_config['snapshot_locations']
  if(not os.path.isdir(snapshot_dir)):
    call(format_cmd('mkdir ' + snapshot_dir))
      
  repos = config_info.getRepos()
  for r in repos:
    print r
    downloadSnapshot(snapshot_dir, project_dir, r)
    


#----------------------------------------------------------------------------------
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("config_file", help = "This is the path to your configuration file.")
  parser.add_argument("-s","--snapshots", action="store_true", help = "Flag that indicates you want to download the snapshots.")
  
  args = parser.parse_args()
  
  config_file = args.config_file
  config_info = ConfigInfo(config_file)  
  
  if(config_info.DATABASE): #If we have database output selected and are performing the parse-log step.
    password = getpass.getpass(prompt="Database option selected, enter your password:")
  else:
    password = ""

  
  if(args.snapshots):
    downloadSnapshots(config_info)
    
      
  
     

  if False:
      if len(sys.argv) == 7:
          all_steps = True
          options = []
      elif len(sys.argv) < 7:
          printUsage()
          raise ValueError('7 or more args expected. ' + str(len(sys.argv) - 1) + ' given.')
      elif len(sys.argv) > 7 and not sys.argv[7] == '--steps':
          printUsage()
          raise ValueError('Expected arg `--steps` not given.')
      else:
          all_steps = False
          options = sys.argv[8:]
          for option in options:
              if not option.isdigit():
                  printUsage()
                  raise ValueError('Args after `--steps` must be numeric. Please try again.')
  
      data_root_path = os.path.abspath(sys.argv[1])
      if not os.path.isdir(data_root_path):
          os.mkdir(data_root_path)
      project_name = sys.argv[2]
      git_url = sys.argv[3]
      language = sys.argv[4]
      num_of_intervals = sys.argv[5]
      num_of_cores = sys.argv[6]
  
      # Relevant directories to store our data
      projects_dir = data_root_path + '/projects/'
      project_dir = projects_dir + project_name + '/'
  
      ss_dir = data_root_path + '/snapshots/'
      project_ss_dir = ss_dir + project_name + '/'
  
      #ss_c_cpp_dir = data_root_path + '/snapshots_c_cpp/'
      #project_ss_c_cpp_dir = ss_c_cpp_dir + project_name + '/'
  
      #ss_srcml_dir = data_root_path + '/snapshots_srcml/'
      #project_ss_srcml_dir = ss_srcml_dir + project_name + '/'
  
      corpus_dir = data_root_path + '/corpus/'
      project_corpus_dir = corpus_dir + project_name + '/'
  
      bf_shas_dir = data_root_path + '/bf_shas/'
      project_bf_shas_file_path = bf_shas_dir + project_name
      
      '''
      entropy_results_dir = data_root_path + '/entropy_results/'
      project_entropy_results_dir = entropy_results_dir + project_name + '/'
  
      ast_node_bugginess_results_dir = data_root_path + '/ast_node_bugginess_results/'
      '''
  
      # TODO parse output of each command for error string
  
  #----------------------------------------------------------------------------------
      if '1' in options or all_steps:
          # 1. Clone the latest version of given project
          msg = '---------------------------------------------------- '
          msg += '1. Clone the latest version of given project '
          msg += '----------------------------------------------------\n'
          print(msg)
  
          cmd = format_cmd('mkdir -p ' + projects_dir)
          call(cmd)
      
          cmd = format_cmd('rm -rf ' + project_dir)
          call(cmd)
      
          cmd = format_cmd('mkdir -p ' + project_dir)
          call(cmd)
      
          cmd = format_cmd('git clone ' + git_url + ' ' + project_dir)
          call(cmd)
      
  #----------------------------------------------------------------------------------
      if '2' in options or all_steps:
          # 2. Dump the snapshots
          msg = '---------------------------------------------------- '
          msg += '2. Dump the snapshots '
          msg += '----------------------------------------------------'
          print(msg)
                  
          cmd = format_cmd('python generate_snapshot_data/get_snapshot_data.py ' + data_root_path + ' ' + language + ' ' \
                            + project_name + ' dump ' + num_of_intervals)
                            
          print cmd
          call(cmd)
  
  #----------------------------------------------------------------------------------
      if '3' in options or all_steps:
          # 3. Dump the history of all commit changes
          msg = '---------------------------------------------------- '
          msg += '3. Dump the history of all commit changes '
          msg += '----------------------------------------------------'
          print(msg)
  
          cmd = format_cmd('python generate_snapshot_data/get_snapshot_data.py ' + data_root_path + ' ' + language + ' ' \
                            + project_name + ' run ' + num_of_intervals)
          call(cmd)
  
  #----------------------------------------------------------------------------------
      if '4' in options or all_steps:
          # 4. Get list of bug-fixing commits from PostgreSQL
          msg = '---------------------------------------------------- '
          msg += '4. Get list of bug-fixing commits from PostgreSQL '
          msg += '----------------------------------------------------'
          print(msg)
  
          cmd = format_cmd('mkdir -p ' + bf_shas_dir)
          call(cmd)
      
          cmd = format_cmd('python szz/get_list_of_bugfix_SHAs.py ' + project_name + ' ' \
                            + project_bf_shas_file_path)
          call(cmd)
      
  #----------------------------------------------------------------------------------
      if '5' in options or all_steps:
          # 5. Run SZZ
          msg = '---------------------------------------------------- '
          msg += '5. Run SZZ to get bug data '
          msg += '----------------------------------------------------'
          print(msg)
  
          cmd = format_cmd('python szz/szz.py ' + project_corpus_dir + ' ' \
                            + project_ss_dir + ' ' + project_bf_shas_file_path + ' ' + num_of_cores)
          call(cmd)
      
  #----------------------------------------------------------------------------------
      if '6' in options or all_steps:
          # 6. Dump the CSV files with bug data into PostgreSQL tables
          msg = '---------------------------------------------------- '
          msg += '6. Dump the CSV files with bug data into PostgreSQL tables '
          msg += '----------------------------------------------------'
          print(msg)
  
          cmd = format_cmd('python szz/dump_bugdata_into_psql_table.py '
                            + data_root_path + ' ' + project_name)
          call(cmd)
          
  #----------------------------------------------------------------------------------
      msg = '---------------------------------------------------- '
      msg += 'main.py DONE for ' + project_name + ' '
      msg += '----------------------------------------------------'
      print(msg)
    
 
if __name__ == '__main__':
  main()
