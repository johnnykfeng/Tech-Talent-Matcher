from app import db
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey


# Many-to-many relationship tables
candidate_skills = Table(
    'candidate_skills', 
    db.metadata,
    Column('candidate_id', Integer, ForeignKey('candidate.id')),
    Column('skill_id', Integer, ForeignKey('skill.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    company_name = db.Column(db.String(100))
    role = db.Column(db.String(50))
    shortlisted_candidates = db.relationship('Shortlist', backref='user', lazy=True)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=False)  # Increased from 100 to 255
    location = db.Column(db.String(100))
    profile_image = db.Column(db.String(255))  # Increased from 200 to 255
    bio = db.Column(db.Text)
    
    # Education and experience
    educations = db.relationship('Education', backref='candidate', lazy=True)
    experiences = db.relationship('Experience', backref='candidate', lazy=True)
    
    # Skills many-to-many relationship
    skills = db.relationship('Skill', secondary=candidate_skills, backref=db.backref('candidates', lazy='dynamic'))
    
    # Shortlists
    shortlisted_by = db.relationship('Shortlist', backref='candidate', lazy=True)


class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(100), nullable=False)
    field = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    year = db.Column(db.Integer)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)


class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    is_current = db.Column(db.Boolean, default=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(50))  # like "Programming", "Soft Skills", etc.


class Shortlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    notes = db.Column(db.Text)
