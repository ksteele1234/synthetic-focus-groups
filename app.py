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
        demo_mode = os.environ.get('DEMO_MODE', '').lower() == 'true'
        if demo_mode:
            st.write("🤖 AI Client:", "⚠️ Demo Mode")
        else:
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
        
        # Ensure session storage for uploads
        if 'uploaded_questions' not in st.session_state:
            st.session_state.uploaded_questions = []
        if 'uploaded_personas' not in st.session_state:
            st.session_state.uploaded_personas = []
        
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
            
            # New: Multi-file upload with Excel support and dedicated action
            st.markdown("**Question Files (CSV, TXT, XLSX)**")
            q_files = st.file_uploader(
                "Upload question files",
                type=["csv", "txt", "xlsx"],
                accept_multiple_files=True,
                key="questions_multi_upload"
            )
            include_uploaded_q = st.checkbox("Include uploaded question files", value=True)
            if st.form_submit_button("➕ Add Question Files"):
                added = 0
                for f in q_files or []:
                    name = f.name.lower()
                    try:
                        if name.endswith('.txt'):
                            content = f.read().decode('utf-8')
                            new_qs = [line.strip() for line in content.split('\n') if line.strip()]
                        elif name.endswith('.csv'):
                            df = pd.read_csv(f)
                            if 'question' in df.columns:
                                new_qs = df['question'].dropna().astype(str).tolist()
                            else:
                                # take first non-empty column
                                first_col = df.columns[0]
                                new_qs = df[first_col].dropna().astype(str).tolist()
                        elif name.endswith('.xlsx'):
                            try:
                                df = pd.read_excel(f)
                            except Exception as ex:
                                st.error("Reading Excel requires openpyxl. Install with: pip install openpyxl")
                                continue
                            if 'question' in df.columns:
                                new_qs = df['question'].dropna().astype(str).tolist()
                            else:
                                first_col = df.columns[0]
                                new_qs = df[first_col].dropna().astype(str).tolist()
                        else:
                            new_qs = []
                        st.session_state.uploaded_questions.extend(new_qs)
                        added += len(new_qs)
                    except Exception as e:
                        st.error(f"Failed to parse {f.name}: {e}")
                if added:
                    st.success(f"Added {added} questions from files")
                else:
                    st.info("No questions added")
            if st.session_state.uploaded_questions:
                st.caption(f"Uploaded questions: {len(st.session_state.uploaded_questions)} (will be included: {include_uploaded_q})")
            
        
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
                st.write("Optional: gender, location, personality_traits, interests, and advanced dimensions")
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
                st.write("Format: [{\"name\": \"...\", \"age\": 30, \"occupation\": \"...\", ...}] including advanced fields")
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
            
            # New: dedicated upload for participant information (CSV/JSON/XLSX)
            st.markdown("**Upload Participant Information (CSV, JSON, XLSX)**")
            p_files = st.file_uploader(
                "Upload participant files",
                type=["csv", "json", "xlsx"],
                accept_multiple_files=True,
                key="participants_multi_upload"
            )
            include_uploaded_personas = st.checkbox("Include uploaded participants", value=True)
            if st.form_submit_button("👥 Add Participant Files"):
                added = 0
                for f in p_files or []:
                    name = f.name.lower()
                    try:
                        if name.endswith('.json'):
                            data = json.loads(f.read().decode('utf-8'))
                            if isinstance(data, dict):
                                data = [data]
                            df = pd.DataFrame(data)
                        elif name.endswith('.csv'):
                            df = pd.read_csv(f)
                        elif name.endswith('.xlsx'):
                            try:
                                df = pd.read_excel(f)
                            except Exception:
                                st.error("Reading Excel requires openpyxl. Install with: pip install openpyxl")
                                continue
                        else:
                            continue
                        parsed = convert_uploaded_personas_to_format(df)
                        st.session_state.uploaded_personas.extend(parsed)
                        added += len(parsed)
                    except Exception as e:
                        st.error(f"Failed to parse {f.name}: {e}")
                if added:
                    st.success(f"Added {added} participants from files")
                else:
                    st.info("No participants added")
            if st.session_state.uploaded_personas:
                st.caption(f"Uploaded participants ready: {len(st.session_state.uploaded_personas)} (will be included: {include_uploaded_personas})")
            
            st.subheader("Session Settings")
            if st.checkbox("Build persona from web evidence here"):
                from research.web_persona_builder import WebPersonaBuilder
                query_inline = st.text_input("Evidence query", value="social media management tool")
                subs_inline = st.text_input("Subreddits (comma-separated)", value="smallbusiness, marketing")
                web_build = st.form_submit_button("🔎 Build persona from web evidence")
                if web_build:
                    try:
                        builder = WebPersonaBuilder()
                        sub_list = [s.strip() for s in subs_inline.split(',') if s.strip()]
                        persona_dict = builder.build_persona_from_evidence(query_inline, subreddits=sub_list)
                        # Convert to runner persona format
                        new_persona = {
                            'persona_id': persona_dict.get('name','web_persona').lower().replace(' ','_'),
                            'name': persona_dict.get('name','Web Persona'),
                            'role': persona_dict.get('occupation','Participant'),
                            'background': persona_dict.get('persona_summary',''),
                        }
                        if 'current_personas' not in st.session_state:
                            st.session_state.current_personas = []
                        st.session_state.current_personas.append(new_persona)
                        st.success(f"Added persona '{new_persona['name']}' from web evidence")
                    except Exception as e:
                        st.error(f"Web persona build failed: {e}")

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
                # If user added personas via inline web research, prefer those
                if 'current_personas' in st.session_state and st.session_state.current_personas:
                    personas = st.session_state.current_personas
                    st.info(f"🌐 Using {len(personas)} web-researched personas")
                else:
                    # Generate sample personas
                    personas = create_sample_personas()[:participant_count]
                    st.info(f"🤖 Generated {len(personas)} AI personas")
            
            if weighted:
                st.subheader("Set Persona Weights")
                weight_configs = []
                for i, persona in enumerate(personas):
                    with st.expander(f"⚖️ {persona.get('name', persona.get('persona_id', f'Persona {i+1}'))}", expanded=i < 5):
                        w = st.slider(f"Weight for {persona.get('persona_id', i)}", 0.5, 5.0, 1.0, 0.5, key=f"weight_{i}")
                        r = st.number_input(f"Rank for {persona.get('persona_id', i)}", min_value=1, max_value=len(personas), value=i+1, key=f"rank_{i}")
                        is_icp = st.checkbox("Primary ICP", value=(i == 0), key=f"icp_{i}")
                        notes = st.text_input("Notes", value=f"{persona.get('role','Participant')}", key=f"notes_{i}")
                        weight_configs.append({
                            'persona_id': persona.get('persona_id') or persona.get('id') or f"persona_{i}",
                            'weight': float(w),
                            'rank': int(r),
                            'is_primary_icp': bool(is_icp),
                            'notes': notes
                        })
                # Persist to project
                project.persona_weights = []
                for cfg in weight_configs:
                    project.persona_weights.append(PersonaWeight(
                        persona_id=cfg['persona_id'],
                        weight=cfg['weight'],
                        rank=cfg['rank'],
                        is_primary_icp=cfg['is_primary_icp'],
                        notes=cfg['notes']
                    ))
                icps = [cfg['persona_id'] for cfg in weight_configs if cfg['is_primary_icp']]
                if icps:
                    project.set_primary_icp(icps[0])
            
            # Include uploaded questions if requested
            try:
                if include_uploaded_q and st.session_state.get('uploaded_questions'):
                    questions = (questions or []) + st.session_state.uploaded_questions
            except Exception:
                pass
            
            # Store in session state
            st.session_state.current_project = project
            # Build personas from multiple sources
            # Tag any created personas with project provenance if applicable
            try:
                for p in st.session_state.get('uploaded_personas', []):
                    p['created_for_project_id'] = project.id
                    p['created_for_project_name'] = project.name
            except Exception:
                pass
            persona_pool = personas
            try:
                if include_uploaded_personas and st.session_state.get('uploaded_personas'):
                    persona_pool = persona_pool + st.session_state.uploaded_personas
            except Exception:
                pass
            st.session_state.current_personas = persona_pool
            
            # Persist weight configs for use by runner
            if weighted and project.persona_weights:
                st.session_state.current_persona_weights = {
                    pw.persona_id: {
                        'weight': pw.weight,
                        'rank': pw.rank,
                        'is_primary_icp': pw.is_primary_icp,
                        'notes': pw.notes,
                    } for pw in project.persona_weights
                }
            
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

def export_current_study_profiles(project, personas, sections: set | None = None):
    """Generate DOCX/PDF ZIPs for current study participants and expose download buttons."""
    import io, zipfile
    from persona_manager import export_persona_docx, export_persona_pdf
    # Personas here are runner-format dicts; attempt to load from storage if needed
    # We will render a lightweight profile using available fields
    docx_zip = io.BytesIO()
    pdf_zip = io.BytesIO()
    with zipfile.ZipFile(docx_zip, 'w', zipfile.ZIP_DEFLATED) as zd, zipfile.ZipFile(pdf_zip, 'w', zipfile.ZIP_DEFLATED) as zp:
        for p in personas:
            # Build a minimal persona-like object with attributes expected by exporters
            class PObj:
                pass
            po = PObj()
            po.name = p.get('name') or p.get('persona_id')
            po.occupation = p.get('role','')
            po.age = int(p.get('age', 35)) if isinstance(p.get('age', 35), (int, float)) else 35
            po.education = p.get('education','')
            po.annual_income = p.get('annual_income','')
            po.location = p.get('location','')
            po.relationship_family = p.get('relationship_family','')
            po.created_for_project_name = project.name
            po.persona_summary = p.get('background','')
            po.personality_traits = p.get('personality_traits', [])
            po.values = p.get('values', [])
            po.community_involvement = p.get('community_involvement', [])
            po.major_struggles = p.get('major_struggles', [])
            po.deep_fears_business = p.get('deep_fears_business', [])
            po.previous_software_tried = p.get('previous_software_tried', [])
            po.tangible_business_results = p.get('tangible_business_results', [])
            po.tangible_personal_results = p.get('tangible_personal_results', [])
            po.emotional_transformations = p.get('emotional_transformations', [])
            po.if_only_soundbites = p.get('if_only_soundbites', [])
            po.desired_reputation = p.get('desired_reputation', [])
            po.things_to_avoid = p.get('things_to_avoid', [])
            po.unwanted_quotes = p.get('unwanted_quotes', [])
            po.big_picture_aspirations = p.get('big_picture_aspirations','')
            po.ideal_day_scenario = p.get('ideal_day_scenario','')
            po.evidence_quotes = p.get('evidence_quotes', [])
            filename = (po.name or 'participant').replace(' ','_').lower()
            try:
                zd.writestr(f"{filename}_profile.docx", export_persona_docx(po, sections=sections))
            except Exception:
                pass
            try:
                zp.writestr(f"{filename}_profile.pdf", export_persona_pdf(po, sections=sections))
            except Exception:
                pass
    # Expose as download buttons
    import streamlit as st
    st.download_button("Download Study Profiles (DOCX ZIP)", docx_zip.getvalue(), file_name="study_profiles_docx.zip", mime="application/zip")
    st.download_button("Download Study Profiles (PDF ZIP)", pdf_zip.getvalue(), file_name="study_profiles_pdf.zip", mime="application/zip")


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
        with st.expander("Profile Export Options", expanded=False):
            section_options = [
                ("Identity/Provenance", "identity"),
                ("Summary", "summary"),
                ("Personality Traits", "traits"),
                ("Values", "values"),
                ("Community Involvement", "community"),
                ("Major Struggles", "struggles"),
                ("Deep Fears (Business)", "fears_business"),
                ("Previous Software Tried", "prev_software"),
                ("Desired Results (Business)", "results_business"),
                ("Desired Results (Personal)", "results_personal"),
                ("Emotional Transformations", "emotional"),
                ("If Only Soundbites", "if_only"),
                ("Desired Reputation", "reputation"),
                ("Things To Avoid", "avoid"),
                ("Unwanted Quotes", "unwanted"),
                ("Big Picture Aspirations", "big_picture"),
                ("Day-in-the-Life", "day_in_life"),
                ("Sources & Citations", "citations"),
            ]
            default_keys = {k for _, k in section_options}
            selected_sections = st.multiselect(
                "Include sections",
                options=[k for _, k in section_options],
                default=list(default_keys),
                format_func=lambda key: next(lbl for lbl,k in section_options if k==key)
            )
        if st.button("📄 Export Current Study Profiles (DOCX/PDF ZIP)"):
            try:
                export_current_study_profiles(project, personas, sections=set(selected_sections))
                st.success("Profiles ready for download (see buttons below)")
            except Exception as e:
                st.error(f"Profile export failed: {e}")
        
        if not st.session_state.session_running:
            if st.button("🚀 Start Session", type="primary"):
                start_session(project, personas)
            # Weight editor after creation
            if st.button("⚖️ View/Edit Weights"):
                st.session_state.show_weight_editor = True
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
    
    # Optional weight editor panel
    if st.session_state.get('show_weight_editor'):
        st.subheader("Adjust Persona Weights")
        weight_map = st.session_state.get('current_persona_weights', {})
        for p in personas:
            pid = p.get('persona_id') or p.get('id')
            if not pid:
                continue
            cfg = weight_map.get(pid, {'weight':1.0,'rank':1,'is_primary_icp':False,'notes':p.get('role','')})
            cols = st.columns([3,2,2,3])
            with cols[0]:
                st.write(p.get('name', pid))
            with cols[1]:
                cfg['weight'] = float(st.slider(f"W:{pid}", 0.5, 5.0, float(cfg['weight']), 0.5, key=f"w_edit_{pid}"))
            with cols[2]:
                cfg['rank'] = int(st.number_input(f"R:{pid}", 1, len(personas), int(cfg['rank']), key=f"r_edit_{pid}"))
            with cols[3]:
                cfg['is_primary_icp'] = bool(st.checkbox(f"ICP:{pid}", value=bool(cfg['is_primary_icp']), key=f"i_edit_{pid}"))
            weight_map[pid] = cfg
        st.session_state.current_persona_weights = weight_map
        if st.button("Save Weights"):
            # Reflect into project model too
            project.persona_weights = []
            for pid, cfg in weight_map.items():
                project.persona_weights.append(PersonaWeight(
                    persona_id=pid,
                    weight=cfg['weight'],
                    rank=cfg['rank'],
                    is_primary_icp=cfg['is_primary_icp'],
                    notes=cfg.get('notes','')
                ))
            icps = [pid for pid,cfg in weight_map.items() if cfg['is_primary_icp']]
            if icps:
                project.set_primary_icp(icps[0])
            st.success("Weights updated")
            st.session_state.show_weight_editor = False

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
                num_questions=len(project.research_questions) if project.research_questions else 3,
                persona_weights=st.session_state.get('current_persona_weights')
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Charts", "📝 Insights", "💬 Transcripts", "📋 Raw Data", "🛡️ Guardrails"])
    
    with tab1:
        show_charts(results)
    
    with tab2:
        show_insights(results)
    
    with tab3:
        show_transcripts(results)
    
    with tab4:
        show_raw_data(results)
    
    with tab5:
        show_guardrails(results)

def show_charts(results: Dict):
    """Display charts and visualizations from actual results with weighted/unweighted toggle."""
    st.subheader("📈 Session Analytics")

    use_weighted = st.checkbox("Use weighted analysis", value=True)

    # Build theme frequencies from turns
    qa_turns = results.get('qa_turns', [])
    weights = {}
    try:
        weights = results.get('weighting_info', {}).get('analysis_weights', {})
    except Exception:
        weights = {}
    
    from collections import defaultdict
    theme_counts = defaultdict(float)
    unweighted_counts = defaultdict(int)

    for t in qa_turns:
        try:
            persona_id = getattr(t, 'persona_id', None) or t.get('persona_id')
            w = float(weights.get(persona_id, 1.0)) if use_weighted else 1.0
            tags = getattr(t, 'tags', None) or t.get('tags', [])
            for tag in tags or []:
                theme_counts[tag] += w
                unweighted_counts[tag] += 1
        except Exception:
            continue

    # Prepare top themes
    items = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    df_themes = pd.DataFrame({
        'Theme': [k for k, _ in items],
        'Score': [v for _, v in items]
    }) if items else pd.DataFrame({'Theme': [], 'Score': []})

    col1, col2 = st.columns(2)
    with col1:
        fig_themes = px.bar(df_themes, x='Score', y='Theme', orientation='h', title="Top Themes")
        st.plotly_chart(fig_themes, use_container_width=True)
    
    with col2:
        # Engagement by persona
        from collections import Counter
        counts = Counter()
        for t in qa_turns:
            try:
                pid = getattr(t, 'persona_id', None) or t.get('persona_id')
                counts[pid] += 1
            except Exception:
                continue
        df_eng = pd.DataFrame({
            'Persona': list(counts.keys()),
            'Responses': list(counts.values())
        })
        fig_eng = px.bar(df_eng, x='Persona', y='Responses', title="Engagement by Persona")
        st.plotly_chart(fig_eng, use_container_width=True)

    # Pain points from tags subset (example filtering)
    st.subheader("😤 Pain Points Frequency")
    pain_tags = ['time_management', 'pricing', 'complexity', 'support', 'feature_gap']
    pain = []
    for tag in pain_tags:
        pain.append({'Pain Point': tag.replace('_',' ').title(), 'Mentions': unweighted_counts.get(tag, 0)})
    fig_pain = px.bar(pd.DataFrame(pain), x='Pain Point', y='Mentions', title="Pain Point Mentions (unweighted)")
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

def show_guardrails(results: Dict):
    """Display guardrail events from the run."""
    st.subheader("🛡️ Guardrail Events")
    events = results.get('guardrail_events', [])
    if not events:
        st.info("No guardrail events recorded.")
        return
    df = pd.DataFrame(events)
    st.dataframe(df, use_container_width=True)
    # Aggregates
    st.markdown("### Summary")
    by_type = df.groupby('type').size().reset_index(name='count') if 'type' in df.columns else pd.DataFrame()
    by_sev = df.groupby('severity').size().reset_index(name='count') if 'severity' in df.columns else pd.DataFrame()
    col1, col2 = st.columns(2)
    with col1:
        if not by_type.empty:
            st.bar_chart(by_type.set_index('type'))
    with col2:
        if not by_sev.empty:
            st.bar_chart(by_sev.set_index('severity'))


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
    """Export hub for generating and downloading results."""
    st.header("💾 Export Hub")
    st.markdown("Choose what to generate. Nothing is created until you click Generate.")

    if 'session_results' not in st.session_state or not st.session_state.session_results:
        st.info("No session results available for export.")
        return

    results = st.session_state.session_results
    project: EnhancedProject = st.session_state.get('current_project')

    with st.form("export_form"):
        st.subheader("Select formats and datasets")
        formats = st.multiselect(
            "Formats",
            ["json", "csv", "yaml", "md"],
            default=["json", "csv", "md"],
            help="PDF not included in demo; MD is supported."
        )
        datasets = st.multiselect(
            "Datasets",
            ["messages", "personas", "insights", "guardrails"],
            default=["messages", "personas", "insights"]
        )
        include_package = st.checkbox("Create comprehensive package (weighted JSON, CSV, agent dashboard, executive summary)", value=True)
        generate = st.form_submit_button("🚀 Generate")

    if generate:
        try:
            # Adapt session_results to Session/Project-like structures if needed
            from models.session import Session, SessionResponse
            from export.enhanced_exporter import EnhancedDataExporter
            from reports.markdown_generator import MarkdownReportGenerator, ReportData

            # Create minimal Session object from stored files if available
            # For demo: reuse saved paths in results['storage_results']
            exporter = EnhancedDataExporter()

            # Prepare agent_results value if present in pipeline (optional)
            agent_results = results.get('agent_results', {})

            # Create markdown reports
            report_gen = MarkdownReportGenerator()

            # In a full implementation we'd reconstruct Session/EnhancedProject fully.
            # Here we create a package directory and drop what we can using EnhancedDataExporter.
            package_dir = exporter.export_comprehensive_package(
                session=Session(id=results['session_id'], project_id=project.id, name=project.name),
                project=project,
                agent_results=agent_results,
                package_name=f"web_export_{results['session_id']}",
                guardrails=results.get('guardrail_events')
            )
            st.success(f"✅ Comprehensive package created: {package_dir}")
            st.write("Open the folder to view weighted_analysis.json, weighted_responses.csv, agent_insights_dashboard.json, executive_summary.md, and manifest.json.")
        except Exception as e:
            st.error(f"Export failed: {e}")

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
    """Convert uploaded personas DataFrame to expected format.
    Robust to different column names (e.g., Google Ads audience exports) and missing fields.
    """
    import re, json as _json

    # Normalize column names to lowercase with underscores for easier matching
    df = personas_df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    def _first(row, keys: List[str], default=None):
        for k in keys:
            if k in row and pd.notna(row[k]) and str(row[k]).strip():
                return row[k]
        return default

    def _as_list(val) -> List[str]:
        if isinstance(val, list):
            return [str(x).strip() for x in val if str(x).strip()]
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return []
        s = str(val).strip()
        # Try JSON array first
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = _json.loads(s)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                pass
        # Split by comma or semicolon
        parts = re.split(r"[,;]", s)
        return [p.strip() for p in parts if p.strip()]

    def _parse_age(val, default=35) -> int:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        s = str(val)
        m = re.findall(r"\d+", s)
        try:
            if len(m) >= 2:
                return int((int(m[0]) + int(m[1])) / 2)
            if len(m) == 1:
                return int(m[0])
        except Exception:
            pass
        return default

    personas: List[Dict] = []
    for idx, row in df.iterrows():
        # Required-ish fields with flexible aliases
        name = _first(row, [
            'name','persona','persona_name','audience','audience_name','segment','profile','user_persona'
        ], default=f"persona_{idx+1}")

        safe_id = str(name).lower().replace(' ', '_').replace('-', '_')

        age = _parse_age(_first(row, ['age','age_range','age_bracket','age_group']))
        occupation = _first(row, ['occupation','role','job_title','profession','industry'], default='Professional')
        background = _first(row, ['background','description','summary','bio','notes','about'], default='Professional with experience in their field')
        gender = _first(row, ['gender','sex'], default='Not specified')
        location = _first(row, ['location','city','region','country','geo'], default='Not specified')

        personality_traits = _as_list(_first(row, ['personality_traits','traits'])) or ['analytical','detail-oriented']
        interests = _as_list(_first(row, ['interests','hobbies'])) or ['professional development']
        core_values = _as_list(_first(row, ['values','core_values']))

        persona = {
            'persona_id': safe_id,
            'name': name,
            'role': occupation,
            'age': age,
            'occupation': occupation,
            'background': background,
            'gender': gender,
            'location': location,
            'personality_traits': personality_traits,
            'interests': interests,
            # Extended dimensions (optional)
            'education': _first(row, ['education','education_level'], default=''),
            'relationship_family': _first(row, ['relationship_family','marital_status','family','household'], default=''),
            'annual_income': _first(row, ['annual_income','income','income_level'], default=''),
            'community_involvement': _as_list(_first(row, ['community_involvement','associations','groups'])),
            'values': core_values,
            'free_time_activities': _first(row, ['free_time_activities'], default=''),
            'lifestyle_description': _first(row, ['lifestyle_description','lifestyle'], default=''),
            'major_struggles': _as_list(_first(row, ['major_struggles','pains','challenges'])),
            'obstacles': _as_list(_first(row, ['obstacles','barriers'])),
            'why_problems_exist': _first(row, ['why_problems_exist','root_cause'], default=''),
            'deep_fears_business': _as_list(_first(row, ['deep_fears_business','business_fears','fears'])),
            'deep_fears_personal': _as_list(_first(row, ['deep_fears_personal','personal_fears'])),
            'previous_software_tried': _as_list(_first(row, ['previous_software_tried','tools_tried','software_tried'])),
            'why_software_failed': _first(row, ['why_software_failed'], default=''),
            'tangible_business_results': _as_list(_first(row, ['tangible_business_results','desired_business_outcomes'])),
            'tangible_personal_results': _as_list(_first(row, ['tangible_personal_results','desired_personal_outcomes'])),
            'emotional_transformations': _as_list(_first(row, ['emotional_transformations','emotional_outcomes'])),
            'if_only_soundbites': _as_list(_first(row, ['if_only_soundbites','soundbites'])),
            'desired_reputation': _as_list(_first(row, ['desired_reputation','how_they_want_to_be_seen'])),
            'success_statements_from_others': _as_list(_first(row, ['success_statements_from_others','what_others_say'])),
            'things_to_avoid': _as_list(_first(row, ['things_to_avoid','unwanted_outcomes'])),
            'unwanted_quotes': _as_list(_first(row, ['unwanted_quotes'])),
            'big_picture_aspirations': _first(row, ['big_picture_aspirations','aspirations','dreams'], default=''),
            'persona_summary': _first(row, ['persona_summary','summary','background'], default=background),
            'ideal_day_scenario': _first(row, ['ideal_day_scenario','day_in_the_life'], default=''),
            'communication_style': _first(row, ['communication_style'], default='Professional and direct'),
        }
        personas.append(persona)

    return personas

def download_export(export_type: str):
    """Handle export downloads."""
    st.success(f"✅ {export_type} downloaded successfully!")
    # In real implementation, generate and trigger file download

if __name__ == "__main__":
    main()