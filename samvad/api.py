"""
Created on Sat Sep 22 20:54:42 2018

@author: arjun
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mongoengine import MongoEngine

from flask_restful import reqparse, Api, Resource


from samvad import xpal

app = Flask(__name__)
app.config.update(
    MONGODB_HOST='localhost',
    MONGODB_PORT='27017',
    MONGODB_DB='samvad',
)
CORS(app)
me = MongoEngine(app)
app.logger = xpal.sakhacabsxpal.logger

api = Api(app)
parser = reqparse.RequestParser()
