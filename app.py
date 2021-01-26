import os
import time
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

API_VERSION = 'v1'
API_PATH = '/api/{}'.format(API_VERSION)

app = Flask(__name__)
app.secret_key = "PALO"
api = Api(app)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

jwt = JWT(app, authenticate, identity)

items = []


class Item(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        name = parser.parse_args().get('name')
        if name:
            item = next(filter(lambda x: x['name'] == name, items), None)
            return {'item': item}, 200 if item is not None else 404
        else:
            return {'message': "malformed body"}, 400

    @jwt_required()
    def post(self):
        request_data = request.get_json(force=True)
        name = request_data['name']
        if next(filter(lambda x: x['name'] == name, items), None) is not None:
            return {"message": "{} already exists".format(name)}, 400
        item = {
            'id': len(items) + 1,
            'name': name,
            'price': request_data['price'],
            'create_time': round(time.time())
        }
        items.append(item)
        return item, 201

    @jwt_required()
    def delete(self):
        global items
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        name = parser.parse_args().get('name')
        items = list(filter(lambda x: x['name'] != name, items))
        return {'items': items}

    def put(self):
        request_data = request.get_json()
        name = request_data['name']
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


class ItemID(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        _id = parser.parse_args().get('id')
        if _id:
            item = next(filter(lambda x: x['id'] == _id, items), None)
            return {'item': item}, 200 if item is not None else 404
        else:
            return {"message":'malformed request body'}, 400


class ItemList(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sort', type=int, required=False)
        _sort = int(parser.parse_args().get('sort'))
        print(_sort)
        if _sort or _sort == 0:
            # sort by create time desc
            if _sort == 0:
                copy = sorted(items, key=lambda k: k['create_time'], reverse=True)
                print(copy)
                return {'items': copy}
            # sort by create time asc
            elif _sort == 1:
                copy = sorted(items, key=lambda k: k['create_time'], reverse=False)
                print(copy)
                return {'items': copy}
            # sort by name asc
            elif _sort == 2:
                copy = sorted(items, key=lambda k: k['name'], reverse=False)
                return {'items': copy}
            elif _sort == 3:
                copy = sorted(items, key=lambda k: k['name'], reverse=True)
                return {'items': copy}
        else:
            return {'items': items}


api.add_resource(Item, '{}/item'.format(API_PATH))
api.add_resource(ItemList, '{}/items'.format(API_PATH))
api.add_resource(ItemID, '{}/item_id'.format(API_PATH))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



