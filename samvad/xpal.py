"""
Created on Sat Sep  8 21:52:07 2018s
@author: arjun
"""

import mongoengine
import xetrapal
from samvad import documents, utils

samvadxpal = xetrapal.Xetrapal(configfile="/opt/samvad-appdata/samvadxpal.conf")

# Setting up mongoengine connections
samvadxpal.logger.info("Setting up MongoEngine")
mongoengine.connect('samvad', alias='default')
