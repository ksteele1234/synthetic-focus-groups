# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Essential Commands

### Setup & Installation
```bash
# Setup system with default data (required first step)
python src/main.py --setup

# Install optional dependencies
pip install -r requirements.txt

# Run basic system validation
python src/main.py --stats
```

### Project Management
```bash
# Create sample project for testing
python src/main.py --create-sample

# List all projects
python src/main.py --list-projects

# View project details (replace with actual project ID)
python src/main.py --project-details <project-id>
```

### Session Execution
```bash
# PREFERRED: Launch web interface for one-click studies
python start_web_app.py
# Opens http://localhost:8501 with full UI

# Alternative: Run demo session for a project (CLI)
python src/main.py --demo-session <project-id>

# Quick demo session with single command runner (CLI)
python run_synthetic_session.py

# Export session data in multiple formats (CLI)
python src/main.py --export <session-id> --export-formats json csv summary
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run integration test that demonstrates enhanced system
python -m pytest tests/test_enhanced_integration.py -v

# Run specific test with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Architecture Overview

### High-Level System Design
This is a **multi-agent AI-powered synthetic focus group system** with **one-click study capabilities**:

1. **Web Interface Layer** (`app.py`, `start_web_app.py`): Streamlit-based one-click study creator and session manager
2. **Core Models Layer** (`src/models/`): Data structures for projects, personas, sessions, and enhanced analytics
3. **AI Agents Layer** (`src/ai/`): Specialized AI agents for research workflows
4. **Visualization Layer** (`src/visualizations/`, `src/reports/`): Chart generation and markdown report creation
5. **Management Layer** (`src/*/manager.py`): Business logic coordinators for different components

### Key Architectural Concepts

#### Enhanced vs. Standard Models
- **Standard Models** (`models/project.py`, `models/persona.py`): Basic focus group functionality
- **Enhanced Models** (`models/enhanced_project.py`): Advanced features with persona weighting, ICP designation, and AI agent integration
- Use Enhanced models for production; Standard models for basic testing

#### Agent System Architecture
The system uses specialized AI agents that coordinate through an orchestrator:
- **OrchestratorAgent**: Manages workflows and coordinates other agents
- **SurveyMethodologistAgent**: Validates research design and methodology
- **QualitativeCodingSpecialist**: Analyzes responses for themes and insights  
- **DataVisualizationDesigner**: Creates charts and executive dashboards

#### Persona Weighting System
- Personas can have weights (0.1-5.0) to prioritize insights from key customer segments
- Primary ICP (Ideal Customer Profile) designation for strategic analysis focus
- Weighted sentiment analysis and response prioritization

### Critical File Structure
```
# ONE-CLICK WEB INTERFACE
app.py                        # Streamlit web application (MAIN ENTRY POINT)
start_web_app.py             # Launch script for web interface
templates/                    # Bulk upload templates (CSV, JSON, TXT)

src/
├── models/
│   ├── enhanced_project.py     # Core project model with weighting
│   ├── session.py             # Session and response management
│   └── qa_turn.py            # Q&A turn data structure
├── ai/
│   ├── agents.py             # All specialized AI agents
│   └── openai_client.py      # AI service integration
├── visualizations/
│   └── chart_generator.py    # PNG/SVG chart generation from specs
├── reports/
│   └── markdown_generator.py # Summary/detailed markdown reports
├── export/
│   ├── enhanced_exporter.py  # Advanced export with weighting
│   └── exporter.py          # Basic export functionality
├── session/
│   └── synthetic_runner.py   # End-to-end session orchestration
└── main.py                   # CLI entry point (alternative to web)
```

### Data Flow Architecture (One-Click Studies)
1. **Web Study Creator**: User configures study via Streamlit interface with persona weighting
2. **Bulk Upload Support**: CSV/JSON persona upload + TXT/CSV questions upload with templates
3. **One-Click Session Launch**: Automated session execution with real-time progress tracking
4. **Live Results Display**: Charts, insights, and transcripts appear immediately in web UI
5. **Multi-Agent Analysis**: Methodology validation → Thematic coding → Visualization → Final report
6. **Auto-Generated Exports**: Markdown reports, PNG charts, CSV data created automatically
7. **Download Hub**: All results available for immediate download from web interface

## Development Workflows

### Creating New Agent Types
When adding new AI agents:
1. Inherit from `BaseAgent` in `src/ai/agents.py`
2. Implement `process()` method with task handling
3. Register with `OrchestratorAgent` for workflow coordination
4. Add corresponding export logic in `enhanced_exporter.py`

### Adding Export Formats
New export formats should be added to `EnhancedDataExporter`:
1. Create method following pattern `export_<format>_<analysis_type>()`
2. Handle weighted analysis and ICP focus appropriately
3. Include agent results integration
4. Add to CLI export options in `main.py`

### Session Data Validation
All session data must conform to structured schemas:
- Use `QATurn` model for standardized Q&A exchanges
- Validate with `validate_schema()` methods
- Storage automatically validates JSONL format compliance

### AI Integration Points
The system has built-in AI integration points but works without AI:
- **With AI**: Real OpenAI API calls for dynamic responses and analysis
- **Fallback Mode**: Pre-defined responses and mock analysis for testing
- Toggle via `OpenAIClient` availability and configuration

### Enhanced vs Standard Project Usage
```python
# Standard Project (basic functionality)
from project_manager import ProjectManager
pm = ProjectManager()
project = pm.create_project(name="Basic Study", research_topic="Topic")

# Enhanced Project (advanced features)
from models.enhanced_project import EnhancedProject, PersonaWeight
project = EnhancedProject(
    weighted_analysis_enabled=True,
    persona_weights=[
        PersonaWeight(persona_id="user1", weight=3.0, is_primary_icp=True),
        PersonaWeight(persona_id="user2", weight=1.5)
    ]
)
```

## Testing Strategy

### Integration Test as Reference
The `test_enhanced_integration.py` demonstrates the complete system workflow:
- Enhanced project creation with persona weighting
- Multi-agent analysis coordination  
- Weighted export generation
- Validation of all data schemas

Use this test as a reference for understanding the full system capabilities.

### Test Data Generation
- `create_sample_personas()` creates realistic test personas
- `SyntheticSessionRunner` generates complete Q&A sessions
- Enhanced models include built-in mock data for testing

## Important Implementation Notes

### PowerShell/Windows Compatibility
- All file paths use `os.path.join()` for cross-platform compatibility
- CLI commands tested on Windows PowerShell
- Use absolute paths when calling Python modules

### AI Client Configuration
- System gracefully degrades when AI services unavailable
- Mock responses maintain data structure consistency
- Real AI integration requires API key configuration in `openai_client.py`

### Data Persistence
- Projects stored in `data/projects/projects.json`
- Sessions can be persisted via `QAStorage` class
- Export files generated in `data/exports/` by default

### Memory and Performance
- Persona generation can create up to 20 participants efficiently
- Session responses stored in-memory during execution
- Large sessions should use streaming export for better performance

## Core Business Logic

### Project Readiness Validation
Projects must meet criteria before session execution:
- Minimum participant count (configurable)
- Assigned facilitator
- Research questions defined
- Use `get_project_readiness()` to validate

### Weighted Analysis Logic
- Weights applied to sentiment scores and theme frequency
- ICP responses get additional analysis depth
- Results stratified by importance tiers (high/medium/low priority personas)

### Agent Coordination Dependencies
Agents have specific execution dependencies:
1. Methodology validation (independent)  
2. Response analysis (requires session data)
3. Visualization (requires analysis results)
4. Final report (requires all previous steps)