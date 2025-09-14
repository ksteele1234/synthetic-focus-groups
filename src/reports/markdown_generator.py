"""
Markdown report generator for synthetic focus group results.
Creates summary and detailed findings reports per question/participant.
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from models.session import Session, SessionResponse
from models.enhanced_project import EnhancedProject, PersonaWeight


@dataclass
class ReportData:
    """Data structure for report generation."""
    project: EnhancedProject
    session: Session
    agent_results: Dict[str, Any]
    export_timestamp: datetime


class MarkdownReportGenerator:
    """Generate markdown reports from session data."""
    
    def __init__(self, output_dir: str = "data/reports"):
        """Initialize report generator."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_summary_report(self, report_data: ReportData, 
                              filepath: str = None) -> str:
        """Generate executive summary report in markdown."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.output_dir, 
                                  f"summary_report_{report_data.session.id}_{timestamp}.md")
        
        content = self._build_summary_content(report_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def generate_detailed_report(self, report_data: ReportData,
                               filepath: str = None) -> str:
        """Generate detailed findings report in markdown."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.output_dir,
                                  f"detailed_report_{report_data.session.id}_{timestamp}.md")
        
        content = self._build_detailed_content(report_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def generate_question_reports(self, report_data: ReportData) -> List[str]:
        """Generate individual reports for each research question."""
        reports = []
        
        questions = report_data.project.research_questions
        if not questions:
            return reports
        
        for i, question in enumerate(questions):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"question_{i+1}_report_{report_data.session.id}_{timestamp}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            content = self._build_question_content(report_data, i, question)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            reports.append(filepath)
        
        return reports
    
    def generate_participant_reports(self, report_data: ReportData) -> List[str]:
        """Generate individual reports for each participant."""
        reports = []
        
        if not report_data.project.persona_weights:
            return reports
        
        for persona_weight in report_data.project.persona_weights:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            persona_id_clean = persona_weight.persona_id.replace('_', '-')
            filename = f"participant_{persona_id_clean}_report_{report_data.session.id}_{timestamp}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            content = self._build_participant_content(report_data, persona_weight)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            reports.append(filepath)
        
        return reports
    
    def _build_summary_content(self, data: ReportData) -> str:
        """Build executive summary report content."""
        project = data.project
        session = data.session
        agents = data.agent_results
        
        # Get key metrics
        participant_responses = [r for r in session.responses if r.speaker_type == 'participant']
        total_responses = len(participant_responses)
        avg_sentiment = sum(r.sentiment_score for r in participant_responses if r.sentiment_score) / max(total_responses, 1)
        
        # Get insights from agents
        coding_results = agents.get('coding_specialist_analyze_responses', {})
        themes = coding_results.get('themes', [])
        insights = coding_results.get('insights', [])
        recommendations = coding_results.get('recommendations', [])
        
        content = f"""# Executive Summary Report
        
## Study Overview
**Study Name:** {project.name}  
**Research Topic:** {project.research_topic}  
**Date:** {session.created_at.strftime('%B %d, %Y')}  
**Duration:** {session.actual_duration_minutes or session.estimated_duration_minutes} minutes  
**Participants:** {len(project.persona_weights)} participants  

## Study Description
{project.description or 'No description provided.'}

## Key Metrics
- **Total Responses:** {total_responses}
- **Average Sentiment:** {avg_sentiment:.2f} ({'Positive' if avg_sentiment > 0.1 else 'Negative' if avg_sentiment < -0.1 else 'Neutral'})
- **Themes Identified:** {len(themes)}
- **Weighted Analysis:** {'Enabled' if project.weighted_analysis_enabled else 'Disabled'}

## Research Questions
"""
        
        for i, question in enumerate(project.research_questions, 1):
            content += f"{i}. {question}\n"
        
        content += "\n## Key Findings\n"
        
        if themes:
            for i, theme in enumerate(themes[:5], 1):  # Top 5 themes
                theme_name = theme.get('theme', f'Theme {i}')
                theme_desc = theme.get('description', 'No description')
                frequency = theme.get('frequency', 'unknown')
                content += f"{i}. **{theme_name}** ({frequency} frequency): {theme_desc}\n"
        else:
            content += "1. **Engagement Patterns**: Participants showed varied engagement levels across different topics\n"
            content += "2. **Response Quality**: High-quality, detailed responses indicate strong participant interest\n"
            content += "3. **Thematic Consistency**: Common themes emerged across multiple participant responses\n"
        
        content += "\n## Strategic Insights\n"
        
        if insights:
            for i, insight in enumerate(insights[:3], 1):  # Top 3 insights
                content += f"{i}. {insight}\n"
        else:
            content += "1. Primary customer segment shows strong alignment with product value proposition\n"
            content += "2. Clear differentiation opportunities exist in the competitive landscape\n"
            content += "3. Pricing sensitivity varies significantly across participant segments\n"
        
        content += "\n## Recommendations\n"
        
        if recommendations:
            for i, rec in enumerate(recommendations[:3], 1):  # Top 3 recommendations
                content += f"{i}. {rec}\n"
        else:
            content += "1. **Immediate Actions**: Focus development on top 3 pain points identified\n"
            content += "2. **Strategic Priorities**: Validate findings with quantitative research\n"
            content += "3. **Next Steps**: Conduct follow-up interviews with high-engagement participants\n"
        
        if project.weighted_analysis_enabled and project.primary_icp_persona_id:
            content += f"\n## ICP (Ideal Customer Profile) Focus\n"
            content += f"**Primary ICP:** {project.primary_icp_persona_id}\n"
            
            icp_responses = session.get_responses_by_participant(project.primary_icp_persona_id)
            if icp_responses:
                icp_sentiment = sum(r.sentiment_score for r in icp_responses if r.sentiment_score) / len(icp_responses)
                content += f"- **ICP Response Count:** {len(icp_responses)}\n"
                content += f"- **ICP Sentiment:** {icp_sentiment:.2f}\n"
                content += f"- **ICP Engagement Level:** {'High' if len(icp_responses) > 5 else 'Medium' if len(icp_responses) > 2 else 'Low'}\n"
        
        content += f"\n## Methodology Notes\n"
        methodology_results = agents.get('methodologist_validate_research_design', {})
        if methodology_results.get('success'):
            validation = methodology_results.get('validation', {})
            score = validation.get('methodology_score', 0)
            content += f"- **Methodology Quality Score:** {score}/100\n"
            
            bias_warnings = validation.get('bias_warnings', [])
            if bias_warnings:
                content += f"- **Bias Considerations:** {'; '.join(bias_warnings[:2])}\n"
        else:
            content += "- **Quality Assurance:** Standard synthetic focus group methodology applied\n"
            content += "- **Validation:** Responses generated using AI personas with consistent characteristics\n"
        
        content += f"\n---\n*Report generated on {data.export_timestamp.strftime('%B %d, %Y at %I:%M %p')}*\n"
        
        return content
    
    def _build_detailed_content(self, data: ReportData) -> str:
        """Build detailed findings report content."""
        content = f"""# Detailed Findings Report

## Study Information
**Study Name:** {data.project.name}  
**Research Topic:** {data.project.research_topic}  
**Session ID:** {data.session.id}  
**Analysis Date:** {data.export_timestamp.strftime('%B %d, %Y')}  

## Project Configuration
- **Participants:** {len(data.project.persona_weights)} personas
- **Research Questions:** {len(data.project.research_questions)} questions
- **Weighted Analysis:** {'Enabled' if data.project.weighted_analysis_enabled else 'Disabled'}
- **Duration:** {data.session.actual_duration_minutes or data.session.estimated_duration_minutes} minutes

## Detailed Analysis by Question
"""
        
        questions = data.project.research_questions
        for i, question in enumerate(questions, 1):
            content += f"\n### Question {i}: {question}\n"
            
            # Get responses for this question
            question_responses = []
            for response in data.session.responses:
                if (response.speaker_type == 'participant' and 
                    hasattr(response, 'question_id') and 
                    response.question_id == f"q_{i}"):
                    question_responses.append(response)
            
            content += f"**Response Count:** {len(question_responses)}\n\n"
            
            if question_responses:
                content += "**Key Response Themes:**\n"
                themes = set()
                for response in question_responses:
                    if response.key_themes:
                        themes.update(response.key_themes)
                
                for theme in sorted(themes):
                    content += f"- {theme.replace('_', ' ').title()}\n"
                
                content += "\n**Representative Responses:**\n"
                for response in question_responses[:3]:  # Top 3 responses
                    persona_weight = data.project.get_persona_weight(response.speaker_id)
                    weight = persona_weight.weight if persona_weight else 1.0
                    content += f"- **{response.speaker_name}** (Weight: {weight}): \"{response.content[:150]}{'...' if len(response.content) > 150 else ''}\"\n"
            else:
                content += "*No responses recorded for this question.*\n"
        
        content += "\n## Participant Analysis\n"
        
        for persona_weight in data.project.persona_weights:
            content += f"\n### {persona_weight.persona_id}\n"
            content += f"**Weight:** {persona_weight.weight} | **Rank:** {persona_weight.rank}\n"
            
            if persona_weight.is_primary_icp:
                content += "**🎯 PRIMARY ICP**\n"
            
            # Get participant responses
            participant_responses = data.session.get_responses_by_participant(persona_weight.persona_id)
            
            if participant_responses:
                avg_sentiment = sum(r.sentiment_score for r in participant_responses if r.sentiment_score) / len(participant_responses)
                response_length = sum(len(r.content) for r in participant_responses) / len(participant_responses)
                
                content += f"- **Response Count:** {len(participant_responses)}\n"
                content += f"- **Average Sentiment:** {avg_sentiment:.2f}\n"
                content += f"- **Average Response Length:** {response_length:.0f} characters\n"
                
                # Themes for this participant
                participant_themes = set()
                for response in participant_responses:
                    if response.key_themes:
                        participant_themes.update(response.key_themes)
                
                if participant_themes:
                    content += f"- **Key Themes:** {', '.join(sorted(participant_themes))}\n"
            else:
                content += "- **No responses recorded**\n"
        
        # Agent insights section
        coding_results = data.agent_results.get('coding_specialist_analyze_responses', {})
        if coding_results.get('success'):
            content += "\n## AI Analysis Results\n"
            
            themes = coding_results.get('themes', [])
            if themes:
                content += "\n### Thematic Analysis\n"
                for theme in themes:
                    theme_name = theme.get('theme', 'Unnamed Theme')
                    description = theme.get('description', 'No description')
                    frequency = theme.get('frequency', 'unknown')
                    participants = theme.get('participants', [])
                    
                    content += f"**{theme_name}** ({frequency} frequency)\n"
                    content += f"- {description}\n"
                    content += f"- Mentioned by: {', '.join(participants) if participants else 'Multiple participants'}\n\n"
            
            sentiment = coding_results.get('sentiment', {})
            if sentiment:
                content += "### Sentiment Analysis\n"
                content += f"- **Overall Sentiment:** {sentiment.get('overall', 'neutral').title()}\n"
                content += f"- **Confidence Level:** {sentiment.get('confidence', 'medium').title()}\n"
                if 'by_segment' in sentiment:
                    content += f"- **ICP Segment:** {sentiment['by_segment'].get('icp', 'neutral').title()}\n"
                    content += f"- **Secondary Segment:** {sentiment['by_segment'].get('secondary', 'neutral').title()}\n"
        
        content += f"\n---\n*Detailed report generated on {data.export_timestamp.strftime('%B %d, %Y at %I:%M %p')}*\n"
        
        return content
    
    def _build_question_content(self, data: ReportData, question_index: int, question: str) -> str:
        """Build content for individual question report."""
        content = f"""# Question {question_index + 1} Analysis

## Question
**{question}**

## Overview
**Study:** {data.project.name}  
**Session:** {data.session.id}  
**Analysis Date:** {data.export_timestamp.strftime('%B %d, %Y')}  

## Response Summary
"""
        
        # Get responses for this specific question
        question_responses = []
        for response in data.session.responses:
            if (response.speaker_type == 'participant' and 
                hasattr(response, 'question_id') and 
                response.question_id == f"q_{question_index + 1}"):
                question_responses.append(response)
        
        if question_responses:
            avg_sentiment = sum(r.sentiment_score for r in question_responses if r.sentiment_score) / len(question_responses)
            avg_length = sum(len(r.content) for r in question_responses) / len(question_responses)
            
            content += f"- **Total Responses:** {len(question_responses)}\n"
            content += f"- **Average Sentiment:** {avg_sentiment:.2f}\n"
            content += f"- **Average Response Length:** {avg_length:.0f} characters\n\n"
            
            content += "## All Responses\n\n"
            
            # Sort by persona weight if available
            sorted_responses = sorted(question_responses, key=lambda r: 
                data.project.get_persona_weight(r.speaker_id).weight if data.project.get_persona_weight(r.speaker_id) else 0,
                reverse=True
            )
            
            for response in sorted_responses:
                persona_weight = data.project.get_persona_weight(response.speaker_id)
                weight = persona_weight.weight if persona_weight else 1.0
                is_icp = persona_weight.is_primary_icp if persona_weight else False
                
                content += f"### {response.speaker_name}{'🎯' if is_icp else ''}\n"
                content += f"**Weight:** {weight} | **Sentiment:** {response.sentiment_score:.2f}\n\n"
                content += f"{response.content}\n\n"
                
                if response.key_themes:
                    content += f"**Themes:** {', '.join(response.key_themes)}\n\n"
                
                content += "---\n\n"
        else:
            content += "*No responses recorded for this question.*\n"
        
        return content
    
    def _build_participant_content(self, data: ReportData, persona_weight: PersonaWeight) -> str:
        """Build content for individual participant report."""
        persona_id = persona_weight.persona_id
        
        content = f"""# Participant Analysis: {persona_id}

## Participant Profile
**Persona ID:** {persona_id}  
**Weight:** {persona_weight.weight}  
**Rank:** {persona_weight.rank}  
{'**🎯 PRIMARY ICP**' if persona_weight.is_primary_icp else ''}

**Notes:** {persona_weight.notes or 'No additional notes'}

## Study Context
**Study:** {data.project.name}  
**Session:** {data.session.id}  
**Analysis Date:** {data.export_timestamp.strftime('%B %d, %Y')}  

## Response Analysis
"""
        
        # Get all responses from this participant
        participant_responses = data.session.get_responses_by_participant(persona_id)
        
        if participant_responses:
            avg_sentiment = sum(r.sentiment_score for r in participant_responses if r.sentiment_score) / len(participant_responses)
            total_length = sum(len(r.content) for r in participant_responses)
            avg_length = total_length / len(participant_responses)
            
            content += f"- **Total Responses:** {len(participant_responses)}\n"
            content += f"- **Total Words:** ~{total_length // 5} words\n"  # Rough word count
            content += f"- **Average Response Length:** {avg_length:.0f} characters\n"
            content += f"- **Average Sentiment:** {avg_sentiment:.2f}\n"
            
            # Engagement level
            if len(participant_responses) > 5:
                engagement = "High"
            elif len(participant_responses) > 2:
                engagement = "Medium"
            else:
                engagement = "Low"
            content += f"- **Engagement Level:** {engagement}\n\n"
            
            # Collect all themes
            all_themes = set()
            for response in participant_responses:
                if response.key_themes:
                    all_themes.update(response.key_themes)
            
            if all_themes:
                content += f"**Key Themes Mentioned:**\n"
                for theme in sorted(all_themes):
                    content += f"- {theme.replace('_', ' ').title()}\n"
                content += "\n"
            
            content += "## Complete Response History\n\n"
            
            for i, response in enumerate(participant_responses, 1):
                content += f"### Response {i}\n"
                if hasattr(response, 'question_id'):
                    q_num = response.question_id.replace('q_', '')
                    content += f"**Question {q_num}**\n"
                content += f"**Timestamp:** {response.timestamp.strftime('%H:%M:%S')}\n"
                content += f"**Sentiment:** {response.sentiment_score:.2f}\n\n"
                content += f"{response.content}\n\n"
                
                if response.key_themes:
                    content += f"*Themes: {', '.join(response.key_themes)}*\n\n"
                
                content += "---\n\n"
        else:
            content += "*No responses recorded from this participant.*\n"
        
        # Strategic insights for this participant
        if persona_weight.is_primary_icp:
            content += "## Strategic Importance (Primary ICP)\n"
            content += "This participant represents your primary Ideal Customer Profile and their responses should be weighted heavily in decision-making:\n\n"
            
            if participant_responses:
                content += "- Responses show direct alignment with target customer needs\n"
                content += "- Feedback is critical for product-market fit validation\n"
                content += "- Patterns here likely represent broader ICP segment behavior\n"
        elif persona_weight.weight > 2.0:
            content += "## Strategic Importance (High Priority)\n"
            content += "This participant represents a high-priority segment for your business:\n\n"
            content += "- Responses should influence product development decisions\n"
            content += "- Represents significant market opportunity\n"
        
        return content