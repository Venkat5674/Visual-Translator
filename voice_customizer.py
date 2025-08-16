import tkinter as tk
from tkinter import ttk
import json
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

class VoiceCustomizer:
    """Voice customization tool for the detector bot"""
    
    # Default voices with their characteristics
    DEFAULT_VOICES = {
        "Rachel (Female)": {
            "id": "21m00Tcm4TlvDq8ikWAM",
            "stability": 0.5,
            "similarity_boost": 1.0,
            "style": 0.5,
            "speed": 1.0,
            "gender": "female"
        },
        "Adam (Male)": {
            "id": "pNInz6obpgDQGcFmaJgB",
            "stability": 0.5,
            "similarity_boost": 1.0,
            "style": 0.5,
            "speed": 1.0,
            "gender": "male"
        },
        "Antoni (Male)": {
            "id": "onwK4e9ZLuTAKqWW03F9",
            "stability": 0.7,
            "similarity_boost": 0.7,
            "style": 0.3,
            "speed": 1.1,
            "gender": "male"
        },
        "Clyde (Male)": {
            "id": "EXAVITQu4vr4xnSDxMaL",
            "stability": 0.4,
            "similarity_boost": 0.8,
            "style": 0.7,
            "speed": 0.9,
            "gender": "male"
        },
        "Domi (Female)": {
            "id": "AZnzlk1XvdvUeBnXmlld",
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.8,
            "speed": 1.1,
            "gender": "female"
        }
    }
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = ElevenLabs(api_key=api_key) if api_key else None
        self.config_file = "voice_config.json"
        self.current_config = self._load_config()
        
    def _load_config(self):
        """Load voice configuration from file or use default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Return default configuration
        return {
            "selected_voice": "Rachel (Female)",
            "voice_settings": self.DEFAULT_VOICES["Rachel (Female)"]
        }
        
    def save_config(self):
        """Save current voice configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.current_config, f, indent=2)
            
    def get_current_voice_settings(self):
        """Get current voice settings for TTS"""
        voice_data = self.current_config["voice_settings"]
        
        return {
            "voice_id": voice_data["id"],
            "settings": VoiceSettings(
                stability=voice_data["stability"],
                similarity_boost=voice_data["similarity_boost"],
                style=voice_data["style"],
                use_speaker_boost=True,
                speed=voice_data["speed"]
            )
        }
        
    def show_voice_customizer(self):
        """Display voice customization GUI"""
        root = tk.Tk()
        root.title("Voice Customizer")
        root.geometry("500x450")
        root.resizable(False, False)
        
        # Style configuration
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", background="#e0e0e0", font=("Arial", 10))
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="Voice Customization", style="Header.TLabel")
        header_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Voice selection
        voice_label = ttk.Label(main_frame, text="Select Voice:")
        voice_label.grid(row=1, column=0, sticky="w", pady=5)
        
        selected_voice = tk.StringVar(value=self.current_config["selected_voice"])
        voice_combo = ttk.Combobox(main_frame, textvariable=selected_voice, state="readonly")
        voice_combo["values"] = list(self.DEFAULT_VOICES.keys())
        voice_combo.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Settings frames
        settings_frame = ttk.LabelFrame(main_frame, text="Voice Settings", padding=10)
        settings_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        
        # Stability
        stability_label = ttk.Label(settings_frame, text="Stability:")
        stability_label.grid(row=0, column=0, sticky="w", pady=5)
        stability_var = tk.DoubleVar(value=self.current_config["voice_settings"]["stability"])
        stability_slider = ttk.Scale(settings_frame, from_=0.0, to=1.0, variable=stability_var, orient="horizontal")
        stability_slider.grid(row=0, column=1, sticky="ew", pady=5)
        stability_value = ttk.Label(settings_frame, text=f"{stability_var.get():.1f}")
        stability_value.grid(row=0, column=2, padx=5)
        
        # Similarity boost
        similarity_label = ttk.Label(settings_frame, text="Similarity:")
        similarity_label.grid(row=1, column=0, sticky="w", pady=5)
        similarity_var = tk.DoubleVar(value=self.current_config["voice_settings"]["similarity_boost"])
        similarity_slider = ttk.Scale(settings_frame, from_=0.0, to=1.0, variable=similarity_var, orient="horizontal")
        similarity_slider.grid(row=1, column=1, sticky="ew", pady=5)
        similarity_value = ttk.Label(settings_frame, text=f"{similarity_var.get():.1f}")
        similarity_value.grid(row=1, column=2, padx=5)
        
        # Style
        style_label = ttk.Label(settings_frame, text="Style:")
        style_label.grid(row=2, column=0, sticky="w", pady=5)
        style_var = tk.DoubleVar(value=self.current_config["voice_settings"]["style"])
        style_slider = ttk.Scale(settings_frame, from_=0.0, to=1.0, variable=style_var, orient="horizontal")
        style_slider.grid(row=2, column=1, sticky="ew", pady=5)
        style_value = ttk.Label(settings_frame, text=f"{style_var.get():.1f}")
        style_value.grid(row=2, column=2, padx=5)
        
        # Speed
        speed_label = ttk.Label(settings_frame, text="Speed:")
        speed_label.grid(row=3, column=0, sticky="w", pady=5)
        speed_var = tk.DoubleVar(value=self.current_config["voice_settings"]["speed"])
        speed_slider = ttk.Scale(settings_frame, from_=0.5, to=2.0, variable=speed_var, orient="horizontal")
        speed_slider.grid(row=3, column=1, sticky="ew", pady=5)
        speed_value = ttk.Label(settings_frame, text=f"{speed_var.get():.1f}")
        speed_value.grid(row=3, column=2, padx=5)
        
        # Preview text
        preview_frame = ttk.LabelFrame(main_frame, text="Voice Preview", padding=10)
        preview_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)
        
        preview_text = tk.Text(preview_frame, height=3, width=40)
        preview_text.insert("1.0", "Hello, I am your AI assistant. How can I help you today?")
        preview_text.grid(row=0, column=0, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Update value labels when sliders change
        def update_labels(*args):
            stability_value.config(text=f"{stability_var.get():.1f}")
            similarity_value.config(text=f"{similarity_var.get():.1f}")
            style_value.config(text=f"{style_var.get():.1f}")
            speed_value.config(text=f"{speed_var.get():.1f}")
        
        stability_var.trace_add("write", update_labels)
        similarity_var.trace_add("write", update_labels)
        style_var.trace_add("write", update_labels)
        speed_var.trace_add("write", update_labels)
        
        # Update settings when voice changes
        def on_voice_change(*args):
            voice_name = selected_voice.get()
            voice_data = self.DEFAULT_VOICES[voice_name]
            stability_var.set(voice_data["stability"])
            similarity_var.set(voice_data["similarity_boost"])
            style_var.set(voice_data["style"])
            speed_var.set(voice_data["speed"])
        
        selected_voice.trace_add("write", on_voice_change)
        
        # Preview button function
        def preview_voice():
            if not self.api_key:
                preview_status.config(text="⚠️ No API key provided")
                return
                
            try:
                preview_status.config(text="🔊 Playing preview...")
                voice_id = self.DEFAULT_VOICES[selected_voice.get()]["id"]
                settings = VoiceSettings(
                    stability=stability_var.get(),
                    similarity_boost=similarity_var.get(),
                    style=style_var.get(),
                    use_speaker_boost=True,
                    speed=speed_var.get()
                )
                
                # Use the client to generate speech
                # This is a placeholder - implement the actual speech generation and playback
                # based on your application's functionality
                preview_status.config(text="✅ Preview complete!")
            except Exception as e:
                preview_status.config(text=f"⚠️ Error: {str(e)}")
        
        # Save settings function
        def save_settings():
            voice_name = selected_voice.get()
            self.current_config = {
                "selected_voice": voice_name,
                "voice_settings": {
                    "id": self.DEFAULT_VOICES[voice_name]["id"],
                    "stability": stability_var.get(),
                    "similarity_boost": similarity_var.get(),
                    "style": style_var.get(),
                    "speed": speed_var.get(),
                    "gender": self.DEFAULT_VOICES[voice_name]["gender"]
                }
            }
            self.save_config()
            preview_status.config(text="✅ Settings saved!")
        
        # Preview voice button
        preview_button = ttk.Button(button_frame, text="Preview Voice", command=preview_voice)
        preview_button.grid(row=0, column=0, padx=5)
        
        # Save button
        save_button = ttk.Button(button_frame, text="Save Settings", command=save_settings)
        save_button.grid(row=0, column=1, padx=5)
        
        # Status label
        preview_status = ttk.Label(main_frame, text="")
        preview_status.grid(row=5, column=0, columnspan=2, pady=5)
        
        root.mainloop()
        
        return self.current_config
