"""
Enhanced persona manager with custom persona parsing and upload capabilities.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid

from models.persona import Persona


class PersonaParser:
    """Parses persona information from various formats and sources."""
    
    def __init__(self):
        """Initialize the persona parser."""
        self.extraction_patterns = {
            'name': [
                r'name:?\s*([^\n,]+)',
                r'called\s+([^\n,]+)',
                r'my name is\s+([^\n,]+)',
                r'^([A-Z][a-z]+ [A-Z][a-z]+)',
            ],
            'age': [
                r'age:?\s*(\d+)',
                r'(\d+)\s*years?\s*old',
                r'born in\s*(\d{4})',
            ],
            'gender': [
                r'gender:?\s*(male|female|non-binary|other)',
                r'identifies? as\s*(male|female|non-binary|other)',
                r'(he/him|she/her|they/them)',
            ],
            'occupation': [
                r'occupation:?\s*([^\n,]+)',
                r'works? as\s+([^\n,]+)',
                r'job:?\s*([^\n,]+)',
                r'profession:?\s*([^\n,]+)',
            ],
            'location': [
                r'location:?\s*([^\n,]+)',
                r'lives? in\s+([^\n,]+)',
                r'from\s+([^\n,]+)',
                r'based in\s+([^\n,]+)',
            ],
            'education': [
                r'education:?\s*([^\n,]+)',
                r'degree:?\s*([^\n,]+)',
                r'studied\s+([^\n,]+)',
                r'graduated from\s+([^\n,]+)',
            ],
            'income': [
                r'income:?\s*([^\n,]+)',
                r'salary:?\s*([^\n,]+)',
                r'earns?\s+([^\n,]+)',
                r'makes?\s+(\$[\d,]+)',
            ]
        }
    
    def parse_persona_text(self, text: str) -> Dict[str, Any]:
        """Parse persona information from free text."""
        persona_data = {}
        text_lower = text.lower()
        
        # Extract basic demographics
        for field, patterns in self.extraction_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    
                    # Post-process specific fields
                    if field == 'age':
                        try:
                            # Handle birth year conversion
                            age_value = int(value)
                            if age_value > 1900:  # Assume it's a birth year
                                current_year = datetime.now().year
                                age_value = current_year - age_value
                            persona_data['age'] = age_value
                        except ValueError:
                            continue
                    elif field == 'gender':
                        # Normalize gender pronouns
                        if 'he/him' in value:
                            persona_data['gender'] = 'male'
                        elif 'she/her' in value:
                            persona_data['gender'] = 'female'
                        elif 'they/them' in value:
                            persona_data['gender'] = 'non-binary'
                        else:
                            persona_data['gender'] = value.title()
                    else:
                        persona_data[field] = value.title()
                    break
        
        # Extract personality traits
        personality_keywords = [
            'outgoing', 'introverted', 'extroverted', 'analytical', 'creative', 
            'practical', 'optimistic', 'pessimistic', 'cautious', 'adventurous',
            'detail-oriented', 'big-picture', 'empathetic', 'logical', 'spontaneous',
            'organized', 'collaborative', 'independent', 'curious', 'traditional',
            'innovative', 'patient', 'energetic', 'calm', 'ambitious', 'humble'
        ]
        
        found_traits = []
        for trait in personality_keywords:
            if trait in text_lower:
                found_traits.append(trait)
        
        if found_traits:
            persona_data['personality_traits'] = found_traits
        
        # Extract interests
        interest_keywords = [
            'reading', 'cooking', 'traveling', 'fitness', 'music', 'movies',
            'gardening', 'technology', 'sports', 'art', 'photography', 'gaming',
            'hiking', 'crafts', 'volunteering', 'languages', 'fashion', 'yoga'
        ]
        
        found_interests = []
        for interest in interest_keywords:
            if interest in text_lower:
                found_interests.append(interest)
        
        if found_interests:
            persona_data['interests'] = found_interests
        
        # Extract background story (use full text if no specific background found)
        background_patterns = [
            r'background:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'story:?\s*([^\n]+(?:\n[^\n]+)*)',
            r'about:?\s*([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in background_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                persona_data['background_story'] = match.group(1).strip()
                break
        
        if 'background_story' not in persona_data:
            # Use the full text as background if no specific section found
            persona_data['background_story'] = text.strip()
        
        return persona_data
    
    def parse_structured_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse persona from structured data (JSON, dict, etc.)."""
        persona_data = {}
        
        # Map common field variations
        field_mappings = {
            'name': ['name', 'full_name', 'persona_name'],
            'age': ['age', 'years_old'],
            'gender': ['gender', 'sex'],
            'occupation': ['occupation', 'job', 'profession', 'work'],
            'location': ['location', 'city', 'address', 'where_they_live'],
            'education_level': ['education', 'education_level', 'degree'],
            'income_level': ['income', 'income_level', 'salary'],
            'personality_traits': ['personality', 'personality_traits', 'traits'],
            'interests': ['interests', 'hobbies', 'likes'],
            'values': ['values', 'beliefs'],
            'background_story': ['background', 'story', 'biography', 'bio', 'about']
        }
        
        for target_field, source_fields in field_mappings.items():
            for source_field in source_fields:
                if source_field in data:
                    value = data[source_field]
                    
                    # Handle list fields
                    if target_field in ['personality_traits', 'interests', 'values']:
                        if isinstance(value, str):
                            # Split comma-separated values
                            persona_data[target_field] = [v.strip() for v in value.split(',')]
                        elif isinstance(value, list):
                            persona_data[target_field] = value
                    else:
                        persona_data[target_field] = value
                    break
        
        return persona_data
    
    def parse_csv_row(self, row: Dict[str, str], field_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """Parse persona from CSV row with optional field mapping."""
        if field_mapping:
            # Apply custom field mapping
            mapped_row = {}
            for target_field, source_field in field_mapping.items():
                if source_field in row:
                    mapped_row[target_field] = row[source_field]
            return self.parse_structured_data(mapped_row)
        else:
            return self.parse_structured_data(row)


class EnhancedPersonaManager:
    """Enhanced persona manager with parsing and upload capabilities."""
    
    def __init__(self, storage_path: str = "data/personas"):
        """Initialize enhanced persona manager."""
        self.storage_path = storage_path
        self.personas_file = os.path.join(storage_path, "personas.json")
        self.personas: Dict[str, Persona] = {}
        self.parser = PersonaParser()
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing personas
        self._load_personas()
    
    def _load_personas(self) -> None:
        """Load personas from storage file."""
        if os.path.exists(self.personas_file):
            try:
                with open(self.personas_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for persona_data in data:
                        persona = Persona.from_dict(persona_data)
                        self.personas[persona.id] = persona
            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Could not load personas from {self.personas_file}: {e}")
    
    def _save_personas(self) -> None:
        """Save personas to storage file."""
        try:
            data = [persona.to_dict() for persona in self.personas.values()]
            with open(self.personas_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving personas to {self.personas_file}: {e}")
    
    def create_persona_from_text(self, text: str, **overrides) -> Persona:
        """Create a persona from free text description."""
        parsed_data = self.parser.parse_persona_text(text)
        
        # Apply overrides
        parsed_data.update(overrides)
        
        # Ensure we have a name
        if 'name' not in parsed_data:
            parsed_data['name'] = f"Persona_{len(self.personas) + 1}"
        
        persona = Persona(**parsed_data)
        self.personas[persona.id] = persona
        self._save_personas()
        return persona
    
    def create_persona_from_data(self, data: Dict[str, Any], **overrides) -> Persona:
        """Create a persona from structured data."""
        parsed_data = self.parser.parse_structured_data(data)
        
        # Apply overrides
        parsed_data.update(overrides)
        
        # Ensure we have a name
        if 'name' not in parsed_data:
            parsed_data['name'] = f"Persona_{len(self.personas) + 1}"
        
        persona = Persona(**parsed_data)
        self.personas[persona.id] = persona
        self._save_personas()
        return persona
    
    def upload_personas_from_file(self, filepath: str, file_type: str = "auto", 
                                field_mapping: Dict[str, str] = None) -> List[Persona]:
        """Upload personas from various file formats."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Auto-detect file type
        if file_type == "auto":
            extension = os.path.splitext(filepath)[1].lower()
            if extension == ".json":
                file_type = "json"
            elif extension == ".csv":
                file_type = "csv"
            elif extension == ".txt":
                file_type = "text"
            else:
                raise ValueError(f"Unsupported file type: {extension}")
        
        personas = []
        
        try:
            if file_type == "json":
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    # Array of personas
                    for item in data:
                        persona = self.create_persona_from_data(item)
                        personas.append(persona)
                elif isinstance(data, dict):
                    # Single persona
                    persona = self.create_persona_from_data(data)
                    personas.append(persona)
            
            elif file_type == "csv":
                import csv
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        parsed_data = self.parser.parse_csv_row(row, field_mapping)
                        persona = self.create_persona_from_data(parsed_data)
                        personas.append(persona)
            
            elif file_type == "text":
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split by double newlines for multiple personas
                persona_texts = re.split(r'\n\s*\n', content)
                for text in persona_texts:
                    if text.strip():
                        persona = self.create_persona_from_text(text.strip())
                        personas.append(persona)
        
        except Exception as e:
            raise Exception(f"Error processing file {filepath}: {e}")
        
        return personas
    
    def bulk_create_personas(self, personas_data: List[Union[str, Dict[str, Any]]]) -> List[Persona]:
        """Create multiple personas from mixed data types."""
        personas = []
        
        for data in personas_data:
            if isinstance(data, str):
                persona = self.create_persona_from_text(data)
            elif isinstance(data, dict):
                persona = self.create_persona_from_data(data)
            else:
                continue  # Skip invalid data
            
            personas.append(persona)
        
        return personas
    
    def enhance_persona_with_ai(self, persona_id: str, enhancement_prompt: str = None) -> bool:
        """Enhance a persona's profile using AI (placeholder for future implementation)."""
        persona = self.get_persona(persona_id)
        if not persona:
            return False
        
        # Placeholder for AI enhancement
        # This would call OpenAI API to enhance the persona based on existing data
        # For now, we'll just update the timestamp
        persona.updated_at = datetime.now()
        self._save_personas()
        return True
    
    def validate_persona_completeness(self, persona_id: str) -> Dict[str, Any]:
        """Validate and score persona completeness."""
        persona = self.get_persona(persona_id)
        if not persona:
            return {'valid': False, 'error': 'Persona not found'}
        
        required_fields = ['name', 'age', 'occupation']
        recommended_fields = [
            'gender', 'location', 'education_level', 'personality_traits', 
            'interests', 'background_story'
        ]
        
        completeness_score = 0
        missing_required = []
        missing_recommended = []
        
        # Check required fields
        for field in required_fields:
            value = getattr(persona, field, None)
            if value and str(value).strip():
                completeness_score += 20  # 60 points total for required
            else:
                missing_required.append(field)
        
        # Check recommended fields
        for field in recommended_fields:
            value = getattr(persona, field, None)
            if value:
                if isinstance(value, list) and len(value) > 0:
                    completeness_score += 7  # 42 points total for recommended
                elif isinstance(value, str) and value.strip():
                    completeness_score += 7
            else:
                missing_recommended.append(field)
        
        return {
            'valid': len(missing_required) == 0,
            'completeness_score': min(completeness_score, 100),
            'missing_required': missing_required,
            'missing_recommended': missing_recommended,
            'suggestions': self._generate_enhancement_suggestions(persona)
        }
    
    def _generate_enhancement_suggestions(self, persona: Persona) -> List[str]:
        """Generate suggestions for enhancing a persona."""
        suggestions = []
        
        if not persona.personality_traits:
            suggestions.append("Add personality traits to make the persona more realistic")
        
        if not persona.interests:
            suggestions.append("Add interests and hobbies to provide conversation topics")
        
        if not persona.background_story or len(persona.background_story) < 50:
            suggestions.append("Expand background story for richer context")
        
        if not persona.relevant_experiences:
            suggestions.append("Add relevant experiences related to the research topic")
        
        if not persona.values:
            suggestions.append("Define personal values that drive decision-making")
        
        return suggestions
    
    # Include all original PersonaManager methods
    def create_persona(self, **kwargs) -> Persona:
        """Create a new persona with provided attributes."""
        persona = Persona(**kwargs)
        self.personas[persona.id] = persona
        self._save_personas()
        return persona
    
    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get a persona by ID."""
        return self.personas.get(persona_id)
    
    def get_all_personas(self, active_only: bool = True) -> List[Persona]:
        """Get all personas, optionally filtering to active ones only."""
        personas = list(self.personas.values())
        if active_only:
            personas = [p for p in personas if p.active]
        return personas
    
    def update_persona(self, persona_id: str, **kwargs) -> Optional[Persona]:
        """Update a persona with new attributes."""
        persona = self.get_persona(persona_id)
        if not persona:
            return None
        
        # Update attributes
        for key, value in kwargs.items():
            if hasattr(persona, key):
                setattr(persona, key, value)
        
        # Update timestamp and regenerate prompt if needed
        persona.updated_at = datetime.now()
        if any(key in kwargs for key in ['name', 'age', 'personality_traits', 'background_story']):
            persona.update_prompt()
        
        self._save_personas()
        return persona
    
    def delete_persona(self, persona_id: str) -> bool:
        """Delete a persona by ID."""
        if persona_id in self.personas:
            del self.personas[persona_id]
            self._save_personas()
            return True
        return False