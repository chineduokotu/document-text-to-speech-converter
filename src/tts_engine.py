"""
Text-to-Speech Engine Module

This module provides the core TTS functionality with voice selection,
speed control, volume adjustment, and various output options.
"""

import pyttsx3
import time
from typing import List, Dict, Optional, Union
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSEngine:
    """Main Text-to-Speech engine class."""
    
    def __init__(self):
        """Initialize the TTS engine with default settings."""
        try:
            self.engine = pyttsx3.init()
            self.voices = self.engine.getProperty('voices')
            self.default_settings = {
                'rate': 200,  # Words per minute
                'volume': 0.9,  # Volume level (0.0 to 1.0)
                'voice_id': 0 if self.voices else None  # Default to first voice
            }
            self.apply_settings(self.default_settings)
            logger.info("TTS Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available voices on the system."""
        voice_list = []
        for i, voice in enumerate(self.voices):
            voice_info = {
                'id': i,
                'name': voice.name,
                'languages': getattr(voice, 'languages', ['Unknown']),
                'gender': getattr(voice, 'gender', 'Unknown'),
                'age': getattr(voice, 'age', 'Unknown')
            }
            voice_list.append(voice_info)
        return voice_list
    
    def set_voice(self, voice_id: int) -> bool:
        """Set the voice by ID."""
        try:
            if 0 <= voice_id < len(self.voices):
                self.engine.setProperty('voice', self.voices[voice_id].id)
                logger.info(f"Voice set to: {self.voices[voice_id].name}")
                return True
            else:
                logger.warning(f"Invalid voice ID: {voice_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")
            return False
    
    def set_rate(self, rate: int) -> bool:
        """Set the speech rate (words per minute)."""
        try:
            if 50 <= rate <= 400:  # Reasonable range
                self.engine.setProperty('rate', rate)
                logger.info(f"Speech rate set to: {rate} WPM")
                return True
            else:
                logger.warning(f"Rate {rate} is outside reasonable range (50-400)")
                return False
        except Exception as e:
            logger.error(f"Failed to set rate: {e}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Set the speech volume (0.0 to 1.0)."""
        try:
            if 0.0 <= volume <= 1.0:
                self.engine.setProperty('volume', volume)
                logger.info(f"Volume set to: {volume}")
                return True
            else:
                logger.warning(f"Volume {volume} is outside valid range (0.0-1.0)")
                return False
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return False
    
    def apply_settings(self, settings: Dict[str, Union[int, float]]) -> None:
        """Apply multiple settings at once."""
        if 'rate' in settings:
            self.set_rate(settings['rate'])
        if 'volume' in settings:
            self.set_volume(settings['volume'])
        if 'voice_id' in settings:
            self.set_voice(settings['voice_id'])
    
    def speak_text(self, text: str, wait_until_done: bool = True) -> bool:
        """
        Convert text to speech.
        
        Args:
            text: The text to convert to speech
            wait_until_done: Whether to wait for speech to complete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not text.strip():
                logger.warning("Empty text provided for speech")
                return False
            
            logger.info(f"Speaking text: {text[:50]}{'...' if len(text) > 50 else ''}")
            self.engine.say(text)
            
            if wait_until_done:
                self.engine.runAndWait()
            
            return True
        except Exception as e:
            logger.error(f"Failed to speak text: {e}")
            return False
    
    def speak_file(self, file_path: Union[str, Path], 
                   chunk_size: int = 1000,
                   pause_between_chunks: float = 0.5) -> bool:
        """
        Speak text from a file, breaking it into chunks for better control.
        
        Args:
            file_path: Path to the text file
            chunk_size: Number of characters per chunk
            pause_between_chunks: Pause duration between chunks (seconds)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if not content.strip():
                logger.warning(f"File is empty: {file_path}")
                return False
            
            # Split content into chunks
            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
            
            logger.info(f"Speaking file in {len(chunks)} chunks: {file_path}")
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Speaking chunk {i+1}/{len(chunks)}")
                if not self.speak_text(chunk, wait_until_done=True):
                    return False
                
                if i < len(chunks) - 1:  # Don't pause after the last chunk
                    time.sleep(pause_between_chunks)
            
            return True
        except Exception as e:
            logger.error(f"Failed to speak file: {e}")
            return False
    
    def save_to_file(self, text: str, output_path: Union[str, Path]) -> bool:
        """
        Save text-to-speech as an audio file.
        Note: This requires additional setup and may not work on all systems.
        """
        try:
            output_path = Path(output_path)
            self.engine.save_to_file(text, str(output_path))
            self.engine.runAndWait()
            logger.info(f"Audio saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            return False
    
    def stop_speaking(self) -> None:
        """Stop the current speech."""
        try:
            self.engine.stop()
            logger.info("Speech stopped")
        except Exception as e:
            logger.error(f"Failed to stop speech: {e}")
    
    def get_current_settings(self) -> Dict[str, Union[int, float, str]]:
        """Get current TTS settings."""
        try:
            current_voice = self.engine.getProperty('voice')
            voice_name = "Unknown"
            voice_id = -1
            
            for i, voice in enumerate(self.voices):
                if voice.id == current_voice:
                    voice_name = voice.name
                    voice_id = i
                    break
            
            return {
                'rate': self.engine.getProperty('rate'),
                'volume': self.engine.getProperty('volume'),
                'voice_name': voice_name,
                'voice_id': voice_id
            }
        except Exception as e:
            logger.error(f"Failed to get current settings: {e}")
            return {}


def main():
    """Test the TTS engine functionality."""
    try:
        # Initialize engine
        tts = TTSEngine()
        
        # Show available voices
        print("Available voices:")
        voices = tts.get_available_voices()
        for voice in voices:
            print(f"  ID: {voice['id']}, Name: {voice['name']}")
        
        # Show current settings
        print(f"\nCurrent settings: {tts.get_current_settings()}")
        
        # Test speech
        test_text = "Hello! This is a test of the text-to-speech engine. It can convert any text into speech with customizable voice settings."
        print(f"\nSpeaking test text...")
        tts.speak_text(test_text)
        
        print("TTS Engine test completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")


if __name__ == "__main__":
    main()