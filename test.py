from flask import session, render_template
from models import db, USER, BOOKING, TREKK
from flask_sqlalchemy import SQLAlchemy

def staff_dashboard():
    staff_id = session.get('user_id')
    assigned_treks = TREKK.query.filter_by(assigned_staff_id=staff_id).order_by(TREKK.start_date).all()
    assigned_treks_count = len(assigned_treks)
    assigned_trekkers = {}

    for trek in assigned_treks:
        assigned_trekkers[trek.trek_id] = BOOKING.query.filter_by(trek_id=trek.trek_id, status='booked').count()

    total_participants = sum(assigned_trekkers.values())

    open_treks = TREKK.query.filter_by(assigned_staff_id=staff_id, status='Open').count()

    return render_template('staff/staff_dashboard', 
                           total_participants=total_participants,
                           assigned_treks_count=assigned_treks_count,
                           assigned_treks=assigned_treks,
                           assigned_trekkers=assigned_trekkers,
                           open_treks=open_treks
                           )
