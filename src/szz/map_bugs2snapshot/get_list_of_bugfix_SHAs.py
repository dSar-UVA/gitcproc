"""
Contains the extractBugfixSHAs() function (see its doc) that fetchs you the list of bugfix SHAs for a given project.
"""
#----------------------------------------------------------------------------------
import os, sys, psycopg2
#----------------------------------------------------------------------------------
def extractBugfixSHAs(project_name, output_file_path):
    """
    Queries the `err_corr_c.all_changes` table in the database `saheel` on `godot` and returns the list of bugfix SHAs for the given project `project_name`
    
    Args
    ----
    project_name: string
        Name of the project for which bugfix SHAs have to be extracted from the database
    output_file_path: string
        Name of the file to which the retrieved bugfix SHAs will be written to
        
    Raises
    ------
    Exception
        When the PostgreSQL query fails or writing to file fails
    """
    con = None
    try:
        con = psycopg2.connect(database='baishakhi', user='bairay')
        cur = con.cursor()
        cur.execute("SELECT sha FROM err_corr_july_2015.all_changes_tmp WHERE project='" + project_name + "' AND isbug='t'")
        shas =  set([sha[0] for sha in cur.fetchall()])

        with open(output_file_path, 'w') as output_file:
            for sha in shas:
                output_file.write(sha + '\n')
        
    except Exception, e:
        sys.stderr.out("Error in fetching bugfix SHAs! Please check whether data exists in `err_corr_july_2015.all_changes_tmp` for `" + project_name + "`")
        if con:
            con.rollback()

        raise

#----------------------------------------------------------------------------------
if __name__ == "__main__":
    
    if len(sys.argv) != 1:
        sys.stderr.write('\nPlease provide valid configuration file.\nUsage: python get_list_of_bugfix_SHAs.py config_file\n\n')
        return
    else:
        
        extractBugfixSHAs(sys.argv[1], sys.argv[2])
        print("Bugfix SHAs written to " + sys.argv[2] + " successfully.")

#----------------------------------------------------------------------------------
