# AI Resume Screening Application

A smart job application platform that uses AI to match candidates with job postings based on their resume and job requirements. The system automatically calculates a similarity score to help HR professionals identify the best candidates.

## Features

### For HR Professionals
- Create company profile and post job listings
- View and manage applications
- Auto-screening of candidates with AI-powered matching
- Shortlist candidates based on resume match score
- Send email notifications to shortlisted candidates

### For Students/Job Seekers
- Create profile and upload resume
- Browse available job postings
- Apply to positions with one click
- Track application status
- View match scores for applications

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **Frontend**: Bootstrap, HTML, CSS, JavaScript
- **AI/ML**: NLTK, scikit-learn for NLP and resume analysis
- **Authentication**: Flask-Login
- **Email**: Flask-Mail

## Prerequisites

- Python 3.8 or higher
- Pip (Python package manager)
- Microsoft C++ Build Tools (for scikit-learn, required on Windows)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Sandipan003/Talent-Match.git
   cd Talent-Match
   ```

2. Create and activate a virtual environment:
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download required NLTK data:
   ```
   python download_nltk.py
   ```

## Environment Variables (Optional)

Create a `.env` file in the root directory to customize settings:

```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///resume_screening.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## Running the Application

1. Initialize the database:
   ```
   python seed.py
   ```

2. Start the application:
   ```
   python run.py
   ```

3. Access the application at `http://localhost:5000`

## Default Accounts

After running the seed script, the following accounts are available for testing:

### HR Account
- Email: hr@example.com
- Password: password

### Student Account
- Email: student@example.com
- Password: password

## Usage Guide

### For HR Users

1. Login with HR credentials
2. Create or update your company profile
3. Post job listings with detailed requirements
4. View applications for your job postings
5. Review automatically calculated match scores
6. Shortlist candidates with high match scores
7. Send email notifications to shortlisted candidates

### For Student Users

1. Login with student credentials
2. Complete your profile and upload your resume
3. Browse available job listings
4. Apply to jobs that match your skills
5. Track the status of your applications
6. Receive notifications when shortlisted

## Troubleshooting

### Common issues:

1. **NLTK Data Download Issues**: If NLTK data download fails, manually download the required packages:
   ```python
   import nltk
   import ssl
   try:
       _create_unverified_https_context = ssl._create_unverified_context
   except AttributeError:
       pass
   else:
       ssl._create_default_https_context = _create_unverified_https_context
   nltk.download('punkt')
   nltk.download('stopwords')
   nltk.download('wordnet')
   ```

2. **scikit-learn Installation Issues on Windows**: Install the Microsoft C++ Build Tools:
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Or use a pre-built wheel: `pip install --only-binary=:all: scikit-learn`

3. **Database Issues**: If you encounter database errors, delete the existing database file and reinitialize:
   ```
   rm instance/resume_screening.db
   python seed.py
   ```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
