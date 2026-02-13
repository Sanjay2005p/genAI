from controller.database import db
from datetime import datetime
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

class role(db.Model):
    __tablename__ = "roles"
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), nullable=False, unique=True)

class user_role(db.Model):
    __tablename__ = "user_roles"
    user_role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.role_id"), nullable=False)
class teacher(db.Model):
    __tablename__ = "teachers"
    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    employee_id = db.Column(db.String(50), nullable=True, unique=True)
    department = db.Column(db.String(100), nullable=True)
    subject = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    qualification = db.Column(db.String(255), nullable=True)
    experience = db.Column(db.String(255), nullable=True)
    dob = db.Column(db.Date, nullable=True)
class student(db.Model):
    __tablename__ = "students"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    roll_number = db.Column(db.String(50), nullable=True, unique=True)
    department = db.Column(db.String(100), nullable=True)
    year_semester = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    grade = db.Column(db.String(10), nullable=True)

class admin(db.Model):
    __tablename__ = "admins"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    admin_identifier = db.Column(db.String(50), nullable=True, unique=True)
    phone = db.Column(db.String(30), nullable=True)
    dob = db.Column(db.Date, nullable=True)

class student_progress(db.Model):
    __tablename__ = "student_progress"
    progress_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    completion_percentage = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=db.func.current_timestamp())

class student_grade(db.Model):
    __tablename__ = "student_grades"
    grade_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Float, default=100)
    grade = db.Column(db.String(5), nullable=False)

class assignment(db.Model):
    __tablename__ = "assignments"
    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(100), nullable=False)
    total_marks = db.Column(db.Float, default=100)
    due_date = db.Column(db.DateTime)

class student_assignment(db.Model):
    __tablename__ = "student_assignments"
    student_assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.assignment_id"), nullable=False)
    score = db.Column(db.Float)
    submission_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending")

class quiz(db.Model):
    __tablename__ = "quizzes"
    quiz_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    total_questions = db.Column(db.Integer)
    total_marks = db.Column(db.Float, default=100)

class student_quiz(db.Model):
    __tablename__ = "student_quizzes"
    student_quiz_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.quiz_id"), nullable=False)
    score = db.Column(db.Float)
    correct_answers = db.Column(db.Integer)
    attempt_date = db.Column(db.DateTime)


class quiz_question(db.Model):
    __tablename__ = "quiz_questions"
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.quiz_id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.teacher_id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default="text")  # text, multiple_choice
    options = db.Column(db.Text, nullable=True)  # JSON for multiple choice options
    correct_answer = db.Column(db.Text, nullable=False)
    marks = db.Column(db.Float, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class student_quiz_answer(db.Model):
    __tablename__ = "student_quiz_answers"
    answer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_quiz_id = db.Column(db.Integer, db.ForeignKey("student_quizzes.student_quiz_id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("quiz_questions.question_id"), nullable=False)
    student_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    marks_obtained = db.Column(db.Float, default=0)


class ai_quiz_attempt(db.Model):
    __tablename__ = "ai_quiz_attempts"

    attempt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.String(50), nullable=False, default="school")
    question = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    hint = db.Column(db.Text, nullable=True)
    student_answer = db.Column(db.Text, nullable=True)
    verdict = db.Column(db.String(20), nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    checked_at = db.Column(db.DateTime, nullable=True)
