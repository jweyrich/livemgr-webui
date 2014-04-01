# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

PACKAGE_NAME = 'livemgr-webui'
PACKAGE_VER = '1.0'
PACKAGE_DESC = 'Web interface for Live Manager'
PACKAGE_URL = 'https://github.com/jweyrich/livemgr-webui'

def get_files_below(path):
    for (dirpath, dirnames, filenames) in os.walk(os.path.join('webui', path)):
        for filename in filenames:
            yield os.path.join(dirpath, filename)[6:]

def get_package_data():
    result = {
        '': [] + list(get_files_below('templates')) + list(get_files_below('locale')) + list(get_files_below('livemgr/templates')),
    }
    return result

setup(
    name = PACKAGE_NAME,
    version = PACKAGE_VER,
    description = PACKAGE_DESC,
    url = PACKAGE_URL,
    packages = find_packages(),
    package_data = get_package_data(),
)
