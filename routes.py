from flask import render_template, request, redirect, url_for, jsonify, session, flash
from app import app, db
from models import Candidate, Education, Experience, Skill, Shortlist
from sqlalchemy import or_, and_, func
import logging
from data.candidates import seed_candidates
from data.skills import seed_skills
from data.locations import LOCATIONS
from data.import_resumes import import_resumes

# Initialize the database - recreate all tables and seed with data
def initialize_data():
    # Drop all tables and recreate them with the updated schema
    with app.app_context():
        db.drop_all()
        db.create_all()
        
    # Seed the database with initial skills and candidates
    seed_skills(db)
    seed_candidates(db)
    
    # Import additional resumes from JSON files
    try:
        added_candidates, added_skills = import_resumes(db)
        logging.info(f"Imported {added_candidates} candidates and {added_skills} new skills from JSON files")
    except Exception as e:
        logging.error(f"Error importing resumes: {e}")
    
    db.session.commit()
    logging.info("Database recreated and seeded with initial data")

# Initialize data when the application starts
with app.app_context():
    initialize_data()

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Match the number in the screenshot (15 candidates)
    
    # Get filters from request
    search_query = request.args.get('q', '')
    location_filter = request.args.getlist('location')
    skill_filter = request.args.getlist('skill')
    education_filter = request.args.getlist('education')
    
    # Base query
    query = Candidate.query
    
    # Apply search if provided
    if search_query:
        search_terms = '%' + search_query + '%'
        query = query.filter(
            or_(
                Candidate.name.ilike(search_terms),
                Candidate.title.ilike(search_terms),
                Candidate.bio.ilike(search_terms)
            )
        )
    
    # Apply location filter if provided
    if location_filter:
        query = query.filter(Candidate.location.in_(location_filter))
    
    # Apply skill filter if provided
    if skill_filter:
        for skill in skill_filter:
            # This will filter candidates who have the specified skill
            skill_obj = Skill.query.filter_by(name=skill).first()
            if skill_obj:
                query = query.filter(Candidate.skills.contains(skill_obj))
    
    # Apply education filter if provided
    if education_filter:
        education_candidates = db.session.query(Education.candidate_id).filter(
            Education.degree.in_(education_filter)
        ).distinct().subquery()
        
        query = query.filter(Candidate.id.in_(education_candidates))
    
    # Execute paginated query
    candidates = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all skills for filter options
    all_skills = Skill.query.order_by(Skill.name).all()
    
    # Get all locations for filter options
    all_locations = LOCATIONS
    
    # Get all education degrees for filter options
    all_degrees = db.session.query(Education.degree).distinct().all()
    all_degrees = [degree[0] for degree in all_degrees]
    
    return render_template(
        'index.html',
        candidates=candidates,
        search_query=search_query,
        location_filter=location_filter,
        skill_filter=skill_filter,
        education_filter=education_filter,
        all_skills=all_skills,
        all_locations=all_locations,
        all_degrees=all_degrees
    )

@app.route('/candidates/<int:id>')
def candidate_detail(id):
    candidate = Candidate.query.get_or_404(id)
    return render_template('candidate_detail.html', candidate=candidate)

@app.route('/api/shortlist', methods=['POST'])
def shortlist_candidate():
    data = request.json
    candidate_id = data.get('candidate_id')
    
    # In a real app, we would use the current user's ID
    # For this demo, we'll use a session-based approach
    user_id = session.get('user_id', 1)  # Default to user 1 for demo
    
    # Check if already shortlisted
    existing = Shortlist.query.filter_by(
        user_id=user_id,
        candidate_id=candidate_id
    ).first()
    
    if existing:
        # Remove from shortlist
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed', 'message': 'Removed from shortlist'})
    else:
        # Add to shortlist
        shortlist = Shortlist(user_id=user_id, candidate_id=candidate_id)
        db.session.add(shortlist)
        db.session.commit()
        return jsonify({'status': 'added', 'message': 'Added to shortlist'})

@app.route('/api/check-shortlist/<int:candidate_id>')
def check_shortlist(candidate_id):
    # In a real app, we would use the current user's ID
    user_id = session.get('user_id', 1)  # Default to user 1 for demo
    
    existing = Shortlist.query.filter_by(
        user_id=user_id,
        candidate_id=candidate_id
    ).first()
    
    return jsonify({'shortlisted': existing is not None})

@app.route('/api/search-suggestions')
def search_suggestions():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    search_term = '%' + query + '%'
    
    # Get candidates matching the search term
    candidates = Candidate.query.filter(
        or_(
            Candidate.name.ilike(search_term),
            Candidate.title.ilike(search_term)
        )
    ).limit(5).all()
    
    # Get skills matching the search term
    skills = Skill.query.filter(Skill.name.ilike(search_term)).limit(5).all()
    
    results = [
        {'type': 'candidate', 'id': c.id, 'text': c.name, 'subtext': c.title}
        for c in candidates
    ]
    
    results.extend([
        {'type': 'skill', 'id': s.id, 'text': s.name, 'subtext': 'Skill'}
        for s in skills
    ])
    
    return jsonify(results)
