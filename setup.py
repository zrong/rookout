import os
import re
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    content = None
    with open(os.path.join(here, *parts), 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def find_requires(*file_paths):
    require_file = read(*file_paths)
    return require_file.splitlines()

setup(
    name = "rookout",
    version=find_version('rookout', '__init__.py'),
    description = "A rookie's workout library by zrong.",
    author = "zrong",
    author_email = "zrongzrong@gmail.com",
    url = "http://github.com/zrong/rookout",
    license = "MIT",
    keywords = "utils development zrong rookie workout",
    packages = find_packages(exclude=["tests*","docs"]),
    classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
)
