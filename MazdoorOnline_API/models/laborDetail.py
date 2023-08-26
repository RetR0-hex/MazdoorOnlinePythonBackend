from MazdoorOnline_API.extensions import db


class LaborDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    labor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    reviews_id = db.Column(db.Integer, db.ForeignKey('reviews.id'))
    labor = db.relationship("User", backref="labordetail")
    category = db.relationship("Category", backref="labordetail")
    review = db.relationship("Reviews", backref="labordetail")