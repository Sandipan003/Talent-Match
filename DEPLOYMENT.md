# Deployment Guide

This document provides instructions for deploying the Resume Screening Application to various platforms.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git
- A deployment platform (Heroku, AWS, Azure, etc.)

## Local Deployment

1. Clone the repository:
   ```
   git clone <repository-url>
   cd resume-screening-app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add the following environment variables:
   ```
   SECRET_KEY=your_secret_key
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_email_password
   MAIL_DEFAULT_SENDER=your_email@example.com
   ```

5. Initialize the database:
   ```
   python
   >>> from app import create_app, db
   >>> app = create_app()
   >>> with app.app_context():
   >>>     db.create_all()
   >>> exit()
   ```

6. (Optional) Seed the database with sample data:
   ```
   python seed.py
   ```

7. Run the application:
   ```
   python run.py
   ```

## Heroku Deployment

1. Create a Heroku account and install the Heroku CLI

2. Login to Heroku:
   ```
   heroku login
   ```

3. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```

4. Add a PostgreSQL add-on:
   ```
   heroku addons:create heroku-postgresql:hobby-dev
   ```

5. Set environment variables:
   ```
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set MAIL_USERNAME=your_email@example.com
   heroku config:set MAIL_PASSWORD=your_email_password
   heroku config:set MAIL_DEFAULT_SENDER=your_email@example.com
   ```

6. Create a `Procfile` in the root directory with the following content:
   ```
   web: gunicorn 'app:create_app()'
   ```

7. Deploy the application:
   ```
   git push heroku main
   ```

8. Initialize the database:
   ```
   heroku run python
   >>> from app import create_app, db
   >>> app = create_app()
   >>> with app.app_context():
   >>>     db.create_all()
   >>> exit()
   ```

9. (Optional) Seed the database:
   ```
   heroku run python seed.py
   ```

## AWS Elastic Beanstalk Deployment

1. Install the AWS CLI and EB CLI

2. Initialize EB CLI repository:
   ```
   eb init -p python-3.7 resume-screening-app
   ```

3. Create a `.ebextensions` directory in the root of your project and add a configuration file `01_flask.config`:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:application:environment:
       SECRET_KEY: your_secret_key
       MAIL_USERNAME: your_email@example.com
       MAIL_PASSWORD: your_email_password
       MAIL_DEFAULT_SENDER: your_email@example.com
     aws:elasticbeanstalk:container:python:
       WSGIPath: app:create_app()
   ```

4. Create an Elastic Beanstalk environment:
   ```
   eb create resume-screening-env
   ```

5. Deploy the application:
   ```
   eb deploy
   ```

6. SSH into the instance to initialize and seed the database:
   ```
   eb ssh
   cd /var/app/current
   python
   >>> from app import create_app, db
   >>> app = create_app()
   >>> with app.app_context():
   >>>     db.create_all()
   >>> exit()
   python seed.py
   ```

## Docker Deployment

1. Create a `Dockerfile` in the root directory:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   ENV FLASK_APP=run.py
   ENV FLASK_ENV=production
   
   CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:create_app()"]
   ```

2. Build the Docker image:
   ```
   docker build -t resume-screening-app .
   ```

3. Run the Docker container:
   ```
   docker run -d -p 5000:5000 \
     -e SECRET_KEY=your_secret_key \
     -e MAIL_USERNAME=your_email@example.com \
     -e MAIL_PASSWORD=your_email_password \
     -e MAIL_DEFAULT_SENDER=your_email@example.com \
     resume-screening-app
   ```

4. Initialize and seed the database:
   ```
   docker exec -it <container_id> python
   >>> from app import create_app, db
   >>> app = create_app()
   >>> with app.app_context():
   >>>     db.create_all()
   >>> exit()
   docker exec -it <container_id> python seed.py
   ```

## Notes

- For production deployments, use a more robust database like PostgreSQL instead of SQLite
- Consider using a dedicated file storage service (e.g., AWS S3) for storing resumes in production
- Set up proper email service integration for production (e.g., SendGrid, Mailgun)
- Configure proper logging and monitoring
- Set up regular database backups 