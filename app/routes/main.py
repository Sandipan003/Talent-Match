from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_hr():
            return redirect(url_for('hr.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return render_template('main/index.html')

@main.route('/about')
def about():
    return render_template('main/about.html')

@main.route('/contact')
def contact():
    return render_template('main/contact.html') 