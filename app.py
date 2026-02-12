from flask import Flask, render_template, request, redirect, url_for, session
from controller.confige import config
from controller.database import db
from controller.model import User, role, user_role
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config.from_object(config)
app.secret_key = 'your-secret-key-change-this'
db.init_app(app)
with app.app_context():
    db.create_all()
    roles = [{"role_id": 1, "role_name": "admin"}
            ,{"role_id": 2, "role_name": "teacher"}
            ,{"role_id": 3, "role_name": "student"}
            ]
    for r in roles:
        existing_role = db.session.get(role, r["role_id"])
        if not existing_role:
            db.session.add(role(role_id=r["role_id"], role_name=r["role_name"]))
    db.session.commit()
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role_name = request.form.get("role")
        
        if password != confirm_password:
            return "Passwords do not match!", 400
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists!", 400
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.flush()
        
        # Get the role from database
        selected_role = role.query.filter_by(role_name=role_name).first()
        if selected_role:
            user_role_entry = user_role(user_id=new_user.id, role_id=selected_role.role_id)
            db.session.add(user_role_entry)
        
        db.session.commit()
        
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            
            # Get user's role
            user_role_entry = user_role.query.filter_by(user_id=user.id).first()
            if user_role_entry:
                user_role_obj = role.query.filter_by(role_id=user_role_entry.role_id).first()
                if user_role_obj:
                    session["role"] = user_role_obj.role_name
            
            return redirect(url_for("home"))
        else:
            return "Invalid username or password!", 401
    
    return render_template("index.html")

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_role_entry = session.get("role")
    
    if user_role_entry == "student":
        return redirect(url_for("student_dashboard"))
    elif user_role_entry == "teacher":
        return redirect(url_for("teacher_dashboard"))
    
    return redirect(url_for("login"))

@app.route("/student")
def student_dashboard():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))
    return render_template("student.html", user=session.get("username"))

@app.route("/teacher")
def teacher_dashboard():
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("login"))
    return render_template("teacher.html", user=session.get("username"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
        