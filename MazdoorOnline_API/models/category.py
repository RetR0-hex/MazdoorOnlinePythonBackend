from MazdoorOnline_API.extensions import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    name = db.Column(db.String(160), index=True, nullable=False)
    base_rate_per_hour = db.Column(db.Integer, nullable=False)
    base_rate_per_km = db.Column(db.Integer, nullable=False)