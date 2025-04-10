from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db, mail
from app.models.user import User, HRProfile
from app.models.job import Job, JobApplication
from app.utils.decorators import hr_required
from flask_mail import Message
from datetime import datetime

hr = Blueprint('hr', __name__)

@hr.route('/dashboard')
@login_required
@hr_required
def dashboard():
    # Get HR's jobs
    jobs = Job.query.filter_by(hr_profile_id=current_user.hr_profile.id).order_by(Job.posted_date.desc()).all()
    
    # Count total applications and shortlisted applications
    total_applications = 0
    shortlisted_applications = 0
    
    for job in jobs:
        total_applications += job.applications.count()
        shortlisted_applications += job.applications.filter_by(status='shortlisted').count()
    
    return render_template('hr/dashboard.html', 
                           jobs=jobs, 
                           total_applications=total_applications, 
                           shortlisted_applications=shortlisted_applications)


@hr.route('/post-job', methods=['GET', 'POST'])
@login_required
@hr_required
def post_job():
    if request.method == 'POST':
        # Create new job
        new_job = Job(
            hr_profile_id=current_user.hr_profile.id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            requirements=request.form.get('requirements'),
            location=request.form.get('location'),
            job_type=request.form.get('job_type'),
            salary_range=request.form.get('salary_range')
        )
        
        # Handle closing date
        closing_date_str = request.form.get('closing_date')
        if closing_date_str:
            try:
                closing_date = datetime.strptime(closing_date_str, '%Y-%m-%d')
                new_job.closing_date = closing_date
            except ValueError:
                flash('Invalid date format for closing date.')
                return redirect(url_for('hr.post_job'))
        
        db.session.add(new_job)
        db.session.commit()
        
        flash('Job posted successfully!')
        return redirect(url_for('hr.view_jobs'))
    
    return render_template('hr/post_job.html')


@hr.route('/jobs')
@login_required
@hr_required
def view_jobs():
    jobs = Job.query.filter_by(hr_profile_id=current_user.hr_profile.id).order_by(Job.posted_date.desc()).all()
    return render_template('hr/jobs.html', jobs=jobs)


@hr.route('/job/<int:job_id>')
@login_required
@hr_required
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to view this job.')
        return redirect(url_for('hr.view_jobs'))
    
    return render_template('hr/job_details.html', job=job)


@hr.route('/job/<int:job_id>/applications')
@login_required
@hr_required
def view_applications(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to view applications for this job.')
        return redirect(url_for('hr.view_jobs'))
    
    # Get all applications for this job
    applications = JobApplication.query.filter_by(job_id=job_id).order_by(JobApplication.similarity_score.desc()).all()
    
    return render_template('hr/applications.html', job=job, applications=applications)


@hr.route('/job/<int:job_id>/shortlisted')
@login_required
@hr_required
def view_shortlisted(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to view shortlisted candidates for this job.')
        return redirect(url_for('hr.view_jobs'))
    
    # Get shortlisted applications for this job
    shortlisted = JobApplication.query.filter_by(job_id=job_id, status='shortlisted').order_by(JobApplication.similarity_score.desc()).all()
    
    return render_template('hr/shortlisted.html', job=job, shortlisted=shortlisted)


@hr.route('/job/<int:job_id>/send-emails', methods=['POST'])
@login_required
@hr_required
def send_emails(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to send emails for this job.')
        return redirect(url_for('hr.view_jobs'))
    
    # Get shortlisted applications that haven't been emailed yet
    shortlisted = JobApplication.query.filter_by(job_id=job_id, status='shortlisted', email_sent=False).all()
    
    if not shortlisted:
        flash('No new shortlisted candidates to email.')
        return redirect(url_for('hr.view_shortlisted', job_id=job_id))
    
    # Get email content from form
    subject = request.form.get('subject')
    body = request.form.get('body')
    
    if not subject or not body:
        flash('Please provide a subject and body for the email.')
        return redirect(url_for('hr.view_shortlisted', job_id=job_id))
    
    # Send emails
    with mail.connect() as conn:
        for application in shortlisted:
            student = User.query.get(application.student_profile.user_id)
            
            msg = Message(
                subject=subject,
                recipients=[student.email],
                body=body,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            conn.send(msg)
            
            # Mark as emailed
            application.email_sent = True
    
    db.session.commit()
    
    flash(f'Emails sent to {len(shortlisted)} shortlisted candidates.')
    return redirect(url_for('hr.view_shortlisted', job_id=job_id))


@hr.route('/application/<int:application_id>/update-status', methods=['POST'])
@login_required
@hr_required
def update_application_status(application_id):
    application = JobApplication.query.get_or_404(application_id)
    job = application.job
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to update this application.', 'danger')
        return redirect(url_for('hr.view_jobs'))
    
    # Get the new status from form data
    new_status = request.form.get('status')
    if new_status not in ['pending', 'shortlisted', 'rejected']:
        flash('Invalid status provided.', 'danger')
        return redirect(url_for('hr.view_applications', job_id=job.id))
    
    # Update the application status
    application.status = new_status
    
    # If shortlisting, set shortlisted_date
    if new_status == 'shortlisted':
        application.shortlisted_date = datetime.utcnow()
    
    db.session.commit()
    
    status_text = new_status.capitalize()
    flash(f'Application status updated to {status_text}.', 'success')
    return redirect(url_for('hr.view_applications', job_id=job.id)) 