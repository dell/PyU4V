# replace_version.py
import fileinput
from PyU4V.version import (VERSION, API_VERSION,
                           UNI_VERSION, MAJOR_VERSION)

version_file_list = ['../../README.rst', '../../index.rst',
                     '../../docs/source/installation.rst',
                     '../../docs/source/index.rst']

for filename in version_file_list:
    with fileinput.input(filename, inplace=True) as f:
        for line in f:
            line = line.replace('{version}', VERSION)
            line = line.replace('{uni_version}', UNI_VERSION)
            line = line.replace('{major_version}', MAJOR_VERSION)
            line = line.replace('{api_version}', API_VERSION)
            print(line, end='')




