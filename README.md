# bc_to_aspace_toolkit

[![GitHub issues](https://img.shields.io/github/issues/bitcurator/bc_to_aspace_toolkit.svg)](https://github.com/bitcurator/bc_to_aspace_toolkit/issues)
[![GitHub forks](https://img.shields.io/github/forks/bitcurator/bc_to_aspace_toolkit.svg)](https://github.com/bitcurator/bc_to_aspace_toolkit/network)

Metadata transfer tools - BitCurator to ArchivesSpace

## Setup and Installation

This script is intended to be run in the BitCurator environment (or a similarly configured Linux host). It requires the **bulk_extractor** tool to be present (https://github.com/simsong/bulk_extractor), along with Brunnhilde (https://github.com/timothyryanwalsh/brunnhilde). Both of these are preinstalled in BitCurator. It also depends on **pandas** and **pathlib**. The **pandas** and **pathlib** dependencies are not included by default in the BitCurator environment; they will be automatically installed by the setup script if not present. 

All commands from this point forward are presented as if logged in as the **bcadmin** user in BitCurator. First, open a terminal and check out the lastest version of this repo from GitHub:

```shell
bcadmin@ubuntu:~$ git clone https://github.com/bitcurator/bc_to_aspace_toolkit
```

To install, run the following commands:

```shell
bcadmin@ubuntu:~$ cd bc_to_aspace_toolkit
bcadmin@ubuntu:~$ python3 setup.py build
bcadmin@ubuntu:~$ sudo python3 setup.py install
```

## Running the script

A simple example with the included sample disk image is provided here.

This script assumes you have a working ArchivesSpace instance running on another host, or in a VM accessible from your host. Need a simple way to get a test instance of ArchivesSpace up and running? See our simple Vagrant deployment option at https://github.com/bitcurator/aspace_vagrant.

Ensure you're in the **bc_to_aspace_toolkit** directory, then copy the provided sample image to your home directory:

```shell
bcadmin@ubuntu:~$ cd ~/bc_to_aspace_toolkit
bcadmin@ubuntu:~$ cp sample_disk_images/nps-2010-emails.E01 ~/
```

The Brunnhilde script uses a tool provided by The Sleuth Kit, **tsk_recover**, to extract files from disk images. The **tsk_recover** tool will make a best effort to autodetect disk image type, file system type, and partition offset, but this does not always work. We know this is likely an Expert Witness (E01) file from the file extension, and we can use the **mmls** tool to find the remaining information:

```shell
bcadmin@ubuntu:~/bc_to_aspace_toolkit$ cd ~/
bcadmin@ubuntu:~$ mmls nps-2010-emails.E01 
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000000000   0000000001   Unallocated
002:  000:000   0000000001   0000020479   0000020479   Win95 FAT32 (0x0b)
```

This tells us there is a FAT32 file system located at sector 1 (512 bytes into the image). We can pass this information through to **tsk_recover** via Brunnhilde as follows:

```shell
bcadmin@ubuntu:~$ brunnhilde.py -z -b --tsk_imgtype ewf --tsk_fstype fat --tsk_sector_offset 1 -d nps-2010-emails.E01 /home/bcadmin brunnhilde-reports
```

This extracts all files into the directory **brunnhilde-reports** in our home directory, **/home/bcadmin**. Note the **-z** flag at the beginning, which tells Brunnhilde to run Siegfried in order to scan compressed files; the **-b** flag, which tells Brunnhilde to run **bulk_extractor** and create the default reports; and the **-d** flag indicating we are providing a path to a disk image. Be aware! The process of running these tools may take some time.

Change directory into the **brunnhilde-reports** directory and examine the contents. Then, change directory into the **csv_reports** directory that it contains and examine those contents:

```shell
bcadmin@ubuntu:~$ cd brunnhilde-reports/
bcadmin@ubuntu:~/brunnhilde-reports$ ls
bulk_extractor  csv_reports  logs         siegfried.csv
carved_files    dfxml.xml    report.html  tree.txt
bcadmin@ubuntu:~/brunnhilde-reports$ cd csv_reports/
bcadmin@ubuntu:~/brunnhilde-reports/csv_reports$ ls
duplicates.csv  formats.csv         mimetypes.csv     warnings.csv
errors.csv      formatVersions.csv  unidentified.csv  years.csv
```

We need the **formats.csv** and **siegfried.csv** files to complete our transfer to our ArchivesSpace instance with **bc_to_as.py**. Prior to running the script, we need to create a folder structure that matches our repository, project, and dataset information. For this example, we will assume our ArchivesSpace instance is **clean** and contains no existing repositories.

First, return to your home directory and create a folder corresponding to a repository name. For this simple example, we'll call it **test_repository**:

```shell
bcadmin@ubuntu:~$ cd ~/
bcadmin@ubuntu:~$ mkdir test_repository
```

Now, create a project directory inside the repository directory. Repository directories can contain more than one project.

```shell
bcadmin@ubuntu:~$ cd test_repository/
bcadmin@ubuntu:~/test_repository$ mkdir project1
```

Now, change into the project directory and make a directory corresponding to our dataset (we'll copy the CSV files we created earlier into this directory next). Name this dataset **SET1_brunnout**. The portion of the name preceding the underscore (**SET1**) will be used as the reference ID when calling the ArchivesSpace API:

```shell
bcadmin@ubuntu:~/test_repository$ cd project1/
bcadmin@ubuntu:~/test_repository/project1$ mkdir SET1_brunnout
```

Now copy the relevant CSV files over (note that **formats.csv** and **siegfried.csv** have different source locations):

```shell
bcadmin@ubuntu:~/test_repository/project1$ cp ~/brunnhilde-reports/csv_reports/formats.csv SET1_brunnout/
bcadmin@ubuntu:~/test_repository/project1$ cp ~/brunnhilde-reports/siegfried.csv SET1_brunnout/
```

Finally, we'll run the **bc_to_as.py** script, passing it the location of our repository as an argument. When the script runs, you will see several prompts to confirm the location and structure of the repository directory. Then you will need to authenticate with a user that has permissions to create and modify repositories and their contents on ArchivesSpace. For this simple example, we'll use the default **admin** user (the default admin password for ArchivesSpace is also **admin**; the password is not shown below, but must be typed in):

```shell
bcadmin@ubuntu:~/test_repository/project1$ cd ~/
bcadmin@ubuntu:~$ bc_to_as.py /home/bcadmin/test_repository/

  [INFO] Found repository structure directory /home/bcadmin/test_repository
  [INFO] Looking for project directories...

  [INFO] - Found project directory /home/bcadmin/test_repository/project1
  [INFO] -- with metadata directory /home/bcadmin/test_repository/project1/SET1_brunnout

Is this the correct set of directories? [y/N]: y
  [INFO] Ok, continuing...

ArchivesSpace backend URL: http://server.url.here:8089
Username: admin
Password: 
Created by: admin
  Connected to ArchivesSpace backend!
  [INFO] Loaded template stream for create_repositories.json
  [INFO] Processing project folder project1
  [INFO] Loaded template stream for create_resources.json
  [INFO] Loaded template stream for create_archival_objects.json
  [INFO] Entering project folder path /home/bcadmin/test_repository/project1
  [INFO] Found dataset directory SET1_brunnout
  [INFO] Using reference ID SET1
  [INFO] Read dataset at /home/bcadmin/test_repository/project1/SET1_brunnout/formats.csv
  [INFO] Read dataset at /home/bcadmin/test_repository/project1/SET1_brunnout/siegfried.csv
  [INFO] Loaded template stream for create_child_archival_objects.json
  [STATUS] Processing result for SET1:
{'status': 'Updated', 'id': 1, 'lock_version': 0, 'stale': None}
  Completed!
```

You should now see the unpublished **ossarcflow_repository** listed in your ArchivesSpace console (assuming you are logged in). 

## Documentation, help, and other information

Additional in-progress documentation at: https://docs.google.com/document/d/1-pU__nBYSgjHhfcxYhQLdci9rxSgo1XiXpLEFgQSkCE

## License(s)

Unless otherwise indicated, software items in this repository are distributed under the terms of the GNU General Public License v3.0. See the LICENSE file for additional details.

## Development Team and Support

Product of the OSSArcFlow research team.
