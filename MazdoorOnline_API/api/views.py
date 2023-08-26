from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from MazdoorOnline_API.extensions import apispec
from MazdoorOnline_API.api.resources import (
    UserResource,
    UserList,
    UserImageResource,
    CurrentUserDataResource,
    CategoryResource,
    OrderResource,
    OrderLocationResource,
    OrderCreateResource,
    OrderCompleteResource,
    PendingOrderResource,
    ActiveOrderResource,
    AcceptActiveOrderResource,
    BillCreationResource,
    BillResource,
    BillPaymentResource,
    ReviewResource,
    GiveReviewResource,
    CompletedOrderCheck,
    BillPaymentCheckResource
)
from MazdoorOnline_API.api.schemas import (
    UserSchema,
    CategorySchema,
    OrderSchema,
    AcceptOrderSchema,
    BillSchema,
    ReviewSchema,
    GiveReviewSchema,
    OrderDetailSchema,
    LocationSchema
)


blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint)


api.add_resource(UserResource, "/users/get-user-by-id/<int:user_id>", endpoint="user_by_id")
api.add_resource(CurrentUserDataResource, "/users/current-user/", endpoint="current_user_data")
api.add_resource(UserList, "/users", endpoint="users")
api.add_resource(UserImageResource, '/user/profile-images', endpoint='profile_images')
api.add_resource(CategoryResource, '/categories', endpoint='categories')
api.add_resource(OrderResource, '/orders/get-order-by-id/order/<int:order_id>', endpoint='order_by_id')
api.add_resource(OrderLocationResource, '/orders/get-location-by-id/order/<int:order_id>', endpoint='location_by_id')
api.add_resource(OrderCreateResource, '/orders/create-order/order', endpoint='create_order')
api.add_resource(OrderCompleteResource, '/orders/complete-order/order/<int:order_id>/', endpoint='complete_order_by_id')
api.add_resource(CompletedOrderCheck, '/orders/check-complete-order/order/<int:order_id>/', endpoint='check_complete_order_by_id')
api.add_resource(ActiveOrderResource, '/orders/active-orders', endpoint='get_active_orders')
api.add_resource(PendingOrderResource, '/orders/active-orders/pending', endpoint='get_pending_orders')
api.add_resource(AcceptActiveOrderResource, '/orders/active-orders/order/accept', endpoint='accept_active_order')
api.add_resource(BillCreationResource, '/bills/create-bill', endpoint='create_new_bill')
api.add_resource(BillResource, '/bills/get-bill-by-order-id/bill/<int:order_id>', endpoint='get_bill_info')
api.add_resource(BillPaymentResource, '/bills/pay-bill-by-id/bill/<int:bill_id>', endpoint='pay_bill_by_id')
api.add_resource(BillPaymentCheckResource, '/bills/check-bill-payment/bill/<int:bill_id>', endpoint='check_bill_payment_by_id')
api.add_resource(ReviewResource, '/reviews/review-by-labor-id/review/<int:labor_id>', endpoint='review_by_labor_id')
api.add_resource(GiveReviewResource, '/reviews/give-review/review/', endpoint='review_order')


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.components.schema("CategorySchema", schema=CategorySchema)
    apispec.spec.components.schema("OrderSchema", schema=OrderSchema)
    apispec.spec.components.schema("OrderDetailSchema", schema=OrderDetailSchema)
    apispec.spec.components.schema("AcceptOrderSchema", schema=AcceptOrderSchema)
    apispec.spec.components.schema("BillSchema", schema=BillSchema)
    apispec.spec.components.schema("ReviewSchema", schema=ReviewSchema)
    apispec.spec.components.schema("GiveReviewSchema", schema=GiveReviewSchema)
    apispec.spec.components.schema("LocationSchema", schema=LocationSchema)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)
    apispec.spec.path(view=UserImageResource, app=current_app)
    apispec.spec.path(view=CategoryResource, app=current_app)
    apispec.spec.path(view=OrderResource, app=current_app)
    apispec.spec.path(view=OrderCreateResource, app=current_app)
    apispec.spec.path(view=OrderCompleteResource, app=current_app)
    apispec.spec.path(view=ActiveOrderResource, app=current_app)
    apispec.spec.path(view=AcceptActiveOrderResource, app=current_app)
    apispec.spec.path(view=PendingOrderResource, app=current_app)
    apispec.spec.path(view=BillCreationResource, app=current_app)
    apispec.spec.path(view=BillResource, app=current_app)
    apispec.spec.path(view=BillPaymentResource, app=current_app)
    apispec.spec.path(view=ReviewResource, app=current_app)
    apispec.spec.path(view=GiveReviewResource, app=current_app)
    apispec.spec.path(view=CurrentUserDataResource, app=current_app)
    apispec.spec.path(view=OrderLocationResource, app=current_app)
    apispec.spec.path(view=CompletedOrderCheck, app=current_app)
    apispec.spec.path(view=BillPaymentCheckResource, app=current_app)

@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
