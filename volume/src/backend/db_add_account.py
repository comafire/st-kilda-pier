from run import db
from models.account import Account

import sqlalchemy
import os, uuid, base62
from passlib.hash import pbkdf2_sha256 as sha256

# add Account
account = Account()
account.id = "user"
account.pw = sha256.hash("user")
account.level = "U"
account.active = "Y"

db.session.add(account)
db.session.commit()
