"""
Enhanced project model with background information and persona weighting capabilities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import json


@dataclass
class PersonaWeight:
    """Represents a persona's weight and ranking in analysis."""
    persona_id: str
    weight: float = 1.0  # Default weight
    rank: Optional[int] = None  # Optional ranking (1 = highest priority)
    is_primary_icp: bool = False  # Designates the primary ICP
    notes: str = ""  # Additional notes about this persona's relevance
    

@dataclass
class BackgroundInformation:
    """Comprehensive background information for research projects."""
    
    # Research Context
    industry_context: str = ""
    market_size: str = ""
    target_market_description: str = ""
    
    # Product Information
    product_description: str = ""
    product_features: List[str] = field(default_factory=list)
    value_propositions: List[str] = field(default_factory=list)
    pricing_information: str = ""
    
    # Competitive Landscape
    competitors: List[Dict[str, Any]] = field(default_factory=list)  # [{name, description, strengths, weaknesses}]
    competitive_advantages: List[str] = field(default_factory=list)
    market_positioning: str = ""
    
    # Research Objectives
    business_objectives: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    decision_criteria: List[str] = field(default_factory=list)
    
    # Methodology Context
    research_methodology: str = ""
    sample_requirements: str = ""
    bias_considerations: List[str] = field(default_factory=list)
    
    # Additional Files/Resources
    uploaded_documents: List[str] = field(default_factory=list)  # File paths
    reference_links: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_competitor(self, name: str, description: str = "", strengths: List[str] = None, 
                      weaknesses: List[str] = None) -> None:
        """Add a competitor to the background information."""
        competitor = {
            'name': name,
            'description': description,
            'strengths': strengths or [],
            'weaknesses': weaknesses or [],
            'added_at': datetime.now().isoformat()
        }
        self.competitors.append(competitor)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'industry_context': self.industry_context,
            'market_size': self.market_size,
            'target_market_description': self.target_market_description,
            'product_description': self.product_description,
            'product_features': self.product_features,
            'value_propositions': self.value_propositions,
            'pricing_information': self.pricing_information,
            'competitors': self.competitors,
            'competitive_advantages': self.competitive_advantages,
            'market_positioning': self.market_positioning,
            'business_objectives': self.business_objectives,
            'success_metrics': self.success_metrics,
            'decision_criteria': self.decision_criteria,
            'research_methodology': self.research_methodology,
            'sample_requirements': self.sample_requirements,
            'bias_considerations': self.bias_considerations,
            'uploaded_documents': self.uploaded_documents,
            'reference_links': self.reference_links,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackgroundInformation':
        """Create from dictionary."""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


@dataclass
class EnhancedProject:
    """Enhanced project model with background information and persona weighting."""
    
    # Basic project info (from original Project model)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    research_topic: str = ""
    
    # Research design
    research_questions: List[str] = field(default_factory=list)
    target_insights: List[str] = field(default_factory=list)
    methodology_notes: str = ""
    
    # Enhanced background information
    background_info: BackgroundInformation = field(default_factory=BackgroundInformation)
    
    # Participant configuration with weighting
    facilitator_id: Optional[str] = None
    persona_weights: List[PersonaWeight] = field(default_factory=list)
    max_participants: int = 20
    min_participants: int = 3
    
    # ICP and ranking system
    primary_icp_persona_id: Optional[str] = None
    persona_ranking_enabled: bool = False
    
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
    weighted_analysis_enabled: bool = True
    
    # Project metadata
    client_info: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    status: str = "draft"  # draft, active, completed, archived
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_session_at: Optional[datetime] = None
    
    def set_primary_icp(self, persona_id: str) -> bool:
        """Set a persona as the primary ICP."""
        # Verify persona exists in the project
        persona_weight = self.get_persona_weight(persona_id)
        if not persona_weight:
            return False
        
        # Clear previous primary ICP
        for pw in self.persona_weights:
            pw.is_primary_icp = False
        
        # Set new primary ICP
        persona_weight.is_primary_icp = True
        self.primary_icp_persona_id = persona_id
        self.updated_at = datetime.now()
        return True
    
    def add_persona_with_weight(self, persona_id: str, weight: float = 1.0, 
                               rank: Optional[int] = None, is_primary_icp: bool = False) -> bool:
        """Add a persona with specific weight and ranking."""
        if len(self.persona_weights) >= self.max_participants:
            return False
        
        # Check if persona already exists
        if self.get_persona_weight(persona_id):
            return False
        
        # Clear primary ICP flag from others if this is primary
        if is_primary_icp:
            for pw in self.persona_weights:
                pw.is_primary_icp = False
            self.primary_icp_persona_id = persona_id
        
        persona_weight = PersonaWeight(
            persona_id=persona_id,
            weight=weight,
            rank=rank,
            is_primary_icp=is_primary_icp
        )
        
        self.persona_weights.append(persona_weight)
        self.updated_at = datetime.now()
        return True
    
    def remove_persona(self, persona_id: str) -> bool:
        """Remove a persona from the project."""
        persona_weight = self.get_persona_weight(persona_id)
        if not persona_weight:
            return False
        
        self.persona_weights.remove(persona_weight)
        
        # Clear primary ICP if this was it
        if self.primary_icp_persona_id == persona_id:
            self.primary_icp_persona_id = None
        
        self.updated_at = datetime.now()
        return True
    
    def get_persona_weight(self, persona_id: str) -> Optional[PersonaWeight]:
        """Get the persona weight object for a specific persona."""
        for pw in self.persona_weights:
            if pw.persona_id == persona_id:
                return pw
        return None
    
    def update_persona_weight(self, persona_id: str, weight: float) -> bool:
        """Update the weight for a specific persona."""
        persona_weight = self.get_persona_weight(persona_id)
        if not persona_weight:
            return False
        
        persona_weight.weight = weight
        self.updated_at = datetime.now()
        return True
    
    def update_persona_rank(self, persona_id: str, rank: int) -> bool:
        """Update the rank for a specific persona."""
        persona_weight = self.get_persona_weight(persona_id)
        if not persona_weight:
            return False
        
        persona_weight.rank = rank
        self.persona_ranking_enabled = True
        self.updated_at = datetime.now()
        return True
    
    def get_ranked_personas(self) -> List[PersonaWeight]:
        """Get personas sorted by rank (primary ICP first, then by rank, then by weight)."""
        # Sort: Primary ICP first, then by rank (ascending), then by weight (descending)
        return sorted(self.persona_weights, key=lambda pw: (
            not pw.is_primary_icp,  # Primary ICP first (False comes before True)
            pw.rank if pw.rank is not None else float('inf'),  # Then by rank
            -pw.weight  # Then by weight descending
        ))
    
    def get_persona_ids(self) -> List[str]:
        """Get list of persona IDs for backward compatibility."""
        return [pw.persona_id for pw in self.persona_weights]
    
    def validate_configuration(self) -> tuple[bool, List[str]]:
        """Validate project configuration."""
        errors = []
        
        if not self.name.strip():
            errors.append("Project name is required")
        
        if not self.research_topic.strip():
            errors.append("Research topic is required")
        
        if not self.research_questions:
            errors.append("At least one research question is required")
        
        if self.facilitator_id is None:
            errors.append("Facilitator must be assigned")
        
        if len(self.persona_weights) < self.min_participants:
            errors.append(f"At least {self.min_participants} personas must be assigned")
        
        if len(self.persona_weights) > self.max_participants:
            errors.append(f"Cannot exceed {self.max_participants} personas")
        
        # Validate weights
        for pw in self.persona_weights:
            if pw.weight <= 0:
                errors.append(f"Persona weight must be positive (persona: {pw.persona_id})")
        
        return len(errors) == 0, errors
    
    def get_analysis_weights(self) -> Dict[str, float]:
        """Get normalized weights for analysis."""
        if not self.weighted_analysis_enabled:
            # Return equal weights if weighting is disabled
            return {pw.persona_id: 1.0 for pw in self.persona_weights}
        
        # Calculate normalized weights
        total_weight = sum(pw.weight for pw in self.persona_weights)
        if total_weight == 0:
            return {pw.persona_id: 1.0 for pw in self.persona_weights}
        
        return {pw.persona_id: pw.weight / total_weight for pw in self.persona_weights}
    
    def update_background_info(self, **kwargs) -> None:
        """Update background information fields."""
        for key, value in kwargs.items():
            if hasattr(self.background_info, key):
                setattr(self.background_info, key, value)
        
        self.background_info.updated_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'research_topic': self.research_topic,
            'research_questions': self.research_questions,
            'target_insights': self.target_insights,
            'methodology_notes': self.methodology_notes,
            'background_info': self.background_info if isinstance(self.background_info, dict) else self.background_info.to_dict() if hasattr(self.background_info, 'to_dict') else {},
            'facilitator_id': self.facilitator_id,
            'persona_weights': [
                {
                    'persona_id': pw.persona_id,
                    'weight': pw.weight,
                    'rank': pw.rank,
                    'is_primary_icp': pw.is_primary_icp,
                    'notes': pw.notes
                } for pw in self.persona_weights
            ],
            'max_participants': self.max_participants,
            'min_participants': self.min_participants,
            'primary_icp_persona_id': self.primary_icp_persona_id,
            'persona_ranking_enabled': self.persona_ranking_enabled,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'session_structure': self.session_structure,
            'collect_demographics': self.collect_demographics,
            'collect_verbatim_responses': self.collect_verbatim_responses,
            'collect_sentiment_analysis': self.collect_sentiment_analysis,
            'export_formats': self.export_formats,
            'auto_analyze': self.auto_analyze,
            'analysis_focus_areas': self.analysis_focus_areas,
            'custom_analysis_instructions': self.custom_analysis_instructions,
            'weighted_analysis_enabled': self.weighted_analysis_enabled,
            'client_info': self.client_info,
            'tags': self.tags,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_session_at': self.last_session_at.isoformat() if self.last_session_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedProject':
        """Create from dictionary."""
        # Handle datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if 'last_session_at' in data and data['last_session_at'] and isinstance(data['last_session_at'], str):
            data['last_session_at'] = datetime.fromisoformat(data['last_session_at'])
        
        # Handle background info
        if 'background_info' in data:
            data['background_info'] = BackgroundInformation.from_dict(data['background_info'])
        
        # Handle persona weights
        if 'persona_weights' in data:
            persona_weights = []
            for pw_data in data['persona_weights']:
                persona_weights.append(PersonaWeight(**pw_data))
            data['persona_weights'] = persona_weights
        
        return cls(**data)