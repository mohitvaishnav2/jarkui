import datetime
import json
import os
from voice.tts import speak
import speech_recognition as sr

# ------------------- JSON file setup -------------------
file_path = "feedback.json"
if not os.path.exists(file_path):
    with open(file_path, "w") as f:
        json.dump([], f, indent=4)

# ------------------- Analytics -------------------
analytics = {"Positive": 0, "Neutral": 0, "Negative": 0}

# ------------------- Voice input -------------------
def listen(timeout=17):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[🎤 Listening...]")
        try:
            audio = recognizer.listen(source, phrase_time_limit=timeout)
            text = recognizer.recognize_google(audio).lower()
            print(f"[Customer]: {text}")
            return text
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand that. Please repeat.")
            return listen()
        except sr.RequestError:
            speak("Speech service unavailable. Please type your feedback.")
            return input("[Customer]: ").lower()
        except sr.WaitTimeoutError:
            speak("You did not respond. Moving on.")
            return "No response"

# ------------------- Feedback storage -------------------
def store_feedback(order_id, f_type, text):
    with open(file_path, "r") as f:
        try:
            feedbacks = json.load(f)
        except json.JSONDecodeError:
            feedbacks = []

    feedback_entry = {
        "order_id": order_id,
        "type": f_type,
        "feedback": text,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    feedbacks.append(feedback_entry)

    with open(file_path, "w") as f:
        json.dump(feedbacks, f, indent=4)

    analytics[f_type] += 1

# ------------------- Staff notification -------------------
def notify_staff(order_id, issue):
    print(f"\n🚨 STAFF ALERT: Order {order_id} has a complaint → {issue}\n")
    speak("The staff has been notified, they will assist you shortly.")

# ------------------- Analytics report -------------------
def update_analytics_report():
    print("\n📊 --- Analytics Report ---")
    for k, v in analytics.items():
        print(f"{k}: {v}")
    print("--------------------------\n")

# ------------------- Feedback handler -------------------
def handle_feedback(order_id):
    speak("How was your experience with your order?")
    feedback = listen()

    if any(word in feedback for word in ["good", "great", "excellent", "nice", "love"]):
        store_feedback(order_id, "Positive", feedback)
        speak("Thank you for your positive feedback!")

    elif any(word in feedback for word in ["okay", "average", "fine", "not bad"]):
        store_feedback(order_id, "Neutral", feedback)
        speak("Thanks for sharing, we'll try to improve.")

    else:
        store_feedback(order_id, "Negative", feedback)
        speak("I'm sorry for the inconvenience. Would you like me to call the staff?")
        choice = listen()
        if choice in ["yes", "yeah", "please", "sure"]:
            notify_staff(order_id, feedback)
        else:
            speak("Okay, I have recorded your complaint. Thank you for telling us.")

    update_analytics_report()
