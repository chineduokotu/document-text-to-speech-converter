"""
Google Cloud Text-to-Speech Engine Module

This module provides TTS functionality using Google Cloud Text-to-Speech API,
which works on cloud platforms where local TTS engines are not available.
"""

import os
from typing import List, Dict, Optional, Union
from pathlib import Path
import logging
from google.cloud import texttospeech
from google.oauth2 import service_account

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleTTSEngine:
    """Google Cloud Text-to-Speech engine class."""

    def __init__(self):
        """Initialize the Google Cloud TTS engine."""
        try:
            # Try to get credentials from environment variable or file
            credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

            if credentials_path and Path(credentials_path).exists():
                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                self.client = texttospeech.TextToSpeechClient(credentials=credentials)
            else:
                # Try to use Application Default Credentials
                self.client = texttospeech.TextToSpeechClient()
                logger.warning("Using Application Default Credentials. For production, set GOOGLE_APPLICATION_CREDENTIALS environment variable.")

            # Default voice settings
            self.default_voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-D",
                ssml_gender=texttospeech.SsmlVoiceGender.MALE,
            )

            self.default_audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,  # 1.0 = normal speed
                pitch=0.0,  # 0.0 = normal pitch
            )

            self.default_settings = {
                'rate': 1.0,  # Speaking rate (0.25 to 4.0)
                'volume': 1.0,  # Volume gain (0.0 to 16.0, but we'll use 0.0-1.0 range)
                'voice_name': 'en-US-Neural2-D',
                'language_code': 'en-US'
            }

            logger.info("Google Cloud TTS Engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud TTS engine: {e}")
            logger.error("Make sure you have set up Google Cloud credentials properly.")
            logger.error("See: https://cloud.google.com/text-to-speech/docs/quickstart")
            raise

    def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available voices from Google Cloud TTS."""
        try:
            # Get list of available voices
            response = self.client.list_voices()
            voices = response.voices

            voice_list = []
            for i, voice in enumerate(voices[:20]):  # Limit to first 20 voices
                voice_info = {
                    'id': i,
                    'name': voice.name,
                    'language_codes': voice.language_codes,
                    'ssml_gender': voice.ssml_gender,
                    'natural_sample_rate_hertz': voice.natural_sample_rate_hertz
                }
                voice_list.append(voice_info)

            return voice_list

        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
            return []

    def set_voice(self, voice_id: int) -> bool:
        """Set the voice by ID."""
        try:
            voices = self.get_available_voices()
            if 0 <= voice_id < len(voices):
                voice_info = voices[voice_id]
                self.default_voice = texttospeech.VoiceSelectionParams(
                    language_code=voice_info['language_codes'][0],
                    name=voice_info['name'],
                    ssml_gender=voice_info['ssml_gender'],
                )
                logger.info(f"Voice set to: {voice_info['name']}")
                return True
            else:
                logger.warning(f"Invalid voice ID: {voice_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")
            return False

    def set_rate(self, rate: float) -> bool:
        """Set the speech rate (0.25 to 4.0)."""
        try:
            if 0.25 <= rate <= 4.0:
                self.default_audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=rate,
                    pitch=self.default_audio_config.pitch if hasattr(self.default_audio_config, 'pitch') else 0.0,
                )
                logger.info(f"Speech rate set to: {rate}")
                return True
            else:
                logger.warning(f"Rate {rate} is outside valid range (0.25-4.0)")
                return False
        except Exception as e:
            logger.error(f"Failed to set rate: {e}")
            return False

    def set_volume(self, volume: float) -> bool:
        """Set the speech volume (0.0 to 16.0, but we'll use 0.0-1.0 range)."""
        try:
            if 0.0 <= volume <= 1.0:
                # Convert 0.0-1.0 range to 0.0-16.0 range for Google TTS
                google_volume = volume * 16.0
                self.default_audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=self.default_audio_config.speaking_rate if hasattr(self.default_audio_config, 'speaking_rate') else 1.0,
                    pitch=self.default_audio_config.pitch if hasattr(self.default_audio_config, 'pitch') else 0.0,
                    volume_gain_db=google_volume,
                )
                logger.info(f"Volume set to: {volume}")
                return True
            else:
                logger.warning(f"Volume {volume} is outside valid range (0.0-1.0)")
                return False
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return False

    def apply_settings(self, settings: Dict[str, Union[int, float, str]]) -> None:
        """Apply multiple settings at once."""
        if 'rate' in settings:
            self.set_rate(float(settings['rate']))
        if 'volume' in settings:
            self.set_volume(float(settings['volume']))
        if 'voice_id' in settings:
            self.set_voice(int(settings['voice_id']))

    def speak_text(self, text: str, wait_until_done: bool = True) -> bool:
        """
        Convert text to speech using Google Cloud TTS.

        Args:
            text: The text to convert to speech
            wait_until_done: Whether to wait for speech to complete (not applicable for cloud TTS)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not text.strip():
                logger.warning("Empty text provided for speech")
                return False

            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.default_voice,
                audio_config=self.default_audio_config
            )

            # For cloud TTS, we can't "speak" directly, but we can save to file
            # In a real application, you'd stream this to the client
            logger.info(f"Successfully synthesized speech for text: {text[:50]}{'...' if len(text) > 50 else ''}")
            return True

        except Exception as e:
            logger.error(f"Failed to synthesize speech: {e}")
            return False

    def save_to_file(self, text: str, output_path: Union[str, Path]) -> bool:
        """
        Save text-to-speech as an audio file using Google Cloud TTS.
        """
        try:
            if not text.strip():
                logger.warning("Empty text provided for speech")
                return False

            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.default_voice,
                audio_config=self.default_audio_config
            )

            # Save the audio to file
            output_path = Path(output_path)
            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            logger.info(f"Audio saved to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            return False

    def get_current_settings(self) -> Dict[str, Union[int, float, str]]:
        """Get current TTS settings."""
        try:
            return {
                'rate': self.default_audio_config.speaking_rate,
                'volume': (self.default_audio_config.volume_gain_db / 16.0) if hasattr(self.default_audio_config, 'volume_gain_db') else 1.0,
                'voice_name': self.default_voice.name,
                'language_code': self.default_voice.language_code
            }
        except Exception as e:
            logger.error(f"Failed to get current settings: {e}")
            return {}

    def stop_speaking(self) -> None:
        """Stop the current speech (not applicable for cloud TTS)."""
        logger.info("Stop speaking not applicable for Google Cloud TTS")


def main():
    """Test the Google Cloud TTS engine functionality."""
    try:
        # Initialize engine
        tts = GoogleTTSEngine()

        # Show available voices
        print("Available voices:")
        voices = tts.get_available_voices()
        for voice in voices[:5]:  # Show first 5 voices
            print(f"  ID: {voice['id']}, Name: {voice['name']}, Language: {voice['language_codes'][0]}")

        # Show current settings
        print(f"\nCurrent settings: {tts.get_current_settings()}")

        # Test speech synthesis (will save to file instead of speaking)
        test_text = "Hello! This is a test of the Google Cloud Text-to-Speech engine."
        print(f"\nSynthesizing test text...")

        # Save to file for testing
        success = tts.save_to_file(test_text, "test_google_tts.mp3")
        if success:
            print("✅ Audio file saved as test_google_tts.mp3")
        else:
            print("❌ Failed to save audio file")

        print("Google Cloud TTS Engine test completed!")

    except Exception as e:
        print(f"Error during testing: {e}")
        print("Make sure you have set up Google Cloud credentials properly.")


if __name__ == "__main__":
    main()