@echo off
echo 🌐 Starting Enhanced Synthetic Focus Group Web Demo...
echo ============================================================
echo 📍 Opening browser to: http://localhost:5000
echo ⏹️  Press Ctrl+C in this window to stop the server
echo ============================================================
echo.

:: Start the web server
python web_demo.py

:: Keep window open if there's an error
pause