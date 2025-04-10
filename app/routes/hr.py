from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from app import db, mail
from app.models.user import User, HRProfile
from app.models.job import Job, JobApplication
from app.utils.decorators import hr_required
from flask_mail import Message
from datetime import datetime
import os

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


@hr.route('/job/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
@hr_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to edit this job.')
        return redirect(url_for('hr.view_jobs'))
    
    if request.method == 'POST':
        # Update job details
        job.title = request.form.get('title')
        job.description = request.form.get('description')
        job.requirements = request.form.get('requirements')
        job.location = request.form.get('location')
        job.job_type = request.form.get('job_type')
        job.salary_range = request.form.get('salary_range')
        
        # Handle is_active checkbox
        job.is_active = 'is_active' in request.form
        
        # Handle closing date
        closing_date_str = request.form.get('closing_date')
        if closing_date_str:
            try:
                closing_date = datetime.strptime(closing_date_str, '%Y-%m-%d')
                job.closing_date = closing_date
            except ValueError:
                flash('Invalid date format for closing date.', 'warning')
                return render_template('hr/edit_job.html', job=job)
        else:
            job.closing_date = None
        
        db.session.commit()
        
        flash('Job updated successfully!', 'success')
        return redirect(url_for('hr.view_job', job_id=job.id))
    
    return render_template('hr/edit_job.html', job=job)


@hr.route('/job/<int:job_id>/toggle-status')
@login_required
@hr_required
def toggle_job_status(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to modify this job.', 'danger')
        return redirect(url_for('hr.view_jobs'))
    
    # Toggle the status
    job.is_active = not job.is_active
    db.session.commit()
    
    status_msg = "activated" if job.is_active else "deactivated"
    flash(f'Job "{job.title}" has been {status_msg}.', 'success')
    
    return redirect(url_for('hr.view_job', job_id=job.id))


@hr.route('/application/<int:application_id>/shortlist')
@login_required
@hr_required
def shortlist_application(application_id):
    application = JobApplication.query.get_or_404(application_id)
    job = Job.query.get_or_404(application.job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to manage applications for this job.', 'danger')
        return redirect(url_for('hr.view_jobs'))
    
    # Update application status
    application.status = 'shortlisted'
    db.session.commit()
    
    flash('Candidate has been shortlisted successfully!', 'success')
    return redirect(url_for('hr.view_applications', job_id=job.id))


@hr.route('/application/<int:application_id>/reject')
@login_required
@hr_required
def reject_application(application_id):
    application = JobApplication.query.get_or_404(application_id)
    job = Job.query.get_or_404(application.job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to manage applications for this job.', 'danger')
        return redirect(url_for('hr.view_jobs'))
    
    # Update application status
    application.status = 'rejected'
    db.session.commit()
    
    flash('Application has been rejected.', 'info')
    return redirect(url_for('hr.view_applications', job_id=job.id))


@hr.route('/application/<int:application_id>/view-resume')
@login_required
@hr_required
def view_resume(application_id):
    application = JobApplication.query.get_or_404(application_id)
    job = Job.query.get_or_404(application.job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to view resumes for this job.', 'danger')
        return redirect(url_for('hr.view_jobs'))
    
    # Get the resume path and render it or redirect to it
    resume_path = application.resume_path
    student_name = f"{application.student_profile.user.first_name} {application.student_profile.user.last_name}"
    
    return render_template('hr/view_resume.html', 
                          application=application, 
                          job=job, 
                          resume_path=resume_path,
                          student_name=student_name)


@hr.route('/application/<int:application_id>/resume')
@login_required
@hr_required
def serve_resume(application_id):
    """Serve resume file for a specific application"""
    application = JobApplication.query.get_or_404(application_id)
    job = Job.query.get_or_404(application.job_id)
    
    # Check if job belongs to current HR
    if job.hr_profile_id != current_user.hr_profile.id:
        flash('You do not have permission to view resumes for this job.', 'danger')
        return redirect(url_for('hr.view_jobs'))
    
    # Get just the filename from the resume path
    if os.path.exists(application.resume_path):
        return send_file(application.resume_path, as_attachment=False)
    else:
        flash('Resume file not found.', 'danger')
        return redirect(url_for('hr.view_shortlisted', job_id=job.id))


@hr.route('/all-applications')
@login_required
@hr_required
def view_all_applications():
    """View all applications across all jobs posted by the HR"""
    # Get all jobs by this HR
    jobs = Job.query.filter_by(hr_profile_id=current_user.hr_profile.id).all()
    job_ids = [job.id for job in jobs]
    
    # Get all applications for these jobs
    applications = JobApplication.query.filter(JobApplication.job_id.in_(job_ids)).order_by(JobApplication.application_date.desc()).all()
    
    # Group applications by job
    applications_by_job = {}
    for app in applications:
        if app.job_id not in applications_by_job:
            applications_by_job[app.job_id] = []
        applications_by_job[app.job_id].append(app)
    
    return render_template('hr/all_applications.html', 
                          applications=applications, 
                          applications_by_job=applications_by_job, 
                          jobs=jobs)


@hr.route('/all-shortlisted')
@login_required
@hr_required
def view_all_shortlisted():
    """View all shortlisted candidates across all jobs posted by the HR"""
    # Get all jobs by this HR
    jobs = Job.query.filter_by(hr_profile_id=current_user.hr_profile.id).all()
    job_ids = [job.id for job in jobs]
    
    # Get all shortlisted applications for these jobs
    shortlisted = JobApplication.query.filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.status == 'shortlisted'
    ).order_by(JobApplication.similarity_score.desc()).all()
    
    # Group shortlisted applications by job
    shortlisted_by_job = {}
    for app in shortlisted:
        if app.job_id not in shortlisted_by_job:
            shortlisted_by_job[app.job_id] = []
        shortlisted_by_job[app.job_id].append(app)
    
    return render_template('hr/all_shortlisted.html', 
                          shortlisted=shortlisted, 
                          shortlisted_by_job=shortlisted_by_job, 
                          jobs=jobs) 