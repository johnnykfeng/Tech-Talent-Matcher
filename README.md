# Tech Talent Matcher

Tech Talent Matcher is an AI-powered platform for tech recruitment that uses advanced algorithms to match candidates with job requirements. The platform leverages LLM-based semantic search and skill matching to find the most relevant candidates for specific roles.

## Features

### Smart Candidate Search
- **LLM-Powered Search**: Semantic search that understands the meaning behind search queries, not just keywords
- **Intelligent Ranking**: Candidates are ranked by how well they match the search query, not just by presence of keywords
- **Advanced Filtering**: Filter candidates by location, skills, education, and more

### Interactive Skill Matching Heatmap
- **Visual Skills Analysis**: See which candidates match specific skills through an intuitive heatmap visualization
- **AI-Enhanced Matching**: Use AI to discover implicit skill matches based on candidate experience and related skills
- **Category Filtering**: Explore skills by category (Programming, AI/ML, Data, etc.)
- **Interactive Visualization**: Interactive D3.js-based heatmap with tooltips and candidate details

### Candidate Management
- **Detailed Profiles**: View comprehensive candidate profiles with education, experience, and skills
- **Shortlisting**: Save candidates to your shortlist for later review
- **Search Suggestions**: Get intelligent search suggestions based on your input

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Visualization**: D3.js for interactive data visualization
- **AI Integration**: OpenAI GPT models for semantic search and skill matching
- **Deployment**: Gunicorn WSGI HTTP Server

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database
- OpenAI API key

### Environment Variables

This application requires the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Your OpenAI API key for LLM-powered search

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd tech-talent-matcher
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   export DATABASE_URL=postgresql://username:password@localhost:5432/tech_talent_matcher
   export OPENAI_API_KEY=your_openai_api_key
   ```

4. Initialize the database:
   ```
   python -c "from app import app; from models import db; with app.app_context(): db.create_all()"
   ```

5. Run the application:
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

### Data Import

The application includes sample data for demonstration purposes. Real candidates are loaded from JSON resume files in the `data/Resumes_JSON` directory.

## API Endpoints

The application provides the following API endpoints:

- `/api/search-suggestions?q={query}`: Get search suggestions
- `/api/skill-categories`: Get all skill categories
- `/api/top-skills?category={category}&limit={limit}`: Get top skills by category
- `/api/top-candidates?skill_id={id}&limit={limit}`: Get top candidates by skills
- `/api/skill-match-matrix?candidate_id={id}&skill_id={id}&use_llm={0|1}`: Get skill match matrix data
- `/api/shortlist`: Add/remove candidates from shortlist
- `/api/check-shortlist/{candidate_id}`: Check if a candidate is shortlisted

## Project Structure

- `app.py`: Flask application setup
- `main.py`: Application entry point
- `models.py`: Database models
- `routes.py`: Route handlers
- `llm_search.py`: LLM-powered search functionality
- `skill_heatmap.py`: Skill matching heatmap functionality
- `data/`: Data import and seeding scripts
- `templates/`: HTML templates
- `static/`: Static files (CSS, JS, images)

## Future Enhancements

- Resume parsing and automatic candidate import
- Job description matching and recommendation
- Team composition analysis
- Customizable matching algorithms
- Recruiter collaboration features
- Automated candidate outreach

## License

This project is licensed under the MIT License - see the LICENSE file for details.