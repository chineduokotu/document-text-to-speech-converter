#!/usr/bin/env python3
"""
Simple Flask app for Render deployment
"""
import os
import sys
from pathlib import Path

# Add current directory and web_app to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "web_app"))

# Import the actual app from web_app
from web_app.app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )