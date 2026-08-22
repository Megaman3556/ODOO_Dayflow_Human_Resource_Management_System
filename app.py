from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///datab.sqlite3"

db = SQLAlchemy(app) 

# once you run from app import app,db in shell (python) run type the below

app.app_context().push()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # employee / hr
    password = db.Column(db.String(255), nullable=False)
    
@app.route('/')
def register():
    return render_template("account.html")


@app.route("/login")
def login():
    return render_template("login.html")
if __name__ == '__main__':
    app.run(debug=True)