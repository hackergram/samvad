#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup
# from distutils.core import setup

setup(
    name='samvad',         # How you named your package folder (MyLib)
    packages=['samvad'],   # Chose the same as "name"
    version='dev-bal1test',      # Start with a small number and increase it with every change you make
    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    license='GNU General Public License v3.0',
    # Give a short description about your library
    description='Community Monitoring and Evaluation Framework',
    author=u'हैकरgram',                   # Type in your name
    author_email='listener@hackergram.org',      # Type in your E-Mail
    # Provide either the link to your github or to your website
    url='https://gitlab.com/hackergram/samvad',
    # I explain this later on
    download_url='https://gitlab.com/hackergram/samvad',
    # Keywords that define your package best
    keywords=['automation', 'orchestration'],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3.0',   # Again, pick a license
        # Specify which pyhton versions that you want to suppots
        'Programming Language :: Python :: 3',
    ],
)
# op=os.popen("sudo -H pip install -r requirements.txt").read()
# print(op)
op = os.popen("sudo -H pip3 install -r requirements.txt").read()
print(op)
