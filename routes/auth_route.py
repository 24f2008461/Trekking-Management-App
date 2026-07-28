from flask import session, request, render_template, Blueprint, flash, url_for, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, USER


auth_bp = Blueprint("auth",__name__)


@auth_bp.route("/")
def main():
   if 'user_id' in session:
      role = session.get('role')
      if role == 'admin':
         return redirect(url_for('admin.admin_dashboard'))
      elif role == 'staff':
         return redirect(url_for("staff.staff_dashboard"))
      else:
         return redirect(url_for("user.user_dashboard"))
   return render_template("mainpage.html")

@auth_bp.route("/login", methods=['GET','POST'])
def login():
   if request.method=="POST":
      uname = request.form.get('uname', '').strip()
      password = request.form.get('password', '').strip()
      loged_user = USER.query.filter_by(username=uname).first()
      if loged_user and check_password_hash(loged_user.password, password):

         if loged_user.status == "blacklisted":
            flash("Your Account has been blacklisted. Please Contact admin!", "danger")
            return redirect(url_for("auth.login"))
         

         session["user_id"] = loged_user.user_id
         session["role"] = loged_user.role.strip()
         session["username"] = loged_user.username
         session["status"] =  loged_user.status='active'
         flash(f"Welcome back, {loged_user.fullname}!", "success")


         if loged_user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
         if loged_user.role == "staff":
            return redirect(url_for("staff.staff_dashboard"))
         return redirect(url_for("user.user_dashboard"))
      flash("Invalid credentials.", "danger")
      
   return render_template("/auth/login.html")

@auth_bp.route("/register", methods=['GET','POST'])
def register():
   if request.method == 'POST':
      uname = request.form.get('uname','').strip()
      fname = request.form.get('fname','').strip()
      email = request.form.get('email','').strip()
      password = request.form.get('password','')
      f_password = request.form.get('fpassword','')
      phone_no = request.form.get('phone_no','').strip()

      if not uname or not email or not password or not f_password or not fname:
         flash("Please fill all required the Fields!","danger")
         return redirect(url_for('auth.register'))

      if len(uname) < 3:
         flash("Username must be 6 character long!","danger")
         return redirect(url_for('auth.register'))

      if len(fname) < 6:
         flash("Full Name must be 6 character long!","danger")
         return redirect(url_for('auth.register'))

      if "@" not in email or "." not in email:
         flash("Invalid Email Address!","danger")
         return redirect(url_for('auth.register'))

      if len(password) < 5:
         flash("Password must be 5 character long!","danger")
         return redirect(url_for('auth.register'))

      if f_password != password:
         flash("Password must be same!", "danger")
         return redirect(url_for('auth.register'))

      if len(phone_no) != 10 or not phone_no.isdigit():
         flash("Invalid Phone number!", "danger")
         return redirect(url_for('auth.register'))
      
      if USER.query.filter_by(username=uname).first():
         flash("Username already exits. Please try another!", "danger")
         return redirect(url_for("auth.register"))
      
      if USER.query.filter_by(email=email).first():
         flash("Email already registered. Please try another!", "danger")
         return redirect(url_for("auth.register"))

      new_user = USER(
         username=uname,
         fullname=fname,
         email=email,
         password=generate_password_hash(f_password),
         phone_number=phone_no,
         role='user',
         is_validated=True
      )
      db.session.add(new_user)
      db.session.commit()

      flash("Registration successful! Please log in.", "success")
      return redirect(url_for("auth.login"))
   
   return render_template("/auth/signup.html")


@auth_bp.route("/logout")
def logout():
   logged_user_id = session.get('user_id')
   if logged_user_id:
      logged_user = USER.query.get(logged_user_id)
      if logged_user:
         logged_user.status='inactive'
         db.session.commit()
   #Now clear session after setting status to inactive!
   session.clear()
   flash("Logged Out!" ,"info")
   return redirect(url_for('auth.main'))