"""
Main application interface for Synthetic Focus Groups.
"""

import argparse
import sys
import os
import json
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project_manager import ProjectManager
from personas.manager import PersonaManager
from personas.generator import PersonaGenerator
from facilitator.manager import FacilitatorManager
from export.exporter import DataExporter
from models.session import Session, SessionResponse, ResponseType


class SyntheticFocusGroupApp:
    """Main application class for managing synthetic focus groups."""
    
    def __init__(self):
        """Initialize the application with all managers."""
        self.project_manager = ProjectManager()
        self.persona_manager = PersonaManager()
        self.persona_generator = PersonaGenerator()
        self.facilitator_manager = FacilitatorManager()
        self.data_exporter = DataExporter()
        
        print("Synthetic Focus Groups System Initialized")
        print("=" * 50)
    
    def setup_default_data(self):
        """Set up default facilitators and sample personas."""
        print("Setting up default data...")
        
        # Create default facilitators
        facilitators = self.facilitator_manager.create_default_facilitators()
        print(f"Created {len(facilitators)} default facilitators")
        
        # Generate sample personas if none exist
        existing_personas = self.persona_manager.get_all_personas()
        if len(existing_personas) < 5:
            sample_personas = self.persona_generator.generate_personas(count=15, ensure_diversity=True)
            for persona in sample_personas:
                self.persona_manager.personas[persona.id] = persona
            self.persona_manager._save_personas()
            print(f"Generated {len(sample_personas)} sample personas")
        else:
            print(f"Found {len(existing_personas)} existing personas")
        
        print("Default data setup complete!")
        print()
    
    def create_sample_project(self, name: str = "Sample Consumer Research", 
                            topic: str = "Consumer Technology Preferences") -> str:
        """Create a sample project for demonstration."""
        print(f"Creating sample project: {name}")
        
        # Create project
        project = self.project_manager.create_project(
            name=name,
            research_topic=topic,
            description="Sample project to demonstrate synthetic focus group capabilities",
            research_questions=[
                "What factors influence your technology purchasing decisions?",
                "How do you research new technology products?",
                "What role does price play in your decision-making?",
                "How important are reviews and recommendations?",
                "What frustrations do you have with current technology products?"
            ],
            target_insights=[
                "Identify key decision-making factors",
                "Understand research behaviors",
                "Explore price sensitivity",
                "Assess influence of social proof",
                "Discover pain points and opportunities"
            ],
            max_participants=10,
            min_participants=6
        )
        
        # Configure personas (get diverse sample)
        success = self.project_manager.configure_project_personas(
            project.id, 
            count=8
        )
        
        if success:
            print(f"Configured {len(project.persona_ids)} personas for project")
        
        # Auto-suggest facilitator
        success = self.project_manager.configure_project_facilitator(
            project.id, 
            auto_suggest=True
        )
        
        if success:
            print("Assigned facilitator to project")
        
        # Check project readiness
        readiness = self.project_manager.get_project_readiness(project.id)
        print(f"Project readiness: {'✓ Ready' if readiness['ready'] else '✗ Not Ready'}")
        
        if not readiness['ready']:
            for error in readiness['validation_errors']:
                print(f"  - {error}")
        
        print(f"Sample project created with ID: {project.id}")
        print()
        return project.id
    
    def list_projects(self):
        """List all projects."""
        projects = self.project_manager.get_all_projects()
        
        if not projects:
            print("No projects found.")
            return
        
        print(f"Found {len(projects)} project(s):")
        print("-" * 80)
        
        for project in projects:
            facilitator = self.facilitator_manager.get_facilitator(project.facilitator_id) if project.facilitator_id else None
            
            print(f"ID: {project.id}")
            print(f"Name: {project.name}")
            print(f"Topic: {project.research_topic}")
            print(f"Status: {project.status}")
            print(f"Participants: {len(project.persona_ids)}/{project.max_participants}")
            print(f"Facilitator: {facilitator.name if facilitator else 'Not assigned'}")
            print(f"Created: {project.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            # Check readiness
            readiness = self.project_manager.get_project_readiness(project.id)
            status = "✓ Ready" if readiness['ready'] else "✗ Not Ready"
            print(f"Ready to run: {status}")
            print("-" * 80)
    
    def show_project_details(self, project_id: str):
        """Show detailed information about a project."""
        project = self.project_manager.get_project(project_id)
        if not project:
            print(f"Project {project_id} not found.")
            return
        
        facilitator = self.facilitator_manager.get_facilitator(project.facilitator_id) if project.facilitator_id else None
        
        print(f"PROJECT DETAILS: {project.name}")
        print("=" * 60)
        print(f"ID: {project.id}")
        print(f"Research Topic: {project.research_topic}")
        print(f"Description: {project.description}")
        print(f"Status: {project.status}")
        print(f"Created: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("RESEARCH QUESTIONS:")
        for i, question in enumerate(project.research_questions, 1):
            print(f"{i}. {question}")
        print()
        
        print("TARGET INSIGHTS:")
        for insight in project.target_insights:
            print(f"• {insight}")
        print()
        
        print(f"FACILITATOR: {facilitator.name if facilitator else 'Not assigned'}")
        if facilitator:
            print(f"  Expertise: {facilitator.expertise_area}")
            print(f"  Style: {facilitator.moderation_style}")
            print(f"  Approach: {facilitator.questioning_approach}")
        print()
        
        print(f"PARTICIPANTS ({len(project.persona_ids)}/{project.max_participants}):")
        for persona_id in project.persona_ids:
            persona = self.persona_manager.get_persona(persona_id)
            if persona:
                print(f"• {persona.name} - {persona.age}yo {persona.gender} - {persona.occupation}")
        print()
        
        # Show readiness
        readiness = self.project_manager.get_project_readiness(project_id)
        print("PROJECT READINESS:")
        print(f"Ready to run: {'✓ Yes' if readiness['ready'] else '✗ No'}")
        
        if not readiness['ready']:
            print("Issues to resolve:")
            for error in readiness['validation_errors']:
                print(f"  - {error}")
    
    def create_demo_session(self, project_id: str) -> str:
        """Create a demonstration session with mock data."""
        project = self.project_manager.get_project(project_id)
        if not project:
            print(f"Project {project_id} not found.")
            return None
        
        print(f"Creating demonstration session for project: {project.name}")
        
        # Create session
        session = Session(
            project_id=project.id,
            name=f"Demo Session - {project.name}",
            description="Demonstration session with simulated responses",
            facilitator_id=project.facilitator_id,
            participant_ids=project.persona_ids[:8],  # Use first 8 participants
            primary_questions=project.research_questions
        )
        
        # Start session
        session.start_session()
        print("Session started...")
        
        # Generate mock responses for demonstration
        facilitator = self.facilitator_manager.get_facilitator(project.facilitator_id)
        
        for i, question in enumerate(project.research_questions[:3]):  # Just do first 3 questions
            print(f"Processing question {i+1}: {question[:50]}...")
            
            # Facilitator asks question
            session.add_response(SessionResponse(
                response_type=ResponseType.FACILITATOR_QUESTION,
                speaker_id=session.facilitator_id,
                speaker_name=facilitator.name if facilitator else "Facilitator",
                speaker_type="facilitator",
                content=question,
                question_id=f"q_{i+1}"
            ))
            
            # Each participant responds
            for j, participant_id in enumerate(session.participant_ids):
                persona = self.persona_manager.get_persona(participant_id)
                if persona:
                    # Generate a realistic response based on persona
                    response_content = self._generate_mock_response(question, persona)
                    
                    session.add_response(SessionResponse(
                        response_type=ResponseType.PARTICIPANT_RESPONSE,
                        speaker_id=participant_id,
                        speaker_name=persona.name,
                        speaker_type="participant",
                        content=response_content,
                        question_id=f"q_{i+1}",
                        sentiment_score=0.1 + (j * 0.1)  # Mock sentiment
                    ))
        
        # End session
        session.end_session()
        print("Session completed!")
        
        # Add some mock analysis
        session.key_insights = [
            "Price is a major factor but not the only consideration",
            "Participants rely heavily on online reviews and recommendations",
            "Brand reputation influences trust and purchase decisions",
            "User experience and ease of use are increasingly important"
        ]
        
        session.themes_discovered = [
            "Value for money",
            "Social proof",
            "Brand trust",
            "Usability",
            "Innovation"
        ]
        
        session.overall_sentiment = 0.3  # Slightly positive
        
        print(f"Demo session created with {len(session.responses)} responses")
        print(f"Session ID: {session.id}")
        print()
        
        return session.id
    
    def _generate_mock_response(self, question: str, persona) -> str:
        """Generate a mock response based on question and persona characteristics."""
        question_lower = question.lower()
        
        # Technology purchasing decisions
        if "purchasing" in question_lower and "technology" in question_lower:
            responses = [
                f"As a {persona.occupation.lower()}, I really need technology that's reliable and efficient. Price matters, but I'm willing to pay more for quality.",
                f"I always look at reviews first. Being {', '.join(persona.personality_traits[:2])}, I want to make sure I'm getting something that will work well for me.",
                f"My budget is important, but I've learned that cheaper isn't always better. I'd rather invest in something that lasts."
            ]
        
        # Research behaviors
        elif "research" in question_lower:
            responses = [
                f"I spend a lot of time reading reviews online. I check multiple sites and look for patterns in what people say.",
                f"I usually ask friends and colleagues for recommendations first. Then I do my own research to validate their suggestions.",
                f"YouTube reviews are really helpful for me. I like seeing the product in action before I buy."
            ]
        
        # Price sensitivity
        elif "price" in question_lower:
            responses = [
                f"Price is definitely a factor, but it's not everything. I look at the overall value - features, durability, support.",
                f"I have a budget, but I'm flexible if something offers significantly better features or quality.",
                f"I compare prices across different retailers, but I also factor in warranty and return policies."
            ]
        
        # Reviews and recommendations
        elif "review" in question_lower or "recommendation" in question_lower:
            responses = [
                f"Reviews are crucial for me. I look for detailed reviews that mention both pros and cons.",
                f"I trust recommendations from people I know more than online reviews, but I still do my research.",
                f"I look for reviews from people who seem to have similar needs and use cases as me."
            ]
        
        # General frustrations
        else:
            responses = [
                f"One thing that frustrates me is when products don't work as advertised. I appreciate honest marketing.",
                f"Customer support is really important. When something goes wrong, I need to be able to get help quickly.",
                f"I wish more companies would focus on making their products intuitive and easy to use."
            ]
        
        import random
        return random.choice(responses)
    
    def export_session_data(self, session_id: str, formats: List[str] = None):
        """Export session data in specified formats."""
        if formats is None:
            formats = ['json', 'csv']
        
        # Create a mock session for demonstration (in real implementation, load from storage)
        print(f"Exporting session data in formats: {', '.join(formats)}")
        
        # For demonstration, create a basic session
        session = Session(
            id=session_id,
            name="Demo Session Export",
            project_id="demo_project"
        )
        
        try:
            exported_files = self.data_exporter.export_session_complete(session, formats)
            
            print("Export completed successfully!")
            for format_name, filepath in exported_files.items():
                print(f"  {format_name}: {filepath}")
            
            return exported_files
            
        except Exception as e:
            print(f"Export failed: {e}")
            return None
    
    def show_statistics(self):
        """Show system statistics."""
        print("SYSTEM STATISTICS")
        print("=" * 50)
        
        # Project statistics
        project_stats = self.project_manager.get_project_statistics()
        print(f"Projects: {project_stats['total_projects']}")
        if project_stats['status_distribution']:
            for status, count in project_stats['status_distribution'].items():
                print(f"  {status}: {count}")
        
        # Persona statistics
        persona_stats = self.persona_manager.get_statistics()
        print(f"Personas: {persona_stats['total_personas']} total, {persona_stats['active_personas']} active")
        
        # Facilitator statistics
        facilitator_stats = self.facilitator_manager.get_statistics()
        print(f"Facilitators: {facilitator_stats['total_facilitators']} total, {facilitator_stats['active_facilitators']} active")
        
        # Export statistics
        export_stats = self.data_exporter.get_export_statistics()
        print(f"Exported files: {export_stats['total_files']} files, {export_stats['total_size_mb']} MB")
        
        print()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Synthetic Focus Groups System")
    parser.add_argument('--setup', action='store_true', help='Set up default data')
    parser.add_argument('--create-sample', action='store_true', help='Create sample project')
    parser.add_argument('--list-projects', action='store_true', help='List all projects')
    parser.add_argument('--project-details', type=str, help='Show project details by ID')
    parser.add_argument('--demo-session', type=str, help='Create demo session for project ID')
    parser.add_argument('--export', type=str, help='Export session data by session ID')
    parser.add_argument('--export-formats', nargs='+', default=['json', 'csv'], 
                       help='Export formats (json, csv, summary, participant_analysis)')
    parser.add_argument('--stats', action='store_true', help='Show system statistics')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Initialize application
    app = SyntheticFocusGroupApp()
    
    # Handle commands
    if args.setup:
        app.setup_default_data()
        
    elif args.create_sample:
        project_id = app.create_sample_project()
        print(f"Sample project created. Use --project-details {project_id} to view details")
        
    elif args.list_projects:
        app.list_projects()
        
    elif args.project_details:
        app.show_project_details(args.project_details)
        
    elif args.demo_session:
        session_id = app.create_demo_session(args.demo_session)
        if session_id:
            print(f"Demo session created. Use --export {session_id} to export data")
        
    elif args.export:
        app.export_session_data(args.export, args.export_formats)
        
    elif args.stats:
        app.show_statistics()
        
    elif args.interactive:
        print("Interactive mode not yet implemented. Use --help to see available commands.")
        
    else:
        print("Synthetic Focus Groups System")
        print("Use --help to see available commands")
        print("Quick start: python src/main.py --setup --create-sample")


if __name__ == "__main__":
    main()