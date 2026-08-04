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
                flash("Invalid User! Access Forbidden.", "danger")
                return redirect(url_for('auth.main'))
            return func(*a, **kw)
        return decorated
    return wrapper




# ==================================================================================================================================

user_bp = Blueprint("user",__name__)


@user_bp.route("/user_dashboard")
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

@user_bp.route("/<int:t_id>/trek")
@role_validator("user")
def book_trek_details(t_id):
    trek = TREKK.query.get_or_404(t_id)
    user_id = session.get('user_id',None)
    isbooked = None
    if user_id:
        isbooked = BOOKING.query.filter_by(user_id=user_id, trek_id=t_id, status="Booked").first()
    
    return render_template("user/book_trek_details.html", trek=trek, isbooked=bool(isbooked))

@user_bp.route("/treks/<int:t_id>/book_trek", methods=["POST"])
@role_validator("user")
def book_trek(t_id):
    booked_trek = TREKK.query.get_or_404(t_id)
    if  booked_trek.status not in ("Open", "Approved"):
        flash("Trek unavailable for Booking.", "warning")
        return redirect(url_for("user.user_trek_detail", t_id=t_id))
    if  booked_trek.avl_slots <= 0:
        flash("No slots available.", "danger")
        return redirect(url_for("user.user_trek_detail", tid=t_id))
    if BOOKING.query.filter_by(user_id=session["user_id"], trek_id=t_id, status="Booked").first():
        flash("Trek Already Booked for this Account.", "warning")
        return redirect(url_for("user.user_trek_detail", t_id=t_id))
    booking = BOOKING(user_id=session["user_id"], trek_id=t_id, status="Booked")
    db.session.add(booking)
    booked_trek.avl_slots -= 1
    db.session.commit()
    flash("Trek Booked Successfully!", "success")
    return redirect(url_for("user.user_dashboard"))


