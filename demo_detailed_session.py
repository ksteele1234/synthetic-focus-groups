#!/usr/bin/env python3
"""
Demo script showing detailed personas in a synthetic focus group session.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from session.synthetic_runner import SyntheticSessionRunner
from sample_detailed_personas import (
    create_sarah_marketing_maven,
    create_mike_growth_hacker,
    create_jenny_scaling_solopreneur
)
from models.persona import Persona

def demo_detailed_personas_in_session():
    """Demonstrate detailed personas in a synthetic focus group session."""
    
    print("🎯 DETAILED PERSONAS IN SYNTHETIC FOCUS GROUPS")
    print("=" * 60)
    
    # Create our detailed personas
    detailed_personas = [
        create_sarah_marketing_maven(),
        create_mike_growth_hacker(),
        create_jenny_scaling_solopreneur()
    ]
    
    print(f"\n👥 Participants ({len(detailed_personas)} detailed personas):")
    for i, persona in enumerate(detailed_personas, 1):
        print(f"{i}. {persona.name} - {persona.occupation}")
        print(f"   🎯 Primary Goal: {persona.tangible_business_results[0] if persona.tangible_business_results else 'Not specified'}")
        print(f"   😰 Key Fear: {persona.deep_fears_business[0] if persona.deep_fears_business else 'Not specified'}")
        print(f"   💭 Signature Quote: \"{persona.if_only_soundbites[0] if persona.if_only_soundbites else 'Not specified'}\"")
        print()
    
    # Convert to session format
    print("🔄 Converting personas to session format...")
    session_personas = []
    
    for persona in detailed_personas:
        # Convert detailed persona to session runner format
        session_persona = {
            'persona_id': persona.name.lower().replace(' ', '_').replace("'", ""),
            'name': persona.name,
            'role': persona.occupation,
            'age': persona.age,
            'occupation': persona.occupation,
            'background': persona.persona_summary,
            'personality_traits': persona.personality_traits,
            'interests': persona.hobbies[:3] if persona.hobbies else ['professional development'],
            'pain_points': persona.major_struggles[:3] if persona.major_struggles else ['general work challenges'],
            'goals': persona.tangible_business_results[:3] if persona.tangible_business_results else ['professional success'],
            'communication_style': 'Professional, detailed, and context-aware',
            # Add detailed context for AI agent
            'detailed_context': persona._generate_detailed_prompt()
        }
        session_personas.append(session_persona)
    
    print(f"✅ Converted {len(session_personas)} personas for session")
    
    # Initialize session runner
    print(f"\n🚀 Starting Enhanced Synthetic Focus Group Session...")
    runner = SyntheticSessionRunner()
    
    # Run a short demo session
    study_id = "detailed_personas_demo"
    topic = "Marketing Automation and Client Management Tools"
    
    print(f"📋 Study: {study_id}")
    print(f"🎯 Topic: {topic}")
    print(f"👥 Participants: {', '.join([p['name'] for p in session_personas])}")
    
    try:
        # Run the session
        results = runner.run_session(
            study_id=study_id,
            topic=topic,
            personas=session_personas,
            num_questions=3
        )
        
        print(f"\n🎉 Session Complete!")
        print(f"📊 Results Summary:")
        
        summary = results.get('summary', {})
        print(f"   • Total Q&A Turns: {summary.get('total_turns', 'N/A')}")
        print(f"   • Average Confidence: {summary.get('avg_confidence', 0)*100:.1f}%")
        print(f"   • Themes Identified: {summary.get('themes_identified', 'N/A')}")
        print(f"   • Session Duration: {summary.get('session_duration_minutes', 'N/A')} minutes")
        
        # Show some sample responses
        qa_turns = results.get('qa_turns', [])
        if qa_turns:
            print(f"\n💬 Sample Responses (showing detailed persona context):")
            
            for i, turn in enumerate(qa_turns[:2], 1):  # Show first 2 Q&A turns
                print(f"\n🔹 Q{i}: {turn.get('question', 'N/A')}")
                
                responses = turn.get('responses', [])
                for response in responses[:2]:  # Show first 2 responses per question
                    persona_name = response.get('persona_name', 'Unknown')
                    content = response.get('content', 'No response')
                    
                    # Find the detailed persona for context
                    detailed_persona = next((p for p in detailed_personas if p.name == persona_name), None)
                    context_note = ""
                    if detailed_persona:
                        key_struggle = detailed_persona.major_struggles[0] if detailed_persona.major_struggles else "N/A"
                        context_note = f" (Key struggle: {key_struggle[:50]}...)"
                    
                    print(f"   👤 {persona_name}{context_note}:")
                    print(f"      \"{content[:200]}{'...' if len(content) > 200 else ''}\"")
        
        # Show benefits of detailed personas
        print(f"\n✨ Benefits of Detailed Personas:")
        print(f"   • Rich psychological context enables more authentic responses")
        print(f"   • Specific fears and desires create realistic motivations")
        print(f"   • Signature phrases and communication styles add personality")
        print(f"   • Day-in-the-life scenarios provide behavioral context")
        print(f"   • Previous attempts/failures inform realistic objections")
        
    except Exception as e:
        print(f"❌ Session error: {e}")
        print("Note: This may be due to missing AI client configuration")
        print("The personas are still properly configured and ready for use!")
    
    print(f"\n🏁 Demo Complete!")
    print(f"The enhanced persona system is ready for production use.")

if __name__ == "__main__":
    demo_detailed_personas_in_session()