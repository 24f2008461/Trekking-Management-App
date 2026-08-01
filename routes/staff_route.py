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
    assigned_treks = TREKK.query.filter(TREKK.assigned_staff_id == staff_id,TREKK.status.in_(['Approved', 'Open', 'Closed'])).order_by(TREKK.start_date).all()
    
    assigned_treks_count = TREKK.query.filter(TREKK.assigned_staff_id == staff_id,TREKK.status.in_(['Approved', 'Open', 'Closed'])).order_by(TREKK.start_date).count()
    assigned_trekkers = {}

    for trek in assigned_treks:
        assigned_trekkers[trek.trek_id] = BOOKING.query.filter_by(trek_id=trek.trek_id, status='booked').count()

    
    total_participants = sum(t.total_slots for t in assigned_treks if t.status=='Open' or t.status=='Closed')

    open_treks = TREKK.query.filter_by(assigned_staff_id=staff_id, status='Open').count()

    return render_template('staff/staff_dashboard.html', 
                           total_participants=total_participants,
                           assigned_treks_count=assigned_treks_count,
                           assigned_treks=assigned_treks,
                           assigned_trekkers=assigned_trekkers,
                           open_treks=open_treks
                           )

@staff_bp.route("/trek/<int:t_id>", methods=['GET','POST'])
@role_validator('staff')
def assigned_trek_details(t_id):
    trek = TREKK.query.filter_by(assigned_staff_id=session['user_id'], trek_id=t_id).first()
    if not trek:
        flash("Trek not Found / Not Assigned to Staff !", "danger")
        return redirect(url_for('staff.staff_dashboard'))
    if request.method=='POST':

        if 'status' in request.form:
            curr_status = request.form.get('status').strip()
            if curr_status in ['Open', 'Closed', 'Completed']:
                trek.status = curr_status
                db.session.commit()
                flash(f"Trek Status : {curr_status} ", "success")
            return redirect(url_for("staff.staff_dashboard"))
        if 'avl_slots' in request.form:
            avl_slots = request.form.get('avl_slots')
            if int(avl_slots) > int(trek.total_slots):
                flash("Invalid Input, Available Slots must to less than Total Slots!", "danger")
                return redirect(url_for("staff.staff_dashboard"))
            trek.avl_slots = avl_slots
            db.session.commit()
            flash("Updated available slots!", "success")
            return redirect(url_for('staff.assigned_trek_details', t_id=trek.trek_id))
        
    return render_template("staff/trek_details.html", trek=trek)

    