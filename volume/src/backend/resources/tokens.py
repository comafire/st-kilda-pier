from flask import jsonify
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt
)

from http import HTTPStatus
from run import db

import sys
sys.path.append('..')
from models.account import Account
from models.token import RevokedToken
from passlib.hash import pbkdf2_sha256 as sha256

token_fields = {
    'id' : fields.String,
    'level' : fields.String,
    'access_token' : fields.String,
    'refresh_token' : fields.String
}

class Tokens(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required = True)
        parser.add_argument('pw', required = True)
        args = parser.parse_args()

        account = Account.verify(args['id'], args['pw'])
        if not account:
            return {}, HTTPStatus.FORBIDDEN

        token = {}
        token['id'] = account.id
        token['level'] = account.level
        token['access_token'] = create_access_token(identity = account.id)
        token['refresh_token'] = create_refresh_token(identity = account.id)
        return token, HTTPStatus.CREATED

    @jwt_refresh_token_required
    def put(self):
        curr_id = get_jwt_identity()

        token = {}
        token['access_token'] = create_access_token(identity = curr_id)
        return token, HTTPStatus.OK

    @jwt_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)

            db.session.add(revoked_token)
            db.session.commit()

            return {'message': 'Access token has been revoked'}, HTTPStatus.OK
        except Exception as e:
            return {'message': "Something went wrong: {}".format(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
