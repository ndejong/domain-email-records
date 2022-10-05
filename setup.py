# This file was auto-generated by Shut. DO NOT EDIT
# For more information about Shut, check out https://pypi.org/project/shut/

from __future__ import print_function
import io
import os
import setuptools
import sys

readme_file = 'README.md'
if os.path.isfile(readme_file):
  with io.open(readme_file, encoding='utf8') as fp:
    long_description = fp.read()
else:
  print("warning: file \"{}\" does not exist.".format(readme_file), file=sys.stderr)
  long_description = None

requirements = [
  'dnspython',
  'async_lru',
]

setuptools.setup(
  name = 'domain-email-records',
  version = '0.4.2',
  author = 'Nicholas de Jong',
  author_email = 'ndejong@threatpatrols.com',
  description = 'CLI tool to quickly lookup MX, SPF, DMARC records for many domains',
  long_description = long_description,
  long_description_content_type = 'text/markdown',
  url = 'https://github.com/ndejong/domain-email-records',
  license = 'BSD2',
  packages = setuptools.find_packages('src', ['test', 'test.*', 'tests', 'tests.*', 'docs', 'docs.*']),
  package_dir = {'': 'src'},
  include_package_data = True,
  install_requires = requirements,
  extras_require = {},
  tests_require = [],
  python_requires = '>=3.7.0,<4.0.0',
  data_files = [],
  entry_points = {
    'console_scripts': [
      'domain-email-records = domain_email_records.cli_entrypoint:main',
    ]
  },
  cmdclass = {},
  keywords = ['domain-name', 'dns', 'email', 'spf', 'dmarc'],
  classifiers = ['Environment :: Console', 'Intended Audience :: System Administrators', 'Intended Audience :: Information Technology', 'Programming Language :: Python :: 3', 'License :: OSI Approved :: BSD License'],
  zip_safe = True,
)
