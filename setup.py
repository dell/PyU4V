from setuptools import setup

setup(name='PyU4V',
      version='3.0.0.5',
      url='https://github.com/ciarams87/PyU4V/',
      author='Dell Inc. or its subsidiaries',
      author_email='ciarastacke@hotmail.com',
      description=("A Python library for use with Dell EMC's Unisphere for "
                   "VMAX RestAPI."),
      license='MIT',
      packages=['PyU4V', 'PyU4V.utils'],
      install_requires=['requests', 'six', 'urllib3'],
      include_package_data=True,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Libraries :: Python Modules', ],
      tests_require=['mock', 'testtools'],
      test_suite='tests'
      )
