from setuptools import setup

setup(name='PyU4V',
      version='0.1',
      url='https://github.com/ciarams87/PyU4V/',
      author='Dell Inc. or its subsidiaries',
      description=("A library showing some of the functionality possible "
                   "using the ReST API of Dell EMC's UniSphere for VMAX."),
      license='MIT',
      packages=['PyU4V'],
      install_requires=['requests', ],
      include_package_data=True,
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Libraries :: Python Modules', ],
      test_suite='nose.collector',
      tests_require=['nose'],
      )
