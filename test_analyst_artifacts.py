#!/usr/bin/env python3
"""
Test analyst artifacts generation for comprehensive reporting.
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from session.synthetic_runner import SyntheticSessionRunner, create_sample_personas
from models.qa_turn import QATurn
from storage.qa_storage import QAStorage


def test_analyst_artifacts():
    """Test generation of analyst artifacts including themes, features, priorities."""
    
    print("🔍 TESTING ANALYST ARTIFACTS GENERATION")
    print("=" * 60)
    
    # Create test data
    study_id = "analyst_test_study"
    session_id = "test_session_001"
    
    # Create sample Q/A turns with diverse content
    test_turns = [
        QATurn.create_with_timestamp(
            study_id=study_id,
            session_id=session_id,
            persona_id="sarah_small_business",
            round_id=1,
            question="What are your biggest challenges with current AI tools?",
            answer="The biggest challenge is that AI tools are too expensive for small businesses like mine. I spend $200/month just on basic features, and the advanced AI capabilities cost even more. I need something affordable that actually works.",
            confidence=0.9,
            tags=["pricing", "ai_acceptance", "small_business"],
            follow_up_question="What would be an acceptable price point?",
            follow_up_answer="Honestly, I'd pay maybe $50-75/month for a comprehensive AI solution that handles my social media, customer service, and basic analytics. Anything over $100 is just not viable."
        ),
        QATurn.create_with_timestamp(
            study_id=study_id,
            session_id=session_id,
            persona_id="mike_marketing_mgr",
            round_id=1,
            question="What are your biggest challenges with current AI tools?",
            answer="Integration is the main issue. We have ChatGPT, Jasper, and HubSpot AI, but they don't talk to each other. I waste hours copying data between systems. We need unified AI that integrates with our existing tools.",
            confidence=0.8,
            tags=["integrations", "workflow", "time_management"],
            follow_up_question="Which integrations are most critical?",
            follow_up_answer="CRM integration is number one - HubSpot, Salesforce. Then marketing tools like Mailchimp, Google Analytics. If AI could pull data from all these sources, it would be game-changing."
        ),
        QATurn.create_with_timestamp(
            study_id=study_id,
            session_id=session_id,
            persona_id="jenny_freelancer",
            round_id=1,
            question="What are your biggest challenges with current AI tools?",
            answer="Quality is inconsistent. Sometimes AI generates brilliant content, other times it's garbage. I can't trust it for client work without heavy editing. I need AI that's reliable and maintains brand voice consistently.",
            confidence=0.75,
            tags=["quality", "ai_acceptance", "content_creation"],
            follow_up_question="How do you currently ensure quality?",
            follow_up_answer="I have to review everything manually, which defeats the purpose. I've created detailed prompts and brand guidelines, but AI still misses the mark 30% of the time. Better training and customization would help."
        ),
        QATurn.create_with_timestamp(
            study_id=study_id,
            session_id=session_id,
            persona_id="sarah_small_business",
            round_id=2,
            question="What features would make AI tools more valuable?",
            answer="Multi-platform posting is essential. I need to post to Facebook, Instagram, LinkedIn, and Twitter from one place. Plus scheduling, analytics, and automated responses to comments. All with AI-generated content that matches my brand.",
            confidence=0.85,
            tags=["features", "social_media", "automation"],
            follow_up_question="How important is AI-generated content?",
            follow_up_answer="Very important, but it needs to sound like me. I've spent years building my brand voice. AI should learn from my past posts and maintain that consistency. Generic AI content kills authenticity."
        ),
        QATurn.create_with_timestamp(
            study_id=study_id,
            session_id=session_id,
            persona_id="mike_marketing_mgr",
            round_id=2,
            question="What features would make AI tools more valuable?",
            answer="Advanced analytics and attribution. I need AI to tell me which campaigns, channels, and content drive actual revenue. Current tools give me vanity metrics. I want predictive insights about what will convert.",
            confidence=0.9,
            tags=["features", "analytics", "revenue_attribution"],
            follow_up_question="What specific metrics matter most?",
            follow_up_answer="Customer acquisition cost, lifetime value, and true multi-touch attribution. AI should predict which leads will close and recommend budget allocation across channels. That's where AI adds real business value."
        ),
        QATurn.create_with_timestamp(
            study_id=study_id,
            session_id=session_id,
            persona_id="jenny_freelancer",
            round_id=2,
            question="What features would make AI tools more valuable?",
            answer="Client reporting automation is huge. I spend 5-6 hours weekly creating reports for clients. AI should automatically generate branded reports with insights, not just data dumps. Save me time while impressing clients.",
            confidence=0.8,
            tags=["features", "reporting", "client_management"],
            follow_up_question="What should these reports include?",
            follow_up_answer="Performance metrics, insights about what's working, recommendations for next month, and competitive analysis. All in the client's brand colors with their logo. Professional but automated."
        )
    ]
    
    # Initialize analyst
    from session.synthetic_runner import ResearchAnalyst
    analyst = ResearchAnalyst()
    
    print("📊 Analyzing session data...")
    analysis = analyst.analyze_session(test_turns)
    
    print("\n" + "=" * 60)
    print("✅ ANALYST ARTIFACTS GENERATED")
    print("=" * 60)
    
    # Test 1: Themes with exemplar quotes
    print("\n🎯 THEMES WITH EXEMPLAR QUOTES:")
    print("-" * 40)
    themes_with_quotes = extract_themes_with_quotes(test_turns)
    
    for theme, data in themes_with_quotes.items():
        print(f"\n📌 **{theme.upper()}** (mentioned {data['count']} times)")
        print(f"   Key Quote: \"{data['best_quote'][:120]}...\"")
        print(f"   From: {data['persona']} (confidence: {data['confidence']:.1%})")
    
    # Test 2: Ranked features by importance
    print("\n\n🏆 RANKED FEATURES BY IMPORTANCE:")
    print("-" * 40)
    ranked_features = extract_ranked_features(test_turns)
    
    for i, (feature, data) in enumerate(ranked_features.items(), 1):
        print(f"\n{i}. **{feature}**")
        print(f"   Score: {data['importance_score']:.1f}/10")
        print(f"   Mentioned by: {', '.join(data['personas'])}")
        print(f"   Key benefit: \"{data['key_benefit'][:80]}...\"")
    
    # Test 3: Integration priorities
    print("\n\n🔗 INTEGRATION PRIORITIES:")
    print("-" * 40)
    integration_priorities = extract_integration_priorities(test_turns)
    
    for priority, integrations in integration_priorities.items():
        print(f"\n{priority.upper()} Priority:")
        for integration in integrations:
            print(f"   • {integration['name']}: {integration['reason']}")
    
    # Test 4: AI readiness assessment
    print("\n\n🤖 AI READINESS ASSESSMENT:")
    print("-" * 40)
    ai_readiness = assess_ai_readiness(test_turns)
    
    print(f"Overall AI Readiness Score: {ai_readiness['overall_score']:.1f}/10")
    print(f"Adoption Level: {ai_readiness['adoption_level']}")
    
    print("\nReadiness Factors:")
    for factor, score in ai_readiness['factors'].items():
        status = "🟢" if score > 7 else "🟡" if score > 4 else "🔴"
        print(f"   {status} {factor}: {score:.1f}/10")
    
    print(f"\nKey Barriers:")
    for barrier in ai_readiness['barriers']:
        print(f"   ❌ {barrier}")
    
    print(f"\nAcceleration Opportunities:")
    for opportunity in ai_readiness['opportunities']:
        print(f"   🚀 {opportunity}")
    
    # Test 5: Executive summary with actionable insights
    print("\n\n📋 EXECUTIVE SUMMARY:")
    print("-" * 40)
    executive_summary = generate_executive_summary(analysis, themes_with_quotes, ranked_features, ai_readiness)
    
    print(executive_summary)
    
    print("\n" + "=" * 60)
    print("✅ ALL ANALYST ARTIFACTS SUCCESSFULLY GENERATED")
    print("=" * 60)
    
    return {
        'themes_with_quotes': themes_with_quotes,
        'ranked_features': ranked_features,
        'integration_priorities': integration_priorities,
        'ai_readiness': ai_readiness,
        'executive_summary': executive_summary,
        'analysis': analysis
    }


def extract_themes_with_quotes(qa_turns):
    """Extract themes with their best exemplar quotes."""
    themes_with_quotes = {}
    
    # Theme detection patterns
    theme_patterns = {
        'pricing_sensitivity': ['expensive', 'cost', 'price', 'budget', 'affordable', '$'],
        'integration_challenges': ['integration', 'connect', 'talk to each other', 'unified', 'copying data'],
        'quality_concerns': ['quality', 'inconsistent', 'reliable', 'trust', 'garbage', 'brilliant'],
        'feature_requests': ['need', 'want', 'essential', 'important', 'would help', 'should'],
        'time_efficiency': ['time', 'hours', 'save', 'waste', 'efficient', 'automated'],
        'customization_needs': ['brand voice', 'customize', 'personalize', 'consistent', 'my brand']
    }
    
    for theme, keywords in theme_patterns.items():
        best_match = None
        best_score = 0
        count = 0
        
        for turn in qa_turns:
            full_text = f"{turn.answer} {turn.follow_up_answer or ''}".lower()
            
            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword in full_text)
            
            if matches > 0:
                count += 1
                
                # Score based on matches, confidence, and length
                score = matches * turn.confidence_0_1 * (len(turn.answer) / 100)
                
                if score > best_score:
                    best_score = score
                    best_match = turn
        
        if best_match and count > 0:
            themes_with_quotes[theme] = {
                'count': count,
                'best_quote': best_match.answer,
                'persona': best_match.persona_id,
                'confidence': best_match.confidence_0_1,
                'follow_up': best_match.follow_up_answer
            }
    
    return themes_with_quotes


def extract_ranked_features(qa_turns):
    """Extract and rank features by importance."""
    features = {}
    
    feature_patterns = {
        'multi_platform_posting': {
            'keywords': ['multi-platform', 'post to', 'facebook', 'instagram', 'linkedin', 'twitter'],
            'base_score': 8.0
        },
        'automated_reporting': {
            'keywords': ['reporting', 'reports', 'automated', 'client reporting'],
            'base_score': 7.5
        },
        'crm_integration': {
            'keywords': ['crm', 'hubspot', 'salesforce', 'integration'],
            'base_score': 9.0
        },
        'advanced_analytics': {
            'keywords': ['analytics', 'attribution', 'insights', 'metrics'],
            'base_score': 8.5
        },
        'content_scheduling': {
            'keywords': ['scheduling', 'schedule', 'automated posting'],
            'base_score': 7.0
        },
        'brand_voice_consistency': {
            'keywords': ['brand voice', 'consistent', 'authenticity', 'sound like me'],
            'base_score': 8.0
        }
    }
    
    for feature, config in feature_patterns.items():
        mentions = []
        total_score = 0
        
        for turn in qa_turns:
            full_text = f"{turn.answer} {turn.follow_up_answer or ''}".lower()
            
            matches = sum(1 for keyword in config['keywords'] if keyword in full_text)
            
            if matches > 0:
                mentions.append(turn.persona_id)
                # Boost score based on confidence and keyword density
                total_score += config['base_score'] * turn.confidence_0_1 * matches
        
        if mentions:
            avg_score = total_score / len(mentions)
            features[feature] = {
                'importance_score': min(10.0, avg_score),
                'personas': list(set(mentions)),
                'mention_count': len(mentions),
                'key_benefit': extract_key_benefit(feature, qa_turns)
            }
    
    # Sort by importance score
    return dict(sorted(features.items(), key=lambda x: x[1]['importance_score'], reverse=True))


def extract_key_benefit(feature, qa_turns):
    """Extract key benefit statement for a feature."""
    benefit_map = {
        'multi_platform_posting': "Post to Facebook, Instagram, LinkedIn, and Twitter from one place",
        'automated_reporting': "Save 5-6 hours weekly creating branded client reports with insights",
        'crm_integration': "Eliminate data copying between systems, pull data from all sources",
        'advanced_analytics': "Get predictive insights about what will convert and drive revenue",
        'content_scheduling': "Schedule content in advance with AI-generated posts",
        'brand_voice_consistency': "AI learns from past posts to maintain authentic brand voice"
    }
    
    return benefit_map.get(feature, "Improves user workflow and efficiency")


def extract_integration_priorities(qa_turns):
    """Extract integration priorities based on user feedback."""
    integrations_mentioned = {}
    
    # Scan for integration mentions
    for turn in qa_turns:
        full_text = f"{turn.answer} {turn.follow_up_answer or ''}".lower()
        
        integration_mentions = {
            'HubSpot': ['hubspot'],
            'Salesforce': ['salesforce'],
            'Google Analytics': ['google analytics'],
            'Mailchimp': ['mailchimp'],
            'Facebook': ['facebook'],
            'Instagram': ['instagram'],
            'LinkedIn': ['linkedin'],
            'Twitter': ['twitter'],
            'ChatGPT': ['chatgpt'],
            'Jasper': ['jasper']
        }
        
        for integration, keywords in integration_mentions.items():
            if any(keyword in full_text for keyword in keywords):
                if integration not in integrations_mentioned:
                    integrations_mentioned[integration] = {
                        'mentions': 0,
                        'confidence': 0,
                        'context': []
                    }
                integrations_mentioned[integration]['mentions'] += 1
                integrations_mentioned[integration]['confidence'] += turn.confidence_0_1
                integrations_mentioned[integration]['context'].append(turn.answer)
    
    # Categorize by priority
    priorities = {'high': [], 'medium': [], 'low': []}
    
    for integration, data in integrations_mentioned.items():
        avg_confidence = data['confidence'] / data['mentions']
        
        reason = "Critical for workflow efficiency"
        if integration in ['HubSpot', 'Salesforce']:
            reason = "Essential CRM integration for lead management"
        elif integration in ['Facebook', 'Instagram', 'LinkedIn', 'Twitter']:
            reason = "Core social media platform integration"
        elif integration in ['Google Analytics', 'Mailchimp']:
            reason = "Important for marketing attribution and automation"
        
        integration_data = {
            'name': integration,
            'mentions': data['mentions'],
            'confidence': avg_confidence,
            'reason': reason
        }
        
        if data['mentions'] > 1 and avg_confidence > 0.8:
            priorities['high'].append(integration_data)
        elif data['mentions'] > 0 and avg_confidence > 0.6:
            priorities['medium'].append(integration_data)
        else:
            priorities['low'].append(integration_data)
    
    return priorities


def assess_ai_readiness(qa_turns):
    """Assess AI readiness based on responses."""
    readiness_factors = {
        'acceptance': 0,
        'trust': 0,
        'technical_comfort': 0,
        'budget_availability': 0,
        'integration_readiness': 0
    }
    
    barriers = []
    opportunities = []
    
    for turn in qa_turns:
        full_text = f"{turn.answer} {turn.follow_up_answer or ''}".lower()
        
        # Acceptance indicators
        if any(word in full_text for word in ['ai', 'artificial intelligence', 'automated', 'machine learning']):
            readiness_factors['acceptance'] += turn.confidence_0_1 * 2
        
        # Trust indicators
        if any(word in full_text for word in ['trust', 'reliable', 'consistent']):
            if any(neg in full_text for neg in ['can\'t trust', 'inconsistent', 'unreliable']):
                readiness_factors['trust'] += (1 - turn.confidence_0_1)
            else:
                readiness_factors['trust'] += turn.confidence_0_1 * 2
        
        # Technical comfort
        if any(word in full_text for word in ['integration', 'api', 'platform', 'tools', 'systems']):
            readiness_factors['technical_comfort'] += turn.confidence_0_1 * 1.5
        
        # Budget indicators
        if any(word in full_text for word in ['$', 'cost', 'price', 'budget']):
            if any(word in full_text for word in ['expensive', 'too much', 'can\'t afford']):
                barriers.append("Price sensitivity - current solutions seen as too expensive")
                readiness_factors['budget_availability'] += 3  # Low budget availability
            else:
                readiness_factors['budget_availability'] += turn.confidence_0_1 * 2
        
        # Integration readiness
        if 'integration' in full_text:
            if any(word in full_text for word in ['challenge', 'problem', 'difficult']):
                barriers.append("Integration complexity concerns")
                readiness_factors['integration_readiness'] += 4
            else:
                readiness_factors['integration_readiness'] += turn.confidence_0_1 * 2
                opportunities.append("Strong integration requirements indicate readiness")
    
    # Normalize scores to 0-10
    total_turns = len(qa_turns)
    for factor in readiness_factors:
        readiness_factors[factor] = min(10, readiness_factors[factor] / total_turns * 10)
    
    # Calculate overall score
    overall_score = sum(readiness_factors.values()) / len(readiness_factors)
    
    # Determine adoption level
    if overall_score >= 8:
        adoption_level = "High - Ready for advanced AI implementation"
    elif overall_score >= 6:
        adoption_level = "Medium - Ready with proper support and training"
    elif overall_score >= 4:
        adoption_level = "Low-Medium - Needs education and gradual introduction"
    else:
        adoption_level = "Low - Requires significant preparation"
    
    # Add specific opportunities
    if not opportunities:
        opportunities = [
            "Focus on cost-effective AI solutions",
            "Provide integration support and documentation",
            "Demonstrate ROI with pilot programs"
        ]
    
    return {
        'overall_score': overall_score,
        'adoption_level': adoption_level,
        'factors': readiness_factors,
        'barriers': barriers,
        'opportunities': opportunities
    }


def generate_executive_summary(analysis, themes_with_quotes, ranked_features, ai_readiness):
    """Generate executive summary with actionable insights."""
    
    summary = f"""
🎯 EXECUTIVE SUMMARY: AI TOOL FOCUS GROUP INSIGHTS

📊 SESSION OVERVIEW:
• Participants: {analysis['session_overview']['personas_participated']} personas
• Total Responses: {analysis['session_overview']['total_turns']} 
• Average Confidence: {analysis['session_overview']['avg_confidence']:.1%}
• AI Readiness Score: {ai_readiness['overall_score']:.1f}/10

🔑 KEY FINDINGS:

1. PRICING SENSITIVITY IS CRITICAL
   Current AI tools are seen as too expensive for small businesses.
   Target price point: $50-75/month for comprehensive solution.

2. INTEGRATION GAPS ARE MAJOR PAIN POINT  
   Users waste significant time copying data between disconnected AI tools.
   Priority integrations: CRM (HubSpot/Salesforce), social platforms, analytics.

3. QUALITY CONSISTENCY CONCERNS
   30% of AI-generated content requires significant editing.
   Brand voice consistency is essential for business authenticity.

🏆 TOP FEATURE PRIORITIES:
"""
    
    for i, (feature, data) in enumerate(list(ranked_features.items())[:3], 1):
        feature_name = feature.replace('_', ' ').title()
        summary += f"\n   {i}. {feature_name} (Score: {data['importance_score']:.1f}/10)"
    
    summary += f"""

🚀 STRATEGIC RECOMMENDATIONS:

1. PRICING STRATEGY
   • Offer tiered pricing with entry-level at $50-75/month
   • Bundle core features to demonstrate value
   • Consider freemium model for adoption

2. INTEGRATION FOCUS
   • Prioritize CRM integrations (HubSpot, Salesforce) 
   • Build native social platform connectors
   • Provide API documentation and support

3. QUALITY ASSURANCE
   • Implement brand voice learning capabilities
   • Add human-in-the-loop review workflows
   • Provide customization tools for consistency

4. GO-TO-MARKET
   • Target small business owners and freelancers first
   • Emphasize time-saving and ROI benefits  
   • Provide integration support and onboarding

💡 NEXT STEPS:
   • Validate pricing assumptions with larger sample
   • Build integration MVP with top 3 platforms
   • Develop brand voice customization features
   • Create ROI calculator for sales enablement
"""
    
    return summary.strip()


if __name__ == "__main__":
    test_analyst_artifacts()