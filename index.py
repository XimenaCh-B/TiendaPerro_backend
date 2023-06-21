from dataclasses import dataclass
from flask import Flask, jsonify, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, ARRAY
from app import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.dbperro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'my_secret_key'

dbperro = SQLAlchemy(app)

@dataclass
class Product(dbperro.Model):
    tablename = 'product'
    id: int
    name: str
    category: str
    description: str
    stock: int
    price: float
    image: str

    id = dbperro.Column(dbperro.Integer, primary_key=True)
    name = dbperro.Column(dbperro.String(255), nullable=False)
    category = dbperro.Column(dbperro.String(255), nullable=False)
    description = dbperro.Column(dbperro.String(255), nullable=False)
    stock = dbperro.Column(dbperro.Integer, nullable=False)
    price = dbperro.Column(dbperro.Float, nullable=False)
    image = dbperro.Column(dbperro.String(255), nullable=False)

    def __repr__(self):
        return f'<Product {self.id}>'

@dataclass
class User(dbperro.Model):
    _tablename_ = 'user'
    password = dbperro.Column(dbperro.String(10), nullable=False)
    name = dbperro.Column(dbperro.String(100), nullable=False)
    dni = dbperro.Column(dbperro.String(8), nullable=False, unique=True, primary_key=True)
    lastname = dbperro.Column(dbperro.String(50), nullable=False)
    address = dbperro.Column(dbperro.String(100), nullable=False)
    orders = dbperro.Column(dbperro.ARRAY(Integer), nullable=False)
    email = dbperro.Column(dbperro.String(50), nullable=False)

class Order(dbperro.Model):
    tablename = 'order'
    ID = dbperro.Column(dbperro.Integer, unique=True, nullable=False, primary_key=True)
    USERDNI = dbperro.Column(dbperro.Integer, ForeignKey("user.dni"), nullable=False)
    PRODUCTSID=dbperro.Column(dbperro.ARRAY(Integer), nullable=False)
    TOTAL=dbperro.Column(dbperro.Integer, nullable=False)
    DATE = dbperro.Column(dbperro.DateTime, nullable=False)
    usuario = dbperro.relationship("User")

with app.app_context():
    dbperro.create_all()
    
@app.route('/products', methods=['GET', 'POST'])
def route_product():
    if request.method == 'GET':
        product = Product.query.all()
        return jsonify(product)
    elif request.method == 'POST':
        data = request.get_json()
        product = Product(name=data["name"], category=data["category"], description=data["description"], stock=data["stock"], price=data["price"], image=data["image"])
        dbperro.session.add(product)
        dbperro.session.commit()
        return jsonify(product)
    
@app.route('/products/<product_id>', methods=['DELETE', 'GET'])
def route_get_player(product_id):
    if request.method == 'DELETE':
        product = Product.query.get_or_404(product_id)
        dbperro.session.delete(product)
        dbperro.session.commit()
        return 'SUCCESS'
    elif request.method == 'GET':
        product = Product.query.filter_by(id=product_id).all()
        return jsonify(product)

@app.route('/users', methods=['GET','POST'])
def route_user():
    if request.method == 'GET':
        users = User.query.all()
        list_user=[]
        for user in users:
            list_user.append({
                    "password": user.password,
                    "name": user.name,
                    "dni": user.dni,
                    "lastname": user.lastname,
                    "address": user.address,
                    "orders": user.orders,
                    "email": user.email,
                    })
        return list_user 
    elif request.method == 'POST':
        data = request.get_json()
        user = User(password=data["password"], name=data["name"], address=data["address"], email=data("email"),dni=data("dni"),lastname=data("lastname"),orders=data("orders"))
        dbperro.session.add(user)
        dbperro.session.commit()
        return jsonify(user)

@app.route('/users/<user_dni>', methods=['GET'])
def route_get_user(user_dni):
    if request.method == 'GET':
        user = User.query.filter_by(dni=user_dni).first()
        return {
                "password": user.password,
                "name": user.name,
                "dni": user.dni,
                "lastname": user.lastname,
                "address": user.address,
                "orders": user.orders,
                "email": user.email,
                }
    elif request.method == 'DELETE':
        user = User.query.get_or_404(user_dni)
        dbperro.session.delete(user)
        dbperro.session.commit()
        return 'SUCCESS'
    
@app.route('/products/<category>', methods=['GET'])
def route_get_category(product_category):
    if request.method == 'GET':
        product = Product.query.filter_by(category=product_category).all()
        
        for i in product:
            return {
                "id": i.id,
                "name": i.name,
                "category": i.category,
                "description": i.description,
                "stock": i.stock,
                "price": i.price,
                "image": i.image,
                }
@app.route('/orders/<order_ID>', methods=['GET'])
def route_get_category(order_ID): 
    if request.method == 'GET':
        order = Order.query.filter_by(ID=order_ID).first()
        return jsonify(order)
               
if __name__ == '__main__':
    app.run(debug=True)
