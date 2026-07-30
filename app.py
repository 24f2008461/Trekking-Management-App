import os  
from flask import Flask,session,g
from werkzeug.security import generate_password_hash
from flask import render_template
from models import db, USER
from routes.auth_route import auth_bp
from routes.admin_route import admin_bp
from routes.user_route import user_bp
from routes.staff_route import staff_bp
# Setting directory
cur_dir = os.path.abspath(os.path.dirname(__file__))  # current/working directory


# Flask App creation
app = Flask(__name__)

#Configuring Database
app.config['SQLALCHEMY_DATABASE_URI']  = "sqlite:///" + os.path.join(cur_dir, "instance", "trekkapp.db")
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY","prj-secret-key-tma")


#Initialising Database
os.makedirs(os.path.join(os.path.dirname(__file__), "instance"),exist_ok=True)
db.init_app(app)


#Adding Admin to Database if not present
with app.app_context():
    db.create_all()
    if not USER.query.filter_by(role="admin").first():
        admin = USER(
            username="admin",
            email="admin@tmapp.com",
            fullname="System Admin",
            password= generate_password_hash("admin@777"),
            phone_number=9191919191,
            role="admin",
            is_validated=True
        )
        db.session.add(admin)
        db.session.commit()


app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(staff_bp)


if __name__ == "__main__":
    app.run(debug=True,port=5500)
