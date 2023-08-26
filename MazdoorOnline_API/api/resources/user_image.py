from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from MazdoorOnline_API.models import User
from MazdoorOnline_API.extensions import db
import cloudinary
import cloudinary.uploader
import uuid


class UserImageResource(Resource):
    """Single object resource

    ---
    get:
      tags:
        - user_profile_image
      summary: get the link to profile picture
      description: get the link to profile picture
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  profile_img_url:
                    type: string
                    example: https://www.example.com/test.png
        404:
          description: user does not exists
    post:
      tags:
        - user_profile_image
      summary: Updates profile picture
      description: Upload profile picture
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                 profile_pic_data:
                    type: string
                    format: binary
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  msg:
                    type: string
                    example: Profile image uploaded successfully.
        404:
          description: error occurred
    """

    method_decorators = [jwt_required()]
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS


    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return {"profile_img_url": user.profile_image_url}

    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        file = request.files['profile_pic_data']
        if file.filename == '':
            error = 'No file selected for uploading'
            return {"error": error}

        if file and self.allowed_file(file.filename):
            # this check is done to make sure if an image on the server
            # already exists then it is replaced rather than re-uploaded
            # this reduces redundancy

            if user.profile_image_name is None:
                # generate unique filename
                image_name = str(uuid.uuid4()).lower()
            else:
                image_name = user.profile_image_name
            res = cloudinary.uploader.upload(
                file=file,
                folder="MazdoorOnline_API/users/profile_images",
                overwrite=True,
                resource_type="image",
                public_id=image_name
            )

            user.profile_image_name = image_name
            user.profile_image_url = res['secure_url']
            db.session.commit()
            return {"msg": "Profile image uploaded successfully."}
        else:
            error = 'Allowed file types are png, jpg, jpeg, gif'
            return {"error": error}
