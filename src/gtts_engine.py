"""
gTTS Engine Module

This module provides TTS functionality using gTTS (Google Text-to-Speech),
which is free, requires no API keys, and works on cloud platforms.
"""

from typing import List, Dict, Optional, Union
from pathlib import Path
import logging
from gtts import gTTS
from gtts.tts import gTTSError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GTTSEngine:
    """gTTS (Google Text-to-Speech) engine class."""

    def __init__(self):
        """Initialize the gTTS engine."""
        try:
            # gTTS doesn't need initialization like pyttsx3
            self.default_settings = {
                'lang': 'en',  # Language code
                'slow': False,  # Speed (False = normal, True = slow)
                'tld': 'com'   # Top-level domain for different accents
            }

            logger.info("gTTS Engine initialized successfully - no API keys needed!")

        except Exception as e:
            logger.error(f"Failed to initialize gTTS engine: {e}")
            raise

    def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available languages/voices from gTTS."""
        # gTTS supports many languages, but we'll return a basic list
        try:
            languages = [
                {'id': 'en', 'name': 'English (US)', 'lang_code': 'en', 'tld': 'com'},
                {'id': 'en-uk', 'name': 'English (UK)', 'lang_code': 'en', 'tld': 'co.uk'},
                {'id': 'en-au', 'name': 'English (Australia)', 'lang_code': 'en', 'tld': 'com.au'},
                {'id': 'es', 'name': 'Spanish', 'lang_code': 'es', 'tld': 'com'},
                {'id': 'fr', 'name': 'French', 'lang_code': 'fr', 'tld': 'com'},
                {'id': 'de', 'name': 'German', 'lang_code': 'de', 'tld': 'com'},
                {'id': 'it', 'name': 'Italian', 'lang_code': 'it', 'tld': 'com'},
                {'id': 'pt', 'name': 'Portuguese', 'lang_code': 'pt', 'tld': 'com'},
                {'id': 'ja', 'name': 'Japanese', 'lang_code': 'ja', 'tld': 'com'},
                {'id': 'ko', 'name': 'Korean', 'lang_code': 'ko', 'tld': 'com'},
                {'id': 'zh-cn', 'name': 'Chinese (Mandarin)', 'lang_code': 'zh-cn', 'tld': 'com'},
            ]
            return languages

        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
            return []

    def set_voice(self, voice_id: int) -> bool:
        """Set the voice/language by ID."""
        try:
            voices = self.get_available_voices()
            if 0 <= voice_id < len(voices):
                voice_info = voices[voice_id]
                self.default_settings['lang'] = voice_info['lang_code']
                self.default_settings['tld'] = voice_info['tld']
                logger.info(f"Voice set to: {voice_info['name']}")
                return True
            else:
                logger.warning(f"Invalid voice ID: {voice_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")
            return False

    def set_rate(self, rate: float) -> bool:
        """Set the speech rate (gTTS uses slow=True/False, not numeric rate)."""
        try:
            # Convert numeric rate to gTTS slow parameter
            # rate < 1.0 = slow, rate >= 1.0 = normal
            self.default_settings['slow'] = rate < 1.0
            logger.info(f"Speech rate set to: {'slow' if self.default_settings['slow'] else 'normal'}")
            return True
        except Exception as e:
            logger.error(f"Failed to set rate: {e}")
            return False

    def set_volume(self, volume: float) -> bool:
        """gTTS doesn't support volume control directly."""
        logger.info("gTTS doesn't support volume control - using default volume")
        return True

    def apply_settings(self, settings: Dict[str, Union[int, float, str]]) -> None:
        """Apply multiple settings at once."""
        if 'rate' in settings and settings['rate'] is not None:
            self.set_rate(float(settings['rate']))
        if 'voice_id' in settings and settings['voice_id'] is not None:
            self.set_voice(int(settings['voice_id']))
        # Volume not supported by gTTS

    def speak_text(self, text: str, wait_until_done: bool = True) -> bool:
        """
        Convert text to speech using gTTS.

        Args:
            text: The text to convert to speech
            wait_until_done: Not applicable for gTTS (always saves to file)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not text.strip():
                logger.warning("Empty text provided for speech")
                return False

            # Create gTTS object
            # Increase timeout for longer texts (up to 60 seconds)
            timeout = min(60, max(10, len(text) // 100))  # 10s min, 60s max, scale with length
            tts = gTTS(
                text=text,
                lang=self.default_settings['lang'],
                slow=self.default_settings['slow'],
                tld=self.default_settings['tld'],
                timeout=timeout
            )

            logger.info(f"Successfully created TTS for text: {text[:50]}{'...' if len(text) > 50 else ''}")
            return True

        except Exception as e:
            logger.error(f"Failed to create TTS: {e}")
            return False

    def save_to_file(self, text: str, output_path: Union[str, Path]) -> bool:
        """
        Save text-to-speech as an audio file using gTTS.
        """
        try:
            if not text.strip():
                logger.warning("Empty text provided for speech")
                return False

            logger.info(f"Attempting to generate TTS with settings: lang={self.default_settings['lang']}, slow={self.default_settings['slow']}, tld={self.default_settings['tld']}")
            logger.info(f"Text length: {len(text)} characters")

            # Create gTTS object
            tts = gTTS(
                text=text,
                lang=self.default_settings['lang'],
                slow=self.default_settings['slow'],
                tld=self.default_settings['tld']
            )

            # Save to file
            output_path = Path(output_path)
            logger.info(f"Saving audio to: {output_path}")
            tts.save(str(output_path))

            logger.info(f"Audio saved successfully to: {output_path}")
            return True

        except gTTSError as e:
            logger.error(f"gTTS specific error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to save audio file (general error): {type(e).__name__}: {e}")
            return False

    def get_current_settings(self) -> Dict[str, Union[int, float, str]]:
        """Get current TTS settings."""
        try:
            return {
                'rate': 0.8 if self.default_settings['slow'] else 1.0,
                'volume': 1.0,  # gTTS doesn't support volume
                'voice_name': f"{self.default_settings['lang']} ({self.default_settings['tld']})",
                'language_code': self.default_settings['lang']
            }
        except Exception as e:
            logger.error(f"Failed to get current settings: {e}")
            return {}

    def stop_speaking(self) -> None:
        """Stop the current speech (not applicable for gTTS)."""
        logger.info("Stop speaking not applicable for gTTS")


def main():
    """Test the gTTS engine functionality."""
    try:
        # Initialize engine
        tts = GTTSEngine()

        # Show available voices
        print("Available voices:")
        voices = tts.get_available_voices()
        for voice in voices[:5]:  # Show first 5 voices
            print(f"  ID: {voice['id']}, Name: {voice['name']}")

        # Show current settings
        print(f"\nCurrent settings: {tts.get_current_settings()}")

        # Test speech synthesis (will save to file)
        test_text = "Hello! This is a test of the gTTS engine. It works without any API keys!"
        print(f"\nCreating TTS for test text...")

        # Save to file for testing
        success = tts.save_to_file(test_text, "test_gtts.mp3")
        if success:
            print("✅ Audio file saved as test_gtts.mp3")
            print("🎵 No API keys needed - gTTS is completely free!")
        else:
            print("❌ Failed to save audio file")

        print("gTTS Engine test completed!")

    except Exception as e:
        print(f"Error during testing: {e}")


if __name__ == "__main__":
    main()