"""Install package"""

import codecs
import sys
from os.path import abspath, dirname, join
from setuptools import setup
from setuptools import find_packages


ABOUT = dict()
with open("anastasia/__about__.py") as _:
    exec(_.read(), ABOUT)

HERE = abspath(dirname(__file__))
with codecs.open(join(HERE, 'README.md'), encoding='utf-8') as f:
    README = f.read()

with open('requirements.txt') as file:
    REQS = [line.strip() for line in file if line and not line.startswith("#")]

setup(
    name='anastasia',
    author=ABOUT['__author__'],
    author_email=ABOUT['__author_email__'],
    description=ABOUT['__description__'],
    # license=ABOUT['__license__'],
    url=ABOUT['__url__'],
    version=ABOUT['__version__'],
    packages=['anastasia', 'anastasia.routers'],
    setup_requires=["nose", "coverage", "mock"],
    install_requires=REQS,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'anastasia = anastasia.__main__:main',
        ],
    },
    long_description=README,
    long_description_content_type='text/markdown',
    zip_safe=False,
    test_suite='nose.collector'
)
