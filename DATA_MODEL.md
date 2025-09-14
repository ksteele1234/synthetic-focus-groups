# Data Model Overview

## 📊 Core Data Models

The Synthetic Focus Groups system uses a comprehensive set of data models to manage research projects, AI personas, sessions, and analysis results.

## 🏗️ Model Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA MODEL HIERARCHY                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  EnhancedProject (Master Entity)                            │
│  ├── PersonaWeight[]        (Weighted participant config)   │
│  ├── BackgroundInformation  (Research context)              │
│  └── research_questions[]   (Study questions)               │
│                                                             │
│  Session (Execution Entity)                                 │
│  ├── SessionResponse[]      (Individual interactions)       │
│  ├── participant_ids[]      (References to personas)        │
│  └── project_id            (References EnhancedProject)     │
│                                                             │
│  Persona (Participant Entity)                              │
│  ├── Demographics          (Age, gender, location, etc.)    │
│  ├── Psychographics        (Personality, values, etc.)      │
│  └── AI Instructions       (Prompts, context)               │
│                                                             │
│  QATurn (Analysis Entity)                                  │
│  └── Structured Q&A data   (JSONL-compatible format)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Primary Models

### 1. EnhancedProject (Production Model)

**File**: `src/models/enhanced_project.py`

The main project configuration with advanced features:

```python
@dataclass
class EnhancedProject:
    # Basic Info
    id: str
    name: str  
    description: str
    research_topic: str
    
    # Research Design
    research_questions: List[str]
    target_insights: List[str]
    
    # Advanced Features
    persona_weights: List[PersonaWeight]      # Strategic weighting system
    background_info: BackgroundInformation    # Rich project context
    primary_icp_persona_id: Optional[str]     # Primary customer profile
    weighted_analysis_enabled: bool           # Enable strategic analysis
    
    # Session Settings
    estimated_duration_minutes: int
    facilitator_id: Optional[str]
    max_participants: int = 20
```

**Key Methods**:
- `set_primary_icp()` - Designate primary customer profile
- `add_persona_with_weight()` - Add weighted participants
- `get_analysis_weights()` - Get normalized weights for analysis
- `validate_configuration()` - Ensure project is ready to run

### 2. PersonaWeight (Strategic Prioritization)

**File**: `src/models/enhanced_project.py`

Assigns strategic importance to different participants:

```python
@dataclass  
class PersonaWeight:
    persona_id: str
    weight: float = 1.0           # 0.1 - 5.0 strategic importance
    rank: Optional[int] = None    # Optional ranking (1 = highest)
    is_primary_icp: bool = False  # Primary Ideal Customer Profile
    notes: str = ""               # Strategic context
```

**Usage**:
- Weight 3.0+ = Primary targets (high influence on decisions)
- Weight 2.0-3.0 = Secondary targets (moderate influence)
- Weight 1.0-2.0 = Edge cases (low influence)
- Weight < 1.0 = Out of target (minimal influence)

### 3. Session (Execution Tracking)

**File**: `src/models/session.py`

Manages live focus group sessions:

```python
@dataclass
class Session:
    # Core Info
    id: str
    project_id: str
    name: str
    
    # Participants
    facilitator_id: str
    participant_ids: List[str]
    
    # State Management
    status: str                    # created, in_progress, completed
    current_question_index: int
    current_phase: str             # setup, introduction, questions, etc.
    
    # Session Data
    responses: List[SessionResponse]
    key_insights: List[str]
    themes_discovered: List[str]
    overall_sentiment: Optional[float]
    
    # Timing
    started_at: Optional[datetime]
    ended_at: Optional[datetime]  
    actual_duration_minutes: Optional[float]
```

**Key Methods**:
- `start_session()` / `end_session()` - State management
- `add_response()` - Record interactions
- `get_responses_by_participant()` - Filter by speaker
- `calculate_statistics()` - Session metrics

### 4. SessionResponse (Individual Interactions)

**File**: `src/models/session.py`

Records each interaction in a focus group:

```python
@dataclass
class SessionResponse:
    # Core Response
    id: str
    session_id: str
    speaker_id: str              # persona_id or facilitator_id
    speaker_name: str
    content: str                 # The actual response text
    
    # Context
    response_type: ResponseType  # FACILITATOR_QUESTION, PARTICIPANT_RESPONSE, etc.
    question_id: Optional[str]   # Which question this responds to
    sequence_number: int         # Order in session
    timestamp: datetime
    
    # Analysis Results
    sentiment_score: Optional[float]  # -1.0 to 1.0
    emotion_tags: List[str]          # ["frustrated", "hopeful", etc.]
    key_themes: List[str]            # ["pricing", "usability", etc.]
```

### 5. Persona (AI Participant)

**File**: `src/models/persona.py`

Defines AI personas for synthetic participants:

```python
@dataclass
class Persona:
    # Identity
    id: str
    name: str
    age: int
    gender: str
    
    # Demographics
    location: str
    occupation: str
    income_level: str
    education_level: str
    
    # Psychographics  
    personality_traits: List[str]    # ["analytical", "creative", etc.]
    values: List[str]               # ["authenticity", "efficiency", etc.]
    interests: List[str]            # ["technology", "sports", etc.]
    
    # AI Behavior
    communication_style: str         # "verbose", "concise", "balanced"
    response_tendency: str           # "agreeable", "contrarian", "honest"
    emotional_expression: str       # "high", "moderate", "low"
    
    # Context
    background_story: str
    base_personality_prompt: str     # AI system prompt
```

## 🔄 Data Flow

### Project Creation → Session Execution → Analysis

1. **Project Setup**:
   ```python
   project = EnhancedProject(
       name="Consumer Research",
       research_questions=["What are your pain points?", ...],
       persona_weights=[
           PersonaWeight(persona_id="user1", weight=3.0, is_primary_icp=True),
           PersonaWeight(persona_id="user2", weight=1.5)
       ]
   )
   ```

2. **Session Execution**:
   ```python
   session = Session(project_id=project.id)
   session.start_session()
   
   # AI interactions create SessionResponse objects
   response = SessionResponse(
       speaker_id="user1", 
       content="My biggest frustration is...",
       sentiment_score=0.2
   )
   session.add_response(response)
   ```

3. **Weighted Analysis**:
   ```python
   weights = project.get_analysis_weights()
   # {"user1": 0.67, "user2": 0.33} (normalized)
   
   weighted_sentiment = sum(
       response.sentiment_score * weights[response.speaker_id] 
       for response in session.responses
   )
   ```

## 💾 Data Persistence

### File Storage Structure
```
data/
├── projects/
│   └── projects.json          # EnhancedProject serialization
├── personas/  
│   └── personas.json          # Persona definitions
├── sessions/
│   └── {study_id}/
│       ├── {session_id}.jsonl # QATurn format (structured)
│       └── {session_id}.csv   # Analysis-ready format
└── exports/
    └── {session_id}/          # Generated reports & charts
```

### Serialization Methods

All models include:
- `to_dict()` - Convert to dictionary for JSON storage
- `from_dict()` - Reconstruct from stored dictionary
- Automatic datetime handling (ISO format)
- Validation methods for data integrity

## 🧪 Specialized Models

### QATurn (Analysis Format)

**File**: `src/models/qa_turn.py`

Structured Q&A format for analysis:

```python
@dataclass
class QATurn:
    study_id: str
    session_id: str
    persona_id: str
    round_id: str
    question: str
    answer: str
    confidence_0_1: float        # AI confidence in response
    tags: List[str]              # Thematic tags
    ts: datetime                 # Timestamp
```

Used for:
- JSONL export (one turn per line)
- External analysis tools
- Data pipeline integration

### BackgroundInformation (Research Context)

**File**: `src/models/enhanced_project.py`

Rich context for research projects:

```python
@dataclass
class BackgroundInformation:
    # Market Context
    industry_context: str
    market_size: str
    target_market_description: str
    
    # Product Info
    product_description: str
    product_features: List[str]
    value_propositions: List[str]
    pricing_information: str
    
    # Competitive Analysis
    competitors: List[Dict[str, Any]]
    competitive_advantages: List[str]
    market_positioning: str
    
    # Research Design
    business_objectives: List[str]
    success_metrics: List[str]
    research_methodology: str
```

## 🔍 Model Usage Patterns

### Creating Studies
```python
# Enhanced Project (Production)
project = EnhancedProject(
    name="SaaS UX Research",
    weighted_analysis_enabled=True,
    persona_weights=[
        PersonaWeight("primary_user", weight=3.0, is_primary_icp=True),
        PersonaWeight("secondary_user", weight=2.0),
        PersonaWeight("edge_case", weight=1.0)
    ]
)

# Standard Project (Basic)  
project = Project(
    name="Basic Research",
    persona_ids=["user1", "user2", "user3"]
)
```

### Running Sessions
```python
session = Session(
    project_id=project.id,
    facilitator_id="ai_facilitator",
    participant_ids=project.get_persona_ids()
)

session.start_session()
# ... AI interactions happen ...
session.end_session()
```

### Analysis & Export
```python
# Weighted analysis
weights = project.get_analysis_weights()
exporter = EnhancedDataExporter()

# Generate weighted reports
exporter.export_weighted_session_analysis(session, project)
exporter.export_icp_focused_report(session, project)
```

## 🎯 Key Design Principles

1. **Strategic Prioritization**: PersonaWeight system allows focusing analysis on most important customer segments

2. **Rich Context**: BackgroundInformation provides AI agents with comprehensive project context

3. **Flexible Analysis**: Both weighted (strategic) and unweighted (equal) analysis modes

4. **Data Integrity**: Comprehensive validation and error handling

5. **Export Compatibility**: Multiple formats (JSON, CSV, JSONL) for different use cases

6. **Extensibility**: Models designed to accommodate future features and integrations

The data model enables both simple focus groups and sophisticated strategic research with AI-powered analysis and persona prioritization.