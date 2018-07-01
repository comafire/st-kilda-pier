from run import db
from passlib.hash import pbkdf2_sha256 as sha256

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.String(32), primary_key = True)
    pw = db.Column(db.String(256), nullable = False)
    level = db.Column(db.String(1), nullable = False)
    active = db.Column(db.String(1), nullable = False, default = "N")
    create_datetime = db.Column(db.DateTime, nullable = False, default = db.text('NOW()'))
    update_datetime = db.Column(db.DateTime, nullable = False, default = db.text('NOW()'), onupdate = db.text('NOW()'))

    @staticmethod
    def get_account(id):
        return Account.query.filter_by(id = id).first()

    @staticmethod
    def verify(id, pw):
        account = Account.query.filter_by(id = id).first()
        if not account:
            return None
        if not sha256.verify(pw, account.pw):
            return None
        if account.active != "Y":
            return None
        return account

    @staticmethod
    def get_level(id):
        account = Account.query.filter_by(id = id).first()
        if not account:
            return ""
        return account.level
