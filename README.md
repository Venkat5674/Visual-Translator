# Enhanced Detector Bot

An AI-powered application that combines computer vision, speech recognition, and natural language processing to create an interactive conversational agent that can see and respond to its environment.

## Features

### Core Capabilities
- **Real-time Face Detection**: Identifies faces in the camera feed
- **Speech Recognition**: Converts spoken language to text
- **Image Analysis**: Uses Gemini AI to understand and describe images
- **Natural Language Processing**: Generates contextually relevant responses
- **Text-to-Speech**: Converts AI responses to natural-sounding speech

### Enhanced Features
- **Conversation Memory**: Remembers previous interactions for contextual responses
- **Persistent History**: Saves conversation logs for future reference
- **Advanced Image Processing**: Face detection, pose estimation, and image enhancement
- **Voice Customization**: Choose from different voices and adjust parameters

## Installation

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd detector_bot
   ```

2. **Install dependencies**:
   ```
   pip install opencv-python numpy sounddevice scipy google-generativeai elevenlabs mediapipe pillow
   ```

3. **API Keys Setup**:
   - **Gemini API Key**: Get from [Google AI Studio](https://ai.google.dev/)
   - **ElevenLabs API Key**: Get from [ElevenLabs](https://elevenlabs.io/) (under Profile > API Key)

## Usage

### Basic Version
Run the standard version with:
```
python main.py
```

### Enhanced Version
Run the version with all advanced features:
```
python enhanced_detector_bot.py
```

### Voice Customization
Customize the voice settings:
```
python customize_voice.py
```

## Controls

### Camera Controls
- **Press 'c'**: Capture image
- **Press 'd'**: Toggle real-time detection
- **Press 'q'**: Quit camera view

### Main Menu Options
1. **Capture Speak**: Start the capture and interaction process
2. **View Conversation History**: Show past interactions
3. **Exit**: End the application

## Project Structure

- `main.py`: Basic detector bot implementation
- `enhanced_detector_bot.py`: Full-featured implementation with memory and advanced features
- `image_processor.py`: Advanced image processing capabilities
- `conversation_memory.py`: Conversation history and context management
- `voice_customizer.py`: Voice customization tools

## Taking the Project Further

Here are some ways to extend this project:

1. **Multi-modal Interactions**: Add gesture recognition for hands-free control
2. **Emotion Recognition**: Detect emotions in faces and adapt responses accordingly
3. **Object Detection**: Recognize and describe objects in the environment
4. **Augmented Reality**: Overlay information on the camera feed
5. **Custom Knowledge Base**: Add domain-specific knowledge for specialized assistance
6. **Mobile App Integration**: Create a mobile version using React Native or Flutter
7. **Smart Home Integration**: Connect to home automation systems
8. **Web Interface**: Create a browser-based version

## Credits

This project uses several powerful APIs and libraries:
- Google's Gemini API for multimodal AI
- ElevenLabs for text-to-speech
- OpenCV for computer vision
- MediaPipe for advanced image processing
- SoundDevice for audio recording and playback

## License

[Your License Information]
