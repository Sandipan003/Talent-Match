from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User, StudentProfile
from app.models.job import Job, JobApplication
from app.utils.decorators import student_required
from app.utils.resume_processor import extract_text, calculate_similarity
import os
from datetime import datetime

student = Blueprint('student', __name__)

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Get student's applications
    applications = JobApplication.query.filter_by(student_profile_id=current_user.student_profile.id).order_by(JobApplication.application_date.desc()).all()
    
    # Get count of pending and shortlisted applications
    pending_count = sum(1 for app in applications if app.status == 'pending')
    shortlisted_count = sum(1 for app in applications if app.status == 'shortlisted')
    
    # Get recommended jobs (active jobs with no applications yet)
    applied_job_ids = [app.job_id for app in applications]
    recommended_jobs = Job.query.filter(Job.is_active == True, ~Job.id.in_(applied_job_ids)).order_by(Job.posted_date.desc()).limit(5).all()
    
    return render_template('student/dashboard.html', 
                           applications=applications, 
                           pending_count=pending_count,
                           shortlisted_count=shortlisted_count,
                           recommended_jobs=recommended_jobs)


@student.route('/jobs')
@login_required
@student_required
def browse_jobs():
    # Get search parameters
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    
    # Build query
    query = Job.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(Job.title.ilike(f'%{search}%') | Job.description.ilike(f'%{search}%'))
    
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    if job_type:
        query = query.filter_by(job_type=job_type)
    
    # Get jobs
    jobs = query.order_by(Job.posted_date.desc()).all()
    
    # Get applied jobs
    applications = JobApplication.query.filter_by(student_profile_id=current_user.student_profile.id).all()
    applied_job_ids = {app.job_id for app in applications}
    
    return render_template('student/browse_jobs.html', 
                           jobs=jobs, 
                           applied_job_ids=applied_job_ids,
                           search=search,
                           location=location,
                           job_type=job_type)


@student.route('/job/<int:job_id>')
@login_required
@student_required
def view_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if job is active
    if not job.is_active:
        flash('This job is no longer active.')
        return redirect(url_for('student.browse_jobs'))
    
    # Check if already applied
    application = JobApplication.query.filter_by(job_id=job_id, student_profile_id=current_user.student_profile.id).first()
    
    return render_template('student/job_details.html', job=job, application=application)


@student.route('/job/<int:job_id>/apply', methods=['GET', 'POST'])
@login_required
@student_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if job is active
    if not job.is_active:
        flash('This job is no longer active.')
        return redirect(url_for('student.browse_jobs'))
    
    # Check if already applied
    existing_application = JobApplication.query.filter_by(job_id=job_id, student_profile_id=current_user.student_profile.id).first()
    if existing_application:
        flash('You have already applied for this job.')
        return redirect(url_for('student.view_job', job_id=job_id))
    
    if request.method == 'POST':
        # Check if resume was uploaded
        if 'resume' not in request.files:
            flash('No resume file provided.')
            return redirect(url_for('student.apply_job', job_id=job_id))
        
        resume_file = request.files['resume']
        
        # If user does not select file, browser also submits an empty part without filename
        if resume_file.filename == '':
            flash('No resume file selected.')
            return redirect(url_for('student.apply_job', job_id=job_id))
        
        # Check file extension
        allowed_extensions = {'pdf', 'docx', 'txt'}
        if not ('.' in resume_file.filename and resume_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            flash('Invalid file format. Please upload a PDF, DOCX, or TXT file.')
            return redirect(url_for('student.apply_job', job_id=job_id))
        
        # Save the resume
        filename = secure_filename(f"{current_user.username}_{job_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{resume_file.filename.rsplit('.', 1)[1].lower()}")
        resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(resume_path)
        
        # Extract text from resume
        resume_text = extract_text(resume_path)
        
        # Calculate similarity score with job description
        similarity_score = calculate_similarity(job.description, resume_text)
        
        # Determine status based on similarity score
        status = 'shortlisted' if similarity_score >= 70 else 'pending'
        
        # Create application
        application = JobApplication(
            job_id=job_id,
            student_profile_id=current_user.student_profile.id,
            resume_path=resume_path,
            similarity_score=similarity_score,
            status=status
        )
        
        db.session.add(application)
        
        # Update student's resume path
        current_user.student_profile.resume_path = resume_path
        
        db.session.commit()
        
        flash('Application submitted successfully!')
        return redirect(url_for('student.view_job', job_id=job_id))
    
    return render_template('student/apply_job.html', job=job)


@student.route('/applications')
@login_required
@student_required
def view_applications():
    applications = JobApplication.query.filter_by(student_profile_id=current_user.student_profile.id).order_by(JobApplication.application_date.desc()).all()
    tab = request.args.get('tab', 'all')  # Get the tab parameter from the URL, default to 'all'
    return render_template('student/applications.html', applications=applications, active_tab=tab)


@student.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def edit_profile():
    if request.method == 'POST':
        # Update user profile
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.phone = request.form.get('phone')
        
        # Update student profile
        current_user.student_profile.university = request.form.get('university')
        current_user.student_profile.degree = request.form.get('degree')
        current_user.student_profile.graduation_year = request.form.get('graduation_year')
        current_user.student_profile.skills = request.form.get('skills')
        
        db.session.commit()
        
        flash('Profile updated successfully.')
        return redirect(url_for('student.edit_profile'))
    
    return render_template('student/edit_profile.html')


@student.route('/view-resume')
@login_required
@student_required
def view_resume():
    """Serve the current user's resume file"""
    # Get the resume path from student profile
    resume_path = current_user.student_profile.resume_path
    
    # Check if resume exists
    if resume_path and os.path.exists(resume_path):
        return send_file(resume_path, as_attachment=False)
    else:
        flash('Resume file not found.', 'danger')
        return redirect(url_for('student.edit_profile')) 