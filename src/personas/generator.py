"""
Persona generator for creating sample personas automatically.
"""

import random
from typing import List, Dict, Any
from models.persona import Persona


class PersonaGenerator:
    """Generates diverse, realistic personas for focus groups."""
    
    # Sample data for generating personas
    NAMES = {
        'male': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Christopher', 
                'Daniel', 'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Kenneth'],
        'female': ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen',
                  'Nancy', 'Lisa', 'Betty', 'Helen', 'Sandra', 'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle'],
        'non-binary': ['Alex', 'Jordan', 'Casey', 'Taylor', 'Morgan', 'Riley', 'Avery', 'Quinn', 'Sage', 'River']
    }
    
    LOCATIONS = [
        'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ',
        'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA', 'Dallas, TX', 'San Jose, CA',
        'Austin, TX', 'Jacksonville, FL', 'Fort Worth, TX', 'Columbus, OH', 'Charlotte, NC',
        'San Francisco, CA', 'Indianapolis, IN', 'Seattle, WA', 'Denver, CO', 'Washington, DC',
        'Boston, MA', 'Nashville, TN', 'Detroit, MI', 'Portland, OR', 'Miami, FL'
    ]
    
    OCCUPATIONS = [
        'Software Engineer', 'Teacher', 'Nurse', 'Sales Manager', 'Marketing Specialist',
        'Accountant', 'Graphic Designer', 'Project Manager', 'Consultant', 'Analyst',
        'Administrator', 'Customer Service Rep', 'Engineer', 'Writer', 'Researcher',
        'Healthcare Worker', 'Retail Manager', 'Freelancer', 'Student', 'Retired',
        'Restaurant Manager', 'Real Estate Agent', 'Financial Advisor', 'Social Worker', 'Artist'
    ]
    
    EDUCATION_LEVELS = [
        'High School Diploma', 'Some College', 'Associate Degree', "Bachelor's Degree",
        "Master's Degree", 'Doctorate', 'Professional Degree', 'Trade Certification'
    ]
    
    INCOME_LEVELS = [
        'Under $25,000', '$25,000-$40,000', '$40,000-$60,000', '$60,000-$80,000',
        '$80,000-$100,000', '$100,000-$150,000', '$150,000-$200,000', 'Over $200,000'
    ]
    
    PERSONALITY_TRAITS = [
        'outgoing', 'introverted', 'analytical', 'creative', 'practical', 'optimistic',
        'cautious', 'adventurous', 'detail-oriented', 'big-picture focused', 'empathetic',
        'logical', 'spontaneous', 'organized', 'collaborative', 'independent', 'curious',
        'traditional', 'innovative', 'patient', 'energetic', 'calm', 'ambitious', 'humble'
    ]
    
    VALUES = [
        'family', 'career success', 'financial security', 'creativity', 'helping others',
        'personal growth', 'work-life balance', 'authenticity', 'tradition', 'innovation',
        'community', 'independence', 'stability', 'adventure', 'education', 'health',
        'spirituality', 'environmental responsibility', 'social justice', 'efficiency'
    ]
    
    INTERESTS = [
        'reading', 'cooking', 'traveling', 'fitness', 'music', 'movies', 'gardening',
        'technology', 'sports', 'art', 'photography', 'gaming', 'hiking', 'crafts',
        'volunteering', 'learning languages', 'fashion', 'home improvement', 'pets',
        'social media', 'investing', 'yoga', 'meditation', 'dancing', 'writing'
    ]
    
    COMMUNICATION_STYLES = ['verbose', 'concise', 'balanced']
    RESPONSE_TENDENCIES = ['agreeable', 'contrarian', 'honest']
    EMOTIONAL_EXPRESSIONS = ['high', 'moderate', 'low']
    
    def __init__(self):
        """Initialize the persona generator."""
        pass
    
    def generate_persona(self, **overrides) -> Persona:
        """Generate a single persona with optional attribute overrides."""
        # Randomly select basic demographics
        gender = overrides.get('gender', random.choice(['male', 'female', 'non-binary']))
        age = overrides.get('age', random.randint(18, 75))
        name = overrides.get('name', random.choice(self.NAMES[gender]))
        
        # Select complementary attributes
        location = overrides.get('location', random.choice(self.LOCATIONS))
        occupation = overrides.get('occupation', random.choice(self.OCCUPATIONS))
        education_level = overrides.get('education_level', random.choice(self.EDUCATION_LEVELS))
        income_level = overrides.get('income_level', random.choice(self.INCOME_LEVELS))
        
        # Generate personality and interests
        personality_traits = overrides.get('personality_traits', 
                                         random.sample(self.PERSONALITY_TRAITS, random.randint(2, 4)))
        values = overrides.get('values', 
                              random.sample(self.VALUES, random.randint(2, 3)))
        interests = overrides.get('interests', 
                                 random.sample(self.INTERESTS, random.randint(3, 6)))
        
        # Behavioral patterns
        communication_style = overrides.get('communication_style', random.choice(self.COMMUNICATION_STYLES))
        response_tendency = overrides.get('response_tendency', random.choice(self.RESPONSE_TENDENCIES))
        emotional_expression = overrides.get('emotional_expression', random.choice(self.EMOTIONAL_EXPRESSIONS))
        
        # Generate background story
        background_story = overrides.get('background_story', 
                                       self._generate_background_story(name, age, occupation, personality_traits))
        
        # Generate relevant experiences
        relevant_experiences = overrides.get('relevant_experiences',
                                           self._generate_relevant_experiences(occupation, interests))
        
        # Create persona with all attributes
        persona_data = {
            'name': name,
            'age': age,
            'gender': gender,
            'location': location,
            'occupation': occupation,
            'income_level': income_level,
            'education_level': education_level,
            'personality_traits': personality_traits,
            'values': values,
            'interests': interests,
            'communication_style': communication_style,
            'response_tendency': response_tendency,
            'emotional_expression': emotional_expression,
            'background_story': background_story,
            'relevant_experiences': relevant_experiences
        }
        
        # Apply any additional overrides
        for key, value in overrides.items():
            if key not in persona_data:
                persona_data[key] = value
        
        return Persona(**persona_data)
    
    def generate_personas(self, count: int = 10, ensure_diversity: bool = True, **constraints) -> List[Persona]:
        """Generate multiple personas with optional diversity constraints."""
        personas = []
        
        if ensure_diversity:
            # Ensure demographic diversity
            used_combinations = set()
            max_attempts = count * 10  # Prevent infinite loops
            
            for _ in range(count):
                attempts = 0
                while attempts < max_attempts:
                    persona = self.generate_persona(**constraints)
                    
                    # Create diversity key (gender, age_range, occupation)
                    age_range = f"{(persona.age // 10) * 10}s"
                    diversity_key = (persona.gender, age_range, persona.occupation)
                    
                    if diversity_key not in used_combinations or attempts > max_attempts // 2:
                        used_combinations.add(diversity_key)
                        personas.append(persona)
                        break
                    
                    attempts += 1
                
                if len(personas) < _ + 1:  # Fallback if diversity constraint can't be met
                    personas.append(self.generate_persona(**constraints))
        else:
            # Generate without diversity constraints
            for _ in range(count):
                personas.append(self.generate_persona(**constraints))
        
        return personas
    
    def generate_targeted_personas(self, target_demographics: List[Dict[str, Any]]) -> List[Persona]:
        """Generate personas based on specific demographic targets."""
        personas = []
        
        for target in target_demographics:
            persona = self.generate_persona(**target)
            personas.append(persona)
        
        return personas
    
    def _generate_background_story(self, name: str, age: int, occupation: str, personality_traits: List[str]) -> str:
        """Generate a background story for the persona."""
        trait_str = ", ".join(personality_traits[:2])
        
        career_stage = ""
        if age < 25:
            career_stage = "just starting their career"
        elif age < 35:
            career_stage = "building their professional experience"
        elif age < 50:
            career_stage = "established in their field"
        else:
            career_stage = "experienced and knowledgeable"
        
        stories = [
            f"{name} is {trait_str} and works as a {occupation.lower()}. They are {career_stage} and bring a unique perspective shaped by their experiences.",
            f"As a {trait_str} {occupation.lower()}, {name} is {career_stage}. Their background has given them insights into various aspects of life and work.",
            f"{name} combines being {trait_str} with their work as a {occupation.lower()}. At {age}, they are {career_stage} and have valuable perspectives to share."
        ]
        
        return random.choice(stories)
    
    def _generate_relevant_experiences(self, occupation: str, interests: List[str]) -> List[str]:
        """Generate relevant experiences based on occupation and interests."""
        experiences = []
        
        # Add occupation-related experience
        if 'teacher' in occupation.lower():
            experiences.extend(['classroom management', 'curriculum development', 'student interaction'])
        elif 'software' in occupation.lower() or 'engineer' in occupation.lower():
            experiences.extend(['technology adoption', 'problem-solving', 'team collaboration'])
        elif 'sales' in occupation.lower() or 'marketing' in occupation.lower():
            experiences.extend(['customer relationships', 'market research', 'persuasion'])
        elif 'healthcare' in occupation.lower() or 'nurse' in occupation.lower():
            experiences.extend(['patient care', 'healthcare systems', 'emergency situations'])
        else:
            experiences.extend(['professional development', 'workplace dynamics', 'industry insights'])
        
        # Add interest-related experiences
        if 'traveling' in interests:
            experiences.append('cultural experiences')
        if 'technology' in interests:
            experiences.append('digital adoption')
        if 'cooking' in interests:
            experiences.append('food and dining preferences')
        if 'fitness' in interests:
            experiences.append('health and wellness routines')
        if 'volunteering' in interests:
            experiences.append('community involvement')
        
        return experiences[:5]  # Limit to 5 experiences
    
    def create_demographic_distribution(self, total_count: int) -> Dict[str, int]:
        """Create a suggested demographic distribution for balanced representation."""
        distribution = {
            'age_ranges': {
                '18-29': max(1, int(total_count * 0.25)),
                '30-44': max(1, int(total_count * 0.35)),
                '45-59': max(1, int(total_count * 0.25)),
                '60+': max(1, int(total_count * 0.15))
            },
            'genders': {
                'female': max(1, int(total_count * 0.5)),
                'male': max(1, int(total_count * 0.45)),
                'non-binary': max(1, int(total_count * 0.05))
            },
            'education_levels': {
                'High School': max(1, int(total_count * 0.2)),
                'Some College/Associate': max(1, int(total_count * 0.3)),
                "Bachelor's": max(1, int(total_count * 0.3)),
                'Advanced Degree': max(1, int(total_count * 0.2))
            }
        }
        
        return distribution
    
    def generate_preset_personas(self, preset_name: str) -> List[Persona]:
        """Generate personas based on preset configurations."""
        presets = {
            'consumer_research': [
                {'age': 28, 'occupation': 'Marketing Specialist', 'income_level': '$60,000-$80,000'},
                {'age': 45, 'occupation': 'Teacher', 'income_level': '$40,000-$60,000'},
                {'age': 35, 'occupation': 'Software Engineer', 'income_level': '$80,000-$100,000'},
                {'age': 52, 'occupation': 'Nurse', 'income_level': '$60,000-$80,000'},
                {'age': 29, 'occupation': 'Freelancer', 'income_level': '$25,000-$40,000'},
                {'age': 41, 'occupation': 'Sales Manager', 'income_level': '$80,000-$100,000'},
                {'age': 33, 'occupation': 'Graphic Designer', 'income_level': '$40,000-$60,000'},
                {'age': 26, 'occupation': 'Student', 'income_level': 'Under $25,000'},
            ],
            'healthcare': [
                {'age': 34, 'occupation': 'Nurse', 'relevant_experiences': ['patient care', 'healthcare systems']},
                {'age': 67, 'occupation': 'Retired', 'relevant_experiences': ['healthcare experience', 'medical concerns']},
                {'age': 42, 'occupation': 'Insurance Agent', 'relevant_experiences': ['healthcare costs', 'insurance']},
                {'age': 29, 'occupation': 'Physical Therapist', 'relevant_experiences': ['rehabilitation', 'patient interaction']},
                {'age': 55, 'occupation': 'Administrator', 'relevant_experiences': ['healthcare administration']},
            ],
            'technology': [
                {'age': 27, 'occupation': 'Software Engineer', 'interests': ['technology', 'gaming']},
                {'age': 31, 'occupation': 'Marketing Specialist', 'interests': ['social media', 'technology']},
                {'age': 45, 'occupation': 'Teacher', 'interests': ['education', 'technology']},
                {'age': 38, 'occupation': 'Consultant', 'interests': ['technology', 'innovation']},
                {'age': 24, 'occupation': 'Student', 'interests': ['technology', 'gaming', 'social media']},
            ]
        }
        
        if preset_name not in presets:
            return self.generate_personas(8)  # Default fallback
        
        return [self.generate_persona(**params) for params in presets[preset_name]]