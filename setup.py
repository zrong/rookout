from setuptools import setup, find_packages

setup(
    name = "zrong",
    version = "0.3.1",
    description = "A python library by zrong",
    author = "zrong",
    author_email = "zrongzrong@gmail.com",
    url = "http://github.com/zrong/python",
    license = "MIT",
    keywords = "utils development 1201",
    packages = find_packages(exclude=["tests*","docs"]),
    classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
)
