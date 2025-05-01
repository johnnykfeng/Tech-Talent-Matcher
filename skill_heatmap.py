import numpy as np
from functools import lru_cache
from sqlalchemy import func
from app import db
from models import Candidate, Skill, candidate_skills

def get_skill_categories():
    """
    Get all skill categories.
    """
    # Query distinct categories that are not None
    categories = db.session.query(Skill.category).filter(
        Skill.category.isnot(None)
    ).distinct().all()
    
    # Extract category names and sort alphabetically
    return sorted([category[0] for category in categories if category[0]])

def get_top_skills_by_category(category=None, limit=10):
    """
    Get the top skills by usage, optionally filtered by category.
    """
    # Build the query
    query = db.session.query(
        Skill.id,
        Skill.name,
        Skill.category,
        func.count(candidate_skills.c.candidate_id).label('count')
    ).outerjoin(
        candidate_skills,
        Skill.id == candidate_skills.c.skill_id
    ).group_by(
        Skill.id
    )
    
    # Apply category filter if provided
    if category:
        query = query.filter(Skill.category == category)
    
    # Get results ordered by usage count, descending
    skills = query.order_by(
        func.count(candidate_skills.c.candidate_id).desc()
    ).limit(limit).all()
    
    # Convert to dictionary format
    return [
        {
            'id': skill.id,
            'name': skill.name,
            'category': skill.category,
            'count': skill.count
        }
        for skill in skills
    ]

def get_top_candidates(skills=None, limit=10):
    """
    Get the top candidates, optionally filtered by skills.
    """
    # Start with a query for candidates and their skill counts
    query = db.session.query(
        Candidate.id,
        Candidate.name,
        Candidate.title,
        Candidate.location,
        func.count(candidate_skills.c.skill_id).label('skill_count')
    ).outerjoin(
        candidate_skills,
        Candidate.id == candidate_skills.c.candidate_id
    ).group_by(
        Candidate.id
    )
    
    # Filter by skills if provided
    if skills and len(skills) > 0:
        # Convert to list if single ID is provided
        if not isinstance(skills, list):
            skills = [skills]
        
        # Create a subquery that counts matches for each candidate
        skill_match_counts = db.session.query(
            candidate_skills.c.candidate_id,
            func.count(candidate_skills.c.skill_id).label('matches')
        ).filter(
            candidate_skills.c.skill_id.in_(skills)
        ).group_by(
            candidate_skills.c.candidate_id
        ).subquery()
        
        # Join with the main query and order by match count
        query = query.join(
            skill_match_counts,
            Candidate.id == skill_match_counts.c.candidate_id
        ).order_by(
            skill_match_counts.c.matches.desc(),
            func.count(candidate_skills.c.skill_id).desc()
        )
    else:
        # If no skills are specified, order by total skill count
        query = query.order_by(
            func.count(candidate_skills.c.skill_id).desc()
        )
    
    # Limit the results
    candidates = query.limit(limit).all()
    
    # Convert to dictionary format
    return [
        {
            'id': candidate.id,
            'name': candidate.name,
            'title': candidate.title,
            'location': candidate.location,
            'skill_count': candidate.skill_count
        }
        for candidate in candidates
    ]

def calculate_skill_match_scores(candidates, skills):
    """
    Calculate a match score matrix between candidates and skills.
    
    Returns:
        A dictionary with:
            - scores: 2D matrix of scores
            - candidates: list of candidate info
            - skills: list of skill info
    """
    # Create empty score matrix
    scores = np.zeros((len(candidates), len(skills)))
    
    # For each candidate
    for i, candidate in enumerate(candidates):
        # Get the candidate's skills
        candidate_skill_ids = set(
            skill_id for skill_id, in db.session.query(
                candidate_skills.c.skill_id
            ).filter(
                candidate_skills.c.candidate_id == candidate['id']
            ).all()
        )
        
        # For each skill
        for j, skill in enumerate(skills):
            # Check if the candidate has this skill
            if skill['id'] in candidate_skill_ids:
                scores[i][j] = 1.0
    
    return {
        'scores': scores.tolist(),
        'candidates': candidates,
        'skills': skills
    }

def calculate_skill_match_matrix(candidate_ids=None, skill_ids=None, use_llm=False):
    """
    Calculate a match matrix between candidates and skills.
    
    Args:
        candidate_ids: List of candidate IDs to include
        skill_ids: List of skill IDs to include
        use_llm: Whether to use LLM to estimate implicit skill matches
        
    Returns:
        Dictionary with scores, candidates, and skills
    """
    # Get candidates
    if candidate_ids:
        # Convert to list if single ID is provided
        if not isinstance(candidate_ids, list):
            candidate_ids = [candidate_ids]
        
        candidates = db.session.query(
            Candidate.id,
            Candidate.name
        ).filter(
            Candidate.id.in_(candidate_ids)
        ).all()
    else:
        # If no candidates specified, get top 10
        candidates = db.session.query(
            Candidate.id,
            Candidate.name
        ).limit(10).all()
    
    # Get skills
    if skill_ids:
        # Convert to list if single ID is provided
        if not isinstance(skill_ids, list):
            skill_ids = [skill_ids]
        
        skills = db.session.query(
            Skill.id,
            Skill.name,
            Skill.category
        ).filter(
            Skill.id.in_(skill_ids)
        ).all()
    else:
        # If no skills specified, get top 10
        skills = db.session.query(
            Skill.id,
            Skill.name,
            Skill.category
        ).limit(10).all()
    
    # Format candidates and skills for output
    candidate_list = [
        {'id': c.id, 'name': c.name} for c in candidates
    ]
    
    skill_list = [
        {'id': s.id, 'name': s.name, 'category': s.category} for s in skills
    ]
    
    # Calculate match scores
    result = calculate_skill_match_scores(candidate_list, skill_list)
    
    # Use LLM to enhance scores if requested
    if use_llm and len(candidate_list) > 0 and len(skill_list) > 0:
        result = enhance_scores_with_llm(result)
    
    return result

def enhance_scores_with_llm(result):
    """
    Enhance skill match scores using LLM to detect implicit matches.
    
    This is a placeholder for the actual LLM-based enhancement.
    In a real implementation, this would use OpenAI or another LLM
    to analyze candidate profiles and determine if they likely
    have skills that aren't explicitly listed.
    """
    try:
        from openai import OpenAI
        import os
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Get the original scores
        scores = np.array(result['scores'])
        candidates = result['candidates']
        skills = result['skills']
        
        # For each candidate and skill
        for i, candidate in enumerate(candidates):
            # Get candidate details
            candidate_data = db.session.query(Candidate).filter(Candidate.id == candidate['id']).first()
            if not candidate_data:
                continue
                
            # Build candidate text
            candidate_text = f"Name: {candidate_data.name}\n"
            candidate_text += f"Title: {candidate_data.title}\n"
            candidate_text += f"Bio: {candidate_data.bio or ''}\n"
            
            # Add education
            candidate_text += "Education:\n"
            for edu in candidate_data.educations:
                candidate_text += f"- {edu.degree} in {edu.field} from {edu.institution}\n"
            
            # Add experience
            candidate_text += "Experience:\n"
            for exp in candidate_data.experiences:
                candidate_text += f"- {exp.role} at {exp.company}: {exp.description or ''}\n"
            
            # For each skill the candidate doesn't explicitly have
            for j, skill in enumerate(skills):
                if scores[i][j] == 0:  # Only process skills the candidate doesn't have
                    # Get more info about the skill
                    skill_data = db.session.query(Skill).filter(Skill.id == skill['id']).first()
                    skill_name = skill_data.name if skill_data else skill['name']
                    
                    # Prepare the prompt
                    prompt = f"""
                    Based on the following candidate profile, determine if they likely have experience with the skill '{skill_name}' 
                    even if it's not explicitly listed. Consider related skills, job roles, and educational background.
                    
                    Candidate profile:
                    {candidate_text}
                    
                    Rate the likelihood on a scale from 0.0 to 0.9, where:
                    - 0.0 means definitely doesn't have the skill
                    - 0.3 means possibly has the skill (low confidence)
                    - 0.6 means likely has the skill (medium confidence)
                    - 0.9 means very likely has the skill (high confidence)
                    
                    Return only the numeric score.
                    """
                    
                    # Call OpenAI
                    response = client.chat.completions.create(
                        model="gpt-4o",  # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
                        messages=[
                            {"role": "system", "content": "You are a skilled technical recruiter who can identify implicit skills from candidate profiles."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=10,
                        temperature=0.2
                    )
                    
                    # Parse response
                    try:
                        score_text = response.choices[0].message.content.strip()
                        score = float(score_text)
                        # Ensure score is in the right range
                        score = max(0.0, min(0.9, score))
                        scores[i][j] = score
                    except (ValueError, IndexError):
                        # If parsing fails, leave as 0
                        pass
        
        # Update the result with enhanced scores
        result['scores'] = scores.tolist()
        
        return result
        
    except Exception as e:
        # If anything goes wrong, return the original scores
        print(f"Error enhancing scores with LLM: {e}")
        return result