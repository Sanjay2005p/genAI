from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from controller.confige import config
from controller.database import db
from controller.model import User, role, user_role, student, student_progress, student_grade, assignment, student_assignment, quiz, student_quiz, quiz_question, student_quiz_answer, teacher, admin, ai_quiz_attempt
from werkzeug.security import generate_password_hash, check_password_hash
from opeAI import generate_quiz_question, check_quiz_answer
from datetime import datetime
import os

app = Flask(__name__, instance_path=os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance')))
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


def parse_date_or_none(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form_data = {}
    if request.method == "POST":
        username = request.form.get("username")
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role_name = request.form.get("role")
        dob_value = parse_date_or_none(request.form.get("dob"))
        allowed_roles = {"teacher", "student", "admin"}
        form_data = {
            "username": username or "",
            "fullname": fullname or "",
            "email": email or "",
            "role": role_name or "",
            "dob": request.form.get("dob") or "",
            "employee_id": request.form.get("employee_id") or "",
            "department": request.form.get("department") or "",
            "subject": request.form.get("subject") or "",
            "phone": request.form.get("phone") or "",
            "qualification": request.form.get("qualification") or "",
            "experience": request.form.get("experience") or "",
            "roll_number": request.form.get("roll_number") or "",
            "year_semester": request.form.get("year_semester") or "",
            "gender": request.form.get("gender") or "",
            "grade": request.form.get("grade") or "",
            "admin_identifier": request.form.get("admin_identifier") or "",
        }
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", form_data=form_data), 400
        if role_name not in allowed_roles:
            flash("Please select a valid role.", "danger")
            return render_template("register.html", form_data=form_data), 400
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Try another one.", "danger")
            return render_template("register.html", form_data=form_data), 400
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered. Use a different email.", "danger")
            return render_template("register.html", form_data=form_data), 400
        
        try:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.flush()

            selected_role = role.query.filter_by(role_name=role_name).first()
            if not selected_role:
                db.session.rollback()
                flash("System role configuration is missing. Contact admin.", "danger")
                return render_template("register.html", form_data=form_data), 500

            user_role_entry = user_role(user_id=new_user.id, role_id=selected_role.role_id)
            db.session.add(user_role_entry)

            if role_name == "teacher":
                teacher_profile = teacher(
                    user_id=new_user.id,
                    name=fullname,
                    email=email,
                    employee_id=request.form.get('employee_id'),
                    department=request.form.get('department'),
                    subject=request.form.get('subject'),
                    phone=request.form.get('phone'),
                    qualification=request.form.get('qualification'),
                    experience=request.form.get('experience'),
                    dob=dob_value
                )
                db.session.add(teacher_profile)
            elif role_name == "student":
                student_profile = student(
                    user_id=new_user.id,
                    name=fullname,
                    email=email,
                    roll_number=request.form.get('roll_number'),
                    department=request.form.get('department'),
                    year_semester=request.form.get('year_semester'),
                    phone=request.form.get('phone'),
                    gender=request.form.get('gender'),
                    dob=dob_value,
                    grade=request.form.get('grade')
                )
                db.session.add(student_profile)
            elif role_name == "admin":
                admin_profile = admin(
                    user_id=new_user.id,
                    name=fullname,
                    email=email,
                    admin_identifier=request.form.get('admin_identifier'),
                    phone=request.form.get('phone'),
                    dob=dob_value
                )
                db.session.add(admin_profile)

            db.session.commit()
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for("login"))
        except Exception:
            db.session.rollback()
            flash("Unable to register right now. Please verify details and try again.", "danger")
            return render_template("register.html", form_data=form_data), 400
    
    return render_template("register.html", form_data=form_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    form_data = {}
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        form_data = {"username": username or ""}
        
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
            flash("Invalid username or password.", "danger")
            return render_template("index.html", form_data=form_data), 401
    
    return render_template("index.html", form_data=form_data)

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_role_entry = session.get("role")
    
    if user_role_entry == "student":
        return redirect(url_for("student_dashboard"))
    elif user_role_entry == "teacher":
        return redirect(url_for("teacher_dashboard"))
    elif user_role_entry == "admin":
        return redirect(url_for("admin_dashboard"))
    
    return redirect(url_for("login"))

@app.route("/student")
def student_dashboard():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))
    
    # Get student info
    student_info = student.query.filter_by(user_id=session["user_id"]).first()
    
    if not student_info:
        return "Student profile not found", 404
    
    # Get student assignments
    student_assignments = db.session.query(student_assignment, assignment).join(
        assignment, student_assignment.assignment_id == assignment.assignment_id
    ).filter(student_assignment.student_id == student_info.student_id).all()
    
    # Get student quizzes
    student_quizzes = db.session.query(student_quiz, quiz).join(
        quiz, student_quiz.quiz_id == quiz.quiz_id
    ).filter(student_quiz.student_id == student_info.student_id).all()
    
    # Get student grades
    student_grades = student_grade.query.filter_by(student_id=student_info.student_id).all()
    
    return render_template("student.html", 
                         user=session.get("username"),
                         student=student_info,
                         assignments=student_assignments,
                         quizzes=student_quizzes,
                         grades=student_grades)


@app.route('/student/quiz')
def student_quiz_page():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("login"))

    student_info = student.query.filter_by(user_id=session["user_id"]).first()
    if not student_info:
        return "Student profile not found", 404

    return render_template("quiz.html",
                         user=session.get("username"),
                         student=student_info)


@app.route("/api/student/quizzes", methods=["GET"])
def get_student_quizzes():
    if "user_id" not in session or session.get("role") != "student":
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        quizzes = quiz.query.all()
        return jsonify([{
            "quiz_id": q.quiz_id,
            "title": q.title,
            "subject": q.subject,
            "total_questions": q.total_questions or 0,
            "total_marks": q.total_marks or 0
        } for q in quizzes])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/student/quiz/<int:quiz_id>", methods=["GET"])
def get_quiz_for_student(quiz_id):
    if "user_id" not in session or session.get("role") != "student":
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        q = db.session.get(quiz, quiz_id)
        if not q:
            return jsonify({"error": "Quiz not found"}), 404
        
        questions = quiz_question.query.filter_by(quiz_id=quiz_id).all()
        return jsonify({
            "quiz_id": q.quiz_id,
            "title": q.title,
            "subject": q.subject,
            "total_marks": q.total_marks or 0,
            "questions": [{
                "question_id": qst.question_id,
                "question_text": qst.question_text,
                "question_type": qst.question_type,
                "options": qst.options,
                "marks": qst.marks
            } for qst in questions]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/student/quiz/submit", methods=["POST"])
def submit_student_quiz():
    if "user_id" not in session or session.get("role") != "student":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json(silent=True) or {}
    quiz_id = data.get("quiz_id")
    answers = data.get("answers", {})
    
    if not quiz_id:
        return jsonify({"error": "Quiz ID required"}), 400
    if not isinstance(answers, dict):
        return jsonify({"error": "answers must be an object"}), 400
    
    try:
        student_info = student.query.filter_by(user_id=session["user_id"]).first()
        if not student_info:
            return jsonify({"error": "Student profile not found"}), 404
        
        q = db.session.get(quiz, quiz_id)
        if not q:
            return jsonify({"error": "Quiz not found"}), 404
        
        # Create student quiz attempt
        student_attempt = student_quiz(
            student_id=student_info.student_id,
            quiz_id=quiz_id,
            attempt_date=datetime.utcnow()
        )
        db.session.add(student_attempt)
        db.session.flush()
        
        # Score the answers
        total_score = 0
        correct_count = 0
        questions = quiz_question.query.filter_by(quiz_id=quiz_id).all()
        
        for qst in questions:
            student_answer = answers.get(str(qst.question_id), "")
            is_correct = False
            correct_answer = (qst.correct_answer or "").strip()
            student_answer_normalized = (student_answer or "").strip()

            # Case-insensitive comparison for text and multiple choice
            if student_answer_normalized.lower() == correct_answer.lower():
                is_correct = True
                total_score += qst.marks
                correct_count += 1
            
            # Record answer
            answer_record = student_quiz_answer(
                student_quiz_id=student_attempt.student_quiz_id,
                question_id=qst.question_id,
                student_answer=student_answer,
                is_correct=is_correct,
                marks_obtained=qst.marks if is_correct else 0
            )
            db.session.add(answer_record)
        
        student_attempt.score = total_score
        student_attempt.correct_answers = correct_count
        db.session.commit()
        
        return jsonify({
            "message": "Quiz submitted",
            "score": total_score,
            "total_marks": q.total_marks or 0,
            "correct_answers": correct_count,
            "total_questions": q.total_questions or 0
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/teacher/quiz/create", methods=["POST"])
def create_quiz():
    if "user_id" not in session or session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    subject = (data.get("subject") or "").strip()
    
    if not title or not subject:
        return jsonify({"error": "Title and subject are required"}), 400
    
    try:
        new_quiz = quiz(title=title, subject=subject, total_questions=0, total_marks=0)
        db.session.add(new_quiz)
        db.session.commit()
        return jsonify({"quiz_id": new_quiz.quiz_id, "message": "Quiz created"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/teacher/quiz/<int:quiz_id>", methods=["PUT"])
def update_quiz(quiz_id):
    if "user_id" not in session or session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    subject = (data.get("subject") or "").strip()
    if not title or not subject:
        return jsonify({"error": "Title and subject are required"}), 400

    try:
        q = db.session.get(quiz, quiz_id)
        if not q:
            return jsonify({"error": "Quiz not found"}), 404
        q.title = title
        q.subject = subject
        db.session.commit()
        return jsonify({"message": "Quiz updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/teacher/quiz/<int:quiz_id>", methods=["DELETE"])
def delete_quiz(quiz_id):
    if "user_id" not in session or session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        q = db.session.get(quiz, quiz_id)
        if not q:
            return jsonify({"error": "Quiz not found"}), 404
        
        # Delete dependent student answers and attempts first.
        question_ids = [row.question_id for row in quiz_question.query.filter_by(quiz_id=quiz_id).all()]
        if question_ids:
            student_quiz_answer.query.filter(
                student_quiz_answer.question_id.in_(question_ids)
            ).delete(synchronize_session=False)

        attempt_ids = [row.student_quiz_id for row in student_quiz.query.filter_by(quiz_id=quiz_id).all()]
        if attempt_ids:
            student_quiz_answer.query.filter(
                student_quiz_answer.student_quiz_id.in_(attempt_ids)
            ).delete(synchronize_session=False)
            student_quiz.query.filter(
                student_quiz.student_quiz_id.in_(attempt_ids)
            ).delete(synchronize_session=False)

        quiz_question.query.filter_by(quiz_id=quiz_id).delete(synchronize_session=False)
        db.session.delete(q)
        db.session.commit()
        return jsonify({"message": "Quiz deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/teacher/quiz/<int:quiz_id>/questions", methods=["GET"])
def get_quiz_questions(quiz_id):
    if "user_id" not in session or session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        q = db.session.get(quiz, quiz_id)
        if not q:
            return jsonify({"error": "Quiz not found"}), 404
        
        questions = quiz_question.query.filter_by(quiz_id=quiz_id).all()
        return jsonify([{
            "question_id": qst.question_id,
            "question_text": qst.question_text,
            "question_type": qst.question_type,
            "options": qst.options,
            "correct_answer": qst.correct_answer,
            "marks": qst.marks
        } for qst in questions])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/teacher/question/create", methods=["POST"])
def create_question():
    if "user_id" not in session or session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json(silent=True) or {}
    quiz_id = data.get("quiz_id")
    question_text = (data.get("question_text") or "").strip()
    question_type = data.get("question_type", "text")
    options = data.get("options")
    correct_answer = (data.get("correct_answer") or "").strip()
    try:
        marks = float(data.get("marks", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "Marks must be a number"}), 400
    
    if not quiz_id or not question_text or not correct_answer:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        teacher_info = teacher.query.filter_by(user_id=session["user_id"]).first()
        if not teacher_info:
            return jsonify({"error": "Teacher profile not found"}), 404
        q = db.session.get(quiz, quiz_id)
        if not q:
            return jsonify({"error": "Quiz not found"}), 404
        
        new_question = quiz_question(
            quiz_id=quiz_id,
            teacher_id=teacher_info.teacher_id,
            question_text=question_text,
            question_type=question_type,
            options=options,
            correct_answer=correct_answer,
            marks=marks
        )
        db.session.add(new_question)
        
        # Update quiz total marks and questions count
        q.total_marks = (q.total_marks or 0) + marks
        q.total_questions = (q.total_questions or 0) + 1
        
        db.session.commit()
        return jsonify({"question_id": new_question.question_id, "message": "Question created"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/teacher/question/<int:question_id>", methods=["GET"])
def get_question(question_id):
    if "user_id" not in session or session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        qst = db.session.get(quiz_question, question_id)
        if not qst:
            return jsonify({"error": "Question not found"}), 404
        
        return jsonify({
            "question_id": qst.question_id,
            "question_text": qst.question_text,
            "question_type": qst.question_type,
            "options": qst.options,
            "correct_answer": qst.correct_answer,
            "marks": qst.marks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/teacher/question/<int:question_id>", methods=["PUT"])
def update_question(question_id):
    if "user_id" not in session or session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json(silent=True) or {}
    question_text = (data.get("question_text") or "").strip()
    question_type = data.get("question_type", "text")
    options = data.get("options")
    correct_answer = (data.get("correct_answer") or "").strip()
    try:
        marks = float(data.get("marks", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "Marks must be a number"}), 400
    
    if not question_text or not correct_answer:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        qst = db.session.get(quiz_question, question_id)
        if not qst:
            return jsonify({"error": "Question not found"}), 404
        
        old_marks = qst.marks
        qst.question_text = question_text
        qst.question_type = question_type
        qst.options = options
        qst.correct_answer = correct_answer
        qst.marks = marks
        
        # Update quiz total marks
        q = db.session.get(quiz, qst.quiz_id)
        if not q:
            return jsonify({"error": "Parent quiz not found"}), 404
        q.total_marks = max(0, (q.total_marks or 0) - old_marks + marks)
        
        db.session.commit()
        return jsonify({"message": "Question updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/teacher/question/<int:question_id>", methods=["DELETE"])
def delete_question(question_id):
    if "user_id" not in session or session.get("role") != "teacher":
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        qst = db.session.get(quiz_question, question_id)
        if not qst:
            return jsonify({"error": "Question not found"}), 404
        
        quiz_id = qst.quiz_id
        marks = qst.marks
        
        # Update quiz total marks and questions count
        q = db.session.get(quiz, quiz_id)
        if not q:
            return jsonify({"error": "Parent quiz not found"}), 404
        q.total_marks = max(0, (q.total_marks or 0) - marks)
        q.total_questions = max(0, (q.total_questions or 0) - 1)

        student_quiz_answer.query.filter_by(question_id=question_id).delete(synchronize_session=False)
        
        db.session.delete(qst)
        db.session.commit()
        return jsonify({"message": "Question deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/teacher/quiz")
def teacher_quiz_page():
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("login"))
    
    teacher_info = teacher.query.filter_by(user_id=session["user_id"]).first()
    if not teacher_info:
        return "Teacher profile not found", 404
    
    # Get all quizzes created by this teacher
    teacher_quizzes = quiz.query.all()  # In future, filter by teacher_id if added to quiz model
    
    return render_template("teacher_quiz.html",
                         user=session.get("username"),
                         teacher=teacher_info,
                         quizzes=teacher_quizzes)


@app.route("/teacher")
def teacher_dashboard():
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("login"))

    teacher_info = teacher.query.filter_by(user_id=session["user_id"]).first()
    if not teacher_info:
        return "Teacher profile not found", 404

    students_list = student.query.all()
    students_data = []
    for stud in students_list:
        progress = student_progress.query.filter_by(student_id=stud.student_id).all()
        grades = student_grade.query.filter_by(student_id=stud.student_id).all()
        students_data.append({
            "student": stud,
            "progress": progress,
            "grades": grades,
        })

    return render_template(
        "teacher.html",
        user=session.get("username"),
        teacher=teacher_info,
        students=students_data,
    )


@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    admin_info = admin.query.filter_by(user_id=session["user_id"]).first()
    all_users = User.query.all()

    users_data = []
    for usr in all_users:
        user_role_entry = user_role.query.filter_by(user_id=usr.id).first()
        role_name = "unknown"
        if user_role_entry:
            role_obj = role.query.filter_by(role_id=user_role_entry.role_id).first()
            if role_obj:
                role_name = role_obj.role_name
        users_data.append({"user": usr, "role": role_name})

    stats = {
        "total_users": len(users_data),
        "total_students": student.query.count(),
        "total_teachers": teacher.query.count(),
        "total_assignments": assignment.query.count(),
    }

    return render_template(
        "admin.html",
        user=session.get("username"),
        admin_profile=admin_info,
        users=users_data,
        stats=stats,
    )


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    usr = db.session.get(User, user_id)
    if not usr:
        return redirect(url_for('admin_dashboard'))

    user_role.query.filter_by(user_id=usr.id).delete()
    student.query.filter_by(user_id=usr.id).delete()
    teacher.query.filter_by(user_id=usr.id).delete()
    admin.query.filter_by(user_id=usr.id).delete()
    db.session.delete(usr)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/change_role', methods=['POST'])
def admin_change_role():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    user_id = request.form.get('user_id')
    new_role = request.form.get('role')
    if not user_id or not new_role:
        return redirect(url_for('admin_dashboard'))

    usr = db.session.get(User, int(user_id))
    if not usr:
        return redirect(url_for('admin_dashboard'))

    role_obj = role.query.filter_by(role_name=new_role).first()
    if not role_obj:
        return redirect(url_for('admin_dashboard'))

    ur = user_role.query.filter_by(user_id=usr.id).first()
    if ur:
        ur.role_id = role_obj.role_id
    else:
        db.session.add(user_role(user_id=usr.id, role_id=role_obj.role_id))

    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
        

