from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import Column, Integer, String, DateTime
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, decode_token

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kavya'
app.config['JWT_SECRET_KEY'] = 'kavya'
jwt = JWTManager(app)



basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'bookstore.db')
db = SQLAlchemy(app)

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("Database is created")

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print("DB is dropped")
    

    
class user(db.Model):
    __tablename__="USER"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    pwd = db.Column(db.String, nullable=False)
    datecreated = db.Column(db.DateTime, default=datetime.now())
    
    def todict(self):
        return {
            'id':self.id,
            'username':self.username,
            'email':self.email,
            'pwd':self.pwd,
            'datecreated':self.datecreated
        }
@app.route('/')
def root():
    return jsonify("Thank you for using bookstore application")

@app.route('/user/register',methods=['POST'])
def register():
    data=request.get_json()
    
    #Scenario where no details are entered.
    if not data:
        return jsonify("No data is provided here"),400
    
    username=data.get('username')
    email=data.get('email')
    pwd=data.get('password')
    
    #scenario where any details are missing during registration
    if username is None or email is None or pwd is None:
        return jsonify("username, email or pwd is missing")
    
    #scenario where user already registered.
    exist=user.query.filter_by(email=email).first()
    if exist:
        return jsonify("User is already registered"),400
    
    new_user=user(username=username,email=email,pwd=pwd)
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.todict()), 201
    
    
@app.route('/user/login', methods=['POST'])
def login():
    data=request.get_json()
    
    #Scenario where no details are entered
    if not data:
        return jsonify("No details are entered"),400
    
    email=data.get("email")
    pwd=data.get("pwd")
    
    #Scenario where one of the details is missing
    if email is None or pwd is None:
        return jsonify("email or password is missing")
    
    x=user.query.filter_by(email=email,pwd=pwd).first()
    
    if x:
        access_token=create_access_token(identity={'email':email})
        return jsonify(access_token=access_token),200
    return jsonify("Invalid credentials")

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify({"msg": f"Hello, {current_user['email']}!"}), 200
    
    
if __name__ == '__main__':
    app.run(debug=True)
