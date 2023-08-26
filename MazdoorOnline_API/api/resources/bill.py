from flask_restful import Resource, reqparse
from flask_jwt_extended import current_user, jwt_required
from MazdoorOnline_API.api.utils.helpers import labor_required
from MazdoorOnline_API.models import Order, Bill, CurrentActiveOrder
from MazdoorOnline_API.api.schemas.bill import BillSchema
from MazdoorOnline_API.extensions import db
from MazdoorOnline_API.api.utils.helpers import convert_seconds_to_hours


class BillResource(Resource):
    """Get Bill by order_id

    ---
    get:
      tags:
        - Bill
      summary: Get bill information by order_id
      description: Get bill information by order_id
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
                  msg:
                    type: string
                    example: Bill of order_id
                  bill: BillSchema
    """

    method_decorators = [jwt_required()]

    def get(self, order_id):
        schema = BillSchema()

        user = current_user

        order = Order.query.get_or_404(order_id)

        if order.is_active and not order.is_completed:
            return {"error": "Order hasn't been completed yet."}, 403

        if user.role is 1 and order.creator_id is not user.id:
            return {"error": "You are not allowed to access this route."}, 403

        if user.role is 2 and order.assigned_labor_id is not user.id:
            return {"error": "You are not allowed to access this route."}, 403

        if order.assigned_labor_id is None:
            return {"error": "Order hasn't been completed yet."}, 403

        bill = Bill.query.filter_by(order_id=order.id).first()

        if bill is None:
            return {"error": "No bill has been generated for this this order yet."}, 403

        return {"msg": f"Bill of Order: {order.id}", "bill": schema.dump(bill)}, 200


class BillPaymentCheckResource(Resource):

    """Check if a bill has been paid or not

    ---
    get:
      tags:
        - Bill
      summary: Check payment of bill
      description: Check payment of bill
      parameters:
        - in: path
          name:  bill_id
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
                      is_payment:
                        type: bool
                        example: true
    """

    method_decorators = [jwt_required()]

    def get(self, bill_id):

        user = current_user

        bill = Bill.query.get_or_404(bill_id)

        order = Order.query.get_or_404(bill.order_id)

        if order.is_active and not order.is_completed:
            return {"error": "Order hasn't been completed yet."}, 403

        if user.role is 1 and order.creator_id is not user.id:
            return {"error": "You are not allowed to access this route."}, 403

        if user.role is 2 and order.assigned_labor_id is not user.id:
            return {"error": "You are not allowed to access this route."}, 403

        if order.assigned_labor_id is None:
            return {"error": "Order hasn't been completed yet."}, 403

        if bill is None:
            return {"error": "No bill has been generated for this this order yet."}, 403

        return {"is_payment": bill.is_paid}



class BillCreationResource(Resource):
    """Bill Creation

    ---
    post:
      tags:
        - Bill
      summary: Create a user
      description: Create a new user
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                order_id:
                    type: int
                    example: 1
      responses:
        201:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Bill Created
                  bill: BillSchema
    """

    method_decorators = [jwt_required()]

    @labor_required
    def post(self):
        req = reqparse.RequestParser()
        schema = BillSchema()
        req.add_argument('order_id', type=int, help='ID of order that needs to be generated')
        args = req.parse_args()

        order_id = args['order_id']
        user = current_user

        order = Order.query.get_or_404(order_id)

        # check if user is the assigned labor or not

        if order.assigned_labor_id is None:
            return {"error": "Order hasn't been completed yet."}, 403

        if user.id != order.assigned_labor_id:
            return {"error": "you are not allowed to generate this bill"}, 403

        if order.is_active and not order.is_completed:
            return {"error": "Order hasn't been completed yet."}, 403

        # now check if bill already exists for the order
        bill = Bill.query.filter_by(order_id=order_id).first()
        if bill is not None:
            return {"msg": "Bill already exists"}, 200

        # now to calculate bill
        difference = order.completed_at - order.created_at

        hours, minutes = convert_seconds_to_hours(difference.seconds)

        # TODO THIS DOESN"T PROPERLY CALCULATE HOUrs FIX THIS LATER IF START AND COMPLETED TIME ARE TWO DIFFERENT DAYS

        amount_for_hours = hours * order.category.base_rate_per_hour
        amount_for_minutes = minutes * (order.category.base_rate_per_hour / 60)

        total_amount = amount_for_hours + amount_for_minutes

        bill = Bill(base_rate=order.category.base_rate_per_hour, hours=hours,
                    minutes=minutes, amount=total_amount, order_id=order.id)

        db.session.add(bill)
        db.session.commit()

        db.session.flush()

        return {"msg": "Bill Created", "bill": schema.dump(bill)}, 200


class BillPaymentResource(Resource):

    """Pay bill by using bill ID
    ---
    get:
      tags:
        - Bill
      summary: Pay bill by using bill-iD, only accessible by labor
      description: Pay bill by using bill-iD, only accessible by labor
      parameters:
        - in: path
          name: bill_id
          schema:
            type: integer
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Bill Payment was successful.
    """

    method_decorators = [jwt_required()]

    @labor_required
    def get(self, bill_id):
        user = current_user
        bill = Bill.query.get_or_404(bill_id)

        if bill.is_paid:
            return {"error": "Bill is already payed"}, 403

        # now check if the bill is even associated with the labor
        if bill.order.assigned_labor_id != user.id:
            return {"error": "You are not allowed to change this bill."}, 403

        # now change the bill to paid status
        bill.is_paid = True

        # now remove this order associated with this bill from active order
        labor_active = CurrentActiveOrder.query.filter_by(labor_id=user.id).first()

        if labor_active is None:
            return {"error": "You have no active orders."}, 403

        if labor_active.order.id != bill.order.id:
            return {"error": "Your Bill order ID doesn't match with your active labor ID."}, 403

        # if the checks pass remove this entry from active order

        db.session.delete(labor_active)
        db.session.commit()

        return {"msg": "Bill Payment was successful."}, 200
