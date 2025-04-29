from flask import render_template, request, redirect, url_for, jsonify, session, flash
from app import app, db
from models import Candidate, Education, Experience, Skill, Shortlist
from sqlalchemy import or_, and_, func
import logging
import os
from data.candidates import seed_candidates
from data.skills import seed_skills
from data.locations import LOCATIONS
from data.import_resumes import import_resumes
from llm_search import search_candidates, get_search_suggestions

# Initialize the database - recreate all tables and seed with data
def initialize_data(force=False):
    # Check if the database needs to be recreated (force=True or if no candidates exist)
    should_initialize = force or Candidate.query.count() == 0
    
    if should_initialize:
        # Count JSON resume files
        resumes_dir = "data/Resumes_JSON"
        resume_files = []
        if os.path.exists(resumes_dir):
            resume_files = [f for f in os.listdir(resumes_dir) if f.endswith('.json')]
        logging.info(f"Found {len(resume_files)} JSON resume files in {resumes_dir}")
        
        # Drop all tables and recreate them with the updated schema
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
    else:
        logging.info("Database already initialized, skipping initialization")

# Initialize data when the application starts
with app.app_context():
    # Force reinitialization to include new resumes
    initialize_data(force=True)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Match the number in the screenshot (15 candidates)
    
    # Get filters from request
    search_query = request.args.get('q', '')
    location_filter = request.args.getlist('location')
    skill_filter = request.args.getlist('skill')
    education_filter = request.args.getlist('education')
    
    # Prepare filters dictionary for the search function
    filters = {}
    if location_filter:
        filters['location'] = location_filter
    if skill_filter:
        filters['skill'] = skill_filter
    if education_filter:
        filters['education'] = education_filter
    
    # Use LLM-powered search function
    candidates = search_candidates(
        db=db,
        search_query=search_query,
        filters=filters,
        page=page,
        per_page=per_page
    )
    
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
    
    # Use our improved search suggestions function that includes LLM suggestions
    results = get_search_suggestions(query, max_results=7)
    
    return jsonify(results)
