"""
Persona model for individual AI participants in focus groups.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import json
import jsonschema


@dataclass
class Persona:
    """Represents an AI persona participating in focus groups with detailed buyer persona characteristics."""
    
    # 1. Buyer Avatar Basics
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    age: int = 25
    gender: str = ""
    education: str = ""  # Highest degree/training
    relationship_family: str = ""  # Marital status, kids, etc.
    occupation: str = ""
    annual_income: str = ""  # Annual income
    location: str = ""  # City, state/country
    
    # 2. Psychographics & Lifestyle
    hobbies: List[str] = field(default_factory=list)
    community_involvement: List[str] = field(default_factory=list)
    personality_traits: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    free_time_activities: str = ""
    lifestyle_description: str = ""
    
    # 3. Pains & Challenges
    major_struggles: List[str] = field(default_factory=list)
    obstacles: List[str] = field(default_factory=list)
    why_problems_exist: str = ""
    
    # 4. Fears & Relationship Impact
    deep_fears_business: List[str] = field(default_factory=list)
    deep_fears_personal: List[str] = field(default_factory=list)
    fear_impact_spouse: str = ""
    fear_impact_kids: str = ""
    fear_impact_employees: str = ""
    fear_impact_peers: str = ""
    fear_impact_clients: str = ""
    potential_remarks_from_others: List[str] = field(default_factory=list)
    
    # 5. Previous Attempts & Frustrations
    previous_agencies_tried: List[str] = field(default_factory=list)
    previous_software_tried: List[str] = field(default_factory=list)
    diy_approaches_tried: List[str] = field(default_factory=list)
    why_agencies_failed: str = ""
    why_software_failed: str = ""
    why_diy_failed: str = ""
    
    # 6. Desired Outcomes (Practical & Emotional)
    tangible_business_results: List[str] = field(default_factory=list)
    tangible_personal_results: List[str] = field(default_factory=list)
    emotional_transformations: List[str] = field(default_factory=list)
    if_only_soundbites: List[str] = field(default_factory=list)  # "If only I could... it would mean..."
    
    # 7. Hopes & Dreams
    professional_recognition_goals: List[str] = field(default_factory=list)
    financial_freedom_goals: List[str] = field(default_factory=list)
    lifestyle_upgrade_goals: List[str] = field(default_factory=list)
    family_legacy_goals: List[str] = field(default_factory=list)
    big_picture_aspirations: str = ""
    
    # 8. How They Want to Be Seen by Others
    desired_reputation: List[str] = field(default_factory=list)
    success_statements_from_others: List[str] = field(default_factory=list)  # What others might say about them
    
    # 9. Unwanted Outcomes
    things_to_avoid: List[str] = field(default_factory=list)
    unwanted_quotes: List[str] = field(default_factory=list)  # In their voice
    
    # 10. Summary (computed from above)
    persona_summary: str = ""
    
    # 11. Day-in-the-Life Scenario
    ideal_day_scenario: str = ""  # Hour-by-hour after solving problems
    
    # Legacy fields for backward compatibility
    interests: List[str] = field(default_factory=list)  # Maps to hobbies
    income_level: str = ""  # Maps to annual_income
    education_level: str = ""  # Maps to education
    lifestyle: str = ""  # Maps to lifestyle_description
    background_story: str = ""  # Maps to persona_summary
    relevant_experiences: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)  # Maps to major_struggles
    goals: List[str] = field(default_factory=list)  # Maps to tangible_business_results
    
    # Behavioral patterns
    communication_style: str = "balanced"  # verbose, concise, balanced
    response_tendency: str = "honest"  # agreeable, contrarian, honest
    emotional_expression: str = "moderate"  # high, moderate, low
    preferred_communication_style: str = ""  # How they like to be communicated with
    tech_comfort_level: str = "moderate"  # high, moderate, low
    
    # System prompts
    base_personality_prompt: str = ""
    context_instructions: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    active: bool = True
    
    def __post_init__(self):
        """Initialize persona with default personality prompt if not provided."""
        # Map legacy fields for backward compatibility
        if not self.income_level and self.annual_income:
            self.income_level = self.annual_income
        if not self.education_level and self.education:
            self.education_level = self.education
        if not self.lifestyle and self.lifestyle_description:
            self.lifestyle = self.lifestyle_description
        if not self.background_story and self.persona_summary:
            self.background_story = self.persona_summary
        if not self.interests and self.hobbies:
            self.interests = self.hobbies
        if not self.pain_points and self.major_struggles:
            self.pain_points = self.major_struggles
        if not self.goals and self.tangible_business_results:
            self.goals = self.tangible_business_results
            
        # Generate summary if not provided
        if not self.persona_summary:
            self.persona_summary = self._generate_persona_summary()
            
        if not self.base_personality_prompt:
            self.base_personality_prompt = self._generate_detailed_prompt()
    
    def _generate_persona_summary(self) -> str:
        """Generate a concise persona summary."""
        summary_parts = []
        
        # Demographics
        demo = f"{self.name} is a {self.age}-year-old {self.gender} {self.occupation} from {self.location}"
        if self.relationship_family:
            demo += f", {self.relationship_family}"
        summary_parts.append(demo + ".")
        
        # Key challenges
        if self.major_struggles:
            challenges = f"Key challenges include {', '.join(self.major_struggles[:2])}"
            summary_parts.append(challenges + ".")
        
        # Goals and motivations
        if self.tangible_business_results:
            goals = f"Primary goals are {', '.join(self.tangible_business_results[:2])}"
            summary_parts.append(goals + ".")
        
        # Personality
        if self.personality_traits:
            personality = f"Personality: {', '.join(self.personality_traits[:3])}"
            summary_parts.append(personality + ".")
            
        return " ".join(summary_parts)
    
    def _generate_detailed_prompt(self) -> str:
        """Generate a detailed personality prompt based on all persona attributes."""
        traits_str = ", ".join(self.personality_traits) if self.personality_traits else "thoughtful and authentic"
        values_str = ", ".join(self.values) if self.values else "integrity and growth"
        
        # Build comprehensive persona context
        context_parts = []
        
        # Basic identity
        context_parts.append(f"You are {self.name}, a {self.age}-year-old {self.gender} from {self.location}.")
        
        if self.relationship_family:
            context_parts.append(f"Personal life: {self.relationship_family}.")
            
        context_parts.append(f"You work as {self.occupation} and have {self.education or 'relevant'} education.")
        
        if self.annual_income:
            context_parts.append(f"Annual income: {self.annual_income}.")
        
        # Psychographics
        context_parts.append(f"Your personality is {traits_str}. You deeply value {values_str}.")
        
        if self.hobbies:
            context_parts.append(f"Hobbies and interests: {', '.join(self.hobbies)}.")
            
        if self.lifestyle_description:
            context_parts.append(f"Lifestyle: {self.lifestyle_description}")
        
        # Challenges and fears
        if self.major_struggles:
            context_parts.append(f"You struggle with: {', '.join(self.major_struggles)}.")
            
        if self.deep_fears_business or self.deep_fears_personal:
            fears = self.deep_fears_business + self.deep_fears_personal
            context_parts.append(f"Deep concerns: {', '.join(fears[:3])}.")
        
        # Goals and aspirations
        if self.tangible_business_results:
            context_parts.append(f"You want to achieve: {', '.join(self.tangible_business_results)}.")
            
        if self.emotional_transformations:
            context_parts.append(f"Emotionally, you hope to feel: {', '.join(self.emotional_transformations)}.")
        
        # Previous frustrations
        if self.previous_software_tried:
            context_parts.append(f"You've tried solutions like {', '.join(self.previous_software_tried[:2])} but they didn't work.")
        
        # Communication style
        context_parts.append(f"Your communication style is {self.communication_style} and you tend to be {self.response_tendency}.")
        context_parts.append(f"You express emotions in a {self.emotional_expression} way.")
        
        # Behavioral instructions
        context_parts.append("When participating in focus groups:")
        context_parts.append("- Stay true to this detailed persona while being helpful and engaging")
        context_parts.append("- Draw from your specific struggles, fears, and aspirations")
        context_parts.append("- Reference your past attempts and why they failed when relevant")
        context_parts.append("- Express both practical needs and emotional desires")
        context_parts.append("- Respond as this character would, considering their complete life context")
        
        if self.if_only_soundbites:
            context_parts.append(f"Use phrases like: {'; '.join(self.if_only_soundbites[:2])}")
        
        return "\n".join(context_parts)
    
    def _generate_default_prompt(self) -> str:
        """Legacy method - redirects to detailed prompt."""
        return self._generate_detailed_prompt()
    
    def to_dict(self) -> Dict:
        """Convert persona to dictionary for serialization."""
        return {
            # Basic identity
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'education': self.education,
            'relationship_family': self.relationship_family,
            'occupation': self.occupation,
            'annual_income': self.annual_income,
            'location': self.location,
            
            # Psychographics & Lifestyle
            'hobbies': self.hobbies,
            'community_involvement': self.community_involvement,
            'personality_traits': self.personality_traits,
            'values': self.values,
            'free_time_activities': self.free_time_activities,
            'lifestyle_description': self.lifestyle_description,
            
            # Pains & Challenges
            'major_struggles': self.major_struggles,
            'obstacles': self.obstacles,
            'why_problems_exist': self.why_problems_exist,
            
            # Fears & Relationship Impact
            'deep_fears_business': self.deep_fears_business,
            'deep_fears_personal': self.deep_fears_personal,
            'fear_impact_spouse': self.fear_impact_spouse,
            'fear_impact_kids': self.fear_impact_kids,
            'fear_impact_employees': self.fear_impact_employees,
            'fear_impact_peers': self.fear_impact_peers,
            'fear_impact_clients': self.fear_impact_clients,
            'potential_remarks_from_others': self.potential_remarks_from_others,
            
            # Previous Attempts & Frustrations
            'previous_agencies_tried': self.previous_agencies_tried,
            'previous_software_tried': self.previous_software_tried,
            'diy_approaches_tried': self.diy_approaches_tried,
            'why_agencies_failed': self.why_agencies_failed,
            'why_software_failed': self.why_software_failed,
            'why_diy_failed': self.why_diy_failed,
            
            # Desired Outcomes
            'tangible_business_results': self.tangible_business_results,
            'tangible_personal_results': self.tangible_personal_results,
            'emotional_transformations': self.emotional_transformations,
            'if_only_soundbites': self.if_only_soundbites,
            
            # Hopes & Dreams
            'professional_recognition_goals': self.professional_recognition_goals,
            'financial_freedom_goals': self.financial_freedom_goals,
            'lifestyle_upgrade_goals': self.lifestyle_upgrade_goals,
            'family_legacy_goals': self.family_legacy_goals,
            'big_picture_aspirations': self.big_picture_aspirations,
            
            # How They Want to Be Seen
            'desired_reputation': self.desired_reputation,
            'success_statements_from_others': self.success_statements_from_others,
            
            # Unwanted Outcomes
            'things_to_avoid': self.things_to_avoid,
            'unwanted_quotes': self.unwanted_quotes,
            
            # Summary & Day-in-the-Life
            'persona_summary': self.persona_summary,
            'ideal_day_scenario': self.ideal_day_scenario,
            
            # Legacy fields (for backward compatibility)
            'interests': self.interests,
            'income_level': self.income_level,
            'education_level': self.education_level,
            'lifestyle': self.lifestyle,
            'background_story': self.background_story,
            'relevant_experiences': self.relevant_experiences,
            'pain_points': self.pain_points,
            'goals': self.goals,
            
            # Behavioral patterns
            'communication_style': self.communication_style,
            'response_tendency': self.response_tendency,
            'emotional_expression': self.emotional_expression,
            'preferred_communication_style': self.preferred_communication_style,
            'tech_comfort_level': self.tech_comfort_level,
            
            # System fields
            'base_personality_prompt': self.base_personality_prompt,
            'context_instructions': self.context_instructions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'active': self.active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Persona':
        """Create persona from dictionary with optional validation."""
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
    
    def validate_schema(self, strict: bool = False) -> List[str]:
        """Validate persona against JSON schema.
        
        Args:
            strict: If True, use detailed schema. If False, use basic schema.
            
        Returns:
            List of validation errors (empty if valid)
        """
        try:
            from .persona_schema import PersonaSchemaValidator
            validator = PersonaSchemaValidator()
            
            persona_dict = self.to_dict()
            
            if strict:
                return validator.validate_detailed_persona(persona_dict)
            else:
                return validator.validate_basic_persona(persona_dict)
                
        except ImportError:
            # Fallback basic validation if schema module not available
            return self._validate_basic_fields()
    
    def _validate_basic_fields(self) -> List[str]:
        """Basic field validation without JSON schema."""
        errors = []
        
        if not self.name or len(self.name) < 2:
            errors.append("Name must be at least 2 characters")
        
        if not isinstance(self.age, int) or self.age < 18 or self.age > 80:
            errors.append("Age must be an integer between 18 and 80")
            
        if not self.occupation or len(self.occupation) < 2:
            errors.append("Occupation must be at least 2 characters")
        
        return errors
    
    def to_json_schema_dict(self) -> Dict:
        """Convert persona to dictionary that strictly follows JSON schema."""
        base_dict = self.to_dict()
        
        # Ensure UUID format for ID
        if not base_dict.get('id'):
            base_dict['id'] = str(uuid.uuid4())
        
        # Ensure required fields have values
        required_fields = {
            'name': self.name or 'Unknown',
            'age': self.age if isinstance(self.age, int) else 25,
            'gender': self.gender or '',
            'education': self.education or '',
            'relationship_family': self.relationship_family or '',
            'occupation': self.occupation or 'Professional',
            'annual_income': self.annual_income or '',
            'location': self.location or '',
            'persona_summary': self.persona_summary or self._generate_persona_summary()
        }
        
        for field, default_value in required_fields.items():
            if not base_dict.get(field):
                base_dict[field] = default_value
        
        # Ensure datetime fields are properly formatted
        if isinstance(base_dict.get('created_at'), str):
            # Already a string, ensure it's ISO format
            try:
                datetime.fromisoformat(base_dict['created_at'].replace('Z', '+00:00'))
            except ValueError:
                base_dict['created_at'] = datetime.now().isoformat()
        else:
            base_dict['created_at'] = datetime.now().isoformat()
            
        if isinstance(base_dict.get('updated_at'), str):
            try:
                datetime.fromisoformat(base_dict['updated_at'].replace('Z', '+00:00'))
            except ValueError:
                base_dict['updated_at'] = datetime.now().isoformat()
        else:
            base_dict['updated_at'] = datetime.now().isoformat()
        
        return base_dict
    
    def is_detailed_persona(self) -> bool:
        """Check if this persona has detailed information (11 sections)."""
        detailed_indicators = [
            len(self.major_struggles) >= 3,
            len(self.deep_fears_business) >= 2,
            len(self.tangible_business_results) >= 2,
            len(self.if_only_soundbites) >= 1,
            bool(self.big_picture_aspirations),
            bool(self.ideal_day_scenario),
            len(self.persona_summary) >= 100
        ]
        
        # Consider it detailed if at least 5 of 7 indicators are met
        return sum(detailed_indicators) >= 5
