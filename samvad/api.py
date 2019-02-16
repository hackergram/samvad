"""
Created on Sat Sep 22 20:54:42 2018

@author: arjun
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mongoengine import MongoEngine
import json
import datetime
from flask_restful import reqparse, Api, Resource

import urllib
from samvad import xpal

app = Flask(__name__)
app.config.update(
    MONGODB_HOST='localhost',
    MONGODB_PORT='27017',
    MONGODB_DB='samvad',
)
CORS(app)
me = MongoEngine(app)
app.logger = xpal.samvadxpal.logger

api = Api(app)
parser = reqparse.RequestParser()


class VyaktiResource(Resource):
    def get(self, command=None, vyakti_id=None):
        if command is not None:
            app.logger.info(
                "VyaktiResource: Received Command {}".format(command))
            if command == "export":
                try:
                    resp = xpal.export_vyaktis()
                    status = "success"
                except Exception as e:
                    app.logger.error("{} {}".format(type(e), str(e)))
                    resp = "{} {}".format(type(e), str(e))
                    status = "error"
            else:
                resp = "Unrecognized command"
                status = "error"
        elif vyakti_id is not None:
            resp = list(xpal.documents.Vyakti.objects(vyakti_id=vyakti_id))
        else:
            resp = list(xpal.documents.Vyakti.objects.all())
        if type(resp) == list and resp != []:
            status = "success"
        else:
            status = "error"
        if resp == []:
            resp = "No records found"
        return jsonify({"resp": resp, "status": status})

    def post(self, command=None):
        app.logger.info("{}".format(request.get_json()))
        respdict = request.get_json()
        if command is None:
            try:
                if xpal.validate_vyakti_dict(respdict)['status'] is True:
                    resp = xpal.create_vyakti(respdict)
                    if type(resp) != list:
                        status = "error"
                    else:
                        status = "success"
                else:
                    status = "error"
                    resp = xpal.validate_vyakti_dict(respdict)['message']
            except Exception as e:
                app.logger.error("{} {}".format(type(e), str(e)))
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        elif command == "import":
            try:
                resp = xpal.import_vyaktis(respdict)
                if type(resp) != list:
                    status = "error"
                else:
                    status = "success"
                for vyakti in resp:
                    if "error" in vyakti['status'].lower():
                        status = "error"
            except Exception as e:
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        elif command == "bulkdelete":
            try:
                if type(respdict) != list:
                    status = "error"
                    resp = "Bulk Delete Expects a list of vyakti ids"
                else:
                    for vyakti_id in respdict:
                        xpal.delete_vyakti(vyakti_id)
                    resp = "Deleted vyaktis {}".format(respdict)
                    status = "success"
            except Exception as e:
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        else:
            resp = "Unrecognized command"
            status = "error"
        return jsonify({"resp": resp, "status": status})

    def put(self, vyakti_id):
        app.logger.info("{}".format(request.get_json()))
        respdict = request.get_json()
        try:
            if xpal.validate_vyakti_dict(respdict, new=False)['status'] is True:
                resp = xpal.update_vyakti(vyakti_id, respdict)
                if type(resp) != list:
                    status = "error"
                else:
                    status = "success"
            else:
                status = "error"
                resp = xpal.validate_vyakti_dict(
                    respdict, new=False)['message']
        except Exception as e:
            app.logger.error("{} {}".format(type(e), str(e)))
            resp = "{} {}".format(type(e), str(e))
            status = "error"
        return jsonify({"resp": resp, "status": status})

    def delete(self, vyakti_id=None):
        if vyakti_id is None:
            resp = "No vyakti ID"
            status = "error"
        else:
            app.logger.info(
                "VyaktiResource: Trying to delete vyakti {}".format(vyakti_id))
            try:
                resp = xpal.delete_vyakti(vyakti_id)
                if type(resp) == list:
                    status = "success"
                else:
                    status = "error"
            except Exception as e:
                app.logger.error("{} {}".format(type(e), str(e)))
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        return jsonify({"resp": resp, "status": status})


api.add_resource(VyaktiResource, "/vyakti", endpoint="vyakti")
api.add_resource(VyaktiResource, "/vyakti/by_vyakti_id/<string:vyakti_id>", endpoint="vyaktiid")
api.add_resource(VyaktiResource, "/vyakti/<string:command>", endpoint="vyakti_command")


class AbhiVyaktiResource(Resource):
    def get(self, command=None, vyakti_id=None):
        if command is not None:
            app.logger.info(
                "AbhiVyaktiResource: Received Command {}".format(command))
            if command == "export":
                try:
                    resp = xpal.export_abhivyaktis()
                    status = "success"
                except Exception as e:
                    app.logger.error("{} {}".format(type(e), str(e)))
                    resp = "{} {}".format(type(e), str(e))
                    status = "error"
            else:
                resp = "Unrecognized command"
                status = "error"
        elif vyakti_id is not None:
            vyakti = xpal.documents.Vyakti.objects(vyakti_id=vyakti_id)
            if len(vyakti) > 0:
                vyakti = vyakti[0]
                resp = list(xpal.documents.AbhiVyakti.objects(vyakti=vyakti))
            else:
                resp = "No Vyakti by that ID"
        else:
            resp = list(xpal.documents.AbhiVyakti.objects.all())
        if type(resp) == list and resp != []:
            status = "success"
        else:
            status = "error"
        if resp == []:
            resp = "No records found"
        return jsonify({"resp": resp, "status": status})

    def post(self, command=None):
        app.logger.info("{}".format(request.get_json()))
        respdict = request.get_json()
        if command is None:
            try:
                if xpal.validate_abhivyakti_dict(respdict)['status'] is True:
                    resp = xpal.create_abhivyakti(respdict)
                    if type(resp) != list:
                        status = "error"
                    else:
                        status = "success"
                else:
                    status = "error"
                    resp = xpal.validate_abhivyakti_dict(respdict)['message']
            except Exception as e:
                app.logger.error("{} {}".format(type(e), str(e)))
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        elif command == "import":
            try:
                # replace with bookinglist=xpal.importbookings(respdict) #91 #83
                resp = xpal.import_abhivyaktis(respdict)
                if type(resp) != list:
                    status = "error"
                else:
                    status = "success"
                for abhivyakti in resp:
                    if "error" in abhivyakti['status'].lower():
                        status = "error"
            except Exception as e:
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        elif command == "bulkdelete":
            try:
                if type(respdict) != list:
                    status = "error"
                    resp = "Bulk Delete Expects a list of abhivyakti ids"
                else:
                    for abhivyakti_id in respdict:
                        xpal.delete_abhivyakti(abhivyakti_id)
                    resp = "Deleted abhivyaktis {}".format(respdict)
                    status = "success"
            except Exception as e:
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        else:
            resp = "Unrecognized command"
            status = "error"
        return jsonify({"resp": resp, "status": status})

    def put(self, abhivyakti_id):
        app.logger.info("{}".format(request.get_json()))
        respdict = request.get_json()
        try:
            if xpal.validate_abhivyakti_dict(respdict, new=False)['status'] is True:
                resp = xpal.update_abhivyakti(abhivyakti_id, respdict)
                if type(resp) != list:
                    status = "error"
                else:
                    status = "success"
            else:
                status = "error"
                resp = xpal.validate_abhivyakti_dict(
                    respdict, new=False)['message']
        except Exception as e:
            app.logger.error("{} {}".format(type(e), str(e)))
            resp = "{} {}".format(type(e), str(e))
            status = "error"
        return jsonify({"resp": resp, "status": status})

    def delete(self, abhivyakti_id=None):
        if abhivyakti_id is None:
            resp = "No abhivyakti ID"
            status = "error"
        else:
            app.logger.info(
                "AbhiVyaktiResource: Trying to delete abhivyakti {}".format(abhivyakti_id))
            try:
                resp = xpal.delete_abhivyakti(abhivyakti_id)
                if type(resp) == list:
                    status = "success"
                else:
                    status = "error"
            except Exception as e:
                app.logger.error("{} {}".format(type(e), str(e)))
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        return jsonify({"resp": resp, "status": status})


api.add_resource(AbhiVyaktiResource, "/abhivyakti", endpoint="abhivyakti")
api.add_resource(AbhiVyaktiResource, "/abhivyakti/by_vyakti_id/<string:vyakti_id>", endpoint="abhivyaktiid")
api.add_resource(AbhiVyaktiResource, "/abhivyakti/<string:command>", endpoint="abhivyakti_command")


class SandeshResource(Resource):
    def get(self, command=None):
        if command is not None:
            app.logger.info(
                "SandeshResource: Received Command {}".format(command))
            if command == "export":
                try:
                    resp = xpal.export_sandesh()
                    status = "success"
                except Exception as e:
                    app.logger.error("{} {}".format(type(e), str(e)))
                    resp = "{} {}".format(type(e), str(e))
                    status = "error"
            else:
                resp = "Unrecognized command"
                status = "error"
        else:
            resp = list(xpal.documents.Sandesh.objects.all())
        if type(resp) == list and resp != []:
            status = "success"
        else:
            status = "error"
        if resp == []:
            resp = "No records found"
        for sandesh in resp:
            if hasattr(sandesh, "file"):
                sandesh.url = sandesh.file.replace(xpal.samvadxpal.datapath, xpal.samvadxpal.config.get("Jeeva", "urlbase")+"/xetrapal-data").replace(" ", "%20")
                sandesh.save()
        return jsonify({"resp": resp, "status": status})

    def post(self, command=None):
        app.logger.info("{}".format(request.get_json()))
        respdict = request.get_json()
        if command is None:
            try:
                if xpal.validate_sandesh_dict(respdict)['status'] is True:
                    resp = xpal.create_sandesh(respdict)
                    if type(resp) != list:
                        status = "error"
                    else:
                        status = "success"
                else:
                    status = "error"
                    resp = xpal.validate_sandesh_dict(respdict)['message']
            except Exception as e:
                app.logger.error("{} {}".format(type(e), str(e)))
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        elif command == "import":
            try:
                # replace with bookinglist=xpal.importbookings(respdict) #91 #83
                resp = xpal.import_sandesh(respdict)
                if type(resp) != list:
                    status = "error"
                else:
                    status = "success"
                for sandesh in resp:
                    if "error" in sandesh['status'].lower():
                        status = "error"
            except Exception as e:
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        elif command == "bulkdelete":
            try:
                if type(respdict) != list:
                    status = "error"
                    resp = "Bulk Delete Expects a list of sandesh ids"
                else:
                    for sandesh_id in respdict:
                        xpal.delete_sandesh(sandesh_id)
                    resp = "Deleted sandesh {}".format(respdict)
                    status = "success"
            except Exception as e:
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        elif command == "search":
            app.logger.info("SandeshResource: Searching Sandesh")
            try:
                queryset = xpal.search_sandesh(respdict)
                resp = queryset
                status = "success"
            except Exception as e:
                app.logger.error("{} {} \n {}".format(
                    type(e), str(e), respdict))
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        else:
            resp = "Unrecognized command"
            status = "error"
        return jsonify({"resp": resp, "status": status})

    def delete(self, sandesh_id=None):
        if sandesh_id is None:
            resp = "No abhivyakti ID"
            status = "error"
        else:
            app.logger.info(
                "SandeshResource: Trying to delete sandesh {}".format(sandesh_id))
            try:
                resp = xpal.delete_sandesh(sandesh_id)
                if type(resp) == list:
                    status = "success"
                else:
                    status = "error"
            except Exception as e:
                app.logger.error("{} {}".format(type(e), str(e)))
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        return jsonify({"resp": resp, "status": status})


api.add_resource(SandeshResource, "/sandesh", endpoint="sandesh")
api.add_resource(SandeshResource, "/sandesh/<string:command>", endpoint="sandesh_command")


if __name__ == '__main__':
    app.run(host="0.0.0.0")
