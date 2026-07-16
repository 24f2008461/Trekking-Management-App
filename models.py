from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime





db = SQLAlchemy()


class user(UserMixin, db.Model):

    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True) #user_id (primary key)
    username = db.Column(db.String(150), unique=True,nullable=False)
    email = db.Column(db.String(250),unique=True,nullable=False)
    fullname = db.Column(db.String(150),nullable=False)
    password = db.Column(db.String(250),nullable=False)
    phone_number = db.Column(db.String(20),nullable=True)
    role = db.Column(db.String(50),nullable=False, default="user") # user ,staff, admin
    status = db.Column(db.String(50),nullable=False, default="active") # active or inactive
    is_validated = db.Column(db.Boolean, default=False) # for admin to verify the user!
    date_of_create = db.Column(db.DateTime, default=datetime.utcnow)

    #relationship
    trek_bookings = db.relationship("booking", backref="user", lazy=True)
    assigned_trek_staff = db.relationship("trekk", backref="user", lazy=True)

    
class trekk(db.Model):

    __tablename__ = 'treks'
    trek_id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False) # easy , moderate or hard
    duration = db.Column(db.String(50), nullable=False) # '2 days' or '5 days'
    location = db.Column(db.String(40),nullable=False)
    total_slots = db.Column(db.Integer, nullable=False) 
    avl_slots = db.Column(db.Integer, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    discription = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False) # 2000.50, 2500.40
    status = db.Column(db.String(50), nullable=False,default="inactive" )  # active or inactive
    start_date = db.Column(db.Date, nullable=False) 
    end_date = db.Column(db.Date, nullable=False)
    date_of_create = db.Column(db.DateTime, default=datetime.utcnow)

    #relationship
    booked_treks = db.relationship("booking", backref="trekk", lazy=True)



class booking(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.trek_id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(40), nullable=False, default="pending") # pending, confirmed or canceled
    notes = db.Column(db.String(200), nullable=True)
