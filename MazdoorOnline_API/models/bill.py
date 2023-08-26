from MazdoorOnline_API.extensions import db
from sqlalchemy.sql import func
from sqlalchemy import event


class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    base_rate = db.Column(db.Float, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    payment_at = db.Column(db.DateTime(timezone=True))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    order = db.relationship("Order", backref="bill", lazy='joined')


@event.listens_for(Bill.is_paid, 'set')
def set_payment_at(target, value, oldvalue, initiator):
    if value:
        target.payment_at = func.now()