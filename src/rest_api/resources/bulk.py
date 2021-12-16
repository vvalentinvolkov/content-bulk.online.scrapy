from flask import request
from flask_restful import Resource


class Bulk(Resource):
    def get(self):
        url_params = request.args
        return url_params
