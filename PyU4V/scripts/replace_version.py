# replace_version.py
import fileinput
from version import VERSION, Unisphere_Min_version, API_VERSION

version_file_list = ['../../README.rst', '../../index.rst',
                     '../../docs/source/installation.rst',
                     '../../docs/source/index.rst']

for filename in version_file_list:
    with fileinput.input(filename, inplace=True) as f:
        for line in f:
            print(line.replace('{version}', VERSION), end='')




