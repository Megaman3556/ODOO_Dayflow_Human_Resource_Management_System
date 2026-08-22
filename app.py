from flask import Flask, render_template,request,redirect, url_for
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
    
@app.route('/',methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')

    else:
        company_name = request.form.get("company")
        employee_id = request.form.get("employee_id")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        role = request.form.get("role")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if password != confirm_password:
            return "Passwords do not match"

        person=User(
            company_name=company_name,
            employee_id=employee_id,
            name=name,
            email=email,
            phone=phone,
            role=role,
            password=password
        )

        db.session.add(person)
        db.session.commit()
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")

    user = User.query.filter_by(
        email=email,
        password=password,
        role=role
    ).first()

    if user:
        return redirect(url_for("user", employee_id=user.employee_id))

    return "Invalid email, password, or role"


@app.route("/user/<employee_id>")
def user(employee_id):

    user = User.query.filter_by(employee_id=employee_id).first()

    if user:
        return render_template("user.html", user=user)

    return "User not found"

if __name__ == '__main__':
    app.run(debug=True)