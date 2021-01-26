import os
from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required
from flasgger import Swagger

from security import authenticate, identity

app = Flask(__name__)
app.secret_key = "PALO"
api = Api(app)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
swagger = Swagger(app)

jwt = JWT(app, authenticate, identity)

items = []


class Item(Resource):

    def get(self, name):
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'item': item}, 200 if item is not None else 404

    @jwt_required()
    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None) is not None:
            return {"message": "{} already exists".format(name)}, 400

        request_data = request.get_json(force=True)
        item = {
            'id': len(items) + 1,
            'name': name,
            'price': request_data['price']
        }
        items.append(item)
        return item, 201

    @jwt_required()
    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'items': items}

    def put(self, name):
        request_data = request.get_json()
        item = next(filter(lambda x: x['name'] == name, items), None)
        if item is None:
            item = {
                'id': len(items) + 1,
                'name': name,
                'price': request_data['price']
            }
            items.append(item)
        else:
            item.update(request_data)
        return item


class ItemList(Resource):

    def get(self):
        return {'items': items}


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



