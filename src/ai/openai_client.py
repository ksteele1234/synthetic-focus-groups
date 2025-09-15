"""
OpenAI API client for generating AI responses from personas and facilitators.
"""

import os
import json
import time
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None


# Lightweight response wrappers to normalize shape across real and mock clients
class _SimpleMessage:
    def __init__(self, content: str):
        self.content = content

class _SimpleChoice:
    def __init__(self, content: str):
        self.message = _SimpleMessage(content)

class _SimpleResponse:
    def __init__(self, content: str):
        self.choices = [_SimpleChoice(content)]


class OpenAIClient:
    """Client for OpenAI API integration."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", max_retries: int = 3):
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        openai.api_key = self.api_key
        self.model = model
        self.max_retries = max_retries
        
        # Default parameters
        self.default_params = {
            'temperature': 0.8,
            'max_tokens': 500,
            'top_p': 0.9,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.1
        }

    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """Wrapper that returns a simple, attribute-accessible response object.
        Matches usage in synthetic_runner (response.choices[0].message.content).
        """
        response = self._make_api_call(messages=messages, **{**self.default_params, **kwargs})
        try:
            content = response['choices'][0]['message']['content'].strip()
        except Exception:
            content = ""
        return _SimpleResponse(content)
    
    def generate_persona_response(self, persona_prompt: str, question: str, context: str = "", 
                                session_context: str = "", **kwargs) -> Dict[str, Any]:
        """Generate a response from a persona using OpenAI."""
        
        # Build the conversation context
        system_prompt = f"""You are roleplaying as a focus group participant with this personality:

{persona_prompt}

You are participating in a focus group discussion. Stay in character and respond naturally as this person would. Keep responses conversational, authentic, and relevant to your background and personality.

Session Context: {session_context}
Previous Context: {context}"""

        user_prompt = f"Facilitator asks: {question}\n\nPlease respond as this persona would, staying true to their personality, background, and experiences."
        
        try:
            response = self._make_api_call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **{**self.default_params, **kwargs}
            )
            
            return {
                'success': True,
                'content': response['choices'][0]['message']['content'].strip(),
                'usage': response.get('usage', {}),
                'model': response.get('model', self.model),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': f"[Error generating response: {str(e)}]",
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_facilitator_question(self, facilitator_prompt: str, primary_question: str,
                                    participant_responses: List[str], context: str = "",
                                    follow_up_count: int = 3, **kwargs) -> Dict[str, Any]:
        """Generate follow-up questions from a facilitator."""
        
        responses_text = "\n".join([f"- {resp}" for resp in participant_responses[-5:]])  # Last 5 responses
        
        system_prompt = f"""You are a professional focus group facilitator with this profile:

{facilitator_prompt}

You are conducting a focus group and need to generate {follow_up_count} thoughtful follow-up questions based on participant responses.

Context: {context}"""

        user_prompt = f"""Original Question: {primary_question}

Recent Participant Responses:
{responses_text}

Generate exactly {follow_up_count} specific, probing follow-up questions that will help gather deeper insights. Make questions:
1. Specific and actionable
2. Non-leading and unbiased  
3. Designed to elicit detailed responses
4. Building on what participants have shared

Format as a numbered list."""

        try:
            response = self._make_api_call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **{**self.default_params, 'temperature': 0.7, **kwargs}
            )
            
            content = response['choices'][0]['message']['content'].strip()
            
            # Parse numbered list into individual questions
            questions = []
            for line in content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering/bullets
                    question = re.sub(r'^\d+\.?\s*', '', line)
                    question = re.sub(r'^-\s*', '', question)
                    if question:
                        questions.append(question.strip())
            
            return {
                'success': True,
                'questions': questions,
                'raw_content': content,
                'usage': response.get('usage', {}),
                'model': response.get('model', self.model),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'questions': [f"Can you tell me more about that? [Error: {str(e)}]"],
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_session_themes(self, session_responses: List[Dict[str, Any]], 
                             background_context: str = "", **kwargs) -> Dict[str, Any]:
        """Analyze session responses to extract themes and insights."""
        
        # Prepare responses for analysis
        responses_text = ""
        for resp in session_responses:
            if resp.get('speaker_type') == 'participant':
                responses_text += f"Participant {resp.get('speaker_name', 'Unknown')}: {resp.get('content', '')}\n\n"
        
        system_prompt = f"""You are a qualitative research analyst specializing in focus group analysis.

Background Context: {background_context}

Analyze the following focus group responses and provide:
1. Key themes (3-7 major themes)
2. Sentiment analysis (overall tone)
3. Notable insights or patterns
4. Potential concerns or opportunities
5. Participant agreement/disagreement patterns

Be objective and evidence-based in your analysis."""

        user_prompt = f"""Focus Group Responses:
{responses_text}

Please provide a structured analysis in the following JSON format:
{{
    "themes": [
        {{"theme": "Theme Name", "description": "Description", "frequency": "high/medium/low", "participants": ["Participant names"]}},
    ],
    "sentiment": {{"overall": "positive/neutral/negative", "score": 0.5, "notes": "explanation"}},
    "insights": ["Key insight 1", "Key insight 2"],
    "patterns": ["Pattern 1", "Pattern 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}}"""

        try:
            response = self._make_api_call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **{**self.default_params, 'temperature': 0.3, **kwargs}
            )
            
            content = response['choices'][0]['message']['content'].strip()
            
            # Try to parse JSON response
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                analysis = {
                    'themes': [],
                    'sentiment': {'overall': 'neutral', 'score': 0.5, 'notes': 'Could not parse detailed analysis'},
                    'insights': [content],
                    'patterns': [],
                    'recommendations': []
                }
            
            return {
                'success': True,
                'analysis': analysis,
                'raw_content': content,
                'usage': response.get('usage', {}),
                'model': response.get('model', self.model),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis': {
                    'themes': [],
                    'sentiment': {'overall': 'neutral', 'score': 0.5, 'notes': f'Analysis failed: {str(e)}'},
                    'insights': [],
                    'patterns': [],
                    'recommendations': []
                },
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_research_report(self, session_data: Dict[str, Any], 
                               background_info: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate a comprehensive research report."""
        
        # Prepare session summary
        session_summary = f"""
Session: {session_data.get('name', 'Unknown')}
Participants: {len(session_data.get('participant_ids', []))}
Responses: {len(session_data.get('responses', []))}
Duration: {session_data.get('actual_duration_minutes', 'Unknown')} minutes
"""
        
        # Include background information if available
        background_text = ""
        if background_info:
            background_text = f"""
Research Context:
- Product: {background_info.get('product_description', '')}
- Market: {background_info.get('target_market_description', '')}
- Objectives: {', '.join(background_info.get('business_objectives', []))}
"""

        system_prompt = f"""You are a senior research analyst creating an executive research report.

{background_text}

Create a comprehensive but concise research report that executives can understand quickly. Focus on:
1. Executive Summary (2-3 key takeaways)
2. Key Findings with evidence
3. Strategic Recommendations  
4. Next Steps
5. Methodology notes

Be professional, evidence-based, and actionable."""

        user_prompt = f"""Session Data:
{session_summary}

Key Insights: {', '.join(session_data.get('key_insights', []))}
Themes: {', '.join(session_data.get('themes_discovered', []))}

Please create a structured executive research report."""

        try:
            response = self._make_api_call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **{**self.default_params, 'temperature': 0.4, 'max_tokens': 1000, **kwargs}
            )
            
            return {
                'success': True,
                'report': response['choices'][0]['message']['content'].strip(),
                'usage': response.get('usage', {}),
                'model': response.get('model', self.model),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'report': f"Error generating report: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
    
    def enhance_persona_profile(self, existing_persona: Dict[str, Any], 
                              research_context: str = "", **kwargs) -> Dict[str, Any]:
        """Enhance a persona profile with AI-generated details."""
        
        system_prompt = f"""You are a persona development specialist. Enhance the given persona with realistic, consistent details.

Research Context: {research_context}

Add missing details while maintaining consistency with existing information. Focus on:
1. Realistic personality traits
2. Relevant background experiences  
3. Motivations and pain points
4. Communication style
5. Values and beliefs

Keep enhancements believable and research-relevant."""

        user_prompt = f"""Current Persona:
Name: {existing_persona.get('name', 'Unknown')}
Age: {existing_persona.get('age', 'Unknown')}
Occupation: {existing_persona.get('occupation', 'Unknown')}
Background: {existing_persona.get('background_story', 'Limited background provided')}

Please enhance this persona with additional realistic details in JSON format:
{{
    "enhanced_background": "Enhanced background story",
    "personality_traits": ["trait1", "trait2"],
    "motivations": ["motivation1", "motivation2"],
    "pain_points": ["pain1", "pain2"],
    "values": ["value1", "value2"],
    "communication_style": "description",
    "relevant_experiences": ["experience1", "experience2"]
}}"""

        try:
            response = self._make_api_call(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **{**self.default_params, 'temperature': 0.6, **kwargs}
            )
            
            content = response['choices'][0]['message']['content'].strip()
            
            try:
                enhancements = json.loads(content)
            except json.JSONDecodeError:
                enhancements = {'enhanced_background': content}
            
            return {
                'success': True,
                'enhancements': enhancements,
                'raw_content': content,
                'usage': response.get('usage', {}),
                'model': response.get('model', self.model),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'enhancements': {},
                'timestamp': datetime.now().isoformat()
            }
    
    def _make_api_call(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Make API call with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                )
                return response
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                
                # Wait before retry (exponential backoff)
                wait_time = (2 ** attempt)
                time.sleep(wait_time)
        
        raise Exception(f"Max retries ({self.max_retries}) exceeded")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the OpenAI API connection."""
        try:
            response = self._make_api_call(
                messages=[{"role": "user", "content": "Hello, this is a test. Please respond with 'Connection successful.'"}],
                max_tokens=50,
                temperature=0
            )
            
            return {
                'success': True,
                'message': 'OpenAI API connection successful',
                'model': response.get('model', self.model),
                'usage': response.get('usage', {})
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'OpenAI API connection failed'
            }


# Utility function to create client instance
class MockOpenAIClient:
    """Mock OpenAI client for demo mode."""
    
    def __init__(self):
        self.model = "demo-mode"
        self.default_params = {}
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """Return a simple response object mimicking OpenAI structure."""
        # Use last user message content as context to craft a basic reply
        prompt_text = ""
        if messages:
            last = messages[-1]
            prompt_text = last.get('content', '') if isinstance(last, dict) else str(last)
        content = f"[Demo response] {prompt_text[:180]}..."
        return _SimpleResponse(content)
    
    def generate_persona_response(self, persona_prompt: str, question: str, context: str = "", 
                                session_context: str = "", **kwargs) -> Dict[str, Any]:
        """Generate a mock response from a persona."""
        import random
        
        # Extract persona name from prompt
        lines = persona_prompt.split('\n')
        name = "Demo Participant"
        for line in lines:
            if line.startswith("Name:"):
                name = line.replace("Name:", "").strip()
                break
        
        # Generate mock response based on question type
        mock_responses = [
            f"As {name}, I think that's really interesting. In my experience...",
            f"That's a great question! From my perspective as {name}...",
            f"I've actually dealt with this before. What I found was...",
            f"This reminds me of something that happened to me recently...",
            f"I have mixed feelings about this. On one hand... but on the other hand..."
        ]
        
        base_response = random.choice(mock_responses)
        
        return {
            'success': True,
            'content': base_response + " [This is a demo response - connect OpenAI for real AI interactions]",
            'usage': {'total_tokens': 50, 'prompt_tokens': 30, 'completion_tokens': 20},
            'model': 'demo-mode',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_facilitator_question(self, facilitator_prompt: str, primary_question: str,
                                    participant_responses: List[str], context: str = "",
                                    follow_up_count: int = 3, **kwargs) -> Dict[str, Any]:
        """Generate mock follow-up questions."""
        mock_questions = [
            "Can you tell me more about that experience?",
            "How do you think others might feel about this?",
            "What would make this solution more appealing to you?",
            "Have you encountered similar situations before?",
            "What's the most important factor in your decision-making?"
        ]
        
        import random
        selected_questions = random.sample(mock_questions, min(follow_up_count, len(mock_questions)))
        
        return {
            'success': True,
            'questions': [q + " [Demo question]" for q in selected_questions],
            'raw_content': "\n".join(f"{i+1}. {q}" for i, q in enumerate(selected_questions)),
            'usage': {'total_tokens': 30},
            'model': 'demo-mode',
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_session_themes(self, session_responses: List[Dict[str, Any]], 
                             background_context: str = "", **kwargs) -> Dict[str, Any]:
        """Generate mock session analysis."""
        mock_analysis = {
            'themes': [
                {"theme": "User Experience Concerns", "description": "Participants emphasized ease of use", "frequency": "high", "participants": ["Demo User 1", "Demo User 2"]},
                {"theme": "Cost Sensitivity", "description": "Budget considerations were frequently mentioned", "frequency": "medium", "participants": ["Demo User 1"]},
                {"theme": "Feature Requests", "description": "Several specific feature enhancements suggested", "frequency": "high", "participants": ["Demo User 2"]}
            ],
            'sentiment': {'overall': 'positive', 'score': 0.7, 'notes': 'Generally positive with some concerns'},
            'insights': ["Users value simplicity over advanced features", "Price point is a key decision factor"],
            'patterns': ["Consistent emphasis on user-friendly design", "Desire for better integration capabilities"],
            'recommendations': ["Prioritize UI/UX improvements", "Consider tiered pricing model"]
        }
        
        return {
            'success': True,
            'analysis': mock_analysis,
            'raw_content': "[Demo analysis - connect OpenAI for real AI analysis]",
            'usage': {'total_tokens': 100},
            'model': 'demo-mode',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_research_report(self, session_data: Dict[str, Any], 
                               background_info: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate mock research report."""
        mock_report = """# Executive Research Report

## Executive Summary
- Participants showed strong interest in the product concept
- Key concerns centered around pricing and ease of use
- Recommendations focus on UI improvements and tiered pricing

## Key Findings
1. **User Experience Priority**: All participants emphasized the importance of intuitive design
2. **Price Sensitivity**: 75% of participants mentioned cost as a primary factor
3. **Feature Requests**: Integration capabilities were the most requested enhancement

## Strategic Recommendations
1. Invest in user experience research and design improvements
2. Develop a tiered pricing strategy to address different market segments
3. Prioritize integration features in the product roadmap

## Next Steps
- Conduct additional research on pricing sensitivity
- Prototype key user experience improvements
- Evaluate integration partnership opportunities

[This is a demo report - connect OpenAI for real AI-generated reports]"""
        
        return {
            'success': True,
            'report': mock_report,
            'usage': {'total_tokens': 200},
            'model': 'demo-mode',
            'timestamp': datetime.now().isoformat()
        }
    
    def enhance_persona_profile(self, existing_persona: Dict[str, Any], 
                              research_context: str = "", **kwargs) -> Dict[str, Any]:
        """Generate mock persona enhancements."""
        mock_enhancements = {
            'enhanced_background': "Enhanced with additional realistic details and motivations [Demo enhancement]",
            'personality_traits': ["Detail-oriented", "Collaborative", "Results-driven"],
            'motivations': ["Professional growth", "Work-life balance", "Financial security"],
            'pain_points': ["Time management challenges", "Budget constraints", "Technology adoption"],
            'values': ["Quality", "Efficiency", "Reliability"],
            'communication_style': "Direct and practical, prefers concrete examples",
            'relevant_experiences': ["Previous software implementations", "Team leadership", "Budget management"]
        }
        
        return {
            'success': True,
            'enhancements': mock_enhancements,
            'raw_content': "[Demo persona enhancements - connect OpenAI for real AI enhancements]",
            'usage': {'total_tokens': 150},
            'model': 'demo-mode',
            'timestamp': datetime.now().isoformat()
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Mock connection test."""
        return {
            'success': True,
            'message': 'Demo mode - OpenAI API not connected',
            'model': 'demo-mode',
            'usage': {}
        }


def create_openai_client(api_key: str = None, model: str = "gpt-3.5-turbo") -> Optional[Union[OpenAIClient, MockOpenAIClient]]:
    """Create OpenAI client instance if API is available, otherwise return mock client for demo mode."""
    # Check for demo mode
    demo_mode = os.environ.get('DEMO_MODE', '').lower() == 'true'
    if demo_mode:
        return MockOpenAIClient()
    
    try:
        return OpenAIClient(api_key=api_key, model=model)
    except (ImportError, ValueError) as e:
        print(f"OpenAI client creation failed: {e}")
        return None
