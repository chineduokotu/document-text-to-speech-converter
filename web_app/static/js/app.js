// Text-to-Speech Web App JavaScript
class TTSApp {
    constructor() {
        this.voices = [];
        this.settings = {
            voice_id: 0,
            rate: 200,
            volume: 0.9
        };
        this.currentTask = null;
        this.statusCheckInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupTabs();
        this.setupEventListeners();
        this.loadVoices();
        this.loadSettings();
    }
    
    setupTabs() {
        const tabButtons = document.querySelectorAll('.nav-tab button');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const targetTab = button.getAttribute('data-tab');
                
                // Update button states
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update content visibility
                tabContents.forEach(content => {
                    content.classList.remove('active');
                });
                
                const targetContent = document.getElementById(targetTab);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    }
    
    setupEventListeners() {
        // Text processing
        const speakBtn = document.getElementById('speak-btn');
        const downloadBtn = document.getElementById('download-btn');
        const textArea = document.getElementById('text-input');
        
        if (speakBtn) {
            speakBtn.addEventListener('click', () => this.speakText());
        }
        
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadAudio());
        }
        
        if (textArea) {
            textArea.addEventListener('input', () => this.updateTextCounter());
        }
        
        // File upload
        const fileInput = document.getElementById('file-input');
        const fileButton = document.getElementById('file-input-button');
        
        if (fileInput && fileButton) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
            fileButton.addEventListener('click', () => fileInput.click());
            
            // Drag and drop
            fileButton.addEventListener('dragover', (e) => {
                e.preventDefault();
                fileButton.classList.add('dragover');
            });
            
            fileButton.addEventListener('dragleave', () => {
                fileButton.classList.remove('dragover');
            });
            
            fileButton.addEventListener('drop', (e) => {
                e.preventDefault();
                fileButton.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    this.handleFileUpload({ target: { files } });
                }
            });
        }
        
        // URL processing
        const urlBtn = document.getElementById('process-url-btn');
        if (urlBtn) {
            urlBtn.addEventListener('click', () => this.processURL());
        }
        
        // Settings
        const voiceSelect = document.getElementById('voice-select');
        const rateSlider = document.getElementById('rate-slider');
        const volumeSlider = document.getElementById('volume-slider');
        
        if (voiceSelect) {
            voiceSelect.addEventListener('change', () => this.updateSettings());
        }
        
        if (rateSlider) {
            rateSlider.addEventListener('input', (e) => {
                document.getElementById('rate-value').textContent = e.target.value;
                this.updateSettings();
            });
        }
        
        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => {
                document.getElementById('volume-value').textContent = parseFloat(e.target.value).toFixed(1);
                this.updateSettings();
            });
        }
        
        // Clear button
        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAll());
        }
    }
    
    async loadVoices() {
        try {
            const response = await fetch('/api/voices');
            const data = await response.json();
            
            if (data.voices) {
                this.voices = data.voices;
                this.populateVoiceSelect();
            }
        } catch (error) {
            console.error('Failed to load voices:', error);
            this.showAlert('Failed to load available voices', 'warning');
        }
    }
    
    populateVoiceSelect() {
        const voiceSelect = document.getElementById('voice-select');
        if (!voiceSelect) return;
        
        voiceSelect.innerHTML = '';
        this.voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = voice.name;
            voiceSelect.appendChild(option);
        });
    }
    
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            const settings = await response.json();
            
            this.settings = { ...this.settings, ...settings };
            this.updateSettingsUI();
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }
    
    updateSettingsUI() {
        const voiceSelect = document.getElementById('voice-select');
        const rateSlider = document.getElementById('rate-slider');
        const volumeSlider = document.getElementById('volume-slider');
        const rateValue = document.getElementById('rate-value');
        const volumeValue = document.getElementById('volume-value');
        
        if (voiceSelect) voiceSelect.value = this.settings.voice_id;
        if (rateSlider) rateSlider.value = this.settings.rate;
        if (volumeSlider) volumeSlider.value = this.settings.volume;
        if (rateValue) rateValue.textContent = this.settings.rate;
        if (volumeValue) volumeValue.textContent = this.settings.volume.toFixed(1);
    }
    
    async updateSettings() {
        const voiceSelect = document.getElementById('voice-select');
        const rateSlider = document.getElementById('rate-slider');
        const volumeSlider = document.getElementById('volume-slider');

        // Ensure we have valid values, not null/undefined
        const voiceValue = voiceSelect?.value;
        const rateValue = rateSlider?.value;
        const volumeValue = volumeSlider?.value;

        this.settings = {
            voice_id: voiceValue !== null && voiceValue !== undefined && voiceValue !== '' ? parseInt(voiceValue) : 0,
            rate: rateValue !== null && rateValue !== undefined && rateValue !== '' ? parseInt(rateValue) : 200,
            volume: volumeValue !== null && volumeValue !== undefined && volumeValue !== '' ? parseFloat(volumeValue) : 0.9
        };

        try {
            await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.settings)
            });
        } catch (error) {
            console.error('Failed to save settings:', error);
        }
    }
    
    async speakText() {
        const textArea = document.getElementById('text-input');
        const text = textArea?.value?.trim();
        
        if (!text) {
            this.showAlert('Please enter some text to convert to speech', 'warning');
            return;
        }
        
        const speakBtn = document.getElementById('speak-btn');
        
        try {
            // Update UI
            speakBtn.disabled = true;
            speakBtn.innerHTML = '<span class="spinner"></span> Processing...';
            
            const response = await fetch('/api/speak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            
            const data = await response.json();
            
            if (data.task_id) {
                this.currentTask = data.task_id;
                this.startStatusCheck();
                this.showAlert('Processing speech... Please wait.', 'info');
            } else {
                throw new Error(data.error || 'Failed to start processing');
            }
            
        } catch (error) {
            console.error('Speech processing failed:', error);
            this.showAlert(error.message || 'Failed to process text', 'danger');
            
            // Reset UI
            speakBtn.disabled = false;
            speakBtn.textContent = '🎤 Speak';
        }
    }
    
    startStatusCheck() {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
        
        this.statusCheckInterval = setInterval(async () => {
            if (!this.currentTask) return;
            
            try {
                const response = await fetch(`/api/status/${this.currentTask}`);
                const status = await response.json();
                
                this.updateProgress(status);
                
                if (status.status === 'completed') {
                    this.onProcessingComplete();
                } else if (status.status === 'error') {
                    this.onProcessingError(status.error);
                }
                
            } catch (error) {
                console.error('Status check failed:', error);
            }
        }, 1000);
    }
    
    updateProgress(status) {
        const progressBar = document.getElementById('progress-bar');
        const statusText = document.getElementById('status-text');
        
        if (progressBar) {
            progressBar.style.width = `${status.progress || 0}%`;
        }
        
        if (statusText) {
            statusText.textContent = this.getStatusText(status.status);
        }
    }
    
    getStatusText(status) {
        switch (status) {
            case 'processing': return 'Converting text to speech...';
            case 'completed': return 'Speech generated successfully!';
            case 'error': return 'Processing failed';
            default: return 'Processing...';
        }
    }
    
    onProcessingComplete() {
        clearInterval(this.statusCheckInterval);

        const speakBtn = document.getElementById('speak-btn');
        const audioPlayerContainer = document.getElementById('audio-player-container');
        const audioPlayer = document.getElementById('audio-player');

        // Reset UI
        speakBtn.disabled = false;
        speakBtn.textContent = '🎤 Speak';

        // Show audio player
        if (audioPlayerContainer && audioPlayer) {
            // Set audio source to the download URL
            const audioUrl = `/api/download/${this.currentTask}`;
            audioPlayer.src = audioUrl;
            audioPlayerContainer.classList.remove('hidden');

            // Scroll to audio player
            audioPlayerContainer.scrollIntoView({ behavior: 'smooth' });
        }

        this.showAlert('🎵 Speech generated successfully! Audio is ready to play.', 'success');
    }
    
    onProcessingError(error) {
        clearInterval(this.statusCheckInterval);
        
        const speakBtn = document.getElementById('speak-btn');
        speakBtn.disabled = false;
        speakBtn.textContent = '🎤 Speak';
        
        this.showAlert(error || 'Processing failed', 'danger');
    }
    
    async downloadAudio() {
        if (!this.currentTask) {
            this.showAlert('No audio file available for download', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/download/${this.currentTask}`);

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'speech.mp3';  // Changed from .wav to .mp3 for gTTS
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                this.showAlert('Audio file downloaded successfully!', 'success');
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Download failed');
            }

        } catch (error) {
            console.error('Download failed:', error);
            this.showAlert(error.message || 'Failed to download audio', 'danger');
        }
    }
    
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const fileInfo = document.getElementById('file-info');
        const textArea = document.getElementById('text-input');
        
        // Show file info
        if (fileInfo) {
            fileInfo.textContent = `Selected: ${file.name} (${this.formatFileSize(file.size)})`;
        }
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            this.showAlert('Reading file...', 'info');
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (textArea) {
                    textArea.value = data.text;
                    this.updateTextCounter();
                }
                
                this.showAlert(`File processed successfully! Extracted ${data.length} characters.`, 'success');
            } else {
                throw new Error(data.error || 'Failed to process file');
            }
            
        } catch (error) {
            console.error('File upload failed:', error);
            this.showAlert(error.message || 'Failed to process file', 'danger');
        }
    }
    
    async processURL() {
        const urlInput = document.getElementById('url-input');
        const url = urlInput?.value?.trim();
        
        if (!url) {
            this.showAlert('Please enter a URL', 'warning');
            return;
        }
        
        const textArea = document.getElementById('text-input');
        
        try {
            this.showAlert('Reading content from URL...', 'info');
            
            const response = await fetch('/api/url', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (textArea) {
                    textArea.value = data.text;
                    this.updateTextCounter();
                }
                
                this.showAlert(`URL processed successfully! Extracted ${data.length} characters.`, 'success');
            } else {
                throw new Error(data.error || 'Failed to process URL');
            }
            
        } catch (error) {
            console.error('URL processing failed:', error);
            this.showAlert(error.message || 'Failed to process URL', 'danger');
        }
    }
    
    updateTextCounter() {
        const textArea = document.getElementById('text-input');
        const counter = document.getElementById('text-counter');
        
        if (textArea && counter) {
            const length = textArea.value.length;
            counter.textContent = `${length} characters`;
            
            // Change color based on length
            if (length > 5000) {
                counter.style.color = 'var(--warning-color)';
            } else if (length > 10000) {
                counter.style.color = 'var(--danger-color)';
            } else {
                counter.style.color = 'var(--secondary-color)';
            }
        }
    }
    
    clearAll() {
        const textArea = document.getElementById('text-input');
        const urlInput = document.getElementById('url-input');
        const fileInput = document.getElementById('file-input');
        const fileInfo = document.getElementById('file-info');
        const downloadBtn = document.getElementById('download-btn');
        
        if (textArea) textArea.value = '';
        if (urlInput) urlInput.value = '';
        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.textContent = 'No file selected';
        if (downloadBtn) downloadBtn.disabled = true;
        
        this.currentTask = null;
        this.updateTextCounter();
        
        // Clear any existing alerts
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            alertContainer.innerHTML = '';
        }
    }
    
    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()" style="float: right; background: none; border: none; font-size: 1.2em; cursor: pointer;">&times;</button>
        `;
        
        // Clear previous alerts of the same type
        const existingAlerts = alertContainer.querySelectorAll(`.alert-${type}`);
        existingAlerts.forEach(el => el.remove());
        
        alertContainer.appendChild(alert);
        
        // Auto-remove success/info alerts after 5 seconds
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 5000);
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TTSApp();
});

// Prevent zoom on input focus (iOS)
window.addEventListener('load', () => {
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(element => {
        element.addEventListener('focus', () => {
            const viewport = document.querySelector('meta[name=viewport]');
            if (viewport) {
                viewport.setAttribute('content', 'width=device-width, initial-scale=1, maximum-scale=1');
            }
        });
        
        element.addEventListener('blur', () => {
            const viewport = document.querySelector('meta[name=viewport]');
            if (viewport) {
                viewport.setAttribute('content', 'width=device-width, initial-scale=1');
            }
        });
    });
});