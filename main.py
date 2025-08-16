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
import re

# API Keys
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize ElevenLabs Client
client = ElevenLabs(api_key="sk_958cb595a36abe70f47db6cf9f6b521ca9eb0af493656b18")


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


# Check if text contains a question
def is_question(text):
    """
    Determines if the provided text is a question.
    Returns (is_question, question_type)
    """
    # Convert to lowercase for easier matching
    text = text.lower().strip()
    
    # Check for question marks
    if '?' in text:
        return True, "direct"
    
    # Check for question words at the beginning of the text
    question_starters = [
        "what", "where", "when", "who", "whom", "whose", "which", 
        "why", "how", "can", "could", "would", "will", "should", 
        "is", "are", "am", "was", "were", "do", "does", "did",
        "have", "has", "had", "may", "might", "must", "shall"
    ]
    
    words = text.split()
    if words and words[0] in question_starters:
        return True, "starter"
    
    # Check for question phrases
    question_phrases = [
        "tell me about", "explain", "describe", "i want to know",
        "can you tell", "do you know", "i'd like to know", "i would like to know",
        "show me", "give me information", "what's", "whats", "who's", "whos",
        "where's", "wheres", "when's", "whens", "how's", "hows", "tell us"
    ]
    
    for phrase in question_phrases:
        if phrase in text:
            return True, "phrase"
    
    # Not detected as a question
    return False, None


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
    
    # Check if the text is a question
    is_question_text, question_type = is_question(text)
    
    # Customize instructions based on whether it's a question or not
    if is_question_text:
        instruction = english_instruction + "This is a question. Please provide a clear, direct answer to: "
    else:
        instruction = english_instruction + "Please respond to: "
    
    # Combine instruction with user text
    prompt_text = instruction + text
    
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
        response_text = response.text.strip()
        
        # Format response for questions
        if is_question_text:
            # For questions, add "The answer is" prefix if it's not already part of the response
            lower_response = response_text.lower()
            if not (lower_response.startswith("the answer") or 
                   lower_response.startswith("answer") or
                   "answer is" in lower_response.split()[:5]):
                response_text = "The answer is: " + response_text
                
        return response_text
    except Exception as e:
        print(f"⚠️ Error in AI response: {e}")
        if is_question_text:
            return "I'm sorry, I couldn't find an answer to your question."
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
    print("\n🌐 English Detector Bot - All interactions will be in English")
    print("🔍 Question detection is enabled - questions will receive direct answers")
    
    while True:
        print("\n🔹 [1] Capture Speak")
        print("🔹 [2] Exit")
        choice = input("👉 Select an option: ")

        if choice == "2":
            print("👋 Exiting...")
            break

        image_path = capture_image()  # Show live video & capture frame
        if image_path is None:
            continue

        recorded_file = record_audio()
        print("🔄 Processing speech to English text...")
        audio_text = transcribe_audio(recorded_file)

        print(f"📝 Transcribed: {audio_text}")
        
        # Check if it's a question
        is_question_text, question_type = is_question(audio_text)
        if is_question_text:
            print(f"❓ Question detected! Type: {question_type}")
            print("🔄 Finding answer to your question...")
        else:
            print("🔄 Generating English response...")
            
        gemini_reply = get_gemini_response(audio_text, image_path)
        print(f"🤖 Bot Says: {gemini_reply}")
        
        print("🔊 Speaking in English...")
        play_speech(gemini_reply)


if __name__ == "__main__":
    main()
