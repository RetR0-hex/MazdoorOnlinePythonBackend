from flask import request, jsonify, Blueprint, current_app as app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from MazdoorOnline_API.models import CurrentLocation
from MazdoorOnline_API.extensions import pwd_context, jwt, apispec
from MazdoorOnline_API.auth.helpers import (
    revoke_token,
    is_token_revoked,
    add_token_to_database,
    create_user,
)

blueprint = Blueprint("location", __name__, url_prefix="/location")


@blueprint.route('/update_location', methods=["PUT"])
@jwt_required()
def update_location():

    """Update location of a user

    ---
    post:
      tags:
        - location
      summary: Updates location
      description: Updates the current location of user on the database
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                latitude:
                  type: float
                  example: 45.24245322
                  required: true
                longitude:
                  type: float
                  example: 45.24245322
                  required: true
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Location Updated successfully
        400:
          description: bad request
    """

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    latitude = float(request.json.get("latitude", None))
    longitude = float(request.json.get("longitude", None))
    if not latitude or not longitude:
        return jsonify({"msg": "Missing latitude or longitude"}), 400

    user_id = get_jwt_identity()
    CurrentLocation.update_location(lat=latitude, long=longitude, user_id=user_id)
    return jsonify({"msg": "Location updated successfully"}), 200


@blueprint.route('/get-location-by-user-id/<int:user_id>', methods=["GET"])
@jwt_required()
def get_location_by_user_id(user_id):

    """Get Location by user_id

    ---
    get:
      tags:
        - location
      summary: Get Location by user_id
      description: Get Location by user_id
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
                latitude:
                  type: float
                  example: 45.24245322
                longitude:
                  type: float
                  example: 45.24245322
    """
    print(user_id)

    location = CurrentLocation.query.filter_by(user_id=user_id).first()

    if location is None:
        return jsonify({"msg": "No User Found"}), 400

    else:
        return jsonify({"latitude": location.latitude, "longitude": location.longitude})








@blueprint.before_app_first_request
def register_views():
    apispec.spec.path(view=update_location, app=app)
    apispec.spec.path(view=get_location_by_user_id, app=app)
