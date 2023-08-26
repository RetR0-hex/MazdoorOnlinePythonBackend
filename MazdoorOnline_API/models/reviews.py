from MazdoorOnline_API.extensions import db


class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    review_val = db.Column(db.Float, default=4.00)
    # todo add total reviews automatic functionality
    total_reviews = db.Column(db.Integer, default=1)
    labor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    labor = db.relationship("User", backref="reviews")


class ReviewsHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    review_val = db.Column(db.Float, default=1.00)
    labor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    labor = db.relationship("User", backref="reviewshistory")
    order = db.relationship("Order", backref="reviewshistory")

