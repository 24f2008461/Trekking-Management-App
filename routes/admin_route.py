from flask import session, request, render_template, Blueprint, flash, url_for, redirect
from functools import wraps
from datetime import date
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, contains_eager
from werkzeug.security import generate_password_hash
from models import db, USER,TREKK,BOOKING




# ------------------------Autherization-validator----------------------
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
        'users' : USER.query.filter_by(role='user',status='approved').count(),
        'staffs' : USER.query.filter_by(role="staff",status='approved').count(),
        'avl_treks' :TREKK.query.filter_by(status="Open").count(),
        'completed_treks' : TREKK.query.filter_by(status="Completed").count(),
        'bookings' :BOOKING.query.filter(BOOKING.status.in_(['Booked','Completed'])).count()   
    }

    bookings = (
        db.session.query(BOOKING)
        .options(joinedload(BOOKING.user), joinedload(BOOKING.trek))
        .order_by(BOOKING.booking_date.desc()).limit(5).all()
    )

    newly_treks = TREKK.query.order_by(TREKK.date_of_create.desc()).limit(5).all()

    return render_template("/admin/admin_dashboard.html", app_data=app_data, bookings=bookings, newly_treks=newly_treks)

# ===========================================Manage Treks======================================================

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



@admin_bp.route("/treks/Add_Treks", methods=['GET','POST'])
@role_validator("admin")
def add_treks():
    staff_list = USER.query.filter_by(role='staff', status='approved').all()
    if request.method == 'POST':
        tname = request.form['tname'].strip()
        location = request.form['location'].strip()

        if not tname or not location:
            flash("Please fill the Trek Name and Location!" , "danger")
            return redirect(url_for('admin.add_treks'))
        try:
            total_slots = int(request.form['total_slots'])
            price = float(request.form.get("price", 0))
            duration = int(request.form['duration'])
            if total_slots <= 0 or price < 0 or duration <= 0:
                raise ValueError

            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            start_date_obj = date.fromisoformat(start_date) if start_date else None
            end_date_obj = date.fromisoformat(end_date) if end_date else None

        except ValueError:
            flash("Total Slots & Duration Days must be positive number, also price can not negatice!", "danger")
            return redirect(url_for('admin.add_treks'))

        new_trek = TREKK(
            name = tname,
            location=location,
            duration = duration,
            difficulty = request.form['difficulty'],
            total_slots=total_slots,
            avl_slots=total_slots,
            price=price,
            assigned_staff_id=request.form['assigned_staff'] or None,
            start_date=start_date_obj,
            end_date=end_date_obj,
            status=request.form.get('status','Pending'),
            description=request.form.get("description", "").strip()
        )

        db.session.add(new_trek)
        db.session.commit()
        flash("Trek Added Successfully!", "success")
        return redirect(url_for('admin.find_treks'))
    return render_template("admin/add_treks.html" ,staff_list=staff_list )



@admin_bp.route("/treks/<int:t_id>/delete_trek", methods=["POST"])
@role_validator("admin")
def delete_treks(t_id):
    if request.method=="POST":
        trek = TREKK.query.get_or_404(t_id)
        BOOKING.query.filter_by(trek_id=t_id).delete()
        if trek is not None:
            db.session.delete(trek)
        db.session.commit()
        flash("Trek deleted.", "info")
        return redirect(url_for("admin.find_treks"))


@admin_bp.route("/treks/<int:t_id>/edit_trek", methods=['GET','POST'])
@role_validator("admin")
def edit_treks(t_id):
    trek = TREKK.query.get_or_404(t_id)
    staff_list = USER.query.filter_by(role="staff", status="approved").all()

    if request.method == 'POST':
        tname = request.form['tname'].strip()
        location = request.form['location'].strip()

        if not tname or not location:
            flash("Please fill the Trek Name and Location!" , "danger")
            return redirect(url_for('admin.edit_treks',t_id=t_id))
        try:
            total_slots_new = int(request.form['total_slots'])
            price = float(request.form.get("price", 0))
            duration = int(request.form['duration'])
            if total_slots_new <= 0 or price < 0 or duration <= 0:
                raise ValueError

            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            start_date_obj = date.fromisoformat(start_date) if start_date else None
            end_date_obj = date.fromisoformat(end_date) if end_date else None

        except ValueError:
            flash("Total Slots & Duration Days must be positive number, also price can not negatice!", "danger")
            return redirect(url_for('admin.edit_treks',t_id=t_id))

        slots_booked = trek.total_slots - trek.avl_slots
        avl_slots_new = max(total_slots_new  - slots_booked, 0)
            
        trek.name=tname
        trek.location=location
        trek.duration = duration
        trek.difficulty = request.form['difficulty']
        trek.total_slots=avl_slots_new
        trek.avl_slots=avl_slots_new
        trek.price=price
        trek.assigned_staff_id=request.form['assigned_staff'] or None
        trek.start_date=start_date_obj or None
        trek.end_date=end_date_obj or None
        trek.status=request.form.get('status','Pending')
        trek.description=request.form.get('description','')
        
        db.session.commit()
        flash("Trek updated Successfully!" ,"success")
        return redirect(url_for('admin.find_treks'))
    return render_template("admin/edit_treks.html", trek=trek, staff_list=staff_list)
    

# ===========================================Manage Staffs======================================================
@admin_bp.route("/staff")
@role_validator("admin")
def find_staff():
    s = request.args.get("s", "").strip()
    query = USER.query.filter_by(role="staff",status="approved")
    if s:
        search_filters = db.or_(
                    USER.name.ilike(f"%{s}%"),
                    USER.user_id == int(s) if s.isdigit() else db.false(),
                    )
        query = query.filter(db.or_(search_filters))
    staff = query.order_by(USER.date_of_create.desc()).all()
    return render_template("admin/staff.html", staff=staff, s=s)



@admin_bp.route("/staff/validate_staff" , methods=['GET','POST'])
@role_validator("admin")
def validate_staff():
    validation_list = USER.query.filter_by(role='staff', is_validated=False).all()
    current_filter = 'pending'
    
    if request.method=='POST':
        validation=request.form.get('validation')

        if validation=='pending':
            validation_list = USER.query.filter( USER.role=='staff', USER.status=='pending').all()

        if validation=='approved':
            validation_list = USER.query.filter(USER.role=='staff', USER.status=='approved').all()

        if validation=='blacklisted':
            validation_list = USER.query.filter(USER.role=='staff', USER.status=='blacklisted').all()
            
    return render_template("admin/validate_staff.html", validation_list=validation_list,current_filter=current_filter )



@admin_bp.route('/staff/<int:user_id>/approve_staff', methods=['POST'])
@role_validator('admin')
def approve_staff(user_id):
    staff = USER.query.get_or_404(user_id)
    if not staff.is_validated:
        staff.status = 'approved'
        staff.is_validated = True
    
    db.session.commit()
    flash('Staff member has been approved.', 'success')
    return redirect(request.referrer or url_for('admin.validate_staff'))

@admin_bp.route('/staff/<int:user_id>/blacklist_staff', methods=['POST'])
@role_validator('admin')
def blacklist_staff(user_id):
    staff = USER.query.get_or_404(user_id)
    staff.status = 'blacklisted'
    staff.is_validated = False
    db.session.commit()
    flash('Staff member has been blacklisted.', 'danger')
    return redirect(request.referrer or url_for('admin.validate_staff'))


@admin_bp.route('/staff/<int:user_id>/delete_staff', methods=['POST'])
@role_validator('admin')
def delete_staff(user_id):
    staff = USER.query.get_or_404(user_id)
    TREKK.query.filter_by(assigned_staff_id=user_id).update({"assigned_staff_id": None})

    if staff is not None:
        db.session.delete(staff)
    db.session.commit()
    flash("Staff Removed.", "info")
    return redirect(url_for("admin.validate_staff"))




# -----------------------------------------Manage-users-----------------------------------------------
@admin_bp.route("/user")
@role_validator("admin")
def find_users():
    s = request.args.get("s", "").strip()
    query = USER.query.filter_by(role="user",status="approved")
    if s:
        search_filters = db.or_(
                    USER.name.ilike(f"%{s}%"),
                    USER.user_id == int(s) if s.isdigit() else db.false(),
                    )
        query = query.filter(db.or_(search_filters))
    user = query.order_by(USER.date_of_create.desc()).all()
    return render_template("admin/users.html", user=user, s=s)


@admin_bp.route("/user/validate_user" , methods=['GET','POST'])
@role_validator("admin")
def validate_users():
    validation_list = USER.query.filter_by(role='user', is_validated=False).all()
    current_filter = 'pending'
    
    if request.method=='POST':
        validation=request.form.get('validation')

        if validation=='pending':
            validation_list = USER.query.filter( USER.role=='user', USER.status=='pending').all()

        if validation=='approved':
            validation_list = USER.query.filter(USER.role=='user', USER.status=='approved').all()

        if validation=='blacklisted':
            validation_list = USER.query.filter(USER.role=='user', USER.status=='blacklisted').all()
            
    return render_template("admin/validate_users.html", validation_list=validation_list,current_filter=current_filter )

@admin_bp.route('/user/<int:user_id>/approve_user', methods=['POST'])
@role_validator('admin')
def approve_users(user_id):
    user = USER.query.get_or_404(user_id)
    if not user.is_validated:
        user.status = 'approved'
        user.is_validated = True
    
    db.session.commit()
    flash('User has been approved.', 'success')
    return redirect(request.referrer or url_for('admin.validate_users'))


@admin_bp.route('/user/<int:user_id>/blacklist_user', methods=['POST'])
@role_validator('admin')
def blacklist_users(user_id):
    user = USER.query.get_or_404(user_id)
    user.status = 'blacklisted'
    user.is_validated = False
    db.session.commit()
    flash('User has been blacklisted.', 'danger')
    return redirect(request.referrer or url_for('admin.validate_users'))


@admin_bp.route('/user/<int:user_id>/delete_user', methods=['POST'])
@role_validator('admin')
def delete_users(user_id):
    user = USER.query.get_or_404(user_id)
    if user is not None:
        db.session.delete(user)
    db.session.commit()
    flash("User Removed.", "info")
    return redirect(url_for("admin.validate_users"))

# ------------------------------------------Manage-Bookings--------------------------------------------
@admin_bp.route("/bookings")
@role_validator("admin")
def find_bookings():
    q = request.args.get("q", "").strip()
    page = request.args.get('page', 1, type=int)
    query = (db.session.query(BOOKING,USER,TREKK)
             .join(USER,BOOKING.user_id == USER.user_id)
             .join(TREKK,BOOKING.trek_id == TREKK.trek_id)
             .options(
            contains_eager(BOOKING.user), 
            contains_eager(BOOKING.trek)
        )
            )
    if q:
        search_filters = [
            USER.fullname.ilike(f"%{q}%"),
            USER.username.ilike(f"%{q}%"),
            TREKK.name.ilike(f"%{q}%")
            ]
        if q.isdigit():
            search_filters.append(BOOKING.id == int(q))
        query = query.filter(db.or_(*search_filters))
    bookings = query.order_by(BOOKING.booking_date.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template("admin/bookings.html", bookings=bookings, q=q)