import uuid
from setuptools import setup,find_packages
import codecs

import anastasia as this_package

from os.path import abspath, dirname, join
here = abspath(dirname(__file__))

with codecs.open(join(here, 'README.md'), encoding='utf-8') as f:
    README = f.read()

with open('requirements.txt') as file:
	reqs = [line.strip() for line in file if line and not line.startswith("#")]

setup(
	name=this_package.__name__,
	author=this_package.__author__,
	author_email=this_package.__author_email__,
	url=this_package.__url__,
	version=this_package.__version__,
	packages=[this_package.__name__],
	install_requires=reqs,
	include_package_data=True,
	entry_points={
		'console_scripts': [
			'anastasia = anastasia.__main__:main',
		],
	},
	long_description=README,
	zip_safe=False
)
