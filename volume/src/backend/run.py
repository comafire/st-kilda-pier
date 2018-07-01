from flask import Flask, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os, uuid, base62

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET"]

DB_HOST = "mysql-skp"
DB_USER = "root"
DB_PW =  os.environ['MYSQL_ROOT_PASSWORD']
DB_NAME = "flask_skp"
DB_ENGINE_URI = "mysql://{}:{}@{}/{}".format(DB_USER, DB_PW, DB_HOST, DB_NAME)

app.config['SQLALCHEMY_POOL_RECYCLE'] = 60
app.config['SQLALCHEMY_DATABASE_URI'] = DB_ENGINE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.environ["FLASK_SECRET"]
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

jwt = JWTManager(app)
db = SQLAlchemy(app)
api = Api(app)

import views

from models.token import RevokedToken
from models.account import Account

from resources.hello import Hello
from resources.tokens import Tokens
from resources.accounts import Accounts, AccountsId

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklisted(jti)

api.add_resource(Hello, '/v1/hello')
api.add_resource(Tokens, '/v1/tokens')
api.add_resource(Accounts, '/v1/accounts')
api.add_resource(AccountsId, '/v1/accounts/<string:id>')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)
