#!/usr/bin/env python3
"""
Text-to-Speech Automation Tool - Usage Examples

This script demonstrates various ways to use the TTS automation tool
programmatically within Python scripts.
"""

import sys
import os
from pathlib import Path

# Add the parent src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from tts_engine import TTSEngine
from document_readers import UniversalDocumentReader
from config_manager import ConfigManager


def example_basic_usage():
    """Basic text-to-speech usage example."""
    print("=== Basic Usage Example ===")
    
    # Initialize the TTS engine
    tts = TTSEngine()
    
    # Simple text-to-speech
    text = "Hello! This is an example of basic text-to-speech functionality."
    print(f"Speaking: {text}")
    tts.speak_text(text)
    
    print("Basic usage example completed.\n")


def example_voice_settings():
    """Example showing how to customize voice settings."""
    print("=== Voice Settings Example ===")
    
    # Initialize the TTS engine
    tts = TTSEngine()
    
    # List available voices
    voices = tts.get_available_voices()
    print("Available voices:")
    for voice in voices[:3]:  # Show first 3 voices
        print(f"  ID: {voice['id']}, Name: {voice['name']}")
    
    # Try different voice settings
    settings_to_try = [
        {"voice_id": 0, "rate": 150, "volume": 0.8},
        {"voice_id": 0, "rate": 250, "volume": 1.0},
    ]
    
    for i, settings in enumerate(settings_to_try):
        print(f"\nTesting settings {i+1}: {settings}")
        tts.apply_settings(settings)
        tts.speak_text(f"This is voice test number {i+1} with different settings.")
    
    print("Voice settings example completed.\n")


def example_document_reading():
    """Example showing how to read different document types."""
    print("=== Document Reading Example ===")
    
    # Create a sample text file for demonstration
    sample_file = Path("sample_text.txt")
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write("This is a sample text file created for demonstration purposes. "
                "The text-to-speech automation tool can read this file and convert "
                "it to speech automatically.")
    
    try:
        # Initialize components
        tts = TTSEngine()
        reader = UniversalDocumentReader()
        
        # Check supported formats
        print("Supported file extensions:", reader.get_supported_extensions())
        
        # Read the sample file
        if reader.is_supported(sample_file):
            print(f"Reading file: {sample_file}")
            content = reader.read_file(sample_file)
            
            if content:
                print(f"File content ({len(content)} characters): {content[:100]}...")
                print("Converting to speech...")
                tts.speak_text(content)
            else:
                print("Failed to read file content")
        else:
            print(f"File type not supported: {sample_file.suffix}")
    
    finally:
        # Clean up the sample file
        if sample_file.exists():
            sample_file.unlink()
    
    print("Document reading example completed.\n")


def example_configuration_management():
    """Example showing configuration management."""
    print("=== Configuration Management Example ===")
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Show default settings
    defaults = config_manager.get_default_settings()
    print("Default settings:", defaults)
    
    # Create custom settings
    custom_settings = {
        'voice_id': 1,
        'rate': 180,
        'volume': 0.8,
        'chunk_size': 800
    }
    
    # Save custom settings
    print("Saving custom settings...")
    success = config_manager.save_config(custom_settings, "example_config.json")
    
    if success:
        print("Settings saved successfully")
        
        # Load the settings back
        loaded_settings = config_manager.load_config("example_config.json")
        print("Loaded settings:", loaded_settings)
        
        # Clean up
        config_file = Path("example_config.json")
        if config_file.exists():
            config_file.unlink()
    else:
        print("Failed to save settings")
    
    print("Configuration management example completed.\n")


def example_web_content():
    """Example showing web content reading (if internet is available)."""
    print("=== Web Content Example ===")
    
    try:
        # Initialize components
        tts = TTSEngine()
        reader = UniversalDocumentReader()
        
        # Try to read content from a simple web page
        test_url = "https://httpbin.org/html"
        print(f"Attempting to read content from: {test_url}")
        
        content = reader.read_url(test_url)
        
        if content:
            # Limit content length for the example
            limited_content = content[:200] + "..." if len(content) > 200 else content
            print(f"Web content ({len(content)} characters): {limited_content}")
            print("Converting to speech...")
            tts.speak_text(limited_content)
        else:
            print("Failed to read web content (this might be due to network issues)")
    
    except Exception as e:
        print(f"Web content example failed: {e}")
        print("This is normal if there's no internet connection")
    
    print("Web content example completed.\n")


def example_batch_processing():
    """Example showing batch processing of multiple texts."""
    print("=== Batch Processing Example ===")
    
    # Create sample files
    sample_texts = [
        "This is the first sample file for batch processing.",
        "This is the second sample file with different content.",
        "This is the third and final sample file in our batch."
    ]
    
    sample_files = []
    try:
        # Create sample files
        for i, text in enumerate(sample_texts):
            filename = f"batch_sample_{i+1}.txt"
            sample_file = Path(filename)
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write(text)
            sample_files.append(sample_file)
        
        # Initialize TTS engine
        tts = TTSEngine()
        reader = UniversalDocumentReader()
        
        # Process each file
        print(f"Processing {len(sample_files)} files in batch...")
        for i, file_path in enumerate(sample_files):
            print(f"Processing file {i+1}/{len(sample_files)}: {file_path}")
            
            content = reader.read_file(file_path)
            if content:
                tts.speak_text(content)
            else:
                print(f"Failed to read file: {file_path}")
    
    finally:
        # Clean up sample files
        for sample_file in sample_files:
            if sample_file.exists():
                sample_file.unlink()
    
    print("Batch processing example completed.\n")


def main():
    """Run all examples."""
    print("Text-to-Speech Automation Tool - Usage Examples")
    print("=" * 50)
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Voice Settings", example_voice_settings),
        ("Document Reading", example_document_reading),
        ("Configuration Management", example_configuration_management),
        ("Web Content", example_web_content),
        ("Batch Processing", example_batch_processing)
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples):
        print(f"  {i+1}. {name}")
    
    print("\nRunning all examples...")
    print("Note: You'll hear speech output for most examples.")
    print("Press Ctrl+C at any time to stop.\n")
    
    try:
        for name, example_func in examples:
            print(f"Running: {name}")
            example_func()
            
            # Brief pause between examples
            import time
            time.sleep(1)
        
        print("All examples completed successfully!")
    
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    main()