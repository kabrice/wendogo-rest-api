from flask import Flask, request, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
from flask_marshmallow import Marshmallow

app = Flask(__name__)

db = SQLAlchemy()
ma = Marshmallow()

mysql =MySQL()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    salutation = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(25), nullable=False)
    occupation = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(2500), nullable=False)

    def __init__(self, firstname, lastname, salutation, city, email, phone, occupation, description):
        self.firstname = firstname
        self.lastname = lastname
        self.salutation = salutation
        self.city = city
        self.email = email
        self.phone = phone
        self.occupation = occupation
        self.description = description

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','firstname', 'lastname', 'salutation','city', 'email', 'phone', 'occupation', 'description')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/wendogo'

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/user/add', methods=['POST'])
def add_user():
    _json = request.json
    firstname = _json['firstname']
    lastname = _json['lastname']
    salutation = _json['salutation']
    city = _json['city']
    email = _json['email']
    phone = _json['phone']
    occupation = _json['occupation']
    description = _json['description']
    new_user = User(firstname=firstname, lastname=lastname, salutation=salutation, city=city, email=email, phone=phone, occupation=occupation, description=description)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "the user has been added "})

@app.route('/user', methods=['GET'])
def get_user():
    users = []
    data = User.query.all()
    users = users_schema.dump(data)
    return jsonify(users)

@app.route('/user/<id>', methods=['GET'])
def user_byid(id):
    user = User.query.get(id)
    data = user_schema.dump(user)
    return jsonify(data)

@app.route('/user/delete/<id>', methods=['POST'])
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify(f"Error: the user doesn't exist")
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "the user has been deleted"})

@app.route('/user/edit/<id>', methods=['POST'])
def edit_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify ({"error": "the prodcut doesn't exist"})
    _json = request.json
    user.name = _json['name']
    user.firstname = _json['firstname']
    user.lastname = _json['lastname']
    user.salutation = _json['salutation']
    user.city = _json['city']
    user.email = _json['email']
    user.phone = _json['phone']
    user.occupation = _json['occupation']
    user.description = _json['description']
    db.session.commit()
    return jsonify({"message": "the user has been edited"})

if __name__ == '__main__':
    app.run(debug=True)
