from models import Skill

def seed_skills(db):
    """
    Seed the database with skills for candidates
    """
    
    # Programming languages
    programming_skills = [
        Skill(name="Python", category="Programming"),
        Skill(name="JavaScript", category="Programming"),
        Skill(name="Java", category="Programming"),
        Skill(name="C++", category="Programming"),
        Skill(name="Ruby", category="Programming"),
        Skill(name="Go", category="Programming"),
        Skill(name="Rust", category="Programming"),
        Skill(name="TypeScript", category="Programming"),
        Skill(name="PHP", category="Programming"),
        Skill(name="Swift", category="Programming"),
        Skill(name="Kotlin", category="Programming")
    ]
    
    # AI/ML skills
    ai_ml_skills = [
        Skill(name="Machine Learning", category="AI/ML"),
        Skill(name="Deep Learning", category="AI/ML"),
        Skill(name="Natural Language Processing", category="AI/ML"),
        Skill(name="Computer Vision", category="AI/ML"),
        Skill(name="Artificial Intelligence", category="AI/ML"),
        Skill(name="Data Science", category="AI/ML"),
        Skill(name="Neural Networks", category="AI/ML"),
        Skill(name="Reinforcement Learning", category="AI/ML"),
        Skill(name="TensorFlow", category="AI/ML"),
        Skill(name="PyTorch", category="AI/ML"),
        Skill(name="Generative Models", category="AI/ML")
    ]
    
    # Data skills
    data_skills = [
        Skill(name="SQL", category="Data"),
        Skill(name="Data Analysis", category="Data"),
        Skill(name="Big Data", category="Data"),
        Skill(name="Data Visualization", category="Data"),
        Skill(name="Data Engineering", category="Data"),
        Skill(name="Database Design", category="Data"),
        Skill(name="Business Intelligence", category="Data"),
        Skill(name="ETL", category="Data"),
        Skill(name="NoSQL", category="Data"),
        Skill(name="Data Mining", category="Data")
    ]
    
    # Physics/Science skills
    science_skills = [
        Skill(name="Physics", category="Science"),
        Skill(name="Space Physics", category="Science"),
        Skill(name="Quantum Physics", category="Science"),
        Skill(name="Astrophysics", category="Science"),
        Skill(name="Particle Physics", category="Science"),
        Skill(name="Computational Physics", category="Science"),
        Skill(name="Material Science", category="Science"),
        Skill(name="Biophysics", category="Science"),
        Skill(name="Statistical Mechanics", category="Science")
    ]
    
    # General professional skills
    general_skills = [
        Skill(name="Research", category="Professional"),
        Skill(name="Project Management", category="Professional"),
        Skill(name="Leadership", category="Professional"),
        Skill(name="Problem Solving", category="Professional"),
        Skill(name="Communication", category="Professional"),
        Skill(name="Team Management", category="Professional"),
        Skill(name="Public Speaking", category="Professional"),
        Skill(name="Technical Writing", category="Professional"),
        Skill(name="Grant Writing", category="Professional")
    ]
    
    # Add all skills to the database
    all_skills = programming_skills + ai_ml_skills + data_skills + science_skills + general_skills
    db.session.add_all(all_skills)
    db.session.commit()
