from app import db
from datetime import datetime

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    hr_profile_id = db.Column(db.Integer, db.ForeignKey('hr_profiles.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(128))
    job_type = db.Column(db.String(64))  # full-time, part-time, internship, etc.
    salary_range = db.Column(db.String(64))
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    closing_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    applications = db.relationship('JobApplication', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Job {self.title}>'


class JobApplication(db.Model):
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    student_profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    resume_path = db.Column(db.String(256), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    similarity_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, shortlisted, rejected
    email_sent = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<JobApplication {self.id}>'
    
    @property
    def is_shortlisted(self):
        return self.similarity_score is not None and self.similarity_score >= 70 and self.status == 'shortlisted' 