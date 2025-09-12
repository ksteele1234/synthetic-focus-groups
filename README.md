# Synthetic Focus Groups

A comprehensive system for conducting AI-powered synthetic focus groups where both moderators and participants are digital personas. Perfect for market research, user experience studies, and product development insights.

## 🎯 Overview

This system enables researchers to:
- Create and manage diverse AI personas (up to 20 participants)
- Configure AI facilitators with different moderation styles
- Run synthetic focus group sessions with realistic interactions
- Export comprehensive data in JSON and CSV formats
- Analyze results with AI-powered research insights

## 🏗️ Architecture

```
synthetic-focus-groups/
├── src/
│   ├── models/           # Core data models
│   ├── personas/         # Persona management system  
│   ├── facilitator/      # AI moderator system
│   ├── session/          # Focus group session engine
│   ├── analysis/         # Research analyst component
│   ├── export/           # Data export functionality
│   └── main.py          # Main application interface
├── config/              # Configuration files
├── data/               # Storage for personas, projects, sessions
├── examples/           # Sample configurations
└── tests/             # Test suites
```

## 🚀 Quick Start

### 1. Setup
```bash
# Clone and navigate to project
cd synthetic-focus-groups

# Install dependencies (optional - core system works with Python stdlib)
pip install -r requirements.txt

# Initialize system with default data
python src/main.py --setup
```

### 2. Create Your First Project
```bash
# Create a sample project
python src/main.py --create-sample

# List all projects
python src/main.py --list-projects

# View project details (use actual project ID)
python src/main.py --project-details <project-id>
```

### 3. Run a Demo Session
```bash
# Create a demonstration session
python src/main.py --demo-session <project-id>

# Export session data
python src/main.py --export <session-id> --export-formats json csv
```

## 🧑‍🤝‍🧑 Personas

### Built-in Persona Generator
The system includes a sophisticated persona generator that creates diverse, realistic participants:

```python
from src.personas.generator import PersonaGenerator

generator = PersonaGenerator()

# Generate diverse personas
personas = generator.generate_personas(count=10, ensure_diversity=True)

# Generate targeted personas
healthcare_personas = generator.generate_preset_personas('healthcare')

# Generate personas with specific criteria
personas = generator.generate_personas(
    count=5, 
    gender='female',
    age_range=(25, 45),
    occupation='Teacher'
)
```

### Persona Characteristics
Each persona includes:
- **Demographics**: Age, gender, location, occupation, education, income
- **Psychographics**: Personality traits, values, interests, lifestyle
- **Behavioral Patterns**: Communication style, response tendency, emotional expression
- **Background**: Personal story and relevant experiences

## 🎙️ Facilitators

### Default Facilitators
The system includes 4 pre-configured facilitators:

1. **Dr. Sarah Chen** - Consumer Research (Balanced/Probing/Professional)
2. **Marcus Rodriguez** - Healthcare Research (Empathetic/Empathetic/Friendly)  
3. **Dr. Emily Watson** - Technology & Innovation (Collaborative/Analytical/Casual)
4. **James Thompson** - Product Development (Directive/Direct/Authoritative)

### Facilitator Capabilities
- Generate 3-5 contextual follow-up questions per participant
- Adapt questioning style based on research objectives
- Manage session flow and time
- Synthesize insights during sessions

## 📊 Projects & Configuration

### Easy Project Setup
```python
from src.project_manager import ProjectManager

pm = ProjectManager()

# Create new project
project = pm.create_project(
    name="Mobile App UX Study",
    research_topic="Mobile App User Experience",
    research_questions=[
        "What frustrations do you have with mobile apps?",
        "What makes an app easy to use?",
        "How important is app speed vs features?"
    ]
)

# Configure participants (auto-select diverse group)
pm.configure_project_personas(project.id, count=8)

# Auto-assign best facilitator for topic
pm.configure_project_facilitator(project.id, auto_suggest=True)
```

### Project Templates
Create reusable project templates:
```python
# Save project as template
template = pm.create_project_template("UX Research Template", project.id)

# Create new project from template
new_project = pm.create_project_from_template(
    "UX Research Template",
    "E-commerce Website Study", 
    "E-commerce User Experience"
)
```

## 📈 Data Export & Analysis

### Export Formats
- **JSON**: Complete session data with full metadata
- **CSV**: Tabular data for analysis in Excel/R/Python
- **Summary**: High-level session metrics and insights  
- **Participant Analysis**: Individual participant breakdowns

### Export Options
```python
from src.export.exporter import DataExporter

exporter = DataExporter()

# Export single session
files = exporter.export_session_complete(session, ['json', 'csv'])

# Create comprehensive data package
package_dir = exporter.create_data_package(session, include_metadata=True)

# Export multiple sessions
combined = exporter.export_multiple_sessions(sessions, combined=True)
```

### Data Package Contents
Each export includes:
- Raw session data
- Response transcripts
- Participant demographics
- Sentiment analysis
- Theme extraction
- Session statistics
- README documentation

## 🔧 Command Line Interface

```bash
# System setup
python src/main.py --setup                          # Initialize with defaults
python src/main.py --stats                          # Show system statistics

# Project management  
python src/main.py --create-sample                  # Create sample project
python src/main.py --list-projects                  # List all projects
python src/main.py --project-details <project-id>   # Show project details

# Session management
python src/main.py --demo-session <project-id>      # Run demo session
python src/main.py --export <session-id>            # Export session data

# Export options
python src/main.py --export <session-id> --export-formats json csv summary
```

## 🎛️ Configuration

### Custom Personas
```python
from src.personas.manager import PersonaManager

pm = PersonaManager()

# Create custom persona
persona = pm.create_persona(
    name="Alex Chen",
    age=32,
    occupation="UX Designer", 
    personality_traits=["analytical", "creative", "detail-oriented"],
    interests=["technology", "design", "user research"],
    background_story="Experienced UX designer passionate about creating intuitive digital experiences..."
)
```

### Custom Facilitators
```python
from src.facilitator.manager import FacilitatorManager

fm = FacilitatorManager()

# Create specialized facilitator
facilitator = fm.create_facilitator(
    name="Dr. Lisa Park",
    expertise_area="Digital Health",
    moderation_style="collaborative",
    questioning_approach="empathetic",
    research_context="Healthcare technology adoption and user experience"
)
```

## 🔮 Extending the System

### AI Integration Points
The system is designed for easy AI integration:

1. **Persona Responses**: Replace mock responses with actual AI-generated responses
2. **Facilitator Questions**: Enhance follow-up question generation with context-aware AI
3. **Real-time Analysis**: Add live sentiment analysis and theme detection
4. **Research Insights**: Implement AI-powered research analysis and recommendations

### Integration Examples
```python
# Placeholder for AI service integration
class AIPersonaEngine:
    def generate_response(self, persona, question, context):
        # Integrate with OpenAI, Anthropic, or other AI service
        pass

class AIFacilitatorEngine:
    def generate_followup_questions(self, response, context):
        # Generate contextual follow-up questions
        pass

class AIResearchAnalyst:
    def analyze_session(self, session_data):
        # Comprehensive session analysis
        pass
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test categories
python -m pytest tests/test_personas.py
python -m pytest tests/test_projects.py
```

## 📋 Use Cases

### Market Research
- Consumer preference studies
- Product concept testing
- Brand perception research
- Purchase decision analysis

### User Experience Research  
- Website/app usability testing
- Feature prioritization
- User journey mapping
- Accessibility evaluation

### Product Development
- Requirements gathering
- Feature validation
- User story development
- Design feedback

### Healthcare Research
- Patient experience studies
- Treatment preference research
- Health behavior analysis
- Medical device usability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions for questions and ideas
- **Documentation**: Additional docs available in the `/docs` folder

## 🗺️ Roadmap

### Phase 1: Core Functionality ✅
- Persona management system
- Project configuration
- Data export capabilities
- Command-line interface

### Phase 2: AI Integration 🔄  
- Real AI-powered persona responses
- Intelligent facilitator interactions
- Advanced analysis capabilities
- Research analyst features

### Phase 3: Advanced Features 📋
- Web-based interface
- Real-time collaboration
- Advanced analytics dashboard
- API endpoints for integration

### Phase 4: Enterprise Features 📋
- Multi-tenant support
- Advanced security features
- Enterprise integrations
- Scalable infrastructure

---

**Ready to revolutionize your research with AI-powered focus groups? Get started today!**

```bash
python src/main.py --setup --create-sample
```