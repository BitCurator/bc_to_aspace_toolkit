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


import pkg_resources

def get_json_template(template_name):
    resource_package = "bc_to_aspace_toolkit"  # Exact package name here
    resource_path = '/'.join(('json_templates', template_name))  # Do not use os.path.join()

    # String alternative (reference only, we'll use the file stream)
    #template = pkg_resources.resource_string(resource_package, resource_path)
    # A file-like stream:
    template = pkg_resources.resource_stream(resource_package, resource_path)
    return template
