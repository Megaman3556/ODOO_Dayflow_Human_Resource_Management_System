from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user, login_required, current_user
)
from functools import wraps

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///company.sqlite3"
app.config["SECRET_KEY"] = "supersecretkey"  # Required for flask_login sessions
db = SQLAlchemy(app)
app.app_context().push()

# --- Flask-Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom decorator to secure Admin/HR routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.strip().upper() != 'HR':
            return render_template("error.html", message="Unauthorized Access"), 403
        return f(*args, **kwargs)
    return decorated_function

# --- Models ---
class User(db.Model, UserMixin): # Inherit from UserMixin
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    
    # Required for Flask-Login
    def get_id(self):
        return str(self.id)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    status = db.Column(db.String(20), nullable=False, default="Present")
    user = db.relationship("User", backref="attendance_records")

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    user = db.relationship("User", backref="leaves")

class EmployeeProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    cost_to_company_annual = db.Column(db.Float)
    cost_to_company_monthly = db.Column(db.Float)
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
    pf_employer_annual = db.Column(db.Float)
    pf_employer_monthly = db.Column(db.Float)
    total_annual = db.Column(db.Float)
    total_monthly = db.Column(db.Float)
    pf_employee_annual = db.Column(db.Float)
    pf_employee_monthly = db.Column(db.Float)
    esi_annual = db.Column(db.Float)
    esi_monthly = db.Column(db.Float)
    labor_welfare_annual = db.Column(db.Float)
    labor_welfare_monthly = db.Column(db.Float)
    net_salary_annual = db.Column(db.Float)
    net_salary_monthly = db.Column(db.Float)
    user = db.relationship("User", backref="salary")

# --- Authentication Routes ---
@app.route('/', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    else:
        person = User(
            company_name=request.form.get("company"),
            employee_id=request.form.get("employee_id"),
            name=request.form.get("name"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            role=request.form.get("role", "").strip().upper(),
            password=request.form.get("password")
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
        role = request.form.get("role", "").strip().upper()
        
        user = User.query.filter_by(employee_id=employee_id, password=password, role=role).first()
        if user:
            login_user(user) # Secure session
            if user.role == "HR":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("user", employee_id=user.employee_id))
        return render_template("error.html", message="Invalid credentials")

@app.route("/logout")
@login_required
def logout():
    logout_user() # Clear session
    return redirect("/login")

# --- Employee Routes (Secured) ---
@app.route("/user/<employee_id>")
@login_required
def user(employee_id):
    user = User.query.filter_by(employee_id=employee_id).first()
    if user: return render_template("dashboard.html", user=user)
    return render_template("error.html", message="User not found")

@app.route("/profile/<emp_id>")
@login_required
def profile(emp_id):
    user = User.query.filter_by(employee_id=emp_id).first()
    emp_profile = EmployeeProfile.query.filter_by(user_id=user.id).first()
    salary = Salary.query.filter_by(user_id=user.id).first()
    return render_template("profile.html", emp_profile=emp_profile, user=user, salary=salary)

@app.route("/profile/edit/<emp_id>", methods=["POST"])
@login_required
def emp_profile_edit(emp_id):
    user = User.query.filter_by(employee_id=emp_id).first()
    emp_profile = EmployeeProfile.query.filter_by(user_id=user.id).first()
    user.phone = request.form.get("phone")
    emp_profile.address = request.form.get("address")
    db.session.commit()
    return redirect("/profile/" + user.employee_id)

@app.route("/leave/<emp_id>", methods=["GET", "POST"])
@login_required
def emp_leave_request(emp_id):
    user = User.query.filter_by(employee_id=emp_id).first()
    if request.method == "GET":
        return render_template("leave_request.html", user=user)
    else:
        leave = Leave(
            user_id=user.id,
            leave_type=request.form.get("leave_type"),
            from_date=datetime.strptime(request.form.get("from_date"), "%Y-%m-%d").date(),
            to_date=datetime.strptime(request.form.get("to_date"), "%Y-%m-%d").date(),
            remarks=request.form.get("remarks")
        )
        db.session.add(leave)
        db.session.commit()
        return redirect("/leave/" + emp_id)

@app.route("/payroll/<emp_id>")
@login_required
def emp_payroll(emp_id):
    user = User.query.filter_by(employee_id=emp_id).first()
    salary_details = Salary.query.filter_by(user_id=user.id).first()
    return render_template("payroll.html", salary=salary_details, user=user)

@app.route("/attendance/<emp_id>")
@login_required
def emp_attendance(emp_id):
    user = User.query.filter_by(employee_id=emp_id).first()
    attendance = Attendance.query.filter_by(user_id=user.id).order_by(Attendance.date.desc()).all()
    return render_template("attendance.html", user=user, attendance=attendance)

@app.route("/attendance/checkin/<emp_id>", methods=["POST"])
@login_required
def check_in(emp_id):
    user = User.query.filter_by(employee_id=emp_id).first()
    today = date.today()
    if not Attendance.query.filter_by(user_id=user.id, date=today).first():
        att = Attendance(user_id=user.id, date=today, check_in=datetime.now().time(), status="Present")
        db.session.add(att)
        db.session.commit()
    return redirect("/attendance/" + emp_id)

@app.route("/attendance/checkout/<emp_id>", methods=["POST"])
@login_required
def check_out(emp_id):
    user = User.query.filter_by(employee_id=emp_id).first()
    today = date.today()
    att = Attendance.query.filter_by(user_id=user.id, date=today).first()
    if att and not att.check_out:
        att.check_out = datetime.now().time()
        db.session.commit()
    return redirect("/attendance/" + emp_id)

# ==========================================
# ADMIN / HR ROUTES (Secured with @admin_required)
# ==========================================

# Step 1: Dashboard & Employee Management
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    employees = User.query.all()
    pending_leaves = Leave.query.filter_by(status="Pending").count()
    return render_template("admin_dashboard.html", employees=employees, pending_leaves=pending_leaves)

@app.route("/admin/employees")
@admin_required
def admin_employees():
    employees = User.query.all()
    return render_template("admin_employees.html", employees=employees)

@app.route("/admin/employee/<emp_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_employee(emp_id):
    user = User.query.filter_by(employee_id=emp_id).first()
    emp_profile = EmployeeProfile.query.filter_by(user_id=user.id).first()
    if not emp_profile:
        emp_profile = EmployeeProfile(user_id=user.id)
        db.session.add(emp_profile)
        db.session.commit()

    if request.method == "POST":
        user.name = request.form.get("name")
        user.phone = request.form.get("phone")
        user.email = request.form.get("email")
        emp_profile.address = request.form.get("address")
        emp_profile.department = request.form.get("department")
        emp_profile.designation = request.form.get("designation")
        db.session.commit()
        return redirect(url_for("admin_employees"))
    return render_template("admin_edit_employee.html", user=user, emp_profile=emp_profile)

# Step 2: Leave Management
@app.route("/admin/leaves")
@admin_required
def admin_leaves():
    leaves = Leave.query.all()
    return render_template("admin_leaves.html", leaves=leaves)

@app.route("/admin/leave/<int:leave_id>/update", methods=["POST"])
@admin_required
def admin_update_leave(leave_id):
    leave = Leave.query.get(leave_id)
    action = request.form.get("action")
    if action in ["Approved", "Rejected"]:
        leave.status = action
        db.session.commit()
    return redirect(url_for("admin_leaves"))

# Step 3: Attendance Management
@app.route("/admin/attendance")
@admin_required
def admin_attendance():
    attendance_records = Attendance.query.order_by(Attendance.date.desc()).all()
    return render_template("admin_attendance.html", attendance_records=attendance_records)

# Step 4: Payroll Management
@app.route("/admin/payroll")
@admin_required
def admin_payroll():
    salaries = Salary.query.all()
    return render_template("admin_payroll.html", salaries=salaries)

@app.route("/admin/payroll/<emp_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_payroll(emp_id):
    user = User.query.filter_by(employee_id=emp_id).first()
    salary = Salary.query.filter_by(user_id=user.id).first()
    if not salary:
        salary = Salary(user_id=user.id)
        db.session.add(salary)
        db.session.commit()

    if request.method == "POST":
        salary.cost_to_company_annual = float(request.form.get("cost_to_company_annual", 0))
        salary.basic_annual = float(request.form.get("basic_annual", 0))
        salary.hra_annual = float(request.form.get("hra_annual", 0))
        salary.net_salary_annual = float(request.form.get("net_salary_annual", 0))
        db.session.commit()
        return redirect(url_for("admin_payroll"))
    return render_template("admin_edit_payroll.html", user=user, salary=salary)

if __name__ == '__main__':
    app.run(debug=True)