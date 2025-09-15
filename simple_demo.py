#!/usr/bin/env python3
"""
Simple Enhanced Synthetic Focus Group Demo
No external dependencies - just run and see results!
"""

import json
import csv
import datetime
import os
from pathlib import Path

def main():
    print("🎯 ENHANCED SYNTHETIC FOCUS GROUP - SIMPLE DEMO")
    print("=" * 60)
    
    while True:
        print("\n📋 Demo Options:")
        print("   1. 🚀 Run Full Enhanced Demo")
        print("   2. 🔒 Show Security Features") 
        print("   3. 📊 Show Demo Data")
        print("   4. 📁 View Generated Files")
        print("   5. 🌐 Open HTML Demo")
        print("   6. 👋 Exit")
        
        try:
            choice = input("\n🔍 Select option (1-6): ").strip()
            
            if choice == "1":
                run_full_demo()
            elif choice == "2":
                show_security_features()
            elif choice == "3":
                show_demo_data()
            elif choice == "4":
                view_generated_files()
            elif choice == "5":
                open_html_demo()
            elif choice == "6":
                print("\n👋 Thanks for testing the Enhanced Synthetic Focus Group Demo!")
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo cancelled.")
            break

def run_full_demo():
    """Run the complete enhanced demo simulation."""
    print("\n🚀 Running Enhanced Demo...")
    print("-" * 40)
    
    # Simulate demo data
    personas = [
        {'id': 'sarah_small_business', 'name': 'Sarah Thompson', 'weight': 3.0, 'rank': 1, 'is_primary_icp': True},
        {'id': 'mike_marketing_mgr', 'name': 'Mike Rodriguez', 'weight': 2.0, 'rank': 2, 'is_primary_icp': False},
        {'id': 'jenny_freelancer', 'name': 'Jenny Chen', 'weight': 1.5, 'rank': 3, 'is_primary_icp': False}
    ]
    
    responses = [
        {'persona_id': 'sarah_small_business', 'sentiment': 0.2, 'themes': ['tool_switching', 'integration_needs', 'pricing_acceptance']},
        {'persona_id': 'sarah_small_business', 'sentiment': 0.6, 'themes': ['pricing_acceptance', 'time_savings', 'roi_focus']},
        {'persona_id': 'mike_marketing_mgr', 'sentiment': 0.1, 'themes': ['attribution_problems', 'roi_tracking', 'executive_pressure']},
        {'persona_id': 'mike_marketing_mgr', 'sentiment': 0.4, 'themes': ['analytics_integration', 'crm_connection', 'business_impact']},
        {'persona_id': 'jenny_freelancer', 'sentiment': 0.0, 'themes': ['multi_client_management', 'manual_reporting', 'budget_constraints']},
        {'persona_id': 'jenny_freelancer', 'sentiment': 0.3, 'themes': ['budget_constraints', 'basic_features', 'pricing_sensitivity']}
    ]
    
    # Calculate weighted analysis
    total_weight = sum(p['weight'] for p in personas)
    normalized_weights = {p['id']: (p['weight'] / total_weight) * len(personas) for p in personas}
    
    # Calculate weighted sentiment
    total_weighted_sentiment = 0
    total_weight_applied = 0
    
    for response in responses:
        weight = normalized_weights[response['persona_id']]
        total_weighted_sentiment += response['sentiment'] * weight
        total_weight_applied += weight
    
    weighted_avg_sentiment = total_weighted_sentiment / total_weight_applied
    
    # Calculate theme weights
    theme_weights = {}
    for response in responses:
        weight = normalized_weights[response['persona_id']]
        for theme in response['themes']:
            theme_weights[theme] = theme_weights.get(theme, 0) + weight
    
    sorted_themes = sorted(theme_weights.items(), key=lambda x: x[1], reverse=True)
    
    # Display results
    print("📊 DEMO RESULTS:")
    print(f"   • Total Responses: {len(responses)}")
    print(f"   • Personas: {len(personas)}")
    print(f"   • Weighted Sentiment: {weighted_avg_sentiment:.3f}")
    print(f"   • Primary ICP: sarah_small_business")
    
    print(f"\n⚖️  Persona Weights:")
    for persona in personas:
        status = "🎯 PRIMARY ICP" if persona['is_primary_icp'] else f"📊 Rank #{persona['rank']}"
        print(f"   • {persona['name']}: {normalized_weights[persona['id']]:.2f}x weight {status}")
    
    print(f"\n🏷️  Top Themes (by weighted importance):")
    for i, (theme, weight) in enumerate(sorted_themes[:5], 1):
        print(f"   {i}. {theme.replace('_', ' ').title()}: {weight:.2f} weighted mentions")
    
    # Generate export files
    print(f"\n📁 Generating export files...")
    
    export_data = {
        'session_info': {
            'session_id': 'demo_session_001',
            'created_at': datetime.datetime.now().isoformat(),
            'total_responses': len(responses),
            'personas_analyzed': len(personas)
        },
        'weighting_system': {
            'weighted_analysis_enabled': True,
            'persona_weights': {p['id']: p['weight'] for p in personas},
            'normalized_weights': normalized_weights,
            'primary_icp': 'sarah_small_business'
        },
        'weighted_analysis': {
            'overall_sentiment': {
                'weighted_score': weighted_avg_sentiment,
                'confidence': 'high',
                'total_weight_applied': total_weight_applied
            },
            'themes_by_importance': sorted_themes[:5]
        },
        'insights': [
            "Primary ICP (Sarah) shows strong willingness to pay $30-50/month for integrated solution",
            "Tool switching and integration needs are the highest weighted concerns", 
            "Clear pricing differentiation needed between business owners ($30-50) and freelancers ($15-20)"
        ]
    }
    
    # Save files
    with open('demo_weighted_analysis_export.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    
    with open('demo_weighted_responses.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['persona_id', 'persona_name', 'persona_weight', 'is_primary_icp', 'sentiment_score', 'weighted_sentiment', 'themes'])
        
        for response in responses:
            persona = next(p for p in personas if p['id'] == response['persona_id'])
            weight = normalized_weights[response['persona_id']]
            writer.writerow([
                response['persona_id'],
                persona['name'], 
                weight,
                persona['is_primary_icp'],
                response['sentiment'],
                response['sentiment'] * weight,
                '; '.join(response['themes'])
            ])
    
    print("✅ Files created:")
    print("   • demo_weighted_analysis_export.json")
    print("   • demo_weighted_responses.csv")
    
    print(f"\n🎯 Key Insights:")
    for insight in export_data['insights']:
        print(f"   • {insight}")

def show_security_features():
    """Display security features information."""
    print("\n🔒 SECURITY FEATURES")
    print("-" * 40)
    
    print("🛡️  Security Measures Implemented:")
    print("   ✅ SQL Injection Prevention - Parameterized queries with identifier quoting")
    print("   ✅ Input Validation - Collection names validated against safe patterns") 
    print("   ✅ Bounds Checking - Vector dimensions limited to reasonable ranges (1-2048)")
    print("   ✅ Connection Security - Secure pooling with timeouts and limits")
    print("   ✅ Credential Validation - Database URL format and security checking")
    
    print(f"\n🔒 Test Cases That Would Be Blocked:")
    print('   ❌ SQL Injection: "test; DROP TABLE users;" - BLOCKED')
    print('   ❌ Null Byte Injection: "test\\x00malicious" - BLOCKED')
    print('   ❌ Empty Input: "" - BLOCKED')  
    print('   ❌ Oversized Dimension: 10000 - BLOCKED')
    
    print(f"\n⚡ To Test Security in Code:")
    print("   python -c \"from src.vector.backend_pgvector import PgVector; PgVector()._ensure_table('invalid; DROP TABLE users;', 1536)\"")

def show_demo_data():
    """Display the demo data structure."""
    print("\n📊 DEMO DATA OVERVIEW")
    print("-" * 40)
    
    personas = [
        {'name': 'Sarah Thompson', 'role': 'Small Business Owner', 'weight': 3.0, 'rank': 1, 'is_primary_icp': True, 'notes': 'Primary ICP - small business owner, high growth potential'},
        {'name': 'Mike Rodriguez', 'role': 'Marketing Manager', 'weight': 2.0, 'rank': 2, 'is_primary_icp': False, 'notes': 'Secondary target - enterprise marketing managers'},
        {'name': 'Jenny Chen', 'role': 'Freelance Social Media Manager', 'weight': 1.5, 'rank': 3, 'is_primary_icp': False, 'notes': 'Lower priority - freelancers with budget constraints'}
    ]
    
    print("👥 Demo Personas & Weights:")
    for persona in personas:
        status = "🎯 PRIMARY ICP" if persona['is_primary_icp'] else f"📊 Rank #{persona['rank']}"
        print(f"   • {persona['name']}: {persona['weight']}x weight {status}")
        print(f"     Role: {persona['role']}")
        print(f"     Notes: {persona['notes']}")
        print()
    
    print("💬 Sample Response Topics:")
    print("   • Tool switching and integration challenges")
    print("   • Pricing acceptance and budget constraints") 
    print("   • ROI attribution and analytics needs")
    print("   • Time savings and efficiency requirements")
    print("   • Feature prioritization (basic vs enterprise)")

def view_generated_files():
    """View information about generated files."""
    print("\n📁 GENERATED FILES")
    print("-" * 40)
    
    files = [
        'demo_weighted_analysis_export.json',
        'demo_weighted_responses.csv', 
        'demo_dashboard_data.json',
        'demo.html'
    ]
    
    print("📋 Available Files:")
    for filename in files:
        file_path = Path(filename)
        if file_path.exists():
            size = file_path.stat().st_size
            modified = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
            print(f"   ✅ {filename}")
            print(f"      Size: {size:,} bytes")
            print(f"      Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   ❌ {filename} (not found)")
        print()
    
    print("💡 To generate files, run option 1 (Full Enhanced Demo)")

def open_html_demo():
    """Open the HTML demo in browser."""
    print("\n🌐 HTML DEMO")
    print("-" * 40)
    
    html_file = Path("demo.html")
    if html_file.exists():
        print("✅ HTML demo file found!")
        print(f"📍 Location: {html_file.absolute()}")
        print("🔍 To open in browser:")
        print(f"   • Double-click: demo.html")  
        print(f"   • Or open: {html_file.absolute()}")
        print("\n💡 The HTML demo includes interactive buttons and beautiful formatting!")
        
        # Try to open in browser automatically
        try:
            import webbrowser
            webbrowser.open(f"file://{html_file.absolute()}")
            print("🚀 Opening in your default browser...")
        except:
            print("⚠️  Could not auto-open browser - please open demo.html manually")
    else:
        print("❌ demo.html not found in current directory")

if __name__ == "__main__":
    main()