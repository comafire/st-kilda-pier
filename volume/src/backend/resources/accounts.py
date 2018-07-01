from flask_restful import Resource, reqparse, fields, marshal_with
from flask import jsonify
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

from models.account import Account
from passlib.hash import pbkdf2_sha256 as sha256

account_fields = {
    'id' : fields.String,
    'level' : fields.String,
    'create_datetime' : fields.String,
    'update_datetime' : fields.String
}

class Accounts(Resource):
    # create new user
    @marshal_with(account_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', required = True)
        parser.add_argument('pw', required = True)
        parser.add_argument('level', required = True)
        args = parser.parse_args()

        account = Account.get_account(args['id'])
        if account:
            return {'msg': "id is already existed"}, HTTPStatus.CONFLICT

        if args['level'] != "U":
            return {'msg': "unknown account level"}, HTTPStatus.BAD_REQUEST

        account = Account()
        account.id = args['id']
        account.pw = sha256.hash(args['pw'])
        account.level = args['level']
        account.active = "N"

        try:
            db.session.add(account)
            db.session.commit()

            return account, HTTPStatus.CREATED
        except Exception as e:
            return {'msg': "fail to create account {}".format(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

class AccountsId(Resource):
    @jwt_required
    @marshal_with(account_fields)
    def put(self, id):
        curr_id = get_jwt_identity()

        parser = reqparse.RequestParser()
        parser.add_argument('pw', required = True)
        parser.add_argument('active', required = True)
        args = parser.parse_args()

        if args['active'] not in ["Y", "N"]:
            return {}, HTTPStatus.BAD_REQUEST

        account = Account.get_account(curr_id)
        if not account:
            return {}, HTTPStatus.FORBIDDEN
        if account.level != "A":
            if curr_id != id:
                return {}, HTTPStatus.FORBIDDEN

        account.pw = sha256.hash(args['pw'])
        account.active = args['active']

        try:
            db.session.add(account)
            db.session.commit()

            return {}, HTTPStatus.OK
        except Exception as e:
            return {'msg': "fail to update account {}".format(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @jwt_required
    @marshal_with(account_fields)
    def get(self, id):
        curr_id = get_jwt_identity()

        account = Account.get_account(curr_id)
        if not account:
            return {}, HTTPStatus.FORBIDDEN
        if account.level != "A":
            if curr_id != id:
                return {}, HTTPStatus.FORBIDDEN

        return account, HTTPStatus.OK

    @jwt_required
    def delete(self, id):
        curr_id = get_jwt_identity()

        account = Account.get_account(curr_id)
        if not account:
            return {}, HTTPStatus.FORBIDDEN
        if account.level != "A":
            if curr_id != id:
                return {}, HTTPStatus.FORBIDDEN

        db.session.delete(account)
        db.session.commit()
        return {}, HTTPStatus.OK
