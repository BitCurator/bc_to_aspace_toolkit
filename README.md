# bc-to-aspace-toolkit

[![GitHub issues](https://img.shields.io/github/issues/bitcurator/bc-to-aspace-toolkit.svg)](https://github.com/bitcurator/bc-to-aspace-toolkit/issues)
[![GitHub forks](https://img.shields.io/github/forks/bitcurator/bc-to-aspace-toolkit.svg)](https://github.com/bitcurator/bc-to-aspace-toolkit/network)

Metadata transfer scripts - BitCurator to ASpace

## Setup and Installation

This script is intended to be run in the BitCurator environment (or a similarly configured Linux host). It requires the bulk_extractor tool to be present, and depends on pandas and pathlib. The pandas and pathlib dependencies are not included by default in the BitCurator environment; they will be automatically installed by the setup script if not present. 

First, open a terminal and check out the lastest version of this repo from GitHub:

```shell
git clone https://github.com/bitcurator/bc-to-aspace-toolkit
```

To install, run the following commands:

```shell
cd bc-to-aspace-toolkit
python3 setup.py build
sudo python3 setup.py install
```

## Running the script

See the Google Doc link in the documentation section below.

## What's in this repository

- **json-templates**: JSON templates for the relevant metadata to be created / transfered
- **sample-data**: Small sample data sets using Brunnhilde output for an existing disk image (not included)
- **bc_to_as.py**: Script to create and transfer the relevant objects via the ASpace API

## Documentation, help, and other information

In-progress documentation at: https://docs.google.com/document/d/1-pU__nBYSgjHhfcxYhQLdci9rxSgo1XiXpLEFgQSkCE

## License(s)

Unless otherwise indicated, software items in this repository are distributed under the terms of the GNU General Public License v3.0. See the LICENSE file for additional details.

## Development Team and Support

Product of the OSSArcFlow research team.
