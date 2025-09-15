"""
Specialized AI agents for research workflow management and analysis.
"""

import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from abc import ABC, abstractmethod

from .openai_client import OpenAIClient, create_openai_client


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, name: str, role: str, ai_client: OpenAIClient = None):
        """Initialize base agent."""
        self.name = name
        self.role = role
        self.ai_client = ai_client
        self.created_at = datetime.now()
        self.agent_id = f"{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
    
    @abstractmethod
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return results."""
        pass
    
    def log_activity(self, activity: str, details: Dict[str, Any] = None) -> None:
        """Log agent activity."""
        log_entry = {
            'agent_id': self.agent_id,
            'agent_name': self.name,
            'timestamp': datetime.now().isoformat(),
            'activity': activity,
            'details': details or {}
        }
        # In a full implementation, this would go to a proper logging system
        print(f"[{self.name}] {activity}")


class OrchestratorAgent(BaseAgent):
    """Orchestrator/Project Manager agent that directs workflow and coordinates other agents."""
    
    def __init__(self, ai_client: OpenAIClient = None):
        """Initialize orchestrator agent."""
        super().__init__("Research Orchestrator", "Project Manager", ai_client)
        self.agents_registry: Dict[str, BaseAgent] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
    def register_agent(self, agent_type: str, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self.agents_registry[agent_type] = agent
        self.log_activity(f"Registered {agent_type} agent", {'agent_name': agent.name})
    
    def create_workflow(self, project_data: Dict[str, Any], workflow_type: str = "full_research") -> str:
        """Create a research workflow."""
        workflow_id = f"workflow_{int(datetime.now().timestamp())}"
        
        # Define workflow steps based on type
        if workflow_type == "full_research":
            workflow_steps = [
                {"agent": "methodologist", "task": "validate_research_design", "dependencies": []},
                {"agent": "facilitator", "task": "conduct_session", "dependencies": ["validate_research_design"]},
                {"agent": "coding_specialist", "task": "analyze_responses", "dependencies": ["conduct_session"]},
                {"agent": "viz_designer", "task": "create_visuals", "dependencies": ["analyze_responses"]},
                {"agent": "orchestrator", "task": "generate_final_report", "dependencies": ["create_visuals"]}
            ]
        elif workflow_type == "quick_analysis":
            workflow_steps = [
                {"agent": "coding_specialist", "task": "analyze_responses", "dependencies": []},
                {"agent": "orchestrator", "task": "generate_summary", "dependencies": ["analyze_responses"]}
            ]
        elif workflow_type == "persona_research_and_build":
            workflow_steps = [
                {"agent": "persona_research", "task": "build_dossier", "dependencies": []},
                {"agent": "persona_compiler", "task": "compile_personas", "dependencies": ["build_dossier"]},
                {"agent": "orchestrator", "task": "generate_summary", "dependencies": ["compile_personas"]}
            ]
        else:
            workflow_steps = [
                {"agent": "orchestrator", "task": "custom_workflow", "dependencies": []}
            ]
        
        self.active_workflows[workflow_id] = {
            'project_data': project_data,
            'workflow_type': workflow_type,
            'steps': workflow_steps,
            'completed_steps': [],
            'current_step': 0,
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'results': {}
        }
        
        self.log_activity(f"Created {workflow_type} workflow", {'workflow_id': workflow_id})
        return workflow_id
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a research workflow."""
        if workflow_id not in self.active_workflows:
            return {'success': False, 'error': 'Workflow not found'}
        
        workflow = self.active_workflows[workflow_id]
        workflow['status'] = 'running'
        
        self.log_activity(f"Executing workflow {workflow_id}")
        
        try:
            # Execute steps in dependency order
            for step_index, step in enumerate(workflow['steps']):
                # Check if dependencies are met
                if not self._check_dependencies(workflow, step['dependencies']):
                    continue
                
                agent_type = step['agent']
                task_type = step['task']
                
                # Get agent and execute task
                if agent_type == 'orchestrator':
                    result = self._execute_orchestrator_task(task_type, workflow['project_data'])
                elif agent_type in self.agents_registry:
                    agent = self.agents_registry[agent_type]
                    task_data = {
                        'task_type': task_type,
                        'project_data': workflow['project_data'],
                        'previous_results': workflow['results']
                    }
                    # Special payloads for persona workflow
                    if agent_type == 'persona_research' and task_type == 'build_dossier':
                        task_data.update({
                            'topic': workflow['project_data'].get('research_topic') or workflow['project_data'].get('name', ''),
                            'region': workflow['project_data'].get('region', 'US'),
                            'include_social': True
                        })
                    if agent_type == 'persona_compiler' and task_type == 'compile_personas':
                        dossier_key = 'persona_research_build_dossier'
                        dossier_res = workflow['results'].get(dossier_key, {})
                        task_data.update({
                            'dossier': dossier_res.get('dossier', {}),
                            'n_personas': workflow['project_data'].get('n_personas', 3)
                        })
                    result = agent.process(task_data)
                else:
                    result = {'success': False, 'error': f'Agent {agent_type} not registered'}
                
                # Store results
                workflow['results'][f"{agent_type}_{task_type}"] = result
                workflow['completed_steps'].append(step_index)
                workflow['current_step'] = step_index + 1
                
                self.log_activity(f"Completed step {step_index}: {agent_type}_{task_type}")
            
            workflow['status'] = 'completed'
            return {'success': True, 'workflow_id': workflow_id, 'results': workflow['results']}
            
        except Exception as e:
            workflow['status'] = 'failed'
            workflow['error'] = str(e)
            return {'success': False, 'error': str(e)}
    
    def _check_dependencies(self, workflow: Dict[str, Any], dependencies: List[str]) -> bool:
        """Check if workflow dependencies are met."""
        if not dependencies:
            return True
        
        completed_tasks = [f"{step['agent']}_{step['task']}" for i, step in enumerate(workflow['steps']) 
                          if i in workflow['completed_steps']]
        
        return all(dep in completed_tasks for dep in dependencies)
    
    def _execute_orchestrator_task(self, task_type: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestrator-specific tasks."""
        if task_type == "generate_final_report":
            return self._generate_final_report(project_data)
        elif task_type == "generate_summary":
            return self._generate_summary(project_data)
        else:
            return {'success': False, 'error': f'Unknown orchestrator task: {task_type}'}
    
    def _generate_final_report(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final research report."""
        if self.ai_client:
            return self.ai_client.generate_research_report(
                project_data, 
                project_data.get('background_info', {})
            )
        else:
            return {
                'success': True, 
                'report': 'Final research report generated (AI client not available)',
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_summary(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary report."""
        return {
            'success': True,
            'summary': f"Research summary for project: {project_data.get('name', 'Unknown')}",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow status."""
        if workflow_id not in self.active_workflows:
            return {'error': 'Workflow not found'}
        
        workflow = self.active_workflows[workflow_id]
        return {
            'workflow_id': workflow_id,
            'status': workflow['status'],
            'current_step': workflow['current_step'],
            'total_steps': len(workflow['steps']),
            'completed_steps': len(workflow['completed_steps']),
            'progress_percentage': (len(workflow['completed_steps']) / len(workflow['steps'])) * 100
        }
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process orchestrator tasks."""
        task_type = task.get('task_type', 'coordinate')
        
        if task_type == 'coordinate':
            return self.execute_workflow(task.get('workflow_id'))
        elif task_type == 'create_workflow':
            workflow_id = self.create_workflow(task.get('project_data', {}))
            return {'success': True, 'workflow_id': workflow_id}
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}


class SurveyMethodologistAgent(BaseAgent):
    """Survey Methodologist agent that crafts unbiased questions and research design."""
    
    def __init__(self, ai_client: OpenAIClient = None):
        """Initialize survey methodologist agent."""
        super().__init__("Survey Methodologist", "Research Design Specialist", ai_client)
        self.bias_checks = [
            "leading_questions",
            "response_anchoring", 
            "double_barreled_questions",
            "loaded_language",
            "assumption_based_questions"
        ]
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process methodologist tasks."""
        task_type = task.get('task_type', 'validate_research_design')
        project_data = task.get('project_data', {})
        
        if task_type == 'validate_research_design':
            return self._validate_research_design(project_data)
        elif task_type == 'create_follow_up_heuristics':
            return self._create_follow_up_heuristics(project_data)
        elif task_type == 'design_attention_checks':
            return self._design_attention_checks(project_data)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def _validate_research_design(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate research design and questions for bias."""
        questions = project_data.get('research_questions', [])
        validation_results = {
            'overall_valid': True,
            'bias_warnings': [],
            'suggestions': [],
            'improved_questions': [],
            'methodology_score': 0
        }
        
        for i, question in enumerate(questions):
            question_analysis = self._analyze_question_bias(question)
            
            if question_analysis['has_bias']:
                validation_results['overall_valid'] = False
                validation_results['bias_warnings'].append({
                    'question_index': i,
                    'question': question,
                    'bias_types': question_analysis['bias_types'],
                    'severity': question_analysis['severity']
                })
            
            if question_analysis['improved_version']:
                validation_results['improved_questions'].append({
                    'original': question,
                    'improved': question_analysis['improved_version'],
                    'improvements': question_analysis['improvements']
                })
        
        # Calculate methodology score
        total_questions = len(questions)
        biased_questions = len(validation_results['bias_warnings'])
        validation_results['methodology_score'] = max(0, 100 - (biased_questions / max(total_questions, 1)) * 100)
        
        # Add general suggestions
        if validation_results['methodology_score'] < 80:
            validation_results['suggestions'].extend([
                "Review questions for leading language",
                "Ensure questions are single-focused",
                "Add neutral response options",
                "Consider randomizing question order"
            ])
        
        self.log_activity("Validated research design", {
            'questions_analyzed': len(questions),
            'bias_warnings': len(validation_results['bias_warnings']),
            'methodology_score': validation_results['methodology_score']
        })
        
        return {'success': True, 'validation': validation_results}
    
    def _analyze_question_bias(self, question: str) -> Dict[str, Any]:
        """Analyze a single question for bias."""
        question_lower = question.lower()
        bias_types = []
        has_bias = False
        severity = 'low'
        
        # Check for leading questions
        leading_indicators = ['don\'t you think', 'wouldn\'t you agree', 'isn\'t it true', 'obviously', 'clearly']
        if any(indicator in question_lower for indicator in leading_indicators):
            bias_types.append('leading_question')
            has_bias = True
            severity = 'high'
        
        # Check for double-barreled questions
        if ' and ' in question_lower and '?' in question:
            if question_lower.count(' and ') >= 1:
                bias_types.append('double_barreled')
                has_bias = True
                severity = 'medium'
        
        # Check for loaded language
        loaded_words = ['should', 'must', 'always', 'never', 'best', 'worst', 'terrible', 'amazing']
        if any(word in question_lower for word in loaded_words):
            bias_types.append('loaded_language')
            has_bias = True
            severity = 'medium'
        
        # Generate improved version if biased
        improved_version = None
        improvements = []
        
        if has_bias:
            improved_version = self._improve_question(question, bias_types)
            improvements = [f"Addressed {bt.replace('_', ' ')}" for bt in bias_types]
        
        return {
            'has_bias': has_bias,
            'bias_types': bias_types,
            'severity': severity,
            'improved_version': improved_version,
            'improvements': improvements
        }
    
    def _improve_question(self, question: str, bias_types: List[str]) -> str:
        """Improve a biased question."""
        improved = question
        
        # Remove leading language
        if 'leading_question' in bias_types:
            improved = improved.replace("Don't you think", "What do you think about")
            improved = improved.replace("Wouldn't you agree", "How do you feel about")
            improved = improved.replace("Isn't it true", "To what extent do you believe")
        
        # Split double-barreled questions
        if 'double_barreled' in bias_types and ' and ' in improved:
            parts = improved.split(' and ')
            improved = f"{parts[0]}?"  # Take first part for now
        
        # Neutralize loaded language
        if 'loaded_language' in bias_types:
            improved = improved.replace("should", "would")
            improved = improved.replace("must", "might")
            improved = improved.replace("always", "typically")
            improved = improved.replace("never", "rarely")
        
        return improved
    
    def _create_follow_up_heuristics(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create follow-up question heuristics for facilitators."""
        heuristics = {
            'probing_strategies': [
                {'trigger': 'vague_response', 'follow_up': 'Can you give me a specific example?'},
                {'trigger': 'emotional_response', 'follow_up': 'What makes you feel that way?'},
                {'trigger': 'behavioral_claim', 'follow_up': 'How often does this happen?'},
                {'trigger': 'preference_stated', 'follow_up': 'What factors influence that preference?'},
                {'trigger': 'problem_mentioned', 'follow_up': 'What would an ideal solution look like?'}
            ],
            'depth_questions': [
                "Tell me more about that experience.",
                "What led you to that conclusion?",
                "How does that compare to your past experiences?",
                "What would need to change for you to feel differently?",
                "Can you walk me through your thought process?"
            ],
            'clarification_questions': [
                "When you say [X], what specifically do you mean?",
                "Can you help me understand what that looks like in practice?",
                "What does [concept] mean to you personally?"
            ]
        }
        
        return {'success': True, 'heuristics': heuristics}
    
    def _design_attention_checks(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Design attention check questions."""
        attention_checks = [
            {
                'type': 'instruction_following',
                'question': 'Please select "Agree" for this question to show you are reading carefully.',
                'correct_answer': 'Agree',
                'placement': 'middle'
            },
            {
                'type': 'consistency_check', 
                'question': 'Earlier you mentioned [previous response]. Is this still accurate?',
                'validation': 'check_consistency',
                'placement': 'end'
            },
            {
                'type': 'comprehension_check',
                'question': 'What was the main topic we just discussed?',
                'validation': 'topic_relevance',
                'placement': 'after_major_section'
            }
        ]
        
        return {'success': True, 'attention_checks': attention_checks}


class QualitativeCodingSpecialist(BaseAgent):
    """Qualitative Coding Specialist that converts free-text into reliable codes/themes."""
    
    def __init__(self, ai_client: OpenAIClient = None):
        """Initialize coding specialist agent."""
        super().__init__("Qualitative Coding Specialist", "Data Analysis Expert", ai_client)
        self.coding_frameworks = ['grounded_theory', 'thematic_analysis', 'content_analysis']
        
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process coding specialist tasks."""
        task_type = task.get('task_type', 'analyze_responses')
        
        if task_type == 'analyze_responses':
            return self._analyze_responses(task)
        elif task_type == 'create_coding_scheme':
            return self._create_coding_scheme(task)
        elif task_type == 'validate_themes':
            return self._validate_themes(task)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def _analyze_responses(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze responses and extract themes/codes."""
        session_data = task.get('project_data', {})
        responses = session_data.get('responses', [])
        
        if not responses:
            return {'success': False, 'error': 'No responses to analyze'}
        
        # Use AI client for analysis if available
        if self.ai_client:
            ai_analysis = self.ai_client.analyze_session_themes(
                [r.to_dict() if hasattr(r, 'to_dict') else r for r in responses],
                str(session_data.get('background_info', {}))
            )
            
            if ai_analysis['success']:
                analysis_result = ai_analysis['analysis']
            else:
                analysis_result = self._fallback_analysis(responses)
        else:
            analysis_result = self._fallback_analysis(responses)
        
        # Add coding quality metrics
        coding_quality = self._assess_coding_quality(analysis_result)
        
        result = {
            'success': True,
            'themes': analysis_result.get('themes', []),
            'sentiment': analysis_result.get('sentiment', {}),
            'insights': analysis_result.get('insights', []),
            'patterns': analysis_result.get('patterns', []),
            'recommendations': analysis_result.get('recommendations', []),
            'coding_quality': coding_quality,
            'methodology': 'ai_assisted_thematic_analysis',
            'timestamp': datetime.now().isoformat()
        }
        
        self.log_activity("Analyzed responses", {
            'responses_analyzed': len(responses),
            'themes_identified': len(result['themes']),
            'quality_score': coding_quality.get('overall_score', 0)
        })
        
        return result
    
    def _fallback_analysis(self, responses: List[Any]) -> Dict[str, Any]:
        """Fallback analysis when AI client is not available."""
        # Simple keyword-based theme extraction
        text_content = ""
        for response in responses:
            if hasattr(response, 'content'):
                text_content += response.content + " "
            elif isinstance(response, dict):
                text_content += response.get('content', '') + " "
        
        # Basic theme extraction
        common_themes = ['price', 'quality', 'service', 'convenience', 'trust', 'experience']
        found_themes = []
        
        text_lower = text_content.lower()
        for theme in common_themes:
            if theme in text_lower:
                count = text_lower.count(theme)
                found_themes.append({
                    'theme': theme.title(),
                    'description': f"References to {theme}",
                    'frequency': 'high' if count > 5 else 'medium' if count > 2 else 'low',
                    'participants': ['Multiple participants']
                })
        
        return {
            'themes': found_themes,
            'sentiment': {'overall': 'neutral', 'score': 0.5, 'notes': 'Fallback analysis'},
            'insights': ['Fallback analysis completed'],
            'patterns': [],
            'recommendations': ['Consider using AI analysis for deeper insights']
        }
    
    def _assess_coding_quality(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of the coding analysis."""
        themes = analysis.get('themes', [])
        insights = analysis.get('insights', [])
        
        quality_score = 0
        quality_factors = []
        
        # Theme diversity
        if len(themes) >= 3:
            quality_score += 25
            quality_factors.append('Good theme diversity')
        
        # Theme depth
        detailed_themes = [t for t in themes if len(t.get('description', '')) > 20]
        if len(detailed_themes) >= len(themes) * 0.7:
            quality_score += 25
            quality_factors.append('Detailed theme descriptions')
        
        # Insight quality
        if len(insights) >= 2:
            quality_score += 25
            quality_factors.append('Multiple insights identified')
        
        # Frequency assessment
        frequency_assessed = [t for t in themes if 'frequency' in t]
        if len(frequency_assessed) >= len(themes) * 0.8:
            quality_score += 25
            quality_factors.append('Frequency assessment included')
        
        return {
            'overall_score': quality_score,
            'quality_factors': quality_factors,
            'improvement_suggestions': [] if quality_score >= 75 else [
                'Include more detailed theme descriptions',
                'Assess theme frequency more systematically',
                'Generate more actionable insights'
            ]
        }
    
    def _create_coding_scheme(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a coding scheme for manual validation."""
        themes = task.get('themes', [])
        
        coding_scheme = {
            'categories': [],
            'definitions': {},
            'examples': {},
            'exclusion_criteria': {}
        }
        
        for theme in themes:
            theme_name = theme.get('theme', 'Unnamed Theme')
            coding_scheme['categories'].append(theme_name)
            coding_scheme['definitions'][theme_name] = theme.get('description', 'No description provided')
            coding_scheme['examples'][theme_name] = f"Example responses related to {theme_name}"
            coding_scheme['exclusion_criteria'][theme_name] = f"Exclude responses that don't directly relate to {theme_name}"
        
        return {'success': True, 'coding_scheme': coding_scheme}
    
    def _validate_themes(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate identified themes for consistency."""
        themes = task.get('themes', [])
        
        validation_results = {
            'valid_themes': [],
            'questionable_themes': [],
            'inter_rater_agreement': 0.85,  # Simulated
            'recommendations': []
        }
        
        for theme in themes:
            theme_name = theme.get('theme', '')
            frequency = theme.get('frequency', 'low')
            
            if frequency in ['high', 'medium'] and len(theme.get('description', '')) > 10:
                validation_results['valid_themes'].append(theme)
            else:
                validation_results['questionable_themes'].append({
                    'theme': theme,
                    'concerns': ['Low frequency' if frequency == 'low' else 'Insufficient description']
                })
        
        return {'success': True, 'validation': validation_results}


class DataVisualizationDesigner(BaseAgent):
    """Data Visualization Designer that creates visual insights and dashboards."""
    
    def __init__(self, ai_client: OpenAIClient = None):
        """Initialize visualization designer agent."""
        super().__init__("Data Visualization Designer", "Visual Insights Specialist", ai_client)
        self.chart_types = ['affinity_map', 'theme_ladder', 'kano_chart', 'sentiment_analysis', 'dashboard']
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process visualization tasks."""
        task_type = task.get('task_type', 'create_visuals')
        
        if task_type == 'create_visuals':
            return self._create_visualizations(task)
        elif task_type == 'design_dashboard':
            return self._design_dashboard(task)
        elif task_type == 'create_executive_summary':
            return self._create_executive_summary(task)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def _create_visualizations(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create various visualizations from analysis results."""
        analysis_data = task.get('previous_results', {})
        coding_results = analysis_data.get('coding_specialist_analyze_responses', {})
        
        if not coding_results or not coding_results.get('success'):
            return {'success': False, 'error': 'No analysis data available for visualization'}
        
        themes = coding_results.get('themes', [])
        sentiment = coding_results.get('sentiment', {})
        
        visualizations = {
            'affinity_map': self._create_affinity_map(themes),
            'theme_ladder': self._create_theme_ladder(themes),
            'sentiment_chart': self._create_sentiment_chart(sentiment),
            'insight_dashboard': self._create_insight_dashboard(coding_results),
            'executive_summary_visual': self._create_executive_visual(coding_results)
        }
        
        self.log_activity("Created visualizations", {
            'visualization_count': len(visualizations),
            'themes_visualized': len(themes)
        })
        
        return {'success': True, 'visualizations': visualizations}
    
    def _create_affinity_map(self, themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create affinity map specification."""
        return {
            'type': 'affinity_map',
            'title': 'Theme Affinity Mapping',
            'description': 'Visual clustering of related themes and concepts',
            'clusters': [
                {
                    'cluster_name': theme.get('theme', 'Unknown'),
                    'items': [theme.get('description', 'No description')],
                    'frequency': theme.get('frequency', 'low'),
                    'participants': theme.get('participants', [])
                } for theme in themes
            ],
            'layout': 'force_directed',
            'color_coding': 'by_frequency',
            'interactive': True
        }
    
    def _create_theme_ladder(self, themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create theme ladder specification."""
        # Sort themes by frequency for ladder
        frequency_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_themes = sorted(themes, key=lambda t: frequency_order.get(t.get('frequency', 'low'), 0), reverse=True)
        
        return {
            'type': 'theme_ladder',
            'title': 'Theme Hierarchy and Importance',
            'description': 'Themes arranged by frequency and importance',
            'levels': [
                {
                    'level': i + 1,
                    'theme': theme.get('theme', 'Unknown'),
                    'frequency': theme.get('frequency', 'low'),
                    'description': theme.get('description', ''),
                    'participant_count': len(theme.get('participants', []))
                } for i, theme in enumerate(sorted_themes)
            ],
            'visual_style': 'hierarchical_ladder'
        }
    
    def _create_sentiment_chart(self, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Create sentiment analysis chart."""
        return {
            'type': 'sentiment_analysis',
            'title': 'Overall Sentiment Analysis',
            'overall_sentiment': sentiment.get('overall', 'neutral'),
            'sentiment_score': sentiment.get('score', 0.5),
            'notes': sentiment.get('notes', 'No additional notes'),
            'visual_type': 'gauge_chart',
            'color_scale': ['red', 'yellow', 'green'],
            'interpretation': self._interpret_sentiment(sentiment.get('score', 0.5))
        }
    
    def _interpret_sentiment(self, score: float) -> str:
        """Interpret sentiment score."""
        if score >= 0.7:
            return "Highly positive sentiment detected"
        elif score >= 0.3:
            return "Generally positive sentiment"
        elif score <= -0.3:
            return "Generally negative sentiment"  
        elif score <= -0.7:
            return "Highly negative sentiment detected"
        else:
            return "Neutral sentiment overall"
    
    def _create_insight_dashboard(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive insight dashboard."""
        return {
            'type': 'insight_dashboard',
            'title': 'Research Insights Dashboard',
            'sections': [
                {
                    'section': 'key_metrics',
                    'title': 'Key Metrics',
                    'widgets': [
                        {'type': 'metric', 'label': 'Total Themes', 'value': len(analysis_data.get('themes', []))},
                        {'type': 'metric', 'label': 'Sentiment Score', 'value': analysis_data.get('sentiment', {}).get('score', 0)},
                        {'type': 'metric', 'label': 'Key Insights', 'value': len(analysis_data.get('insights', []))}
                    ]
                },
                {
                    'section': 'theme_distribution',
                    'title': 'Theme Distribution', 
                    'widget': {'type': 'pie_chart', 'data': self._theme_frequency_data(analysis_data.get('themes', []))}
                },
                {
                    'section': 'insights',
                    'title': 'Key Insights',
                    'widget': {'type': 'bullet_list', 'items': analysis_data.get('insights', [])}
                },
                {
                    'section': 'recommendations',
                    'title': 'Recommendations',
                    'widget': {'type': 'action_items', 'items': analysis_data.get('recommendations', [])}
                }
            ],
            'layout': 'executive_friendly',
            'export_formats': ['pdf', 'png', 'interactive_html']
        }
    
    def _theme_frequency_data(self, themes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert themes to frequency chart data."""
        frequency_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        for theme in themes:
            freq = theme.get('frequency', 'low')
            frequency_counts[freq] = frequency_counts.get(freq, 0) + 1
        
        return [
            {'label': 'High Frequency', 'value': frequency_counts['high']},
            {'label': 'Medium Frequency', 'value': frequency_counts['medium']},
            {'label': 'Low Frequency', 'value': frequency_counts['low']}
        ]
    
    def _create_executive_visual(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary visualization."""
        return {
            'type': 'executive_summary',
            'title': 'Executive Summary Visual',
            'format': '2_minute_read',
            'sections': [
                {
                    'title': 'Top 3 Insights',
                    'content': analysis_data.get('insights', [])[:3],
                    'visual': 'highlight_boxes'
                },
                {
                    'title': 'Key Themes', 
                    'content': [t.get('theme', '') for t in analysis_data.get('themes', [])[:5]],
                    'visual': 'tag_cloud'
                },
                {
                    'title': 'Sentiment Overview',
                    'content': analysis_data.get('sentiment', {}),
                    'visual': 'sentiment_indicator'
                },
                {
                    'title': 'Next Steps',
                    'content': analysis_data.get('recommendations', [])[:3],
                    'visual': 'action_checklist'
                }
            ],
            'style': 'executive_presentation',
            'read_time': '2 minutes'
        }
    
    def _design_dashboard(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Design interactive dashboard."""
        return {
            'success': True,
            'dashboard': {
                'title': 'Research Analytics Dashboard',
                'layout': 'responsive_grid',
                'sections': ['overview', 'themes', 'sentiment', 'recommendations'],
                'interactivity': ['filtering', 'drill_down', 'export'],
                'update_frequency': 'real_time'
            }
        }
    
    def _create_executive_summary(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary format."""
        return {
            'success': True,
            'summary': {
                'format': 'executive_brief',
                'read_time': '2_minutes',
                'sections': ['key_takeaways', 'strategic_implications', 'next_steps'],
                'visual_elements': ['infographics', 'key_metrics', 'action_items']
            }
        }


class SafetyAgent(BaseAgent):
    """Safety agent: basic prompt/output moderation and guardrail logging."""
    def __init__(self, ai_client: OpenAIClient = None):
        super().__init__("Safety Agent", "Guardrails", ai_client)
        self.pi_patterns = [
            r"[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}",  # email
            r"\b\+?\d[\d\s\-]{7,}\b"  # phone-ish
        ]
        self.toxic_keywords = ["idiot", "stupid", "hate", "racist"]

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        text = task.get('text', '')
        events = self.check_text(text)
        return {"success": True, "events": events}

    def check_turn(self, question: str, answer: str) -> List[Dict[str, Any]]:
        events = []
        events.extend(self.check_text(question))
        events.extend(self.check_text(answer))
        return events

    def check_text(self, text: str) -> List[Dict[str, Any]]:
        import re
        events = []
        for pat in self.pi_patterns:
            if re.search(pat, text or ""):
                events.append({
                    'type': 'pii_detected', 'severity': 'medium', 'details': {'pattern': pat},
                    'ts': datetime.now().isoformat()
                })
        lower = (text or "").lower()
        if any(k in lower for k in self.toxic_keywords):
            events.append({
                'type': 'toxicity', 'severity': 'low', 'details': {'keywords': self.toxic_keywords},
                'ts': datetime.now().isoformat()
            })
        return events


class ConsistencyAgent(BaseAgent):
    """Detect persona voice drift using simple lexical similarity across answers."""
    def __init__(self, ai_client: OpenAIClient = None):
        super().__init__("Consistency Agent", "Voice Consistency", ai_client)
        self.last_answer_by_persona: Dict[str, str] = {}

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        persona_id = task.get('persona_id')
        answer = task.get('answer', '')
        drift = self.check_drift(persona_id, answer)
        return {"success": True, "drift": drift}

    def check_drift(self, persona_id: str, answer: str) -> Optional[Dict[str, Any]]:
        prev = self.last_answer_by_persona.get(persona_id)
        self.last_answer_by_persona[persona_id] = answer
        if not prev:
            return None
        # Jaccard similarity on word sets as a simple proxy
        def words(s: str):
            import re
            return set(w for w in re.findall(r"[a-zA-Z]+", (s or "").lower()) if len(w) > 2)
        a, b = words(prev), words(answer)
        union = len(a | b) or 1
        jacc = len(a & b) / union
        drift_score = 1 - jacc
        if drift_score > 0.75:
            return {
                'type': 'voice_drift', 'severity': 'low',
                'details': {'drift_score': drift_score}, 'ts': datetime.now().isoformat()
            }
        return None


def create_agent_team(ai_client: OpenAIClient = None) -> Dict[str, BaseAgent]:
    """Create a complete team of AI agents."""
    orchestrator = OrchestratorAgent(ai_client)
    methodologist = SurveyMethodologistAgent(ai_client)
    coding_specialist = QualitativeCodingSpecialist(ai_client)
    viz_designer = DataVisualizationDesigner(ai_client)

    # Optional persona agents (wire if credentials exist)
    from .persona_agents import ResearchAgent, PersonaCompilerAgent
    from .perplexity_client import PerplexityClient
    from .claude_client import ClaudeClient
    persona_research = None
    persona_compiler = None
    try:
        pplx = PerplexityClient()
        from research.web_persona_builder import WebPersonaBuilder
        persona_research = ResearchAgent(pplx, WebPersonaBuilder())
    except Exception:
        pass
    try:
        claude = ClaudeClient()
        from models.persona_schema import DETAILED_PERSONA_SCHEMA
        persona_compiler = PersonaCompilerAgent(claude, DETAILED_PERSONA_SCHEMA)
    except Exception:
        pass
    
    # Register agents with orchestrator
    orchestrator.register_agent('methodologist', methodologist)
    orchestrator.register_agent('coding_specialist', coding_specialist)
    orchestrator.register_agent('viz_designer', viz_designer)
    if persona_research:
        orchestrator.register_agent('persona_research', persona_research)
    if persona_compiler:
        orchestrator.register_agent('persona_compiler', persona_compiler)
    
    return {
        'orchestrator': orchestrator,
        'methodologist': methodologist,
        'coding_specialist': coding_specialist,
        'viz_designer': viz_designer,
        'persona_research': persona_research,
        'persona_compiler': persona_compiler,
    }
