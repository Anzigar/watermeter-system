import crypt
import string
from faker import Faker
import random
import bcrypt
from flask import Flask, session, abort
from flask_login import login_required, LoginManager
from flask_login import logout_user
from datetime import timedelta
from flask import request,render_template, redirect, url_for
from werkzeug.security import  check_password_hash
from datetime import datetime
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from api import api_bp

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/watermeter'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/watermeter'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'secret_key'
app.permanent_session_lifetime = timedelta(minutes=30)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# session(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

# database
class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

class Permission(db.Model):
    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    # secondary table for many-to-many relationship between User and Role
user_roles = db.Table("user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True)
)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    balance = db.Column(db.Float)
    roles = db.relationship("Role", secondary=user_roles, lazy="subquery", 
    backref=db.backref("users", lazy=True))

    def __repr__(self):
        return f'<{self.id}>'

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Transaction(db.Model):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transaction_timestamp = db.Column(db.DateTime)
    transaction_amount = db.Column(db.Float)
    transaction_type = db.Column(db.String(255))

    def __repr__(self):
        return f"<{self.id}>"
        
    @classmethod
    def find_by_name(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def find_by_user_id(cls,user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class Meter(db.Model):
    __tablename__ = "meter"
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.String(255), unique=True)
    location = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<{self.id}>"

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class Reading(db.Model):
    __tablename__ = "reading"
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.Integer, db.ForeignKey('meter.id'))
    reading = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return f"<{self.id}>"

    @classmethod
    def find_all(cls):
        return cls.query.all()

    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

# my routes are here 
@app.route('/index')
@login_manager.user_loader
# @login_required
def index():
     return render_template('index2.html')

# @app.route('/index2')
# def index2():
#      return render_template('index2.html')


#History route
@app.route('/history')
def history():
     return render_template('pages/tables/simple.html')

#Transaction
#add transaction
@app.route('/transaction')
def transaction():
     return render_template('pages/tables/transaction.html')

#profile
@app.route('/profile')
def profile():
     return render_template('pages/examples/profile.html')

#meter reading
@app.route('/meterreading')
def meterreading():
     return render_template('meter_reading.html')

#Roles routes
@app.route('/roles')
def roles():
    roles = Role.query.all()
    return render_template('roles.html', roles=roles)

@app.route('/permissions')
def permissions():
    permissions = Permission.query.all()
    return render_template('permission.html', permissions=permissions)

@app.route('/sucess/<name>')
def sucess(name):
    return 'Welcome %s' % name

@app.route('/users')
def users_list():
    return render_template('users.html')


# User account management
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login", name=user))
    return render_template("pages/examples/register.html")

@app.route('/')
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # login logic here
            # return redirect(url_for("index"))
            error= 'Invalid Credentials. Please try again.'
        else:
            # handle invalid login
            return redirect(url_for("index", name=email))
        if user:
             if user['role'] == 'admin':
                session['loggedin'] = True
                session['userid'] = user['userid']
                session['name'] = user['name']
                session['email'] = user['email']
                message= "Login Successfull !"
                return redirect(url_for('index'))
             else:
                message = "Only admin can login"
    return render_template("login.html", message=message, error=error)

#CRUD for user
#create the user
@app.route('/data/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('createuser.html')
    
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        balance = request.form.get("balance")
        user = User(name=name, email=email, password=password, balance=balance)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("users", id=user.id))
#view all
@app.route('/userslist')
def userslist():
    users = User.query.all()
    return render_template('userlist.html', users=users)

#retrieve user
@app.route('/users/<int:id>')
def users(id):
    user = User.query.filter_by(id=id).first()
    if user:
        return render_template('users.html', user=user )
    return f"User withe the id = {id} Does not Exist"

#update user
@app.route('/users/<int:id>/update', methods = ['POST', 'GET'])
def update(id):
     user = User.query.filter_by(id=id).first()
     if request.method == "POST":
        if user:
            db.session.delete(user)
            db.session.commit()
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            balance = request.form.get("balance")
            user = User(name=name, email=email, password=password, balance=balance)
            db.session.add(user)
            db.session.commit()
            return redirect(f'/users/{id}')
        return f"User withe the id = {id} Does not Exist"
     return render_template('update.html', user=user)

#delete user
@app.route('/users/<int:id>/delete', methods=['POST', 'GET'])
def delete(id):
    user = User.query.filter_by(id=id).first()
    if request.method == "POST":
        if user:
            db.session.delete(user)
            db.session.commit()
            return redirect('/users')
        abort(404)
    return render_template('delete.html')



#add the meter 
app.route("/add-meter", methods=["GET", "POST"])
def add_meter():
    if request.method == 'GET':
        return render_template('add_meter.html')

    if request.method == "POST":
        meter_id = request.form.get("meter_id")
        location = request.form.get("location")
        user_id = request.form.get("user_id")
        meter =Meter(meter_id=meter_id, location=location, user_id=user_id)
        db.session.add(meter)
        db.session.commit()
        return redirect(url_for("index"))



@app.route("/view-meters")
def view_meters():
     meters = Meter.query.all()
     return render_template("meter_reading.html", meters=meters)


@app.route("/update-reading/<int:id>", methods=["GET", "POST"])
def update_reading(id):
    reading=Reading.query.filter_by(id=id).first()
    if request.method == "POST":
        meter_id = request.form.get("meter_id")
        reading = request.form.get("reading")
        reading = Reading(meter_id=meter_id, reading=reading, timestamp=datetime.now())
        db.session.add(reading)
        db.session.commit()
        # calculate usage and bill the user here
        return redirect(url_for("index"))
    return render_template("editreading.html")

#update 

@app.route("/add-reading", methods=["GET", "POST"])
def add_reading():
    if request.method == "POST":
        meter_id = request.form.get("meter_id")
        reading = request.form.get("reading")
        reading = Reading(meter_id=meter_id, reading=reading, timestamp=datetime.now())
        db.session.add(reading)
        db.session.commit()
        # calculate usage and bill the user here
        return redirect(url_for("index"))
    return render_template("add_reading.html")

@app.route("/add-funds", methods=["GET", "POST"])
def add_funds():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        amount = int(request.form.get("amount"))
        user = User.query.filter_by(id=user_id).first()
        user.balance += amount
        transaction = Transaction(user_id=user_id, transaction_timestamp=datetime.now(),
                                transaction_amount=amount, transaction_type="Deposit")
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("addtransaction.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('loggedin', None)
    session.pop("userid", None)
    session.pop("email",None)
    session.pop("name", None)
    return redirect("/login")

#api routes
#user routes
# @api.resource('/user')
# class UserList(Resource):
#     def post():
#         pass


# Session(app)
app.register_blueprint(api_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
     db.init_app(app)
     ma.init_app(app)
     app.run(debug=True )