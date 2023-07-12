from dataclasses import dataclass
from flask import Flask, jsonify, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey, Integer, ARRAY
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

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
    tablename = 'user'

    dni: str
    password: str
    name: str
    lastname: str
    username: str
    address: str
    orders: str
    email: str

    password = dbperro.Column(dbperro.String(10), nullable=False)
    name = dbperro.Column(dbperro.String(100), nullable=False)
    dni = dbperro.Column(dbperro.String(8), nullable=False, unique=True, primary_key=True)
    lastname = dbperro.Column(dbperro.String(50), nullable=False)
    username = dbperro.Column(dbperro.String(50), nullable=False)
    address = dbperro.Column(dbperro.String(100), nullable=False)
    orders = dbperro.Column(dbperro.String, nullable=False)
    email = dbperro.Column(dbperro.String(50), nullable=False)

@dataclass
class Order(dbperro.Model):
    tablename = 'order'

    id: int
    userID: int
    products: str
    totalPrice: float
    date: str

    id = dbperro.Column(dbperro.Integer, primary_key=True)
    userID = dbperro.Column(dbperro.Integer, nullable=False)
    products=dbperro.Column(dbperro.String, nullable=False)
    totalPrice=dbperro.Column(dbperro.Float, nullable=False)
    date = dbperro.Column(dbperro.String(24), nullable=False)

    def __repr__(self):
        return f'<Order {self.id}>'

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
        user = User(password=data["password"], name=data["name"], address=data["address"], email=data["email"],dni=data["dni"],lastname=data["lastname"],orders=data["orders"])
        dbperro.session.add(user)
        dbperro.session.commit()
        return jsonify(user)

@app.route('/users/<user_dni>', methods=['GET', 'DELETE'])
def route_get_user(user_dni):
    if request.method == 'GET':
        user = User.query.filter_by(dni=user_dni).first()
        return jsonify(user)
    elif request.method == 'DELETE':
        user = User.query.get_or_404(user_dni)
        dbperro.session.delete(user)
        dbperro.session.commit()
        return 'SUCCESS'

    
@app.route('/products/category/<product_category>', methods=['GET'])
def route_get_category(product_category):
    if request.method == 'GET':
        products = Product.query.filter_by(category=product_category).all()
        return jsonify(products)
    
@app.route('/orders/<userID>/<order_ID>', methods=['GET'])
def route_get_order(userID, order_ID): 
    if request.method == 'GET':        
        order_query = Order.query.filter_by(userID=userID)
        if order_ID == 'last':
            order = order_query.order_by(Order.id.desc()).first()
        else:
            order = order_query.filter_by(id=order_ID).first()

        products = []
        productsID = order.products.split(',')

        for productID in productsID:
            product = Product.query.filter_by(id=productID).first()
            products.append(product)

        order.products = products

        return jsonify(order)
    
@app.route('/orders', methods=['GET', 'POST'])
def route_orders(): 
    if request.method == 'GET':
        orders = Order.query.all()
        return jsonify(orders)
    elif request.method == 'POST':
        data = request.get_json()
        order = Order(userID=data['userID'],products=data['products'],totalPrice=data['totalPrice'],date=data['date'])

        dbperro.session.add(order)
        dbperro.session.commit()

        user = User.query.filter_by(dni=data['userID']).first()
        print(order.id)
        user.orders += f'{order.id},'

        dbperro.session.add(user)
        dbperro.session.commit()
        return 'SUCCESS'
    
@app.route('/sign-in', methods=['POST'])
def signIn():
    if request.method == 'POST':
        credentials = request.get_json()
        email = credentials['email']
        password = credentials['password']
        
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            return {'status': 'SUCCESS', 'content': user.dni}
        return {'status': 'ERROR', 'content': 'El usuario no está registrado'}


@app.route('/sign-up', methods=['POST'])
def signUp():
    if request.method=='POST':
        data = request.get_json()
        name = data["name"]
        lastname = data["lastname"]
        username = data["username"]
        email = data["email"]
        password = data["password"]
        dni = data["dni"]
        address = data["address"]
        orders = ''

        if not lastname or not username or not email or not password:
            return 'Invalid'

        userEmail = User.query.filter_by(email=email).first()
        userId = User.query.filter_by(dni=dni).first()
        
        if userEmail or userId:
            return 'El usuario ya existe.'
        

        hashpassword = generate_password_hash(password)
        newUser = User(dni=dni,orders=orders,address=address,name=name, lastname=lastname,username=username, email=email, password=hashpassword)
        dbperro.session.add(newUser)
        dbperro.session.commit()

        return 'SUCCESS'

if __name__ == '__main__':
    app.run()