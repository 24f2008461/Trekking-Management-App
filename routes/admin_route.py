from flask import session, request, render_template, Blueprint, flash, url_for, redirect
from functools import wraps
from datetime import date
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
    staff_list = USER.query.filter_by(role='staff', status='active').all()
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
            discription=request.form.get("description", "").strip()
        )

        db.session.add(new_trek)
        db.session.commit()
        flash("Trek Added Successfully!", "success")
        return redirect(url_for('admin.find_treks'))
    return render_template("admin/add_treks.html" ,staff_list=staff_list )



@admin_bp.route("/treks/<int:t_id>/delete", methods=["POST"])
@role_validator("admin")
def delete_treks(t_id):
    trek = TREKK.query.get_or_404(t_id)
    BOOKING.query.filter_by(trek_id=t_id).delete()
    db.session.delete(trek)
    db.session.commit()
    flash("Trek deleted.", "info")
    return redirect(url_for("admin.find_treks"))


@admin_bp.route("/treks/<int:t_id>/edit", methods=['GET','POST'])
@role_validator("admin")
def edit_treks(t_id):
    trek = TREKK.query.get_or_404(t_id)
    staff_list = USER.query.filter_by(role="staff", status="active").all()
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


        updated_trek = TREKK(
            name=tname,
            location=location,
            duration = duration,
            difficulty = request.form['difficulty'],
            total_slots=avl_slots_new,
            avl_slots=avl_slots_new,
            price=price,
            assigned_staff_id=request.form['assigned_staff'] or None,
            start_date=start_date_obj or None,
            end_date=end_date_obj or None,
            status=request.form.get('status','Pending'),
            discription=request.form.get("description", "").strip()
        )
        db.session.add(updated_trek)
        db.session.commit()
        flash("Trek updated Successfully!" ,"success")
        return redirect(url_for('admin.find_treks'))
    return render_template("admin/edit_treks.html", trek=trek, staff_list=staff_list)
    

# ===========================================Manage Staffs======================================================
@admin_bp.route("/staff")
@role_validator("admin")
def find_staff():
    s = request.args.get("s", "").strip()
    query = USER.query.filter_by(role="staff")
    if s:
        search_filters = db.or_(
                    USER.name.ilike(f"%{s}%"),
                    USER.user_id == int(s) if s.isdigit() else db.false(),
                    )
        query = query.filter(db.or_(search_filters))
    staff = query.order_by(USER.date_of_create.desc()).all()
    return render_template("admin/staff.html", staff=staff, s=s)


# ======================================================================================================
# ==============================to be added to user route later====================================
@admin_bp.route("/staff/Add_staffs" , methods=['GET','POST'])
@role_validator("admin")
def add_staff():
    if request.method=='POST':
        username = request.form.get('username', '').strip()
        fullname = request.form.get('fullname','').strip()
        email = request.form.get('email','').strip()
        password = request.form.get('password','')
        f_password = request.form.get('fpassword','')
        phone_no = request.form.get('phone_no','').strip()
        qualification=request.form.get('qualification').strip()

        if not username or not fullname or not email or not password or not f_password or not qualification or not phone_no:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for('admin.add_staff'))

        if USER.query.filter_by(username=username).first():
            flash("Username already exits. Please try another!", "danger")
            return redirect(url_for('admin.add_staff'))
        
        if USER.query.filter_by(email=email).first():
            flash("Email already registered. Please try another!", "danger")
            return redirect(url_for('admin.add_staff'))
        
        if len(username) < 3:
            flash("Username must be 6 character long!","danger")
            return redirect(url_for('admin.add_staff'))
        
        if len(fullname) < 6:
            flash("Full Name must be 6 character long!","danger")
            return redirect(url_for('admin.add_staff'))
        
        if "@" not in email or "." not in email:
            flash("Invalid Email Address!","danger")
            return redirect(url_for('admin.add_staff'))
            
        if len(password) < 5:
            flash("Password must be 5 character long!", "danger")
            return redirect(url_for('admin.add_staff'))
        
        if f_password != password:
            flash("Password must be same!", "danger")
            return redirect(url_for('auth.add_staff'))
        
        if len(phone_no) != 10 or not phone_no.isdigit():
                 flash("Invalid Phone number!", "danger")
                 return redirect(url_for('auth.add_staff'))

        new_staff = USER(
            username = username,
            fullname=fullname,
            email=email,
            password= generate_password_hash(f_password),
            phone_number=phone_no,
            role ='staff',
            is_validated=False,
            qualification=qualification
        )
        db.session.add(new_staff)
        db.session.commit()
        flash("Added Staff! Successfully!", "success")
        return redirect(url_for("admin.find_staff"))
    return render_template("admin/add_staff.html")
#  =============================================================================================================           
# =================================================================================================================

@admin_bp.route("/staff/validate_staffs" , methods=['GET','POST'])
@role_validator("admin")
def validate_staff():
    validation_list = USER.query.filter_by(role='staff', is_validated=False).all()
    current_filter = "Pending"
    
    if request.method=='POST':
        validation=request.form.get('validation')

        if validation=='Pending':
            validation_list = USER.query.filter( USER.role=='staff', USER.is_validated==False, USER.status.in_(['active', 'inactive'])).all()

        if validation=='Approved':
            validation_list = USER.query.filter_by(role='staff', is_validated=True).all()
            
        if validation=='Rejected':
            validation_list = USER.query.filter_by(role='staff', status='blacklisted').all()
            
    return render_template(
        "admin/validate_staff.html", validation_list=validation_list, 
        current_filter=current_filter
    )
# Route to handle Approval
@admin_bp.route('/approve_staff/<int:user_id>', methods=['GET','POST'])
@role_validator('admin')
def approve_staff(user_id):
    staff = USER.query.get_or_404(user_id)
    staff.is_validated = True

    db.session.commit()
    flash('Staff member has been approved.', 'success')
    return redirect(request.referrer or url_for('admin.validate_staff'))


# Route to handle Rejection
@admin_bp.route('/reject_staff/<int:user_id>', methods=['GET','POST'])
@role_validator('admin')
def reject_staff(user_id):
    staff = USER.query.get_or_404(user_id)
    staff.is_validated = False
    staff.status = 'blacklisted'
    db.session.commit()
    flash('Staff member has been rejected and blacklisted.', 'danger')
    return redirect(request.referrer or url_for('admin.validate_staff'))