from flask import session, request, render_template, Blueprint, flash, url_for, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, USER, TREKK, BOOKING
from functools import wraps


def login_validator(func):
    @wraps(func)
    def decorated(*a, **kw):
        if 'user_id' not in session:
            flash("Please Log in to your Account First!", "warning")
            return redirect(url_for('auth.main'))
        return func(*a, **kw)
    return decorated


def role_validator(*roles):
    def wrapper(func):
        @wraps(func)
        @login_validator
        def decorated(*a, **kw):
            if session.get('role') not in roles:
                flash("Invalid User! Access Forbiden.", "danger")
                return redirect(url_for('auth.main'))
            return func(*a, **kw)
        return decorated
    return wrapper

staff_bp = Blueprint("staff",__name__,url_prefix="/staff")

@staff_bp.route("/staff_dashboard")
@role_validator('staff')
def staff_dashboard():
    staff_id = session.get('user_id')
    assigned_treks = TREKK.query.filter(TREKK.assigned_staff_id==staff_id,TREKK.status.in_(['Open','Closed'])).order_by(TREKK.start_date).limit(6)
    assigned_open_treks = TREKK.query.filter(TREKK.assigned_staff_id==staff_id,TREKK.status.in_(['Open'])).order_by(TREKK.start_date).all()
    
    assigned_treks_count = len(assigned_open_treks)
    assigned_trekkers = {}

    for trek in assigned_treks:
        assigned_trekkers[trek.trek_id] = BOOKING.query.filter_by(trek_id=trek.trek_id, status='booked').count()

    
    total_participants = sum(t.total_slots for t in assigned_treks if t.status=='Open')

    open_treks = TREKK.query.filter_by(assigned_staff_id=staff_id, status='Open').count()

    return render_template('staff/staff_dashboard.html', 
                           total_participants=total_participants,
                           assigned_treks_count=assigned_treks_count,
                           assigned_open_treks=assigned_open_treks,
                           assigned_treks=assigned_treks,
                           assigned_trekkers=assigned_trekkers,
                           open_treks=open_treks
                           )

