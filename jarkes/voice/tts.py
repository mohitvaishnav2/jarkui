import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set speaking rate and volume
engine.setProperty('rate', 160)      # Speed (default ~200)
engine.setProperty('volume', 1.0)    # Volume (0.0 to 1.0)

# You can customize the voice (optional)
voices = engine.getProperty('voices')
# For Mac: try female voice (usually at index 1)
engine.setProperty('voice', voices[132].id)  

def speak(text):
    print(f"[🗣️ Speaking]: {text}")
    engine.say(text)
    engine.runAndWait()
