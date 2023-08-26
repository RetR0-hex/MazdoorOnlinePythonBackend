from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from MazdoorOnline_API.models import Order, CurrentActiveOrder, LaborDetail, CurrentLocation
from MazdoorOnline_API.api.schemas import OrderSchema, AcceptOrderSchema, OrderDetailSchema, LocationSchema
from MazdoorOnline_API.extensions import db
from MazdoorOnline_API.api.utils.helpers import labor_required, near_order, user_required, check_near_order


class OrderResource(Resource):
    """get Order

    ---
    get:
      tags:
        - Order
      summary: Get Order my id
      description: Get Order my id
      parameters:
        - in: path
          name: order_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  order:
                    type: object
                    items:
                      $ref: '#/components/schemas/OrderDetailSchema'
    """
    # method_decorators = [jwt_required()]

    def get(self, order_id):
        order = Order.query.get_or_404(order_id)
        schema = OrderDetailSchema()
        return {"order": schema.dump(order)}, 200


class OrderLocationResource(Resource):
    """get Order

    ---
    get:
      tags:
        - Order
      summary: Get Order my id
      description: Get Order my id
      parameters:
        - in: path
          name: order_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  order:
                    type: object
                    items:
                      $ref: '#/components/schemas/LocationSchema'
    """
    method_decorators = [jwt_required()]
    def get(self, order_id):
        order = Order.query.get_or_404(order_id)
        current_location = CurrentLocation.query.filter_by(user_id=order.creator_id).first()
        schema = LocationSchema()
        return {"location": schema.dump(current_location)}, 200


class OrderCreateResource(Resource):
    """ Update Order

    ---
    post:
      tags:
        - Order
      summary: Create an Order
      description: Create a new order
      requestBody:
        content:
          application/json:
            schema:
              OrderSchema
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Order created
                  order: OrderSchema


    """

    method_decorators = [jwt_required()]

    @user_required
    def post(self):
        user_id = get_jwt_identity()
        schema = OrderSchema()
        order = schema.load(request.json)
        order.creator_id = user_id
        order.is_active = True
        db.session.add(order)
        db.session.flush()

        # when a order is created, also add it to CurrentActiveOrder

        # TODO if an active order already exists don't let this user create another entry
        # but for now we will let the user do that for Debugging purposes

        active_order = CurrentActiveOrder.query.filter_by(creator_id=user_id).first()

        if active_order is not None:
            active_order.creator_id = user_id
            active_order.current_active_order = order.id

        else:
            active_order = CurrentActiveOrder(creator_id=order.creator_id, current_active_order=order.id)
            db.session.add(active_order)

        db.session.commit()

        # TODO WRITE A FUNCTION THAT SENDS TO ORDER NOTIFICATION TO LABOR

        return {"msg": "order created", "order": schema.dump(order)}, 201


class OrderCompleteResource(Resource):
    """complete Order

    ---
    get:
      tags:
        - Order
      summary: Complete Order my id
      description: Complete Order my id
      parameters:
        - in: path
          name: order_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: object
                    properties:
                      msg:
                        type: string
                        example: order completed successfully
    """

    method_decorators = [jwt_required()]

    @labor_required
    def get(self, order_id):

        user = current_user

        order = Order.query.get_or_404(order_id)
        if order.assigned_labor_id != user.id:
            return {"error": "you are not allowed to change this order"}, 403

        if order.is_completed:
            return {"error": "order is already completed"}, 403

        order.is_active = False
        order.is_completed = True

        db.session.commit()

        return {"msg": "Order completed successfully"}, 200


class CompletedOrderCheck(Resource):
    """Check if an order has been completed or not

    ---
    get:
      tags:
        - Order
      summary: Check completion of order
      description: Check completion of order
      parameters:
        - in: path
          name: order_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: object
                    properties:
                      is_completed:
                        type: bool
                        example: true
    """

    method_decorators = [jwt_required()]

    @user_required
    def get(self, order_id):

        user = current_user

        order = Order.query.get_or_404(order_id)
        if order.creator_id != user.id:
            return {"error": "you are not allowed to change this order"}, 403

        return {"is_completed": order.is_completed}, 200


class ActiveOrderResource(Resource):
    """GEt All active orders

    ---
    get:
      tags:
        - Order
      summary: get a list of all active orders valid for a labor
      description: get a list of all active orders valid for a labor
      responses:
        200:
          content:
            application/json:
              schema:
                properties:
                  orders:
                    type: array
                    items:
                      $ref: '#/components/schemas/OrderSchema'

    """

    method_decorators = [jwt_required()]

    @labor_required
    def get(self):
        order_schema = OrderSchema(many=True)
        user = current_user

        # check if user already has an active order, if yes reject the request
        if CurrentActiveOrder.query.filter_by(labor_id=user.id).first() is not None:
            return {"error": "you already have an active order."}, 403

        # query all orders that don't have an active assigned labor
        orders = Order.query.filter_by(assigned_labor_id=None)

        if not orders.all():
            return {"msg": "No active orders found."}, 204

        # find labor category
        labor_detail = LaborDetail.query.filter_by(labor_id=user.id).first()

        # filter by category of labor
        # TODO REMOVE THIS FOR DEBUGGING
        orders = orders.filter_by(category_id=labor_detail.category_id)

        # now filter out the orders which are not active/completed
        orders = orders.filter_by(is_active=True)
        orders = orders.filter_by(is_completed=False).all()

        if not orders:
            return {"msg": "No active orders found."}, 204

        # todo write a function that takes in a list of orders and returns back the
        # orders which are near to the labor based on his location

        orders = near_order(orders)

        if not orders:
            return {"error": "No active near you."}, 403

        return {"msg": "List of current active order.", "orders": order_schema.dump(orders)}, 200


class AcceptActiveOrderResource(Resource):
    """Accept an active order

    ---
    get:
      tags:
        - Order
      summary: Get current active orders associated with ur account
      description: Get current active orders associated with ur account
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Your current active orders.
                  order: OrderSchema
        403:
          description: no active orders
    post:
      tags:
        - Order
      summary: Accept an active order
      description: Accept an active order
      requestBody:
        content:
          application/json:
            schema:
              AcceptOrderSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: "Order Accepted successfully"
    """

    method_decorators = [jwt_required()]

    def get(self):
        user = current_user
        schema = OrderSchema()

        if user.role is 1:
            active_order = CurrentActiveOrder.query.filter_by(creator_id=user.id).first()
            if active_order is None:
                return {"error": "You currently have no active order"}, 403
            return {"msg": "Your current active orders.", "orders": schema.dump(active_order.order)}, 200

        elif user.role == 2:
            active_order = CurrentActiveOrder.query.filter_by(labor_id=user.id).first()
            if active_order is None:
                return {"error": "You currently have no active order"}, 403
            return {"msg": "Your current active orders.", "orders": schema.dump(active_order.order)}, 200

        else:
            return {"error": "You are not allowed to access this route"}, 403

    @labor_required
    def post(self):
        schema = AcceptOrderSchema()
        accept_order = schema.load(request.json)
        order = Order.query.get_or_404(accept_order['order_id'])
        user = current_user
        labor_detail = LaborDetail.query.filter_by(labor_id=user.id).first()

        # now to do all the checks before accepting this order

        # check if labor already has an active order
        if CurrentActiveOrder.query.filter_by(labor_id=user.id).first() is not None:
            return {"error": "you already have an active order."}, 403

        if order.category_id != labor_detail.category_id:
            return {"error": "Not allowed to accept this order."}, 403

        if order.assigned_labor_id is not None:
            return {"error": "Not allowed to accept this order."}, 403

        if not order.is_active and order.is_completed:
            return {"error": "Not allowed to accept this order."}, 403

        # write a function to check if its near labor
        # TODO REMOVE COMMENTS WHEN YOU CONNECT WITH THE APP
        # as right now the lat and long locations are empty
        if not check_near_order(order):
             return {"error": "Not allowed to accept this order."}, 403

        order.assigned_labor_id = user.id

        # create a record in the LaborCurrentActiveOrder about the current Order
        order_active = CurrentActiveOrder.query.filter_by(current_active_order=order.id).first()
        order_active.labor_id = user.id

        db.session.commit()

        return {"msg": "Order Accepted successfully"}, 200


class PendingOrderResource(Resource):
    """get active order status

    ---
    get:
      tags:
        - Order
      summary: Get Status of your pending order
      description: Get Status of your pending order
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  isAccepted:
                    type: bool
                    example: True.
        403:
          description: no active orders
    """

    method_decorators = [jwt_required()]

    @user_required
    def get(self):
        user_id = get_jwt_identity()

        # get current active orders of id
        # TODO  is a problem, as user can create more than one order......
        # TODO restrict users from creating more orders unless completed\
        # TODO GET PENDING ORDER STATUS BY ORDER_ID
        # TODO IF THERE IS ALREADY AN ORDER WITH NO LABOR ID REPLACE IT
        active_order = CurrentActiveOrder.query.filter_by(creator_id=user_id).first()

        if active_order is None:
            return {"error", "No active order associated with your account"}, 401

        if active_order.labor_id is None:
            print(active_order.labor_id)
            return {"isAccepted": False}, 200
        else:
            return {"isAccepted": True}, 200