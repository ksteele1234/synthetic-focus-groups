"""
Facilitator model for AI moderators in focus groups.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid


@dataclass
class Facilitator:
    """Represents an AI facilitator/moderator for focus groups."""
    
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    expertise_area: str = ""
    
    # Facilitation style
    moderation_style: str = "balanced"  # directive, collaborative, balanced, hands-off
    questioning_approach: str = "probing"  # direct, probing, empathetic, analytical
    tone: str = "professional"  # casual, professional, friendly, authoritative
    
    # Question management
    primary_questions: List[str] = field(default_factory=list)
    follow_up_count_range: tuple = field(default=(3, 5))  # min, max follow-ups per participant
    
    # Instructions and prompts  
    base_instructions: str = ""
    research_context: str = ""
    objectives: List[str] = field(default_factory=list)
    
    # Behavior settings
    encourage_discussion: bool = True
    manage_time: bool = True
    handle_conflicts: bool = True
    synthesize_responses: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    active: bool = True
    
    def __post_init__(self):
        """Initialize facilitator with default instructions if not provided."""
        if not self.base_instructions:
            self.base_instructions = self._generate_default_instructions()
    
    def _generate_default_instructions(self) -> str:
        """Generate default facilitator instructions based on settings."""
        objectives_str = "\\n".join([f"- {obj}" for obj in self.objectives]) if self.objectives else "- Gather meaningful insights from participants"
        
        follow_up_range = f"{self.follow_up_count_range[0]}-{self.follow_up_count_range[1]}"
        
        return f"""
        You are {self.name}, an expert focus group facilitator specializing in {self.expertise_area}.
        Your moderation style is {self.moderation_style} and you use a {self.questioning_approach} questioning approach.
        Your tone should be {self.tone} throughout the session.
        
        RESEARCH CONTEXT:
        {self.research_context}
        
        SESSION OBJECTIVES:
        {objectives_str}
        
        FACILITATION GUIDELINES:
        1. Work through the primary questions systematically
        2. Ask {follow_up_range} follow-up questions for each participant to probe deeper
        3. {"Encourage cross-participant discussion and build on responses" if self.encourage_discussion else "Focus on individual responses"}
        4. {"Monitor time and keep the session moving" if self.manage_time else "Allow natural flow without time pressure"}  
        5. {"Address any conflicts or disagreements constructively" if self.handle_conflicts else "Let disagreements play out naturally"}
        6. {"Synthesize key themes and insights as you progress" if self.synthesize_responses else "Focus on eliciting responses without synthesis"}
        
        FOLLOW-UP QUESTION TECHNIQUES:
        - "Can you tell me more about that?"
        - "What makes you feel that way?"
        - "How does that compare to your past experiences?"
        - "What would need to change for you to feel differently?"
        - "Can you give me a specific example?"
        
        Remember to stay curious, non-judgmental, and focused on the research objectives.
        Create a welcoming environment where all participants feel comfortable sharing.
        """.strip()
    
    def generate_follow_up_questions(self, participant_response: str, context: str = "") -> List[str]:
        """Generate contextual follow-up questions based on participant response."""
        # This would integrate with AI service to generate contextual follow-ups
        # For now, return template follow-ups that can be customized
        
        templates = [
            f"That's interesting - can you elaborate on what you mean by that?",
            f"What experiences have shaped that perspective?", 
            f"How does that impact your daily life?",
            f"Can you give me a specific example?",
            f"What would make you feel differently about this?"
        ]
        
        # Return random selection based on range
        import random
        num_questions = random.randint(*self.follow_up_count_range)
        return templates[:num_questions]
    
    def to_dict(self) -> Dict:
        """Convert facilitator to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'expertise_area': self.expertise_area,
            'moderation_style': self.moderation_style,
            'questioning_approach': self.questioning_approach,
            'tone': self.tone,
            'primary_questions': self.primary_questions,
            'follow_up_count_range': self.follow_up_count_range,
            'base_instructions': self.base_instructions,
            'research_context': self.research_context,
            'objectives': self.objectives,
            'encourage_discussion': self.encourage_discussion,
            'manage_time': self.manage_time,
            'handle_conflicts': self.handle_conflicts,
            'synthesize_responses': self.synthesize_responses,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'active': self.active
        }
    
    @classmethod  
    def from_dict(cls, data: Dict) -> 'Facilitator':
        """Create facilitator from dictionary."""
        # Handle datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Handle tuple field
        if 'follow_up_count_range' in data and isinstance(data['follow_up_count_range'], list):
            data['follow_up_count_range'] = tuple(data['follow_up_count_range'])
            
        return cls(**data)
    
    def update_instructions(self) -> None:
        """Update the facilitator instructions and timestamp."""
        self.base_instructions = self._generate_default_instructions()
        self.updated_at = datetime.now()