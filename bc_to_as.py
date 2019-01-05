#!/usr/bin/python
# coding=UTF-8
#
# bc_to_as.py
# 
# This code is distributed under the terms of the GNU General Public 
# License, Version 3. See the text file "COPYING" for further details 
# about the terms of this license.
#
# This python script prepares metadata produced by the Brunnhilde tool
# for import into ArchivesSpace, and uses the ArchivesSpace API to perform
# the import.
# 

from pathlib import Path
import getpass
import datetime
import sys

try:
    from argparse import ArgumentParser
except ImportError:
    raise ImportError("This script requires ArgumentParser (Python 2.7/3.x)")


def get_dir_names(dir_path, exclude=['__pycache__', 'json_templates']):
    """
    Get names of the first-level folders existed in a given folder

    Args:
        dir_path (str): the path of the given folders;
        exclude (array): the folders don't want to be retrieved;
    Returns:
        type: folder names (array).
    """
    import os
    dir_names = [dirs for root, dirs, files in os.walk(dir_path)][0]
    results = []
    for dir in dir_names:
        if dir not in exclude:
            path = dir_path + '/' + dir
            if len(os.listdir(path)) > 0:
                results.append(dir)
    return results


def create_json_file(template_name, dir_path):
    """
    Create a json file using existing json templates

    Args:
        template_name (string): the name of the json template
        dir_path (string): the path of the folder with json templates

    Returns:
        type: a json file
    """
    import json
    template_path = dir_path + '/json_templates/' + template_name + '.json'
    with open(template_path) as f:
        template = json.load(f)
    return template


def load_dataset(file_name, dir_path):
    """
    load dataset

    Args:
        file_name (string): file name;
        dir_path (string): the path of the folder with datasets

    Returns:
        type: dataset(pandas dataframe)
    """
    import pandas as pd
    import os
    dataset_path = dir_path + '/' + file_name + '.csv'
    if os.path.isfile(dataset_path):
        dataset = pd.read_csv(dataset_path)
        return dataset


def extract_date(time):
    """
    extract '%Y-%m-%d' from datetime data

    Args:
        time (string): datetime

    Returns:
        type: extracted date (datetime object)
    """
    import re
    import datetime
    match = re.search('\d{4}-\d{2}-\d{2}', time)
    date_extracted = datetime.datetime.strptime(
        match.group(), '%Y-%m-%d').date()
    return date_extracted


def get_sessionId(host, username, password):
    """
    Get session id from ArchivesSpace backend

    Args:
        host (string): API URL
        username (string): username of your ArchivesSpace account
        password (string): password of your ArchivesSpace account

    Returns:
        type : session id(string)
    """
    import requests
    import json
    url = host + '/users/' + username + '/login'
    params = {
        'password': password
    }
    authentication = requests.post(url, params=params).json()
    return authentication['session']


def call_archivesspace_api(host, session_id, action, api, data=""):
    """
    call ArchivesSpace api

    Args:
        host (string): api URL
        session_id (string): session id retreived from ArchivesSpace backend
        action (string): api action ("post" or "get")

    Returns:
        type: json file (json)

    Raises:
        Exception: error code
    """
    import requests
    import json
    url = host + api
    headers = {
        'X-ArchivesSpace-Session': session_id
    }

    if action == "post":
        result = requests.post(url, headers=headers,
                               data=json.dumps(data)).json()
        return result
    elif action == 'get':
        result = requests.get(url, headers=headers).json()
        return result
    else:
        print('Please specify API action: "post" or "get"')


def get_archival_object(ref_id, repository_uri, session_id, host):
    """
    Get a archival object in ArchivesSpace repository using a given ref_id

    Args:
        repository_uri (string): the URI of the respiratory that will be retrieved from
        ref_id (string): a given id used to search for archival objects in the repository
        session_id (string): session_id
        host (string): API URL

    Returns:
        type: return an archival object if ref_id exists in the repository;
            otherwise, return ""
    """
    archival_object_output = ''
    check_ref_id_api = repository_uri + '/archival_objects?all_ids=true'
    archival_object_ids = call_archivesspace_api(
        host, session_id, 'get', check_ref_id_api)
    if len(archival_object_ids) > 0:
        for id in archival_object_ids:
            archival_object_api = repository_uri + \
                '/archival_objects/' + str(id)
            archival_object = call_archivesspace_api(
                host, session_id, 'get', archival_object_api)
            if archival_object['ref_id'] == str(ref_id):
                archival_object_output = archival_object
    return archival_object_output


def get_repository_uri(repo_code, session_id, host):
    """
    Get a repository uri in ArchivesSpace database using a given repo_code

    Args:
        repo_code (string): a given id used to search for repositories in database
        session_id (string): session_id
        host (string): api URL

    Returns:
        type: return a repository URI if repo_code exists in the database;
            otherwise, return ""
    """
    repository_list = call_archivesspace_api(
        host, session_id, 'get', '/repositories')
    repository_uri = ''
    for repository in repository_list:
        if repository['repo_code'] == repo_code:
            repository_uri = repository['uri']
    return repository_uri


#################################################################

def run_session(dir_path):

    if sys.version_info[0] < 3:
        host = raw_input('ASpace backend URL: ')
        username = raw_input('Username: ')
        password = getpass.getpass(prompt='Password: ')
        created_by = raw_input('Created by: ')
    else:
        host = input('ASpace backend URL: ')
        username = input('Username: ')
        password = getpass.getpass(prompt='Password: ')
        created_by = input('Created by: ')

    # retrieve session id
    try:
        session_id = get_sessionId(host, username, password)
        print("Connected to ASpace backend!")
    except:
        sys.exit("Oops! the username or password was incorrect.  Try again...")

    # For each repository folder in the home diretory (dir_path)
    #     Search for a repository using the name of the repository folder;
    #     If this repository does not exist, create one using
    #         the name of this repository folder as a repo_code.
    for repository_folder in get_dir_names(dir_path):
        repository_uri = get_repository_uri(repository_folder, session_id, host)

        if repository_uri == '':
            repository = create_json_file('create_repositories', dir_path)
            repository['create_time'] = datetime.datetime.now().strftime(
                '%Y-%m-%d')
            repository['created_by'] = created_by
            repository['name'] = repository_folder
            repository['repo_code'] = repository_folder
            repository['system_mtime'] = datetime.datetime.now().strftime(
                '%Y-%m-%dT%H:%M:%SZ')
            repository_uri = call_archivesspace_api(
                host, session_id, 'post', '/repositories', repository)['uri']

        # Find the path of the preject folders in the repository folder.
        project_folder_paths = dir_path + '/' + repository_folder

        # For each project folder in the repository folder:
        #     Search for a parent archive object using the name of the project folder;
        #     If this parent archival object does not exist, create one using
        #         the name of the project folder as a ref_id.
        #     If this parent archival object exists, but its resouce is missing, create
        #     a new resource.
        for project_folder in get_dir_names(project_folder_paths):
            ref_id_parent = project_folder

            parent_archival_object = get_archival_object(
                ref_id_parent, repository_uri, session_id, host)

            if parent_archival_object != '':
                parent_resource_uri = parent_archival_object['resource']['ref']
                parent_archival_object_uri = parent_archival_object['uri']
            else:
                parent_resource_uri = ''
                parent_archival_object_uri = ''

            if parent_archival_object_uri == '':
                parent_resource = create_json_file('create_resources', dir_path)
                parent_resource['id_0'] = project_folder
                parent_resource['dates'][0]['begin'] = datetime.datetime.now().strftime(
                    '%Y-%m-%d')
                parent_resource['dates'][0]['end'] = datetime.datetime.now().strftime(
                    '%Y-%m-%d')
                parent_resource['extents'][0]['number'] = 'Unknown'
                parent_resource['notes'] = []
                parent_resource['level'] = 'file'
                parent_resource['title'] = project_folder
                resource_api = repository_uri + '/resources'
                parent_resource_uri = call_archivesspace_api(
                    host, session_id, 'post', resource_api, parent_resource)['uri']

                parent_object = create_json_file(
                    'create_archival_objects', dir_path)
                parent_object['title'] = project_folder
                parent_object['level'] = 'file'
                parent_object['ref_id'] = project_folder
                parent_object['resource']['ref'] = parent_resource_uri
                parent_object['dates'] = []
                parent_object['extents'] = []
                parent_object['notes'] = []
                parent_object_api = repository_uri + '/archival_objects'
                parent_archival_object_uri = call_archivesspace_api(
                    host, session_id, 'post', parent_object_api, parent_object)['uri']
            else:
                if parent_resource_uri == '':
                    parent_resource = create_json_file(
                        'create_resources', dir_path)
                    parent_resource['id_0'] = project_folder
                    parent_resource['dates'][0]['begin'] = datetime.datetime.now().strftime(
                        '%Y-%m-%d')
                    parent_resource['dates'][0]['end'] = datetime.datetime.now().strftime(
                        '%Y-%m-%d')
                    parent_resource['extents'][0]['number'] = 'Unknown'
                    parent_resource['notes'] = []
                    parent_resource['level'] = 'file'
                    parent_resource['title'] = project_folder
                    resource_api = repository_uri + '/resources'
                    parent_resource_uri = call_archivesspace_api(
                        host, session_id, 'post', resource_api, parent_resource)['uri']

            # Find the path of the files in the project folder
            file_folder_path = project_folder_paths + '/' + project_folder

            # For all the files in the project folder:
            #     Create a child archival object in ArchivesSpace
            #         using the combination of the project folder's name and
            #         the file's name as a ref_id.
            for file in get_dir_names(file_folder_path):
                # extract file name
                file_name = file.split("_")[0]
                # Find the path of each file
                file_path = file_folder_path + '/' + file

                # load datasets
                formats = load_dataset('formats', file_path)
                siegfried = load_dataset('siegfried', file_path)
                # extract date
                end_date = extract_date(max(siegfried['modified']))
                begin_date = extract_date(min(siegfried['modified']))
                # Get total file sizes
                total_file_size = siegfried['filesize'].sum()

                # Create notes to document the counts of all the file types
                #     identified in the _format_ file
                n_formats = formats.shape[0]

                note_detail = []
                for i in range(n_formats):
                    note_detail.append(
                        "Number of " + str(formats['Format'][i]) + ": " + str(formats['Count'][i]))

                child_archival_object = create_json_file(
                    'create_child_archival_objects', dir_path)
                child_archival_object['children'][0]['dates'][0]['begin'] = begin_date.strftime(
                    '%Y-%m-%d')
                child_archival_object['children'][0]['dates'][0]['end'] = end_date.strftime(
                    '%Y-%m-%d')
                child_archival_object['children'][0]['dates'][0]['label'] = "modified"
                child_archival_object['children'][0]['level'] = 'file'
                child_archival_object['children'][0]['title'] = file_name
                child_archival_object['children'][0]['ref_id'] = project_folder + \
                    '_' + file_name
                child_archival_object['children'][0]['notes'][0]['content'] = note_detail
                child_archival_object['children'][0]['notes'][0]['type'] = 'physdesc'
                child_archival_object['children'][0]['extents'][0]['number'] = str(
                    total_file_size)
                child_archival_object['children'][0]['resource']['ref'] = parent_resource_uri

                if begin_date.strftime('%Y-%m') > end_date.strftime('%Y-%m'):
                    child_archival_object['children'][0]['dates'][0]['expression'] = begin_date.strftime(
                        '%Y-%m') + '-' + end_date.strftime('%Y-%m')
                else:
                    child_archival_object['children'][0]['dates'][0]['expression'] = begin_date.strftime(
                        '%Y')

                child_archival_object_api = parent_archival_object_uri + '/children'

                info = call_archivesspace_api(
                    host, session_id, 'post', child_archival_object_api, child_archival_object)
                print('status of ' + file_name + ":")
                print(info)

    print('Completed!')


if __name__=="__main__":
   
    # Get the path of home diretory
    dir_path = sys.argv[1]

    parser = ArgumentParser(prog='bc_to_as.py', description='Import Brunnhilde-generated metadata into ArchivesSpace')
    parser.add_argument('--repo', action='store', help="Top level local directory corresponding to repository structure")
    args = parser.parse_args()

    if args.repo:
        repo_dir = args.repo
        run_session(args.repo)
    else:
        print("You must specify a local directory corresponding to the top level repository.")
    exit(1)
