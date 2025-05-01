import numpy as np
from models import Candidate, Skill, db
from sqlalchemy import func, text
from llm_search import get_candidate_text, openai_client
import json
import logging

def get_skill_categories():
    """
    Get all skill categories.
    """
    categories = db.session.query(Skill.category).distinct().order_by(Skill.category).all()
    return [category[0] for category in categories if category[0]]

def get_top_skills_by_category(category=None, limit=10):
    """
    Get the top skills by usage, optionally filtered by category.
    """
    query = db.session.query(
        Skill.id, 
        Skill.name, 
        Skill.category,
        func.count(text('candidate_skills.candidate_id')).label('candidate_count')
    ).outerjoin(text('candidate_skills')).group_by(Skill.id, Skill.name, Skill.category)
    
    if category:
        query = query.filter(Skill.category == category)
    
    skills = query.order_by(text('candidate_count DESC')).limit(limit).all()
    
    return [
        {
            'id': skill.id,
            'name': skill.name,
            'category': skill.category,
            'count': skill.candidate_count
        }
        for skill in skills
    ]

def get_top_candidates(skills=None, limit=10):
    """
    Get the top candidates, optionally filtered by skills.
    """
    query = Candidate.query
    
    if skills and len(skills) > 0:
        for skill_id in skills:
            skill_obj = Skill.query.get(skill_id)
            if skill_obj:
                query = query.filter(Candidate.skills.contains(skill_obj))
    
    candidates = query.limit(limit).all()
    
    return [
        {
            'id': candidate.id,
            'name': candidate.name,
            'title': candidate.title,
            'location': candidate.location,
            'image': candidate.profile_image,
            'skill_count': len(candidate.skills)
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
    if not candidates or not skills:
        return {
            'scores': [],
            'candidates': [],
            'skills': []
        }
    
    # Initialize score matrix
    scores = np.zeros((len(candidates), len(skills)))
    
    # Get explicit matches (candidate has the skill)
    for i, candidate in enumerate(candidates):
        candidate_obj = Candidate.query.get(candidate['id'])
        if not candidate_obj:
            continue
            
        candidate_skill_ids = [skill.id for skill in candidate_obj.skills]
        
        for j, skill in enumerate(skills):
            if skill['id'] in candidate_skill_ids:
                scores[i, j] = 1.0
    
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
    # Get candidates and skills
    if not candidate_ids:
        candidates = get_top_candidates(limit=10)
    else:
        candidates = [
            {
                'id': candidate.id,
                'name': candidate.name,
                'title': candidate.title,
                'location': candidate.location,
                'image': candidate.profile_image,
                'skill_count': len(candidate.skills)
            }
            for candidate in Candidate.query.filter(Candidate.id.in_(candidate_ids)).all()
        ]
    
    if not skill_ids:
        skills = get_top_skills_by_category(limit=10)
    else:
        skills = [
            {
                'id': skill.id,
                'name': skill.name,
                'category': skill.category,
                'count': db.session.query(func.count(text('candidate_skills.candidate_id')))
                    .select_from(Skill)
                    .outerjoin(text('candidate_skills'))
                    .filter(Skill.id == skill.id)
                    .scalar() or 0
            }
            for skill in Skill.query.filter(Skill.id.in_(skill_ids)).all()
        ]
    
    # Calculate basic matches
    result = calculate_skill_match_scores(candidates, skills)
    
    # If LLM-based matching is requested
    if use_llm and candidates and skills:
        try:
            # Enhance scores with LLM-based matching
            result = enhance_scores_with_llm(result)
        except Exception as e:
            logging.error(f"Error in LLM matching: {e}")
    
    return result

def enhance_scores_with_llm(result):
    """
    Enhance skill match scores using LLM to detect implicit matches.
    """
    scores = np.array(result['scores'])
    candidates = result['candidates']
    skills = result['skills']
    
    # Only process candidates/skills with 0 scores (not explicit matches)
    for i, candidate in enumerate(candidates):
        candidate_obj = Candidate.query.get(candidate['id'])
        if not candidate_obj:
            continue
            
        # Get candidate text representation
        candidate_text = get_candidate_text(candidate_obj)
        
        # Prepare batch of skills to evaluate
        zero_score_indices = [j for j, score in enumerate(scores[i]) if score < 0.5]
        if not zero_score_indices:
            continue
            
        skills_to_check = [skills[j]['name'] for j in zero_score_indices]
        
        # Prepare prompt
        prompt = f"""
        Based on the following candidate profile, evaluate their potential proficiency in each of the listed skills.
        Assign a score between 0.0 and 0.9 for each skill, where:
        - 0.0 means no evidence of the skill
        - 0.3 means they likely have basic familiarity based on related skills or experience
        - 0.6 means they likely have moderate proficiency based on their background
        - 0.9 means they very likely have strong proficiency based on closely related skills and experience
        
        Never assign 1.0 as that's reserved for explicitly listed skills.
        
        Return your analysis as a JSON object with skill names as keys and scores as values.
        
        Candidate Profile:
        {candidate_text}
        
        Skills to evaluate:
        {', '.join(skills_to_check)}
        """
        
        try:
            # Call OpenAI API
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a recruiting assistant helping to evaluate candidates' potential skill matches."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            # Parse the response
            result_text = response.choices[0].message.content
            skill_scores = json.loads(result_text)
            
            # Update scores
            for j, skill_idx in enumerate(zero_score_indices):
                skill_name = skills[skill_idx]['name']
                if skill_name in skill_scores:
                    scores[i, skill_idx] = min(0.9, max(0, float(skill_scores[skill_name])))
        
        except Exception as e:
            logging.error(f"Error evaluating skills with LLM for candidate {candidate['id']}: {e}")
    
    # Update result with enhanced scores
    result['scores'] = scores.tolist()
    return result