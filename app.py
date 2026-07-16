import os
from flask import Flask
from flask import render_template
from models import db, user



cur_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

#Configuring Database
app.config['SQLALCHEMY_DATABASE_URI']  = "sqlite:///project.db"

app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

app.config["secret_key"] = "prj-secret-key"


#Initialising Database
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(debug=True)
