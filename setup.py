#!/usr/bin/env python3
from setuptools import setup, find_packages

long_description = """
Jenni provides a Python-based system for configuring and running Jenkins jobs.

- It allows programmatic generation of Jenkins Jobs using the flexibility and familiarity of the Python language.
- Using class-based models for defining jobs allows for template-like instantiation of jobs.
- It provides a flexible framework for iterative development of Jenkins jobs.
"""

setup(
    name="jenni",
    version="0.1.0",
    packages=find_packages(include=("jenni", "jenni.*"), exclude=("jenni.tests", "jenni.tests.*")),
    install_requires=[],
    python_requires=">=3.6",
    license="Apache 2.0",
    url="https://pypi.org/project/jenni",
    author="Wouter Batelaan (Synamedia)",
    author_email="jenni-oss@synamedia.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    description="A Python-based system for configuring and running Jenkins jobs.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    test_suite="test",
    tests_require=[],
)
