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

import os
import sys
import datetime
import getpass
import json
import re
import requests
import xmltodict
import pandas as pd
from pathlib import Path
from bc_to_aspace_toolkit import utilities
import xmltodict

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
    dir_names = [dirs for root, dirs, files in os.walk(dir_path)][0]
    results = []
    for dir in dir_names:
        if dir not in exclude:
            path = dir_path + '/' + dir
            if len(os.listdir(path)) > 0:
                results.append(dir)
    return results


def create_json_file(template_name):
    """
    Create a json file using existing json templates

    Args:
        template_name (string): the name of the json template
        dir_path (string): the path of the folder with json templates

    Returns:
        type: a json file
    """
    template_stream = utilities.get_json_template(template_name + '.json')
    template = json.load(template_stream)
    print("  [INFO] Loaded template stream for {}".format(template_name + '.json'))

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
    dataset_path = dir_path + '/' + file_name + '.csv'
    if os.path.isfile(dataset_path):
        dataset = pd.read_csv(dataset_path)
        print("  [INFO] Read dataset at {}".format(dataset_path))
        return dataset


def extract_date(time):
    """
    extract '%Y-%m-%d' from datetime data

    Args:
        time (string): datetime

    Returns:
        type: extracted date (datetime object)
    """
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
        print('  Please specify API action: "post" or "get"')


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
    check_ref_id_api = repository_uri + \
        '/find_by_id/archival_objects?ref_id[]=' + ref_id
    archival_object_ids = call_archivesspace_api(
        host, session_id, 'get', check_ref_id_api)
    if len(archival_object_ids['archival_objects']) > 0:
        archival_object_api = archival_object_ids['archival_objects'][0]['ref']
        archival_object_output = call_archivesspace_api(
            host, session_id, 'get', archival_object_api)
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


def xmlConvertToJson (file_path):
    """
    convert xml to Josn
    Args:
        file_path: path of the dfxml(xml) file
    Returns:
        json file: reutn the json format of the input file
    """
    with open(file_path, 'r') as f:
        xmlFile = f.read()
    jsonFile = json.dumps(xmltodict.parse(xmlFile), indent=4)
    print("  [INFO] Read dataset at {}".format(file_path))
    return json.loads(jsonFile)


def run_session(dir_path):

    if sys.version_info[0] < 3:
        host = raw_input('ArchivesSpace backend URL: ')
        username = raw_input('Username: ')
        password = getpass.getpass(prompt='Password: ')
        created_by = raw_input('Created by: ')
    else:
        host = input('ArchivesSpace backend URL: ')
        username = input('Username: ')
        password = getpass.getpass(prompt='Password: ')
        created_by = input('Created by: ')

    # retrieve session id
    try:
        session_id = get_sessionId(host, username, password)
        print("  Connected to ArchivesSpace backend!")
    except:
        user_response = utilities.ask_user("Username, password, or URL was incorrect.  Try again?")
        if user_response == False:
            print("  [ABORT] Quitting...")
            exit(1)
        else:
            return run_session(dir_path)

    # Search for a repository using the name of the repository folder;
    #     If the repository does not exist, create one using
    #     the name of this repository folder as a repo_code.
    repository_folder = os.path.basename(dir_path)
    repository_uri = get_repository_uri(repository_folder, session_id, host)

    if repository_uri == '':
        print("  [ERROR] The repository {} does not exist in this ArchivesSpace instance. Exiting.".format(repository_folder))
        exit(1)
    else:
        print("  [INFO] Found the repository: {}".format(repository_uri))

    # Find the path of the preject folders in the repository folder.
    # project_folder_paths = dir_path + '/' + repository_folder

    # For each project folder in the repository folder:
    #     Search for a parent archive object using the name of the project folder;
    #     If this parent archival object does not exist, create one using
    #         the name of the project folder as a ref_id.
    #     If this parent archival object exists, but its resouce is missing, create
    #     a new resource.
    for project_folder in get_dir_names(dir_path):
        print("  [INFO] Processing project folder {}".format(project_folder))
        ref_id_parent = project_folder.replace(" ", '_')

        parent_archival_object = get_archival_object(
            ref_id_parent, repository_uri, session_id, host)

        if parent_archival_object != '':
            parent_resource_uri = parent_archival_object['resource']['ref']
            parent_archival_object_uri = parent_archival_object['uri']
        else:
            parent_resource_uri = ''
            parent_archival_object_uri = ''

        if parent_archival_object_uri == '':
            parent_resource = create_json_file('create_resources')
            parent_resource['id_0'] = project_folder.replace(" ", "_")
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

            parent_object = create_json_file('create_archival_objects')
            parent_object['title'] = project_folder
            parent_object['level'] = 'file'
            parent_object['ref_id'] = ref_id_parent
            parent_object['resource']['ref'] = parent_resource_uri
            parent_object['dates'] = []
            parent_object['extents'] = []
            parent_object['notes'] = []
            parent_object_api = repository_uri + '/archival_objects'
            parent_archival_object_uri = call_archivesspace_api(
                host, session_id, 'post', parent_object_api, parent_object)['uri']
        else:
            if parent_resource_uri == '':
                parent_resource = create_json_file('create_resources')
                parent_resource['id_0'] = project_folder.replace(" ", "_")
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
        file_folder_path = dir_path + '/' + project_folder
        print("  [INFO] Entering project folder path {}".format(file_folder_path))

        # For all the files in the project folder:
        #     Create a child archival object in ArchivesSpace
        #         using the combination of the project folder's name and
        #         the file's name as a ref_id.
        for file in get_dir_names(file_folder_path):
            print("  [INFO] Found dataset directory {}".format(file))
            # extract file name
            file_name = file.split("_")[0]
            print("  [INFO] Using reference ID {}".format(file_name))
            # Find the path of each file
            file_path = file_folder_path + '/' + file
            file_csv_report_path = file_folder_path + '/' + file + '/csv_reports'
            child_archival_object = create_json_file('create_child_archival_objects')

            # load datasets
            formats = load_dataset('formats', file_csv_report_path)
            siegfried = load_dataset('siegfried', file_path)

            # use siegfried dates by default, overwrite if dfxml present
            end_date = extract_date(max(siegfried['modified']))
            begin_date = extract_date(min(siegfried['modified']))

            dfxml_path = file_folder_path + '/' + file + '/dfxml.xml'

            # If no DFXML exists, warn and optionally default to Siegfried dates
            if not os.path.isfile(dfxml_path):
                print("  [WARNING] No dfxml.xml found for dataset {}".format(file))
                print("            Type N and hit enter at the following prompt to")
                print("            skip this dataset, or y to continue processing")
                print("            using timestamps from Siegfried.")
                user_response = utilities.ask_user("Continue processing this dataset using Siegfried timestamps?")
                if user_response == False:
                    print("  [INFO] Skipping, moving to next dataset...")
                    continue
                else:
                    print("  [INFO] Continuing, using dates from Siegfried...")

            # If DFXML exists, use modified dates or warn and optionally default to
            # Siegfried dates if no modified dates are found (e.g. CD-ROM)
            if os.path.isfile(dfxml_path):
                dfxml_files = xmlConvertToJson(dfxml_path)['dfxml']
                if 'volume' in dfxml_files:
                    dfxml_file_objects = dfxml_files['volume']['fileobject']
                else:
                    dfxml_file_objects = dfxml_files['fileobject']

                modified_time = []
                for file in dfxml_file_objects:
                    if "mtime" in file:
                        if "#text" in file['mtime']:
                            modified_time.append(file['mtime']['#text'])
                        else:
                            modified_time.append(file['mtime'])
                # Some disk images may have no modified times. Use Siegfried values
                # and warn in that case.
                if modified_time == []:
                    print("  [WARNING] No modified times found in DFXML for files in dataset {}".format(file))
                    print("            Type N and hit enter at the following prompt to")
                    print("            skip this dataset, or y to continue processing")
                    print("            using timestamps from Siegfried.")
                    user_response = utilities.ask_user("Continue processing this dataset using Siegfried timestamps?")
                    if user_response == False:
                        print("  [INFO] Skipping, moving to next dataset...")
                        continue
                    else:
                        print("  [INFO] Continuing, using dates from Siegfried...")
                else:
                    end_date = extract_date(max(modified_time))
                    begin_date = extract_date(min(modified_time))


            # Get total file sizes, converting from bytes to megabytes at 2 dec. places
            total_file_size_bytes = siegfried['filesize'].sum()
            total_file_size_megabytes = round((total_file_size_bytes / 1048576), 2)

            # Create notes to document the counts of all the file types
            #     identified in the _format_ file
            n_formats = formats.shape[0]

            note_detail = []
            for i in range(n_formats):
                # String format of Siegfried output may yield NaN for format name.
                # Check and replace with the phrase unidentified files if needed
                if pd.isnull(formats['Format'][i]):
                    note_detail.append(
                        "Number of unidentified files: " + str(formats['Count'][i]))
                else:
                    note_detail.append(
                        "Number of " + str(formats['Format'][i]) + ": " + str(formats['Count'][i]))


            child_archival_object['children'][0]['dates'][0]['begin'] = begin_date.strftime(
                '%Y-%m-%d')
            child_archival_object['children'][0]['dates'][0]['end'] = end_date.strftime(
                '%Y-%m-%d')
            child_archival_object['children'][0]['dates'][0]['label'] = "modified"
            child_archival_object['children'][0]['level'] = 'file'
            child_archival_object['children'][0]['title'] = file_name
            # child_archival_object['children'][0]['ref_id'] = project_folder.replace(" ", "_") + \
            #     '_' + file_name.replace(" ", "_")
            child_archival_object['children'][0]['notes'][0]['content'] = note_detail
            child_archival_object['children'][0]['notes'][0]['type'] = 'physdesc'
            child_archival_object['children'][0]['extents'][0]['number'] = str(
                total_file_size_megabytes)
            child_archival_object['children'][0]['resource']['ref'] = parent_resource_uri

            if begin_date.strftime('%Y-%m') < end_date.strftime('%Y-%m'):
                child_archival_object['children'][0]['dates'][0]['expression'] = begin_date.strftime(
                    '%Y-%m') + '-' + end_date.strftime('%Y-%m')
            else:
                child_archival_object['children'][0]['dates'][0]['expression'] = begin_date.strftime(
                    '%Y')

            child_archival_object_api = parent_archival_object_uri + '/children'

            info = call_archivesspace_api(
                host, session_id, 'post', child_archival_object_api, child_archival_object)
            print('  [STATUS] Processing result for ' + file_name + ":")
            print(info)

    print('  Completed!')


if __name__=="__main__":

    parser = ArgumentParser(prog='bc_to_as.py', description='Import Brunnhilde-generated metadata into ArchivesSpace')
    parser.add_argument('repodir', action='store', help="Top level local directory corresponding to the remote repository structure")
    args = parser.parse_args()

    if os.path.isdir(args.repodir):
       repo_dir = (args.repodir).rstrip("/")

       # Check the structure of the local directory.
       utilities.check_repo_structure(repo_dir)

       # Proceed and connect to backend.
       run_session(repo_dir)

    else:
       print("  [ABORT] The directory {} does not exist. You must use the full path to the local directory corresponding to the repository structure. Check the path and directory name and try again.".format(args.repodir))
