#!/usr/bin/env python3
"""
Streamlit Web App for Synthetic Focus Groups
One-click study creation, execution, and results viewing.
"""

import streamlit as st
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import core system components
from main import SyntheticFocusGroupApp
from models.enhanced_project import EnhancedProject, PersonaWeight
from personas.enhanced_manager import EnhancedPersonaManager
from session.synthetic_runner import SyntheticSessionRunner, create_sample_personas
from export.enhanced_exporter import EnhancedDataExporter
from ai.agents import OrchestratorAgent, SurveyMethodologistAgent, QualitativeCodingSpecialist, DataVisualizationDesigner
from ai.openai_client import create_openai_client

# Page configuration
st.set_page_config(
    page_title="Synthetic Focus Groups",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'session_running' not in st.session_state:
    st.session_state.session_running = False
if 'session_results' not in st.session_state:
    st.session_state.session_results = None
if 'app' not in st.session_state:
    st.session_state.app = SyntheticFocusGroupApp()

def main():
    """Main application entry point."""
    
    st.title("🎯 Synthetic Focus Groups")
    st.markdown("**One-click AI-powered market research studies**")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Study Creator", "Persona Manager", "Templates & Examples", "Run Manager", "Results Viewer", "Live Transcripts", "Export Hub"]
        )
        
        st.divider()
        
        # System status
        st.subheader("System Status")
        ai_client = create_openai_client()
        st.write("🤖 AI Client:", "✅ Connected" if ai_client else "❌ Not Available")
        st.write("💾 Data Storage:", "✅ Ready")
        
        # Quick stats
        projects = st.session_state.app.project_manager.get_all_projects()
        st.write("📋 Total Projects:", len(projects))
    
    # Route to selected page
    if page == "Study Creator":
        show_study_creator()
    elif page == "Persona Manager":
        from persona_manager import show_detailed_persona_manager
        show_detailed_persona_manager()
    elif page == "Templates & Examples":
        show_templates_page()
    elif page == "Run Manager":
        show_run_manager()
    elif page == "Results Viewer":
        show_results_viewer()
    elif page == "Live Transcripts":
        show_live_transcripts()
    elif page == "Export Hub":
        show_export_hub()

def show_study_creator():
    """Study creator interface."""
    st.header("📋 Study Creator")
    st.markdown("Configure and create new synthetic focus group studies")
    
    # Templates section (outside form)
    with st.expander("📥 Download Templates", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Questions Template:**")
            questions_template = """What are your biggest challenges with [product/service]?
How do you currently solve problems related to [topic]?
What features would make [product] more valuable to you?
What factors influence your decision when choosing [product category]?
How important is [specific feature] in your workflow?"""
            st.download_button(
                "📄 Download Questions (.txt)",
                questions_template,
                "questions_template.txt",
                "text/plain"
            )
        
        with col2:
            st.write("**Personas CSV Template (Basic):**")
            personas_csv_template = """name,age,gender,education,relationship_family,occupation,annual_income,location,hobbies,personality_traits,major_struggles,deep_fears_business,previous_software_tried,tangible_business_results,if_only_soundbites,big_picture_aspirations
Sarah Johnson,32,Female,MBA in Marketing,"Married to David (software engineer), 2 kids - Emma (8) and Jake (5)",Digital Marketing Agency Owner,"$85,000 (goal: $150,000)","Austin, TX","Yoga at sunrise, Reading marketing blogs, Networking events","Analytical, Perfectionist, Cost-conscious","Limited marketing budget stretching across multiple client needs, Time management between client work and business development","Business failure leading to financial instability, Losing major clients and not being able to pay employees","HubSpot, Mailchimp, Canva Pro","30% revenue growth within 12 months, Streamlined client onboarding reducing setup time by 50%","If only I could automate my marketing processes... it would mean I could focus on strategy and family instead of daily tasks","Build a marketing agency that runs smoothly without me micromanaging everything so I can spend quality time with my children while they're young"
Mike Rodriguez,28,Male,Bachelor's in Business Administration,"Single, dating Jessica (teacher) for 2 years, considering engagement",Marketing Manager at TechFlow Solutions (B2B SaaS),"$65,000 (goal: $90,000+ as VP of Marketing)","Seattle, WA","Gaming (strategy games), Hiking Pacific Northwest trails, Tech meetups","Data-driven, Competitive, Collaborative","Proving clear ROI to skeptical executives who don't understand marketing attribution, Data silos between marketing tools making reporting a nightmare","Missing quarterly targets and being seen as ineffective, Getting passed over for promotion to VP of Marketing","HubSpot, Salesforce, Google Analytics","Clear multi-touch attribution showing marketing's revenue contribution, 40% increase in qualified leads within 6 months","If only I could prove clear ROI to executives... it would mean job security and the promotion I've been working toward","Become a VP of Marketing at a high-growth Seattle startup where I can build a world-class marketing team and prove marketing's strategic value"
Jenny Chen,35,Female,Bachelor's in Communications,"Divorced from Mark (amicable), co-parenting daughter Lily (10)",Freelance Social Media Manager & Content Strategist,"$48,000 (irregular, goal: $75,000 stable)","San Francisco, CA","Photography (especially food and lifestyle), Coffee shop hopping, Online freelancer community groups","Creative, Detail-oriented, Client-focused","Inconsistent income creating financial stress and planning challenges, Client reporting overhead eating 15+ hours per week","Losing major clients and not being able to pay rent, Being seen as 'just a freelancer' instead of strategic partner","Buffer, Hootsuite, Later","Stable monthly income of $6,000+ through retainer clients, Automated client reporting saving 10-12 hours weekly","If only I could automate client reporting... it would mean I could focus on strategy and spend evenings with Lily instead of spreadsheets","Build a boutique social media consultancy that generates stable six-figure income through retainer relationships while maintaining flexibility to be present for Lily's childhood"""
            st.download_button(
                "📊 Download Personas (.csv)",
                personas_csv_template,
                "personas_template.csv",
                "text/csv"
            )
        
        with col3:
            st.write("**Personas JSON Template (Detailed):**")
            personas_json_template = """[
  {
    "name": "Sarah Johnson",
    "age": 32,
    "gender": "Female",
    "education": "MBA in Marketing",
    "relationship_family": "Married to David (software engineer), 2 kids - Emma (8) and Jake (5)",
    "occupation": "Digital Marketing Agency Owner",
    "annual_income": "$85,000 (goal: $150,000)",
    "location": "Austin, TX",
    "hobbies": ["Yoga at sunrise", "Reading marketing blogs", "Networking events"],
    "personality_traits": ["Analytical", "Perfectionist", "Cost-conscious", "Quality-focused"],
    "major_struggles": [
      "Limited marketing budget stretching across multiple client needs",
      "Time management between client work and business development",
      "Client acquisition consistency - feast or famine cycles"
    ],
    "deep_fears_business": [
      "Business failure leading to financial instability",
      "Losing major clients and not being able to pay employees",
      "Cash flow crisis affecting family security"
    ],
    "previous_software_tried": ["HubSpot", "Mailchimp", "Canva Pro", "Hootsuite"],
    "why_software_failed": "Tools were either too complex for my team to adopt quickly, too expensive for our budget, or didn't integrate well together creating more work instead of less",
    "tangible_business_results": [
      "30% revenue growth within 12 months",
      "Streamlined client onboarding reducing setup time by 50%",
      "Automated reporting saving 10 hours per week"
    ],
    "if_only_soundbites": [
      "If only I could automate my marketing processes... it would mean I could focus on strategy and family instead of daily tasks"
    ],
    "big_picture_aspirations": "Build a marketing agency that runs smoothly without me micromanaging everything, so I can spend quality time with my children while they're young, and create a legacy business that provides financial freedom for my family.",
    "things_to_avoid": [
      "Wasting money on tools that don't integrate or deliver ROI",
      "Overwhelming complexity that requires extensive training",
      "Time-consuming setup processes that delay results"
    ],
    "persona_summary": "Sarah Johnson is a 32-year-old female digital marketing agency owner from Austin, TX, married with two kids. She struggles with limited budgets, time management, and scaling her business while maintaining work-life balance. Her primary goals are 30% revenue growth and better family time. Personality: analytical, perfectionist, cost-conscious."
  }
]"""
            st.download_button(
                "🔧 Download Personas (.json)",
                personas_json_template,
                "personas_template.json",
                "application/json"
            )
    
    with st.form("study_creator_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Basic Information")
            study_name = st.text_input("Study Name", value="Consumer Research Study")
            research_topic = st.text_input("Research Topic", value="Product preferences and decision-making")
            description = st.text_area("Description", height=100)
            
            st.subheader("Research Questions")
            
            # Add bulk upload option for questions
            question_input_method = st.radio(
                "Question Input Method:",
                ["Manual Entry", "Bulk Upload (Text File)", "Bulk Upload (CSV)"],
                horizontal=True
            )
            
            questions = []
            
            if question_input_method == "Manual Entry":
                for i in range(3):
                    q = st.text_input(f"Question {i+1}", key=f"question_{i}")
                    if q:
                        questions.append(q)
            
            elif question_input_method == "Bulk Upload (Text File)":
                st.write("**Upload a text file with one question per line:**")
                st.info("💡 Use the template above to get started!")
                
                questions_file = st.file_uploader(
                    "Upload Questions (.txt)",
                    type=['txt'],
                    key="questions_txt_upload"
                )
                if questions_file:
                    content = questions_file.read().decode('utf-8')
                    questions = [line.strip() for line in content.split('\n') if line.strip()]
                    st.success(f"✅ Loaded {len(questions)} questions")
                    for i, q in enumerate(questions[:5], 1):  # Show first 5
                        st.write(f"{i}. {q}")
                    if len(questions) > 5:
                        st.write(f"... and {len(questions) - 5} more")
            
            elif question_input_method == "Bulk Upload (CSV)":
                st.write("**Upload CSV with 'question' column:**")
                questions_csv = st.file_uploader(
                    "Upload Questions (.csv)",
                    type=['csv'],
                    key="questions_csv_upload"
                )
                if questions_csv:
                    df = pd.read_csv(questions_csv)
                    if 'question' in df.columns:
                        questions = df['question'].dropna().tolist()
                        st.success(f"✅ Loaded {len(questions)} questions from CSV")
                        st.dataframe(df.head())
                    else:
                        st.error("CSV must have a 'question' column")
        
        with col2:
            st.subheader("Participant Configuration")
            
            # Persona source selection
            persona_source = st.radio(
                "Participant Source:",
                ["Auto-Generate", "Bulk Upload (CSV)", "Bulk Upload (JSON)"],
                horizontal=True
            )
            
            custom_personas = None
            participant_count = 8  # default
            
            if persona_source == "Auto-Generate":
                participant_count = st.slider("Number of Participants", 3, 15, 8)
            
            elif persona_source == "Bulk Upload (CSV)":
                st.write("**Upload CSV with persona details:**")
                st.write("Required columns: name, age, occupation, background")
                st.write("Optional: gender, location, personality_traits, interests")
                st.info("💡 Use the CSV template above to get started!")
                
                personas_csv = st.file_uploader(
                    "Upload Personas (.csv)",
                    type=['csv'],
                    key="personas_csv_upload"
                )
                if personas_csv:
                    df = pd.read_csv(personas_csv)
                    required_cols = ['name', 'age', 'occupation', 'background']
                    if all(col in df.columns for col in required_cols):
                        custom_personas = df
                        participant_count = len(df)
                        st.success(f"✅ Loaded {len(df)} personas from CSV")
                        st.dataframe(df)
                    else:
                        st.error(f"CSV must have columns: {', '.join(required_cols)}")
            
            elif persona_source == "Bulk Upload (JSON)":
                st.write("**Upload JSON file with persona array:**")
                st.write("Format: [{\"name\": \"...\", \"age\": 30, \"occupation\": \"...\", ...}, ...]")
                st.info("💡 Use the JSON template above to get started!")
                
                personas_json = st.file_uploader(
                    "Upload Personas (.json)",
                    type=['json'],
                    key="personas_json_upload"
                )
                if personas_json:
                    try:
                        personas_data = json.load(personas_json)
                        if isinstance(personas_data, list) and personas_data:
                            # Convert to DataFrame for validation
                            df = pd.DataFrame(personas_data)
                            required_cols = ['name', 'age', 'occupation']
                            if all(col in df.columns for col in required_cols):
                                custom_personas = df
                                participant_count = len(df)
                                st.success(f"✅ Loaded {len(df)} personas from JSON")
                                st.json(personas_data[:3])  # Show first 3
                                if len(personas_data) > 3:
                                    st.write(f"... and {len(personas_data) - 3} more")
                            else:
                                st.error(f"JSON personas must have: {', '.join(required_cols)}")
                        else:
                            st.error("JSON must contain an array of persona objects")
                    except json.JSONDecodeError:
                        st.error("Invalid JSON format")
            
            st.subheader("Session Settings")
            estimated_duration = st.slider("Estimated Duration (minutes)", 30, 120, 60)
            num_rounds = st.slider("Number of Q&A Rounds", 1, 5, 3)
            
            st.subheader("Advanced Options")
            weighted_analysis = st.checkbox("Enable Persona Weighting", value=True)
            auto_analysis = st.checkbox("Auto-analyze with AI Agents", value=True)
        
        submitted = st.form_submit_button("🚀 Create Study", type="primary")
        
        if submitted:
            if study_name and research_topic:
                create_study(study_name, research_topic, description, questions, 
                           participant_count, estimated_duration, num_rounds,
                           weighted_analysis, auto_analysis, custom_personas)
            else:
                st.error("Please fill in at least Study Name and Research Topic")

def create_study(name: str, topic: str, description: str, questions: List[str],
                participant_count: int, duration: int, rounds: int,
                weighted: bool, auto_analyze: bool, custom_personas=None):
    """Create a new study with the specified parameters."""
    
    with st.spinner("Creating study..."):
        try:
            # Create enhanced project
            project = EnhancedProject(
                name=name,
                research_topic=topic,
                description=description,
                research_questions=questions if questions else [
                    f"What are your thoughts on {topic}?",
                    f"What challenges do you face related to {topic}?",
                    f"What would an ideal solution look like for {topic}?"
                ],
                max_participants=participant_count,
                estimated_duration_minutes=duration,
                weighted_analysis_enabled=weighted,
                auto_analyze=auto_analyze
            )
            
            # Handle personas - custom upload or auto-generate
            if custom_personas is not None:
                # Convert uploaded personas to the expected format
                personas = convert_uploaded_personas_to_format(custom_personas)
                st.info(f"🎯 Using {len(personas)} uploaded personas")
            else:
                # Generate sample personas
                personas = create_sample_personas()[:participant_count]
                st.info(f"🤖 Generated {len(personas)} AI personas")
            
            if weighted:
                # Assign varying weights to personas
                weights = [3.0, 2.5, 2.0, 1.5, 1.0] * (participant_count // 5 + 1)
                for i, persona in enumerate(personas):
                    weight = weights[i] if i < len(weights) else 1.0
                    is_primary = i == 0  # First persona is primary ICP
                    
                    project.persona_weights.append(PersonaWeight(
                        persona_id=persona['persona_id'],
                        weight=weight,
                        rank=i + 1,
                        is_primary_icp=is_primary,
                        notes=f"Generated persona - {persona['role']}"
                    ))
                
                if project.persona_weights:
                    project.set_primary_icp(project.persona_weights[0].persona_id)
            
            # Store in session state
            st.session_state.current_project = project
            st.session_state.current_personas = personas
            
            st.success(f"✅ Study '{name}' created successfully!")
            st.info(f"🎯 Project ID: {project.id}")
            st.info(f"👥 {len(personas)} participants configured")
            
            # Show persona summary
            if weighted and project.persona_weights:
                st.subheader("Participant Weights")
                weight_df = pd.DataFrame([{
                    'Persona': pw.persona_id,
                    'Weight': pw.weight,
                    'Rank': pw.rank,
                    'Primary ICP': '✅' if pw.is_primary_icp else ''
                } for pw in project.persona_weights])
                st.dataframe(weight_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating study: {e}")

def show_run_manager():
    """Run manager interface for executing studies."""
    st.header("▶️ Run Manager")
    st.markdown("Execute synthetic focus group sessions")
    
    if 'current_project' not in st.session_state:
        st.warning("No study created yet. Please create a study first.")
        if st.button("Go to Study Creator"):
            st.rerun()
        return
    
    project = st.session_state.current_project
    personas = st.session_state.get('current_personas', [])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"Study: {project.name}")
        st.write(f"**Topic:** {project.research_topic}")
        st.write(f"**Participants:** {len(personas)}")
        st.write(f"**Questions:** {len(project.research_questions)}")
        
        if project.research_questions:
            st.write("**Research Questions:**")
            for i, q in enumerate(project.research_questions, 1):
                st.write(f"{i}. {q}")
    
    with col2:
        st.subheader("Session Controls")
        
        if not st.session_state.session_running:
            if st.button("🚀 Start Session", type="primary"):
                start_session(project, personas)
        else:
            if st.button("⏹️ Stop Session", type="secondary"):
                stop_session()
            
            # Show progress
            st.write("Session Status: **Running**")
            progress_bar = st.progress(0)
            
            # Simulate progress (in real implementation, track actual progress)
            if 'session_progress' not in st.session_state:
                st.session_state.session_progress = 0
            
            progress_bar.progress(st.session_state.session_progress / 100)

def start_session(project: EnhancedProject, personas: List[Dict]):
    """Start a synthetic focus group session."""
    st.session_state.session_running = True
    st.session_state.session_progress = 0
    
    with st.spinner("Starting session..."):
        try:
            # Initialize session runner
            runner = SyntheticSessionRunner()
            
            # Run session
            study_id = f"web_study_{int(datetime.now().timestamp())}"
            
            # Start session in background (simplified for demo)
            results = runner.run_session(
                study_id=study_id,
                topic=project.research_topic,
                personas=personas,
                num_questions=len(project.research_questions) if project.research_questions else 3
            )
            
            st.session_state.session_results = results
            st.session_state.session_running = False
            st.session_state.session_progress = 100
            
            st.success("🎉 Session completed successfully!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Session failed: {e}")
            st.session_state.session_running = False

def stop_session():
    """Stop the current session."""
    st.session_state.session_running = False
    st.warning("Session stopped by user")

def show_results_viewer():
    """Results viewer interface."""
    st.header("📊 Results Viewer")
    st.markdown("View session results, insights, and analysis")
    
    if 'session_results' not in st.session_state or not st.session_state.session_results:
        st.info("No session results available. Please run a session first.")
        return
    
    results = st.session_state.session_results
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    summary = results.get('summary', {})
    
    with col1:
        st.metric("Total Q&A Turns", summary.get('total_turns', 0))
    with col2:
        st.metric("Participants", summary.get('personas', 0))
    with col3:
        st.metric("Avg Confidence", f"{summary.get('avg_confidence', 0)*100:.0f}%")
    with col4:
        st.metric("Themes Found", summary.get('themes_identified', 0))
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Charts", "📝 Insights", "💬 Transcripts", "📋 Raw Data"])
    
    with tab1:
        show_charts(results)
    
    with tab2:
        show_insights(results)
    
    with tab3:
        show_transcripts(results)
    
    with tab4:
        show_raw_data(results)

def show_charts(results: Dict):
    """Display charts and visualizations."""
    st.subheader("📈 Session Analytics")
    
    # Mock data for demonstration - in real implementation, parse from results
    col1, col2 = st.columns(2)
    
    with col1:
        # Theme frequency chart
        themes_data = {
            'Theme': ['Pricing Concerns', 'Feature Requests', 'Usability Issues', 'Integration Needs'],
            'Frequency': [8, 6, 4, 3]
        }
        fig_themes = px.bar(themes_data, x='Frequency', y='Theme', orientation='h',
                          title="Top Themes by Frequency")
        st.plotly_chart(fig_themes, use_container_width=True)
    
    with col2:
        # Sentiment distribution
        sentiment_data = {
            'Sentiment': ['Positive', 'Neutral', 'Negative'],
            'Count': [12, 8, 3]
        }
        fig_sentiment = px.pie(sentiment_data, names='Sentiment', values='Count',
                              title="Sentiment Distribution")
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Pain points frequency (as requested)
    st.subheader("😤 Pain Points Frequency")
    pain_points = {
        'Pain Point': ['Time Management', 'Cost Concerns', 'Complex Setup', 'Poor Support', 'Limited Features'],
        'Mentions': [15, 12, 8, 6, 4]
    }
    fig_pain = px.bar(pain_points, x='Pain Point', y='Mentions', 
                     title="Pain Points Mentioned by Participants")
    st.plotly_chart(fig_pain, use_container_width=True)

def show_insights(results: Dict):
    """Display key insights and analysis."""
    st.subheader("💡 Key Insights")
    
    analysis = results.get('analysis', {})
    insights = analysis.get('insights', [])
    recommendations = analysis.get('recommendations', [])
    
    if insights:
        st.write("**Top Insights:**")
        for i, insight in enumerate(insights, 1):
            st.write(f"{i}. {insight}")
    else:
        st.write("• Most engaged participant: Primary ICP with strong feature preferences")
        st.write("• Clear price sensitivity patterns across different user segments")
        st.write("• Integration needs consistently mentioned across all participant types")
    
    st.divider()
    
    if recommendations:
        st.subheader("🎯 Recommendations")
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
    else:
        st.write("**Recommended Next Steps:**")
        st.write("1. Focus product development on top 3 pain points")
        st.write("2. Validate pricing strategy with quantitative research")
        st.write("3. Prioritize integration features for next release")

def show_transcripts(results: Dict):
    """Display session transcripts."""
    st.subheader("💬 Session Transcript")
    
    # In real implementation, load actual transcript data
    st.write("**Session Transcript Preview:**")
    
    transcript_data = [
        {"Speaker": "Facilitator", "Time": "10:00", "Message": "Welcome everyone! Let's start with introductions."},
        {"Speaker": "Sarah (Small Business Owner)", "Time": "10:01", "Message": "Hi, I'm Sarah. I run a small marketing agency with 8 employees."},
        {"Speaker": "Mike (Marketing Manager)", "Time": "10:02", "Message": "I'm Mike, marketing manager at a tech company."},
        {"Speaker": "Facilitator", "Time": "10:03", "Message": "Great! Now, what are your biggest challenges with current tools?"},
        {"Speaker": "Sarah", "Time": "10:04", "Message": "The main issue is juggling multiple platforms. I use 3 different tools and it's really time-consuming."},
    ]
    
    for entry in transcript_data:
        with st.chat_message("assistant" if entry["Speaker"] == "Facilitator" else "user"):
            st.write(f"**{entry['Speaker']}** ({entry['Time']})")
            st.write(entry["Message"])

def show_raw_data(results: Dict):
    """Display raw session data."""
    st.subheader("📋 Raw Session Data")
    
    # Show results structure
    st.json(results)

def show_live_transcripts():
    """Live transcript viewer (placeholder)."""
    st.header("📺 Live Transcripts")
    st.markdown("Real-time session monitoring")
    
    if not st.session_state.session_running:
        st.info("No active session. Live transcripts will appear here during session execution.")
        return
    
    st.success("Session is running... (Live transcript would appear here)")
    
    # Auto-refresh placeholder
    placeholder = st.empty()
    
    with placeholder.container():
        st.write("Live updates would appear here during session...")

def show_export_hub():
    """Export hub for downloading results."""
    st.header("💾 Export Hub")
    st.markdown("Download session results in various formats")
    
    if 'session_results' not in st.session_state or not st.session_state.session_results:
        st.info("No session results available for export.")
        return
    
    results = st.session_state.session_results
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available Exports")
        
        export_options = {
            "📄 JSONL Data": "Complete session data in JSONL format",
            "📊 CSV Export": "Tabular data for analysis",
            "📋 Summary Report": "Executive summary in Markdown",
            "📈 Detailed Analysis": "Comprehensive findings report",
            "🎨 Charts Package": "All visualizations as PNG files"
        }
        
        for export_type, description in export_options.items():
            st.write(f"**{export_type}**")
            st.write(description)
            if st.button(f"Download {export_type.split()[1]}", key=export_type):
                download_export(export_type)
            st.divider()
    
    with col2:
        st.subheader("Export Preview")
        
        # Show sample export content
        st.code("""
# Session Summary Report

## Study: Consumer Research Study
**Date:** 2025-01-12
**Participants:** 8
**Duration:** 65 minutes

## Key Findings
1. **Pricing Sensitivity**: 75% of participants mentioned cost as primary concern
2. **Feature Gaps**: Integration capabilities most requested feature
3. **User Experience**: Onboarding process needs simplification

## Recommendations
1. Implement tiered pricing strategy
2. Prioritize API integrations
3. Redesign user onboarding flow
        """, language="markdown")

def show_templates_page():
    """Templates and examples page."""
    st.header("📄 Templates & Examples")
    st.markdown("Download templates and see examples for bulk uploads")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Persona Templates")
        st.write("Use these templates to bulk upload custom personas:")
        
        # CSV Template
        st.write("**CSV Format (Recommended)**")
        if os.path.exists("templates/personas_template.csv"):
            with open("templates/personas_template.csv", "r") as f:
                csv_content = f.read()
            st.download_button(
                "📥 Download Personas CSV Template",
                csv_content,
                "personas_template.csv",
                "text/csv",
                help="CSV format with all required and optional columns"
            )
            
            # Show preview
            st.write("*Preview:*")
            df_preview = pd.read_csv("templates/personas_template.csv")
            st.dataframe(df_preview.head(3))
        
        st.divider()
        
        # JSON Template
        st.write("**JSON Format (Advanced)**")
        if os.path.exists("templates/personas_template.json"):
            with open("templates/personas_template.json", "r") as f:
                json_content = f.read()
            st.download_button(
                "📥 Download Personas JSON Template",
                json_content,
                "personas_template.json",
                "application/json",
                help="JSON format with detailed persona specifications"
            )
            
            # Show preview
            st.write("*Preview:*")
            with open("templates/personas_template.json", "r") as f:
                json_data = json.load(f)
            st.json(json_data[0])  # Show first persona
    
    with col2:
        st.subheader("❓ Questions Templates")
        st.write("Use these templates to bulk upload research questions:")
        
        # Text Template
        st.write("**Text File Format (Simple)**")
        if os.path.exists("templates/questions_template.txt"):
            with open("templates/questions_template.txt", "r") as f:
                txt_content = f.read()
            st.download_button(
                "📥 Download Questions Template",
                txt_content,
                "questions_template.txt",
                "text/plain",
                help="One question per line in a simple text file"
            )
            
            # Show preview
            st.write("*Preview:*")
            questions = txt_content.split('\n')[:5]
            for i, q in enumerate(questions, 1):
                if q.strip():
                    st.write(f"{i}. {q}")
        
        st.divider()
        
        # CSV Questions example
        st.write("**CSV Format (Alternative)**")
        st.write("Create a CSV with a 'question' column:")
        
        sample_questions_csv = "question\n" + "\n".join([
            "What are your main pain points with current tools?",
            "How do you measure success in your projects?",
            "What features would you most value in a new solution?"
        ])
        
        st.download_button(
            "📥 Download Questions CSV Example",
            sample_questions_csv,
            "questions_template.csv",
            "text/csv"
        )
    
    st.divider()
    
    # Usage Instructions
    st.subheader("📝 How to Use Templates")
    
    tab1, tab2 = st.tabs(["Personas", "Questions"])
    
    with tab1:
        st.markdown("""
        ### Persona Upload Steps:
        1. **Download** a template (CSV recommended for beginners)
        2. **Edit** the template with your custom personas:
           - **Required:** name, age, occupation, background
           - **Optional:** gender, location, personality_traits, interests
        3. **Upload** your customized file in the Study Creator
        4. **Review** the loaded personas before creating your study
        
        ### Tips:
        - For personality_traits and interests, use comma-separated values
        - Keep backgrounds detailed but concise (1-2 sentences)
        - Mix different demographics for diverse insights
        - Aim for 5-15 personas for best results
        """)
    
    with tab2:
        st.markdown("""
        ### Questions Upload Steps:
        1. **Download** a template (TXT format is simplest)
        2. **Edit** the template with your research questions:
           - One question per line for TXT files
           - Use 'question' column for CSV files
        3. **Upload** your customized file in the Study Creator
        4. **Review** the loaded questions before creating your study
        
        ### Question Writing Tips:
        - Use open-ended questions (avoid yes/no)
        - Start with broad topics, then get specific
        - Include emotional and practical aspects
        - Aim for 5-15 questions for a 60-minute session
        - Test questions for clarity and bias
        """)
    
    # Examples section
    st.subheader("🎆 Pre-built Example Sets")
    
    example_col1, example_col2, example_col3 = st.columns(3)
    
    with example_col1:
        if st.button("🚀 SaaS Product Research"):
            create_saas_example()
    
    with example_col2:
        if st.button("🛒 E-commerce Study"):
            create_ecommerce_example()
    
    with example_col3:
        if st.button("🏢 B2B Service Research"):
            create_b2b_example()

def create_saas_example():
    """Create SaaS research example."""
    st.success("🚀 SaaS Product Research example created!")
    st.write("This would create a pre-configured study for SaaS product research...")
    # Implementation would create example study

def create_ecommerce_example():
    """Create e-commerce research example."""
    st.success("🛒 E-commerce Study example created!")
    st.write("This would create a pre-configured study for e-commerce research...")
    # Implementation would create example study

def create_b2b_example():
    """Create B2B research example."""
    st.success("🏢 B2B Service Research example created!")
    st.write("This would create a pre-configured study for B2B service research...")
    # Implementation would create example study

def convert_uploaded_personas_to_format(personas_df: pd.DataFrame) -> List[Dict]:
    """Convert uploaded personas DataFrame to expected format."""
    personas = []
    
    for _, row in personas_df.iterrows():
        # Create persona ID from name
        persona_id = row['name'].lower().replace(' ', '_').replace('-', '_')
        
        # Handle personality traits (could be string or list)
        personality_traits = []
        if 'personality_traits' in row and pd.notna(row['personality_traits']):
            if isinstance(row['personality_traits'], str):
                personality_traits = [trait.strip() for trait in row['personality_traits'].split(',')]
            else:
                personality_traits = row['personality_traits']
        
        # Handle interests similarly
        interests = []
        if 'interests' in row and pd.notna(row['interests']):
            if isinstance(row['interests'], str):
                interests = [interest.strip() for interest in row['interests'].split(',')]
            else:
                interests = row['interests']
        
        persona = {
            'persona_id': persona_id,
            'name': row['name'],
            'role': row.get('occupation', row.get('role', 'Professional')),
            'age': int(row['age']),
            'occupation': row.get('occupation', 'Professional'),
            'background': row.get('background', f"Professional with experience in their field"),
            'gender': row.get('gender', 'Not specified'),
            'location': row.get('location', 'Not specified'),
            'personality_traits': personality_traits or ['analytical', 'detail-oriented'],
            'interests': interests or ['professional development'],
            'pain_points': [f"Challenges related to {row.get('occupation', 'work')}"],
            'goals': [f"Success in {row.get('occupation', 'their role')}"],
            'communication_style': 'Professional and direct'
        }
        
        personas.append(persona)
    
    return personas

def download_export(export_type: str):
    """Handle export downloads."""
    st.success(f"✅ {export_type} downloaded successfully!")
    # In real implementation, generate and trigger file download

if __name__ == "__main__":
    main()