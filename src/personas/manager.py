"""
Persona manager for CRUD operations and persona storage.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from models.persona import Persona


class PersonaManager:
    """Manages personas with file-based storage and CRUD operations."""
    
    def __init__(self, storage_path: str = "data/personas"):
        """Initialize persona manager with storage path."""
        self.storage_path = storage_path
        self.personas_file = os.path.join(storage_path, "personas.json")
        self.personas: Dict[str, Persona] = {}
        
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
    
    def deactivate_persona(self, persona_id: str) -> bool:
        """Deactivate a persona (soft delete)."""
        persona = self.get_persona(persona_id)
        if persona:
            persona.active = False
            persona.updated_at = datetime.now()
            self._save_personas()
            return True
        return False
    
    def activate_persona(self, persona_id: str) -> bool:
        """Activate a persona."""
        persona = self.get_persona(persona_id)
        if persona:
            persona.active = True
            persona.updated_at = datetime.now()
            self._save_personas()
            return True
        return False
    
    def search_personas(self, query: str, search_fields: List[str] = None) -> List[Persona]:
        """Search personas by query string in specified fields."""
        if search_fields is None:
            search_fields = ['name', 'occupation', 'personality_traits', 'interests']
        
        query_lower = query.lower()
        results = []
        
        for persona in self.get_all_personas():
            for field in search_fields:
                if field == 'personality_traits' or field == 'interests':
                    # Handle list fields
                    field_value = getattr(persona, field, [])
                    if any(query_lower in trait.lower() for trait in field_value):
                        results.append(persona)
                        break
                else:
                    # Handle string fields
                    field_value = getattr(persona, field, "")
                    if query_lower in field_value.lower():
                        results.append(persona)
                        break
        
        return results
    
    def filter_personas(self, filters: Dict[str, Any]) -> List[Persona]:
        """Filter personas by specified criteria."""
        personas = self.get_all_personas()
        
        for key, value in filters.items():
            if not hasattr(Persona, key):
                continue
                
            if isinstance(value, list):
                # Filter by list membership (for fields like personality_traits)
                personas = [p for p in personas if any(v in getattr(p, key, []) for v in value)]
            elif isinstance(value, str):
                # Filter by string match
                personas = [p for p in personas if value.lower() in getattr(p, key, "").lower()]
            else:
                # Filter by exact match
                personas = [p for p in personas if getattr(p, key, None) == value]
        
        return personas
    
    def get_personas_by_demographics(self, age_range: tuple = None, gender: str = None, 
                                   location: str = None, occupation: str = None) -> List[Persona]:
        """Get personas filtered by demographic criteria."""
        personas = self.get_all_personas()
        
        if age_range:
            min_age, max_age = age_range
            personas = [p for p in personas if min_age <= p.age <= max_age]
        
        if gender:
            personas = [p for p in personas if p.gender.lower() == gender.lower()]
        
        if location:
            personas = [p for p in personas if location.lower() in p.location.lower()]
        
        if occupation:
            personas = [p for p in personas if occupation.lower() in p.occupation.lower()]
        
        return personas
    
    def get_diverse_sample(self, count: int = 10, diversity_fields: List[str] = None) -> List[Persona]:
        """Get a diverse sample of personas based on specified fields."""
        if diversity_fields is None:
            diversity_fields = ['age', 'gender', 'occupation', 'location']
        
        all_personas = self.get_all_personas()
        if len(all_personas) <= count:
            return all_personas
        
        # Simple diversity sampling - aim for variety in specified fields
        selected = []
        used_values = {field: set() for field in diversity_fields}
        
        # Sort personas randomly to avoid bias
        import random
        shuffled_personas = all_personas.copy()
        random.shuffle(shuffled_personas)
        
        # First pass: select personas that add new diversity
        for persona in shuffled_personas:
            if len(selected) >= count:
                break
                
            adds_diversity = False
            for field in diversity_fields:
                value = getattr(persona, field, "")
                if value not in used_values[field]:
                    adds_diversity = True
                    break
            
            if adds_diversity or len(selected) == 0:
                selected.append(persona)
                for field in diversity_fields:
                    value = getattr(persona, field, "")
                    used_values[field].add(value)
        
        # Second pass: fill remaining slots if needed
        remaining = [p for p in shuffled_personas if p not in selected]
        while len(selected) < count and remaining:
            selected.append(remaining.pop(0))
        
        return selected[:count]
    
    def export_personas(self, filepath: str, persona_ids: List[str] = None) -> bool:
        """Export personas to a file."""
        try:
            if persona_ids:
                personas_to_export = [self.get_persona(pid) for pid in persona_ids if self.get_persona(pid)]
            else:
                personas_to_export = self.get_all_personas()
            
            data = [persona.to_dict() for persona in personas_to_export]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting personas to {filepath}: {e}")
            return False
    
    def import_personas(self, filepath: str, overwrite_existing: bool = False) -> int:
        """Import personas from a file. Returns number of personas imported."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for persona_data in data:
                try:
                    persona = Persona.from_dict(persona_data)
                    
                    # Check if persona already exists
                    if persona.id in self.personas and not overwrite_existing:
                        continue
                    
                    self.personas[persona.id] = persona
                    imported_count += 1
                    
                except Exception as e:
                    print(f"Error importing persona: {e}")
                    continue
            
            if imported_count > 0:
                self._save_personas()
            
            return imported_count
            
        except Exception as e:
            print(f"Error importing personas from {filepath}: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the persona collection."""
        personas = self.get_all_personas()
        
        if not personas:
            return {
                'total_personas': 0,
                'active_personas': 0,
                'demographics': {}
            }
        
        # Calculate demographic distributions
        age_distribution = {}
        gender_distribution = {}
        occupation_distribution = {}
        location_distribution = {}
        
        for persona in personas:
            # Age ranges
            age_range = f"{(persona.age // 10) * 10}-{(persona.age // 10) * 10 + 9}"
            age_distribution[age_range] = age_distribution.get(age_range, 0) + 1
            
            # Gender
            gender_distribution[persona.gender] = gender_distribution.get(persona.gender, 0) + 1
            
            # Occupation
            occupation_distribution[persona.occupation] = occupation_distribution.get(persona.occupation, 0) + 1
            
            # Location
            location_distribution[persona.location] = location_distribution.get(persona.location, 0) + 1
        
        return {
            'total_personas': len(self.personas),
            'active_personas': len(personas),
            'demographics': {
                'age_distribution': age_distribution,
                'gender_distribution': gender_distribution,
                'occupation_distribution': occupation_distribution,
                'location_distribution': location_distribution
            },
            'average_age': sum(p.age for p in personas) / len(personas) if personas else 0
        }