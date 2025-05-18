import os
import json
import logging
import time
import re
from typing import Dict, List, Any
import math

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Helper function to handle OpenAI API calls with retries and error handling
def safe_openai_call(func, *args, max_retries=3, **kwargs):
    """Safely call OpenAI API with retries and error handling"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"OpenAI API call failed (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s, etc.
                time.sleep(2 ** attempt)
                continue
            # If we've exhausted retries, log the error and return None
            logging.error(f"OpenAI API call failed after {max_retries} attempts: {str(e)}")
            return None

def score_keyword_match(text: str, keywords: List[str]) -> float:
    """Calculate keyword match score"""
    text = text.lower()
    matches = sum(1 for keyword in keywords if keyword.lower() in text)
    return min(10, (matches / len(keywords)) * 10)

def generate_resume(user_data: Dict[str, str]) -> Dict[str, Any]:
    """Generate formatted resume with basic scoring"""
    # Format skills as a list
    skills_list = user_data.get('skills', '').split(',') if ',' in user_data.get('skills', '') else user_data.get('skills', '').split('\n')
    skills_list = [skill.strip() for skill in skills_list if skill.strip()]
    skills_html = ''.join([f'<li>{skill}</li>' for skill in skills_list])

    # Format education into paragraphs
    education_paragraphs = user_data.get('education', '').split('\n')
    education_html = ''.join([f'<p>{edu.strip()}</p>' for edu in education_paragraphs if edu.strip()])

    # Format experience into paragraphs
    experience_paragraphs = user_data.get('experience', '').split('\n')
    experience_html = ''.join([f'<p>{exp.strip()}</p>' for exp in experience_paragraphs if exp.strip()])

    # Create HTML content
    html_content = f"""
    <div class="resume">
        <div class="resume-header">
            <h1>{user_data.get('name', '')}</h1>
            <p>{user_data.get('email', '')} | {user_data.get('phone', '')} | {user_data.get('location', '')}</p>
        </div>

        <div class="resume-section">
            <h2>Professional Summary</h2>
            <p>{user_data.get('summary', '')}</p>
        </div>

        <div class="resume-section">
            <h2>Education</h2>
            {education_html}
        </div>

        <div class="resume-section">
            <h2>Experience</h2>
            {experience_html}
        </div>

        <div class="resume-section">
            <h2>Skills</h2>
            <ul>
                {skills_html}
            </ul>
        </div>
    </div>
    """

    # Calculate basic keyword score
    content = f"{user_data.get('summary', '')} {user_data.get('experience', '')} {user_data.get('skills', '')}"
    common_keywords = ['experienced', 'skilled', 'professional', 'developed', 'managed', 'led', 'created', 'implemented']
    keyword_score = score_keyword_match(content, common_keywords)

    return {
        "html_content": html_content,
        "keyword_score": keyword_score,
        "improvement_tips": [
            "Use action verbs to describe your experiences",
            "Quantify achievements with numbers when possible",
            "Include relevant industry keywords",
            "Keep formatting consistent",
            "Proofread for errors"
        ]
    }

def evaluate_resume(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Evaluate resume against job description"""
    # Extract keywords from job description
    job_keywords = set(re.findall(r'\b\w+\b', job_description.lower()))
    resume_keywords = set(re.findall(r'\b\w+\b', resume_text.lower()))

    # Calculate keyword match
    matching_keywords = job_keywords.intersection(resume_keywords)
    keyword_score = len(matching_keywords) / len(job_keywords) * 10 if job_keywords else 5

    # Check for common sections
    sections = ['education', 'experience', 'skills', 'summary', 'objective']
    missing_sections = [section for section in sections if section not in resume_text.lower()]

    # Calculate formatting score
    formatting_score = 10
    formatting_issues = []

    if len(resume_text.split('\n\n')) < 3:
        formatting_score -= 2
        formatting_issues.append("Improve section spacing")

    if len(re.findall(r'[A-Z]{2,}', resume_text)) < 2:
        formatting_score -= 2
        formatting_issues.append("Use clear section headers")

    return {
        "ats_score": round(min(10, (keyword_score + formatting_score) / 2), 1),
        "missing_elements": missing_sections or ["No major sections missing"],
        "improvement_suggestions": [
            "Add more keywords from the job description",
            "Use standard section headers",
            "Include quantifiable achievements",
            "Keep formatting consistent",
            "Use bullet points for better readability"
        ],
        "formatting_issues": formatting_issues,
        "strengths": [
            f"Found {len(matching_keywords)} matching keywords",
            "Basic sections present" if not missing_sections else "Sections need improvement",
            "Good formatting" if formatting_score > 7 else "Format needs improvement"
        ]
    }

def analyze_cat_answers(answers: Dict[str, str]) -> Dict[str, Any]:
    """Analyze career test answers and provide recommendations"""
    # Define career domains and their keywords
    domains = {
        "Technology": ["programming", "computer", "software", "technical", "coding", "data"],
        "Business": ["management", "business", "leadership", "strategy", "marketing"],
        "Creative": ["design", "art", "creative", "visual", "content"],
        "Healthcare": ["medical", "health", "care", "patient", "clinical"],
        "Education": ["teaching", "education", "training", "learning", "instructor"]
    }

    # Calculate domain scores
    domain_scores = {}
    for domain, keywords in domains.items():
        score = 0
        for answer in answers.values():
            if isinstance(answer, str):
                score += score_keyword_match(answer, keywords)
        domain_scores[domain] = min(95, max(40, score))

    # Sort domains by score
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)

    # Generate career recommendations
    recommendations = []
    for domain, score in sorted_domains[:3]:
        if domain == "Technology" and score > 60:
            recommendations.append({
                "title": "Software Developer",
                "description": "Develop and maintain software applications",
                "match_percentage": score
            })
        elif domain == "Business" and score > 60:
            recommendations.append({
                "title": "Business Analyst",
                "description": "Analyze business processes and recommend improvements",
                "match_percentage": score
            })
        elif domain == "Creative" and score > 60:
            recommendations.append({
                "title": "UX Designer",
                "description": "Design user-friendly digital experiences",
                "match_percentage": score
            })

    return {
        "recommended_careers": recommendations,
        "strengths": [
            "Technical aptitude" if domain_scores["Technology"] > 70 else None,
            "Business acumen" if domain_scores["Business"] > 70 else None,
            "Creative thinking" if domain_scores["Creative"] > 70 else None
        ],
        "development_areas": [
            "Technical skills" if domain_scores["Technology"] < 60 else None,
            "Business knowledge" if domain_scores["Business"] < 60 else None,
            "Creative abilities" if domain_scores["Creative"] < 60 else None
        ],
        "domain_matches": [{"domain": k, "percentage": v} for k, v in sorted_domains]
    }

def generate_cat_questions(previous_answers=None):
    """Generate Career Assistance Test questions based on previous answers"""
    try:
        if not previous_answers:
            # Initial questions
            return {
                "questions": [
                    {
                        "id": "interests",
                        "type": "text",
                        "question": "What activities or subjects do you find most engaging and enjoyable?"
                    },
                    {
                        "id": "strengths",
                        "type": "text",
                        "question": "What skills or abilities do others compliment you on?"
                    },
                    {
                        "id": "values",
                        "type": "multiselect",
                        "question": "Which of these work values are most important to you?",
                        "options": [
                            "Work-life balance",
                            "High income potential",
                            "Helping others",
                            "Creative expression",
                            "Intellectual challenge",
                            "Leadership opportunities",
                            "Job security",
                            "Recognition",
                            "Independence"
                        ]
                    }
                ],
                "progress": 30
            }
        else:
            # Generate follow-up questions based on previous answers
            prompt = f"""
            Based on these previous CAT (Career Assistance Test) answers:
            {json.dumps(previous_answers, indent=2)}
            
            Generate the next set of personalized questions to help determine suitable career paths.
            The questions should be adapted based on the user's previous responses and explore deeper
            into their interests, skills, and preferences.
            
            Return the response as JSON with the following structure:
            {{
                "questions": [
                    {{
                        "id": "unique_question_id",
                        "type": "text|multiselect|scale",
                        "question": "The question text",
                        "options": ["Option 1", "Option 2"] // only for multiselect questions
                    }}
                ],
                "progress": 60 // percentage of test completion
            }}
            """
            
            # Use safe OpenAI call with retries
            response = safe_openai_call(
                openai.chat.completions.create,
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a career counseling expert creating a dynamic career assessment test."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            if response and response.choices and response.choices[0].message.content:
                result = json.loads(response.choices[0].message.content)
                return result
            else:
                # Fallback to template-based questions if OpenAI API fails
                return generate_template_questions(previous_answers)
    
    except Exception as e:
        logging.error(f"Error in generate_cat_questions: {str(e)}")
        # Use fallback template instead of raising exception
        return generate_template_questions(previous_answers)

def generate_template_questions(previous_answers=None):
    """Fallback function to generate basic career test questions without using OpenAI API"""
    if not previous_answers:
        # This should never happen since the non-API initial questions are already handled
        return {
            "questions": [
                {
                    "id": "interests",
                    "type": "text",
                    "question": "What activities or subjects do you find most engaging and enjoyable?"
                },
                {
                    "id": "strengths",
                    "type": "text",
                    "question": "What skills or abilities do others compliment you on?"
                },
                {
                    "id": "values",
                    "type": "multiselect",
                    "question": "Which of these work values are most important to you?",
                    "options": [
                        "Work-life balance",
                        "High income potential",
                        "Helping others",
                        "Creative expression",
                        "Intellectual challenge",
                        "Leadership opportunities",
                        "Job security",
                        "Recognition",
                        "Independence"
                    ]
                }
            ],
            "progress": 30
        }
    
    # Check what stage of the test we're in based on the previous answers
    if "interests" in previous_answers and "education_background" not in previous_answers:
        # Second set of questions
        return {
            "questions": [
                {
                    "id": "education_background",
                    "type": "text",
                    "question": "What is your educational background? (degree, major, certifications, etc.)"
                },
                {
                    "id": "work_experience",
                    "type": "text",
                    "question": "What work experience do you have? Describe any jobs, internships, or volunteer work."
                },
                {
                    "id": "preferred_environment",
                    "type": "multiselect",
                    "question": "What type of work environment do you prefer?",
                    "options": [
                        "Office setting",
                        "Remote work",
                        "Hybrid",
                        "Outdoors",
                        "Fast-paced",
                        "Structured",
                        "Flexible",
                        "Collaborative",
                        "Independent"
                    ]
                }
            ],
            "progress": 60
        }
    else:
        # Final set of questions
        return {
            "questions": [
                {
                    "id": "tech_comfort",
                    "type": "scale",
                    "question": "How comfortable are you with technology? (1 = Not comfortable, 5 = Very comfortable)"
                },
                {
                    "id": "career_goals",
                    "type": "text",
                    "question": "What are your long-term career goals or aspirations?"
                },
                {
                    "id": "challenges",
                    "type": "text",
                    "question": "What challenges or obstacles do you face in your career development?"
                }
            ],
            "progress": 90
        }

def generate_interview_questions(domain, num_questions=10):
    """Generate interview questions based on the chosen domain"""
    try:
        prompt = f"""
        Generate {num_questions} interview questions for a {domain} position.
        Include both technical and behavioral questions.
        Return as JSON with the following structure:
        {{
            "technical_questions": [
                {{ "question": "question text", "ideal_answer": "ideal answer text" }}
            ],
            "behavioral_questions": [
                {{ "question": "question text", "tips": "interview tips" }}
            ]
        }}
        """
        
        openai = OpenAI(api_key=OPENAI_API_KEY)

        response = safe_openai_call(
            openai.chat.completions.create,
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        if response and response.choices and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)
        return generate_template_questions(domain)
    except Exception as e:
        logging.error(f"Error generating interview questions: {str(e)}")
        return generate_template_questions(domain)

def generate_career_roadmap(career_path):
    """Generate a career roadmap with milestones"""
    try:
        prompt = f"""
        Generate a detailed career roadmap for a {career_path} career path.
        Include milestones, skills to acquire, and estimated timeframes.
        Return as JSON with the following structure:
        {{
            "entry_level": {{
                "title": "role title",
                "skills": ["required skills"],
                "timeframe": "estimated time",
                "milestones": ["key milestones"]
            }},
            "mid_level": {{
                "title": "role title",
                "skills": ["required skills"],
                "timeframe": "estimated time",
                "milestones": ["key milestones"]
            }},
            "senior_level": {{
                "title": "role title",
                "skills": ["required skills"],
                "timeframe": "estimated time",
                "milestones": ["key milestones"]
            }}
        }}
        """
        openai = OpenAI(api_key=OPENAI_API_KEY)

        response = safe_openai_call(
            openai.chat.completions.create,
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert career counselor."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        if response and response.choices and response.choices[0].message.content:
            return json.loads(response.choices[0].message.content)
        return generate_template_roadmap(career_path)
    except Exception as e:
        logging.error(f"Error generating career roadmap: {str(e)}")
        return generate_template_roadmap(career_path)

def generate_template_roadmap(career_path):
    """Template for generating career roadmap"""
    return {
        "entry_level": {
            "title": "Entry Level Role",
            "skills": ["Skill 1", "Skill 2"],
            "timeframe": "0-2 years",
            "milestones": ["Milestone 1", "Milestone 2"]
        },
        "mid_level": {
            "title": "Mid Level Role",
            "skills": ["Skill 3", "Skill 4"],
            "timeframe": "3-5 years",
            "milestones": ["Milestone 3", "Milestone 4"]
        },
        "senior_level": {
            "title": "Senior Level Role",
            "skills": ["Skill 5", "Skill 6"],
            "timeframe": "5+ years",
            "milestones": ["Milestone 5", "Milestone 6"]
        }
    }

def generate_suggestions(career_data):
    """Generate actionable career suggestions based on career data"""
    try:
        prompt = f"""
        Based on the user's career assessment results:
        
        {json.dumps(career_data, indent=2)}
        
        Provide actionable career development suggestions including:
        1. Job descriptions for recommended roles
        2. Relevant certifications or courses to pursue
        3. Companies known to hire in these domains
        4. Learning resources and paths
        5. Industry insights for the recommended career paths
        
        Return the response as JSON with the following structure:
        {{
            "job_descriptions": [
                {{ "title": "Job Title", "description": "Detailed description", "requirements": ["req1", "req2"] }}
            ],
            "certifications": [
                {{ "name": "Certification Name", "provider": "Provider", "description": "Description", "difficulty": "Beginner|Intermediate|Advanced" }}
            ],
            "companies": [
                {{ "name": "Company Name", "industry": "Industry", "why_good_fit": "Explanation" }}
            ],
            "learning_resources": [
                {{ "name": "Resource Name", "type": "Book|Course|Website", "link": "URL if applicable", "description": "Description" }}
            ],
            "industry_insights": ["List of key industry insights"]
        }}
        """
        openai = OpenAI(api_key=OPENAI_API_KEY)

        # Use safe OpenAI call with retries
        response = safe_openai_call(
            openai.chat.completions.create,
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a career development expert providing actionable suggestions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        if response and response.choices and response.choices[0].message and response.choices[0].message.content:
            result = json.loads(response.choices[0].message.content)
            return result
        else:
            # Fallback to template-based suggestions if OpenAI API fails
            return generate_template_suggestions(career_data)
    
    except Exception as e:
        logging.error(f"Error in generate_suggestions: {str(e)}")
        # Use fallback template instead of raising exception
        return generate_template_suggestions(career_data)

def generate_template_suggestions(career_data):
    """Fallback function to generate basic career suggestions without using OpenAI API"""
    # Extract recommended careers from the input data
    recommended_careers = career_data.get("recommended_careers", [])
    career_titles = [career.get("title", "") for career in recommended_careers]
    
    # Default job descriptions
    job_descriptions = [
        {
            "title": "Software Developer",
            "description": "Software developers design, build, and maintain computer programs and applications. They work in various industries, solving problems and creating solutions through code.",
            "requirements": [
                "Proficiency in programming languages like Python, JavaScript, or Java",
                "Understanding of software development principles",
                "Problem-solving abilities",
                "Bachelor's degree in Computer Science or related field (or equivalent experience)",
                "Experience with version control systems like Git"
            ]
        },
        {
            "title": "Data Analyst",
            "description": "Data analysts collect, process, and analyze data to help organizations make better decisions. They transform raw data into insights that drive business strategy.",
            "requirements": [
                "Proficiency with data analysis tools (Excel, SQL, Python or R)",
                "Experience with data visualization tools like Tableau or Power BI",
                "Strong analytical and critical thinking skills",
                "Bachelor's degree in analytics, statistics, mathematics, or related field",
                "Communication skills to present findings clearly"
            ]
        },
        {
            "title": "Project Manager",
            "description": "Project managers plan, execute, and close projects, ensuring they are completed on time, within budget, and according to specifications. They coordinate team members and resources to achieve project goals.",
            "requirements": [
                "Strong organizational and planning skills",
                "Leadership and team management abilities",
                "Communication and negotiation skills",
                "Experience with project management methodologies (Agile, Scrum, etc.)",
                "Problem-solving capabilities to address issues that arise"
            ]
        },
        {
            "title": "UX/UI Designer",
            "description": "UX/UI designers create user-friendly and aesthetically pleasing digital experiences. They combine design principles with user research to develop interfaces that are both beautiful and functional.",
            "requirements": [
                "Proficiency with design tools like Figma, Adobe XD, or Sketch",
                "Understanding of user-centered design principles",
                "Knowledge of interface design patterns and best practices",
                "Portfolio demonstrating UI/UX projects",
                "Ability to incorporate user feedback into designs"
            ]
        }
    ]
    
    # Filter job descriptions based on recommended careers
    filtered_jobs = []
    for job in job_descriptions:
        if any(career.lower() in job["title"].lower() for career in career_titles) or len(filtered_jobs) < 2:
            filtered_jobs.append(job)
    
    # Add at least 3 jobs
    while len(filtered_jobs) < 3:
        for job in job_descriptions:
            if job not in filtered_jobs:
                filtered_jobs.append(job)
                break
    
    # Default certifications
    certifications = [
        {
            "name": "Project Management Professional (PMP)",
            "provider": "Project Management Institute",
            "description": "A globally recognized certification for project management professionals that validates expertise in leading and directing projects.",
            "difficulty": "Advanced"
        },
        {
            "name": "Google Data Analytics Certificate",
            "provider": "Google",
            "description": "A comprehensive program that covers the entire data analysis process, from collecting and processing data to analyzing and sharing insights.",
            "difficulty": "Beginner"
        },
        {
            "name": "AWS Certified Solutions Architect",
            "provider": "Amazon Web Services",
            "description": "Validates technical expertise in designing and deploying scalable systems on AWS, a leading cloud platform.",
            "difficulty": "Intermediate"
        },
        {
            "name": "Certified ScrumMaster (CSM)",
            "provider": "Scrum Alliance",
            "description": "Demonstrates knowledge of Scrum principles and the ability to facilitate a Scrum team in implementing these methodologies.",
            "difficulty": "Beginner"
        },
        {
            "name": "Google UX Design Certificate",
            "provider": "Google",
            "description": "A comprehensive program that covers the fundamentals of UX design, including research, wireframing, prototyping, and testing.",
            "difficulty": "Beginner"
        }
    ]
    
    # Default companies
    companies = [
        {
            "name": "Google",
            "industry": "Technology",
            "why_good_fit": "Known for innovative work environment, strong career development, and impactful projects across many domains."
        },
        {
            "name": "Microsoft",
            "industry": "Technology",
            "why_good_fit": "Offers diverse roles in software, cloud services, and business applications with opportunities for professional growth."
        },
        {
            "name": "IBM",
            "industry": "Technology & Consulting",
            "why_good_fit": "Combines technology innovation with business consulting, offering a variety of career paths in AI, cloud, and digital transformation."
        },
        {
            "name": "Accenture",
            "industry": "Consulting",
            "why_good_fit": "Global professional services company providing opportunities in strategy, consulting, technology, and operations across industries."
        },
        {
            "name": "Adobe",
            "industry": "Software & Design",
            "why_good_fit": "Ideal for creative and technical professionals with interest in design, digital media, and creative software solutions."
        }
    ]
    
    # Default learning resources
    learning_resources = [
        {
            "name": "Coursera",
            "type": "Website",
            "link": "https://www.coursera.org/",
            "description": "Online platform offering courses, specializations, and degrees from universities and companies across various disciplines."
        },
        {
            "name": "LinkedIn Learning",
            "type": "Website",
            "link": "https://www.linkedin.com/learning/",
            "description": "Professional development platform with courses on business, creative, and technology skills."
        },
        {
            "name": "Atomic Habits",
            "type": "Book",
            "link": "https://jamesclear.com/atomic-habits",
            "description": "Guide to building good habits and breaking bad ones, essential for professional development and career growth."
        },
        {
            "name": "edX",
            "type": "Website",
            "link": "https://www.edx.org/",
            "description": "Platform offering courses from top universities and institutions, with options for certificates and degrees."
        },
        {
            "name": "Udemy",
            "type": "Website",
            "link": "https://www.udemy.com/",
            "description": "Marketplace for online learning with a vast library of courses on professional and personal development topics."
        }
    ]
    
    # Industry insights relevant to common career paths
    industry_insights = [
        "Remote and hybrid work models are becoming standard across most industries",
        "AI and automation are transforming roles across sectors, requiring professionals to adapt",
        "Soft skills like communication and adaptability are increasingly valued alongside technical abilities",
        "Continuous learning and upskilling are essential in today's rapidly changing job market",
        "Cross-functional collaboration is becoming more important as projects span multiple disciplines",
        "Data literacy is becoming a fundamental skill across virtually all professional roles",
        "Companies are increasingly valuing diversity, equity, and inclusion in their hiring practices"
    ]
    
    # Return template-based suggestions
    return {
        "job_descriptions": filtered_jobs[:4],  # Limit to 4 job descriptions
        "certifications": certifications[:5],   # Limit to 5 certifications
        "companies": companies[:5],             # Limit to 5 companies
        "learning_resources": learning_resources[:5],  # Limit to 5 resources
        "industry_insights": industry_insights
    }