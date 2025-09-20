"""
Configuration Manager for TTS Settings

This module handles saving and loading configuration settings
for the text-to-speech automation tool.
"""

import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration settings for the TTS application."""
    
    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory to store config files (default: user's home/.tts-automation)
        """
        if config_dir is None:
            self.config_dir = Path.home() / ".tts-automation"
        else:
            self.config_dir = Path(config_dir)
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default config file paths
        self.default_config_file = self.config_dir / "default.json"
        self.user_config_file = self.config_dir / "user_settings.ini"
        
        logger.debug(f"Config directory: {self.config_dir}")
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default TTS settings."""
        return {
            'rate': 200,
            'volume': 0.9,
            'voice_id': 0,
            'chunk_size': 1000,
            'pause_between_chunks': 0.5
        }
    
    def save_config(self, settings: Dict[str, Any], 
                   config_file: Optional[Union[str, Path]] = None) -> bool:
        """
        Save configuration settings to file.
        
        Args:
            settings: Dictionary of settings to save
            config_file: Path to config file (default: default.json)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if config_file is None:
                config_file = self.default_config_file
            else:
                config_file = Path(config_file)
            
            # Ensure directory exists
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert any non-serializable values
            serializable_settings = {}
            for key, value in settings.items():
                if isinstance(value, (int, float, str, bool, type(None))):
                    serializable_settings[key] = value
                else:
                    serializable_settings[key] = str(value)
            
            # Add metadata
            config_data = {
                'version': '1.0',
                'settings': serializable_settings,
                'created_by': 'TTS Automation Tool'
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load_config(self, config_file: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
        """
        Load configuration settings from file.
        
        Args:
            config_file: Path to config file (default: default.json)
            
        Returns:
            dict: Configuration settings, or None if failed
        """
        try:
            if config_file is None:
                config_file = self.default_config_file
            else:
                config_file = Path(config_file)
            
            if not config_file.exists():
                logger.warning(f"Config file not found: {config_file}")
                return None
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Extract settings from config data
            if 'settings' in config_data:
                settings = config_data['settings']
            else:
                # Assume the entire file is settings (legacy format)
                settings = config_data
            
            logger.info(f"Configuration loaded from: {config_file}")
            return settings
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None
    
    def save_user_preferences(self, preferences: Dict[str, Any]) -> bool:
        """
        Save user preferences using INI format.
        
        Args:
            preferences: Dictionary of preferences to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config = configparser.ConfigParser()
            
            # Voice settings
            if any(key in preferences for key in ['voice_id', 'rate', 'volume']):
                config['Voice'] = {}
                if 'voice_id' in preferences:
                    config['Voice']['voice_id'] = str(preferences['voice_id'])
                if 'rate' in preferences:
                    config['Voice']['rate'] = str(preferences['rate'])
                if 'volume' in preferences:
                    config['Voice']['volume'] = str(preferences['volume'])
            
            # Processing settings
            if any(key in preferences for key in ['chunk_size', 'pause_between_chunks']):
                config['Processing'] = {}
                if 'chunk_size' in preferences:
                    config['Processing']['chunk_size'] = str(preferences['chunk_size'])
                if 'pause_between_chunks' in preferences:
                    config['Processing']['pause_between_chunks'] = str(preferences['pause_between_chunks'])
            
            # General settings
            general_settings = {}
            for key, value in preferences.items():
                if key not in ['voice_id', 'rate', 'volume', 'chunk_size', 'pause_between_chunks']:
                    general_settings[key] = str(value)
            
            if general_settings:
                config['General'] = general_settings
            
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            logger.info(f"User preferences saved to: {self.user_config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save user preferences: {e}")
            return False
    
    def load_user_preferences(self) -> Optional[Dict[str, Any]]:
        """
        Load user preferences from INI file.
        
        Returns:
            dict: User preferences, or None if failed
        """
        try:
            if not self.user_config_file.exists():
                logger.debug("User preferences file not found")
                return None
            
            config = configparser.ConfigParser()
            config.read(self.user_config_file, encoding='utf-8')
            
            preferences = {}
            
            # Load voice settings
            if 'Voice' in config:
                voice_section = config['Voice']
                if 'voice_id' in voice_section:
                    preferences['voice_id'] = int(voice_section['voice_id'])
                if 'rate' in voice_section:
                    preferences['rate'] = int(voice_section['rate'])
                if 'volume' in voice_section:
                    preferences['volume'] = float(voice_section['volume'])
            
            # Load processing settings
            if 'Processing' in config:
                proc_section = config['Processing']
                if 'chunk_size' in proc_section:
                    preferences['chunk_size'] = int(proc_section['chunk_size'])
                if 'pause_between_chunks' in proc_section:
                    preferences['pause_between_chunks'] = float(proc_section['pause_between_chunks'])
            
            # Load general settings
            if 'General' in config:
                for key, value in config['General'].items():
                    preferences[key] = value
            
            logger.info(f"User preferences loaded from: {self.user_config_file}")
            return preferences
            
        except Exception as e:
            logger.error(f"Failed to load user preferences: {e}")
            return None
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default settings.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            default_settings = self.get_default_settings()
            return self.save_config(default_settings)
            
        except Exception as e:
            logger.error(f"Failed to reset to defaults: {e}")
            return False
    
    def list_config_files(self) -> Dict[str, Path]:
        """
        List available configuration files.
        
        Returns:
            dict: Dictionary mapping config names to file paths
        """
        config_files = {}
        
        try:
            # Look for JSON config files
            for json_file in self.config_dir.glob("*.json"):
                config_files[json_file.stem] = json_file
            
            # Add INI files
            for ini_file in self.config_dir.glob("*.ini"):
                config_files[ini_file.stem] = ini_file
            
            return config_files
            
        except Exception as e:
            logger.error(f"Failed to list config files: {e}")
            return {}
    
    def delete_config(self, config_name: str) -> bool:
        """
        Delete a configuration file.
        
        Args:
            config_name: Name of the config to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_files = self.list_config_files()
            
            if config_name not in config_files:
                logger.error(f"Configuration '{config_name}' not found")
                return False
            
            config_file = config_files[config_name]
            config_file.unlink()
            
            logger.info(f"Configuration '{config_name}' deleted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete configuration '{config_name}': {e}")
            return False
    
    def export_config(self, output_file: Union[str, Path], 
                     config_name: Optional[str] = None) -> bool:
        """
        Export configuration to a file.
        
        Args:
            output_file: Path to export file
            config_name: Name of config to export (default: current default)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if config_name is None:
                settings = self.load_config()
            else:
                config_files = self.list_config_files()
                if config_name not in config_files:
                    logger.error(f"Configuration '{config_name}' not found")
                    return False
                settings = self.load_config(config_files[config_name])
            
            if settings is None:
                logger.error("No settings to export")
                return False
            
            return self.save_config(settings, output_file)
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False


def main():
    """Test the configuration manager."""
    print("Configuration Manager Test")
    print("==========================")
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Test default settings
    print("Default settings:")
    defaults = config_manager.get_default_settings()
    for key, value in defaults.items():
        print(f"  {key}: {value}")
    
    # Test saving configuration
    print("\nSaving test configuration...")
    test_settings = {
        'rate': 180,
        'volume': 0.8,
        'voice_id': 1,
        'chunk_size': 500
    }
    
    success = config_manager.save_config(test_settings, "test_config.json")
    print(f"Save result: {success}")
    
    # Test loading configuration
    print("\nLoading test configuration...")
    loaded_settings = config_manager.load_config("test_config.json")
    if loaded_settings:
        print("Loaded settings:")
        for key, value in loaded_settings.items():
            print(f"  {key}: {value}")
    
    # Test user preferences
    print("\nSaving user preferences...")
    prefs = {
        'voice_id': 2,
        'rate': 220,
        'favorite_format': 'pdf'
    }
    config_manager.save_user_preferences(prefs)
    
    print("Loading user preferences...")
    loaded_prefs = config_manager.load_user_preferences()
    if loaded_prefs:
        print("Loaded preferences:")
        for key, value in loaded_prefs.items():
            print(f"  {key}: {value}")
    
    # List config files
    print("\nAvailable configuration files:")
    config_files = config_manager.list_config_files()
    for name, path in config_files.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()