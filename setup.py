import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 0):
    sys.exit("Sorry, Python < 3.0 is not supported")

import re

VERSIONFILE = "subspy/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

install_requires = [
    "argcomplete >= 1.8.2",
    "colorama >= 0.3.7",
    "pysubs2 >= 1.6.0",
    "chardet >= 3.0.4",
    "translators @ git+https://github.com/UlionTse/translators@master#egg=translators",
    "opencc-python-reimplemented @ git+https://github.com/yichen0831/opencc-python@master#egg=opencc-python-reimplemented",
]

setup(
    name="subspy",
    version=verstr,
    description="subspy",
    long_description="Please visit `Github <https://github.com/saycv/subspy>`_ for more information.",
    author="subspy project developers",
    author_email="",
    url="https://github.com/saycv/subspy",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    entry_points={"console_scripts": ["subspy = subspy.main:main"]},
    include_package_data=True,
    install_requires=install_requires,
)
