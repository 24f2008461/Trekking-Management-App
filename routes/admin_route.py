from flask import session, request, render_template, Blueprint, flash, url_for, redirect
from functools import wraps
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, USER,TREKK,BOOKING





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

admin_bp = Blueprint("admin", __name__, url_prefix='/admin')


#---------------------------------------main-dashboard-----------------------------------
@admin_bp.route("/admin_dashboard")
@role_validator("admin")
def admin_dashboard():
    app_data = {
        'treks': TREKK.query.count(),
        'users' : USER.query.filter_by(role='user').count(),
        'staffs' : USER.query.filter_by(role="staff").count(),
        'avl_treks' :TREKK.query.filter_by(status="Open").count(),
        'completed_treks' : TREKK.query.filter_by(status="Completed").count(),
        'bookings' :BOOKING.query.count()
        
    }

    bookings = (
        db.session.query(BOOKING)
        .options(joinedload(BOOKING.user), joinedload(BOOKING.trek))
        .order_by(BOOKING.booking_date.desc()).limit(5).all()
    )

    newly_treks = TREKK.query.order_by(TREKK.date_of_create.desc()).limit(5).all()




    return render_template("/admin/admin_dashboard.html", app_data=app_data, bookings=bookings, newly_treks=newly_treks)

#-------------------------------------Manage-Treks----------------------------------

@admin_bp.route("/treks")
@role_validator("admin")
def find_treks():
    t = request.args.get("t", '').strip()
    query = TREKK.query
    if t:
        search_filters = db.or_(
            TREKK.name.ilike(f"%{t}%"),
            TREKK.trek_id == int(t) if t.isdigit() else db.false(),
            TREKK.location.ilike(f"%{t}%") ,
            )
        query = query.filter(search_filters)

    treks = query.order_by(TREKK.date_of_create.desc()).all()
    return render_template("admin/treks.html", treks=treks, t=t)



@admin_bp.route("/Add_Treks")
@role_validator("admin")
def add_treks():
    return render_template("admin/add_treks.html")