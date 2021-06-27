#!/usr/bin/env python3
import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="artblog",
    version="0.1.0",
    packages=['artblog'],
    package_dir={'artblog': 'artblog'},
    package_data={
        'artblog': ['html/*.html'],
        'artblog': ['css/*.css']
        },
    #packages=setuptools.find_packages(),

    # include_package_data=True,
    # package_data={
    #     "artblog": ["css/*.css"],
    #     "artblog": ["html/*.html"],
    # },

    entry_points={
        'console_scripts': [
            'artblog=artblog.artblog:main'
        ],
    },

    python_requires=">=3.6",
    install_requires=[
        "python-slugify",
        "requests",
        "pyyaml",
        "mistune==2.0.0rc1"
    ],

    author="Ravi Chandran",
    description="Static site generator for simple personal art/picture/photo blogs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ravi-chandran/artblog",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
