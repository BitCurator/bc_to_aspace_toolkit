#!/usr/bin/python
# coding=UTF-8
#
# utilities.py
# 
# This code is distributed under the terms of the GNU General Public 
# License, Version 3. See the text file "COPYING" for further details 
# about the terms of this license.
#
# Support utilities for bc_to_aspace_toolkit
# 

import os
import sys
import pkg_resources

def ask_user(question):
    while "Please enter y or n":
        if sys.version_info[0] < 3:
            reply = str(raw_input(question+' [y/N]: ')).lower().strip()
        else:
            reply = str(input(question+' [y/N]: ')).lower().strip()
        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False

def get_dir_paths(dir_path, exclude=['__pycache__']):
    """
    Get paths of the first-level folders existed in a given folder

    Args:
        dir_path (str): the path of the given folders;
        exclude (array): the folders don't want to be retrieved;
    Returns:
        type: folder paths (array).
    """
    dir_names = [dirs for root, dirs, files in os.walk(dir_path)][0]
    results = []
    for dir in dir_names:
        if dir not in exclude:
            path = dir_path + '/' + dir
            if len(os.listdir(path)) > 0:
                results.append(path)
    return results

def check_repo_structure(repo_dir):
    print()
    print("  [INFO] Found repository structure directory {}".format(repo_dir))
    print("  [INFO] Looking for project directories...")
    print()
    project_dirs = get_dir_paths(repo_dir)
    if len(project_dirs) == 0:
        print("  [ABORT] No project directories found!")
        exit(1)
    else:
        for project_dir in project_dirs:
            print("  [INFO] - Found project directory {}".format(project_dir))
            metadata_dirs = get_dir_paths(project_dir)
            if len(metadata_dirs) == 0:
                print("  [ABORT] No metadata directories found in project directory {}!".format(project_dir))
                exit(1)
            else:
                for metadata_dir in metadata_dirs:
                    print("  [INFO] -- with metadata directory {}".format(metadata_dir))
            print()
    user_response = ask_user("Is this the correct set of directories?")
    if user_response == False:
       print("  [ABORT] Please check the directory structure and try again.")
       exit(1)
    else:
       print("  [INFO] Ok, continuing...")
       print()


def get_json_template(template_name):
    resource_package = "bc_to_aspace_toolkit"  # Exact package name here
    resource_path = '/'.join(('json_templates', template_name))  # Do not use os.path.join()
    # Read template as file-like stream:
    template = pkg_resources.resource_stream(resource_package, resource_path)
    return template
