from flask import abort
from functools import wraps
from flask_jwt_extended import current_user
from typing import List
from MazdoorOnline_API.models import Order
from MazdoorOnline_API.models import CurrentLocation
from MazdoorOnline_API.models import CurrentActiveOrder
from geopy.distance import distance


def labor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role == 1:
            abort(403, description="You are not allowed to access this route")
        return f(*args, **kwargs)

    return wrapper


def convert_seconds_to_hours(time_in_seconds):
    hours, remainder = divmod(time_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return hours, minutes


# todo write a helper function to return order that are near to labor
def near_order(orders: List[Order]):
    # first get current location of labor
    user = current_user
    location_labor = CurrentLocation.query.filter_by(user_id=user.id).first()

    # now find the locations of order creators
    less_distance_orders = []
    orders_location = []
    for order in orders:
        temp_location = CurrentLocation.query.filter_by(user_id=order.creator_id).first()
        orders_location.append(temp_location)

    # to find the distance between two points, in our case order.creator.latitude, order.creator.latitude
    # and labor.latitude and labor.longitude we will use haversine formula
    # and return all labors which are less than 25KM away

    for i in range(len(orders)):
        dist_btw_labor_order = distance((location_labor.latitude, location_labor.longitude),
                                        (orders_location[i].latitude, orders_location[i].longitude)).km

        if dist_btw_labor_order < 25:
            less_distance_orders.append(orders[i])

    return less_distance_orders


def check_near_order(order: Order):
    user = current_user
    location_labor = CurrentLocation.query.filter_by(user_id=user.id).first()
    order_location = CurrentLocation.query.filter_by(user_id=order.creator_id).first()
    dist_btw_labor_order = distance((location_labor.latitude, location_labor.longitude),
                                    (order_location.latitude, order_location.longitude)).km

    if dist_btw_labor_order < 25:
        return True

    return False

def user_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role == 2:
            abort(403, description="You are not allowed to access this route")
        return f(*args, **kwargs)

    return wrapper