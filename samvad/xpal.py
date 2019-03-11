"""
Created on Sat Jan  12 21:52:07 2019

@author: arjunvenkatraman
"""
# import os
# import sys
# sys.path.append("/opt/xetrapal")
from xetrapal import Xetrapal
from samvad import samvadgraphmodel, xpalfuncs

import mongoengine

# import pandas

# from bs4 import BeautifulSoup


samvadxpal = Xetrapal(configfile="/opt/samvad-appdata/samvadxpal.conf")
baselogger = samvadxpal.logger
# Setting up mongoengine connections
samvadxpal.logger.info("Setting up MongoEngine")
mongoengine.connect('samvad', alias='default')
samvadgraphmodel.config.DATABASE_URL = 'bolt://neo4j:test123@localhost:7687'

samvadxpal.load_module(xpalfuncs)
