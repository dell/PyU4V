# replace_version.py
import fileinput
from version import (VERSION, API_VERSION,
                     UNI_VERSION, MAJOR_VERSION)
import os
import shutil

template_file_list = ['../../README_template.rst', '../../index_template.rst',
                     '../../docs/source/installation_template.rst',
                     '../../docs/source/index_template.rst']


version_file_list = ['../../README.rst', '../../index.rst',
                     '../../docs/source/installation.rst',
                     '../../docs/source/index.rst']


def copy_files_with_version_names(template_file_list, version_file_list):
    if len(template_file_list) != len(version_file_list):
        raise ValueError(
            "The length of template_file_list and version_file_list must be the same.")

    for original_file_path, new_file_name in zip(template_file_list,
                                                 version_file_list):
        # Get the directory and file extension
        directory, original_file_name = os.path.split(original_file_path)
        _, file_extension = os.path.splitext(original_file_name)

        # Create the new file path
        new_file_path = os.path.join(directory, new_file_name + file_extension)

        # Copy the file to the new location with the new name
        shutil.copyfile(original_file_path, new_file_path)
        print(f"Copied {original_file_path} to {new_file_path}")

def update_version():
    for filename in version_file_list:
        with fileinput.input(filename, inplace=True) as f:
            for line in f:
                line = line.replace('{version}', VERSION)
                line = line.replace('{uni_version}', UNI_VERSION)
                line = line.replace('{major_version}', MAJOR_VERSION)
                line = line.replace('{api_version}', API_VERSION)
                print(line, end='')

copy_files_with_version_names(template_file_list, version_file_list)


