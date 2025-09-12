"""
Project management system for configuring and managing focus group projects.
"""

import json
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.project import Project
from models.persona import Persona
from models.facilitator import Facilitator
from personas.manager import PersonaManager
from facilitator.manager import FacilitatorManager


class ProjectManager:
    """Manages focus group projects with easy configuration and swapping capabilities."""
    
    def __init__(self, storage_path: str = "data/projects"):
        """Initialize project manager with storage path."""
        self.storage_path = storage_path
        self.projects_file = os.path.join(storage_path, "projects.json")
        self.projects: Dict[str, Project] = {}
        
        # Initialize component managers
        self.persona_manager = PersonaManager()
        self.facilitator_manager = FacilitatorManager()
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing projects
        self._load_projects()
    
    def _load_projects(self) -> None:
        """Load projects from storage file."""
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for project_data in data:
                        project = Project.from_dict(project_data)
                        self.projects[project.id] = project
            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Could not load projects from {self.projects_file}: {e}")
    
    def _save_projects(self) -> None:
        """Save projects to storage file."""
        try:
            data = [project.to_dict() for project in self.projects.values()]
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving projects to {self.projects_file}: {e}")
    
    def create_project(self, name: str, research_topic: str, **kwargs) -> Project:
        """Create a new project with provided configuration."""
        project_data = {
            'name': name,
            'research_topic': research_topic,
            **kwargs
        }
        
        project = Project(**project_data)
        self.projects[project.id] = project
        self._save_projects()
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        return self.projects.get(project_id)
    
    def get_all_projects(self, status_filter: str = None) -> List[Project]:
        """Get all projects, optionally filtered by status."""
        projects = list(self.projects.values())
        if status_filter:
            projects = [p for p in projects if p.status == status_filter]
        return projects
    
    def update_project(self, project_id: str, **kwargs) -> Optional[Project]:
        """Update a project with new configuration."""
        project = self.get_project(project_id)
        if not project:
            return None
        
        # Update attributes
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        project.updated_at = datetime.now()
        self._save_projects()
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project by ID."""
        if project_id in self.projects:
            del self.projects[project_id]
            self._save_projects()
            return True
        return False
    
    def configure_project_personas(self, project_id: str, persona_criteria: Dict[str, Any] = None, 
                                 persona_ids: List[str] = None, count: int = 8) -> bool:
        """Configure project personas either by criteria or specific IDs."""
        project = self.get_project(project_id)
        if not project:
            return False
        
        if persona_ids:
            # Use specific persona IDs
            valid_personas = []
            for pid in persona_ids:
                persona = self.persona_manager.get_persona(pid)
                if persona and persona.active:
                    valid_personas.append(pid)
            
            project.persona_ids = valid_personas[:project.max_participants]
        else:
            # Use criteria to select personas
            if persona_criteria:
                personas = self.persona_manager.filter_personas(persona_criteria)
            else:
                # Get diverse sample if no criteria specified
                personas = self.persona_manager.get_diverse_sample(count)
            
            project.persona_ids = [p.id for p in personas[:project.max_participants]]
        
        project.updated_at = datetime.now()
        self._save_projects()
        return True
    
    def configure_project_facilitator(self, project_id: str, facilitator_id: str = None, 
                                    auto_suggest: bool = False) -> bool:
        """Configure project facilitator either by ID or auto-suggestion."""
        project = self.get_project(project_id)
        if not project:
            return False
        
        if facilitator_id:
            # Use specific facilitator
            facilitator = self.facilitator_manager.get_facilitator(facilitator_id)
            if facilitator and facilitator.active:
                project.facilitator_id = facilitator_id
            else:
                return False
        elif auto_suggest:
            # Auto-suggest facilitator based on research topic
            suggested = self.facilitator_manager.suggest_facilitator_for_research(project.research_topic)
            if suggested:
                project.facilitator_id = suggested.id
            else:
                return False
        else:
            return False
        
        project.updated_at = datetime.now()
        self._save_projects()
        return True
    
    def swap_personas(self, project_id: str, remove_persona_ids: List[str] = None, 
                     add_persona_ids: List[str] = None, replacement_criteria: Dict[str, Any] = None) -> bool:
        """Swap personas in a project - remove some, add others."""
        project = self.get_project(project_id)
        if not project:
            return False
        
        # Remove specified personas
        if remove_persona_ids:
            for pid in remove_persona_ids:
                project.remove_persona(pid)
        
        # Add specified personas
        if add_persona_ids:
            for pid in add_persona_ids:
                if len(project.persona_ids) < project.max_participants:
                    persona = self.persona_manager.get_persona(pid)
                    if persona and persona.active:
                        project.add_persona(pid)
        
        # Add personas based on criteria to fill remaining slots
        if replacement_criteria:
            remaining_slots = project.max_participants - len(project.persona_ids)
            if remaining_slots > 0:
                replacement_personas = self.persona_manager.filter_personas(replacement_criteria)
                # Filter out personas already in the project
                replacement_personas = [p for p in replacement_personas if p.id not in project.persona_ids]
                
                for persona in replacement_personas[:remaining_slots]:
                    project.add_persona(persona.id)
        
        project.updated_at = datetime.now()
        self._save_projects()
        return True
    
    def swap_facilitator(self, project_id: str, new_facilitator_id: str = None, 
                        auto_suggest: bool = False) -> bool:
        """Swap the facilitator in a project."""
        return self.configure_project_facilitator(project_id, new_facilitator_id, auto_suggest)
    
    def clone_project(self, project_id: str, new_name: str, **modifications) -> Optional[Project]:
        """Clone an existing project with optional modifications."""
        original = self.get_project(project_id)
        if not original:
            return None
        
        # Create new project based on original
        project_data = original.to_dict()
        project_data.pop('id')  # Remove ID to generate new one
        project_data.pop('created_at')
        project_data.pop('updated_at')
        project_data.pop('last_session_at', None)
        
        # Apply modifications
        project_data['name'] = new_name
        project_data['status'] = 'draft'  # Reset status
        
        for key, value in modifications.items():
            if key in project_data:
                project_data[key] = value
        
        cloned_project = Project.from_dict(project_data)
        self.projects[cloned_project.id] = cloned_project
        self._save_projects()
        
        return cloned_project
    
    def create_project_template(self, template_name: str, base_project_id: str = None) -> Dict[str, Any]:
        """Create a project template from an existing project or default settings."""
        if base_project_id:
            base_project = self.get_project(base_project_id)
            if base_project:
                template = base_project.to_dict()
                # Remove instance-specific data
                template.pop('id')
                template.pop('name')
                template.pop('created_at')
                template.pop('updated_at')
                template.pop('last_session_at', None)
                template.pop('persona_ids')  # Templates shouldn't have specific personas
                template.pop('facilitator_id', None)
                template['template_name'] = template_name
                
                # Save template
                templates_dir = os.path.join(self.storage_path, "templates")
                os.makedirs(templates_dir, exist_ok=True)
                
                template_file = os.path.join(templates_dir, f"{template_name}.json")
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(template, f, indent=2, ensure_ascii=False)
                
                return template
        
        # Create default template
        default_template = {
            'template_name': template_name,
            'description': '',
            'research_topic': '',
            'research_questions': [],
            'target_insights': [],
            'max_participants': 10,
            'min_participants': 5,
            'estimated_duration_minutes': 60,
            'session_structure': [
                "Welcome and introductions",
                "Primary questions discussion",
                "Follow-up and probing questions", 
                "Final thoughts and wrap-up"
            ],
            'collect_demographics': True,
            'collect_verbatim_responses': True,
            'collect_sentiment_analysis': True,
            'export_formats': ['json', 'csv'],
            'auto_analyze': True
        }
        
        return default_template
    
    def create_project_from_template(self, template_name: str, project_name: str, 
                                   research_topic: str, **overrides) -> Optional[Project]:
        """Create a new project from a template."""
        templates_dir = os.path.join(self.storage_path, "templates")
        template_file = os.path.join(templates_dir, f"{template_name}.json")
        
        if not os.path.exists(template_file):
            return None
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            # Apply project-specific settings
            template['name'] = project_name
            template['research_topic'] = research_topic
            template.pop('template_name')
            
            # Apply overrides
            for key, value in overrides.items():
                if key in template:
                    template[key] = value
            
            project = Project.from_dict(template)
            self.projects[project.id] = project
            self._save_projects()
            
            return project
            
        except Exception as e:
            print(f"Error creating project from template: {e}")
            return None
    
    def get_project_readiness(self, project_id: str) -> Dict[str, Any]:
        """Check project readiness and return status information."""
        project = self.get_project(project_id)
        if not project:
            return {'ready': False, 'error': 'Project not found'}
        
        is_valid, errors = project.validate_configuration()
        
        # Check if personas and facilitator exist and are active
        facilitator = self.facilitator_manager.get_facilitator(project.facilitator_id) if project.facilitator_id else None
        active_personas = []
        
        for pid in project.persona_ids:
            persona = self.persona_manager.get_persona(pid)
            if persona and persona.active:
                active_personas.append(persona)
        
        readiness = {
            'ready': is_valid and facilitator is not None and len(active_personas) >= project.min_participants,
            'validation_errors': errors,
            'facilitator_status': {
                'assigned': project.facilitator_id is not None,
                'exists': facilitator is not None,
                'active': facilitator.active if facilitator else False,
                'name': facilitator.name if facilitator else None
            },
            'persona_status': {
                'assigned_count': len(project.persona_ids),
                'active_count': len(active_personas),
                'min_required': project.min_participants,
                'max_allowed': project.max_participants,
                'personas': [{'id': p.id, 'name': p.name, 'active': p.active} for p in active_personas]
            },
            'configuration_completeness': {
                'has_research_questions': bool(project.research_questions),
                'has_objectives': bool(project.target_insights),
                'has_description': bool(project.description.strip())
            }
        }
        
        return readiness
    
    def get_project_statistics(self) -> Dict[str, Any]:
        """Get statistics about all projects."""
        projects = self.get_all_projects()
        
        if not projects:
            return {
                'total_projects': 0,
                'status_distribution': {},
                'average_participants': 0
            }
        
        # Calculate statistics
        status_distribution = {}
        participant_counts = []
        
        for project in projects:
            status_distribution[project.status] = status_distribution.get(project.status, 0) + 1
            participant_counts.append(len(project.persona_ids))
        
        return {
            'total_projects': len(projects),
            'status_distribution': status_distribution,
            'average_participants': sum(participant_counts) / len(participant_counts) if participant_counts else 0,
            'projects_by_month': self._get_projects_by_month(projects)
        }
    
    def _get_projects_by_month(self, projects: List[Project]) -> Dict[str, int]:
        """Group projects by creation month."""
        by_month = {}
        
        for project in projects:
            month_key = project.created_at.strftime('%Y-%m')
            by_month[month_key] = by_month.get(month_key, 0) + 1
        
        return by_month
    
    def export_project(self, project_id: str, filepath: str, include_references: bool = True) -> bool:
        """Export a project configuration to a file."""
        project = self.get_project(project_id)
        if not project:
            return False
        
        try:
            export_data = {'project': project.to_dict()}
            
            if include_references:
                # Include persona and facilitator data
                export_data['personas'] = []
                for pid in project.persona_ids:
                    persona = self.persona_manager.get_persona(pid)
                    if persona:
                        export_data['personas'].append(persona.to_dict())
                
                if project.facilitator_id:
                    facilitator = self.facilitator_manager.get_facilitator(project.facilitator_id)
                    if facilitator:
                        export_data['facilitator'] = facilitator.to_dict()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting project to {filepath}: {e}")
            return False
    
    def import_project(self, filepath: str, overwrite_existing: bool = False) -> Optional[Project]:
        """Import a project configuration from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project_data = data['project']
            project = Project.from_dict(project_data)
            
            # Check if project already exists
            if project.id in self.projects and not overwrite_existing:
                # Generate new ID for imported project
                project.id = str(uuid.uuid4())
                project.name = f"{project.name} (Imported)"
            
            # Import referenced personas and facilitators if included
            if 'personas' in data:
                for persona_data in data['personas']:
                    persona = Persona.from_dict(persona_data)
                    if persona.id not in self.persona_manager.personas:
                        self.persona_manager.personas[persona.id] = persona
                self.persona_manager._save_personas()
            
            if 'facilitator' in data:
                facilitator_data = data['facilitator']
                facilitator = Facilitator.from_dict(facilitator_data)
                if facilitator.id not in self.facilitator_manager.facilitators:
                    self.facilitator_manager.facilitators[facilitator.id] = facilitator
                self.facilitator_manager._save_facilitators()
            
            # Save imported project
            self.projects[project.id] = project
            self._save_projects()
            
            return project
            
        except Exception as e:
            print(f"Error importing project from {filepath}: {e}")
            return None