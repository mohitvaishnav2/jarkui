import speech_recognition as sr
from recognizer.face_recognizer import recognize_face
from order_manager import take_order, speak, show_menu_console_and_speak
from feedback_manager import handle_feedback
import random
import time

# -----------------------------
# Helper Functions
# -----------------------------
def generate_order_id():
    return random.randint(1000, 9999)

# -----------------------------
# Main Program
# -----------------------------
if __name__ == "__main__":
    speak("[LOG] Welcome to JARK Café!")
    

    print("[LOG] Starting face recognition...")
    current_customer_name, user_type, current_gender = recognize_face()
    print(f"[LOG] Name: {current_customer_name}, User Type: {user_type}, Gender: {current_gender}")

    if not current_customer_name:
        speak("Sorry, I couldn't detect you. Please try again.")
    else:
        # Normal order flow at first
        take_order(customer_name=current_customer_name, gender=current_gender)

    # Bill print ke turant baad
    speak("Sir, before you leave, could you please share your feedback?")
    handle_feedback(order_id=generate_order_id())

    speak("Thank you for visiting JARK Café! Have a great day!")
    speak("[LOG] Goodbye!")
    time.sleep(1)
    exit(0)
   