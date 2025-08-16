# This file contains implementation to detect questions in user input

def is_question(text):
    """
    Determines if the provided text is a question.
    Returns (is_question, question_type)
    """
    # Convert to lowercase for easier matching
    if not text:
        return False, None
        
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
