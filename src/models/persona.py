"""
Persona model for individual AI participants in focus groups.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid


@dataclass
class Persona:
    """Represents an AI persona participating in focus groups."""
    
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    age: int = 25
    gender: str = ""
    
    # Demographics  
    location: str = ""
    occupation: str = ""
    income_level: str = ""
    education_level: str = ""
    
    # Psychographics
    personality_traits: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    lifestyle: str = ""
    
    # Behavioral patterns
    communication_style: str = "balanced"  # verbose, concise, balanced
    response_tendency: str = "honest"  # agreeable, contrarian, honest
    emotional_expression: str = "moderate"  # high, moderate, low
    
    # Background context
    background_story: str = ""
    relevant_experiences: List[str] = field(default_factory=list)
    
    # System prompts
    base_personality_prompt: str = ""
    context_instructions: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    active: bool = True
    
    def __post_init__(self):
        """Initialize persona with default personality prompt if not provided."""
        if not self.base_personality_prompt:
            self.base_personality_prompt = self._generate_default_prompt()
    
    def _generate_default_prompt(self) -> str:
        """Generate a default personality prompt based on persona attributes."""
        traits_str = ", ".join(self.personality_traits) if self.personality_traits else "friendly and thoughtful"
        values_str = ", ".join(self.values) if self.values else "authenticity and respect"
        
        return f"""
        You are {self.name}, a {self.age}-year-old {self.gender} from {self.location}.
        You work as {self.occupation} and have {self.education_level} education.
        
        Your personality is {traits_str}. You value {values_str}.
        Your communication style is {self.communication_style} and you tend to be {self.response_tendency} in your responses.
        You express emotions in a {self.emotional_expression} way.
        
        Background: {self.background_story}
        
        When participating in focus groups, stay true to this persona while being helpful and engaging.
        Draw from your experiences: {', '.join(self.relevant_experiences) if self.relevant_experiences else 'your general life experience'}.
        
        Respond naturally as this character would, considering their background, personality, and perspectives.
        """.strip()
    
    def to_dict(self) -> Dict:
        """Convert persona to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'location': self.location,
            'occupation': self.occupation,
            'income_level': self.income_level,
            'education_level': self.education_level,
            'personality_traits': self.personality_traits,
            'values': self.values,
            'interests': self.interests,
            'lifestyle': self.lifestyle,
            'communication_style': self.communication_style,
            'response_tendency': self.response_tendency,
            'emotional_expression': self.emotional_expression,
            'background_story': self.background_story,
            'relevant_experiences': self.relevant_experiences,
            'base_personality_prompt': self.base_personality_prompt,
            'context_instructions': self.context_instructions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'active': self.active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Persona':
        """Create persona from dictionary."""
        # Handle datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
        return cls(**data)
    
    def update_prompt(self) -> None:
        """Update the personality prompt and timestamp."""
        self.base_personality_prompt = self._generate_default_prompt()
        self.updated_at = datetime.now()