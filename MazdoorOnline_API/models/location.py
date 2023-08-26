from MazdoorOnline_API.extensions import db
from sqlalchemy.sql import func


class LocationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class CurrentLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @staticmethod
    def update_location(lat, long, user_id):
        curr_location = CurrentLocation.query.filter_by(user_id=user_id).first()
        if curr_location is None:
            curr_location = CurrentLocation(
                latitude=lat,
                longitude=long,
                user_id=user_id
            )
            db.session.add(curr_location)
            db.session.commit()
        else:
            curr_location.latitude = lat
            curr_location.longitude = long
            db.session.commit()
