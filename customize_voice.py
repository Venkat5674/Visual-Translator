from voice_customizer import VoiceCustomizer
import os

# Get API key
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY") or "sk_958cb595a36abe70f47db6cf9f6b521ca9eb0af493656b18"

# Create and launch the customizer
customizer = VoiceCustomizer(ELEVEN_LABS_API_KEY)
customizer.show_voice_customizer()

print("\nVoice settings saved. Use enhanced_detector_bot.py to use your customized voice.")
