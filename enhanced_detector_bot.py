import cv2
import os
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import google.generativeai as genai
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from io import BytesIO
import base64
import time
import json
import datetime
from collections import deque

# API Keys
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize ElevenLabs Client
client = ElevenLabs(api_key="sk_958cb595a36abe70f47db6cf9f6b521ca9eb0af493656b18")


# Chat memory manager
class ChatMemory:
    def __init__(self, max_history=10):
        self.history = deque(maxlen=max_history)
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_log_file = f"conversation_{self.session_id}.json"
    
    def add_interaction(self, user_input, bot_response, image_path=None):
        timestamp = datetime.datetime.now().isoformat()
        interaction = {
            "timestamp": timestamp,
            "user_input": user_input,
            "bot_response": bot_response,
            "image_captured": image_path is not None
        }
        self.history.append(interaction)
        self._save_history()
        
    def get_context_for_ai(self, max_entries=3):
        """Returns formatted conversation history for AI context"""
        if not self.history:
            return ""
            
        context = "Previous conversation:\n"
        recent_history = list(self.history)[-max_entries:]
        
        for i, interaction in enumerate(recent_history):
            context += f"User: {interaction['user_input']}\n"
            context += f"Bot: {interaction['bot_response']}\n"
            
        return context
    
    def _save_history(self):
        """Save conversation history to a JSON file"""
        with open(self.conversation_log_file, 'w') as f:
            json.dump(list(self.history), f, indent=2)
    
    def summarize_session(self):
        """Generate a summary of the conversation session"""
        if not self.history:
            return "No conversation history available."
            
        total_interactions = len(self.history)
        first_interaction = self.history[0]["timestamp"]
        last_interaction = self.history[-1]["timestamp"]
        
        return f"Session Summary:\n- {total_interactions} interactions\n- Started: {first_interaction}\n- Last interaction: {last_interaction}"


# Show Live Video & Capture an Image with Real-time Detection
def capture_image(enable_realtime_detection=False):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("⚠️ Error: Could not open webcam.")
        return None

    print("🎥 Press 'c' to capture an image, 'd' to toggle detection, or 'q' to quit.")
    
    # Load pre-trained face detection model from OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    detection_active = enable_realtime_detection
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to capture frame.")
            break
            
        display_frame = frame.copy()
        
        # If detection is active, detect faces and draw rectangles
        if detection_active:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw rectangles around faces
            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(display_frame, 'Face Detected', (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
        
        # Add detection status to frame
        status_text = "Detection: ON" if detection_active else "Detection: OFF"
        cv2.putText(display_frame, status_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if detection_active else (0, 0, 255), 2)

        cv2.imshow("Live Video - Press 'c' to Capture", display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):  # Press 'c' to capture
            img_path = "captured_frame.jpg"
            cv2.imwrite(img_path, frame)  # Save original frame without overlays
            print(f"📸 Image saved: {img_path}")
            break
        elif key == ord("d"):  # Press 'd' to toggle detection
            detection_active = not detection_active
            print(f"🔍 Detection {'enabled' if detection_active else 'disabled'}")
        elif key == ord("q"):  # Press 'q' to quit
            print("❌ Exiting video capture.")
            img_path = None
            break

    cap.release()
    cv2.destroyAllWindows()
    return img_path


# Convert image to base64 for Gemini
def encode_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        print(f"⚠️ Error encoding image: {e}")
        return None


# Record Audio
def record_audio(filename="input_audio.wav", duration=5, samplerate=44100):
    print("🎙️ Recording... Speak now!")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    wav.write(filename, samplerate, audio_data)
    print(f"📁 Recording saved as {filename}")
    return filename


# Transcribe Audio to Text
def transcribe_audio(audio_path):
    try:
        with open(audio_path, "rb") as audio_file:
            # Set language to English for transcription
            response = client.speech_to_text.convert(
                model_id="scribe_v1", 
                file=audio_file,
                language_code="en" # Force English transcription
            )
        transcribed_text = response.text.strip()
        return transcribed_text
    except Exception as e:
        print(f"⚠️ Error in transcription: {e}")
        return "No speech detected"


# Send Image + Text to Gemini
def get_gemini_response(text, image_path):
    genai.configure(api_key="AIzaSyAsi3P4_W5ZNDVfCWs_rT6A0T3YWWXNDyI")
    model = genai.GenerativeModel("gemini-1.5-flash", generation_config={
        "temperature": 0.7, "top_p": 1, "top_k": 1, "max_output_tokens": 100
    })

    # Add English instruction to ensure response in English
    english_instruction = "Please respond only in English. "
    
    # If text is None or empty, provide a default prompt
    if not text or text == "None" or text == "No speech detected":
        text = "Describe what you see in this image."
    
    # Combine instruction with user text
    prompt_text = english_instruction + text
    
    # Prepare content in the correct format
    content = [{"text": prompt_text}]
    
    # Add image if available
    if image_path:
        image_data = encode_image(image_path)
        if image_data:
            content.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            })

    try:
        # Use correct request format
        response = model.generate_content(contents=[{"parts": content}])
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Error in AI response: {e}")
        
        # Add more specific error handling
        if "429" in str(e):
            print("⚠️ Rate limit exceeded. Trying a simpler response.")
            return "I'm sorry, I've reached my rate limit. Please try again in a minute."
        
        return "I'm sorry, I couldn't process that."


# Convert AI Response to Speech & Play
def play_speech(text):
    try:
        # Using a standard English voice (Adam) instead of the multilingual one
        # Voice IDs: 
        # - "21m00Tcm4TlvDq8ikWAM" (Rachel - Female)
        # - "pNInz6obpgDQGcFmaJgB" (Adam - Male)
        # - "onwK4e9ZLuTAKqWW03F9" (Antoni - Male)
        # - "EXAVITQu4vr4xnSDxMaL" (Clyde - Male)
        response = client.text_to_speech.convert(
            model_id="eleven_monolingual_v1",  # English-focused model
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel - Clear English female voice
            output_format="pcm_16000",
            text=text,
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=1.0, style=0.5, use_speaker_boost=True, speed=1.0),
        )

        audio_stream = BytesIO()
        for chunk in response:
            if chunk:
                audio_stream.write(chunk)

        audio_stream.seek(0)
        audio_data = np.frombuffer(audio_stream.read(), dtype=np.int16)
        sd.play(audio_data, samplerate=16000)
        sd.wait()
    except Exception as e:
        print(f"⚠️ Error playing speech: {e}")


# Run the Real-time AI Assistant
def main():
    print("\n🌐 Enhanced Detector Bot - All interactions will be in English")
    
    # Initialize chat memory
    memory = ChatMemory()
    
    while True:
        print("\n🔹 [1] Capture Speak")
        print("🔹 [2] View Conversation History")
        print("🔹 [3] Exit")
        choice = input("👉 Select an option: ")

        if choice == "3":
            # Show summary before exiting
            print("\n" + memory.summarize_session())
            print("👋 Exiting...")
            break
            
        elif choice == "2":
            # Display conversation history
            if not memory.history:
                print("No conversation history yet.")
            else:
                print("\n📜 Conversation History:")
                for i, interaction in enumerate(memory.history):
                    print(f"\n--- Interaction {i+1} ---")
                    print(f"👤 You: {interaction['user_input']}")
                    print(f"🤖 Bot: {interaction['bot_response']}")
            continue

        # Enable real-time detection in video capture
        image_path = capture_image(enable_realtime_detection=True)
        if image_path is None:
            continue

        recorded_file = record_audio()
        print("🔄 Processing speech to English text...")
        audio_text = transcribe_audio(recorded_file)

        print(f"📝 Transcribed: {audio_text}")
        
        # Get conversation context and generate response
        print("🔄 Generating English response with conversation context...")
        conversation_context = memory.get_context_for_ai() if len(memory.history) > 0 else ""
        
        if conversation_context:
            # Add context to the prompt
            enhanced_prompt = f"{conversation_context}\nNew input: {audio_text}"
            gemini_reply = get_gemini_response(enhanced_prompt, image_path)
        else:
            gemini_reply = get_gemini_response(audio_text, image_path)
            
        print(f"🤖 Bot Says: {gemini_reply}")
        
        # Add this interaction to memory
        memory.add_interaction(audio_text, gemini_reply, image_path)
        
        print("🔊 Speaking in English...")
        play_speech(gemini_reply)


if __name__ == "__main__":
    main()
