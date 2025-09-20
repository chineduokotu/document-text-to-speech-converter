"""
Command Line Interface for Text-to-Speech Automation

This module provides a user-friendly CLI for the TTS automation tool
with options for file input, voice settings, and output controls.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
import logging

# Import our modules
from tts_engine import TTSEngine
from document_readers import UniversalDocumentReader
from config_manager import ConfigManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class TTSCommandLine:
    """Command-line interface for TTS automation."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.tts_engine = None
        self.config = ConfigManager()
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description='Text-to-Speech Automation Tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Examples:
  %(prog)s --file document.pdf                    # Convert PDF to speech
  %(prog)s --text "Hello world"                   # Convert text to speech
  %(prog)s --url https://example.com              # Convert web page to speech
  %(prog)s --file doc.txt --voice 1 --rate 150   # Use specific voice and rate
  %(prog)s --batch *.txt                          # Convert multiple files
  %(prog)s --list-voices                          # Show available voices
            '''
        )
        
        # Input options (mutually exclusive)
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument(
            '--file', '-f',
            type=str,
            help='Path to document file (PDF, DOCX, PPTX, TXT)'
        )
        input_group.add_argument(
            '--text', '-t',
            type=str,
            help='Text to convert to speech'
        )
        input_group.add_argument(
            '--url', '-u',
            type=str,
            help='URL to read content from'
        )
        input_group.add_argument(
            '--batch', '-b',
            type=str,
            nargs='+',
            help='Multiple files to process (supports wildcards)'
        )
        input_group.add_argument(
            '--list-voices',
            action='store_true',
            help='List available voices and exit'
        )
        
        # Voice settings
        voice_group = parser.add_argument_group('voice settings')
        voice_group.add_argument(
            '--voice', '-v',
            type=int,
            help='Voice ID to use (see --list-voices)'
        )
        voice_group.add_argument(
            '--rate', '-r',
            type=int,
            help='Speech rate in words per minute (50-400, default: 200)'
        )
        voice_group.add_argument(
            '--volume',
            type=float,
            help='Speech volume (0.0-1.0, default: 0.9)'
        )
        
        # Processing options
        process_group = parser.add_argument_group('processing options')
        process_group.add_argument(
            '--chunk-size',
            type=int,
            default=1000,
            help='Characters per chunk for long texts (default: 1000)'
        )
        process_group.add_argument(
            '--pause',
            type=float,
            default=0.5,
            help='Pause between chunks in seconds (default: 0.5)'
        )
        process_group.add_argument(
            '--no-wait',
            action='store_true',
            help='Don\'t wait for speech to complete before continuing'
        )
        
        # Output options
        output_group = parser.add_argument_group('output options')
        output_group.add_argument(
            '--save-audio',
            type=str,
            help='Save speech as audio file (experimental)'
        )
        output_group.add_argument(
            '--save-config',
            action='store_true',
            help='Save current settings as default'
        )
        output_group.add_argument(
            '--load-config',
            type=str,
            help='Load settings from config file'
        )
        
        # Other options
        parser.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Suppress informational messages'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        
        return parser
    
    def setup_logging(self, quiet: bool = False, verbose: bool = False):
        """Configure logging based on options."""
        if quiet:
            logging.getLogger().setLevel(logging.WARNING)
        elif verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.INFO)
    
    def initialize_tts(self, args) -> bool:
        """Initialize the TTS engine with settings."""
        try:
            self.tts_engine = TTSEngine()
            
            # Load config if specified
            if args.load_config:
                settings = self.config.load_config(args.load_config)
                if settings:
                    self.tts_engine.apply_settings(settings)
                    logger.info(f"Loaded configuration from {args.load_config}")
            
            # Apply command line settings
            settings = {}
            if args.voice is not None:
                settings['voice_id'] = args.voice
            if args.rate is not None:
                settings['rate'] = args.rate
            if args.volume is not None:
                settings['volume'] = args.volume
            
            if settings:
                self.tts_engine.apply_settings(settings)
            
            # Save config if requested
            if args.save_config:
                current_settings = self.tts_engine.get_current_settings()
                self.config.save_config(current_settings)
                logger.info("Configuration saved as default")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            return False
    
    def list_voices(self) -> bool:
        """List available voices."""
        try:
            if not self.initialize_tts(argparse.Namespace()):
                return False
            
            voices = self.tts_engine.get_available_voices()
            
            print("Available Voices:")
            print("=================")
            for voice in voices:
                print(f"ID: {voice['id']:2d} | Name: {voice['name']}")
                if voice['languages'] != ['Unknown']:
                    print(f"      | Languages: {', '.join(voice['languages'])}")
                if voice['gender'] != 'Unknown':
                    print(f"      | Gender: {voice['gender']}")
                print()
            
            current = self.tts_engine.get_current_settings()
            if current.get('voice_id', -1) >= 0:
                print(f"Current voice: ID {current['voice_id']} - {current['voice_name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return False
    
    def process_text(self, text: str, args) -> bool:
        """Process and speak text."""
        try:
            if not text.strip():
                logger.error("No text to process")
                return False
            
            logger.info(f"Processing text ({len(text)} characters)")
            
            if args.save_audio:
                return self.tts_engine.save_to_file(text, args.save_audio)
            else:
                return self.tts_engine.speak_text(
                    text, 
                    wait_until_done=not args.no_wait
                )
                
        except Exception as e:
            logger.error(f"Failed to process text: {e}")
            return False
    
    def process_file(self, file_path: str, args) -> bool:
        """Process and speak file content."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            logger.info(f"Reading file: {file_path}")
            content = UniversalDocumentReader.read_file(file_path)
            
            if not content:
                logger.error(f"Failed to extract content from {file_path}")
                return False
            
            logger.info(f"Extracted {len(content)} characters from {file_path.name}")
            
            if args.save_audio:
                output_path = args.save_audio
                if output_path == "auto":
                    output_path = file_path.stem + ".wav"
                return self.tts_engine.save_to_file(content, output_path)
            else:
                return self.tts_engine.speak_file(
                    file_path,
                    chunk_size=args.chunk_size,
                    pause_between_chunks=args.pause
                )
                
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            return False
    
    def process_url(self, url: str, args) -> bool:
        """Process and speak web content."""
        try:
            logger.info(f"Reading URL: {url}")
            content = UniversalDocumentReader.read_url(url)
            
            if not content:
                logger.error(f"Failed to extract content from {url}")
                return False
            
            logger.info(f"Extracted {len(content)} characters from URL")
            
            if args.save_audio:
                return self.tts_engine.save_to_file(content, args.save_audio)
            else:
                return self.tts_engine.speak_text(
                    content,
                    wait_until_done=not args.no_wait
                )
                
        except Exception as e:
            logger.error(f"Failed to process URL {url}: {e}")
            return False
    
    def process_batch(self, file_patterns: List[str], args) -> bool:
        """Process multiple files."""
        try:
            import glob
            
            all_files = []
            for pattern in file_patterns:
                files = glob.glob(pattern)
                all_files.extend(files)
            
            if not all_files:
                logger.error("No files found matching the patterns")
                return False
            
            logger.info(f"Processing {len(all_files)} files")
            
            success_count = 0
            for i, file_path in enumerate(all_files):
                logger.info(f"Processing file {i+1}/{len(all_files)}: {file_path}")
                
                if self.process_file(file_path, args):
                    success_count += 1
                else:
                    logger.warning(f"Failed to process: {file_path}")
            
            logger.info(f"Successfully processed {success_count}/{len(all_files)} files")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to process batch: {e}")
            return False
    
    def run(self, args=None) -> int:
        """Run the CLI application."""
        try:
            parser = self.create_parser()
            args = parser.parse_args(args)
            
            # Setup logging
            self.setup_logging(args.quiet, args.verbose)
            
            # Handle list voices command
            if args.list_voices:
                return 0 if self.list_voices() else 1
            
            # Initialize TTS engine
            if not self.initialize_tts(args):
                return 1
            
            # Process input
            success = False
            
            if args.text:
                success = self.process_text(args.text, args)
            elif args.file:
                success = self.process_file(args.file, args)
            elif args.url:
                success = self.process_url(args.url, args)
            elif args.batch:
                success = self.process_batch(args.batch, args)
            
            return 0 if success else 1
            
        except KeyboardInterrupt:
            logger.info("Operation cancelled by user")
            if self.tts_engine:
                self.tts_engine.stop_speaking()
            return 1
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = TTSCommandLine()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())