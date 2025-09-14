#!/usr/bin/env python3
"""
Startup script for Synthetic Focus Groups Web Application.
Launches the Streamlit web interface for one-click studies.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit web application."""
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🎯 Starting Synthetic Focus Groups Web Interface...")
    print("=" * 50)
    print()
    print("📋 Features available:")
    print("   • One-click study creator")
    print("   • Interactive session runner")
    print("   • Real-time results viewer")
    print("   • Automated chart generation")
    print("   • Markdown report exports")
    print("   • Live session transcripts")
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
        print("❌ Streamlit not found. Please install dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()