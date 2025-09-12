"""
Project model for managing research configurations and focus group setups.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


@dataclass
class Project:
    """Represents a focus group research project configuration."""
    
    # Basic project info
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    research_topic: str = ""
    
    # Research design
    research_questions: List[str] = field(default_factory=list)
    target_insights: List[str] = field(default_factory=list)
    methodology_notes: str = ""
    
    # Participant configuration
    facilitator_id: Optional[str] = None
    persona_ids: List[str] = field(default_factory=list)
    max_participants: int = 20
    min_participants: int = 3
    
    # Session settings
    estimated_duration_minutes: int = 60
    session_structure: List[str] = field(default_factory=lambda: [
        "Welcome and introductions",
        "Primary questions discussion", 
        "Follow-up and probing questions",
        "Final thoughts and wrap-up"
    ])
    
    # Data collection preferences
    collect_demographics: bool = True
    collect_verbatim_responses: bool = True
    collect_sentiment_analysis: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["json", "csv"])
    
    # Analysis settings
    auto_analyze: bool = True
    analysis_focus_areas: List[str] = field(default_factory=list)
    custom_analysis_instructions: str = ""
    
    # Project metadata
    client_info: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    status: str = "draft"  # draft, active, completed, archived
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_session_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate project configuration."""
        if self.max_participants > 20:
            self.max_participants = 20
        if self.min_participants < 1:
            self.min_participants = 1
    
    def validate_configuration(self) -> tuple[bool, List[str]]:
        """Validate project configuration and return validation status and errors."""
        errors = []
        
        if not self.name.strip():
            errors.append("Project name is required")
        
        if not self.research_topic.strip():
            errors.append("Research topic is required")
        
        if not self.research_questions:
            errors.append("At least one research question is required")
        
        if self.facilitator_id is None:
            errors.append("Facilitator must be assigned")
        
        if len(self.persona_ids) < self.min_participants:
            errors.append(f"At least {self.min_participants} personas must be assigned")
        
        if len(self.persona_ids) > self.max_participants:
            errors.append(f"Cannot exceed {self.max_participants} personas")
        
        return len(errors) == 0, errors
    
    def get_participant_count(self) -> int:
        """Get current number of assigned participants."""
        return len(self.persona_ids)
    
    def add_persona(self, persona_id: str) -> bool:
        """Add a persona to the project if within limits."""
        if persona_id not in self.persona_ids and len(self.persona_ids) < self.max_participants:
            self.persona_ids.append(persona_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def remove_persona(self, persona_id: str) -> bool:
        """Remove a persona from the project."""
        if persona_id in self.persona_ids:
            self.persona_ids.remove(persona_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def set_facilitator(self, facilitator_id: str) -> None:
        """Set the facilitator for this project."""
        self.facilitator_id = facilitator_id
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: str) -> bool:
        """Update project status if valid."""
        valid_statuses = ["draft", "active", "completed", "archived"]
        if new_status in valid_statuses:
            self.status = new_status
            self.updated_at = datetime.now()
            return True
        return False
    
    def record_session(self) -> None:
        """Record that a session was conducted."""
        self.last_session_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary view of the project."""
        return {
            'id': self.id,
            'name': self.name,
            'research_topic': self.research_topic,
            'status': self.status,
            'participant_count': len(self.persona_ids),
            'has_facilitator': self.facilitator_id is not None,
            'question_count': len(self.research_questions),
            'created_at': self.created_at.isoformat(),
            'last_session_at': self.last_session_at.isoformat() if self.last_session_at else None
        }
    
    def to_dict(self) -> Dict:
        """Convert project to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'research_topic': self.research_topic,
            'research_questions': self.research_questions,
            'target_insights': self.target_insights,
            'methodology_notes': self.methodology_notes,
            'facilitator_id': self.facilitator_id,
            'persona_ids': self.persona_ids,
            'max_participants': self.max_participants,
            'min_participants': self.min_participants,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'session_structure': self.session_structure,
            'collect_demographics': self.collect_demographics,
            'collect_verbatim_responses': self.collect_verbatim_responses,
            'collect_sentiment_analysis': self.collect_sentiment_analysis,
            'export_formats': self.export_formats,
            'auto_analyze': self.auto_analyze,
            'analysis_focus_areas': self.analysis_focus_areas,
            'custom_analysis_instructions': self.custom_analysis_instructions,
            'client_info': self.client_info,
            'tags': self.tags,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_session_at': self.last_session_at.isoformat() if self.last_session_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        """Create project from dictionary."""
        # Handle datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if 'last_session_at' in data and data['last_session_at'] and isinstance(data['last_session_at'], str):
            data['last_session_at'] = datetime.fromisoformat(data['last_session_at'])
        
        return cls(**data)