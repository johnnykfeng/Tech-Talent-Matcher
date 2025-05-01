# Tech Talent Matcher - Project Documentation

## Overview

Tech Talent Matcher is an advanced recruitment platform designed to connect tech companies with qualified candidates using AI-powered matching algorithms. The platform provides intelligent search capabilities, interactive skill visualization, and candidate management tools.

## Key Features

### 1. LLM-Powered Search

The platform uses OpenAI's GPT models to provide semantic search capabilities that understand the meaning behind search queries, not just keywords:

- **Semantic Understanding**: Searches like "data scientist with cloud experience" will match candidates with AWS/Azure skills even if they don't explicitly mention "cloud"
- **Intelligent Ranking**: Candidates are ranked by relevance to the search query
- **Smart Suggestions**: Search suggestions include semantically related terms

Implementation details:
- Found in `llm_search.py`
- Uses OpenAI embeddings for semantic matching
- Includes both explicit keyword matching and semantic matching
- Optimizes token usage by pre-filtering for simpler queries
- Caches results for better performance

### 2. Interactive Skill Matching Heatmap

A D3.js-powered visualization that shows the relationship between candidates and skills:

- **Visual Skill Matrix**: Shows which candidates have which skills through color-coded cells
- **AI-Enhanced Matching**: Can infer implicit skills based on candidate experience
- **Interactive Filtering**: Filter by skill category, number of skills, or candidates
- **Detailed Information**: Hover tooltips with match confidence and details

Implementation details:
- Backend logic in `skill_heatmap.py`
- Frontend visualization in `templates/skill_heatmap.html`
- Uses D3.js for interactive data visualization
- Supports both explicit matches (candidate lists the skill) and AI-inferred matches

### 3. Candidate Management

Comprehensive candidate profiles and management tools:

- **Detailed Profiles**: View candidate education, experience, skills, and more
- **Advanced Filtering**: Filter by location, skills, education, and other criteria
- **Shortlisting**: Save candidates for later review

## Technical Architecture

### Backend Components

- **Flask Application**: Main web application framework
  - `app.py`: Application configuration and initialization
  - `main.py`: Entry point
  - `routes.py`: Request routing and API endpoints
  
- **Database Models**: SQLAlchemy ORM models
  - `models.py`: Database schema for candidates, skills, education, etc.

- **AI Components**:
  - `llm_search.py`: LLM-powered search functionality
  - `skill_heatmap.py`: Skill matching and visualization data

- **Data Import**:
  - `data/import_resumes.py`: Import candidate data from JSON files
  - `data/candidates.py`: Seed initial candidate data
  - `data/skills.py`: Seed skill data

### Frontend Components

- **Templates**: Jinja2 HTML templates
  - `templates/base.html`: Base layout template
  - `templates/index.html`: Homepage and search results
  - `templates/candidate_detail.html`: Candidate profile page
  - `templates/skill_heatmap.html`: Skill visualization page

- **Static Assets**:
  - `static/css/styles.css`: Custom CSS styles
  - `static/js/main.js`: JavaScript functions for user interactions

### Database Schema

The application uses a PostgreSQL database with the following core models:

- **Candidate**: Core candidate information (name, title, location, bio)
- **Skill**: Skill information (name, category)
- **Education**: Candidate education details
- **Experience**: Work experience information
- **Shortlist**: User-saved candidates

The relationships include:
- Many-to-many between Candidates and Skills
- One-to-many between Candidates and Education/Experience
- Many-to-many between Users and Candidates (via Shortlist)

## API Endpoints

### Search Endpoints

- `GET /api/search-suggestions?q={query}`
  - Get search suggestions for a query
  - Returns list of candidate and skill suggestions

### Skill Heatmap Endpoints

- `GET /api/skill-categories`
  - Get all skill categories
  - Returns array of category names

- `GET /api/top-skills?category={category}&limit={limit}`
  - Get top skills in a category
  - Parameters:
    - `category`: Optional filter by category
    - `limit`: Maximum number of skills to return
  - Returns array of skill objects with usage counts

- `GET /api/top-candidates?skill_id={id}&limit={limit}`
  - Get top candidates matching skills
  - Parameters:
    - `skill_id`: Skill IDs to filter by (can be multiple)
    - `limit`: Maximum number of candidates to return
  - Returns array of candidate objects

- `GET /api/skill-match-matrix?candidate_id={id}&skill_id={id}&use_llm={0|1}`
  - Get heatmap matrix data
  - Parameters:
    - `candidate_id`: Candidate IDs to include (can be multiple)
    - `skill_id`: Skill IDs to include (can be multiple)
    - `use_llm`: Whether to use AI inference for implicit matches
  - Returns matrix of match scores between candidates and skills

### Candidate Management Endpoints

- `POST /api/shortlist`
  - Add/remove a candidate from shortlist
  - Request body: `{ "candidate_id": 123 }`
  - Returns: `{ "status": "added|removed", "message": "..." }`

- `GET /api/check-shortlist/{candidate_id}`
  - Check if a candidate is in the user's shortlist
  - Returns: `{ "shortlisted": true|false }`

## Development Guidelines

### Adding New Features

1. **New Skills or Categories**:
   - Add to the appropriate seeding file in the `data` directory
   - Run initialization to update the database

2. **Frontend Changes**:
   - Follow the existing style using Bootstrap 5 components
   - Add any custom styles to `static/css/styles.css`
   - Add JavaScript functionality to `static/js/main.js`

3. **New API Endpoints**:
   - Add route handlers to `routes.py`
   - Implement business logic in separate modules

### Running the Application

The application can be run with Gunicorn:

```
gunicorn --bind 0.0.0.0:5000 main:app
```

## Future Enhancements

1. **Resume Upload and Parsing**:
   - Allow users to upload resumes in PDF/DOCX format
   - Automatically extract candidate information

2. **Job Description Matching**:
   - Match candidates to job descriptions
   - Provide percentage match scores

3. **Candidate Outreach**:
   - Email integration for contacting candidates
   - Email templates and tracking

4. **Analytics Dashboard**:
   - Recruitment funnel analytics
   - Hiring performance metrics

5. **Team Composition Analysis**:
   - Analyze team skill gaps
   - Recommend candidates to fill skill gaps