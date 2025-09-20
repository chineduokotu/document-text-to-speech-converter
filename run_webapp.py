#!/usr/bin/env python3
"""
Text-to-Speech Web App Launcher

Launch the Flask web application for mobile access.
"""

import sys
import os
from pathlib import Path

# Add web_app directory to path
web_app_dir = Path(__file__).parent / "web_app"
sys.path.insert(0, str(web_app_dir))

# Import and run the Flask app
from app import app

if __name__ == "__main__":
    print("🎤 Starting Text-to-Speech Web App...")
    print("📱 Mobile-friendly interface available at:")
    print("   Local:   http://localhost:5000")
    print("   Network: http://[your-ip]:5000")
    print("")
    print("🔧 To access from your phone:")
    print("   1. Make sure your phone is on the same WiFi network")
    print("   2. Find your computer's IP address")
    print("   3. Open http://[computer-ip]:5000 on your phone")
    print("")
    print("📖 Press Ctrl+C to stop the server")
    print("")
    
    # Run the Flask development server
    # For production, use a proper WSGI server like Gunicorn
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=port,
        debug=False,     # Set to False for production
        threaded=True
    )