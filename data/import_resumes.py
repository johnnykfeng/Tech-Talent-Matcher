import os
import json
import logging
import random
from datetime import datetime
from app import db
from models import Candidate, Education, Experience, Skill, candidate_skills

# List of profile image URLs to choose from
PROFILE_IMAGES = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330",
    "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2",
    "https://images.unsplash.com/photo-1546456073-92b9f0a8d413",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9",
    "https://images.unsplash.com/photo-1603415526960-f7e0328c63b1",
    "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde",
    "https://images.unsplash.com/photo-1570295999919-56ceb5ecca61",
    "https://images.unsplash.com/photo-1542103749-8ef59b94f47e",
    "https://images.unsplash.com/photo-1546593064-053d21199be1",
    "https://images.unsplash.com/photo-1551069613-1904dbdcda11",
]

def import_resumes(db):
    """
    Import candidate resumes from JSON files in the data/Resumes_JSON directory
    """
    logging.info("Importing candidate resumes from JSON files")
    
    # Path to the resumes directory
    resumes_dir = "data/Resumes_JSON"
    
    # Check if directory exists
    if not os.path.exists(resumes_dir):
        logging.error(f"Directory {resumes_dir} not found")
        return
    
    # Get all JSON files in the directory
    resume_files = [f for f in os.listdir(resumes_dir) if f.endswith('.json')]
    
    # Track added candidates and skills
    added_candidates = 0
    added_skills = 0
    
    for resume_file in resume_files:
        try:
            # Read the JSON file
            with open(os.path.join(resumes_dir, resume_file), 'r') as f:
                resume_data = json.load(f)
            
            # Extract basic candidate info
            name = resume_data.get('name')
            job_title = resume_data.get('job_title')
            location = resume_data.get('location')
            summary = resume_data.get('summary')
            
            # Skip if essential data is missing
            if not all([name, job_title, location]):
                logging.warning(f"Skipping {resume_file}: Missing essential data")
                continue
            
            # Get a random profile image
            profile_image = random.choice(PROFILE_IMAGES)
            
            # Create candidate
            candidate = Candidate(
                name=name,
                title=job_title,
                location=location,
                profile_image=profile_image,
                bio=summary
            )
            
            # Add education
            for edu in resume_data.get('education', []):
                institution = edu.get('institution')
                degree = edu.get('degree')
                field = edu.get('field')
                
                if institution and degree:
                    # Extract the graduation year if available
                    grad_date = edu.get('graduation_date')
                    year = None
                    if grad_date:
                        try:
                            year = int(grad_date)
                        except ValueError:
                            # Try extracting year from a date string
                            if len(grad_date) == 4 and grad_date.isdigit():
                                year = int(grad_date)
                    
                    education = Education(
                        degree=degree,
                        field=field or "Not specified",
                        institution=institution,
                        location=location,  # Using candidate location as fallback
                        year=year
                    )
                    candidate.educations.append(education)
            
            # Add experience
            for exp in resume_data.get('experience', []):
                company = exp.get('company')
                position = exp.get('position')
                duration = exp.get('duration')
                description_list = exp.get('description', [])
                
                if company and position:
                    # Parse duration to get start and end dates
                    start_date = None
                    end_date = None
                    is_current = False
                    
                    if duration:
                        try:
                            # Format expected: "Jan 2021 - Present" or "May 2016 - Dec 2020"
                            # or "June 2019 - Present" or "January 2016 - December 2020"
                            parts = duration.split(' - ')
                            
                            if len(parts) >= 2:
                                # Parse start date
                                start_part = parts[0].strip()
                                
                                # Month mapping for more robust parsing
                                month_mapping = {
                                    'january': 1, 'jan': 1,
                                    'february': 2, 'feb': 2,
                                    'march': 3, 'mar': 3,
                                    'april': 4, 'apr': 4,
                                    'may': 5,
                                    'june': 6, 'jun': 6,
                                    'july': 7, 'jul': 7,
                                    'august': 8, 'aug': 8,
                                    'september': 9, 'sep': 9, 'sept': 9,
                                    'october': 10, 'oct': 10,
                                    'november': 11, 'nov': 11,
                                    'december': 12, 'dec': 12
                                }
                                
                                # Custom date parsing logic
                                start_parts = start_part.lower().split()
                                if len(start_parts) == 2:
                                    month_str = start_parts[0]
                                    year_str = start_parts[1]
                                    
                                    if month_str in month_mapping and year_str.isdigit() and len(year_str) == 4:
                                        month_num = month_mapping[month_str]
                                        year_num = int(year_str)
                                        start_date = datetime(year_num, month_num, 1)
                                    else:
                                        # Fall back to default date
                                        logging.warning(f"Could not parse month/year in start date: {start_part}")
                                        start_date = datetime(2020, 1, 1)
                                else:
                                    # Fall back to default date
                                    logging.warning(f"Unexpected format for start date: {start_part}")
                                    start_date = datetime(2020, 1, 1)
                                
                                # Parse end date
                                end_part = parts[1].strip()
                                
                                if end_part.lower() == 'present':
                                    is_current = True
                                    end_date = None
                                else:
                                    # Apply same custom parsing for end date
                                    end_parts = end_part.lower().split()
                                    if len(end_parts) == 2:
                                        month_str = end_parts[0]
                                        year_str = end_parts[1]
                                        
                                        if month_str in month_mapping and year_str.isdigit() and len(year_str) == 4:
                                            month_num = month_mapping[month_str]
                                            year_num = int(year_str)
                                            # Use last day of month for end dates
                                            if month_num in [4, 6, 9, 11]:  # 30-day months
                                                end_date = datetime(year_num, month_num, 30)
                                            elif month_num == 2:  # February
                                                if (year_num % 4 == 0 and year_num % 100 != 0) or (year_num % 400 == 0):
                                                    end_date = datetime(year_num, month_num, 29)  # Leap year
                                                else:
                                                    end_date = datetime(year_num, month_num, 28)
                                            else:  # 31-day months
                                                end_date = datetime(year_num, month_num, 31)
                                        else:
                                            logging.warning(f"Could not parse month/year in end date: {end_part}")
                                            end_date = None
                                    else:
                                        logging.warning(f"Unexpected format for end date: {end_part}")
                                        end_date = None
                        except Exception as e:
                            logging.warning(f"Error parsing duration '{duration}': {e}")
                            start_date = datetime(2020, 1, 1)
                            end_date = None
                            is_current = True
                    
                    # Combine description list into a single text
                    description = "\n".join(description_list) if description_list else ""
                    
                    experience = Experience(
                        role=position,
                        company=company,
                        location=location,  # Using candidate location as fallback
                        description=description,
                        start_date=start_date,
                        end_date=end_date,
                        is_current=is_current
                    )
                    candidate.experiences.append(experience)
            
            # Add skills
            for skill_name in resume_data.get('skills', []):
                # Check if the skill already exists
                skill = Skill.query.filter_by(name=skill_name).first()
                
                # Create skill if it doesn't exist
                if not skill:
                    # Determine a category based on keywords in the skill name
                    category = "Technical"
                    
                    if any(kw in skill_name.lower() for kw in ["management", "leadership", "team", "communication"]):
                        category = "Soft Skills"
                    elif any(kw in skill_name.lower() for kw in ["marketing", "seo", "content", "social media"]):
                        category = "Marketing"
                    elif any(kw in skill_name.lower() for kw in ["data", "analytics", "analysis", "statistics"]):
                        category = "Data Analysis"
                    elif any(kw in skill_name.lower() for kw in ["programming", "java", "python", "javascript", "code"]):
                        category = "Programming"
                    
                    # Create the skill
                    skill = Skill(name=skill_name, category=category)
                    db.session.add(skill)
                    added_skills += 1
                
                # Add skill to candidate
                candidate.skills.append(skill)
            
            # Add candidate to session
            db.session.add(candidate)
            added_candidates += 1
            
        except Exception as e:
            logging.error(f"Error processing {resume_file}: {e}")
    
    # Commit changes
    db.session.commit()
    logging.info(f"Successfully imported {added_candidates} candidates and {added_skills} new skills")
    return added_candidates, added_skills

if __name__ == "__main__":
    # This allows running this script directly
    from app import app
    with app.app_context():
        import_resumes(db)