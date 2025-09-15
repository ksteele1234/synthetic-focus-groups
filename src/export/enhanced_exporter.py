"""
Enhanced data exporter with weighted analysis, ICP focus, and agent-generated insights.
"""

import json
import csv
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.session import Session, SessionResponse
from models.enhanced_project import EnhancedProject, PersonaWeight


class EnhancedDataExporter:
    """Enhanced exporter with weighted analysis and agent insights."""
    
    SCHEMA_VERSION = "1.0.0"
    
    def __init__(self, export_path: str = "data/exports"):
        """Initialize enhanced data exporter."""
        self.export_path = export_path
        os.makedirs(export_path, exist_ok=True)
    """Enhanced exporter with weighted analysis and agent insights."""
    
    def __init__(self, export_path: str = "data/exports"):
        """Initialize enhanced data exporter."""
        self.export_path = export_path
        os.makedirs(export_path, exist_ok=True)
    
    def export_weighted_session_analysis(self, session: Session, project: EnhancedProject, 
                                       agent_results: Dict[str, Any] = None,
                                       filepath: str = None) -> str:
        """Export session analysis with persona weights and ICP focus."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.export_path, f"weighted_analysis_{session.id}_{timestamp}.json")
        
        try:
            # Get persona weights
            weights = project.get_analysis_weights()
            primary_icp_id = project.primary_icp_persona_id
            
            # Calculate weighted sentiment
            weighted_sentiment = self._calculate_weighted_sentiment(session, weights)
            
            # Analyze ICP responses specifically
            icp_analysis = self._analyze_icp_responses(session, primary_icp_id) if primary_icp_id else None
            
            # Organize responses by persona weight tiers
            response_tiers = self._organize_responses_by_weight(session, project.get_ranked_personas())
            
            export_data = {
                'session_info': {
                    'session_id': session.id,
                    'session_name': session.name,
                    'project_id': session.project_id,
                    'duration_minutes': session.actual_duration_minutes,
                    'response_count': len(session.responses),
                    'export_timestamp': datetime.now().isoformat()
                },
                'weighting_system': {
                    'weighted_analysis_enabled': project.weighted_analysis_enabled,
                    'persona_weights': {pw.persona_id: pw.weight for pw in project.persona_weights},
                    'normalized_weights': weights,
                    'primary_icp': primary_icp_id,
                    'ranking_enabled': project.persona_ranking_enabled
                },
                'weighted_analysis': {
                    'overall_sentiment': weighted_sentiment,
                    'response_tiers': response_tiers,
                    'icp_focus_analysis': icp_analysis
                },
                'unweighted_analysis': {
                    'overall_sentiment': self._calculate_unweighted_sentiment(session),
                    'persona_contributions': self._calculate_unweighted_contributions(session)
                },
                'agent_insights': agent_results or {},
                'persona_contributions': self._calculate_persona_contributions(session, weights),
                'recommendations': self._generate_weighted_recommendations(session, project, agent_results)
            }
            
            export_data['schema_version'] = self.SCHEMA_VERSION
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting weighted analysis: {e}")
    
    def export_icp_focused_report(self, session: Session, project: EnhancedProject, 
                                 agent_results: Dict[str, Any] = None,
                                 filepath: str = None) -> str:
        """Export report focused on ICP (Ideal Customer Profile) insights."""
        if not project.primary_icp_persona_id:
            raise ValueError("No primary ICP designated for this project")
        
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.export_path, f"icp_report_{session.id}_{timestamp}.json")
        
        try:
            icp_responses = session.get_responses_by_participant(project.primary_icp_persona_id)
            
            # Get ICP persona weight info
            icp_weight_info = project.get_persona_weight(project.primary_icp_persona_id)
            
            # Analyze ICP-specific patterns
            icp_analysis = self._deep_analyze_icp(icp_responses, icp_weight_info)
            
            # Compare ICP vs others
            comparison_analysis = self._compare_icp_to_others(session, project)
            
            export_data = {
                'icp_profile': {
                    'persona_id': project.primary_icp_persona_id,
                    'weight': icp_weight_info.weight if icp_weight_info else 1.0,
                    'rank': icp_weight_info.rank if icp_weight_info else None,
                    'notes': icp_weight_info.notes if icp_weight_info else ""
                },
                'icp_responses': {
                    'total_responses': len(icp_responses),
                    'average_length': sum(len(r.content) for r in icp_responses) / max(len(icp_responses), 1),
                    'sentiment_scores': [r.sentiment_score for r in icp_responses if r.sentiment_score],
                    'key_themes': list(set([theme for r in icp_responses for theme in r.key_themes]))
                },
                'icp_analysis': icp_analysis,
                'comparison_to_others': comparison_analysis,
                'strategic_implications': self._generate_icp_strategy_insights(
                    icp_analysis, comparison_analysis, agent_results
                ),
                'export_info': {
                    'session_id': session.id,
                    'timestamp': datetime.now().isoformat(),
                    'focus': 'primary_icp_analysis'
                }
            }
            
            export_data['schema_version'] = self.SCHEMA_VERSION
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting ICP report: {e}")
    
    def export_agent_insights_dashboard(self, agent_results: Dict[str, Any], 
                                      session_context: Dict[str, Any] = None,
                                      filepath: str = None) -> str:
        """Export comprehensive agent insights in dashboard format."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.export_path, f"agent_dashboard_{timestamp}.json")
        
        try:
            # Extract insights from each agent
            methodologist_results = agent_results.get('methodologist_validate_research_design', {})
            coding_results = agent_results.get('coding_specialist_analyze_responses', {})
            viz_results = agent_results.get('viz_designer_create_visuals', {})
            orchestrator_results = agent_results.get('orchestrator_generate_final_report', {})
            
            dashboard_data = {
                'dashboard_info': {
                    'generated_at': datetime.now().isoformat(),
                    'session_context': session_context or {},
                    'agents_involved': list(agent_results.keys())
                },
                'methodology_assessment': {
                    'validation_score': methodologist_results.get('validation', {}).get('methodology_score', 0),
                    'bias_warnings': methodologist_results.get('validation', {}).get('bias_warnings', []),
                    'improved_questions': methodologist_results.get('validation', {}).get('improved_questions', []),
                    'status': 'validated' if methodologist_results.get('success') else 'needs_review'
                },
                'thematic_analysis': {
                    'themes_identified': len(coding_results.get('themes', [])),
                    'quality_score': coding_results.get('coding_quality', {}).get('overall_score', 0),
                    'top_themes': coding_results.get('themes', [])[:5],
                    'sentiment_summary': coding_results.get('sentiment', {}),
                    'key_insights': coding_results.get('insights', [])
                },
                'visualizations': {
                    'available_charts': list(viz_results.get('visualizations', {}).keys()),
                    'executive_summary': viz_results.get('visualizations', {}).get('executive_summary_visual', {}),
                    'dashboard_spec': viz_results.get('visualizations', {}).get('insight_dashboard', {})
                },
                'executive_report': {
                    'report_available': orchestrator_results.get('success', False),
                    'report_preview': orchestrator_results.get('report', '')[:500] + '...' if orchestrator_results.get('report') else '',
                    'full_report_path': 'See orchestrator results for full report'
                },
                'quality_metrics': {
                    'overall_confidence': self._calculate_overall_confidence(agent_results),
                    'completeness_score': self._calculate_completeness_score(agent_results),
                    'data_quality_flags': self._identify_quality_flags(agent_results)
                },
                'recommendations': {
                    'immediate_actions': self._extract_immediate_actions(agent_results),
                    'strategic_insights': self._extract_strategic_insights(agent_results),
                    'next_research_steps': self._suggest_next_research(agent_results)
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting agent dashboard: {e}")
    
    def export_weighted_csv(self, session: Session, project: EnhancedProject, 
                          filepath: str = None) -> str:
        """Export CSV with weighted analysis data."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.export_path, f"weighted_responses_{session.id}_{timestamp}.csv")
        
        try:
            csv_data = []
            weights = project.get_analysis_weights()
            
            for response in session.responses:
                if response.speaker_type == 'participant':
                    persona_weight_obj = project.get_persona_weight(response.speaker_id)
                    
                    row = {
                        'session_id': response.session_id,
                        'response_id': response.id,
                        'sequence_number': response.sequence_number,
                        'timestamp': response.timestamp.isoformat(),
                        'speaker_id': response.speaker_id,
                        'speaker_name': response.speaker_name,
                        'content': response.content,
                        'sentiment_score': response.sentiment_score,
                        'persona_weight': weights.get(response.speaker_id, 1.0),
                        'persona_rank': persona_weight_obj.rank if persona_weight_obj else None,
                        'is_primary_icp': persona_weight_obj.is_primary_icp if persona_weight_obj else False,
                        'weighted_sentiment': (response.sentiment_score or 0) * weights.get(response.speaker_id, 1.0),
                        'response_length': len(response.content),
                        'weighted_importance': self._calculate_response_importance(response, weights),
                        'themes': '; '.join(response.key_themes) if response.key_themes else '',
                        'emotion_tags': '; '.join(response.emotion_tags) if response.emotion_tags else ''
                    }
                    csv_data.append(row)
            
            if csv_data:
                fieldnames = csv_data[0].keys()
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(csv_data)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error exporting weighted CSV: {e}")
    
    def export_comprehensive_package(self, session: Session, project: EnhancedProject, 
                                   agent_results: Dict[str, Any] = None,
                                   package_name: str = None,
                                   guardrails: List[Dict[str, Any]] = None) -> str:
        """Create comprehensive export package with all enhanced features."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = package_name or f"enhanced_analysis_{session.id}_{timestamp}"
        package_dir = os.path.join(self.export_path, package_name)
        os.makedirs(package_dir, exist_ok=True)
        
        try:
            # Export all enhanced formats
            files_created = {}
            
            # Weighted + unweighted analysis
            files_created['weighted_analysis'] = self.export_weighted_session_analysis(
                session, project, agent_results, 
                os.path.join(package_dir, "weighted_analysis.json")
            )
            # Also emit an explicit unweighted file for clarity
            unweighted_path = os.path.join(package_dir, "unweighted_analysis.json")
            with open(files_created['weighted_analysis'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            unweighted_payload = {
                'schema_version': self.SCHEMA_VERSION,
                'session_id': session.id,
                'project_id': project.id,
                'unweighted_analysis': data.get('unweighted_analysis', {})
            }
            with open(unweighted_path, 'w', encoding='utf-8') as f:
                json.dump(unweighted_payload, f, indent=2, ensure_ascii=False)
            files_created['unweighted_analysis'] = unweighted_path
            
            # ICP-focused report (if ICP exists)
            if project.primary_icp_persona_id:
                files_created['icp_report'] = self.export_icp_focused_report(
                    session, project, agent_results,
                    os.path.join(package_dir, "icp_focused_report.json")
                )
            
            # Agent insights dashboard
            if agent_results:
                files_created['agent_dashboard'] = self.export_agent_insights_dashboard(
                    agent_results, {'session_id': session.id, 'project_id': project.id},
                    os.path.join(package_dir, "agent_insights_dashboard.json")
                )
            
            # Weighted CSV
            files_created['weighted_csv'] = self.export_weighted_csv(
                session, project, 
                os.path.join(package_dir, "weighted_responses.csv")
            )
            
            # Guardrails export if provided
            if guardrails:
                files_created['guardrails_csv'] = self.export_guardrails_csv(
                    guardrails, os.path.join(package_dir, "guardrails.csv")
                )
            
            # YAML bundle
            try:
                files_created['yaml_bundle'] = self.export_yaml_bundle(
                    session, project, os.path.join(package_dir, "bundle.yaml")
                )
            except Exception:
                pass
            
            # Project configuration export
            files_created['project_config'] = self._export_project_config(
                project, os.path.join(package_dir, "project_configuration.json")
            )
            
            # Executive summary
            files_created['executive_summary'] = self._create_executive_summary_file(
                session, project, agent_results, 
                os.path.join(package_dir, "executive_summary.md")
            )
            
            # Package manifest
            manifest = {
                'schema_version': self.SCHEMA_VERSION,
                'package_info': {
                    'name': package_name,
                    'created_at': datetime.now().isoformat(),
                    'session_id': session.id,
                    'project_id': project.id,
                    'project_name': project.name
                },
                'files_included': files_created,
                'analysis_features': {
                    'weighted_analysis': project.weighted_analysis_enabled,
                    'icp_analysis': project.primary_icp_persona_id is not None,
                    'agent_insights': agent_results is not None,
                    'persona_count': len(project.persona_weights),
                    'primary_icp': project.primary_icp_persona_id
                },
                'usage_instructions': {
                    'weighted_analysis': 'Contains persona-weighted analysis with normalized importance scores',
                    'icp_report': 'Focused analysis on primary ICP responses and behaviors',
                    'agent_dashboard': 'Comprehensive insights from all AI agents involved in analysis',
                    'weighted_csv': 'Response data with weighting calculations for external analysis',
                    'executive_summary': 'Human-readable summary of key findings and recommendations'
                }
            }
            
            manifest_path = os.path.join(package_dir, "manifest.json")
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            # Checksums
            checksums = {name: self._checksum(path) for name, path in files_created.items() if isinstance(path, str)}
            with open(os.path.join(package_dir, "checksums.json"), 'w', encoding='utf-8') as f:
                json.dump(checksums, f, indent=2, ensure_ascii=False)
            
            return package_dir
            
        except Exception as e:
            raise Exception(f"Error creating comprehensive package: {e}")
    
    def _calculate_weighted_sentiment(self, session: Session, weights: Dict[str, float]) -> Dict[str, Any]:
        """Calculate weighted sentiment analysis."""
        participant_responses = [r for r in session.responses if r.speaker_type == 'participant']
        
        if not participant_responses:
            return {'overall': 'neutral', 'weighted_score': 0.5, 'confidence': 'low'}
        
        weighted_scores = []
        total_weight = 0
        
        for response in participant_responses:
            if response.sentiment_score is not None:
                weight = weights.get(response.speaker_id, 1.0)
                weighted_scores.append(response.sentiment_score * weight)
                total_weight += weight
        
        if not weighted_scores:
            return {'overall': 'neutral', 'weighted_score': 0.5, 'confidence': 'low'}
        
        weighted_avg = sum(weighted_scores) / total_weight if total_weight > 0 else 0.5
        
        return {
            'overall': 'positive' if weighted_avg > 0.1 else 'negative' if weighted_avg < -0.1 else 'neutral',
            'weighted_score': weighted_avg,
            'confidence': 'high' if len(weighted_scores) >= 10 else 'medium' if len(weighted_scores) >= 5 else 'low',
            'response_count': len(weighted_scores),
            'total_weight_applied': total_weight
        }
    
    def _calculate_unweighted_sentiment(self, session: Session) -> Dict[str, Any]:
        """Calculate unweighted sentiment analysis."""
        participant_responses = [r for r in session.responses if r.speaker_type == 'participant']
        scores = [r.sentiment_score for r in participant_responses if r.sentiment_score is not None]
        if not scores:
            return {'overall': 'neutral', 'score': 0.5, 'count': 0}
        avg = sum(scores) / len(scores)
        return {
            'overall': 'positive' if avg > 0.1 else 'negative' if avg < -0.1 else 'neutral',
            'score': avg,
            'count': len(scores)
        }

    def _analyze_icp_responses(self, session: Session, icp_persona_id: str) -> Dict[str, Any]:
        """Analyze responses specifically from the ICP persona."""
        icp_responses = session.get_responses_by_participant(icp_persona_id)
        
        if not icp_responses:
            return {'error': 'No responses found for ICP persona'}
        
        sentiment_scores = [r.sentiment_score for r in icp_responses if r.sentiment_score is not None]
        all_themes = []
        for r in icp_responses:
            all_themes.extend(r.key_themes)
        
        return {
            'response_count': len(icp_responses),
            'avg_sentiment': sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0,
            'unique_themes': list(set(all_themes)),
            'avg_response_length': sum(len(r.content) for r in icp_responses) / len(icp_responses),
            'engagement_level': 'high' if len(icp_responses) > 5 else 'medium' if len(icp_responses) > 2 else 'low',
            'key_quotes': [r.content[:100] + '...' for r in icp_responses[:3]]
        }
    
    def _organize_responses_by_weight(self, session: Session, ranked_personas: List[PersonaWeight]) -> Dict[str, Any]:
        """Organize responses by persona weight tiers."""
        tiers = {'high_priority': [], 'medium_priority': [], 'low_priority': []}
        
        for persona_weight in ranked_personas:
            responses = session.get_responses_by_participant(persona_weight.persona_id)
            
            tier = 'high_priority' if persona_weight.weight >= 2.0 else 'medium_priority' if persona_weight.weight >= 1.0 else 'low_priority'
            
            tiers[tier].extend([{
                'persona_id': persona_weight.persona_id,
                'weight': persona_weight.weight,
                'rank': persona_weight.rank,
                'is_primary_icp': persona_weight.is_primary_icp,
                'response_count': len(responses),
                'avg_sentiment': sum(r.sentiment_score for r in responses if r.sentiment_score) / max(len([r for r in responses if r.sentiment_score]), 1)
            }])
        
        return tiers
    
    def _calculate_persona_contributions(self, session: Session, weights: Dict[str, float]) -> Dict[str, Any]:
        """Calculate each persona's contribution to overall insights."""
        contributions = {}
        
        for persona_id, weight in weights.items():
            responses = session.get_responses_by_participant(persona_id)
            
            contributions[persona_id] = {
                'weight': weight,
                'response_count': len(responses),
                'total_content_length': sum(len(r.content) for r in responses),
                'weighted_contribution': len(responses) * weight,
                'unique_themes': len(set([theme for r in responses for theme in r.key_themes])),
                'avg_sentiment': sum(r.sentiment_score for r in responses if r.sentiment_score) / max(len([r for r in responses if r.sentiment_score]), 1)
            }
        
        return contributions
    
    def _calculate_unweighted_contributions(self, session: Session) -> Dict[str, Any]:
        """Unweighted persona contributions for baseline comparison."""
        contributions = {}
        participants = [r.speaker_id for r in session.responses if r.speaker_type == 'participant']
        for pid in set(participants):
            responses = session.get_responses_by_participant(pid)
            contributions[pid] = {
                'weight': 1.0,
                'response_count': len(responses),
                'total_content_length': sum(len(r.content) for r in responses),
                'unique_themes': len(set([theme for r in responses for theme in r.key_themes])),
                'avg_sentiment': sum(r.sentiment_score for r in responses if r.sentiment_score) / max(len([r for r in responses if r.sentiment_score]), 1)
            }
        return contributions

    def _generate_weighted_recommendations(self, session: Session, project: EnhancedProject, 
                                         agent_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on weighted analysis."""
        recommendations = []
        
        # Analyze weight distribution
        weights = list(project.get_analysis_weights().values())
        weight_variance = max(weights) - min(weights) if weights else 0
        
        if weight_variance > 1.0:
            recommendations.append("Consider balancing persona weights - high variance detected in importance levels")
        
        if project.primary_icp_persona_id:
            icp_responses = session.get_responses_by_participant(project.primary_icp_persona_id)
            if len(icp_responses) < 3:
                recommendations.append("Primary ICP provided limited responses - consider follow-up engagement")
        
        # Add agent-based recommendations
        if agent_results:
            coding_results = agent_results.get('coding_specialist_analyze_responses', {})
            if coding_results.get('recommendations'):
                recommendations.extend(coding_results['recommendations'][:2])
        
        return recommendations
    
    def _deep_analyze_icp(self, icp_responses: List[SessionResponse], weight_info: PersonaWeight) -> Dict[str, Any]:
        """Deep analysis of ICP responses."""
        return {
            'response_patterns': {
                'avg_length': sum(len(r.content) for r in icp_responses) / max(len(icp_responses), 1),
                'sentiment_trend': [r.sentiment_score for r in icp_responses if r.sentiment_score],
                'engagement_consistency': len(icp_responses) / max(1, 1)  # Placeholder calculation
            },
            'content_analysis': {
                'key_themes': list(set([theme for r in icp_responses for theme in r.key_themes])),
                'emotional_indicators': list(set([tag for r in icp_responses for tag in r.emotion_tags])),
                'decision_factors_mentioned': self._extract_decision_factors(icp_responses)
            },
            'strategic_value': {
                'weight': weight_info.weight if weight_info else 1.0,
                'priority_rank': weight_info.rank if weight_info else None,
                'strategic_notes': weight_info.notes if weight_info else ""
            }
        }
    
    def _compare_icp_to_others(self, session: Session, project: EnhancedProject) -> Dict[str, Any]:
        """Compare ICP responses to other participants."""
        icp_responses = session.get_responses_by_participant(project.primary_icp_persona_id)
        other_responses = [r for r in session.responses 
                          if r.speaker_type == 'participant' and r.speaker_id != project.primary_icp_persona_id]
        
        return {
            'response_volume': {
                'icp_count': len(icp_responses),
                'others_avg': len(other_responses) / max(len(project.persona_weights) - 1, 1),
                'relative_engagement': 'high' if len(icp_responses) > len(other_responses) / max(len(project.persona_weights) - 1, 1) else 'low'
            },
            'sentiment_comparison': {
                'icp_avg': sum(r.sentiment_score for r in icp_responses if r.sentiment_score) / max(len([r for r in icp_responses if r.sentiment_score]), 1),
                'others_avg': sum(r.sentiment_score for r in other_responses if r.sentiment_score) / max(len([r for r in other_responses if r.sentiment_score]), 1),
            },
            'unique_themes': {
                'icp_only': list(set([theme for r in icp_responses for theme in r.key_themes]) - 
                               set([theme for r in other_responses for theme in r.key_themes])),
                'shared_themes': list(set([theme for r in icp_responses for theme in r.key_themes]) & 
                                    set([theme for r in other_responses for theme in r.key_themes]))
            }
        }
    
    def _generate_icp_strategy_insights(self, icp_analysis: Dict[str, Any], 
                                      comparison: Dict[str, Any], 
                                      agent_results: Dict[str, Any]) -> List[str]:
        """Generate strategic insights focused on ICP."""
        insights = []
        
        # Based on response volume
        if comparison['response_volume']['relative_engagement'] == 'high':
            insights.append("ICP shows high engagement - leverage this for deeper insights")
        else:
            insights.append("ICP engagement is low - consider targeted follow-up research")
        
        # Based on unique themes
        if comparison['unique_themes']['icp_only']:
            insights.append(f"ICP has unique concerns: {', '.join(comparison['unique_themes']['icp_only'][:3])}")
        
        # Based on sentiment
        icp_sentiment = comparison['sentiment_comparison']['icp_avg']
        others_sentiment = comparison['sentiment_comparison']['others_avg']
        
        if icp_sentiment > others_sentiment + 0.2:
            insights.append("ICP sentiment significantly more positive than others")
        elif icp_sentiment < others_sentiment - 0.2:
            insights.append("ICP sentiment concerns identified - investigate barriers")
        
        return insights
    
    def _calculate_overall_confidence(self, agent_results: Dict[str, Any]) -> float:
        """Calculate overall confidence score from agent results."""
        confidence_scores = []
        
        # Methodology confidence
        method_score = agent_results.get('methodologist_validate_research_design', {}).get('validation', {}).get('methodology_score', 0)
        confidence_scores.append(method_score / 100)
        
        # Coding quality confidence
        coding_quality = agent_results.get('coding_specialist_analyze_responses', {}).get('coding_quality', {}).get('overall_score', 0)
        confidence_scores.append(coding_quality / 100)
        
        return sum(confidence_scores) / max(len(confidence_scores), 1)
    
    def _calculate_completeness_score(self, agent_results: Dict[str, Any]) -> float:
        """Calculate completeness score based on agent outputs."""
        completeness_factors = []
        
        # Check if each agent provided results
        expected_agents = ['methodologist', 'coding_specialist', 'viz_designer']
        for agent in expected_agents:
            agent_key = f"{agent}_" 
            has_results = any(key.startswith(agent_key) for key in agent_results.keys())
            completeness_factors.append(1.0 if has_results else 0.0)
        
        return sum(completeness_factors) / len(completeness_factors)
    
    def _identify_quality_flags(self, agent_results: Dict[str, Any]) -> List[str]:
        """Identify quality concerns from agent results."""
        flags = []
        
        # Check methodology flags
        method_results = agent_results.get('methodologist_validate_research_design', {})
        if method_results.get('validation', {}).get('bias_warnings'):
            flags.append("Research design contains bias warnings")
        
        # Check coding quality flags
        coding_results = agent_results.get('coding_specialist_analyze_responses', {})
        coding_score = coding_results.get('coding_quality', {}).get('overall_score', 100)
        if coding_score < 60:
            flags.append("Low coding quality score detected")
        
        return flags
    
    def _extract_immediate_actions(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract immediate action items from agent results."""
        actions = []
        
        # From methodology
        method_results = agent_results.get('methodologist_validate_research_design', {})
        if method_results.get('validation', {}).get('suggestions'):
            actions.extend(method_results['validation']['suggestions'][:2])
        
        # From coding specialist
        coding_results = agent_results.get('coding_specialist_analyze_responses', {})
        if coding_results.get('recommendations'):
            actions.extend(coding_results['recommendations'][:2])
        
        return actions[:5]  # Limit to top 5
    
    def _extract_strategic_insights(self, agent_results: Dict[str, Any]) -> List[str]:
        """Extract strategic insights from agent results."""
        insights = []
        
        coding_results = agent_results.get('coding_specialist_analyze_responses', {})
        if coding_results.get('insights'):
            insights.extend(coding_results['insights'][:3])
        
        return insights
    
    def _suggest_next_research(self, agent_results: Dict[str, Any]) -> List[str]:
        """Suggest next research steps based on findings."""
        suggestions = [
            "Conduct follow-up interviews with high-engagement participants",
            "Validate key themes through quantitative survey",
            "Test specific hypotheses identified in analysis"
        ]
        
        return suggestions[:3]
    
    def export_guardrails_csv(self, guardrails: List[Dict[str, Any]], filepath: str) -> str:
        """Export guardrail events to CSV."""
        import csv
        if not guardrails:
            return filepath
        fieldnames = sorted({k for ev in guardrails for k in ev.keys()})
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for ev in guardrails:
                writer.writerow(ev)
        return filepath

    def export_yaml_bundle(self, session: Session, project: EnhancedProject, filepath: str) -> str:
        """Export a simple YAML bundle with schema_version, study and personas."""
        try:
            import yaml
        except ImportError:
            raise Exception("PyYAML not installed. Install with: pip install pyyaml")
        bundle = {
            'schema_version': self.SCHEMA_VERSION,
            'study': {
                'id': project.id,
                'name': project.name,
                'research_topic': project.research_topic,
                'weighted_analysis_enabled': project.weighted_analysis_enabled,
                'primary_icp': project.primary_icp_persona_id,
                'persona_weights': [pw.__dict__ for pw in project.persona_weights],
            },
            'session': {
                'id': session.id,
                'project_id': session.project_id,
                'name': session.name,
            }
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.safe_dump(bundle, f, sort_keys=False, allow_unicode=True)
        return filepath

    def _calculate_response_importance(self, response: SessionResponse, weights: Dict[str, float]) -> float:
        """Calculate weighted importance score for a response."""
        base_score = len(response.content) / 100  # Base on content length
        weight_multiplier = weights.get(response.speaker_id, 1.0)
        sentiment_boost = abs(response.sentiment_score or 0) * 0.5  # Boost for strong sentiment
        
        return (base_score + sentiment_boost) * weight_multiplier
    
    def _export_project_config(self, project: EnhancedProject, filepath: str) -> str:
        """Export project configuration."""
        data = project.to_dict()
        data['schema_version'] = self.SCHEMA_VERSION
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath
    
    def _create_executive_summary_file(self, session: Session, project: EnhancedProject, 
                                     agent_results: Dict[str, Any], filepath: str) -> str:
        """Create executive summary markdown file."""
        coding_results = agent_results.get('coding_specialist_analyze_responses', {}) if agent_results else {}
        
        summary_content = f"""# Executive Summary: {project.name}

## Overview
- **Session Duration**: {session.actual_duration_minutes or 'N/A'} minutes
- **Participants**: {len(project.persona_weights)}
- **Primary ICP**: {'Yes' if project.primary_icp_persona_id else 'No'}
- **Weighted Analysis**: {'Enabled' if project.weighted_analysis_enabled else 'Disabled'}

## Key Findings
{chr(10).join(['- ' + insight for insight in coding_results.get('insights', ['Analysis results not available'])[:5]])}

## Top Themes
{chr(10).join(['- ' + theme.get('theme', 'Unknown') + ': ' + theme.get('description', 'No description') for theme in coding_results.get('themes', [])[:5]])}

## Recommendations
{chr(10).join(['- ' + rec for rec in coding_results.get('recommendations', ['No specific recommendations available'])[:5]])}

## Next Steps
1. Review detailed analysis in accompanying data files
2. Validate key findings with stakeholders  
3. Plan follow-up research if needed

---
*Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return filepath
    
    def _checksum(self, path: str) -> Optional[str]:
        try:
            import hashlib
            h = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None
    
    def _extract_decision_factors(self, responses: List[SessionResponse]) -> List[str]:
        """Extract decision factors mentioned in responses."""
        decision_keywords = ['price', 'cost', 'quality', 'brand', 'feature', 'service', 'convenience', 'trust']
        factors = []
        
        for response in responses:
            content_lower = response.content.lower()
            for keyword in decision_keywords:
                if keyword in content_lower:
                    factors.append(keyword)
        
        return list(set(factors))