from flask import session, request, render_template, Blueprint, flash, url_for, redirect
from functools import wraps
from sqlalchemy.orm import joinedload
from models import db, USER, TREKK, BOOKING



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




# ==================================================================================================================================

user_bp = Blueprint("user",__name__)


@user_bp.route("/dashboard")
@role_validator("user")
def user_dashboard():
    u_id = session.get('user_id','')
    query = TREKK.query.filter(TREKK.status.in_(['Open','Approved']))

    difficulty= request.args.get('difficulty')
    location = request.args.get('location')

    if difficulty:
        query = query.filter(TREKK.difficulty == difficulty)

    if location:
        query = query.filter(TREKK.location == location)

    avl_treks = query.order_by(TREKK.start_date).all()
    all_avl_location = [loc[0] for loc in db.session.query(TREKK.location).distinct().all() if loc[0]]

    my_bookings = (
        db.session.query(BOOKING, TREKK)
        .join(TREKK,BOOKING.trek_id == TREKK.trek_id)
        .filter(BOOKING.user_id == u_id, BOOKING.status == "Booked")
        .order_by(BOOKING.booking_date.desc()).all()
    )

    my_details = {
        "total_bookings" : BOOKING.query.filter_by(user_id=u_id).count(),
        "active" : BOOKING.query.filter_by(user_id=u_id, status="Booked").count(),
        "completed" : BOOKING.query.filter_by(user_id=u_id, status="Completed").count()
    }

    return render_template("user/user_dashboard.html",
                           avl_treks=avl_treks,
                           my_bookings=my_bookings,
                           my_details=my_details,
                           all_avl_location=all_avl_location
                           )





