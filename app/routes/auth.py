from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User, HRProfile, StudentProfile
from werkzeug.urls import url_parse

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_hr():
            return redirect(url_for('hr.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.verify_password(password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if user.is_hr():
                next_page = url_for('hr.dashboard')
            else:
                next_page = url_for('student.dashboard')
        
        return redirect(next_page)
    
    return render_template('auth/login.html')


@auth.route('/register/hr', methods=['GET', 'POST'])
def register_hr():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if email or username already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.')
            return redirect(url_for('auth.register_hr'))
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('auth.register_hr'))
        
        # Create new user
        new_user = User(
            email=email,
            username=username,
            password=password,
            role='hr',
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            phone=request.form.get('phone')
        )
        
        # Create HR profile
        hr_profile = HRProfile(
            company_name=request.form.get('company_name'),
            company_website=request.form.get('company_website'),
            position=request.form.get('position'),
            department=request.form.get('department')
        )
        
        new_user.hr_profile = hr_profile
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_hr.html')


@auth.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if email or username already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.')
            return redirect(url_for('auth.register_student'))
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('auth.register_student'))
        
        # Create new user
        new_user = User(
            email=email,
            username=username,
            password=password,
            role='student',
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            phone=request.form.get('phone')
        )
        
        # Create student profile
        student_profile = StudentProfile(
            university=request.form.get('university'),
            degree=request.form.get('degree'),
            graduation_year=request.form.get('graduation_year'),
            skills=request.form.get('skills')
        )
        
        new_user.student_profile = student_profile
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_student.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 