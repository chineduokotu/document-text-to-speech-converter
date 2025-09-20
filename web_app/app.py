#!/usr/bin/env python3
"""
Text-to-Speech Web Application

Flask web app that provides a mobile-friendly interface for the TTS automation tool.
"""

import os
import sys
from pathlib import Path
import tempfile
import threading
import time
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
import uuid

# Add parent src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Try to use gTTS (free, no API keys), fallback to pyttsx3 if not available
try:
    from gtts_engine import GTTSEngine
    TTSEngine = GTTSEngine
    print("✅ Using gTTS (free Google Text-to-Speech - no API keys needed!)")
except ImportError as e:
    print(f"⚠️ gTTS not available ({e}), falling back to pyttsx3")
    try:
        from tts_engine import TTSEngine
        print("✅ Using pyttsx3 (offline Text-to-Speech)")
    except ImportError:
        print("❌ No TTS engines available - app will work without voice")
        TTSEngine = None

from document_readers import UniversalDocumentReader
from config_manager import ConfigManager

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'

# Ensure upload directory exists
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Global instances
tts_engine = None
document_reader = UniversalDocumentReader()
config_manager = ConfigManager()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx', '.pptx'}

# Store audio files temporarily (in production, use Redis or database)
audio_files = {}
processing_status = {}


def init_tts_engine():
    """Initialize TTS engine on first use."""
    global tts_engine
    if tts_engine is None:
        try:
            tts_engine = TTSEngine()
            print("✅ TTS Engine initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️ TTS Engine initialization failed: {e}")
            print("📝 Document processing will still work without TTS")
            tts_engine = None  # Explicitly set to None to indicate no TTS
            return False
    return True


def allowed_file(filename):
    """Check if file extension is allowed."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def cleanup_old_files():
    """Clean up old uploaded and audio files (run periodically)."""
    current_time = time.time()
    
    # Clean up uploads older than 1 hour
    for file_path in app.config['UPLOAD_FOLDER'].glob('*'):
        if current_time - file_path.stat().st_mtime > 3600:  # 1 hour
            try:
                file_path.unlink()
            except:
                pass
    
    # Clean up old audio files from memory
    to_remove = []
    for task_id, info in audio_files.items():
        if current_time - info.get('created', 0) > 3600:  # 1 hour
            to_remove.append(task_id)
            if info.get('file_path') and Path(info['file_path']).exists():
                try:
                    Path(info['file_path']).unlink()
                except:
                    pass
    
    for task_id in to_remove:
        audio_files.pop(task_id, None)
        processing_status.pop(task_id, None)


@app.route('/')
def index():
    """Main page."""
    # Try to initialize TTS, but don't fail if it doesn't work
    init_tts_engine()

    # Always show the main page - TTS is optional
    return render_template('index.html')


@app.route('/api/voices')
def get_voices():
    """API endpoint to get available voices."""
    if not init_tts_engine() or tts_engine is None:
        return jsonify({
            'voices': [],
            'message': 'TTS not configured - using default voice settings'
        }), 200

    try:
        voices = tts_engine.get_available_voices()
        return jsonify({'voices': voices})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """API endpoint for settings management."""
    if request.method == 'GET':
        # Get current settings
        if 'settings' not in session:
            session['settings'] = config_manager.get_default_settings()
        return jsonify(session['settings'])
    
    elif request.method == 'POST':
        # Update settings
        try:
            settings = request.get_json()
            session['settings'] = settings
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 400


@app.route('/api/speak', methods=['POST'])
def speak_text():
    """API endpoint to convert text to speech."""
    if not init_tts_engine() or tts_engine is None:
        return jsonify({
            'error': 'TTS engine not available',
            'message': 'Text-to-speech is not configured. Document processing still works perfectly!'
        }), 200  # Return 200 instead of 500 to not break the app

    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Apply user settings with safety checks
        settings = session.get('settings', config_manager.get_default_settings())

        # Ensure settings are not None
        if settings is None:
            settings = config_manager.get_default_settings()

        # Clean up settings to remove any None values
        clean_settings = {}
        for key, value in settings.items():
            if value is not None:
                clean_settings[key] = value

        print(f"Applying settings: {clean_settings}")  # Debug logging
        tts_engine.apply_settings(clean_settings)

        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Start background processing
        processing_status[task_id] = {'status': 'processing', 'progress': 0}

        def process_speech():
            try:
                print(f"Starting speech processing for task {task_id}")  # Debug logging
                # Create temporary file for audio
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    temp_path = temp_file.name
                print(f"Created temp file: {temp_path}")  # Debug logging

                processing_status[task_id]['progress'] = 50

                # Generate speech
                print("Calling tts_engine.save_to_file...")  # Debug logging
                success = tts_engine.save_to_file(text, temp_path)
                print(f"save_to_file returned: {success}")  # Debug logging

                if success:
                    audio_files[task_id] = {
                        'file_path': temp_path,
                        'created': time.time(),
                        'filename': 'speech.mp3'
                    }
                    processing_status[task_id] = {'status': 'completed', 'progress': 100}
                    print("Speech processing completed successfully")  # Debug logging
                else:
                    processing_status[task_id] = {'status': 'error', 'error': 'Failed to generate speech'}
                    print("Speech processing failed")  # Debug logging

            except Exception as e:
                print(f"Speech processing error: {e}")  # Debug logging
                processing_status[task_id] = {'status': 'error', 'error': str(e)}

        # Start processing in background
        thread = threading.Thread(target=process_speech)
        thread.daemon = True
        thread.start()

        return jsonify({'task_id': task_id, 'status': 'processing'})

    except Exception as e:
        print(f"Speak text error: {e}")  # Debug logging
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API endpoint to upload and process files."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported. Supported: TXT, PDF, DOCX, PPTX'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = app.config['UPLOAD_FOLDER'] / unique_filename
        file.save(file_path)
        
        # Extract text from file
        content = document_reader.read_file(file_path)
        
        if not content:
            file_path.unlink()  # Clean up failed file
            return jsonify({'error': 'Could not extract text from file'}), 400
        
        # Clean up uploaded file after extraction
        file_path.unlink()
        
        return jsonify({
            'success': True,
            'text': content,
            'filename': filename,
            'length': len(content)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/url', methods=['POST'])
def process_url():
    """API endpoint to process web URLs."""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        content = document_reader.read_url(url)
        
        if not content:
            return jsonify({'error': 'Could not extract content from URL'}), 400
        
        return jsonify({
            'success': True,
            'text': content,
            'url': url,
            'length': len(content)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<task_id>')
def get_status(task_id):
    """API endpoint to check processing status."""
    status = processing_status.get(task_id, {'status': 'not_found'})
    return jsonify(status)


@app.route('/api/download/<task_id>')
def download_audio(task_id):
    """API endpoint to download generated audio."""
    if task_id not in audio_files:
        return jsonify({'error': 'Audio file not found'}), 404
    
    file_info = audio_files[task_id]
    file_path = file_info['file_path']
    
    if not Path(file_path).exists():
        return jsonify({'error': 'Audio file no longer available'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=file_info.get('filename', 'speech.wav'),
        mimetype='audio/wav'
    )


@app.route('/settings')
def settings_page():
    """Settings page."""
    if not init_tts_engine():
        return render_template('error.html', error="Failed to initialize TTS engine")
    
    return render_template('settings.html')


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    return render_template('error.html', error="Internal server error"), 500


@app.errorhandler(413)
def file_too_large(error):
    """413 error handler for file too large."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413


# Cleanup task (run periodically) - Flask 2.0+ compatible
def setup_cleanup():
    """Setup periodic cleanup."""
    def cleanup_worker():
        while True:
            time.sleep(3600)  # Clean up every hour
            cleanup_old_files()

    cleanup_thread = threading.Thread(target=cleanup_worker)
    cleanup_thread.daemon = True
    cleanup_thread.start()

# Start cleanup on app context
with app.app_context():
    setup_cleanup()


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)