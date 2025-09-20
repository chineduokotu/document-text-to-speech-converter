#!/usr/bin/env python3
"""
Simple start script for deployment
"""
import os
import sys
from pathlib import Path

# Add web_app directory to path
web_app_dir = Path(__file__).parent / "web_app"
sys.path.insert(0, str(web_app_dir))

# Import and run the Flask app
from app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )