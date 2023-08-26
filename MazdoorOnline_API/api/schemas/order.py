from MazdoorOnline_API.models import Order, Category
from MazdoorOnline_API.api.schemas import CategorySchema, UserSchema
from MazdoorOnline_API.extensions import ma, db


class OrderSchema(ma.SQLAlchemyAutoSchema):
    id = ma.Int(dump_only=True)
    assigned_labor_id = ma.Int(dump_only=True)
    creator_id = ma.Int(dump_only=True)
    category = ma.Nested(CategorySchema(only=("name",)), dump_only=True)

    class Meta:
        model = Order
        sqla_session = db.session
        load_instance = True
        include_fk = True
        include_relationships = True

        exclude = ("is_active", "is_completed", "completed_at", "current_active_order", "labor", "bill", "reviewshistory", "created_at")


class AcceptOrderSchema(ma.Schema):
    order_id = ma.Int(required=True)


class OrderDetailSchema(ma.SQLAlchemyAutoSchema):
    id = ma.Int(dump_only=True)
    assigned_labor_id = ma.Int(dump_only=True)
    creator_id = ma.Int(dump_only=True)
    category = ma.Nested(CategorySchema(only=("name",)))
    creator = ma.Nested(UserSchema(only=("full_name", "phone_number", "email")))

    class Meta:
        model = Order
        sqla_session = db.session
        load_instance = True
        include_fk = True

        exclude = ("is_active", "is_completed", "completed_at", "current_active_order", "labor", "bill", "reviewshistory", "created_at")
