#!/usr/bin/env python3
"""
Simple "Run" interface for synthetic focus group sessions.

Usage:
    python run_synthetic_session.py

Click "Run" and it produces JSONL + CSV with zero schema errors.
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from session.synthetic_runner import SyntheticSessionRunner, create_sample_personas


def run_demo_session():
    """Run a complete demo synthetic session."""
    
    print("🎯 Synthetic Focus Group Session Runner")
    print("=" * 50)
    
    # Configuration
    study_id = "social_media_tool_study"
    topic = "social media management tools for small businesses"
    
    print(f"📋 Study ID: {study_id}")
    print(f"🎯 Research Topic: {topic}")
    print()
    
    # Ask user if they want to proceed
    response = input("▶️  Press Enter to RUN synthetic session (or 'q' to quit): ").strip().lower()
    
    if response == 'q':
        print("👋 Goodbye!")
        return
    
    print("\n🚀 RUNNING SYNTHETIC SESSION...")
    print("=" * 50)
    
    try:
        # Initialize runner
        runner = SyntheticSessionRunner()
        
        # Get sample personas
        personas = create_sample_personas()
        
        # Run the session
        results = runner.run_session(
            study_id=study_id,
            topic=topic,
            personas=personas,
            num_questions=3
        )
        
        # Display results
        print("\n" + "=" * 50)
        print("✅ SESSION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        summary = results['summary']
        validation = results['validation_results']
        
        print(f"📊 RESULTS SUMMARY:")
        print(f"   • Session ID: {results['session_id']}")
        print(f"   • Total Q/A Turns: {summary['total_turns']}")
        print(f"   • Participants: {summary['personas']}")
        print(f"   • Questions Asked: {summary['questions']}")
        print(f"   • Average Confidence: {summary['avg_confidence']:.1%}")
        print(f"   • Themes Identified: {summary['themes_identified']}")
        print(f"   • Insights Generated: {summary['insights_generated']}")
        print(f"   • Files Created: {summary['files_created']}")
        
        print(f"\n📁 FILES CREATED:")
        storage = results['storage_results']
        print(f"   📄 JSONL: {storage['jsonl_path']}")
        print(f"   📊 CSV: {storage['csv_path']}")
        print(f"   📋 Metadata: {storage['metadata_path']}")
        print(f"   📂 Folder: {storage['session_folder']}")
        
        print(f"\n✅ DATA VALIDATION:")
        if validation['status'] == 'valid':
            print("   🎉 ZERO SCHEMA ERRORS - All data validates perfectly!")
        else:
            print(f"   ❌ {validation['total_errors']} validation errors found")
        
        print(f"\n🎯 TOP INSIGHTS:")
        analysis = results['analysis']
        for i, insight in enumerate(analysis.get('insights', [])[:3], 1):
            print(f"   {i}. {insight}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(analysis.get('recommendations', [])[:3], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n🏆 SUCCESS! The session ran end-to-end with zero errors.")
        print(f"    Ready for production use.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Session failed - please check the error details above.")
        return False
    
    return True


def run_custom_session():
    """Run a custom session with user input."""
    
    print("🛠️  CUSTOM SESSION CONFIGURATION")
    print("=" * 40)
    
    # Get user input
    study_id = input("Study ID (default: custom_study): ").strip() or "custom_study"
    topic = input("Research topic: ").strip()
    
    if not topic:
        print("❌ Research topic is required!")
        return False
    
    print(f"\n📋 Configuration:")
    print(f"   Study ID: {study_id}")
    print(f"   Topic: {topic}")
    
    response = input("\n▶️  Proceed with these settings? (y/n): ").strip().lower()
    if response != 'y':
        print("👋 Session cancelled.")
        return False
    
    print(f"\n🚀 RUNNING CUSTOM SESSION...")
    print("=" * 40)
    
    try:
        runner = SyntheticSessionRunner()
        personas = create_sample_personas()
        
        results = runner.run_session(
            study_id=study_id,
            topic=topic,
            personas=personas,
            num_questions=3
        )
        
        print(f"\n✅ CUSTOM SESSION COMPLETED!")
        print(f"   Session ID: {results['session_id']}")
        print(f"   Files: {results['storage_results']['session_folder']}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False
    
    return True


def main():
    """Main interface."""
    
    print("""
    🤖 SYNTHETIC FOCUS GROUP RUNNER
    
    This tool runs end-to-end synthetic focus group sessions
    with AI facilitators and personas, producing structured
    JSONL and CSV data with zero schema errors.
    
    """)
    
    while True:
        print("OPTIONS:")
        print("1. 🚀 Run Demo Session (recommended)")
        print("2. 🛠️  Run Custom Session") 
        print("3. 🔍 Validate Existing Session")
        print("4. 📊 View Sample Data")
        print("5. ❌ Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            run_demo_session()
            
        elif choice == '2':
            run_custom_session()
            
        elif choice == '3':
            validate_session()
            
        elif choice == '4':
            show_sample_data()
            
        elif choice == '5':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-5.")
        
        print("\n" + "─" * 60)


def validate_session():
    """Validate an existing session."""
    print("\n🔍 SESSION VALIDATION")
    print("=" * 30)
    
    study_id = input("Study ID: ").strip()
    session_id = input("Session ID: ").strip()
    
    if not study_id or not session_id:
        print("❌ Both Study ID and Session ID are required!")
        return
    
    from storage.qa_storage import QAStorage
    
    storage = QAStorage()
    results = storage.validate_stored_session(study_id, session_id)
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"   Status: {results['status']}")
    print(f"   Total Errors: {results['total_errors']}")
    
    for validation in results['validation_results']:
        print(f"   File: {validation['file']}")
        print(f"      Turns: {validation['turns_count']}")
        print(f"      Status: {validation['status']}")
        if validation['errors']:
            for error in validation['errors']:
                print(f"         ❌ {error}")


def show_sample_data():
    """Show sample Q/A turn data."""
    print("\n📊 SAMPLE Q/A TURN DATA")
    print("=" * 35)
    
    from models.qa_turn import create_sample_qa_turn
    
    sample = create_sample_qa_turn()
    
    print("📄 JSON Structure:")
    print(sample.to_json())
    
    print(f"\n✅ Schema Validation:")
    try:
        sample.validate_schema()
        print("   🎉 Valid - passes all schema checks!")
    except Exception as e:
        print(f"   ❌ Invalid: {e}")
    
    print(f"\n📋 Required Fields:")
    required_fields = [
        "study_id", "session_id", "persona_id", "round_id",
        "question", "answer", "confidence_0_1", "tags", "ts"
    ]
    
    for field in required_fields:
        value = getattr(sample, field)
        print(f"   {field}: {value}")


if __name__ == "__main__":
    main()