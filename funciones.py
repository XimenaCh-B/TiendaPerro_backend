
from index import User
from flask import Blueprint,jsonify,request,flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import app,db
import requests

# -------------------------- USER REFERENCE ----------------------------
def signin():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        
        user = User.query.filter_by(email=email).first()

        if check_password_hash(user.password, password) and user:
            print("Login successful")
            return jsonify(email=email, password=password)
        return None

def signup():
    if request.method=='POST':
        name = request.json["name"]
        lastname = request.json["lastname"]
        username = request.json["username"]
        email = request.json["email"]
        password = request.json["password"]
        dni = request.json["dni"]
        address = request.json["address"]
        orders = request.json["orders"]
        if not lastname or not username or not email or not password:
            flash('Invalid')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Existing email')

        if len(password)>10:
            flash('la contraseña es demasiado grande')

        hashpassword = generate_password_hash(password)
        newUser = User(dni=dni,orders=orders,address=address,name=name, lastname=lastname,username=username, email=email, password=hashpassword)
        db.session.add(newUser)
        try:
            db.session.commit()
            return jsonify(dni=dni,orders=orders,address=address,name=name, lastname=lastname,username=username, email=email, password=hashpassword)
        except Exception as error:
            flash(error)
        flash('success')