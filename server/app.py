#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask import jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    response = [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]
    return jsonify(response)


# GET /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify(restaurant.to_dict()), 200



# DELETE /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)
    else:
        return jsonify({"error": "Restaurant not found"}), 404


# GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    response = [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]
    return jsonify(response)


# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        # Validate that price is between 1 and 30
        if not (1 <= price <= 30):
            return jsonify({"errors": ["Price must be between 1 and 30"]}), 400

        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        response = restaurant_pizza.to_dict(
            include={
                'pizza': ('id', 'name', 'ingredients'),
                'restaurant': ('id', 'name', 'address'),
                'id': 'id',
                'price': 'price',
                'pizza_id': 'pizza_id',
                'restaurant_id': 'restaurant_id'
            }
        )
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400



if __name__ == '__main__':
    app.run(port=5555, debug=True)
