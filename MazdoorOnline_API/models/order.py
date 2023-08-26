from MazdoorOnline_API.extensions import db
from sqlalchemy.sql import func
from sqlalchemy import event


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    desc = db.Column(db.String(512))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at = db.Column(db.DateTime(timezone=True), default=None)
    is_active = db.Column(db.Boolean, default=True)
    is_completed = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship("Category", backref="order", lazy='joined')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_labor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship("User", backref="order_creator", lazy='joined', foreign_keys=[creator_id])
    labor = db.relationship("User", backref="order_assigned_labor", lazy='joined', foreign_keys=[assigned_labor_id])


class CurrentActiveOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    labor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    current_active_order = db.Column(db.Integer, db.ForeignKey('order.id'))
    labor = db.relationship("User", backref="labor_current_active_order", foreign_keys=[labor_id])
    creator = db.relationship("User", backref="user_current_active_order", foreign_keys=[creator_id])
    order = db.relationship("Order", backref="current_active_order")



@event.listens_for(Order.is_completed, 'set')
def set_completed_at(target, value, oldvalue, initiator):
    if value:
        target.completed_at = func.now()
