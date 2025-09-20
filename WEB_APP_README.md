# 📱 Text-to-Speech Web App

A mobile-friendly web application for converting text and documents to speech. Access the full TTS functionality from your phone, tablet, or any device with a web browser!

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web App
```bash
python run_webapp.py
```

### 3. Access on Your Phone
1. Make sure your phone is connected to the same WiFi network as your computer
2. Find your computer's IP address:
   - **Windows**: `ipconfig` in Command Prompt, look for "IPv4 Address"
   - **Mac/Linux**: `ifconfig` or `ip addr show`, look for your WiFi adapter
3. Open your phone's browser and go to: `http://[your-computer-ip]:5000`

**Example**: If your computer's IP is `192.168.1.100`, open `http://192.168.1.100:5000` on your phone.

## 📱 Mobile Features

### Touch-Optimized Interface
- **Large buttons** (48px minimum) for easy touch interaction
- **Responsive design** that adapts to any screen size
- **Touch-friendly sliders** for voice settings
- **Drag & drop** file upload support
- **Swipe navigation** between tabs

### Mobile-Specific Optimizations
- **Prevents zoom** on input focus (iOS)
- **Dark mode support** based on device preferences
- **PWA-ready** for "Add to Home Screen" functionality
- **Offline-friendly** design (with service worker support)

### File Handling
- **Direct upload** from phone gallery/files
- **Camera integration** for document scanning (when supported)
- **Audio download** for offline listening
- **Multiple format support**: PDF, DOCX, PPTX, TXT

## 🎯 Usage Guide

### Main Tab - Text Processing
1. **Enter Text**: Type or paste text directly
2. **Upload File**: Tap "Choose File" to upload documents
3. **Web Content**: Enter any URL to extract and read webpage content
4. **Generate Speech**: Tap "🎤 Speak" button
5. **Download Audio**: Once processed, tap "📥 Download Audio"

### Settings Tab - Voice Control
- **Voice Selection**: Choose from available system voices
- **Speed Control**: Adjust from 50-400 words per minute
- **Volume Control**: Set from 0% to 100%
- Settings are automatically saved for your session

### About Tab - Help & Info
- Feature overview
- Usage instructions
- Supported file types
- Troubleshooting tips

## 🔧 Advanced Setup

### Production Deployment

For production use, consider using a proper WSGI server:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
cd web_app
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
```bash
# Set secret key for production
export SECRET_KEY="your-secret-key-here"

# Optional: Set custom upload folder
export UPLOAD_FOLDER="/path/to/uploads"
```

### Nginx Configuration (Optional)
For production deployment with Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    client_max_body_size 16M;
}
```

## 📂 Project Structure

```
web_app/
├── app.py                  # Flask application
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Main page
│   └── error.html         # Error page
├── static/                # Static assets
│   ├── css/
│   │   └── style.css      # Mobile-responsive styles
│   └── js/
│       └── app.js         # JavaScript functionality
└── uploads/               # Temporary file storage
```

## 🔐 Security Features

### File Upload Security
- **File type validation** - only allows safe document types
- **File size limits** - maximum 16MB per file
- **Temporary storage** - files are automatically cleaned up
- **Secure filenames** - prevents directory traversal attacks

### Session Management
- **Session-based settings** - preferences stored securely
- **CSRF protection** - prevents cross-site request forgery
- **Input sanitization** - all user input is properly sanitized

## 📊 API Endpoints

The web app provides RESTful API endpoints:

### Voice Management
- `GET /api/voices` - List available voices
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings

### Text Processing
- `POST /api/speak` - Convert text to speech
- `POST /api/upload` - Upload and process file
- `POST /api/url` - Process web URL

### Audio Management
- `GET /api/status/<task_id>` - Check processing status
- `GET /api/download/<task_id>` - Download audio file

## 🐛 Troubleshooting

### Common Issues

#### "TTS Engine Failed to Initialize"
- **Windows**: Ensure SAPI is available (should be by default)
- **Linux**: Install espeak: `sudo apt-get install espeak`
- **Mac**: System TTS should work by default

#### "File Upload Failed"
- Check file size is under 16MB
- Ensure file type is supported (TXT, PDF, DOCX, PPTX)
- Verify sufficient disk space

#### "Cannot Access from Phone"
- Ensure both devices are on the same WiFi network
- Check firewall settings allow port 5000
- Verify the IP address is correct
- Try restarting the web app

#### "Audio Download Not Working"
- Wait for processing to complete
- Check browser download permissions
- Try a different browser
- Clear browser cache

### Performance Tips

#### For Large Documents
- Break very long texts into smaller sections
- Use lower quality settings for faster processing
- Process during off-peak hours

#### For Mobile Users
- Download audio files for offline listening
- Use WiFi for large file uploads
- Close other browser tabs for better performance

## 🔄 Updates & Maintenance

### Automatic Cleanup
- Uploaded files are deleted after 1 hour
- Audio files are cleaned up automatically
- Session data expires after browser closure

### Monitoring
Check the console output for:
- Processing status messages
- Error logs
- File cleanup notifications

## 🆘 Support

### Getting Help
1. Check the troubleshooting section above
2. Review browser console for error messages
3. Verify all dependencies are installed correctly
4. Test with different file types/sizes

### Feature Requests
The web app supports the same core features as the desktop version:
- Multiple document formats
- Voice customization
- Batch processing (through multiple uploads)
- Configuration management

---

**Enjoy using your mobile-friendly Text-to-Speech tool!** 🎤📱