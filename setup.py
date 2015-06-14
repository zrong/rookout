from setuptools import setup, find_packages

setup(
    name = "rookout",
    version = "0.4.0",
    description = "A rookie's workout library by zrong.",
    author = "zrong",
    author_email = "zrongzrong@gmail.com",
    url = "http://github.com/zrong/python",
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
