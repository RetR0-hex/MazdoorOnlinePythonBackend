from MazdoorOnline_API.models import Category
from MazdoorOnline_API.extensions import ma, db


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        sqla_session = db.session
        load_instance = True
        fields = ("id", "name", "base_rate_per_hour")
