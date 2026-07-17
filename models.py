from flask_sqlalchemy import SQLAlchemy # ORM Librrary
from flask_login import UserMixin # login session helper 
from datetime import datetime





db = SQLAlchemy() # the ORM Instance


class USER(UserMixin, db.Model): # user table(entity)

    __tablename__ = 'users'

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
    trek_bookings = db.relationship("BOOKING", backref="user", lazy=True)
    assigned_trek_staff = db.relationship("TREKK", backref="staff", foreign_keys="TREKK.assigned_staff_id", lazy=True,  )

    def __repr__(self):
        return f"<USER {self.username}>"

    
class TREKK(db.Model): # trek table(entity)

    __tablename__ = 'treks'
    trek_id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False) # easy , moderate or hard
    duration = db.Column(db.String(50), nullable=False) # '2 days' or '5 days'
    location = db.Column(db.String(40),nullable=False)
    total_slots = db.Column(db.Integer, nullable=False) 
    avl_slots = db.Column(db.Integer, nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    discription = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False) # 2000.50, 2500.40
    status = db.Column(db.String(50), nullable=False,default="inactive" )  # active or inactive
    start_date = db.Column(db.Date, nullable=False) 
    end_date = db.Column(db.Date, nullable=False)
    date_of_create = db.Column(db.DateTime, default=datetime.utcnow)

    #relationship
    booked_treks = db.relationship("BOOKING", backref="trek", lazy=True)

    def __repr__(self):
        return f"<TREKK {self.trek_id}>"




class BOOKING(db.Model): #booking table(entity)

    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.trek_id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(40), nullable=False, default="pending") # pending, confirmed or canceled
    notes = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<BOOKING {self.booking_id}>"

