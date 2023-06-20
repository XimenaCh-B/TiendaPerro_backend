from dataclasses import dataclass
from flask import Flask, jsonify, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.dbperro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'my_secret_key'

dbperro = SQLAlchemy(app)

@dataclass
class Product(dbperro.Model):
    tablename = 'producto'
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
    stock = dbperro.Column(dbperro.String(255), nullable=False)
    price = dbperro.Column(dbperro.String(255), nullable=False)
    image = dbperro.Column(dbperro.String(255), nullable=False)

    def __repr__(self):
        return f'<Product {self.id}>'

@dataclass
class User(dbperro.Model):
    _tablename_ = 'usuario'
    password = dbperro.Column(dbperro.String(10), nullable=False)
    name = dbperro.Column(dbperro.String(100), nullable=False)
    dni = dbperro.Column(dbperro.String(8), nullable=False, unique=True, primary_key=True)
    lastname = dbperro.Column(dbperro.String(50), nullable=False)
    address = dbperro.Column(dbperro.String(100), nullable=False)
    orders = dbperro.Column(dbperro.String(100), nullable=False)
    email = dbperro.Column(dbperro.String(100), nullable=False)

with app.app_context():
    dbperro.create_all()
    
@app.route('/', methods=['GET', 'POST'])
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
    
@app.route('/<product_id>', methods=['DELETE'])
def route_get_player(product_id):
    if request.method == 'DELETE':
        product = Product.query.get_or_404(product_id)
        dbperro.session.delete(product)
        dbperro.session.commit()
        return 'SUCCESS'

@app.route('/user', methods=['GET','POST'])
def route_user():
    if request.method == 'GET':
        user = User.query.all()
        return jsonify(user)
    elif request.method == 'POST':
        data = request.get_json()
        user = User(password=data["password"], name=data["name"], address=data["address"], email=data("email"),dni=data("dni"),lastname=data("lastname"),orders=data("orders"))
        dbperro.session.add(user)
        dbperro.session.commit()
        return jsonify(user)

if __name__ == '__main__':
    app.run(debug=True)
