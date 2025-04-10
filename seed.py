"""
Seed script to populate the database with initial test data.
Run this script after setting up the database to have some data to work with.
"""

import os
import sys
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User, HRProfile, StudentProfile
from app.models.job import Job, JobApplication

def seed_data():
    print("Starting database seeding...")
    
    # Create app context
    app = create_app()
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        JobApplication.query.delete()
        Job.query.delete()
        StudentProfile.query.delete()
        HRProfile.query.delete()
        User.query.delete()
        
        # Create HR users
        print("Creating HR users...")
        hr1 = User(
            email="hr1@example.com",
            username="hr_manager1",
            password="password",
            role="hr",
            first_name="John",
            last_name="Doe",
            phone="123-456-7890"
        )
        
        hr2 = User(
            email="hr2@example.com",
            username="hr_manager2",
            password="password",
            role="hr",
            first_name="Jane",
            last_name="Smith",
            phone="123-456-7891"
        )
        
        # Create HR profiles
        hr1_profile = HRProfile(
            company_name="Tech Innovations Inc.",
            company_website="https://techinnovations.example.com",
            position="HR Manager",
            department="Human Resources"
        )
        
        hr2_profile = HRProfile(
            company_name="Global Solutions Ltd.",
            company_website="https://globalsolutions.example.com",
            position="Talent Acquisition Specialist",
            department="Recruitment"
        )
        
        hr1.hr_profile = hr1_profile
        hr2.hr_profile = hr2_profile
        
        db.session.add_all([hr1, hr2])
        db.session.commit()
        
        # Create jobs
        print("Creating jobs...")
        job1 = Job(
            hr_profile_id=hr1.hr_profile.id,
            title="Python Developer",
            description="""We're looking for a skilled Python Developer to join our team. 
            The ideal candidate should have strong experience with Python, Django, and RESTful APIs. 
            Responsibilities include developing and maintaining web applications, collaborating with 
            cross-functional teams, and writing clean, testable code.""",
            requirements="3+ years of Python experience, Django, RESTful APIs, Git",
            location="San Francisco, CA",
            job_type="Full-time",
            salary_range="$90,000 - $120,000",
            posted_date=datetime.utcnow() - timedelta(days=5),
            closing_date=datetime.utcnow() + timedelta(days=25),
            is_active=True
        )
        
        job2 = Job(
            hr_profile_id=hr1.hr_profile.id,
            title="Data Scientist",
            description="""We are seeking a Data Scientist to join our analytics team. 
            You will work on complex data analysis and machine learning projects. 
            The ideal candidate has strong statistical knowledge, experience with machine learning algorithms, 
            and proficiency in Python and SQL.""",
            requirements="MS/PhD in Computer Science or related field, Python, Machine Learning, SQL",
            location="New York, NY",
            job_type="Full-time",
            salary_range="$100,000 - $140,000",
            posted_date=datetime.utcnow() - timedelta(days=3),
            closing_date=datetime.utcnow() + timedelta(days=27),
            is_active=True
        )
        
        job3 = Job(
            hr_profile_id=hr2.hr_profile.id,
            title="Frontend Developer",
            description="""We're looking for a Frontend Developer with experience in modern JavaScript frameworks. 
            You'll be responsible for building user interfaces, implementing responsive designs, and ensuring 
            cross-browser compatibility.""",
            requirements="React.js, HTML5, CSS3, JavaScript, UI/UX principles",
            location="Remote",
            job_type="Full-time",
            salary_range="$80,000 - $110,000",
            posted_date=datetime.utcnow() - timedelta(days=7),
            closing_date=datetime.utcnow() + timedelta(days=23),
            is_active=True
        )
        
        job4 = Job(
            hr_profile_id=hr2.hr_profile.id,
            title="DevOps Engineer",
            description="""We are looking for a DevOps Engineer to help us build and maintain our cloud infrastructure. 
            You'll work on CI/CD pipelines, infrastructure as code, and ensuring system reliability and performance.""",
            requirements="AWS/Azure, Docker, Kubernetes, CI/CD, Terraform",
            location="Austin, TX",
            job_type="Full-time",
            salary_range="$95,000 - $130,000",
            posted_date=datetime.utcnow() - timedelta(days=2),
            closing_date=datetime.utcnow() + timedelta(days=28),
            is_active=True
        )
        
        job5 = Job(
            hr_profile_id=hr1.hr_profile.id,
            title="Marketing Intern",
            description="""Join our marketing team as an intern to gain hands-on experience in digital marketing. 
            You'll assist with social media campaigns, content creation, and market research.""",
            requirements="Currently pursuing a degree in Marketing or related field, social media experience",
            location="Chicago, IL",
            job_type="Internship",
            salary_range="$20 - $25 per hour",
            posted_date=datetime.utcnow() - timedelta(days=1),
            closing_date=datetime.utcnow() + timedelta(days=14),
            is_active=True
        )
        
        db.session.add_all([job1, job2, job3, job4, job5])
        db.session.commit()
        
        # Create student users
        print("Creating student users...")
        student1 = User(
            email="student1@example.com",
            username="student1",
            password="password",
            role="student",
            first_name="Alex",
            last_name="Johnson",
            phone="123-456-7892"
        )
        
        student2 = User(
            email="student2@example.com",
            username="student2",
            password="password",
            role="student",
            first_name="Sarah",
            last_name="Williams",
            phone="123-456-7893"
        )
        
        # Create student profiles
        student1_profile = StudentProfile(
            university="Stanford University",
            degree="Bachelor of Science in Computer Science",
            graduation_year=2023,
            skills="Python, Java, SQL, Machine Learning, Data Analysis"
        )
        
        student2_profile = StudentProfile(
            university="MIT",
            degree="Master of Science in Computer Science",
            graduation_year=2022,
            skills="JavaScript, React, HTML, CSS, UI/UX Design"
        )
        
        student1.student_profile = student1_profile
        student2.student_profile = student2_profile
        
        db.session.add_all([student1, student2])
        db.session.commit()
        
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_data() 