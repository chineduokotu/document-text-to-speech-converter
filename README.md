# Text-to-Speech Automation Tool

A comprehensive Python application that converts documents and text into speech with support for multiple file formats, customizable voice settings, and both command-line and graphical interfaces.

## Features

### 🎤 Text-to-Speech Capabilities
- **Multiple Voice Options**: Select from available system voices
- **Adjustable Settings**: Control speech rate (50-400 WPM), volume (0.0-1.0)
- **Chunked Processing**: Handle large documents by breaking them into manageable chunks
- **Audio Export**: Save speech as audio files (experimental feature)

### 📄 Document Support
- **PDF Files**: Extract and read text from PDF documents
- **Word Documents**: Support for .docx files with text and table extraction
- **PowerPoint Presentations**: Read text from .pptx slides
- **Plain Text**: Support for .txt files with automatic encoding detection
- **Web Content**: Extract and read text from web URLs

### 🖥️ User Interfaces
- **Graphical Interface**: User-friendly GUI with tabs for main controls, settings, and batch processing
- **Command Line Interface**: Powerful CLI with extensive options for automation and scripting
- **Batch Processing**: Process multiple files automatically

### ⚙️ Configuration Management
- **Persistent Settings**: Save and load voice preferences
- **Multiple Profiles**: Create different configuration profiles
- **Auto-save Preferences**: Remember your settings between sessions

## Installation

### Prerequisites
- Python 3.7 or higher
- Windows, macOS, or Linux operating system

### Step 1: Clone or Download
```bash
# Clone the repository (if using Git)
git clone <repository-url>
cd text-to-speech-automation

# Or download and extract the ZIP file
```

### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Dependencies Installed:
- `pyttsx3>=2.90` - Text-to-speech engine
- `PyPDF2>=3.0.1` - PDF text extraction
- `python-docx>=0.8.11` - Word document processing
- `python-pptx>=0.6.21` - PowerPoint presentation processing
- `chardet>=5.0.0` - Text encoding detection
- `beautifulsoup4>=4.11.1` - Web content parsing
- `requests>=2.28.1` - HTTP requests for web content

## Usage

### Quick Start

#### Using the GUI
```bash
python main.py --gui
```

#### Using the Command Line
```bash
# Convert text to speech
python main.py --text "Hello, this is a test of the text-to-speech system."

# Convert a PDF file to speech
python main.py --file document.pdf

# Convert a web page to speech
python main.py --url https://example.com

# Use specific voice and settings
python main.py --file document.txt --voice 1 --rate 150 --volume 0.8
```

### Command Line Interface (CLI)

The CLI provides extensive options for automation and scripting:

#### Basic Usage
```bash
python main.py [OPTIONS]
```

#### Input Options
```bash
--file, -f FILE         Path to document file (PDF, DOCX, PPTX, TXT)
--text, -t TEXT         Text to convert to speech
--url, -u URL          URL to read content from
--batch, -b FILES      Multiple files to process (supports wildcards)
--list-voices          List available voices and exit
```

#### Voice Settings
```bash
--voice, -v ID         Voice ID to use (see --list-voices)
--rate, -r RATE        Speech rate in words per minute (50-400, default: 200)
--volume VOLUME        Speech volume (0.0-1.0, default: 0.9)
```

#### Processing Options
```bash
--chunk-size SIZE      Characters per chunk for long texts (default: 1000)
--pause SECONDS        Pause between chunks in seconds (default: 0.5)
--no-wait              Don't wait for speech to complete before continuing
```

#### Output Options
```bash
--save-audio FILE      Save speech as audio file (experimental)
--save-config          Save current settings as default
--load-config FILE     Load settings from config file
```

#### Other Options
```bash
--quiet, -q            Suppress informational messages
--verbose              Enable verbose logging
```

### Examples

#### Basic Text-to-Speech
```bash
# Simple text
python main.py --text "Welcome to the text-to-speech automation tool!"

# Read a text file
python main.py --file README.txt

# Read a PDF document
python main.py --file report.pdf --rate 180
```

#### Voice and Settings
```bash
# List available voices
python main.py --list-voices

# Use specific voice with custom settings
python main.py --text "Testing voice" --voice 2 --rate 150 --volume 0.7
```

#### Batch Processing
```bash
# Process multiple files
python main.py --batch *.txt *.pdf

# Process files with custom settings
python main.py --batch documents/*.pdf --rate 200 --chunk-size 500
```

#### Web Content
```bash
# Read content from a webpage
python main.py --url https://en.wikipedia.org/wiki/Text-to-speech

# Save web content as audio
python main.py --url https://example.com --save-audio webpage.wav
```

#### Configuration Management
```bash
# Save current settings
python main.py --text "test" --voice 1 --rate 180 --save-config

# Load custom settings
python main.py --load-config my-settings.json --file document.pdf
```

### Graphical User Interface (GUI)

Launch the GUI with:
```bash
python main.py --gui
```

#### GUI Features:
- **Main Tab**: Text input, file selection, URL input, and basic controls
- **Settings Tab**: Voice selection, speed/volume controls, and configuration management
- **Batch Processing Tab**: Add multiple files and process them sequentially

#### GUI Usage:
1. **Text Input**: Type or paste text directly into the text area
2. **File Input**: Click "Browse" to select supported document files
3. **URL Input**: Enter a webpage URL to read its content
4. **Settings**: Adjust voice, speed, and volume in the Settings tab
5. **Batch Processing**: Add multiple files and process them automatically

## Configuration

### Configuration Files
The application stores configuration in your user directory under `.tts-automation/`:

- `default.json` - Default settings
- `user_settings.ini` - User preferences (auto-saved)
- Custom configuration files can be saved and loaded

### Settings Structure
```json
{
  "version": "1.0",
  "settings": {
    "voice_id": 0,
    "rate": 200,
    "volume": 0.9,
    "chunk_size": 1000,
    "pause_between_chunks": 0.5
  },
  "created_by": "TTS Automation Tool"
}
```

## Supported File Formats

| Format | Extension | Features |
|--------|-----------|----------|
| Plain Text | `.txt` | Full text with encoding detection |
| PDF Documents | `.pdf` | Text extraction from all pages |
| Word Documents | `.docx` | Text and table content |
| PowerPoint | `.pptx` | Text from all slides |
| Web Pages | URLs | Content extraction from HTML |

## Troubleshooting

### Common Issues

#### "No module named 'pyttsx3'"
```bash
pip install pyttsx3
```

#### "Failed to initialize TTS engine"
- On Linux: Install `espeak` or `festival`
  ```bash
  sudo apt-get install espeak espeak-data libespeak1 libespeak-dev
  ```
- On macOS: The system TTS should work by default
- On Windows: SAPI should be available by default

#### PDF Text Extraction Issues
- Some PDFs with images or complex layouts may not extract text properly
- Try using OCR tools for scanned PDFs before processing

#### Audio File Saving Not Working
- Audio file saving is experimental and may not work on all systems
- Ensure you have proper audio drivers and permissions

### Performance Tips

1. **Large Documents**: Use appropriate chunk sizes (500-2000 characters)
2. **Batch Processing**: Process files during off-hours for better performance
3. **Web Content**: Some websites may block automated requests
4. **Memory Usage**: Close other applications when processing large files

## Project Structure

```
text-to-speech-automation/
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── tts_engine.py      # Core TTS functionality
│   ├── document_readers.py # Document format readers
│   ├── cli.py             # Command-line interface
│   ├── gui.py             # Graphical interface
│   └── config_manager.py  # Configuration management
├── docs/                  # Documentation
└── examples/              # Example files and scripts
```

## Development

### Running Tests
```bash
# Test the TTS engine
python src/tts_engine.py

# Test document readers
python src/document_readers.py

# Test configuration manager
python src/config_manager.py
```

### Adding New Features
1. Document readers can be extended in `document_readers.py`
2. TTS settings can be modified in `tts_engine.py`
3. GUI components are in `gui.py`
4. CLI options are defined in `cli.py`

## License

This project is open source. Please check the license file for details.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Changelog

### Version 1.0.0
- Initial release
- Support for PDF, DOCX, PPTX, TXT files
- Command-line and GUI interfaces
- Batch processing capabilities
- Configuration management
- Web content support

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review existing issues in the repository
3. Create a new issue with detailed information

---

**Enjoy using the Text-to-Speech Automation Tool!** 🎤📄