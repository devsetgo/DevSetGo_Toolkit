# -*- coding: utf-8 -*-
"""Setup script for realpython-reader"""

import os.path

from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="devsetgo_toolkit",
    version="0.1.0",
    description="Async tools to simplify building applications",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/devsetgo/dev_com_lib",
    project_urls={
        "Documentation": "https://devsetgo.github.io/devsetgo_toolkit/",
        "Source": "https://github.com/devsetgo/devsetgo_toolkit",
    },
    keywords=["asyncio", "async", "sqlalchemy"],
    author="Mike Ryan",
    author_email="mikeryan56@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
    packages=["devsetgo_toolkit"],
    include_package_data=True,
    install_requires=[
        "sqlalchemy>=2.0.0,<2.0.99",
        "pydantic>=2.4.0,<2.9.99",
        "email-validator>=2.0.0,<2.2.0",
        "fastapi>=0.100.0<0.110",
    ],
)
