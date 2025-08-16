import json
import datetime
from collections import deque

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
