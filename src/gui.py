"""
Graphical User Interface for Text-to-Speech Automation

This module provides a user-friendly GUI using tkinter for the TTS automation tool.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# Import our modules
from tts_engine import TTSEngine
from document_readers import UniversalDocumentReader
from config_manager import ConfigManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSGui:
    """Main GUI application for text-to-speech automation."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("Text-to-Speech Automation Tool")
        self.root.geometry("800x700")
        
        # Initialize components
        self.tts_engine = None
        self.config_manager = ConfigManager()
        self.current_thread = None
        self.is_speaking = False
        
        # GUI variables
        self.voice_var = tk.StringVar()
        self.rate_var = tk.IntVar(value=200)
        self.volume_var = tk.DoubleVar(value=0.9)
        self.chunk_size_var = tk.IntVar(value=1000)
        self.pause_var = tk.DoubleVar(value=0.5)
        
        # Create GUI elements
        self.create_widgets()
        
        # Initialize TTS engine
        self.initialize_tts()
        
        # Load user preferences
        self.load_preferences()
    
    def create_widgets(self):
        """Create and layout GUI widgets."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab
        self.main_frame = ttk.Frame(notebook)
        notebook.add(self.main_frame, text="Main")
        
        # Settings tab
        self.settings_frame = ttk.Frame(notebook)
        notebook.add(self.settings_frame, text="Settings")
        
        # Batch tab
        self.batch_frame = ttk.Frame(notebook)
        notebook.add(self.batch_frame, text="Batch Processing")
        
        # Create main tab widgets
        self.create_main_tab()
        
        # Create settings tab widgets
        self.create_settings_tab()
        
        # Create batch tab widgets
        self.create_batch_tab()
        
        # Create status bar
        self.create_status_bar()
    
    def create_main_tab(self):
        """Create widgets for the main tab."""
        # Input section
        input_frame = ttk.LabelFrame(self.main_frame, text="Input", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Text input
        text_frame = ttk.Frame(input_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(text_frame, text="Enter text to speak:").pack(anchor=tk.W)
        self.text_area = scrolledtext.ScrolledText(
            text_frame, 
            height=10, 
            wrap=tk.WORD,
            font=("Segoe UI", 10)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # File input
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="Or select a file:").pack(anchor=tk.W)
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(file_select_frame, text="Browse", command=self.browse_file).pack(side=tk.RIGHT)
        
        # URL input
        url_frame = ttk.Frame(input_frame)
        url_frame.pack(fill=tk.X)
        
        ttk.Label(url_frame, text="Or enter a URL:").pack(anchor=tk.W)
        self.url_var = tk.StringVar()
        ttk.Entry(url_frame, textvariable=self.url_var).pack(fill=tk.X, pady=(5, 0))
        
        # Control section
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.speak_button = ttk.Button(
            button_frame, 
            text="Speak", 
            command=self.start_speaking
        )
        self.speak_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(
            button_frame, 
            text="Stop", 
            command=self.stop_speaking,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Save Audio", 
            command=self.save_audio
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear_inputs
        ).pack(side=tk.RIGHT)
    
    def create_settings_tab(self):
        """Create widgets for the settings tab."""
        # Voice settings
        voice_frame = ttk.LabelFrame(self.settings_frame, text="Voice Settings", padding=10)
        voice_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Voice selection
        ttk.Label(voice_frame, text="Voice:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_var, state="readonly")
        self.voice_combo.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=2)
        self.voice_combo.bind("<<ComboboxSelected>>", self.on_voice_changed)
        
        # Rate setting
        ttk.Label(voice_frame, text="Speed (WPM):").grid(row=1, column=0, sticky=tk.W, pady=2)
        rate_frame = ttk.Frame(voice_frame)
        rate_frame.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=2)
        
        self.rate_scale = ttk.Scale(
            rate_frame, 
            from_=50, 
            to=400, 
            variable=self.rate_var,
            orient=tk.HORIZONTAL,
            command=self.on_rate_changed
        )
        self.rate_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.rate_label = ttk.Label(rate_frame, text="200")
        self.rate_label.pack(side=tk.RIGHT)
        
        # Volume setting
        ttk.Label(voice_frame, text="Volume:").grid(row=2, column=0, sticky=tk.W, pady=2)
        volume_frame = ttk.Frame(voice_frame)
        volume_frame.grid(row=2, column=1, sticky=tk.EW, padx=(10, 0), pady=2)
        
        self.volume_scale = ttk.Scale(
            volume_frame,
            from_=0.0,
            to=1.0,
            variable=self.volume_var,
            orient=tk.HORIZONTAL,
            command=self.on_volume_changed
        )
        self.volume_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.volume_label = ttk.Label(volume_frame, text="0.9")
        self.volume_label.pack(side=tk.RIGHT)
        
        voice_frame.columnconfigure(1, weight=1)
        
        # Processing settings
        process_frame = ttk.LabelFrame(self.settings_frame, text="Processing Settings", padding=10)
        process_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(process_frame, text="Chunk Size (chars):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(
            process_frame,
            from_=100,
            to=5000,
            textvariable=self.chunk_size_var,
            width=10
        ).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        ttk.Label(process_frame, text="Pause (seconds):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(
            process_frame,
            from_=0.0,
            to=5.0,
            increment=0.1,
            textvariable=self.pause_var,
            width=10
        ).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Configuration buttons
        config_frame = ttk.LabelFrame(self.settings_frame, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X)
        
        config_button_frame = ttk.Frame(config_frame)
        config_button_frame.pack(fill=tk.X)
        
        ttk.Button(
            config_button_frame,
            text="Save Settings",
            command=self.save_settings
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            config_button_frame,
            text="Load Settings",
            command=self.load_settings
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            config_button_frame,
            text="Reset to Default",
            command=self.reset_settings
        ).pack(side=tk.RIGHT)
    
    def create_batch_tab(self):
        """Create widgets for the batch processing tab."""
        # File list
        list_frame = ttk.LabelFrame(self.batch_frame, text="Files to Process", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # File listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(list_container, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Batch control buttons
        batch_button_frame = ttk.Frame(list_frame)
        batch_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            batch_button_frame,
            text="Add Files",
            command=self.add_batch_files
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            batch_button_frame,
            text="Remove Selected",
            command=self.remove_batch_files
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            batch_button_frame,
            text="Clear All",
            command=self.clear_batch_files
        ).pack(side=tk.LEFT)
        
        # Batch processing controls
        batch_control_frame = ttk.LabelFrame(self.batch_frame, text="Batch Controls", padding=10)
        batch_control_frame.pack(fill=tk.X)
        
        self.batch_progress = ttk.Progressbar(
            batch_control_frame,
            mode='determinate'
        )
        self.batch_progress.pack(fill=tk.X, pady=(0, 10))
        
        batch_buttons = ttk.Frame(batch_control_frame)
        batch_buttons.pack(fill=tk.X)
        
        self.batch_process_button = ttk.Button(
            batch_buttons,
            text="Process All Files",
            command=self.start_batch_processing
        )
        self.batch_process_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.batch_stop_button = ttk.Button(
            batch_buttons,
            text="Stop Batch",
            command=self.stop_batch_processing,
            state=tk.DISABLED
        )
        self.batch_stop_button.pack(side=tk.LEFT)
    
    def create_status_bar(self):
        """Create the status bar at the bottom."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Progress bar for long operations
        self.progress = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def initialize_tts(self):
        """Initialize the TTS engine."""
        try:
            self.tts_engine = TTSEngine()
            self.populate_voice_list()
            self.status_var.set("TTS Engine initialized")
            logger.info("TTS Engine initialized in GUI")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize TTS engine: {e}")
            logger.error(f"Failed to initialize TTS engine: {e}")
    
    def populate_voice_list(self):
        """Populate the voice selection combo box."""
        if not self.tts_engine:
            return
        
        try:
            voices = self.tts_engine.get_available_voices()
            voice_names = [f"{voice['id']}: {voice['name']}" for voice in voices]
            self.voice_combo['values'] = voice_names
            
            if voice_names:
                self.voice_combo.set(voice_names[0])
                self.voice_var.set(voice_names[0])
            
        except Exception as e:
            logger.error(f"Failed to populate voice list: {e}")
    
    def browse_file(self):
        """Open file browser to select a document."""
        supported_types = [
            ("All supported", "*.txt;*.pdf;*.docx;*.pptx"),
            ("Text files", "*.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("PowerPoint presentations", "*.pptx")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select document to read",
            filetypes=supported_types
        )
        
        if filename:
            self.file_path_var.set(filename)
            self.text_area.delete(1.0, tk.END)  # Clear text area when file is selected
    
    def get_input_text(self) -> Optional[str]:
        """Get text from the current input source."""
        # Check for direct text input first
        text_content = self.text_area.get(1.0, tk.END).strip()
        if text_content:
            return text_content
        
        # Check for file input
        file_path = self.file_path_var.get().strip()
        if file_path:
            self.status_var.set("Reading file...")
            self.progress.start()
            try:
                content = UniversalDocumentReader.read_file(file_path)
                if content:
                    return content
                else:
                    messagebox.showerror("Error", f"Failed to read file: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading file: {e}")
            finally:
                self.progress.stop()
        
        # Check for URL input
        url = self.url_var.get().strip()
        if url:
            self.status_var.set("Reading URL...")
            self.progress.start()
            try:
                content = UniversalDocumentReader.read_url(url)
                if content:
                    return content
                else:
                    messagebox.showerror("Error", f"Failed to read URL: {url}")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading URL: {e}")
            finally:
                self.progress.stop()
        
        return None
    
    def start_speaking(self):
        """Start text-to-speech in a separate thread."""
        if self.is_speaking:
            return
        
        text = self.get_input_text()
        if not text:
            messagebox.showwarning("Warning", "Please enter text, select a file, or enter a URL.")
            return
        
        self.is_speaking = True
        self.speak_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Speaking...")
        
        # Apply current settings
        self.apply_current_settings()
        
        # Start speaking in a separate thread
        self.current_thread = threading.Thread(
            target=self._speak_thread,
            args=(text,),
            daemon=True
        )
        self.current_thread.start()
    
    def _speak_thread(self, text: str):
        """Thread function for speaking text."""
        try:
            success = self.tts_engine.speak_text(text)
            
            # Update UI in main thread
            self.root.after(0, self._speaking_finished, success)
            
        except Exception as e:
            self.root.after(0, self._speaking_error, str(e))
    
    def _speaking_finished(self, success: bool):
        """Handle speaking completion in the main thread."""
        self.is_speaking = False
        self.speak_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if success:
            self.status_var.set("Speaking completed")
        else:
            self.status_var.set("Speaking failed")
            messagebox.showerror("Error", "Failed to speak text")
    
    def _speaking_error(self, error_message: str):
        """Handle speaking error in the main thread."""
        self.is_speaking = False
        self.speak_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Error occurred")
        messagebox.showerror("Error", f"Speaking error: {error_message}")
    
    def stop_speaking(self):
        """Stop the current speech."""
        if self.tts_engine:
            self.tts_engine.stop_speaking()
        
        self.is_speaking = False
        self.speak_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Speaking stopped")
    
    def save_audio(self):
        """Save text as audio file."""
        text = self.get_input_text()
        if not text:
            messagebox.showwarning("Warning", "Please enter text, select a file, or enter a URL.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save audio as...",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if filename:
            self.status_var.set("Saving audio...")
            self.progress.start()
            
            try:
                self.apply_current_settings()
                success = self.tts_engine.save_to_file(text, filename)
                
                if success:
                    self.status_var.set("Audio saved successfully")
                    messagebox.showinfo("Success", f"Audio saved to: {filename}")
                else:
                    self.status_var.set("Failed to save audio")
                    messagebox.showerror("Error", "Failed to save audio file")
                    
            except Exception as e:
                self.status_var.set("Error saving audio")
                messagebox.showerror("Error", f"Error saving audio: {e}")
            
            finally:
                self.progress.stop()
    
    def clear_inputs(self):
        """Clear all input fields."""
        self.text_area.delete(1.0, tk.END)
        self.file_path_var.set("")
        self.url_var.set("")
        self.status_var.set("Inputs cleared")
    
    def apply_current_settings(self):
        """Apply current settings to the TTS engine."""
        if not self.tts_engine:
            return
        
        try:
            # Parse voice ID from combo box selection
            voice_selection = self.voice_var.get()
            if voice_selection:
                voice_id = int(voice_selection.split(":")[0])
                self.tts_engine.set_voice(voice_id)
            
            self.tts_engine.set_rate(int(self.rate_var.get()))
            self.tts_engine.set_volume(self.volume_var.get())
            
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
    
    def on_voice_changed(self, event=None):
        """Handle voice selection change."""
        self.apply_current_settings()
    
    def on_rate_changed(self, value):
        """Handle rate change."""
        rate = int(float(value))
        self.rate_label.config(text=str(rate))
        if self.tts_engine:
            self.tts_engine.set_rate(rate)
    
    def on_volume_changed(self, value):
        """Handle volume change."""
        volume = float(value)
        self.volume_label.config(text=f"{volume:.1f}")
        if self.tts_engine:
            self.tts_engine.set_volume(volume)
    
    def save_settings(self):
        """Save current settings to configuration."""
        try:
            settings = {
                'voice_id': int(self.voice_var.get().split(":")[0]) if self.voice_var.get() else 0,
                'rate': self.rate_var.get(),
                'volume': self.volume_var.get(),
                'chunk_size': self.chunk_size_var.get(),
                'pause_between_chunks': self.pause_var.get()
            }
            
            success = self.config_manager.save_config(settings)
            
            if success:
                self.status_var.set("Settings saved")
                messagebox.showinfo("Success", "Settings saved successfully")
            else:
                messagebox.showerror("Error", "Failed to save settings")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load settings from configuration file."""
        filename = filedialog.askopenfilename(
            title="Load settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                settings = self.config_manager.load_config(filename)
                if settings:
                    self.apply_loaded_settings(settings)
                    self.status_var.set("Settings loaded")
                    messagebox.showinfo("Success", "Settings loaded successfully")
                else:
                    messagebox.showerror("Error", "Failed to load settings")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error loading settings: {e}")
    
    def apply_loaded_settings(self, settings: Dict[str, Any]):
        """Apply loaded settings to the GUI."""
        try:
            if 'voice_id' in settings:
                voice_id = settings['voice_id']
                voices = self.voice_combo['values']
                for voice in voices:
                    if voice.startswith(f"{voice_id}:"):
                        self.voice_var.set(voice)
                        break
            
            if 'rate' in settings:
                self.rate_var.set(settings['rate'])
            
            if 'volume' in settings:
                self.volume_var.set(settings['volume'])
            
            if 'chunk_size' in settings:
                self.chunk_size_var.set(settings['chunk_size'])
            
            if 'pause_between_chunks' in settings:
                self.pause_var.set(settings['pause_between_chunks'])
            
            self.apply_current_settings()
            
        except Exception as e:
            logger.error(f"Error applying loaded settings: {e}")
    
    def reset_settings(self):
        """Reset settings to default values."""
        try:
            defaults = self.config_manager.get_default_settings()
            self.apply_loaded_settings(defaults)
            self.status_var.set("Settings reset to defaults")
            messagebox.showinfo("Success", "Settings reset to defaults")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error resetting settings: {e}")
    
    def load_preferences(self):
        """Load user preferences on startup."""
        try:
            preferences = self.config_manager.load_user_preferences()
            if preferences:
                self.apply_loaded_settings(preferences)
                logger.info("User preferences loaded")
        except Exception as e:
            logger.warning(f"Failed to load user preferences: {e}")
    
    def save_preferences_on_exit(self):
        """Save current settings as user preferences."""
        try:
            settings = {
                'voice_id': int(self.voice_var.get().split(":")[0]) if self.voice_var.get() else 0,
                'rate': self.rate_var.get(),
                'volume': self.volume_var.get(),
                'chunk_size': self.chunk_size_var.get(),
                'pause_between_chunks': self.pause_var.get()
            }
            
            self.config_manager.save_user_preferences(settings)
            logger.info("User preferences saved")
            
        except Exception as e:
            logger.warning(f"Failed to save user preferences: {e}")
    
    def add_batch_files(self):
        """Add files to batch processing list."""
        filenames = filedialog.askopenfilenames(
            title="Select files for batch processing",
            filetypes=[
                ("All supported", "*.txt;*.pdf;*.docx;*.pptx"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("Word documents", "*.docx"),
                ("PowerPoint presentations", "*.pptx")
            ]
        )
        
        for filename in filenames:
            if filename not in self.file_listbox.get(0, tk.END):
                self.file_listbox.insert(tk.END, filename)
        
        self.status_var.set(f"Added {len(filenames)} files to batch")
    
    def remove_batch_files(self):
        """Remove selected files from batch list."""
        selected_indices = list(self.file_listbox.curselection())
        selected_indices.reverse()  # Remove from end to avoid index issues
        
        for index in selected_indices:
            self.file_listbox.delete(index)
        
        self.status_var.set(f"Removed {len(selected_indices)} files from batch")
    
    def clear_batch_files(self):
        """Clear all files from batch list."""
        count = self.file_listbox.size()
        self.file_listbox.delete(0, tk.END)
        self.status_var.set(f"Cleared {count} files from batch")
    
    def start_batch_processing(self):
        """Start batch processing of files."""
        files = list(self.file_listbox.get(0, tk.END))
        if not files:
            messagebox.showwarning("Warning", "No files selected for batch processing")
            return
        
        self.batch_process_button.config(state=tk.DISABLED)
        self.batch_stop_button.config(state=tk.NORMAL)
        self.batch_progress.config(maximum=len(files))
        self.batch_progress['value'] = 0
        
        # Start batch processing in separate thread
        self.current_thread = threading.Thread(
            target=self._batch_process_thread,
            args=(files,),
            daemon=True
        )
        self.current_thread.start()
    
    def _batch_process_thread(self, files: List[str]):
        """Thread function for batch processing."""
        try:
            success_count = 0
            
            for i, file_path in enumerate(files):
                if not self.is_speaking:  # Check if stopped
                    break
                
                # Update progress in main thread
                self.root.after(0, self._update_batch_progress, i, file_path)
                
                try:
                    content = UniversalDocumentReader.read_file(file_path)
                    if content:
                        success = self.tts_engine.speak_text(content)
                        if success:
                            success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
            
            # Batch processing completed
            self.root.after(0, self._batch_processing_finished, success_count, len(files))
            
        except Exception as e:
            self.root.after(0, self._batch_processing_error, str(e))
    
    def _update_batch_progress(self, index: int, filename: str):
        """Update batch processing progress."""
        self.batch_progress['value'] = index
        self.status_var.set(f"Processing: {Path(filename).name}")
    
    def _batch_processing_finished(self, success_count: int, total_count: int):
        """Handle batch processing completion."""
        self.batch_process_button.config(state=tk.NORMAL)
        self.batch_stop_button.config(state=tk.DISABLED)
        self.batch_progress['value'] = total_count
        self.status_var.set(f"Batch completed: {success_count}/{total_count} files processed")
        
        messagebox.showinfo(
            "Batch Processing Complete",
            f"Successfully processed {success_count} out of {total_count} files."
        )
    
    def _batch_processing_error(self, error_message: str):
        """Handle batch processing error."""
        self.batch_process_button.config(state=tk.DISABLED)
        self.batch_stop_button.config(state=tk.DISABLED)
        self.status_var.set("Batch processing error")
        messagebox.showerror("Error", f"Batch processing error: {error_message}")
    
    def stop_batch_processing(self):
        """Stop batch processing."""
        self.is_speaking = False
        if self.tts_engine:
            self.tts_engine.stop_speaking()
        
        self.batch_process_button.config(state=tk.NORMAL)
        self.batch_stop_button.config(state=tk.DISABLED)
        self.status_var.set("Batch processing stopped")
    
    def on_closing(self):
        """Handle application closing."""
        try:
            # Stop any ongoing speech
            if self.is_speaking:
                self.stop_speaking()
            
            # Save user preferences
            self.save_preferences_on_exit()
            
            # Destroy the window
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error during application closing: {e}")
            self.root.destroy()
    
    def run(self):
        """Start the GUI application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def main():
    """Main entry point for the GUI application."""
    try:
        app = TTSGui()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {e}")
        logger.error(f"Failed to start GUI application: {e}")


if __name__ == "__main__":
    main()