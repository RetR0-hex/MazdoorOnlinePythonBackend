from MazdoorOnline_API.models import CurrentLocation
from MazdoorOnline_API.extensions import ma, db


class LocationSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = CurrentLocation
        sqla_session = db.session
        load_instance = True
        fields = ("latitude", "longitude")
