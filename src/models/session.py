"""
Session and response models for managing focus group interactions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from enum import Enum


class ResponseType(Enum):
    """Types of responses in a session."""
    FACILITATOR_QUESTION = "facilitator_question"
    PARTICIPANT_RESPONSE = "participant_response"
    FACILITATOR_FOLLOWUP = "facilitator_followup"
    CROSS_DISCUSSION = "cross_discussion"
    FACILITATOR_SUMMARY = "facilitator_summary"


@dataclass
class SessionResponse:
    """Represents a single interaction in a focus group session."""
    
    # Basic response info
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    response_type: ResponseType = ResponseType.PARTICIPANT_RESPONSE
    
    # Speaker info
    speaker_id: str = ""  # persona_id or facilitator_id
    speaker_name: str = ""
    speaker_type: str = ""  # "participant" or "facilitator"
    
    # Response content
    content: str = ""
    question_id: Optional[str] = None  # Reference to specific question if applicable
    responding_to_id: Optional[str] = None  # Reference to previous response if follow-up
    
    # Context and metadata
    sequence_number: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    duration_seconds: Optional[float] = None
    
    # Analysis data (populated after response)
    sentiment_score: Optional[float] = None  # -1.0 to 1.0
    emotion_tags: List[str] = field(default_factory=list)
    key_themes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert response to dictionary for serialization."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'response_type': self.response_type.value,
            'speaker_id': self.speaker_id,
            'speaker_name': self.speaker_name,
            'speaker_type': self.speaker_type,
            'content': self.content,
            'question_id': self.question_id,
            'responding_to_id': self.responding_to_id,
            'sequence_number': self.sequence_number,
            'timestamp': self.timestamp.isoformat(),
            'duration_seconds': self.duration_seconds,
            'sentiment_score': self.sentiment_score,
            'emotion_tags': self.emotion_tags,
            'key_themes': self.key_themes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SessionResponse':
        """Create response from dictionary."""
        if 'response_type' in data and isinstance(data['response_type'], str):
            data['response_type'] = ResponseType(data['response_type'])
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)


@dataclass  
class Session:
    """Represents a complete focus group session."""
    
    # Basic session info
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    name: str = ""
    description: str = ""
    
    # Session configuration
    facilitator_id: str = ""
    participant_ids: List[str] = field(default_factory=list)
    primary_questions: List[str] = field(default_factory=list)
    
    # Session state
    status: str = "created"  # created, in_progress, completed, failed
    current_question_index: int = 0
    current_phase: str = "setup"  # setup, introduction, questions, wrap_up, complete
    
    # Timing
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None  
    estimated_duration_minutes: int = 60
    actual_duration_minutes: Optional[float] = None
    
    # Session data
    responses: List[SessionResponse] = field(default_factory=list)
    session_notes: str = ""
    facilitator_observations: str = ""
    
    # Results and analysis
    key_insights: List[str] = field(default_factory=list)
    themes_discovered: List[str] = field(default_factory=list)
    participant_summaries: Dict[str, str] = field(default_factory=dict)
    overall_sentiment: Optional[float] = None
    
    # Export and sharing
    exported_formats: List[str] = field(default_factory=list)
    export_timestamps: Dict[str, datetime] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def start_session(self) -> bool:
        """Start the session if not already started."""
        if self.status == "created":
            self.status = "in_progress"
            self.started_at = datetime.now()
            self.current_phase = "introduction"
            self.updated_at = datetime.now()
            return True
        return False
    
    def end_session(self) -> bool:
        """End the session and calculate duration."""
        if self.status == "in_progress":
            self.status = "completed"
            self.ended_at = datetime.now()
            self.current_phase = "complete"
            
            if self.started_at:
                duration = self.ended_at - self.started_at
                self.actual_duration_minutes = duration.total_seconds() / 60
            
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_response(self, response: SessionResponse) -> None:
        """Add a response to the session."""
        response.session_id = self.id
        response.sequence_number = len(self.responses) + 1
        self.responses.append(response)
        self.updated_at = datetime.now()
    
    def get_responses_by_participant(self, participant_id: str) -> List[SessionResponse]:
        """Get all responses from a specific participant."""
        return [r for r in self.responses if r.speaker_id == participant_id and r.speaker_type == "participant"]
    
    def get_responses_by_question(self, question_id: str) -> List[SessionResponse]:
        """Get all responses related to a specific question."""
        return [r for r in self.responses if r.question_id == question_id]
    
    def get_facilitator_questions(self) -> List[SessionResponse]:
        """Get all facilitator questions."""
        return [r for r in self.responses if r.response_type == ResponseType.FACILITATOR_QUESTION]
    
    def get_participant_responses(self) -> List[SessionResponse]:
        """Get all participant responses."""
        return [r for r in self.responses if r.speaker_type == "participant"]
    
    def advance_question(self) -> bool:
        """Move to the next question if available."""
        if self.current_question_index < len(self.primary_questions) - 1:
            self.current_question_index += 1
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_current_question(self) -> Optional[str]:
        """Get the current question being discussed."""
        if 0 <= self.current_question_index < len(self.primary_questions):
            return self.primary_questions[self.current_question_index]
        return None
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calculate session statistics."""
        participant_responses = self.get_participant_responses()
        facilitator_questions = self.get_facilitator_questions()
        
        return {
            'total_responses': len(self.responses),
            'participant_responses': len(participant_responses),
            'facilitator_questions': len(facilitator_questions),
            'unique_participants': len(set(r.speaker_id for r in participant_responses)),
            'questions_asked': len(facilitator_questions),
            'average_response_length': sum(len(r.content) for r in participant_responses) / max(len(participant_responses), 1),
            'session_duration_minutes': self.actual_duration_minutes,
            'responses_per_participant': {
                pid: len(self.get_responses_by_participant(pid)) 
                for pid in self.participant_ids
            }
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary view of the session."""
        stats = self.calculate_statistics()
        
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_minutes': self.actual_duration_minutes,
            'participant_count': len(self.participant_ids),
            'response_count': len(self.responses),
            'current_phase': self.current_phase,
            'insights_count': len(self.key_insights),
            'themes_count': len(self.themes_discovered)
        }
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary for serialization."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'facilitator_id': self.facilitator_id,
            'participant_ids': self.participant_ids,
            'primary_questions': self.primary_questions,
            'status': self.status,
            'current_question_index': self.current_question_index,
            'current_phase': self.current_phase,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'actual_duration_minutes': self.actual_duration_minutes,
            'responses': [r.to_dict() for r in self.responses],
            'session_notes': self.session_notes,
            'facilitator_observations': self.facilitator_observations,
            'key_insights': self.key_insights,
            'themes_discovered': self.themes_discovered,
            'participant_summaries': self.participant_summaries,
            'overall_sentiment': self.overall_sentiment,
            'exported_formats': self.exported_formats,
            'export_timestamps': {k: v.isoformat() for k, v in self.export_timestamps.items()},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """Create session from dictionary."""
        # Handle datetime fields
        if 'started_at' in data and data['started_at'] and isinstance(data['started_at'], str):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if 'ended_at' in data and data['ended_at'] and isinstance(data['ended_at'], str):
            data['ended_at'] = datetime.fromisoformat(data['ended_at'])
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Handle export timestamps
        if 'export_timestamps' in data:
            data['export_timestamps'] = {
                k: datetime.fromisoformat(v) if isinstance(v, str) else v
                for k, v in data['export_timestamps'].items()
            }
        
        # Handle responses
        if 'responses' in data:
            data['responses'] = [SessionResponse.from_dict(r) for r in data['responses']]
        
        return cls(**data)