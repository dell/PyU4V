# replace_version.py
import fileinput
from version import (VERSION, API_VERSION,
                     UNI_VERSION, MAJOR_VERSION)
import shutil

version_file_list = ['../../README.rst', '../../index.rst','../../setup.py',
                     '../../docs/source/installation.rst',
                     '../../docs/source/index.rst']

files_to_copy = [('../../README_template.rst',
                       '../../README.rst'),
                      ('../../index_template.rst','../../index.rst'),
                      ('../../setup_template.py', '../../setup.py' ),
                     ('../../docs/source/installation_template.rst',
                      '../../docs/source/installation.rst'),
                     ('../../docs/source/index_template.rst',
                      '../../docs/source/index.rst')]
for original_file, new_file in files_to_copy:
    shutil.copyfile(original_file, new_file)

def update_version(version_file_list):
    for filename in version_file_list:
        with fileinput.input(filename, inplace=True) as f:
            for line in f:
                line = line.replace('{version}', VERSION)
                line = line.replace('{uni_version}', UNI_VERSION)
                line = line.replace('{major_version}', MAJOR_VERSION)
                line = line.replace('{api_version}', API_VERSION)
                print(line, end='')

update_version(version_file_list)

