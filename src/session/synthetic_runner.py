"""
Synthetic session runner that orchestrates the 4 core agents through complete Q/A rounds.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

from models.qa_turn import QATurn
from storage.qa_storage import QAStorage
from ai.openai_client import OpenAIClient, create_openai_client


class SyntheticFacilitator:
    """AI facilitator that asks questions and creates follow-ups."""
    
    def __init__(self, ai_client: OpenAIClient = None):
        self.ai_client = ai_client or create_openai_client()
        
    def generate_questions(self, topic: str, num_questions: int = 3) -> List[str]:
        """Generate main research questions."""
        if self.ai_client:
            try:
                prompt = f"""Generate {num_questions} focused research questions for a focus group about: {topic}
                
                Questions should be:
                - Open-ended and encourage detailed responses
                - Non-leading and unbiased
                - Suitable for different customer segments
                - Research-oriented
                
                Return as a simple list, one question per line."""
                
                response = self.ai_client.chat_completion([{
                    "role": "user", 
                    "content": prompt
                }])
                
                if response and response.choices:
                    questions = response.choices[0].message.content.strip().split('\n')
                    return [q.strip('- 1234567890.') for q in questions if q.strip()]
                    
            except Exception as e:
                print(f"AI question generation failed: {e}")
        
        # Fallback questions
        return [
            f"What are your biggest challenges with {topic}?",
            f"How do you currently solve problems related to {topic}?",
            f"What would an ideal solution for {topic} look like to you?"
        ]
    
    def generate_follow_up(self, question: str, answer: str, persona_context: str = "", persona_profile: Dict[str, Any] = None) -> Optional[str]:
        """Generate contextual follow-up question using detailed persona awareness."""
        if not answer.strip():
            return None
            
        if self.ai_client:
            try:
                # Build enhanced context using persona details
                enhanced_context = persona_context
                if persona_profile:
                    context_parts = []
                    if persona_profile.get('major_struggles'):
                        context_parts.append(f"Struggles: {', '.join(persona_profile['major_struggles'])}")
                    if persona_profile.get('deep_fears_business'):
                        context_parts.append(f"Fears: {', '.join(persona_profile['deep_fears_business'])}")
                    if persona_profile.get('previous_software_tried'):
                        context_parts.append(f"Previous attempts: {', '.join(persona_profile['previous_software_tried'])}")
                    if persona_profile.get('tangible_business_results'):
                        context_parts.append(f"Goals: {', '.join(persona_profile['tangible_business_results'])}")
                    
                    if context_parts:
                        enhanced_context += f" | Persona details: {' | '.join(context_parts)}"
                
                prompt = f"""Based on this Q&A exchange, generate a natural follow-up question:

                Original Question: {question}
                Answer: {answer}
                Persona Context: {enhanced_context}
                
                Generate a follow-up that:
                - Digs deeper into their response
                - Is specific to what they mentioned
                - Considers their background struggles and fears
                - Explores how this relates to their goals
                - References their past attempts if relevant
                - Feels conversational, not interrogating
                - Shows empathy for their situation
                
                Return just the follow-up question, nothing else."""
                
                response = self.ai_client.chat_completion([{
                    "role": "user",
                    "content": prompt
                }])
                
                if response and response.choices:
                    follow_up = response.choices[0].message.content.strip()
                    return follow_up if follow_up.endswith('?') else f"{follow_up}?"
                    
            except Exception as e:
                print(f"AI follow-up generation failed: {e}")
        
        # Fallback follow-ups based on keywords
        answer_lower = answer.lower()
        if 'time' in answer_lower:
            return "How much time does this typically take?"
        elif 'expensive' in answer_lower or 'cost' in answer_lower or 'price' in answer_lower:
            return "What would be a reasonable price point for you?"
        elif 'difficult' in answer_lower or 'hard' in answer_lower or 'challenge' in answer_lower:
            return "What makes this particularly challenging?"
        else:
            return "Can you give me a specific example of that?"


class SyntheticPersona:
    """AI persona that responds to questions in character."""
    
    def __init__(self, persona_id: str, profile: Dict[str, Any], ai_client: OpenAIClient = None):
        self.persona_id = persona_id
        self.profile = profile
        self.ai_client = ai_client or create_openai_client()
        
    def respond_to_question(self, question: str, context: str = "") -> Dict[str, Any]:
        """Generate response to a question as this persona."""
        if self.ai_client:
            try:
                persona_prompt = self._build_detailed_persona_prompt(question, context)
                
                response = self.ai_client.chat_completion([{
                    "role": "user",
                    "content": persona_prompt
                }])
                
                if response and response.choices:
                    answer = response.choices[0].message.content.strip()
                    confidence = self._calculate_confidence(question, answer)
                    tags = self._extract_tags(question, answer)
                    
                    return {
                        'answer': answer,
                        'confidence': confidence,
                        'tags': tags
                    }
                    
            except Exception as e:
                print(f"AI persona response failed: {e}")
        
        # Fallback response using detailed profile
        return {
            'answer': self._generate_fallback_response(question),
            'confidence': 0.7,
            'tags': self._extract_basic_tags(question)
        }
    
    def _build_detailed_persona_prompt(self, question: str, context: str = "") -> str:
        """Build comprehensive persona prompt using all available profile data."""
        
        # Start with basic identity
        name = self.profile.get('name', self.persona_id)
        age = self.profile.get('age', 'adult')
        gender = self.profile.get('gender', 'person')
        occupation = self.profile.get('occupation', 'professional')
        location = self.profile.get('location', 'somewhere')
        
        prompt_parts = []
        prompt_parts.append(f"You are {name}, a {age}-year-old {gender} {occupation} from {location}.")
        
        # Add family/relationship context
        if self.profile.get('relationship_family'):
            prompt_parts.append(f"Personal life: {self.profile['relationship_family']}.")
        
        # Add education and income
        if self.profile.get('education'):
            prompt_parts.append(f"Education: {self.profile['education']}.")
        if self.profile.get('annual_income'):
            prompt_parts.append(f"Annual income: {self.profile['annual_income']}.")
        
        # Add personality and values
        if self.profile.get('personality_traits'):
            traits = ', '.join(self.profile['personality_traits'])
            prompt_parts.append(f"Your personality: {traits}.")
        
        if self.profile.get('values'):
            values = ', '.join(self.profile['values'])
            prompt_parts.append(f"You value: {values}.")
        
        # Add hobbies and lifestyle
        if self.profile.get('hobbies'):
            hobbies = ', '.join(self.profile['hobbies'])
            prompt_parts.append(f"Hobbies: {hobbies}.")
        
        # Add major struggles and fears - this is crucial for authentic responses
        if self.profile.get('major_struggles'):
            struggles = ', '.join(self.profile['major_struggles'])
            prompt_parts.append(f"Current struggles: {struggles}.")
        
        if self.profile.get('deep_fears_business'):
            fears = ', '.join(self.profile['deep_fears_business'])
            prompt_parts.append(f"Deep business fears: {fears}.")
        
        if self.profile.get('deep_fears_personal'):
            fears = ', '.join(self.profile['deep_fears_personal'])
            prompt_parts.append(f"Personal concerns: {fears}.")
        
        # Add previous attempts and frustrations
        if self.profile.get('previous_software_tried'):
            software = ', '.join(self.profile['previous_software_tried'])
            prompt_parts.append(f"You've tried: {software}.")
            
        if self.profile.get('why_software_failed'):
            prompt_parts.append(f"Why previous solutions failed: {self.profile['why_software_failed']}.")
        
        # Add desired outcomes
        if self.profile.get('tangible_business_results'):
            results = ', '.join(self.profile['tangible_business_results'])
            prompt_parts.append(f"You want to achieve: {results}.")
        
        if self.profile.get('emotional_transformations'):
            emotions = ', '.join(self.profile['emotional_transformations'])
            prompt_parts.append(f"Emotionally, you hope to feel: {emotions}.")
        
        # Add signature phrases
        if self.profile.get('if_only_soundbites'):
            soundbites = '; '.join(self.profile['if_only_soundbites'][:2])
            prompt_parts.append(f"You often think: {soundbites}.")
        
        # Add things to avoid
        if self.profile.get('things_to_avoid'):
            avoid = ', '.join(self.profile['things_to_avoid'])
            prompt_parts.append(f"You want to avoid: {avoid}.")
        
        # Add behavioral instructions
        prompt_parts.append("\nWhen answering questions:")
        prompt_parts.append("- Draw from your specific struggles, fears, and past experiences")
        prompt_parts.append("- Reference your failed attempts when relevant")
        prompt_parts.append("- Express both practical needs and emotional concerns")
        prompt_parts.append("- Use your characteristic phrases and concerns")
        prompt_parts.append("- Be authentic to your situation and personality")
        prompt_parts.append("- Show vulnerability about your fears and frustrations")
        
        if context:
            prompt_parts.append(f"\nContext: {context}")
            
        prompt_parts.append(f"\nQuestion: {question}")
        prompt_parts.append("\nRespond naturally as this person would, incorporating their complete life context and emotional state.")
        
        return "\n".join(prompt_parts)
    
    def _generate_fallback_response(self, question: str) -> str:
        """Generate fallback response using available persona details."""
        # Use detailed profile info for fallback
        name = self.profile.get('name', 'I')
        occupation = self.profile.get('occupation', 'professional')
        
        base = f"As a {occupation}, this is something I deal with regularly."
        
        # Add struggle-based context if available
        if self.profile.get('major_struggles'):
            struggle = self.profile['major_struggles'][0]
            base += f" {struggle} is definitely a concern in my work."
        
        # Add fear-based context if available
        if self.profile.get('deep_fears_business'):
            fear = self.profile['deep_fears_business'][0]
            base += f" I worry about {fear.lower()}."
        
        # Add previous attempt context if available
        if self.profile.get('previous_software_tried'):
            software = self.profile['previous_software_tried'][0]
            base += f" I've tried {software} before but it didn't quite work for my needs."
        
        return base + f" {question.replace('?', '')} is definitely something that affects my daily work."
    
    def _extract_basic_tags(self, question: str) -> List[str]:
        """Extract basic tags from question and persona profile."""
        tags = []
        
        # Extract from persona profile
        if self.profile.get('major_struggles'):
            for struggle in self.profile['major_struggles']:
                if 'budget' in struggle.lower() or 'cost' in struggle.lower():
                    tags.append('pricing')
                if 'time' in struggle.lower():
                    tags.append('time_management')
                if 'team' in struggle.lower() or 'collaboration' in struggle.lower():
                    tags.append('collaboration')
        
        # Add general response tag
        tags.append('general_response')
        
        return tags
    
    def _calculate_confidence(self, question: str, answer: str) -> float:
        """Calculate confidence based on response characteristics."""
        # Simple heuristic based on response length and specificity
        base_confidence = 0.7
        
        # Longer responses suggest more confidence
        if len(answer) > 100:
            base_confidence += 0.1
        if len(answer) > 200:
            base_confidence += 0.1
            
        # Specific details suggest higher confidence
        if any(word in answer.lower() for word in ['specifically', 'exactly', 'always', 'never']):
            base_confidence += 0.05
            
        # Questions or uncertainty suggest lower confidence
        if any(word in answer.lower() for word in ['maybe', 'perhaps', 'not sure', 'might']):
            base_confidence -= 0.1
            
        return min(1.0, max(0.1, base_confidence))
    
    def _extract_tags(self, question: str, answer: str) -> List[str]:
        """Extract thematic tags from the response."""
        text = (question + " " + answer).lower()
        
        tag_keywords = {
            'pricing': ['price', 'cost', 'expensive', 'cheap', 'budget', 'afford'],
            'time_management': ['time', 'hours', 'quickly', 'slow', 'efficient'],
            'workflow': ['process', 'workflow', 'steps', 'procedure', 'system'],
            'collaboration': ['team', 'colleagues', 'share', 'together', 'group'],
            'technology': ['tool', 'software', 'app', 'platform', 'system'],
            'customer_service': ['support', 'help', 'service', 'assistance'],
            'quality': ['quality', 'good', 'bad', 'excellent', 'poor'],
            'frustration': ['frustrating', 'annoying', 'difficult', 'problem', 'issue'],
            'satisfaction': ['happy', 'satisfied', 'pleased', 'love', 'great']
        }
        
        extracted_tags = []
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                extracted_tags.append(tag)
        
        return extracted_tags or ['general']


class ResearchAnalyst:
    """Analyzes session data for insights."""
    
    def __init__(self, ai_client: OpenAIClient = None):
        self.ai_client = ai_client or create_openai_client()
    
    def analyze_session(self, qa_turns: List[QATurn]) -> Dict[str, Any]:
        """Analyze complete session for insights."""
        if not qa_turns:
            return {'insights': [], 'themes': [], 'recommendations': []}
        
        # Basic analysis
        personas = list(set(turn.persona_id for turn in qa_turns))
        rounds = list(set(turn.round_id for turn in qa_turns))
        
        # Aggregate tags
        all_tags = []
        for turn in qa_turns:
            all_tags.extend(turn.tags)
        
        tag_frequency = {}
        for tag in all_tags:
            tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
        
        # Calculate average confidence by persona
        persona_confidence = {}
        for persona_id in personas:
            persona_turns = [t for t in qa_turns if t.persona_id == persona_id]
            avg_conf = sum(t.confidence_0_1 for t in persona_turns) / len(persona_turns)
            persona_confidence[persona_id] = avg_conf
        
        analysis = {
            'session_overview': {
                'total_turns': len(qa_turns),
                'personas_participated': len(personas),
                'rounds_completed': len(rounds),
                'avg_confidence': sum(t.confidence_0_1 for t in qa_turns) / len(qa_turns)
            },
            'themes': [{'theme': tag, 'frequency': freq} for tag, freq in sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)],
            'persona_insights': persona_confidence,
            'top_concerns': self._extract_concerns(qa_turns),
            'insights': self._generate_insights(qa_turns),
            'recommendations': self._generate_recommendations(qa_turns, tag_frequency)
        }
        
        return analysis
    
    def _extract_concerns(self, qa_turns: List[QATurn]) -> List[str]:
        """Extract top concerns mentioned."""
        concern_keywords = ['challenge', 'problem', 'issue', 'difficult', 'frustrating', 'pain']
        concerns = []
        
        for turn in qa_turns:
            answer_lower = turn.answer.lower()
            if any(keyword in answer_lower for keyword in concern_keywords):
                # Extract the sentence with the concern
                sentences = turn.answer.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in concern_keywords):
                        concerns.append(sentence.strip())
                        break
        
        return concerns[:5]  # Top 5 concerns
    
    def _generate_insights(self, qa_turns: List[QATurn]) -> List[str]:
        """Generate key insights from the data."""
        insights = []
        
        # Confidence insights
        high_confidence_turns = [t for t in qa_turns if t.confidence_0_1 > 0.8]
        if high_confidence_turns:
            insights.append(f"{len(high_confidence_turns)} responses showed high confidence (>80%), indicating strong opinions on key topics")
        
        # Engagement insights
        personas = set(t.persona_id for t in qa_turns)
        if len(personas) > 1:
            persona_responses = {p: len([t for t in qa_turns if t.persona_id == p]) for p in personas}
            most_engaged = max(persona_responses.items(), key=lambda x: x[1])
            insights.append(f"Most engaged participant: {most_engaged[0]} with {most_engaged[1]} responses")
        
        # Follow-up insights
        follow_ups = [t for t in qa_turns if t.follow_up_question and t.follow_up_answer]
        if follow_ups:
            insights.append(f"{len(follow_ups)} follow-up exchanges revealed deeper insights beyond initial responses")
        
        return insights
    
    def _generate_recommendations(self, qa_turns: List[QATurn], tag_frequency: Dict[str, int]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Tag-based recommendations
        if tag_frequency.get('pricing', 0) > 2:
            recommendations.append("Price sensitivity is a key concern - consider flexible pricing strategies")
        
        if tag_frequency.get('time_management', 0) > 2:
            recommendations.append("Time efficiency is important to users - prioritize features that save time")
        
        if tag_frequency.get('frustration', 0) > 1:
            recommendations.append("Multiple frustration points identified - focus on user experience improvements")
        
        # Confidence-based recommendations
        low_conf_turns = [t for t in qa_turns if t.confidence_0_1 < 0.6]
        if len(low_conf_turns) > len(qa_turns) * 0.3:
            recommendations.append("Many responses showed uncertainty - consider follow-up research to validate findings")
        
        return recommendations


class DataVisualizationDesigner:
    """Creates visualization specifications from session data."""
    
    def create_visualizations(self, analysis: Dict[str, Any], qa_turns: List[QATurn]) -> Dict[str, Any]:
        """Create visualization specifications."""
        
        visualizations = {
            'confidence_by_persona': self._create_confidence_chart(qa_turns),
            'theme_frequency': self._create_theme_chart(analysis.get('themes', [])),
            'response_timeline': self._create_timeline_chart(qa_turns),
            'engagement_overview': self._create_engagement_chart(qa_turns),
            'dashboard_summary': self._create_dashboard_spec(analysis)
        }
        
        return visualizations
    
    def _create_confidence_chart(self, qa_turns: List[QATurn]) -> Dict[str, Any]:
        """Create confidence by persona chart specification."""
        personas = set(t.persona_id for t in qa_turns)
        
        data = []
        for persona_id in personas:
            persona_turns = [t for t in qa_turns if t.persona_id == persona_id]
            avg_confidence = sum(t.confidence_0_1 for t in persona_turns) / len(persona_turns)
            data.append({
                'persona': persona_id,
                'avg_confidence': round(avg_confidence, 2),
                'response_count': len(persona_turns)
            })
        
        return {
            'type': 'bar_chart',
            'title': 'Average Confidence by Persona',
            'data': data,
            'x_axis': 'persona',
            'y_axis': 'avg_confidence',
            'description': 'Shows how confident each persona was in their responses'
        }
    
    def _create_theme_chart(self, themes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create theme frequency chart."""
        return {
            'type': 'horizontal_bar_chart',
            'title': 'Most Common Themes',
            'data': themes[:10],  # Top 10 themes
            'x_axis': 'frequency',
            'y_axis': 'theme',
            'description': 'Frequency of different themes mentioned across all responses'
        }
    
    def _create_timeline_chart(self, qa_turns: List[QATurn]) -> Dict[str, Any]:
        """Create response timeline chart."""
        timeline_data = []
        for turn in qa_turns:
            timeline_data.append({
                'timestamp': turn.ts,
                'round': turn.round_id,
                'persona': turn.persona_id,
                'confidence': turn.confidence_0_1
            })
        
        return {
            'type': 'timeline_chart',
            'title': 'Session Response Timeline',
            'data': timeline_data,
            'description': 'Timeline of responses throughout the session'
        }
    
    def _create_engagement_chart(self, qa_turns: List[QATurn]) -> Dict[str, Any]:
        """Create engagement overview chart."""
        personas = set(t.persona_id for t in qa_turns)
        
        engagement_data = []
        for persona_id in personas:
            persona_turns = [t for t in qa_turns if t.persona_id == persona_id]
            total_chars = sum(len(t.answer) for t in persona_turns)
            follow_ups = len([t for t in persona_turns if t.follow_up_answer])
            
            engagement_data.append({
                'persona': persona_id,
                'response_count': len(persona_turns),
                'total_content_length': total_chars,
                'follow_up_answers': follow_ups,
                'engagement_score': (len(persona_turns) * 0.4 + follow_ups * 0.6) * 100
            })
        
        return {
            'type': 'scatter_plot',
            'title': 'Participant Engagement Analysis',
            'data': engagement_data,
            'x_axis': 'response_count',
            'y_axis': 'engagement_score',
            'size_by': 'total_content_length',
            'description': 'Shows engagement levels across different personas'
        }
    
    def _create_dashboard_spec(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive dashboard specification."""
        return {
            'type': 'executive_dashboard',
            'title': 'Session Analysis Dashboard',
            'sections': [
                {
                    'title': 'Key Metrics',
                    'type': 'metrics_cards',
                    'metrics': [
                        {'label': 'Total Responses', 'value': analysis['session_overview']['total_turns']},
                        {'label': 'Participants', 'value': analysis['session_overview']['personas_participated']},
                        {'label': 'Rounds Completed', 'value': analysis['session_overview']['rounds_completed']},
                        {'label': 'Avg Confidence', 'value': f"{analysis['session_overview']['avg_confidence']:.1%}"}
                    ]
                },
                {
                    'title': 'Top Themes',
                    'type': 'theme_list',
                    'data': analysis.get('themes', [])[:5]
                },
                {
                    'title': 'Key Insights',
                    'type': 'insight_list',
                    'data': analysis.get('insights', [])
                },
                {
                    'title': 'Recommendations',
                    'type': 'recommendation_list',
                    'data': analysis.get('recommendations', [])
                }
            ],
            'description': 'Executive summary of session findings'
        }


class SyntheticSessionRunner:
    """Orchestrates the complete synthetic focus group session."""
    
    def __init__(self, ai_client: OpenAIClient = None):
        self.ai_client = ai_client or create_openai_client()
        self.facilitator = SyntheticFacilitator(ai_client)
        self.analyst = ResearchAnalyst(ai_client)
        self.viz_designer = DataVisualizationDesigner()
        self.storage = QAStorage()
        
    def run_session(self, study_id: str, topic: str, personas: List[Dict[str, Any]], 
                   num_questions: int = 3, session_id: str = None) -> Dict[str, Any]:
        """Run a complete synthetic focus group session."""
        
        session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        print(f"🚀 Starting synthetic session: {session_id}")
        print(f"📋 Topic: {topic}")
        print(f"👥 Participants: {len(personas)}")
        
        # Initialize synthetic personas
        synthetic_personas = []
        for persona_data in personas:
            persona_id = persona_data.get('id', f"persona_{uuid.uuid4().hex[:6]}")
            synthetic_persona = SyntheticPersona(persona_id, persona_data, self.ai_client)
            synthetic_personas.append(synthetic_persona)
        
        # Generate research questions
        print("💭 Generating research questions...")
        questions = self.facilitator.generate_questions(topic, num_questions)
        print(f"✅ Generated {len(questions)} questions")
        
        # Run Q&A rounds
        qa_turns = []
        
        for round_id, question in enumerate(questions, 1):
            print(f"\n🔄 Round {round_id}: {question[:60]}...")
            
            for persona in synthetic_personas:
                # Generate main response
                print(f"  💬 {persona.persona_id} responding...")
                response_data = persona.respond_to_question(question, f"This is round {round_id} of {len(questions)}")
                
                # Create Q/A turn
                qa_turn = QATurn.create_with_timestamp(
                    study_id=study_id,
                    session_id=session_id,
                    persona_id=persona.persona_id,
                    round_id=round_id,
                    question=question,
                    answer=response_data['answer'],
                    confidence=response_data['confidence'],
                    tags=response_data['tags']
                )
                
                # Generate and add follow-up if applicable with detailed persona awareness
                follow_up_q = self.facilitator.generate_follow_up(
                    question, 
                    response_data['answer'], 
                    persona.profile.get('background', ''),
                    persona_profile=persona.profile  # Pass full profile for enhanced context
                )
                
                if follow_up_q:
                    print(f"    🔍 Follow-up: {follow_up_q[:40]}...")
                    follow_up_data = persona.respond_to_question(follow_up_q, f"Follow-up to: {response_data['answer'][:100]}...")
                    
                    qa_turn.follow_up_question = follow_up_q
                    qa_turn.follow_up_answer = follow_up_data['answer']
                
                qa_turns.append(qa_turn)
        
        print(f"\n📊 Session complete! Generated {len(qa_turns)} Q/A turns")
        
        # Analyze session
        print("🔍 Analyzing session data...")
        analysis = self.analyst.analyze_session(qa_turns)
        
        # Create visualizations
        print("📈 Creating visualizations...")
        visualizations = self.viz_designer.create_visualizations(analysis, qa_turns)
        
        # Save data
        print("💾 Saving session data...")
        storage_results = self.storage.save_qa_turns(qa_turns, study_id, session_id)
        
        print(f"✅ Session saved to: {storage_results['session_folder']}")
        print(f"   📄 JSONL: {storage_results['jsonl_path']}")
        print(f"   📊 CSV: {storage_results['csv_path']}")
        
        # Validate stored data
        validation_results = self.storage.validate_stored_session(study_id, session_id)
        
        if validation_results['status'] == 'valid':
            print("✅ All data validated successfully - zero schema errors!")
        else:
            print(f"❌ Validation issues: {validation_results['total_errors']} errors found")
        
        return {
            'session_id': session_id,
            'study_id': study_id,
            'qa_turns': qa_turns,
            'analysis': analysis,
            'visualizations': visualizations,
            'storage_results': storage_results,
            'validation_results': validation_results,
            'summary': {
                'total_turns': len(qa_turns),
                'personas': len(synthetic_personas),
                'questions': len(questions),
                'avg_confidence': sum(t.confidence_0_1 for t in qa_turns) / len(qa_turns),
                'themes_identified': len(analysis.get('themes', [])),
                'insights_generated': len(analysis.get('insights', [])),
                'files_created': len(storage_results),
                'schema_errors': validation_results['total_errors']
            }
        }


def create_sample_personas() -> List[Dict[str, Any]]:
    """Create sample personas for testing."""
    return [
        {
            'id': 'sarah_small_business',
            'name': 'Sarah Thompson',
            'role': 'Small Business Owner',
            'background': 'Owns a local marketing consultancy with 5 employees. Tech-savvy but time-constrained.',
            'pain_points': ['Limited time for admin tasks', 'Juggling multiple tools', 'Budget constraints'],
            'goals': ['Streamline workflows', 'Improve client results', 'Scale business efficiently']
        },
        {
            'id': 'mike_marketing_mgr', 
            'name': 'Mike Rodriguez',
            'role': 'Marketing Manager',
            'background': 'Marketing manager at 200-person B2B company. Focused on lead generation and brand awareness.',
            'pain_points': ['Proving ROI to executives', 'Team collaboration', 'Data silos'],
            'goals': ['Increase qualified leads', 'Improve attribution', 'Better team coordination']
        },
        {
            'id': 'jenny_freelancer',
            'name': 'Jenny Chen', 
            'role': 'Freelance Social Media Manager',
            'background': 'Freelance social media manager serving 8-10 small business clients simultaneously.',
            'pain_points': ['Client reporting demands', 'Tool costs', 'Inconsistent income'],
            'goals': ['Efficient client management', 'Professional reporting', 'Stable income growth']
        }
    ]