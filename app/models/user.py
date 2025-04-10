from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'hr' or 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User profile information
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    
    # Relationships
    hr_profile = db.relationship('HRProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_hr(self):
        return self.role == 'hr'
    
    def is_student(self):
        return self.role == 'student'


class HRProfile(db.Model):
    __tablename__ = 'hr_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(128))
    company_website = db.Column(db.String(128))
    position = db.Column(db.String(64))
    department = db.Column(db.String(64))
    
    # Relationships
    jobs = db.relationship('Job', backref='hr_profile', lazy='dynamic', cascade='all, delete-orphan')


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    university = db.Column(db.String(128))
    degree = db.Column(db.String(64))
    graduation_year = db.Column(db.Integer)
    skills = db.Column(db.Text)
    
    # Current resume path
    resume_path = db.Column(db.String(256))
    
    # Relationships
    applications = db.relationship('JobApplication', backref='student_profile', lazy='dynamic', cascade='all, delete-orphan')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 