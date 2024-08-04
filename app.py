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
        
class Books(db.Model):
    __tablename__ = "Books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric, nullable=False)
    category = db.Column(db.String)
    cover_image = db.Column(db.String)  # URL to the cover image
    created_at = db.Column(db.DateTime, default=datetime.now())

    def todict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'price': str(self.price),  # Convert Decimal to string for JSON serialization
            'category': self.category,
            'cover_image': self.cover_image,
            'created_at': self.created_at.isoformat()  # Convert datetime to ISO format string
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
    
@app.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    data = request.get_json()
    
    # Scenario where no details are provided
    if not data:
        return jsonify({"msg": "No data provided"}), 400
    
    title = data.get('title')
    author = data.get('author')
    description = data.get('description')
    price = data.get('price')
    category = data.get('category')
    cover_image = data.get('cover_image')
    
    # Scenario where any details are missing
    if title is None or author is None or price is None:
        return jsonify({"msg": "Title, author, or price is missing"}), 400
    
    new_book = Books(
        title=title,
        author=author,
        description=description,
        price=price,
        category=category,
        cover_image=cover_image
    )
    
    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.todict()), 201

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Books.query.get(book_id)
    if book:
        return jsonify(book.todict()), 200
    return jsonify({"msg": "Book not found"}), 404

@app.route('/books', methods=['GET'])
def list_books():
    books = Books.query.all()
    return jsonify([book.todict() for book in books]), 200

@app.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    data = request.get_json()
    book = Books.query.get(book_id)
    
    if not book:
        return jsonify({"msg": "Book not found"}), 404
    
    title = data.get('title')
    author = data.get('author')
    description = data.get('description')
    price = data.get('price')
    category = data.get('category')
    cover_image = data.get('cover_image')
    
    if title:
        book.title = title
    if author:
        book.author = author
    if description:
        book.description = description
    if price:
        book.price = price
    if category:
        book.category = category
    if cover_image:
        book.cover_image = cover_image
    
    db.session.commit()
    return jsonify(book.todict()), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    book = Books.query.get(book_id)
    
    if not book:
        return jsonify({"msg": "Book not found"}), 404
    
    db.session.delete(book)
    db.session.commit()
    return jsonify({"msg": "Book deleted"}), 200
    
if __name__ == '__main__':
    app.run(debug=True)
