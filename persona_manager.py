#!/usr/bin/env python3
"""
Streamlit Web App for Synthetic Focus Groups - Enhanced Persona UI
This component adds detailed persona profile management to the web app.
"""

import streamlit as st
import pandas as pd
import json
import sys
import os
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import persona-related components
from models.persona import Persona

def show_detailed_persona_manager():
    """
    Persona Manager interface for creating, editing, and viewing detailed personas.
    """
    st.header("👤 Detailed Persona Manager")
    st.markdown("Create and manage comprehensive buyer personas for your synthetic focus groups")
    
    tab1, tab2, tab3 = st.tabs(["Create New Persona", "View & Edit Personas", "Import/Export"])
    
    with tab1:
        show_persona_creator()
    
    with tab2:
        show_persona_editor()
    
    with tab3:
        show_persona_import_export()

def show_persona_creator():
    """Interface for creating a new detailed persona from scratch."""
    st.subheader("🆕 Create New Detailed Persona")
    
    # Persona data dictionary to collect all fields
    persona_data = {}
    
    # Create expandable sections for each category of persona details
    with st.expander("1️⃣ Buyer Avatar Basics", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            persona_data["name"] = st.text_input("Full Name", key="new_name", 
                                               help="The persona's full name")
            persona_data["age"] = st.number_input("Age", min_value=18, max_value=80, value=35, key="new_age")
            persona_data["gender"] = st.selectbox("Gender", 
                                                ["Male", "Female", "Non-binary", "Prefer not to specify"], 
                                                key="new_gender")
            persona_data["education"] = st.text_input("Education", key="new_education",
                                                   help="Highest level of education and relevant certifications")
        
        with col2:
            persona_data["relationship_family"] = st.text_area("Relationship & Family Status", key="new_family",
                                                          height=80, help="Marital status, children, family dynamics")
            persona_data["occupation"] = st.text_input("Occupation", key="new_occupation",
                                                    help="Current job title and type of company")
            persona_data["annual_income"] = st.text_input("Annual Income", key="new_income",
                                                       help="Income range or specific amount (include goals if relevant)")
            persona_data["location"] = st.text_input("Location", key="new_location",
                                                  help="City, state/province, country")
    
    with st.expander("2️⃣ Psychographics & Lifestyle", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            hobbies = st.text_area("Hobbies & Interests", key="new_hobbies", height=100,
                                help="List multiple hobbies separated by commas")
            persona_data["hobbies"] = [hobby.strip() for hobby in hobbies.split(",")] if hobbies else []
            
            community = st.text_area("Community Involvement", key="new_community", height=100,
                                   help="Groups, associations, volunteer work")
            persona_data["community_involvement"] = [item.strip() for item in community.split(",")] if community else []
        
        with col2:
            traits = st.text_area("Personality Traits", key="new_traits", height=100,
                               help="Key personality characteristics, separated by commas")
            persona_data["personality_traits"] = [trait.strip() for trait in traits.split(",")] if traits else []
            
            values = st.text_area("Core Values", key="new_values", height=100,
                               help="Guiding principles and beliefs, separated by commas")
            persona_data["values"] = [value.strip() for value in values.split(",")] if values else []
        
        persona_data["free_time_activities"] = st.text_area("Free Time Activities", key="new_free_time", height=80,
                                                       help="How they spend their time outside of work")
        persona_data["lifestyle_description"] = st.text_area("Lifestyle Description", key="new_lifestyle", height=100,
                                                        help="General overview of their day-to-day lifestyle")
    
    with st.expander("3️⃣ Pains & Challenges", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            struggles = st.text_area("Major Struggles", key="new_struggles", height=150,
                                  help="List the biggest challenges they face, one per line")
            persona_data["major_struggles"] = [struggle.strip() for struggle in struggles.split("\n") if struggle.strip()]
        
        with col2:
            obstacles = st.text_area("Obstacles", key="new_obstacles", height=150,
                                  help="List specific barriers they encounter, one per line")
            persona_data["obstacles"] = [obstacle.strip() for obstacle in obstacles.split("\n") if obstacle.strip()]
        
        persona_data["why_problems_exist"] = st.text_area("Why These Problems Exist", key="new_why_problems", height=100,
                                                     help="Root causes of their challenges and struggles")
    
    with st.expander("4️⃣ Fears & Relationship Impact", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            business_fears = st.text_area("Deep Business Fears", key="new_biz_fears", height=150,
                                       help="List their worst business-related fears, one per line")
            persona_data["deep_fears_business"] = [fear.strip() for fear in business_fears.split("\n") if fear.strip()]
            
            personal_fears = st.text_area("Deep Personal Fears", key="new_personal_fears", height=150,
                                       help="List their worst personal fears, one per line")
            persona_data["deep_fears_personal"] = [fear.strip() for fear in personal_fears.split("\n") if fear.strip()]
        
        with col2:
            persona_data["fear_impact_spouse"] = st.text_area("Impact on Spouse/Partner", key="new_spouse_impact", height=80)
            persona_data["fear_impact_kids"] = st.text_area("Impact on Children", key="new_kids_impact", height=80)
            persona_data["fear_impact_employees"] = st.text_area("Impact on Employees/Team", key="new_employee_impact", height=80)
            persona_data["fear_impact_clients"] = st.text_area("Impact on Clients/Customers", key="new_client_impact", height=80)
            
        remarks = st.text_area("Potential Remarks from Others", key="new_remarks", height=100,
                            help="What others might say about them, one per line")
        persona_data["potential_remarks_from_others"] = [remark.strip() for remark in remarks.split("\n") if remark.strip()]
    
    with st.expander("5️⃣ Previous Attempts & Frustrations", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            agencies = st.text_area("Previous Agencies/Consultants Tried", key="new_agencies", height=80,
                                 help="List separated by commas")
            persona_data["previous_agencies_tried"] = [agency.strip() for agency in agencies.split(",")] if agencies else []
            
            software = st.text_area("Previous Software/Tools Tried", key="new_software", height=80,
                                 help="List separated by commas")
            persona_data["previous_software_tried"] = [tool.strip() for tool in software.split(",")] if software else []
            
            diy = st.text_area("DIY Approaches Tried", key="new_diy", height=80,
                            help="List separated by commas")
            persona_data["diy_approaches_tried"] = [approach.strip() for approach in diy.split(",")] if diy else []
        
        with col2:
            persona_data["why_agencies_failed"] = st.text_area("Why Agencies/Consultants Failed", key="new_why_agencies", height=80)
            persona_data["why_software_failed"] = st.text_area("Why Software/Tools Failed", key="new_why_software", height=80)
            persona_data["why_diy_failed"] = st.text_area("Why DIY Approaches Failed", key="new_why_diy", height=80)
    
    with st.expander("6️⃣ Desired Outcomes", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            biz_results = st.text_area("Tangible Business Results Wanted", key="new_biz_results", height=150,
                                    help="List specific measurable outcomes, one per line")
            persona_data["tangible_business_results"] = [result.strip() for result in biz_results.split("\n") if result.strip()]
            
            personal_results = st.text_area("Tangible Personal Results Wanted", key="new_personal_results", height=150,
                                         help="List specific personal outcomes, one per line")
            persona_data["tangible_personal_results"] = [result.strip() for result in personal_results.split("\n") if result.strip()]
        
        with col2:
            emotional = st.text_area("Emotional Transformations Desired", key="new_emotional", height=150,
                                  help="How they want to feel differently, one per line")
            persona_data["emotional_transformations"] = [trans.strip() for trans in emotional.split("\n") if trans.strip()]
            
            soundbites = st.text_area("'If Only' Soundbites", key="new_soundbites", height=150,
                                   help="Statements starting with 'If only I could...', one per line")
            persona_data["if_only_soundbites"] = [bite.strip() for bite in soundbites.split("\n") if bite.strip()]
    
    with st.expander("7️⃣ Hopes & Dreams", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            recognition = st.text_area("Professional Recognition Goals", key="new_recognition", height=100,
                                    help="List desired accolades and recognition, one per line")
            persona_data["professional_recognition_goals"] = [goal.strip() for goal in recognition.split("\n") if goal.strip()]
            
            financial = st.text_area("Financial Freedom Goals", key="new_financial", height=100,
                                  help="List financial objectives, one per line")
            persona_data["financial_freedom_goals"] = [goal.strip() for goal in financial.split("\n") if goal.strip()]
        
        with col2:
            lifestyle = st.text_area("Lifestyle Upgrade Goals", key="new_lifestyle_goals", height=100,
                                  help="List desired lifestyle improvements, one per line")
            persona_data["lifestyle_upgrade_goals"] = [goal.strip() for goal in lifestyle.split("\n") if goal.strip()]
            
            legacy = st.text_area("Family/Legacy Goals", key="new_legacy", height=100,
                               help="List long-term legacy objectives, one per line")
            persona_data["family_legacy_goals"] = [goal.strip() for goal in legacy.split("\n") if goal.strip()]
        
        persona_data["big_picture_aspirations"] = st.text_area("Big Picture Aspirations", key="new_big_picture", height=100,
                                                          help="Overall life and career aspirations")
    
    with st.expander("8️⃣ How They Want to Be Seen by Others", expanded=False):
        reputation = st.text_area("Desired Reputation", key="new_reputation", height=100,
                               help="How they want to be perceived by others, one per line")
        persona_data["desired_reputation"] = [rep.strip() for rep in reputation.split("\n") if rep.strip()]
        
        statements = st.text_area("Success Statements from Others", key="new_statements", height=100,
                               help="What they want others to say about them, one per line")
        persona_data["success_statements_from_others"] = [statement.strip() for statement in statements.split("\n") if statement.strip()]
    
    with st.expander("9️⃣ Unwanted Outcomes", expanded=False):
        avoid = st.text_area("Things to Avoid", key="new_avoid", height=100,
                          help="What they specifically want to avoid, one per line")
        persona_data["things_to_avoid"] = [thing.strip() for thing in avoid.split("\n") if thing.strip()]
        
        unwanted = st.text_area("Unwanted Quotes", key="new_unwanted", height=100,
                             help="Things they never want to hear, one per line")
        persona_data["unwanted_quotes"] = [quote.strip() for quote in unwanted.split("\n") if quote.strip()]
    
    with st.expander("🔟 Summary", expanded=False):
        persona_data["persona_summary"] = st.text_area("One-Paragraph Persona Summary", key="new_summary", height=150,
                                                   help="Concise overview of the entire persona in one paragraph")
    
    with st.expander("1️⃣1️⃣ Day-in-the-Life Scenario", expanded=False):
        persona_data["ideal_day_scenario"] = st.text_area("Ideal Day Scenario", key="new_ideal_day", height=300,
                                                      help="Detailed hour-by-hour description of their ideal day")
    
    # Submit button
    if st.button("💾 Save New Persona", type="primary"):
        if persona_data["name"]:
            save_persona(persona_data)
            st.success(f"✅ Persona '{persona_data['name']}' created successfully!")
        else:
            st.error("❌ Persona name is required!")

def show_persona_editor():
    """Interface for viewing and editing existing personas."""
    st.subheader("✏️ View & Edit Personas")
    
    # Load existing personas
    personas = load_personas()
    
    if not personas:
        st.info("No saved personas found. Create a new persona first.")
        return
    
    # Select persona to view/edit
    persona_names = [p.name for p in personas]
    selected_name = st.selectbox("Select a persona to view or edit:", persona_names)
    
    selected_persona = next((p for p in personas if p.name == selected_name), None)
    if not selected_persona:
        st.error("Could not find selected persona.")
        return
    
    # Display persona card
    st.divider()
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(selected_persona.name)
        st.caption(f"{selected_persona.age} • {selected_persona.gender}")
        st.write(f"📍 {selected_persona.location}")
        st.write(f"💼 {selected_persona.occupation}")
        st.write(f"💰 {selected_persona.annual_income}")
        
        # Action buttons
        edit_mode = st.button("✏️ Edit This Persona")
        delete_mode = st.button("🗑️ Delete This Persona")
        
    with col2:
        st.markdown("### Persona Overview")
        st.write(selected_persona.persona_summary)
        
        st.markdown("### Key Struggles")
        for struggle in selected_persona.major_struggles[:3]:
            st.write(f"• {struggle}")
        
        st.markdown("### Signature Quote")
        if selected_persona.if_only_soundbites:
            st.info(f"*\"{selected_persona.if_only_soundbites[0]}\"*")
    
    # Display full persona details in expandable sections
    st.divider()
    
    with st.expander("View Complete Persona Profile", expanded=False):
        tab1, tab2, tab3, tab4 = st.tabs(["Basic & Lifestyle", "Challenges & Fears", "Goals & Aspirations", "Life Scenario"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Basic Information")
                st.write(f"**Education:** {selected_persona.education}")
                st.write(f"**Family:** {selected_persona.relationship_family}")
                
                st.markdown("#### Personality")
                st.write("**Traits:**")
                for trait in selected_persona.personality_traits:
                    st.write(f"• {trait}")
                
                st.write("**Values:**")
                for value in selected_persona.values:
                    st.write(f"• {value}")
            
            with col2:
                st.markdown("#### Lifestyle")
                st.write(f"**Free Time:** {selected_persona.free_time_activities}")
                st.write(f"**Description:** {selected_persona.lifestyle_description}")
                
                st.markdown("#### Community & Hobbies")
                st.write("**Hobbies:**")
                for hobby in selected_persona.hobbies:
                    st.write(f"• {hobby}")
                
                st.write("**Community Involvement:**")
                for community in selected_persona.community_involvement:
                    st.write(f"• {community}")
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Major Struggles")
                for struggle in selected_persona.major_struggles:
                    st.write(f"• {struggle}")
                
                st.markdown("#### Business Fears")
                for fear in selected_persona.deep_fears_business:
                    st.write(f"• {fear}")
                
                st.markdown("#### Previous Solutions Tried")
                st.write("**Software:**")
                for software in selected_persona.previous_software_tried:
                    st.write(f"• {software}")
                st.write(f"**Why Failed:** {selected_persona.why_software_failed}")
            
            with col2:
                st.markdown("#### Personal Fears")
                for fear in selected_persona.deep_fears_personal:
                    st.write(f"• {fear}")
                
                st.markdown("#### Fear Impact")
                st.write(f"**On Family:** {selected_persona.fear_impact_spouse}")
                st.write(f"**On Children:** {selected_persona.fear_impact_kids}")
                st.write(f"**On Work:** {selected_persona.fear_impact_employees}")
                
                st.markdown("#### What Others Might Say")
                for remark in selected_persona.potential_remarks_from_others:
                    st.write(f"• {remark}")
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Desired Business Outcomes")
                for result in selected_persona.tangible_business_results:
                    st.write(f"• {result}")
                
                st.markdown("#### Professional Recognition")
                for goal in selected_persona.professional_recognition_goals:
                    st.write(f"• {goal}")
                
                st.markdown("#### Financial Goals")
                for goal in selected_persona.financial_freedom_goals:
                    st.write(f"• {goal}")
            
            with col2:
                st.markdown("#### Desired Personal Outcomes")
                for result in selected_persona.tangible_personal_results:
                    st.write(f"• {result}")
                
                st.markdown("#### Emotional Transformations")
                for transformation in selected_persona.emotional_transformations:
                    st.write(f"• {transformation}")
                
                st.markdown("#### Big Picture")
                st.write(selected_persona.big_picture_aspirations)
        
        with tab4:
            st.markdown("#### Ideal Day Scenario")
            st.write(selected_persona.ideal_day_scenario)
    
    # Handle edit mode
    if edit_mode:
        st.divider()
        st.subheader(f"Edit {selected_persona.name}")
        # In a real implementation, this would populate a form with the persona's data
        # and allow updates, similar to the creation form but pre-filled
        st.info("Edit functionality would be implemented here with pre-filled form fields")
    
    # Handle delete mode
    if delete_mode:
        st.divider()
        st.warning(f"Are you sure you want to delete {selected_persona.name}?")
        if st.button("✅ Confirm Delete"):
            # In a real implementation, this would remove the persona from storage
            st.error(f"Deleted {selected_persona.name}")

def show_persona_import_export():
    """Interface for importing and exporting detailed personas."""
    st.subheader("📤 Import & Export Personas")
    
    tab1, tab2 = st.tabs(["Import", "Export"])
    
    with tab1:
        st.markdown("### Import Personas")
        st.write("Upload personas from file in various formats:")
        
        import_format = st.radio(
            "Select Import Format:",
            ["CSV (Basic)", "CSV (Detailed)", "JSON", "Python File"],
            horizontal=True
        )
        
        if import_format == "CSV (Basic)":
            st.info("Upload a CSV with basic persona fields (name, age, gender, occupation, etc.)")
            upload_file = st.file_uploader("Upload CSV File", type=["csv"], key="basic_csv_upload")
            
            if upload_file:
                try:
                    df = pd.read_csv(upload_file)
                    st.success(f"CSV file loaded with {len(df)} records")
                    st.dataframe(df.head())
                    
                    if st.button("Import These Personas"):
                        st.success(f"Imported {len(df)} personas!")
                except Exception as e:
                    st.error(f"Error loading CSV: {e}")
        
        elif import_format == "CSV (Detailed)":
            st.info("Upload a CSV with all detailed persona fields")
            upload_file = st.file_uploader("Upload Detailed CSV File", type=["csv"], key="detailed_csv_upload")
            
            # Similar processing as above
            
        elif import_format == "JSON":
            st.info("Upload a JSON file with persona data")
            upload_file = st.file_uploader("Upload JSON File", type=["json"], key="json_upload")
            
            if upload_file:
                try:
                    data = json.load(upload_file)
                    st.success(f"JSON file loaded with {len(data)} personas")
                    st.json(data[0] if data else {})
                    
                    if st.button("Import These Personas"):
                        st.success(f"Imported {len(data)} personas!")
                except Exception as e:
                    st.error(f"Error loading JSON: {e}")
        
        elif import_format == "Python File":
            st.info("Upload a Python file with Persona objects (advanced)")
            upload_file = st.file_uploader("Upload Python File", type=["py"], key="py_upload")
            
            if upload_file:
                content = upload_file.read().decode()
                st.code(content, language="python")
                
                if st.button("Import Python Personas"):
                    st.success("Python persona import would be processed here")
    
    with tab2:
        st.markdown("### Export Personas")
        st.write("Export your personas in various formats:")
        
        # Load personas for export
        personas = load_personas()
        
        if not personas:
            st.info("No personas available for export.")
            return
        
        # Select personas to export
        persona_names = [p.name for p in personas]
        selected_personas = st.multiselect("Select personas to export:", persona_names, default=persona_names)
        
        if not selected_personas:
            st.warning("Please select at least one persona to export.")
            return
        
        # Export format options
        export_format = st.radio(
            "Select Export Format:",
            ["CSV", "JSON", "Python Script"],
            horizontal=True
        )
        
        # Select personas for export
        export_personas = [p for p in personas if p.name in selected_personas]
        
        if export_format == "CSV":
            # Convert personas to DataFrame for CSV export
            if st.button("Generate CSV Export"):
                st.success(f"CSV export ready for {len(export_personas)} personas")
                # In real implementation, generate and provide download
                st.download_button(
                    "Download CSV",
                    "name,age,gender,occupation\nMock Data",
                    "personas_export.csv",
                    "text/csv",
                    key="csv_download"
                )
        
        elif export_format == "JSON":
            # Convert personas to JSON
            if st.button("Generate JSON Export"):
                st.success(f"JSON export ready for {len(export_personas)} personas")
                # In real implementation, convert and provide download
                sample_json = json.dumps([{"name": p.name, "age": p.age} for p in export_personas])
                st.download_button(
                    "Download JSON",
                    sample_json,
                    "personas_export.json",
                    "application/json",
                    key="json_download"
                )
        
        elif export_format == "Python Script":
            # Generate Python code
            if st.button("Generate Python Script"):
                st.success(f"Python script ready for {len(export_personas)} personas")
                # In real implementation, generate actual code
                sample_code = "# Sample persona code\ndef create_personas():\n    # Code would go here\n    pass"
                st.code(sample_code, language="python")
                st.download_button(
                    "Download Python Script",
                    sample_code,
                    "personas_export.py",
                    "text/plain",
                    key="py_download"
                )

def save_persona(persona_data):
    """Save a new persona (mock implementation)."""
    # In a real implementation, this would save to a database or file
    if 'saved_personas' not in st.session_state:
        st.session_state.saved_personas = []
    
    # Convert to Persona object
    try:
        new_persona = Persona(**persona_data)
        st.session_state.saved_personas.append(new_persona)
    except Exception as e:
        st.error(f"Error creating persona: {e}")

def load_personas():
    """Load existing personas (mock implementation)."""
    # In a real implementation, this would load from a database or file
    if 'saved_personas' not in st.session_state:
        # For demo, create sample personas if none exist
        from sample_detailed_personas import (
            create_sarah_marketing_maven,
            create_mike_growth_hacker, 
            create_jenny_scaling_solopreneur
        )
        
        st.session_state.saved_personas = [
            create_sarah_marketing_maven(),
            create_mike_growth_hacker(),
            create_jenny_scaling_solopreneur()
        ]
    
    return st.session_state.saved_personas

if __name__ == "__main__":
    st.set_page_config(
        page_title="Persona Manager",
        page_icon="👤",
        layout="wide"
    )
    show_detailed_persona_manager()