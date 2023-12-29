from flask import Flask, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.event import listens_for
from flaskext.mysql import MySQL
from flask_cors import CORS
from datetime import datetime
import sys
from helper import Helper
from dataclasses import dataclass
from sqlalchemy import text

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:3000"])
#app.config['SECRET_KEY'] = 'top-secret!'


db = SQLAlchemy()
#ma = Marshmallow()

mysql =MySQL()

@dataclass
class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(35), nullable=False)#2
    description = db.Column(db.String(2500), nullable=False)#2
    email = db.Column(db.String(50), nullable=False)#1
    firstname = db.Column(db.String(46), nullable=False)#1
    lastname = db.Column(db.String(46), nullable=False)#1
    salutation = db.Column(db.String(15), nullable=False)#1
    created_date = db.Column(db.DateTime, default=datetime.utcnow())
    country = db.Column(db.String(4), nullable=False)
    last_modified_date = db.Column(db.DateTime)
    phone = db.Column(db.String(25), nullable=False)
    has_whatsapp = db.Column(db.Boolean, unique=False, default=False, nullable=False)
    whatsapp_verification_attempt = db.Column(db.Integer, default=0)
    occupation = db.Column(db.String(20), nullable=False)#2
    subscription_step =  db.Column(db.String(255), nullable=False)
    

    def __init__(self, firstname, lastname, salutation, city, email, phone, occupation, description, country):
        self.firstname = firstname
        self.lastname = lastname
        self.salutation = salutation
        self.city = city
        self.email = email
        self.phone = phone
        self.occupation = occupation
        self.description = description
        self.country = country

    def as_dict(self):
        excluded_fields = ['id', 'created_date', 'last_modified_date', 'whatsapp_verification_attempt']
        return {field.name:getattr(self, field.name) for field in self.__table__.c if field.name not in excluded_fields}

@dataclass
class User(db.Model):

    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(35), nullable=False)#2
    description = db.Column(db.String(2500), nullable=False)#2
    email = db.Column(db.String(50), nullable=False)#1
    firstname = db.Column(db.String(46), nullable=False)#1
    lastname = db.Column(db.String(46), nullable=False)#1
    salutation = db.Column(db.String(15), nullable=False)#1
    created_date = db.Column(db.DateTime, default=datetime.utcnow())
    country = db.Column(db.String(4), nullable=False)
    last_modified_date = db.Column(db.DateTime)
    phone = db.Column(db.String(25), nullable=False)
    has_whatsapp = db.Column(db.Boolean, unique=False, default=False, nullable=False)
    whatsapp_verification_attempt = db.Column(db.Integer, default=0)
    occupation = db.Column(db.String(20), nullable=False)#2
    subscription_step = db.Column(db.String(255), nullable=False)

    def __init__(self, firstname, lastname, salutation, city, email, phone, occupation, description, country):
        self.firstname = firstname
        self.lastname = lastname
        self.salutation = salutation
        self.city = city
        self.email = email
        self.phone = phone
        self.occupation = occupation
        self.description = description
        self.country = country

    def as_dict(self):
        excluded_fields = ['id', 'created_date', 'last_modified_date', 'whatsapp_verification_attempt']
        return {field.name:getattr(self, field.name) for field in self.__table__.c if field.name not in excluded_fields}
            
@listens_for(User, 'after_update')
def update_user_log(mapper, connection, target):
    user_table = User.__table__
    connection.execute(
        user_table.update().
        where(user_table.c.id==target.id).
        values(last_modified_date=datetime.utcnow())
    )

# user_schema = UserSchema()
# users_schema = UserSchema(many=True)
@dataclass
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_input = db.Column(db.String(255))
    message = db.Column(db.String(2500), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self, request_input, message):
        self.request_input = request_input
        self.message = message

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
    return jsonify({"message": "user has been added "})

@app.route('/users', methods=['GET'])
def get_user():
    #users = []
    users = User.query.all()
    #users = users_schema.dump(data)
    return jsonify(users)

@app.route('/user/<phone>', methods=['GET'])
def user_byphone(phone):
    user = User.query.filter_by(phone = phone).first()
    #data = user_schema.dump(user)
    return jsonify(user)

@app.route('/user/delete/<id>', methods=['POST'])
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify(f"Error: user doesn't exist")
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "user has been deleted"})

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
    return jsonify({"message": "user has been edited"})

@app.route('/user/add/verification', methods=['POST'])
def verify_whatsapp_and_add_user():
    try:
        _json = request.get_json()
        firstname = _json['firstname'].title()
        lastname = _json['lastname'].title()
        phone = _json.get('phone')
        country = _json.get('country')
        userMaybe = User.query.filter_by(phone = phone).first()
        is_code_has_been_sent = False
        #return jsonify({"user": 'new_user.as_dict()', "sent": False, "success": True})
        #print ('<==== userMaybe ', Helper.rows_as_dicts(userMaybe))
        if userMaybe is None : # user doesn't exist, we send a verification code and we create a new user
            print('########## user doesn\'t exist')
            new_user = User(firstname=firstname, lastname=lastname, salutation='', city='', email='', phone=phone, occupation='', description='', country=country)
            new_user.subscription_step = '/verification' #Step 1 => Go to  Verification Code Page
            db.session.add(new_user)
            db.session.commit()
            if phone is not None:
                print('########## user does exist and has been verified')
                is_code_has_been_sent = Helper.send_whatsapp_verification_code(phone)
            return jsonify({"user": new_user.as_dict(), "sent": is_code_has_been_sent,  "success": True})
        elif userMaybe.has_whatsapp : # user does exist and has been verified, we'll suggest to user to edit occupation/description
            print('########## user does exist and has been verified')
            return jsonify({"user": userMaybe.as_dict(), "sent": is_code_has_been_sent, "success": True})
        elif not userMaybe.has_whatsapp: # user does exist and hasn't been verified, we sent a verification once again
            print('########## user does exist and hasn\'t been verified')
            Helper.send_whatsapp_verification_code(phone)
            return jsonify({"user": userMaybe.as_dict(), "sent": is_code_has_been_sent, "success": True})
        
    except Exception as e:
       Helper.logError(e, db, Log, request)    

@app.route('/user/verificationCheck', methods=['POST'])
def check_whatsapp_phone():   
    try:
        _json = request.get_json()
        phone = _json.get('phone')
        code = _json.get('code')
        is_number_verify = Helper.check_whatsapp_verification_code(phone, code) 
        user = User.query.filter_by(phone = phone).first()
        user.whatsapp_verification_attempt = user.whatsapp_verification_attempt+1
        if is_number_verify:
            user.has_whatsapp = True
            user.subscription_step = '/credentialstart' #Step 2 => Go to  Credential 1 Page
        db.session.commit()
        return jsonify({"user": user.as_dict(), "verify": is_number_verify, "success": True})
    except Exception as e:
        Helper.logError(e, db, Log, request) 
    
@app.route('/user/update/credentials', methods=['POST'])
def update_credentials():  
    try:
        _json = request.get_json()
        phone = _json.get('phone')
        user = User.query.filter_by(phone = phone).first()
        if _json.get('firstname') and _json.get('lastname') and _json.get('salutation') and _json.get('email'):
            user.firstname = _json.get('firstname').title()
            user.lastname = _json.get('lastname').title()
            user.salutation = _json.get('salutation')
            user.email = _json.get('email') if not _json.get('doesntHaveEmail') else ''
            user.subscription_step = '/credentialend'  #Step 3 => Go to  Credential 2 Page
        elif _json.get('country') and _json.get('city') and _json.get('occupation') and _json.get('description'):
            user.country = _json.get('country').title()
            user.city = _json.get('city').title()
            user.occupation = _json.get('occupation')
            user.description = _json.get('description')
            user.subscription_step = '/congratulation' #Step 4 => Go to  Congratulation Page
        db.session.commit()
        return jsonify({"user": user.as_dict(), "success": True})
    except Exception as e:
        Helper.logError(e, db, Log, request) 

@app.route('/user/update/subscriptionStep', methods=['PUT'])
def update_subscription_step():  
    try:
        _json = request.get_json()
        phone = _json.get('phone')
        user = User.query.filter_by(phone = phone).first()
        if _json.get('subscriptionStep'):
            user.subscription_step = _json.get('subscriptionStep')  
        db.session.commit()
        return jsonify({"user": user.as_dict(), "success": True})
    except Exception as e:
        Helper.logError(e, db, Log, request) 

@app.route('/countries/<country_iso2>', methods=['GET'])
def get_countries(country_iso2):
    try:    
        country_res = db.session.execute(text("SELECT translations, iso2, capital FROM countries"))
        data_country, data_city = [], []
        selectedCountryCapital = ''

        for row in country_res:
            json_object = row[0]
            json_object = json.loads(json_object)
            #country_local = json_object['fr']
            if "fr" in json_object:
                if row[1] == country_iso2:
                    selectedCountryCapital = row[2]
                data_country.append({'value': str(json_object["fr"]), 'selected':row[1] == country_iso2})

        city_res = db.session.execute(text("SELECT name, country_code FROM cities WHERE country_code = '"+country_iso2+"'"))

        for row in city_res:
            data_city.append({'value': row[0], 'selected': Helper.f_remove_accents(row[0]) == Helper.f_remove_accents(selectedCountryCapital)})

        return {"countries": data_country, "cities": data_city, "success": True}
    except Exception as e:
        Helper.logError(e, db, Log, request) 

if __name__ == '__main__':
    app.run(debug=True)
