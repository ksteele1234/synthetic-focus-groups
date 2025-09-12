"""
Facilitator manager for CRUD operations and AI moderation capabilities.
"""

import json
import os
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.facilitator import Facilitator


class FacilitatorManager:
    """Manages facilitators with file-based storage and AI interaction capabilities."""
    
    def __init__(self, storage_path: str = "data/facilitators"):
        """Initialize facilitator manager with storage path."""
        self.storage_path = storage_path
        self.facilitators_file = os.path.join(storage_path, "facilitators.json")
        self.facilitators: Dict[str, Facilitator] = {}
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing facilitators
        self._load_facilitators()
    
    def _load_facilitators(self) -> None:
        """Load facilitators from storage file."""
        if os.path.exists(self.facilitators_file):
            try:
                with open(self.facilitators_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for facilitator_data in data:
                        facilitator = Facilitator.from_dict(facilitator_data)
                        self.facilitators[facilitator.id] = facilitator
            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Could not load facilitators from {self.facilitators_file}: {e}")
    
    def _save_facilitators(self) -> None:
        """Save facilitators to storage file."""
        try:
            data = [facilitator.to_dict() for facilitator in self.facilitators.values()]
            with open(self.facilitators_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving facilitators to {self.facilitators_file}: {e}")
    
    def create_facilitator(self, **kwargs) -> Facilitator:
        """Create a new facilitator with provided attributes."""
        facilitator = Facilitator(**kwargs)
        self.facilitators[facilitator.id] = facilitator
        self._save_facilitators()
        return facilitator
    
    def get_facilitator(self, facilitator_id: str) -> Optional[Facilitator]:
        """Get a facilitator by ID."""
        return self.facilitators.get(facilitator_id)
    
    def get_all_facilitators(self, active_only: bool = True) -> List[Facilitator]:
        """Get all facilitators, optionally filtering to active ones only."""
        facilitators = list(self.facilitators.values())
        if active_only:
            facilitators = [f for f in facilitators if f.active]
        return facilitators
    
    def update_facilitator(self, facilitator_id: str, **kwargs) -> Optional[Facilitator]:
        """Update a facilitator with new attributes."""
        facilitator = self.get_facilitator(facilitator_id)
        if not facilitator:
            return None
        
        # Update attributes
        for key, value in kwargs.items():
            if hasattr(facilitator, key):
                setattr(facilitator, key, value)
        
        # Update timestamp and regenerate instructions if needed
        facilitator.updated_at = datetime.now()
        if any(key in kwargs for key in ['moderation_style', 'research_context', 'objectives']):
            facilitator.update_instructions()
        
        self._save_facilitators()
        return facilitator
    
    def delete_facilitator(self, facilitator_id: str) -> bool:
        """Delete a facilitator by ID."""
        if facilitator_id in self.facilitators:
            del self.facilitators[facilitator_id]
            self._save_facilitators()
            return True
        return False
    
    def deactivate_facilitator(self, facilitator_id: str) -> bool:
        """Deactivate a facilitator (soft delete)."""
        facilitator = self.get_facilitator(facilitator_id)
        if facilitator:
            facilitator.active = False
            facilitator.updated_at = datetime.now()
            self._save_facilitators()
            return True
        return False
    
    def generate_follow_up_questions(self, facilitator_id: str, participant_response: str, 
                                   question_context: str = "", session_context: str = "") -> List[str]:
        """Generate follow-up questions based on participant response."""
        facilitator = self.get_facilitator(facilitator_id)
        if not facilitator:
            return []
        
        # Enhanced follow-up question generation based on response content and context
        follow_ups = []
        
        # Analyze response for key themes to probe
        response_lower = participant_response.lower()
        
        # Question templates based on facilitator's approach
        if facilitator.questioning_approach == "probing":
            templates = [
                "Can you tell me more about what you mean when you say '{key_phrase}'?",
                "That's interesting - what experiences led you to that perspective?",
                "How does that impact your daily life or decisions?",
                "Can you give me a specific example of that?",
                "What would need to change for you to feel differently about this?"
            ]
        elif facilitator.questioning_approach == "empathetic":
            templates = [
                "I can hear that this is important to you - can you help me understand why?",
                "It sounds like you've given this some thought. What shaped your thinking on this?",
                "How do you think others in your situation might view this differently?",
                "What has been your personal experience with this?",
                "How do you feel when you encounter this situation?"
            ]
        elif facilitator.questioning_approach == "analytical":
            templates = [
                "What factors influenced your response to this?",
                "How would you rank the importance of different aspects of this issue?",
                "What patterns have you noticed in your experience with this?",
                "What would you consider the pros and cons of this approach?",
                "How does this compare to alternatives you've considered?"
            ]
        else:  # direct
            templates = [
                "What specifically about this stands out to you?",
                "Why do you think that is?",
                "What would you do differently?",
                "How often does this happen in your experience?",
                "What's the most important aspect of this for you?"
            ]
        
        # Generate questions based on response content
        num_questions = random.randint(*facilitator.follow_up_count_range)
        
        # Look for key phrases in the response to personalize questions
        key_phrases = self._extract_key_phrases(participant_response)
        
        # Select and personalize templates
        selected_templates = random.sample(templates, min(num_questions, len(templates)))
        
        for i, template in enumerate(selected_templates):
            if key_phrases and '{key_phrase}' in template:
                key_phrase = random.choice(key_phrases)
                question = template.format(key_phrase=key_phrase)
            else:
                question = template.replace('{key_phrase}', 'that')
            
            follow_ups.append(question)
        
        return follow_ups
    
    def _extract_key_phrases(self, text: str, max_phrases: int = 3) -> List[str]:
        """Extract key phrases from participant response for personalized follow-ups."""
        # Simple phrase extraction - in a real implementation, this could use NLP
        import re
        
        # Remove common words and extract meaningful phrases
        text = text.lower()
        
        # Look for quoted phrases or emphatic expressions
        quoted_phrases = re.findall(r'"([^"]*)"', text)
        if quoted_phrases:
            return quoted_phrases[:max_phrases]
        
        # Look for emphasis patterns
        emphatic_patterns = [
            r'i (really|absolutely|definitely|strongly) ([^,.\n]+)',
            r'it\s+(is|was) (so|very|really|extremely) ([^,.\n]+)',
            r'i (love|hate|feel|think|believe) ([^,.\n]+)',
        ]
        
        phrases = []
        for pattern in emphatic_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    phrase = ' '.join(match).strip()
                else:
                    phrase = match.strip()
                if len(phrase) > 3 and phrase not in phrases:
                    phrases.append(phrase)
        
        return phrases[:max_phrases]
    
    def create_default_facilitators(self) -> List[Facilitator]:
        """Create a set of default facilitators with different styles."""
        default_facilitators = [
            {
                'name': 'Dr. Sarah Chen',
                'expertise_area': 'Consumer Research',
                'moderation_style': 'balanced',
                'questioning_approach': 'probing',
                'tone': 'professional',
                'research_context': 'General consumer research and market insights',
                'objectives': [
                    'Understand participant perspectives and motivations',
                    'Identify key themes and patterns',
                    'Gather actionable insights for decision-making'
                ]
            },
            {
                'name': 'Marcus Rodriguez',
                'expertise_area': 'Healthcare Research', 
                'moderation_style': 'empathetic',
                'questioning_approach': 'empathetic',
                'tone': 'friendly',
                'research_context': 'Healthcare experiences and patient perspectives',
                'objectives': [
                    'Understand patient experiences and concerns',
                    'Identify barriers and facilitators to care',
                    'Gather insights to improve healthcare delivery'
                ]
            },
            {
                'name': 'Dr. Emily Watson',
                'expertise_area': 'Technology & Innovation',
                'moderation_style': 'collaborative',
                'questioning_approach': 'analytical',
                'tone': 'casual',
                'research_context': 'Technology adoption and digital experiences',
                'objectives': [
                    'Understand technology usage patterns',
                    'Identify user needs and pain points',
                    'Explore innovation opportunities'
                ]
            },
            {
                'name': 'James Thompson',
                'expertise_area': 'Product Development',
                'moderation_style': 'directive',
                'questioning_approach': 'direct',
                'tone': 'authoritative',
                'research_context': 'Product features, usability, and market fit',
                'objectives': [
                    'Evaluate product concepts and features',
                    'Understand user preferences and priorities',
                    'Identify areas for product improvement'
                ]
            }
        ]
        
        created_facilitators = []
        for facilitator_data in default_facilitators:
            # Only create if doesn't already exist
            existing = [f for f in self.get_all_facilitators() if f.name == facilitator_data['name']]
            if not existing:
                facilitator = self.create_facilitator(**facilitator_data)
                created_facilitators.append(facilitator)
        
        return created_facilitators
    
    def get_facilitators_by_expertise(self, expertise_area: str) -> List[Facilitator]:
        """Get facilitators filtered by expertise area."""
        return [f for f in self.get_all_facilitators() 
                if expertise_area.lower() in f.expertise_area.lower()]
    
    def get_facilitators_by_style(self, moderation_style: str = None, 
                                questioning_approach: str = None, tone: str = None) -> List[Facilitator]:
        """Get facilitators filtered by facilitation style attributes."""
        facilitators = self.get_all_facilitators()
        
        if moderation_style:
            facilitators = [f for f in facilitators if f.moderation_style == moderation_style]
        
        if questioning_approach:
            facilitators = [f for f in facilitators if f.questioning_approach == questioning_approach]
        
        if tone:
            facilitators = [f for f in facilitators if f.tone == tone]
        
        return facilitators
    
    def suggest_facilitator_for_research(self, research_topic: str, target_audience: str = "") -> Optional[Facilitator]:
        """Suggest the best facilitator based on research topic and audience."""
        facilitators = self.get_all_facilitators()
        if not facilitators:
            return None
        
        # Score facilitators based on topic relevance
        topic_lower = research_topic.lower()
        scored_facilitators = []
        
        for facilitator in facilitators:
            score = 0
            
            # Score based on expertise area match
            if any(keyword in facilitator.expertise_area.lower() 
                   for keyword in ['consumer', 'market', 'product'] 
                   if keyword in topic_lower):
                score += 3
            
            if 'healthcare' in topic_lower and 'healthcare' in facilitator.expertise_area.lower():
                score += 5
            
            if 'technology' in topic_lower and 'technology' in facilitator.expertise_area.lower():
                score += 5
            
            # Score based on research context match
            if any(keyword in facilitator.research_context.lower() 
                   for keyword in topic_lower.split()):
                score += 2
            
            # Prefer balanced/collaborative styles for general research
            if facilitator.moderation_style in ['balanced', 'collaborative']:
                score += 1
            
            scored_facilitators.append((facilitator, score))
        
        # Return facilitator with highest score
        scored_facilitators.sort(key=lambda x: x[1], reverse=True)
        return scored_facilitators[0][0] if scored_facilitators else facilitators[0]
    
    def export_facilitators(self, filepath: str, facilitator_ids: List[str] = None) -> bool:
        """Export facilitators to a file."""
        try:
            if facilitator_ids:
                facilitators_to_export = [self.get_facilitator(fid) for fid in facilitator_ids 
                                        if self.get_facilitator(fid)]
            else:
                facilitators_to_export = self.get_all_facilitators()
            
            data = [facilitator.to_dict() for facilitator in facilitators_to_export]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting facilitators to {filepath}: {e}")
            return False
    
    def import_facilitators(self, filepath: str, overwrite_existing: bool = False) -> int:
        """Import facilitators from a file. Returns number of facilitators imported."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            for facilitator_data in data:
                try:
                    facilitator = Facilitator.from_dict(facilitator_data)
                    
                    # Check if facilitator already exists
                    if facilitator.id in self.facilitators and not overwrite_existing:
                        continue
                    
                    self.facilitators[facilitator.id] = facilitator
                    imported_count += 1
                    
                except Exception as e:
                    print(f"Error importing facilitator: {e}")
                    continue
            
            if imported_count > 0:
                self._save_facilitators()
            
            return imported_count
            
        except Exception as e:
            print(f"Error importing facilitators from {filepath}: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the facilitator collection."""
        facilitators = self.get_all_facilitators()
        
        if not facilitators:
            return {
                'total_facilitators': 0,
                'active_facilitators': 0,
                'style_distribution': {}
            }
        
        # Calculate style distributions
        moderation_styles = {}
        questioning_approaches = {}
        tones = {}
        expertise_areas = {}
        
        for facilitator in facilitators:
            moderation_styles[facilitator.moderation_style] = moderation_styles.get(facilitator.moderation_style, 0) + 1
            questioning_approaches[facilitator.questioning_approach] = questioning_approaches.get(facilitator.questioning_approach, 0) + 1
            tones[facilitator.tone] = tones.get(facilitator.tone, 0) + 1
            expertise_areas[facilitator.expertise_area] = expertise_areas.get(facilitator.expertise_area, 0) + 1
        
        return {
            'total_facilitators': len(self.facilitators),
            'active_facilitators': len(facilitators),
            'style_distribution': {
                'moderation_styles': moderation_styles,
                'questioning_approaches': questioning_approaches,
                'tones': tones,
                'expertise_areas': expertise_areas
            }
        }