from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_hr():
            flash('Access denied. HR login required.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_student():
            flash('Access denied. Student login required.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function 