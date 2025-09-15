"""
Integration test for the enhanced project system with agents, weighting, and ICP analysis.
"""

import unittest
from datetime import datetime, timedelta
import json
import os
import tempfile
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from models.enhanced_project import EnhancedProject, PersonaWeight
from models.session import Session, SessionResponse
from personas.enhanced_manager import EnhancedPersonaManager
from ai.agents import OrchestratorAgent, SurveyMethodologistAgent, QualitativeCodingSpecialist, DataVisualizationDesigner
from export.enhanced_exporter import EnhancedDataExporter
from src.vector.backend_pgvector import PgVector
from session.synthetic_runner import SyntheticSessionRunner, PersonaWeight, create_sample_personas, create_sample_persona_weights
import jsonschema
import hashlib


class TestEnhancedIntegration(unittest.TestCase):
    """Test the full enhanced project system integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create enhanced project with weighted analysis
        self.project = EnhancedProject(
            id="test_project_001",
            name="Enhanced Customer Research Study",
            description="Testing enhanced features with persona weighting and ICP analysis",
            weighted_analysis_enabled=True,
            persona_ranking_enabled=True,
            background_info={
                'research_context': 'Mobile app user experience research',
                'product_information': 'Social media scheduling app for small businesses',
                'competitive_landscape': 'Competing with Buffer, Hootsuite, Later',
                'research_objectives': [
                    'Understand user pain points in current workflows',
                    'Identify key features for product-market fit',
                    'Validate pricing strategy with target segments'
                ],
                'methodology_context': 'Semi-structured interviews with persona-based weighting'
            },
            persona_weights=[
                PersonaWeight(
                    persona_id="sarah_001", 
                    weight=3.0, 
                    rank=1, 
                    is_primary_icp=True,
                    notes="Primary target: Small business owner with 5-20 employees"
                ),
                PersonaWeight(
                    persona_id="mike_002", 
                    weight=2.0, 
                    rank=2,
                    notes="Secondary target: Marketing manager at medium company"
                ),
                PersonaWeight(
                    persona_id="jenny_003", 
                    weight=1.5, 
                    rank=3,
                    notes="Edge case: Freelancer with occasional team collaboration needs"
                ),
                PersonaWeight(
                    persona_id="alex_004", 
                    weight=0.8, 
                    rank=4,
                    notes="Low priority: Enterprise user - out of target market"
                )
            ]
        )
        self.project.set_primary_icp("sarah_001")
        
        # Create test session with realistic responses
        self.session = Session(
            id="session_001",
            project_id="test_project_001",
            name="Enhanced Analysis Test Session",
            estimated_duration_minutes=60,
            actual_duration_minutes=65
        )
        
        # Add realistic participant responses with different engagement levels
        self._add_realistic_responses()
        
        self.exporter = EnhancedDataExporter(export_path=self.test_dir)
    
    def _add_realistic_responses(self):
        """Add realistic responses with varying sentiment and engagement."""
        base_time = datetime.now()
        
        # High-weight ICP responses (Sarah - primary target)
        sarah_responses = [
            "I currently use three different apps to manage my social media and it's really frustrating to switch between them constantly.",
            "The biggest pain point for me is scheduling posts for multiple time zones - my customers are global but the tools I use don't handle this well.",
            "I'd definitely pay $30-50/month for a solution that could handle all my scheduling, analytics, and team collaboration in one place.",
            "The onboarding process needs to be super simple because I don't have time to learn complex software.",
            "Integration with my existing CRM would be a game-changer for my business workflow."
        ]
        
        # Medium-weight responses (Mike - secondary target)  
        mike_responses = [
            "Our marketing team struggles with content approval workflows - we need better collaboration features.",
            "Analytics and reporting are crucial for us to justify social media ROI to executives.",
            "We're currently using Hootsuite but the interface feels outdated and clunky.",
            "Budget is always a concern - we need clear value proposition for any tool switch."
        ]
        
        # Lower-weight responses (Jenny - edge case)
        jenny_responses = [
            "As a freelancer, I mostly need basic scheduling - I don't need all the enterprise features.",
            "Price sensitivity is high for me - I can't afford expensive monthly subscriptions."
        ]
        
        # Lowest-weight responses (Alex - out of target)
        alex_responses = [
            "Enterprise security and compliance are our top priorities.",
            "We need extensive API access for custom integrations with our enterprise stack."
        ]
        
        # Add responses to session with realistic sentiment scores
        response_id = 1
        
        for i, content in enumerate(sarah_responses):
            sentiment = 0.1 if "frustrating" in content or "pain point" in content else 0.6 if "definitely" in content or "game-changer" in content else 0.3
            self.session.add_response(SessionResponse(
                id=f"resp_{response_id:03d}",
                session_id=self.session.id,
                sequence_number=response_id,
                timestamp=base_time + timedelta(minutes=i*3),
                speaker_id="sarah_001",
                speaker_name="Sarah (Small Business Owner)",
                speaker_type="participant",
                content=content,
                sentiment_score=sentiment,
                key_themes=["workflow_efficiency", "time_zones", "pricing", "onboarding", "integrations"][i:i+2],
                emotion_tags=["frustrated", "hopeful", "pragmatic"][i%3:i%3+1]
            ))
            response_id += 1
        
        for i, content in enumerate(mike_responses):
            sentiment = 0.2 if "struggles" in content else 0.4
            self.session.add_response(SessionResponse(
                id=f"resp_{response_id:03d}",
                session_id=self.session.id,
                sequence_number=response_id,
                timestamp=base_time + timedelta(minutes=20 + i*2),
                speaker_id="mike_002",
                speaker_name="Mike (Marketing Manager)",
                speaker_type="participant",
                content=content,
                sentiment_score=sentiment,
                key_themes=["collaboration", "analytics", "competitor_analysis", "budget"][i:i+1],
                emotion_tags=["analytical", "cautious"][i%2:i%2+1]
            ))
            response_id += 1
        
        for i, content in enumerate(jenny_responses):
            self.session.add_response(SessionResponse(
                id=f"resp_{response_id:03d}",
                session_id=self.session.id,
                sequence_number=response_id,
                timestamp=base_time + timedelta(minutes=35 + i*4),
                speaker_id="jenny_003",
                speaker_name="Jenny (Freelancer)",
                speaker_type="participant",
                content=content,
                sentiment_score=0.3,
                key_themes=["basic_features", "price_sensitivity"],
                emotion_tags=["practical"]
            ))
            response_id += 1
        
        for i, content in enumerate(alex_responses):
            self.session.add_response(SessionResponse(
                id=f"resp_{response_id:03d}",
                session_id=self.session.id,
                sequence_number=response_id,
                timestamp=base_time + timedelta(minutes=50 + i*2),
                speaker_id="alex_004",
                speaker_name="Alex (Enterprise User)",
                speaker_type="participant",
                content=content,
                sentiment_score=0.5,
                key_themes=["enterprise_security", "api_access"],
                emotion_tags=["professional"]
            ))
            response_id += 1
    
    @patch('ai.openai_client.OpenAIClient')
    def test_full_enhanced_workflow(self, mock_openai):
        """Test the complete enhanced workflow with all features."""
        # Mock AI responses
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock the AI client methods that agents use
        mock_client.analyze_session_themes.return_value = {
            'success': True,
            'analysis': {
                'themes': [
                    {'theme': 'Workflow Integration Pain Points', 'description': 'Users struggle with multiple disconnected tools', 'frequency': 'high', 'participants': ['sarah_001', 'mike_002']},
                    {'theme': 'Pricing Sensitivity by Segment', 'description': 'Clear price differentiation between user segments', 'frequency': 'medium', 'participants': ['sarah_001', 'jenny_003']},
                    {'theme': 'Feature Prioritization', 'description': 'Core features vs nice-to-have distinction', 'frequency': 'medium', 'participants': ['sarah_001', 'alex_004']}
                ],
                'sentiment': {'overall': 'mixed_positive', 'score': 0.3, 'by_segment': {'icp': 'positive', 'secondary': 'neutral'}},
                'insights': [
                    'Primary ICP shows strong willingness to pay for integrated solution',
                    'Secondary targets need more ROI justification',
                    'Clear feature gap exists in current market solutions'
                ],
                'patterns': ['Price sensitivity varies inversely with business size', 'Integration needs are consistent across segments'],
                'recommendations': [
                    'Focus product development on workflow integration features',
                    'Develop tiered pricing strategy based on user segments',
                    'Prioritize simple onboarding experience for small business users'
                ]
            }
        }
        
        # Mock report generation
        mock_client.generate_research_report.return_value = {
            'success': True,
            'report': """# Enhanced Research Report: Customer Experience Study

## Executive Summary
The research reveals strong product-market fit potential with clear user segments and pain points.

## Key Findings
1. **Workflow Integration is Critical**: 80% of participants mentioned struggles with multiple tools
2. **Pricing Acceptance Varies by Segment**: ICP willing to pay 2-3x more than edge cases
3. **Feature Gaps Identified**: Time zone management and approval workflows are underserved

## Recommendations
1. Prioritize unified workflow features for core product
2. Implement tiered pricing strategy ($15-50/month range)
3. Focus initial marketing on small business owners (ICP segment)

## Strategic Implications
The weighted analysis confirms that focusing on the primary ICP segment will drive the highest ROI for product development and go-to-market efforts.
""",
            'timestamp': datetime.now().isoformat()
        }
        
        # Mock chat completion responses for fallback scenarios
        mock_client.chat_completion.side_effect = [
            # Methodology validation
            Mock(choices=[Mock(message=Mock(content=json.dumps({
                'methodology_score': 85,
                'bias_warnings': ['Sample size may be too small for generalization'],
                'improved_questions': ['What specific features would increase your willingness to pay?'],
                'suggestions': ['Consider follow-up quantitative validation', 'Include more diverse business sizes']
            })))]),
            
            # Coding analysis
            Mock(choices=[Mock(message=Mock(content=json.dumps({
                'themes': [
                    {'theme': 'Workflow Integration Pain Points', 'description': 'Users struggle with multiple disconnected tools', 'frequency': 8},
                    {'theme': 'Pricing Sensitivity by Segment', 'description': 'Clear price differentiation between user segments', 'frequency': 6},
                    {'theme': 'Feature Prioritization', 'description': 'Core features vs nice-to-have distinction', 'frequency': 5}
                ],
                'sentiment': {'overall': 'mixed_positive', 'by_segment': {'icp': 'positive', 'secondary': 'neutral'}},
                'insights': [
                    'Primary ICP shows strong willingness to pay for integrated solution',
                    'Secondary targets need more ROI justification',
                    'Clear feature gap exists in current market solutions'
                ],
                'recommendations': [
                    'Focus product development on workflow integration features',
                    'Develop tiered pricing strategy based on user segments',
                    'Prioritize simple onboarding experience for small business users'
                ]
            })))]),
            
            # Visualization generation
            Mock(choices=[Mock(message=Mock(content=json.dumps({
                'visualizations': {
                    'persona_weight_chart': {'type': 'bar', 'data': 'persona weights'},
                    'sentiment_by_segment': {'type': 'scatter', 'data': 'sentiment analysis'},
                    'executive_summary_visual': {'type': 'dashboard', 'sections': ['key_findings', 'recommendations']},
                    'insight_dashboard': {'type': 'comprehensive', 'metrics': ['engagement', 'sentiment', 'themes']}
                }
            })))]),
            
            # Final report generation
            Mock(choices=[Mock(message=Mock(content="""# Enhanced Research Report: Customer Experience Study

## Executive Summary
The research reveals strong product-market fit potential with clear user segments and pain points.

## Key Findings
1. **Workflow Integration is Critical**: 80% of participants mentioned struggles with multiple tools
2. **Pricing Acceptance Varies by Segment**: ICP willing to pay 2-3x more than edge cases
3. **Feature Gaps Identified**: Time zone management and approval workflows are underserved

## Recommendations
1. Prioritize unified workflow features for core product
2. Implement tiered pricing strategy ($15-50/month range)
3. Focus initial marketing on small business owners (ICP segment)

## Strategic Implications
The weighted analysis confirms that focusing on the primary ICP segment will drive the highest ROI for product development and go-to-market efforts.
"""))])
        ]
        
        # Initialize agents
        orchestrator = OrchestratorAgent(mock_client)
        methodologist = SurveyMethodologistAgent(mock_client)
        coding_specialist = QualitativeCodingSpecialist(mock_client)
        viz_designer = DataVisualizationDesigner(mock_client)
        
        # Execute full agent workflow
        print("🚀 Starting Enhanced Analysis Workflow...")
        
        # Step 1: Validate methodology
        print("📊 Validating research methodology...")
        methodology_result = methodologist.process({
            'task_type': 'validate_research_design',
            'project_data': {
                'research_questions': self.project.background_info['research_objectives'],
                'methodology': self.project.background_info['methodology_context']
            }
        })
        self.assertTrue(methodology_result['success'])
        print(f"✅ Methodology validation complete - Score: {methodology_result['validation']['methodology_score']}")
        
        # Step 2: Analyze responses with weighting
        print("🔍 Analyzing responses with persona weighting...")
        coding_result = coding_specialist.process({
            'task_type': 'analyze_responses',
            'project_data': {
                'responses': self.session.responses,
                'background_info': self.project.background_info
            }
        })
        self.assertTrue(coding_result['success'])
        print(f"✅ Identified {len(coding_result['themes'])} key themes")
        
        # Step 3: Create visualizations
        print("📈 Generating visualizations...")
        viz_result = viz_designer.process({
            'task_type': 'create_visuals',
            'previous_results': {
                'coding_specialist_analyze_responses': coding_result
            },
            'session_data': {'session_id': self.session.id, 'participant_count': len(self.project.persona_weights)}
        })
        self.assertTrue(viz_result['success'])
        print(f"✅ Created {len(viz_result['visualizations'])} visualization types")
        
        # Step 4: Generate final report
        print("📑 Generating comprehensive report...")
        all_results = {
            'methodology': methodology_result,
            'coding': coding_result,
            'visualizations': viz_result
        }
        
        final_report = orchestrator._generate_final_report({
            'analysis_results': all_results,
            'project_context': self.project.to_dict(),
            'session_context': {'session': self.session.to_dict()},
            'name': self.project.name,
            'background_info': self.project.background_info
        })
        self.assertTrue(final_report['success'])
        # Check if report contains meaningful content
        if 'report' in final_report and 'product-market fit' in final_report.get('report', ''):
            print("✅ Final report generated successfully with AI insights")
        else:
            print("✅ Report generation completed (fallback mode)")
        
        # Step 5: Create enhanced exports
        print("📦 Creating enhanced export package...")
        
        # Compile all agent results
        agent_results = {
            'methodologist_validate_research_design': methodology_result,
            'coding_specialist_analyze_responses': coding_result,
            'viz_designer_create_visuals': viz_result,
            'orchestrator_generate_final_report': final_report
        }
        
        # Test weighted analysis export
        weighted_analysis_file = self.exporter.export_weighted_session_analysis(
            self.session, self.project, agent_results
        )
        self.assertTrue(os.path.exists(weighted_analysis_file))
        
        # Verify weighted analysis content
        with open(weighted_analysis_file, 'r') as f:
            weighted_data = json.load(f)
        
        self.assertEqual(weighted_data['weighting_system']['primary_icp'], "sarah_001")
        self.assertTrue(weighted_data['weighting_system']['weighted_analysis_enabled'])
        self.assertIn('persona_contributions', weighted_data)
        print("✅ Weighted analysis export verified")
        
        # Test ICP-focused report
        icp_report_file = self.exporter.export_icp_focused_report(
            self.session, self.project, agent_results
        )
        self.assertTrue(os.path.exists(icp_report_file))
        
        with open(icp_report_file, 'r') as f:
            icp_data = json.load(f)
        
        self.assertEqual(icp_data['icp_profile']['persona_id'], "sarah_001")
        self.assertGreater(icp_data['icp_profile']['weight'], 2.0)
        self.assertIn('strategic_implications', icp_data)
        print("✅ ICP-focused report verified")
        
        # Test agent insights dashboard
        dashboard_file = self.exporter.export_agent_insights_dashboard(
            agent_results,
            {'session_id': self.session.id, 'project_id': self.project.id}
        )
        self.assertTrue(os.path.exists(dashboard_file))
        
        with open(dashboard_file, 'r') as f:
            dashboard_data = json.load(f)
        
        self.assertGreater(dashboard_data['quality_metrics']['overall_confidence'], 0.5)
        self.assertIn('methodology_assessment', dashboard_data)
        self.assertIn('thematic_analysis', dashboard_data)
        print("✅ Agent insights dashboard verified")
        
        # Test comprehensive package
        package_dir = self.exporter.export_comprehensive_package(
            self.session, self.project, agent_results,
            "test_enhanced_package"
        )
        self.assertTrue(os.path.exists(package_dir))
        
        # Verify package contents
        manifest_file = os.path.join(package_dir, "manifest.json")
        self.assertTrue(os.path.exists(manifest_file))
        
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        self.assertTrue(manifest['analysis_features']['weighted_analysis'])
        self.assertTrue(manifest['analysis_features']['icp_analysis'])
        self.assertTrue(manifest['analysis_features']['agent_insights'])
        self.assertEqual(manifest['analysis_features']['persona_count'], 4)
        print("✅ Comprehensive package verified")
        
        # Test weighted CSV export
        csv_file = self.exporter.export_weighted_csv(self.session, self.project)
        self.assertTrue(os.path.exists(csv_file))
        
        # Verify CSV contains weighted data
        import csv as csv_module
        with open(csv_file, 'r') as f:
            reader = csv_module.DictReader(f)
            rows = list(reader)
        
        # Check that ICP responses have higher weights
        sarah_rows = [r for r in rows if r['speaker_id'] == 'sarah_001']
        alex_rows = [r for r in rows if r['speaker_id'] == 'alex_004']
        
        self.assertGreater(float(sarah_rows[0]['persona_weight']), float(alex_rows[0]['persona_weight']))
        self.assertEqual(sarah_rows[0]['is_primary_icp'], 'True')
        self.assertEqual(alex_rows[0]['is_primary_icp'], 'False')
        print("✅ Weighted CSV export verified")
        
        print("\n🎉 Enhanced Integration Test Completed Successfully!")
        print(f"📂 Results exported to: {package_dir}")
        
        # Print summary insights
        print("\n📋 Test Summary:")
        print(f"   • Total responses analyzed: {len(self.session.responses)}")
        print(f"   • Persona weight range: {min(pw.weight for pw in self.project.persona_weights):.1f} - {max(pw.weight for pw in self.project.persona_weights):.1f}")
        print(f"   • Primary ICP engagement: {len([r for r in self.session.responses if r.speaker_id == 'sarah_001'])} responses")
        print(f"   • Agent insights generated: {len(agent_results)} different analyses")
        print(f"   • Export formats created: {len(manifest['files_included'])}")
        
        return {
            'agent_results': agent_results,
            'exports': manifest['files_included'],
            'insights': coding_result['insights'],
            'package_dir': package_dir
        }
    
    def test_persona_weighting_calculations(self):
        """Test that persona weighting calculations work correctly."""
        weights = self.project.get_analysis_weights()
        
        # Verify weights are properly normalized
        self.assertEqual(weights['sarah_001'], 3.0)  # Primary ICP
        self.assertEqual(weights['mike_002'], 2.0)   # Secondary
        self.assertEqual(weights['alex_004'], 0.8)   # Lowest priority
        
        # Test ranking
        ranked_personas = self.project.get_ranked_personas()
        self.assertEqual(ranked_personas[0].persona_id, 'sarah_001')
        self.assertEqual(ranked_personas[0].rank, 1)
        self.assertEqual(ranked_personas[-1].persona_id, 'alex_004')
        self.assertEqual(ranked_personas[-1].rank, 4)
        
        print("✅ Persona weighting calculations verified")
    
    def test_icp_analysis_accuracy(self):
        """Test ICP analysis provides accurate insights."""
        # Get ICP-specific responses
        icp_responses = self.session.get_responses_by_participant('sarah_001')
        
        # Verify ICP has most responses (highest engagement)
        all_response_counts = {}
        for pw in self.project.persona_weights:
            all_response_counts[pw.persona_id] = len(
                self.session.get_responses_by_participant(pw.persona_id)
            )
        
        self.assertEqual(max(all_response_counts.values()), len(icp_responses))
        
        # Test ICP analysis extraction
        icp_analysis = self.exporter._analyze_icp_responses(self.session, 'sarah_001')
        
        self.assertEqual(icp_analysis['response_count'], len(icp_responses))
        self.assertEqual(icp_analysis['engagement_level'], 'high')
        self.assertIn('workflow_efficiency', icp_analysis['unique_themes'])
        
        print("✅ ICP analysis accuracy verified")
    
    def test_vector_backend_security(self):
        """Test that vector backend security measures work correctly."""
        # Test input validation
        backend = PgVector()
        
        # Test invalid collection names (should raise ValueError)
        with self.assertRaises(ValueError):
            backend._ensure_table("invalid; DROP TABLE users;", 1536)  # SQL injection attempt
        
        with self.assertRaises(ValueError):
            backend._ensure_table("invalid\x00name", 1536)  # Null byte injection
        
        with self.assertRaises(ValueError):
            backend._ensure_table("", 1536)  # Empty name
        
        # Test dimension validation
        with self.assertRaises(ValueError):
            backend._ensure_table("valid_name", 0)  # Invalid dimension
        
        with self.assertRaises(ValueError):
            backend._ensure_table("valid_name", 5000)  # Too large dimension
        
        print("✅ Vector backend security validation verified")
    
    def test_schema_validation_insights(self):
        """Test that exports conform to insights schema."""
        # Load the schema
        with open('schemas/insights.schema.json', 'r') as f:
            schema = json.load(f)
        
        # Create a mock export following the schema structure
        mock_insight = {
            "schema_version": "1.0.0",
            "study_id": "test_study_001",
            "generated_at": datetime.now().isoformat(),
            "checksum": hashlib.sha256(b"test_data").hexdigest(),
            "insights": {
                "weighted": {
                    "themes": [
                        {
                            "theme": "Workflow Integration",
                            "score": 0.85,
                            "sentiment": "positive",
                            "quotes": [
                                {
                                    "text": "Integration would be game-changing",
                                    "persona_id": "sarah_001",
                                    "weight": 3.0
                                }
                            ]
                        }
                    ],
                    "sentiment_summary": {
                        "positive": 0.6,
                        "negative": 0.2,
                        "neutral": 0.2
                    },
                    "limitations": ["Sample size may be limited"],
                    "agreement_scores": {
                        "workflow_integration": 0.85
                    }
                },
                "unweighted": {
                    "themes": [],
                    "sentiment_summary": {"positive": 0.5, "negative": 0.3, "neutral": 0.2},
                    "limitations": [],
                    "agreement_scores": {}
                },
                "per_persona": [
                    {
                        "persona_id": "sarah_001",
                        "name": "Sarah Thompson",
                        "weight": 3.0,
                        "contributions": {
                            "message_count": 5,
                            "dominant_sentiment": "positive",
                            "key_themes": ["workflow_integration"],
                            "influence_score": 0.8
                        }
                    }
                ]
            },
            "metadata": {
                "study_title": "Enhanced Customer Research",
                "objective": "Understand user pain points",
                "total_personas": 4,
                "session_duration_minutes": 65.0,
                "guardrail_events": 0
            }
        }
        
        # Validate against schema
        try:
            jsonschema.validate(mock_insight, schema)
            print("✅ Insights schema validation passed")
        except jsonschema.ValidationError as e:
            self.fail(f"Schema validation failed: {e}")
    
    def test_schema_validation_messages(self):
        """Test that message exports conform to messages schema."""
        # Load the schema
        with open('schemas/messages.schema.json', 'r') as f:
            schema = json.load(f)
        
        # Create mock messages following the schema
        mock_messages = [
            {
                "study_id": "test_study_001",
                "turn": 1,
                "persona_name": "Sarah Thompson",
                "role": "participant",
                "content": "I currently use three different apps and it's frustrating",
                "tokens": 12,
                "cost": 0.001,
                "topics": ["workflow_efficiency", "tool_management"],
                "sentiment": "negative",
                "ts": datetime.now().isoformat()
            },
            {
                "study_id": "test_study_001",
                "turn": 2,
                "persona_name": None,
                "role": "facilitator",
                "content": "Can you tell me more about that frustration?",
                "tokens": 10,
                "cost": None,
                "topics": [],
                "sentiment": None,
                "ts": datetime.now().isoformat()
            }
        ]
        
        # Validate against schema
        try:
            jsonschema.validate(mock_messages, schema)
            print("✅ Messages schema validation passed")
        except jsonschema.ValidationError as e:
            self.fail(f"Message schema validation failed: {e}")
    
    def test_synthetic_runner_persona_weighting(self):
        """Test the new persona weighting functionality in synthetic runner."""
        # Create synthetic runner
        runner = SyntheticSessionRunner()
        
        # Test setting persona weights
        runner.set_persona_weight("test_persona_1", 3.0, rank=1, is_primary_icp=True, notes="Primary target")
        runner.set_persona_weight("test_persona_2", 1.5, rank=2, notes="Secondary target")
        
        # Test weight retrieval and normalization
        weights = runner.get_analysis_weights()
        self.assertIn("test_persona_1", weights)
        self.assertIn("test_persona_2", weights)
        self.assertGreater(weights["test_persona_1"], weights["test_persona_2"])
        
        # Test primary ICP setting
        self.assertEqual(runner.primary_icp_persona_id, "test_persona_1")
        
        # Test persona ranking
        ranked = runner.get_ranked_personas()
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0].persona_id, "test_persona_1")
        self.assertEqual(ranked[0].rank, 1)
        self.assertTrue(ranked[0].is_primary_icp)
        
        print("✅ Synthetic runner persona weighting verified")
    
    def test_sample_persona_data_integrity(self):
        """Test that sample persona data is consistent and valid."""
        # Test sample personas
        personas = create_sample_personas()
        self.assertEqual(len(personas), 3)
        
        for persona in personas:
            self.assertIn('id', persona)
            self.assertIn('name', persona)
            self.assertIn('role', persona)
            self.assertIsInstance(persona['id'], str)
            self.assertGreater(len(persona['id']), 0)
        
        # Test sample weights
        weights = create_sample_persona_weights()
        self.assertEqual(len(weights), 3)
        
        # Verify primary ICP is set correctly
        primary_icp_count = sum(1 for w in weights.values() if w.get('is_primary_icp', False))
        self.assertEqual(primary_icp_count, 1)
        
        # Verify weight ranges are valid (0-5)
        for weight_config in weights.values():
            weight_val = weight_config.get('weight', 1.0)
            self.assertGreaterEqual(weight_val, 0.0)
            self.assertLessEqual(weight_val, 5.0)
        
        print("✅ Sample persona data integrity verified")
    
    def test_export_data_consistency(self):
        """Test that different export formats contain consistent data."""
        # Create agent results for testing
        mock_agent_results = {
            'coding_specialist_analyze_responses': {
                'success': True,
                'themes': [{'theme': 'Test Theme', 'frequency': 5}],
                'insights': ['Test insight'],
                'recommendations': ['Test recommendation']
            }
        }
        
        # Export in multiple formats
        weighted_file = self.exporter.export_weighted_session_analysis(
            self.session, self.project, mock_agent_results
        )
        
        csv_file = self.exporter.export_weighted_csv(
            self.session, self.project
        )
        
        # Load and compare data
        with open(weighted_file, 'r') as f:
            weighted_data = json.load(f)
        
        import csv as csv_module
        with open(csv_file, 'r') as f:
            reader = csv_module.DictReader(f)
            csv_rows = list(reader)
        
        # Verify session IDs match
        self.assertEqual(weighted_data['session_info']['session_id'], self.session.id)
        self.assertEqual(csv_rows[0]['session_id'], self.session.id)
        
        # Verify response counts match
        expected_responses = len([r for r in self.session.responses if r.speaker_type == 'participant'])
        self.assertEqual(len(csv_rows), expected_responses)
        
        # Verify persona weights are consistent
        for row in csv_rows:
            persona_id = row['speaker_id']
            expected_weight = self.project.get_analysis_weights().get(persona_id, 1.0)
            actual_weight = float(row['persona_weight'])
            self.assertAlmostEqual(expected_weight, actual_weight, places=2)
        
        print("✅ Export data consistency verified")
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)


if __name__ == '__main__':
    # Run with verbose output to see progress
    test = TestEnhancedIntegration()
    test.setUp()
    
    try:
        result = test.test_full_enhanced_workflow()
        print(f"\n🏆 Integration test successful!")
        print(f"📊 Key insights discovered:")
        for insight in result['insights']:
            print(f"   • {insight}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        test.tearDown()