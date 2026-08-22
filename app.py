from flask import Flask, render_template,request,redirect, url_for
from datetime import datetime, date, timedelta
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


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///company.sqlite3"

db = SQLAlchemy(app) 


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

class Attendance(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    check_in = db.Column(db.Time)

    check_out = db.Column(db.Time)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Present"
    )

class Leave(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    leave_type = db.Column(
        db.String(50),
        nullable=False
    )

    from_date = db.Column(
        db.Date,
        nullable=False
    )

    to_date = db.Column(
        db.Date,
        nullable=False
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Pending",
        nullable=False
    )

class EmployeeProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )

    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))

    address = db.Column(db.String(255))
    city = db.Column(db.String(100))

    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    date_of_joining = db.Column(db.Date)
    employment_type = db.Column(db.String(50))
    reporting_manager = db.Column(db.String(100))

    profile_picture = db.Column(db.String(255))

class Salary(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )

    # Cost to Company
    cost_to_company_annual = db.Column(db.Float)
    cost_to_company_monthly = db.Column(db.Float)

    # Salary Components
    basic_annual = db.Column(db.Float)
    basic_monthly = db.Column(db.Float)

    hra_annual = db.Column(db.Float)
    hra_monthly = db.Column(db.Float)

    medical_annual = db.Column(db.Float)
    medical_monthly = db.Column(db.Float)

    special_allowance_annual = db.Column(db.Float)
    special_allowance_monthly = db.Column(db.Float)

    telephone_annual = db.Column(db.Float)
    telephone_monthly = db.Column(db.Float)

    conveyance_annual = db.Column(db.Float)
    conveyance_monthly = db.Column(db.Float)

    ex_gratia_annual = db.Column(db.Float)
    ex_gratia_monthly = db.Column(db.Float)

    # Employer contribution
    pf_employer_annual = db.Column(db.Float)
    pf_employer_monthly = db.Column(db.Float)

    # Gross salary
    total_annual = db.Column(db.Float)
    total_monthly = db.Column(db.Float)

    # Employee deductions
    pf_employee_annual = db.Column(db.Float)
    pf_employee_monthly = db.Column(db.Float)

    esi_annual = db.Column(db.Float)
    esi_monthly = db.Column(db.Float)

    labor_welfare_annual = db.Column(db.Float)
    labor_welfare_monthly = db.Column(db.Float)

    # Take home
    net_salary_annual = db.Column(db.Float)
    net_salary_monthly = db.Column(db.Float)

    user = db.relationship("User", backref="salary")

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
            return render_template("error.html",message="Passwords do not match")

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
    else:
        employee_id = request.form.get("employee_id")
        password = request.form.get("password")
        role = request.form.get("role")

        user = User.query.filter_by(
        employee_id=employee_id,
        password=password,
        role=role
        ).first()

        if user:
            if user.role!="HR":
                return redirect(url_for("user", employee_id=user.employee_id))
            
        return render_template("error.html",message="Invalid")

@app.route("/user/<employee_id>")
def user(employee_id):

    user = User.query.filter_by(employee_id=employee_id).first()

    if user:
        return render_template("dashboard.html", user=user)

    return render_template("error.html",message="User not found")

@app.route("/profile/<emp_id>")
def profile(emp_id):
    user=User.query.filter_by(employee_id=emp_id).first()
    user_id = user.id
    emp_profile=EmployeeProfile.query.filter_by(user_id=user_id).first()
    salary=Salary.query.filter_by(user_id=user_id).first()
    return render_template("profile.html",emp_profile=emp_profile,user=user,salary=salary)

@app.route("/profile/edit/<emp_id>", methods=["POST"])
def emp_profile_edit(emp_id):

    user = User.query.filter_by(employee_id=emp_id).first()

    if not user:
        return render_template("error.html",message="User not found")

    emp_profile = EmployeeProfile.query.filter_by(
        user_id=user.id
    ).first()

    new_address = request.form.get("address")
    new_phone = request.form.get("phone")

    # Update phone
    user.phone = new_phone

    # Update address
    emp_profile.address = new_address

    db.session.commit()

    return redirect("/profile/" + user.employee_id)

@app.route("/leave/<emp_id>", methods=["GET", "POST"])
def emp_leave_request(emp_id):

    user = User.query.filter_by(employee_id=emp_id).first()

    if not user:
        return render_template("error.html",message="User not found")

    if request.method == "GET":
        return render_template(
            "leave_request.html",
            user=user
        )

    else:
        leave_type = request.form.get("leave_type")
        from_date = request.form.get("from_date")
        to_date = request.form.get("to_date")
        remarks = request.form.get("remarks")

        from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        leave = Leave(
            user_id=user.id,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date,
            remarks=remarks
        )

        db.session.add(leave)
        db.session.commit()

        return render_template("error.html",message="Leave Request Submitted Successfully")

@app.route("/payroll/<emp_id>")
def emp_payroll(emp_id):
    user=User.query.filter_by(employee_id=emp_id).first()
    user_id=user.id
    salary_details=Salary.query.filter_by(user_id=user_id).first()
    return render_template("payroll.html",salary=salary_details,user=user)

@app.route("/attendance/<emp_id>")
def emp_attendance(emp_id):

    user = User.query.filter_by(
        employee_id=emp_id
    ).first()

    if not user:
        return render_template("error.html",message="User Not Found")

    attendance = Attendance.query.filter_by(
        user_id=user.id
    ).order_by(
        Attendance.date.desc()
    ).all()

    return render_template(
        "attendance.html",
        user=user,
        attendance=attendance
    )
@app.route("/attendance/checkin/<emp_id>", methods=["POST"])
def check_in(emp_id):

    user = User.query.filter_by(
        employee_id=emp_id
    ).first()

    if not user:
        return render_template("error.html",message="User Not Found")

    today = date.today()

    attendance = Attendance.query.filter_by(
        user_id=user.id,
        date=today
    ).first()

    if attendance:
        return render_template("error.html",message="Already Checked in Today")

    attendance = Attendance(
        user_id=user.id,
        date=today,
        check_in=datetime.now().time(),
        status="Present"
    )

    db.session.add(attendance)
    db.session.commit()

    return redirect("/attendance/" + emp_id)

@app.route("/attendance/checkout/<emp_id>", methods=["POST"])
def check_out(emp_id):

    user = User.query.filter_by(
        employee_id=emp_id
    ).first()

    if not user:
        return render_template("error.html",message="User Not Found")

    today = date.today()

    attendance = Attendance.query.filter_by(
        user_id=user.id,
        date=today
    ).first()

    if not attendance:
        return render_template("error.html",message="Please Check In First")

    if attendance.check_out:
        return render_template("error.html",message="Already Checked Out Today")

    attendance.check_out = datetime.now().time()

    db.session.commit()

    return redirect("/attendance/" + emp_id)

@app.route("/logout")
def logout():
    return redirect("/login")

if __name__ == '__main__':
    app.run(debug=True)