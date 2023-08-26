from MazdoorOnline_API.models import Reviews
from MazdoorOnline_API.extensions import ma, db


class ReviewSchema(ma.SQLAlchemyAutoSchema):
    review_val = ma.Int(dump_only=True)
    labor_name = ma.Function(lambda obj: obj.labor.name)

    class Meta:
        model = Reviews
        sqla_session = db.session
        load_instance = True

        exclude = ("id", "labor_id")

        #category_name = ma.Function(lambda obj: obj.category.category.name, dump_only=True)
        #creator_name = ma.Function(lambda obj: obj.user.user.full_name, dump_only=True)


class GiveReviewSchema(ma.Schema):
    order_id = ma.Int(required=True)
    review_val = ma.Float(required=True)
