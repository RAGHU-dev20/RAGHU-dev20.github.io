import os
import logging
import json
from flask import Flask, render_template, request, jsonify, session, url_for, redirect, flash
from werkzeug.utils import secure_filename
import ai_services

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/ats')
def ats():
    return render_template('ats.html')

@app.route('/cat')
def cat():
    return render_template('cat.html')

@app.route('/career')
def career():
    # Get results from session if available
    cat_results = session.get('cat_results', None)
    return render_template('career.html', results=cat_results)

# API endpoints
@app.route('/api/generate-resume', methods=['POST'])
def generate_resume():
    try:
        data = request.json
        result = ai_services.generate_resume(data)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error generating resume: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/evaluate-resume', methods=['POST'])
def evaluate_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text from the resume file (simple implementation)
            resume_text = ""
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                resume_text = f.read()
            
            # Delete the file after reading
            os.remove(filepath)
            
            # Get job description from form data
            job_description = request.form.get('job_description', '')
            
            # Get evaluation from AI service
            evaluation = ai_services.evaluate_resume(resume_text, job_description)
            return jsonify(evaluation)
    except Exception as e:
        logging.error(f"Error evaluating resume: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cat-questions', methods=['GET'])
def get_cat_questions():
    try:
        # Get initial or next questions based on previous answers
        previous_answers = request.args.get('answers', '{}')
        previous_answers = json.loads(previous_answers)
        
        questions = ai_services.generate_cat_questions(previous_answers)
        return jsonify(questions)
    except Exception as e:
        logging.error(f"Error getting CAT questions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cat-results', methods=['POST'])
def get_cat_results():
    try:
        answers = request.json
        results = ai_services.analyze_cat_answers(answers)
        
        # Store results in session for use in the career page
        session['cat_results'] = results
        
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error analyzing CAT results: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/interview-questions', methods=['POST'])
def get_interview_questions():
    try:
        data = request.json
        domain = data.get('domain')
        num_questions = data.get('num_questions', 10)
        questions = ai_services.generate_interview_questions(domain, num_questions)
        return jsonify(questions)
    except Exception as e:
        logging.error(f"Error generating interview questions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/career-roadmap', methods=['POST'])
def get_career_roadmap():
    try:
        data = request.json
        if not data or 'career_path' not in data:
            return jsonify({"error": "Career path is required"}), 400
            
        career_path = data.get('career_path')
        roadmap = ai_services.generate_career_roadmap(career_path)
        
        if not roadmap:
            return jsonify({"error": "Failed to generate roadmap"}), 500
            
        return jsonify(roadmap)
    except Exception as e:
        logging.error(f"Error generating career roadmap: {str(e)}")
        return jsonify({"error": "Failed to generate roadmap. Please try again."}), 500

@app.route('/api/import-profile', methods=['POST'])
def import_profile():
    try:
        data = request.json
        platform = data.get('platform')
        profile_url = data.get('profile_url')
        
        if platform == 'github':
            # Extract username from GitHub URL
            username = profile_url.split('/')[-1]
            
            # Make request to GitHub API
            import requests
            github_api_url = f'https://api.github.com/users/{username}'
            response = requests.get(github_api_url)
            
            if response.status_code == 200:
                profile_data = response.json()
                return jsonify({
                    "success": True,
                    "profile": {
                        "name": profile_data.get('name'),
                        "bio": profile_data.get('bio'),
                        "location": profile_data.get('location'),
                        "public_repos": profile_data.get('public_repos'),
                        "followers": profile_data.get('followers'),
                        "following": profile_data.get('following'),
                        "avatar_url": profile_data.get('avatar_url')
                    }
                })
            else:
                return jsonify({"error": "Failed to fetch GitHub profile"}), 400
                
        return jsonify({"error": "Platform not supported yet"}), 400
    except Exception as e:
        logging.error(f"Error importing profile: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    try:
        career_data = request.json
        suggestions = ai_services.generate_suggestions(career_data)
        return jsonify(suggestions)
    except Exception as e:
        logging.error(f"Error generating suggestions: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
