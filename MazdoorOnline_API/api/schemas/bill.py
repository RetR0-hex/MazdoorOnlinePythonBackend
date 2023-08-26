from MazdoorOnline_API.models import Bill
from MazdoorOnline_API.api.schemas import OrderSchema
from MazdoorOnline_API.extensions import ma, db


class BillSchema(ma.SQLAlchemyAutoSchema):
    order_info = ma.Nested(OrderSchema(only=("id", "created_at")))
    class Meta:
        model = Bill
        sqla_session = db.session
        load_instance = True

        exclude = ["order", "payment_at", "is_paid"]

        # category_name = ma.Function(lambda obj: obj.category.category.name, dump_only=True)
        # creator_name = ma.Function(lambda obj: obj.user.user.full_name, dump_only=True)
