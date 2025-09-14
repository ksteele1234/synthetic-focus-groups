"""
Q/A Turn data contract and JSON schema for synthetic focus group sessions.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import jsonschema


# JSON Schema definition for Q/A turns
QA_TURN_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Q/A Turn",
    "description": "Schema for question/answer turns in synthetic focus group sessions",
    "type": "object",
    "required": [
        "study_id",
        "session_id", 
        "persona_id",
        "round_id",
        "question",
        "answer",
        "confidence_0_1",
        "tags",
        "ts"
    ],
    "properties": {
        "study_id": {
            "type": "string",
            "description": "Unique identifier for the research study"
        },
        "session_id": {
            "type": "string", 
            "description": "Unique identifier for the focus group session"
        },
        "persona_id": {
            "type": "string",
            "description": "Unique identifier for the participating persona"
        },
        "round_id": {
            "type": "integer",
            "description": "Sequential round number within the session",
            "minimum": 1
        },
        "question": {
            "type": "string",
            "description": "The facilitator question asked to the persona"
        },
        "answer": {
            "type": "string",
            "description": "The persona's response to the question"
        },
        "follow_up_question": {
            "type": ["string", "null"],
            "description": "Optional follow-up question from facilitator"
        },
        "follow_up_answer": {
            "type": ["string", "null"],
            "description": "Optional persona response to follow-up question"
        },
        "confidence_0_1": {
            "type": "number",
            "description": "Confidence score for the persona's answer",
            "minimum": 0.0,
            "maximum": 1.0
        },
        "tags": {
            "type": "array",
            "description": "List of thematic tags for the Q/A turn",
            "items": {
                "type": "string"
            }
        },
        "ts": {
            "type": "string",
            "description": "ISO timestamp of when the turn occurred",
            "format": "date-time"
        }
    },
    "additionalProperties": False
}


@dataclass
class QATurn:
    """Represents a single Q/A turn in a synthetic focus group session."""
    
    study_id: str
    session_id: str
    persona_id: str
    round_id: int
    question: str
    answer: str
    confidence_0_1: float
    tags: List[str]
    ts: str
    follow_up_question: Optional[str] = None
    follow_up_answer: Optional[str] = None
    
    def __post_init__(self):
        """Validate data after initialization."""
        # Ensure confidence is between 0 and 1
        if not (0.0 <= self.confidence_0_1 <= 1.0):
            raise ValueError(f"confidence_0_1 must be between 0.0 and 1.0, got {self.confidence_0_1}")
        
        # Ensure round_id is positive
        if self.round_id < 1:
            raise ValueError(f"round_id must be >= 1, got {self.round_id}")
        
        # Validate timestamp format
        try:
            datetime.fromisoformat(self.ts.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {self.ts}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "study_id": self.study_id,
            "session_id": self.session_id,
            "persona_id": self.persona_id,
            "round_id": self.round_id,
            "question": self.question,
            "answer": self.answer,
            "follow_up_question": self.follow_up_question,
            "follow_up_answer": self.follow_up_answer,
            "confidence_0_1": self.confidence_0_1,
            "tags": self.tags,
            "ts": self.ts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QATurn':
        """Create QATurn from dictionary."""
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    def validate_schema(self) -> bool:
        """Validate against JSON schema."""
        try:
            jsonschema.validate(self.to_dict(), QA_TURN_SCHEMA)
            return True
        except jsonschema.ValidationError as e:
            raise ValueError(f"Schema validation failed: {e.message}")
    
    @classmethod
    def create_with_timestamp(cls, study_id: str, session_id: str, persona_id: str,
                            round_id: int, question: str, answer: str, confidence: float,
                            tags: List[str], follow_up_question: Optional[str] = None,
                            follow_up_answer: Optional[str] = None) -> 'QATurn':
        """Create QATurn with current timestamp."""
        return cls(
            study_id=study_id,
            session_id=session_id,
            persona_id=persona_id,
            round_id=round_id,
            question=question,
            answer=answer,
            confidence_0_1=confidence,
            tags=tags,
            ts=datetime.utcnow().isoformat() + 'Z',
            follow_up_question=follow_up_question,
            follow_up_answer=follow_up_answer
        )


def validate_qa_turns(qa_turns: List[QATurn]) -> List[str]:
    """Validate a list of Q/A turns and return any errors."""
    errors = []
    
    for i, turn in enumerate(qa_turns):
        try:
            turn.validate_schema()
        except ValueError as e:
            errors.append(f"Turn {i}: {e}")
    
    # Check for logical consistency
    session_rounds = {}
    for turn in qa_turns:
        key = (turn.study_id, turn.session_id)
        if key not in session_rounds:
            session_rounds[key] = []
        session_rounds[key].append(turn.round_id)
    
    # Validate round sequence
    for (study_id, session_id), rounds in session_rounds.items():
        sorted_rounds = sorted(set(rounds))
        expected_rounds = list(range(1, len(sorted_rounds) + 1))
        
        if sorted_rounds != expected_rounds:
            errors.append(f"Study {study_id}, Session {session_id}: Round sequence invalid. Expected {expected_rounds}, got {sorted_rounds}")
    
    return errors


def create_sample_qa_turn() -> QATurn:
    """Create a sample Q/A turn for testing."""
    return QATurn.create_with_timestamp(
        study_id="study_001",
        session_id="session_001", 
        persona_id="sarah_small_business",
        round_id=1,
        question="What are your biggest challenges with current social media management tools?",
        answer="I'm constantly juggling between 3 different apps - Hootsuite for scheduling, Canva for graphics, and Google Analytics for tracking. It's exhausting and time-consuming.",
        confidence=0.85,
        tags=["workflow_inefficiency", "tool_fragmentation", "time_management"],
        follow_up_question="How much time do you spend switching between these tools daily?",
        follow_up_answer="Probably 30-45 minutes just switching and syncing data between platforms. That's time I could spend on actual content creation."
    )