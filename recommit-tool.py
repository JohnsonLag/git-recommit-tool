import sys
import subprocess
import os
import io
import re

def switch_to_backup_branch():
    print("\nCreating a new branch and switching to it...")
    my_command = "git branch --show-current"
    old_branch_name = subprocess.run(my_command, capture_output=True, text=True).stdout.split("\n")[0]
    
    new_branch_name = "recommit-" + old_branch_name
    my_command = "git checkout -b "+new_branch_name
    subprocess.run(my_command)
    
def get_exclude_files(exclude_file = "recommit-exclude.txt"):
    exclude_set = set([])
    
    print("\nGetting list of files to exclude from recommits...")
    with open(exclude_file, 'r', encoding='utf-8') as efile:
        for line in efile:
            exclude_set.add(line.removesuffix('\n'))
    
    return exclude_set

def get_all_previous_committed_files():
    file_regex = r'^(\s)*((\S)*/){0,}((\S)*\.(\S)*){1,}[ ]{1,}(.){0,}(|){1,}'
    
    print("\nGetting list of all files from the most recent commit...")
    log_output_file = "git-log-output.txt"
    initial_set = set([])
    
    my_command = "git log --compact-summary -1"
    log_output = subprocess.run(my_command, capture_output=True, encoding="utf-8").stdout

    with open(log_output_file, 'w', encoding='utf-8') as lofile:
        lofile.write(log_output)
        
    # Build array of files to recommit.
    with open(log_output_file, 'r', encoding='utf-8') as lofile:
        lofile.seek(0, os.SEEK_SET)
        for line in lofile:
            match = re.search(file_regex, line)
            if match:
                print(match.groups())
                
                if type(match.group(2)) == type(None):
                    file_name = match.group(4)
                else:
                    file_name = match.group(2)+match.group(4)
                
                initial_set.add(file_name)

    return initial_set

def do_intermediate_commit(exclude_set, recommit_set):
    file_regex = r'^(\s)*((\S)*/){0,}((\S)*\.(\S)*){1}'
    
    for rm_file in exclude_set:
        match = re.search(file_regex, rm_file)
        if match:
            print(match.groups())
            
            if type(match.group(2)) == type(None):
                    file_name = match.group(4)
            else:
                file_name = match.group(2)+match.group(4)
                    
            recommit_copy_file_name = match.group(2)+"recommit-copy-"+match.group(4)
            my_command = "cp "+rm_file+" "+recommit_copy_file_name
            subprocess.run(my_command)
            my_command = "git rm "+rm_file
            subprocess.run(my_command)
    
    for recommit_file in recommit_set:
        with open(recommit_file, 'r+', encoding='utf-8') as rfile:
            rfile.seek(0, os.SEEK_END)
            rfile.write('\n')
    
    my_command = "git add -u"
    subprocess.run(my_command)
    my_command = 'git commit -m "Intermediate commit by recommit tool'
    subprocess.run(my_command)
    
def do_final_commit():
    # Restore the files.
    my_command = "git restore -s HEAD~1 *"
    subprocess.run(my_command)
    
    my_command = "git add -u"
    subprocess.run(my_command)
    my_command = 'git commit -m "Final commit by recommit tool'
    subprocess.run(my_command)

def main():
    print("Starting recommit tool...")
    
    switch_to_backup_branch()
    input("\nDone switching branches. Enter any character to continue: ")
    
    exclude_file = sys.argv[1]
    
    exclude_set = get_exclude_files(exclude_file)
    if len(exclude_set) == 0:
        print("\nNo files found to exclude. Ending program.")
    
    initial_set = get_all_previous_committed_files()
    
    recommit_set = initial_set.difference(exclude_set)
    
    input("\nDone excluding files. Enter any character to continue: ")
    
    set_list = [initial_set, exclude_set, recommit_set]
    
    print("\nall files committed in the most recent commit:")
    
    for file in set_list[0]:
        print(file)
        
    print("\nexclude these files:")
    
    for file in set_list[1]:
        print(file)
        
    print("\nfinal set:")
    
    for file in set_list[2]:
        print(file)
    
    input("Done creating final set. Enter any character to continue: ")
    
    do_intermediate_commit(exclude_set, recommit_set)
    input("Done with intermediate commit. Enter any character to continue: ")
    do_final_commit()
    input("Done with final commit. Enter any character to continue: ")
    
if __name__ == "__main__":
    main()

