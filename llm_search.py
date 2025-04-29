import os
import json
import logging
from openai import OpenAI
from models import Candidate, Skill, Education, Experience
from sqlalchemy import or_, and_, func, text
from flask import current_app
from functools import lru_cache

# Initialize the OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_embeddings(text):
    """
    Generate embeddings for a given text using OpenAI's embedding API.
    """
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        # Return the embedding vector
        return response.data[0].embedding
    except Exception as e:
        logging.error(f"Error generating embeddings: {e}")
        return None

def get_candidate_text(candidate):
    """
    Create a text representation of a candidate for semantic search.
    """
    # Combine candidate name, title, and bio
    candidate_text = f"{candidate.name} - {candidate.title}\n{candidate.bio}"
    
    # Add skills
    skills_text = ", ".join([skill.name for skill in candidate.skills])
    if skills_text:
        candidate_text += f"\nSkills: {skills_text}"
    
    # Add education
    for edu in candidate.educations:
        edu_text = f"{edu.degree} in {edu.field} from {edu.institution}"
        if edu.year:
            edu_text += f" ({edu.year})"
        candidate_text += f"\n{edu_text}"
    
    # Add experience
    for exp in candidate.experiences:
        exp_text = f"{exp.role} at {exp.company}"
        if exp.description:
            exp_text += f"\n{exp.description}"
        candidate_text += f"\n{exp_text}"
    
    return candidate_text

def rank_candidates_with_llm(search_query, candidates, top_n=15):
    """
    Rank candidates based on their relevance to the search query using LLM.
    """
    if not search_query or not candidates:
        return candidates
    
    try:
        # For short and simple queries, optimize the search
        if len(search_query.split()) <= 3:
            # Use regular database search as a pre-filter
            search_terms = '%' + search_query + '%'
            pre_filtered = [c for c in candidates if 
                            search_query.lower() in c.name.lower() or 
                            search_query.lower() in c.title.lower() or 
                            (c.bio and search_query.lower() in c.bio.lower()) or
                            any(search_query.lower() in skill.name.lower() for skill in c.skills)]
            
            # If we have enough results, use those, otherwise use all candidates
            candidates_to_rank = pre_filtered if len(pre_filtered) >= 5 else candidates
        else:
            # For complex queries, evaluate all candidates
            candidates_to_rank = candidates
        
        # If we have a lot of candidates, use OpenAI to rank them
        if len(candidates_to_rank) > 0:
            # Create a prompt for the LLM to evaluate candidate matches
            prompt = f"""
            I need to find the best candidates matching this search query: "{search_query}"
            
            Please rank the following candidates from most relevant to least relevant based on how well they match the search query.
            Consider skills, experience, job titles, and education when determining relevance.
            Return your response as a JSON array of candidate IDs in order of relevance.
            
            Candidates:
            """
            
            # Add candidate information to the prompt
            for i, candidate in enumerate(candidates_to_rank[:50]):  # Limit to 50 to avoid token limit
                candidate_text = get_candidate_text(candidate)
                prompt += f"\nID {candidate.id}: {candidate_text}\n{'='*40}"
            
            # Call OpenAI API
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                messages=[
                    {"role": "system", "content": "You are a recruiting assistant helping to find the best matched candidates for a search query. Rank candidates purely by relevance to the search query."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            # Parse the response
            result_text = response.choices[0].message.content
            
            try:
                # Try to parse as JSON
                result = json.loads(result_text)
                if "ranked_candidates" in result:
                    ordered_ids = result["ranked_candidates"]
                else:
                    # Look for an array in the response
                    for key in result:
                        if isinstance(result[key], list) and all(isinstance(x, int) for x in result[key]):
                            ordered_ids = result[key]
                            break
                    else:
                        # Fallback: find the first list in the result
                        for key in result:
                            if isinstance(result[key], list):
                                ordered_ids = result[key]
                                break
                        else:
                            ordered_ids = list(result.values())[0] if result else []
                
                # Convert to integers if they're strings
                ordered_ids = [int(id) if isinstance(id, str) and id.isdigit() else id for id in ordered_ids]
                
                # Filter to only include valid candidate IDs
                valid_ids = [c.id for c in candidates_to_rank]
                ordered_ids = [id for id in ordered_ids if id in valid_ids]
                
                # Add any missing candidates at the end
                missing_ids = [id for id in valid_ids if id not in ordered_ids]
                ordered_ids.extend(missing_ids)
                
                # Create the ordered list of candidates
                id_to_index = {id: i for i, id in enumerate(ordered_ids)}
                ranked_candidates = sorted(candidates, key=lambda c: id_to_index.get(c.id, len(candidates)))
                
                return ranked_candidates[:top_n]
                
            except Exception as e:
                logging.error(f"Error parsing LLM response: {e}")
                logging.error(f"Response was: {result_text}")
                # Fallback: return candidates sorted by name
                return sorted(candidates, key=lambda c: c.name)[:top_n]
                
    except Exception as e:
        logging.error(f"Error in LLM ranking: {e}")
    
    # Fallback: return candidates as is
    return candidates[:top_n]

def search_candidates(db, search_query, filters=None, page=1, per_page=15):
    """
    Main search function that combines database filtering with LLM-based relevance ranking.
    
    Args:
        db: SQLAlchemy database instance
        search_query: User's search query string
        filters: Dictionary of filters to apply (location, skills, education)
        page: Page number for pagination
        per_page: Number of results per page
        
    Returns:
        Paginated results of candidates ranked by relevance
    """
    # Start with base query
    query = Candidate.query
    
    # Apply basic filters first (before LLM ranking)
    if filters:
        # Apply location filter
        location_filter = filters.get('location', [])
        if location_filter:
            query = query.filter(Candidate.location.in_(location_filter))
        
        # Apply skill filter
        skill_filter = filters.get('skill', [])
        if skill_filter:
            for skill in skill_filter:
                skill_obj = Skill.query.filter_by(name=skill).first()
                if skill_obj:
                    query = query.filter(Candidate.skills.contains(skill_obj))
        
        # Apply education filter
        education_filter = filters.get('education', [])
        if education_filter:
            education_candidates = db.session.query(Education.candidate_id).filter(
                Education.degree.in_(education_filter)
            ).distinct().subquery()
            
            query = query.filter(Candidate.id.in_(education_candidates))
    
    # Get all candidates that match the filters
    filtered_candidates = query.all()
    
    # Apply LLM-based ranking if we have a search query
    if search_query:
        ranked_candidates = rank_candidates_with_llm(search_query, filtered_candidates, top_n=len(filtered_candidates))
    else:
        ranked_candidates = filtered_candidates
    
    # Calculate pagination
    total = len(ranked_candidates)
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    
    # Create a subset for the current page
    current_page_candidates = ranked_candidates[start:end]
    
    # Create a pagination-like object
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
        
        @property
        def has_prev(self):
            return self.page > 1
            
        @property
        def prev_num(self):
            return self.page - 1 if self.has_prev else None
            
        @property
        def has_next(self):
            return self.page < self.pages
            
        @property
        def next_num(self):
            return self.page + 1 if self.has_next else None
    
    # Return pagination object
    return Pagination(
        items=current_page_candidates,
        page=page,
        per_page=per_page,
        total=total
    )

@lru_cache(maxsize=100)
def get_search_suggestions(query, max_results=5):
    """
    Get semantically relevant search suggestions for a query using LLM.
    This function is cached to improve performance for repeated queries.
    
    Args:
        query: The search query to get suggestions for
        max_results: Maximum number of suggestions to return
        
    Returns:
        List of suggestion dictionaries with text and type
    """
    if not query or len(query) < 2:
        return []
        
    try:
        # First try regular database matching for efficiency
        search_term = '%' + query + '%'
        
        # Get candidates matching the search term
        candidates = Candidate.query.filter(
            or_(
                Candidate.name.ilike(search_term),
                Candidate.title.ilike(search_term)
            )
        ).limit(max_results).all()
        
        # Get skills matching the search term
        skills = Skill.query.filter(Skill.name.ilike(search_term)).limit(max_results).all()
        
        results = [
            {'type': 'candidate', 'id': c.id, 'text': c.name, 'subtext': c.title}
            for c in candidates
        ]
        
        results.extend([
            {'type': 'skill', 'id': s.id, 'text': s.name, 'subtext': 'Skill'}
            for s in skills
        ])
        
        # If we don't have enough results, use LLM to suggest related search terms
        if len(results) < max_results and len(query) >= 3:
            prompt = f"""
            I'm looking for candidates with the following search query: "{query}"
            
            Please suggest {max_results - len(results)} related search terms that might help find relevant candidates.
            Consider related skills, job titles, or industries that might match what I'm looking for.
            Return your suggestions as a JSON array with "text" and "subtext" fields.
            Format: 
            {{"suggestions": [
                {{"text": "suggested search term", "subtext": "reason for suggestion"}}
            ]}}
            
            Be concise in your suggestions and make them highly relevant to tech recruitment and the original query.
            """
            
            try:
                # Call OpenAI API
                response = openai_client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                    messages=[
                        {"role": "system", "content": "You are a recruiting assistant helping to find relevant search suggestions for a tech recruitment platform."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                    max_tokens=300
                )
                
                # Parse the response
                result_text = response.choices[0].message.content
                result = json.loads(result_text)
                
                if "suggestions" in result and isinstance(result["suggestions"], list):
                    for suggestion in result["suggestions"]:
                        if "text" in suggestion:
                            results.append({
                                'type': 'suggested',
                                'id': None,
                                'text': suggestion["text"],
                                'subtext': suggestion.get("subtext", "Suggested search")
                            })
            except Exception as e:
                logging.error(f"Error getting LLM suggestions: {e}")
        
        return results[:max_results]
        
    except Exception as e:
        logging.error(f"Error in search suggestions: {e}")
        return []