from flask_restful import Resource
from flask import request
from flask_jwt_extended import current_user, jwt_required
from MazdoorOnline_API.api.utils.helpers import user_required
from MazdoorOnline_API.models import Reviews, Order, ReviewsHistory, User
from MazdoorOnline_API.api.schemas import ReviewSchema, GiveReviewSchema
from MazdoorOnline_API.extensions import db


class ReviewResource(Resource):
    
    """Get review of a labor by id

    ---
    get:
      tags:
        - Reviews
      summary: Get review of a labor by id
      description: Get review of a labor by id
      parameters:
        - in: path
          name: labor_id
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
                    example: Labor review
                  review: ReviewSchema
    """
    method_decorators = [jwt_required()]

    def get(self, labor_id):
        schema = ReviewSchema()
        labor = User.query.get_or_404(labor_id)

        # check if user being reviews is even a labor or not
        if labor.role != 2:
            return {"error": "not allowed to review this user"}, 403

        review = Reviews.query.filter_by(labor_id=labor.id).first()

        if review is None:
            return {"error": "No review availible"}, 200

        return {"msg": "Labor review", "review": schema.dump(review)}, 200


class GiveReviewResource(Resource):

    """Review a labor by order_id

    ---
    put:
      tags:
        - Reviews
      summary: Review a labor by order_id
      description: Review a labor by order_id
      requestBody:
        content:
          application/json:
            schema:
              GiveReviewSchema
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Review updated successfully
    """

    method_decorators = [jwt_required()]

    @user_required
    def put(self):
        user = current_user

        schema = GiveReviewSchema()
        args = schema.load(request.json)

        order_id = args["order_id"]
        review_val = args["review_val"]

        if review_val > 5:
            return {"error": "You can't give a review value of higher than 5."}, 403

        order = Order.query.get_or_404(order_id)

        if order.is_active and not order.is_completed:
            return {"error": "You can't review an incomplete order."}, 403

        if order.creator_id != user.id:
            return {"error": "You don't have permission to access this route"}, 403

        # check if review already exists
        if ReviewsHistory.query.filter_by(order_id=order_id).first() is not None:
            return {"error": "You have already reviewed this order"}, 403

        # now to add new review to review history

        review_history = ReviewsHistory(
            order_id=order_id,
            review_val=review_val,
            labor_id=order.labor.id,
        )

        db.session.add(review_history)

        review = Reviews.query.filter_by(labor_id=order.labor.id).first()

        review.total_reviews += 1

        review.review_val = (review.review_val + review_val) / review.total_reviews

        db.session.commit()

        return {"msg": "review updated successfully"}, 200
