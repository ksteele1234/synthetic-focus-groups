"""
JSON Schema contracts for detailed persona data structures.
Enforces validation for all 65 fields across 11 sections.
"""

import jsonschema
from typing import Dict, Any, List
import json

# Comprehensive JSON Schema for Enhanced Detailed Personas
DETAILED_PERSONA_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Detailed Persona Schema",
    "description": "Schema for comprehensive 11-section buyer personas with 65 fields",
    "type": "object",
    "required": [
        "id", "name", "age", "gender", "education", "relationship_family", 
        "occupation", "annual_income", "location", "persona_summary"
    ],
    "properties": {
        # Core Identity (Required)
        "id": {
            "type": "string",
            "description": "Unique identifier for the persona",
            "pattern": "^[a-fA-F0-9-]{36}$"  # UUID format
        },
        "name": {
            "type": "string",
            "description": "Full name of the persona",
            "minLength": 2,
            "maxLength": 100
        },
        "age": {
            "type": "integer",
            "description": "Age of the persona",
            "minimum": 18,
            "maximum": 80
        },
        "gender": {
            "type": "string",
            "description": "Gender identity",
            "enum": ["Male", "Female", "Non-binary", "Prefer not to specify", ""]
        },
        
        # Section 1: Buyer Avatar Basics
        "education": {
            "type": "string",
            "description": "Highest level of education and certifications",
            "maxLength": 200
        },
        "relationship_family": {
            "type": "string", 
            "description": "Marital status, children, family dynamics",
            "maxLength": 300
        },
        "occupation": {
            "type": "string",
            "description": "Current job title and company type",
            "maxLength": 200
        },
        "annual_income": {
            "type": "string",
            "description": "Income range or specific amount with goals",
            "maxLength": 100
        },
        "location": {
            "type": "string",
            "description": "City, state/province, country",
            "maxLength": 100
        },
        
        # Section 2: Psychographics & Lifestyle
        "hobbies": {
            "type": "array",
            "description": "List of hobbies and interests",
            "items": {
                "type": "string",
                "maxLength": 100
            },
            "maxItems": 20
        },
        "community_involvement": {
            "type": "array",
            "description": "Groups, associations, volunteer work",
            "items": {
                "type": "string",
                "maxLength": 150
            },
            "maxItems": 15
        },
        "personality_traits": {
            "type": "array",
            "description": "Key personality characteristics",
            "items": {
                "type": "string",
                "maxLength": 50
            },
            "maxItems": 20
        },
        "values": {
            "type": "array",
            "description": "Core values and guiding principles",
            "items": {
                "type": "string",
                "maxLength": 100
            },
            "maxItems": 15
        },
        "free_time_activities": {
            "type": "string",
            "description": "How they spend time outside of work",
            "maxLength": 500
        },
        "lifestyle_description": {
            "type": "string",
            "description": "General overview of day-to-day lifestyle",
            "maxLength": 1000
        },
        
        # Section 3: Pains & Challenges
        "major_struggles": {
            "type": "array",
            "description": "5+ biggest challenges they face",
            "items": {
                "type": "string",
                "maxLength": 300
            },
            "maxItems": 20
        },
        "obstacles": {
            "type": "array",
            "description": "Specific barriers they encounter",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 15
        },
        "why_problems_exist": {
            "type": "string",
            "description": "Root causes of their challenges and struggles",
            "maxLength": 1000
        },
        
        # Section 4: Fears & Relationship Impact
        "deep_fears_business": {
            "type": "array",
            "description": "5+ worst business-related fears",
            "items": {
                "type": "string",
                "maxLength": 300
            },
            "maxItems": 20
        },
        "deep_fears_personal": {
            "type": "array",
            "description": "Personal vulnerabilities and fears",
            "items": {
                "type": "string",
                "maxLength": 300
            },
            "maxItems": 15
        },
        "fear_impact_spouse": {
            "type": "string",
            "description": "How fears affect spouse/partner relationship",
            "maxLength": 500
        },
        "fear_impact_kids": {
            "type": "string",
            "description": "How fears affect children",
            "maxLength": 500
        },
        "fear_impact_employees": {
            "type": "string",
            "description": "How fears affect employees/team",
            "maxLength": 500
        },
        "fear_impact_peers": {
            "type": "string",
            "description": "How fears affect peer relationships",
            "maxLength": 500
        },
        "fear_impact_clients": {
            "type": "string",
            "description": "How fears affect client relationships",
            "maxLength": 500
        },
        "potential_remarks_from_others": {
            "type": "array",
            "description": "What critics or others might say about them",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 10
        },
        
        # Section 5: Previous Attempts & Frustrations
        "previous_agencies_tried": {
            "type": "array",
            "description": "Agencies or consultants they've worked with",
            "items": {
                "type": "string",
                "maxLength": 100
            },
            "maxItems": 15
        },
        "previous_software_tried": {
            "type": "array",
            "description": "Software/tools they've tried",
            "items": {
                "type": "string",
                "maxLength": 100
            },
            "maxItems": 25
        },
        "diy_approaches_tried": {
            "type": "array",
            "description": "DIY approaches they've attempted",
            "items": {
                "type": "string",
                "maxLength": 150
            },
            "maxItems": 15
        },
        "why_agencies_failed": {
            "type": "string",
            "description": "Why previous agencies didn't work out",
            "maxLength": 1000
        },
        "why_software_failed": {
            "type": "string",
            "description": "Why previous software/tools failed them",
            "maxLength": 1000
        },
        "why_diy_failed": {
            "type": "string",
            "description": "Why DIY approaches didn't work",
            "maxLength": 1000
        },
        
        # Section 6: Desired Outcomes (Practical & Emotional)
        "tangible_business_results": {
            "type": "array",
            "description": "Specific measurable business outcomes desired",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 20
        },
        "tangible_personal_results": {
            "type": "array",
            "description": "Specific personal improvements desired",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 15
        },
        "emotional_transformations": {
            "type": "array",
            "description": "How they want to feel differently",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 15
        },
        "if_only_soundbites": {
            "type": "array",
            "description": "Signature desire phrases starting with 'If only I could...'",
            "items": {
                "type": "string",
                "maxLength": 500
            },
            "maxItems": 10
        },
        
        # Section 7: Hopes & Dreams
        "professional_recognition_goals": {
            "type": "array",
            "description": "Desired professional accolades and recognition",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 15
        },
        "financial_freedom_goals": {
            "type": "array",
            "description": "Financial objectives and targets",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 15
        },
        "lifestyle_upgrade_goals": {
            "type": "array",
            "description": "Desired lifestyle improvements",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 15
        },
        "family_legacy_goals": {
            "type": "array",
            "description": "Long-term legacy and family objectives",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 10
        },
        "big_picture_aspirations": {
            "type": "string",
            "description": "Overall life and career aspirations",
            "maxLength": 2000
        },
        
        # Section 8: How They Want to Be Seen by Others
        "desired_reputation": {
            "type": "array",
            "description": "How they want to be perceived by others",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 10
        },
        "success_statements_from_others": {
            "type": "array",
            "description": "What they want others to say about them",
            "items": {
                "type": "string",
                "maxLength": 300
            },
            "maxItems": 10
        },
        
        # Section 9: Unwanted Outcomes
        "things_to_avoid": {
            "type": "array",
            "description": "What they specifically want to avoid",
            "items": {
                "type": "string",
                "maxLength": 200
            },
            "maxItems": 15
        },
        "unwanted_quotes": {
            "type": "array",
            "description": "Things they never want to hear",
            "items": {
                "type": "string",
                "maxLength": 300
            },
            "maxItems": 10
        },
        
        # Section 10: Summary (Required)
        "persona_summary": {
            "type": "string",
            "description": "One-paragraph persona overview",
            "minLength": 50,
            "maxLength": 2000
        },
        
        # Section 11: Day-in-the-Life Scenario
        "ideal_day_scenario": {
            "type": "string",
            "description": "Hour-by-hour description of their ideal day",
            "maxLength": 5000
        },
        
        # Legacy fields (for backward compatibility)
        "interests": {
            "type": "array",
            "description": "Legacy field - maps to hobbies",
            "items": {
                "type": "string",
                "maxLength": 100
            }
        },
        "income_level": {
            "type": "string",
            "description": "Legacy field - maps to annual_income",
            "maxLength": 100
        },
        "education_level": {
            "type": "string",
            "description": "Legacy field - maps to education",
            "maxLength": 200
        },
        "lifestyle": {
            "type": "string",
            "description": "Legacy field - maps to lifestyle_description",
            "maxLength": 1000
        },
        "background_story": {
            "type": "string",
            "description": "Legacy field - maps to persona_summary",
            "maxLength": 2000
        },
        "relevant_experiences": {
            "type": "array",
            "description": "Legacy field - relevant past experiences",
            "items": {
                "type": "string",
                "maxLength": 200
            }
        },
        "pain_points": {
            "type": "array",
            "description": "Legacy field - maps to major_struggles",
            "items": {
                "type": "string",
                "maxLength": 300
            }
        },
        "goals": {
            "type": "array",
            "description": "Legacy field - maps to tangible_business_results",
            "items": {
                "type": "string",
                "maxLength": 200
            }
        },
        
        # Behavioral patterns
        "communication_style": {
            "type": "string",
            "description": "Communication style preference",
            "enum": ["verbose", "concise", "balanced"],
            "default": "balanced"
        },
        "response_tendency": {
            "type": "string", 
            "description": "General response tendency",
            "enum": ["agreeable", "contrarian", "honest"],
            "default": "honest"
        },
        "emotional_expression": {
            "type": "string",
            "description": "Level of emotional expression",
            "enum": ["high", "moderate", "low"],
            "default": "moderate"
        },
        "preferred_communication_style": {
            "type": "string",
            "description": "How they like to be communicated with",
            "maxLength": 200
        },
        "tech_comfort_level": {
            "type": "string",
            "description": "Comfort level with technology",
            "enum": ["high", "moderate", "low"],
            "default": "moderate"
        },
        
        # System fields
        "base_personality_prompt": {
            "type": "string",
            "description": "Generated AI personality prompt",
            "maxLength": 10000
        },
        "context_instructions": {
            "type": "string",
            "description": "Additional context instructions",
            "maxLength": 2000
        },
        "created_at": {
            "type": "string",
            "description": "Creation timestamp",
            "format": "date-time"
        },
        "updated_at": {
            "type": "string",
            "description": "Last update timestamp", 
            "format": "date-time"
        },
        "active": {
            "type": "boolean",
            "description": "Whether persona is active",
            "default": True
        }
    },
    "additionalProperties": False
}

# Simplified schema for basic persona validation (backward compatibility)
BASIC_PERSONA_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Basic Persona Schema",
    "description": "Minimal schema for basic persona validation",
    "type": "object",
    "required": ["id", "name", "age", "occupation"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string", "minLength": 2},
        "age": {"type": "integer", "minimum": 18, "maximum": 80},
        "gender": {"type": "string"},
        "occupation": {"type": "string", "minLength": 2},
        "location": {"type": "string"},
        "personality_traits": {"type": "array", "items": {"type": "string"}},
        "interests": {"type": "array", "items": {"type": "string"}},
        "pain_points": {"type": "array", "items": {"type": "string"}},
        "goals": {"type": "array", "items": {"type": "string"}},
        "communication_style": {"type": "string"},
        "active": {"type": "boolean", "default": True}
    },
    "additionalProperties": True  # Allow additional fields for flexibility
}

# Session persona schema (for runtime session data)
SESSION_PERSONA_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Session Persona Schema",
    "description": "Schema for persona data used in synthetic sessions",
    "type": "object",
    "required": ["persona_id", "name", "role", "age", "occupation"],
    "properties": {
        "persona_id": {"type": "string"},
        "name": {"type": "string"},
        "role": {"type": "string"}, 
        "age": {"type": "integer"},
        "occupation": {"type": "string"},
        "background": {"type": "string"},
        "personality_traits": {"type": "array", "items": {"type": "string"}},
        "interests": {"type": "array", "items": {"type": "string"}},
        "pain_points": {"type": "array", "items": {"type": "string"}},
        "goals": {"type": "array", "items": {"type": "string"}},
        "communication_style": {"type": "string"},
        "detailed_context": {"type": "string"}  # Full persona prompt
    },
    "additionalProperties": False
}


class PersonaSchemaValidator:
    """Validator class for persona schema enforcement."""
    
    def __init__(self):
        """Initialize validator with compiled schemas."""
        self.detailed_validator = jsonschema.Draft7Validator(DETAILED_PERSONA_SCHEMA)
        self.basic_validator = jsonschema.Draft7Validator(BASIC_PERSONA_SCHEMA)
        self.session_validator = jsonschema.Draft7Validator(SESSION_PERSONA_SCHEMA)
    
    def validate_detailed_persona(self, persona_data: Dict[str, Any]) -> List[str]:
        """
        Validate a detailed persona against the comprehensive schema.
        
        Args:
            persona_data: Dictionary containing persona data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            self.detailed_validator.validate(persona_data)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message} at path: {'.'.join(str(p) for p in e.path)}")
        
        # Additional business logic validation
        errors.extend(self._validate_business_rules(persona_data))
        
        return errors
    
    def validate_basic_persona(self, persona_data: Dict[str, Any]) -> List[str]:
        """
        Validate a basic persona (backward compatibility).
        
        Args:
            persona_data: Dictionary containing persona data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            self.basic_validator.validate(persona_data)
        except jsonschema.ValidationError as e:
            errors.append(f"Basic validation failed: {e.message}")
        
        return errors
    
    def validate_session_persona(self, persona_data: Dict[str, Any]) -> List[str]:
        """
        Validate a session persona format.
        
        Args:
            persona_data: Dictionary containing session persona data
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            self.session_validator.validate(persona_data)
        except jsonschema.ValidationError as e:
            errors.append(f"Session validation failed: {e.message}")
        
        return errors
    
    def _validate_business_rules(self, persona_data: Dict[str, Any]) -> List[str]:
        """
        Validate business logic rules for detailed personas.
        
        Args:
            persona_data: Dictionary containing persona data
            
        Returns:
            List of business rule validation errors
        """
        errors = []
        
        # Check that essential lists have content
        essential_lists = [
            ('major_struggles', 'at least 3 major struggles'),
            ('deep_fears_business', 'at least 2 business fears'),
            ('personality_traits', 'at least 3 personality traits'),
            ('tangible_business_results', 'at least 2 desired business results')
        ]
        
        for field_name, requirement in essential_lists:
            field_value = persona_data.get(field_name, [])
            if isinstance(field_value, list):
                min_count = 2 if 'fears' in field_name or 'results' in field_name else 3
                if len(field_value) < min_count:
                    errors.append(f"Business rule violation: {field_name} should have {requirement}")
        
        # Check persona summary quality
        summary = persona_data.get('persona_summary', '')
        if summary and len(summary) < 100:
            errors.append("Business rule violation: persona_summary should be at least 100 characters for detailed personas")
        
        # Check if_only_soundbites format
        soundbites = persona_data.get('if_only_soundbites', [])
        for i, soundbite in enumerate(soundbites):
            if not soundbite.lower().startswith('if only'):
                errors.append(f"Business rule violation: if_only_soundbites[{i}] should start with 'If only'")
        
        # Validate age consistency
        age = persona_data.get('age')
        occupation = persona_data.get('occupation', '').lower()
        if age and age < 22 and any(word in occupation for word in ['senior', 'manager', 'director', 'owner', 'ceo']):
            errors.append(f"Business rule violation: Age {age} seems inconsistent with senior occupation '{occupation}'")
        
        return errors
    
    def validate_persona_collection(self, personas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a collection of personas.
        
        Args:
            personas: List of persona dictionaries
            
        Returns:
            Validation results with summary and detailed errors
        """
        results = {
            'total_personas': len(personas),
            'valid_personas': 0,
            'invalid_personas': 0,
            'total_errors': 0,
            'persona_results': []
        }
        
        for i, persona in enumerate(personas):
            errors = self.validate_detailed_persona(persona)
            persona_result = {
                'index': i,
                'name': persona.get('name', f'Persona {i}'),
                'valid': len(errors) == 0,
                'errors': errors,
                'error_count': len(errors)
            }
            
            results['persona_results'].append(persona_result)
            results['total_errors'] += len(errors)
            
            if len(errors) == 0:
                results['valid_personas'] += 1
            else:
                results['invalid_personas'] += 1
        
        return results


def validate_persona_file(file_path: str) -> Dict[str, Any]:
    """
    Validate a JSON file containing persona data.
    
    Args:
        file_path: Path to JSON file containing persona data
        
    Returns:
        Validation results
    """
    validator = PersonaSchemaValidator()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle single persona or array of personas
        if isinstance(data, dict):
            # Single persona
            errors = validator.validate_detailed_persona(data)
            return {
                'file_path': file_path,
                'valid': len(errors) == 0,
                'errors': errors,
                'persona_count': 1,
                'total_errors': len(errors)
            }
        elif isinstance(data, list):
            # Array of personas
            return {
                'file_path': file_path,
                **validator.validate_persona_collection(data)
            }
        else:
            return {
                'file_path': file_path,
                'valid': False,
                'errors': ['Invalid file format: expected object or array'],
                'persona_count': 0,
                'total_errors': 1
            }
            
    except FileNotFoundError:
        return {
            'file_path': file_path,
            'valid': False, 
            'errors': ['File not found'],
            'persona_count': 0,
            'total_errors': 1
        }
    except json.JSONDecodeError as e:
        return {
            'file_path': file_path,
            'valid': False,
            'errors': [f'Invalid JSON: {e}'],
            'persona_count': 0,
            'total_errors': 1
        }
    except Exception as e:
        return {
            'file_path': file_path,
            'valid': False,
            'errors': [f'Validation error: {e}'],
            'persona_count': 0,
            'total_errors': 1
        }


# Export main schemas and validator
__all__ = [
    'DETAILED_PERSONA_SCHEMA',
    'BASIC_PERSONA_SCHEMA', 
    'SESSION_PERSONA_SCHEMA',
    'PersonaSchemaValidator',
    'validate_persona_file'
]