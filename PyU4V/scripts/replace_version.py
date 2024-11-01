# replace_version.py
import fileinput
from version import (VERSION, API_VERSION,
                     UNI_VERSION, MAJOR_VERSION)
import shutil


def copy_file(original_file, new_file):
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


def main():
    version_files = [
        '../../README.rst',
        '../../index.rst',
        '../../setup.py',
        '../../docs/source/installation.rst',
        '../../docs/source/index.rst'
    ]

    original_files = [
        '../../README_template.rst',
        '../../index_template.rst',
        '../../setup_template.py',
        '../../docs/source/installation_template.rst',
        '../../docs/source/index_template.rst'
    ]

    for original, new in zip(original_files, version_files):
        copy_file(original, new)

    update_version(version_files)


if __name__ == '__main__':
    main()
