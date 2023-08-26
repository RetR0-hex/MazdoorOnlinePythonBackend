from sqlalchemy.ext.hybrid import hybrid_property
from MazdoorOnline_API.extensions import db, pwd_context


class User(db.Model):
    """Basic user model"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(80), nullable=False, index=True)
    profile_image_name = db.Column(db.String(255), default=None)
    profile_image_url = db.Column(db.String(1000))
    email = db.Column(db.String(80), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(13), unique=True, nullable=False, index=True)
    _password = db.Column("password", db.String(255), nullable=False)
    role = db.Column(db.Integer)
    # 0 for admin, 1 for user, 2 for labour
    active = db.Column(db.Boolean, default=True)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = pwd_context.hash(value)

    def __repr__(self):
        return "<User %s>" % self.full_name

