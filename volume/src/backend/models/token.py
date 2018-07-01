from run import db

class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'

    jti = db.Column(db.String(120), primary_key = True)

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)
