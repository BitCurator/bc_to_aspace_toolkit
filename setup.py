import os,glob
from setuptools import setup, find_packages

setup(
    name = 'bc_to_aspace_toolkit',
    version = '0.0.3',
    url = 'https://github.com/bitcurator/bc_to_aspace_toolkit',
    author = 'Yinglong Zhang',
    author_email = 'yz6939@email.unc.edu',

    packages = ['bc_to_aspace_toolkit'],
    scripts = ['bc_to_as.py'],

    # Required for access to our static json_templates resources
    include_package_data = True,

    description = 'Metqdata transfer script from BitCurator to ASpace',
    keywords = 'metadata identification disk images',

    platforms = ['POSIX', 'Windows'],
    install_requires=['pandas', 'pathlib', 'xmltodict'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
)
