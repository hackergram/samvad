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
app.logger = xpal.samvadxpal.logger

api = Api(app)
parser = reqparse.RequestParser()


class UserResource(Resource):
    def get(self, tgid=None, mobile_num=None, docid=None, user_id=None, command=None):
        if command is not None:
            app.logger.info(
                "UserResource: Received Command {}".format(command))
            if command == "export":
                try:
                    resp = xpal.export_users()
                    status = "success"
                except Exception as e:
                    app.logger.error("{} {}".format(type(e), str(e)))
                    resp = "{} {}".format(type(e), str(e))
                    status = "error"
            else:
                resp = "Unrecognized command"
                status = "error"
        elif docid is not None:
            resp = [xpal.documents.documents.User.objects.with_id(docid)]
        elif tgid is not None:
            resp = list(xpal.documents.User.objects(tgid=tgid))
        elif mobile_num is not None:
            resp = list(xpal.documents.User.objects(mobile_num=mobile_num))
        elif user_id is not None:
            resp = list(xpal.documents.User.objects(user_id=user_id))
        else:
            resp = list(xpal.documents.User.objects.all())
        if type(resp) == list and resp != []:
            status = "success"
        else:
            status = "error"
        return jsonify({"resp": resp, "status": status})

    def post(self, command=None):
        # app.logger.info("{}".format(request.get_json()))
        respdict = request.get_json()
        if command is None:
            try:
                if xpal.validate_user_dict(respdict)['status'] is True:
                    resp = xpal.create_user(respdict)
                    if type(resp) != list:
                        status = "error"
                    else:
                        status = "success"
                else:
                    status = "error"
                    resp = xpal.validate_user_dict(respdict)['message']
            except Exception as e:
                app.logger.error("{} {}".format(type(e), str(e)))
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        elif command == "import":
            try:
                # replace with bookinglist=xpal.importbookings(respdict) #91 #83
                resp = xpal.import_users(respdict)
                if type(resp) != list:
                    status = "error"
                else:
                    status = "success"
                for user in resp:
                    if "error" in user['status'].lower():
                        status = "error"
            except Exception as e:
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        elif command == "bulkdelete":
            try:
                if type(respdict) != list:
                    status = "error"
                    resp = "Bulk Delete Expects a list of user ids"
                else:
                    for user_id in respdict:
                        xpal.delete_user(user_id)
                    resp = "Deleted users {}".format(respdict)
                    status = "success"
            except Exception as e:
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        else:
            resp = "Unrecognized command"
            status = "error"
        return jsonify({"resp": resp, "status": status})

    def put(self, user_id):
        app.logger.info("{}".format(request.get_json()))
        respdict = request.get_json()
        try:
            if xpal.validate_user_dict(respdict, new=False)['status'] is True:
                resp = xpal.update_user(user_id, respdict)
                if type(resp) != list:
                    status = "error"
                else:
                    status = "success"
            else:
                status = "error"
                resp = xpal.validate_user_dict(
                    respdict, new=False)['message']
        except Exception as e:
            app.logger.error("{} {}".format(type(e), str(e)))
            resp = "{} {}".format(type(e), str(e))
            status = "error"
        return jsonify({"resp": resp, "status": status})

    def delete(self, user_id=None):
        if user_id is None:
            resp = "No user ID"
            status = "error"
        else:
            app.logger.info(
                "UserResource: Trying to delete user {}".format(user_id))
            try:
                resp = xpal.delete_user(user_id)
                if type(resp) == list:
                    status = "success"
                else:
                    status = "error"
            except Exception as e:
                app.logger.error("{} {}".format(type(e), str(e)))
                resp = "{} {}".format(type(e), str(e))
                status = "error"
        return jsonify({"resp": resp, "status": status})


if __name__ == '__main__':
    app.run(host="0.0.0.0")
