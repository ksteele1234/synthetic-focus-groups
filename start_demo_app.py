#!/usr/bin/env python3
"""
Demo launcher for Synthetic Focus Groups Web Application.
Runs in demo mode without requiring OpenAI API key.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit web application in demo mode."""
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Set demo mode environment variable
    os.environ['DEMO_MODE'] = 'true'
    os.environ['OPENAI_API_KEY'] = 'demo-key-not-real'  # Dummy key for demo
    
    print("🎯 Starting Synthetic Focus Groups Web Interface (DEMO MODE)...")
    print("=" * 60)
    print()
    print("📋 Features available:")
    print("   ✅ Study Creator - Configure and create new studies")
    print("   ✅ Persona Manager - Create/upload personas with full profiles")
    print("   ✅ Templates & Examples - Download CSV/JSON templates")
    print("   ✅ Session Runner - Execute focus groups with AI agents")
    print("   ✅ Results Viewer - Real-time analytics and insights")
    print("   ✅ Live Transcripts - Real-time conversation tracking")
    print("   ✅ Export Hub - Professional reporting and exports")
    print("   ✅ Persona Weighting - Enhanced with ICP focus")
    print("   ⚠️  AI Features - Running in demo mode (mock responses)")
    print()
    print("🌐 Opening web interface...")
    print("   URL: http://localhost:8501")
    print("   Press Ctrl+C to stop")
    print()
    
    try:
        # Launch Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.serverAddress", "localhost",
            "--browser.serverPort", "8501"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Web application stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install:")
        print("   pip install streamlit plotly pandas")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()