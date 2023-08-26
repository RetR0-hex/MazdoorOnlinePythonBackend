from flask_restful import Resource
from MazdoorOnline_API.api.schemas import CategorySchema
from MazdoorOnline_API.models import Category


class CategoryResource(Resource):
    """Category Get all

    ---
    get:
      tags:
        - category
      summary: Get a list of categories with data
      description: Get a list of categories with data
      responses:
        200:
          content:
            application/json:
              schema:
                type: object
                properties:
                  categories:
                    type: array
                    items:
                      $ref: '#/components/schemas/CategorySchema'


    """


    def get(self):
        categories = Category.query.all()
        schema = CategorySchema(many=True)
        return {"categories": schema.dump(categories)}, 200
