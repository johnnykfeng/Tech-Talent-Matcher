from models import Candidate, Education, Experience, Skill
from datetime import datetime

def seed_candidates(db):
    """
    Seed the database with candidate data based on the screenshot and requirements
    """
    
    # Collect skills to assign to candidates
    python_skill = Skill.query.filter_by(name="Python").first()
    physics_skill = Skill.query.filter_by(name="Physics").first()
    ai_skill = Skill.query.filter_by(name="Artificial Intelligence").first()
    ml_skill = Skill.query.filter_by(name="Machine Learning").first()
    space_physics_skill = Skill.query.filter_by(name="Space Physics").first()
    research_skill = Skill.query.filter_by(name="Research").first()
    data_analysis_skill = Skill.query.filter_by(name="Data Analysis").first()
    deep_learning_skill = Skill.query.filter_by(name="Deep Learning").first()
    computer_vision_skill = Skill.query.filter_by(name="Computer Vision").first()
    generative_models_skill = Skill.query.filter_by(name="Generative Models").first()
    nlp_skill = Skill.query.filter_by(name="Natural Language Processing").first()
    
    # Create Laura Mazzino (from screenshot)
    laura = Candidate(
        name="Laura Mazzino",
        title="Assistant Professor - Teaching Department of Physics and Astronomy Faculty of Science at University of Calgary",
        location="Calgary, Alberta, Canada",
        profile_image="https://images.unsplash.com/photo-1573496358773-bdcdbd984982",
        bio="Assistant Professor at the University of Calgary with a PhD in Space Physics from the University of Alberta. She has extensive research experience, including a postdoctoral role managing the ABOVE2 project and investigating Whistler-mode waves."
    )
    
    laura_edu1 = Education(
        degree="PhD",
        field="Space Physics",
        institution="University of Alberta",
        location="Alberta, Canada",
        year=2016
    )
    
    laura_edu2 = Education(
        degree="MSc",
        field="Physics",
        institution="University of Calgary",
        location="Calgary, Canada",
        year=2011
    )
    
    laura_exp1 = Experience(
        role="Assistant Professor",
        company="University of Calgary",
        location="Calgary, Alberta, Canada",
        description="Teaching in the Department of Physics and Astronomy, Faculty of Science.",
        start_date=datetime.strptime("2019-09-01", "%Y-%m-%d"),
        is_current=True
    )
    
    laura_exp2 = Experience(
        role="Postdoctoral Researcher",
        company="University of Alberta",
        location="Edmonton, Alberta, Canada",
        description="Managing the ABOVE2 project and investigating Whistler-mode waves.",
        start_date=datetime.strptime("2016-06-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2019-08-30", "%Y-%m-%d"),
        is_current=False
    )
    
    laura.educations.append(laura_edu1)
    laura.educations.append(laura_edu2)
    laura.experiences.append(laura_exp1)
    laura.experiences.append(laura_exp2)
    laura.skills.extend([physics_skill, space_physics_skill, research_skill, data_analysis_skill])
    
    # Create Vikram Voleti (from screenshot)
    vikram = Candidate(
        name="Vikram Voleti",
        title="Research Scientist at Stability AI",
        location="Kitchener, Ontario, Canada",
        profile_image="https://images.unsplash.com/photo-1556157382-97eda2d62296",
        bio="Research Scientist at Stability AI with a PhD from Mila in Montreal. He has extensive experience in AI research, including generative models for image to 3D and text to 3D, and has contributed to transformative research initiatives in generative media."
    )
    
    vikram_edu = Education(
        degree="PhD",
        field="Computer Science",
        institution="Université de Montréal",
        location="Montreal, Quebec, Canada",
        year=2020
    )
    
    vikram_exp = Experience(
        role="Research Scientist",
        company="Stability AI",
        location="Kitchener, Ontario, Canada",
        description="Working on generative models for image to 3D and text to 3D conversion.",
        start_date=datetime.strptime("2021-03-01", "%Y-%m-%d"),
        is_current=True
    )
    
    vikram.educations.append(vikram_edu)
    vikram.experiences.append(vikram_exp)
    vikram.skills.extend([ai_skill, ml_skill, deep_learning_skill, generative_models_skill])
    
    # Create Jeff Beis (from screenshot)
    jeff = Candidate(
        name="Jeff Beis",
        title="Research Scientist at Amazon",
        location="North Vancouver, British Columbia, Canada",
        profile_image="https://images.unsplash.com/photo-1554774853-b415df9eeb92",
        bio="Research Scientist at Amazon with a Master of Science in Physics from the University of Toronto. He has extensive research experience, including a role as a Vision Research Scientist at Braintech, where he led a successful funding proposal and developed algorithms for vision-guided robotics."
    )
    
    jeff_edu1 = Education(
        degree="Master of Science",
        field="Physics",
        institution="University of Toronto",
        location="Toronto, Ontario, Canada",
        year=2015
    )
    
    jeff_edu2 = Education(
        degree="BSc",
        field="Computer Science",
        institution="The University of British Columbia",
        location="Vancouver, BC, Canada",
        year=2012
    )
    
    jeff_exp1 = Experience(
        role="Research Scientist",
        company="Amazon",
        location="North Vancouver, British Columbia, Canada",
        description="Working on computer vision applications for retail technology.",
        start_date=datetime.strptime("2019-05-01", "%Y-%m-%d"),
        is_current=True
    )
    
    jeff_exp2 = Experience(
        role="Vision Research Scientist",
        company="Braintech",
        location="Vancouver, BC, Canada",
        description="Led a successful funding proposal and developed algorithms for vision-guided robotics.",
        start_date=datetime.strptime("2015-06-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2019-04-30", "%Y-%m-%d"),
        is_current=False
    )
    
    jeff.educations.append(jeff_edu1)
    jeff.educations.append(jeff_edu2)
    jeff.experiences.append(jeff_exp1)
    jeff.experiences.append(jeff_exp2)
    jeff.skills.extend([physics_skill, computer_vision_skill, ai_skill, research_skill])
    
    # Additional candidates
    sarah = Candidate(
        name="Sarah Chen",
        title="Machine Learning Engineer at Google",
        location="Toronto, Ontario, Canada",
        profile_image="https://images.unsplash.com/photo-1573496359142-b8475525ff78",
        bio="Machine Learning Engineer with expertise in natural language processing and deep learning. Currently working on large language models at Google."
    )
    
    sarah_edu = Education(
        degree="PhD",
        field="Computer Science",
        institution="University of Waterloo",
        location="Waterloo, Ontario, Canada",
        year=2018
    )
    
    sarah_exp = Experience(
        role="Machine Learning Engineer",
        company="Google",
        location="Toronto, Ontario, Canada",
        description="Working on large language models and natural language processing technologies.",
        start_date=datetime.strptime("2018-07-01", "%Y-%m-%d"),
        is_current=True
    )
    
    sarah.educations.append(sarah_edu)
    sarah.experiences.append(sarah_exp)
    sarah.skills.extend([ai_skill, ml_skill, nlp_skill, deep_learning_skill])
    
    # Create Michael Rodriguez
    michael = Candidate(
        name="Michael Rodriguez",
        title="Senior Data Scientist at Microsoft",
        location="Vancouver, British Columbia, Canada",
        profile_image="https://images.unsplash.com/photo-1553484771-898ed465e931",
        bio="Senior Data Scientist with a background in statistical modeling and machine learning. Specializes in developing predictive analytics solutions for business problems."
    )
    
    michael_edu = Education(
        degree="MSc",
        field="Data Science",
        institution="Simon Fraser University",
        location="Burnaby, BC, Canada",
        year=2016
    )
    
    michael_exp = Experience(
        role="Senior Data Scientist",
        company="Microsoft",
        location="Vancouver, BC, Canada",
        description="Leading a team developing predictive analytics models for Azure cloud services.",
        start_date=datetime.strptime("2019-01-15", "%Y-%m-%d"),
        is_current=True
    )
    
    michael.educations.append(michael_edu)
    michael.experiences.append(michael_exp)
    michael.skills.extend([python_skill, ml_skill, data_analysis_skill])
    
    # Create Priya Sharma
    priya = Candidate(
        name="Priya Sharma",
        title="AI Researcher at OpenAI",
        location="Montreal, Quebec, Canada",
        profile_image="https://images.unsplash.com/photo-1573496359142-b8475525ff78",
        bio="AI Researcher specializing in reinforcement learning and multi-agent systems. Currently working on developing more efficient training methods for large language models."
    )
    
    priya_edu = Education(
        degree="PhD",
        field="Artificial Intelligence",
        institution="McGill University",
        location="Montreal, Quebec, Canada",
        year=2019
    )
    
    priya_exp = Experience(
        role="AI Researcher",
        company="OpenAI",
        location="Montreal, Quebec, Canada",
        description="Researching reinforcement learning approaches for large language models.",
        start_date=datetime.strptime("2020-02-01", "%Y-%m-%d"),
        is_current=True
    )
    
    priya.educations.append(priya_edu)
    priya.experiences.append(priya_exp)
    priya.skills.extend([ai_skill, ml_skill, deep_learning_skill, nlp_skill])
    
    # Add all candidates to the session
    db.session.add_all([laura, vikram, jeff, sarah, michael, priya])
    db.session.commit()
