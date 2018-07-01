from flask_restful import Resource, reqparse, fields, marshal_with
from flask import jsonify

from http import HTTPStatus

class Hello(Resource):
    def get(self):
        return jsonify({'status':'SUCCESS', 'message':'Hello!!'})

    def post(self):
        return {'status':'SUCCESS', 'message':'Hello!!'}, HTTPStatus.CREATED
