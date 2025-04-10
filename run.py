from app import create_app, db
from app.models.user import User, HRProfile, StudentProfile
from app.models.job import Job, JobApplication

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'HRProfile': HRProfile, 
        'StudentProfile': StudentProfile,
        'Job': Job,
        'JobApplication': JobApplication
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 