import os
import json
import pickle
from datetime import datetime
import warnings
import cv2
import numpy as np

# Try to import face_recognition with fallback
try:
    # Suppress stdout/stderr during import to avoid dependency warning messages
    import sys
    import os
    from contextlib import redirect_stdout, redirect_stderr
    
    with redirect_stdout(open(os.devnull, 'w')), redirect_stderr(open(os.devnull, 'w')):
        import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("[LOG] Face recognition loaded successfully")
except Exception as e:
    print(f"[WARN] Face recognition not available: {e}")
    print("[INFO] Using fallback mode - will ask for customer name directly")
    FACE_RECOGNITION_AVAILABLE = False
    face_recognition = None  # Define a placeholder to avoid NameError

import pyttsx3
import speech_recognition as sr
from voice.tts import speak

warnings.filterwarnings("ignore", category=UserWarning)

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
DATA_DIR = os.path.dirname(__file__)
KNOWN_FACES_PATH = os.path.join(DATA_DIR, 'data', 'known_faces.pkl')
VISIT_LOG_PATH   = os.path.join(DATA_DIR, 'data', 'visit_log.json')
CUSTOMER_IMAGES_DIR = os.path.join(DATA_DIR, 'data', 'customer_images')
GENDER_LOG_PATH  = os.path.join(DATA_DIR, 'data', 'gender_log.json')

os.makedirs(CUSTOMER_IMAGES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(KNOWN_FACES_PATH), exist_ok=True)

# ------------------------------------------------------------------
# Gender model (OpenCV DNN Caffe)
# ------------------------------------------------------------------
GENDER_MODEL_DIR  = os.path.join(DATA_DIR, 'gender_model')
GENDER_PROTO      = os.path.join(GENDER_MODEL_DIR, 'deploy_gender.prototxt')
GENDER_MODEL      = os.path.join(GENDER_MODEL_DIR, 'gender_net.caffemodel')
GENDER_LABELS     = ["Male", "Female"]  # model index order

def load_gender_model():
    if not (os.path.exists(GENDER_PROTO) and os.path.exists(GENDER_MODEL)):
        print("[WARN] Gender model files not found. Will ask guest instead.")
        return None
    try:
        net = cv2.dnn.readNetFromCaffe(GENDER_PROTO, GENDER_MODEL)
        print("[LOG] Gender model loaded.")
        return net
    except Exception as e:
        print(f"[ERROR] Could not load gender model: {e}")
        return None

gender_net = load_gender_model()

# ------------------------------------------------------------------
# TTS + ASR
# ------------------------------------------------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('volume', 1.0)

# def speak(text: str):
#     print(f"[🗣️ Speaking]: {text}")
#     engine.say(text)
#     engine.runAndWait()

def listen(prompt: str | None = None, timeout: float = 5, phrase_time_limit: float = 4):
    """
    Robust speech capture:
    - Optional spoken prompt
    - Ambient noise adjustment
    - Short phrase limit (reduces upload size, avoids Google timeouts)
    - Full exception safety (returns None on ANY failure)
    """
    if prompt:
        speak(prompt)

    r = sr.Recognizer()
    r.dynamic_energy_threshold = True  # auto adjust to noise

    with sr.Microphone() as source:
        try:
            # quick ambient noise calibrate (short so we stay responsive)
            r.adjust_for_ambient_noise(source, duration=0.4)
        except Exception as e:
            print(f"[ASR WARN] ambient noise adjust failed: {e}")

        print("🎤 Listening...")
        try:
            audio = r.listen(source, phrase_time_limit=15) # timeout=17 hataya hai 
        except sr.WaitTimeoutError:
            print("[ASR] Timeout: no speech heard.")
            return None
        except Exception as e:
            print(f"[ASR ERROR] mic listen failed: {e}")
            return None

    # Send to Google
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        print("[ASR] Speech not understood.")
        return None
    except sr.RequestError as e:
        print(f"[ASR ERROR] Google request failed: {e}")
        return None
    except Exception as e:
        print(f"[ASR ERROR] Unexpected: {e}")
        return None


# ------------------------------------------------------------------
# Persistence
# ------------------------------------------------------------------
def load_known_faces():
    if os.path.exists(KNOWN_FACES_PATH):
        with open(KNOWN_FACES_PATH, 'rb') as f:
            return pickle.load(f)
    return {}

def save_known_faces(known_faces):
    with open(KNOWN_FACES_PATH, 'wb') as f:
        pickle.dump(known_faces, f)

def load_visit_log():
    if os.path.exists(VISIT_LOG_PATH) and os.path.getsize(VISIT_LOG_PATH) > 0:
        with open(VISIT_LOG_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_visit_log(log):
    with open(VISIT_LOG_PATH, 'w') as f:
        json.dump(log, f, indent=4)

def load_gender_log():
    if os.path.exists(GENDER_LOG_PATH) and os.path.getsize(GENDER_LOG_PATH) > 0:
        with open(GENDER_LOG_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_gender_log(glog):
    with open(GENDER_LOG_PATH, 'w') as f:
        json.dump(glog, f, indent=4)

# ------------------------------------------------------------------
# Utility: classify visit frequency
# ------------------------------------------------------------------
def classify_user(name, log):
    visits = log.get(name, [])
    count = len(visits)
    if count == 1:
        return "new"
    elif 2 <= count <= 4:
        return "occasional"
    elif 5 <= count <= 8:
        return "frequent"
    else:
        return "regular"

# ------------------------------------------------------------------
# Mood-based greetings (unchanged from your prior version)
# ------------------------------------------------------------------
def get_greeting(name, user_type, mood):
    mood = mood.lower() if mood else "neutral"
    greetings = {
        "new": {
            "happy":   f"Hey {name}! You look cheerful today! Welcome to JARK Café!",
            "sad":     f"Hi {name}, tough day? Let JARK Café lift your mood!",
            "tired":   f"Hey {name}, need a break? We've got your comfort food!",
            "excited": f"Whoa {name}, you're full of energy! Let’s keep the vibe going at JARK!",
            "neutral": f"Welcome {name}! Great to have you at JARK Café!"
        },
        "occasional": {
            "happy":   f"Great to see that smile again, {name}!",
            "sad":     f"Welcome back {name}, we're here to make your day better.",
            "tired":   f"{name}, need a caffeine boost? We've got you covered!",
            "excited": f"{name}! That energy is contagious. Let’s fuel it more!",
            "neutral": f"Hey {name}, good to see you again!"
        },
        "frequent": {
            "happy":   f"{name}, you're glowing! Welcome back, as always!",
            "sad":     f"{name}, let your favorite drink cheer you up!",
            "tired":   f"{name}, same cozy table and a warm cup ready for you.",
            "excited": f"{name}, let’s make today even better at JARK!",
            "neutral": f"Welcome back {name}! You’re practically family now!"
        },
        "regular": {
            "happy":   f"{name}! Our sunshine is here again!",
            "sad":     f"{name}, your usual comfort treat is coming right up!",
            "tired":   f"{name}, recharge mode: ON. Let us serve you!",
            "excited": f"{name}, your table’s already buzzing with good vibes!",
            "neutral": f"{name}, as always, your table is waiting!"
        }
    }
    return greetings.get(user_type, {}).get(mood, f"Welcome {name}!")

# ------------------------------------------------------------------
# Gender Helpers
# ------------------------------------------------------------------
def detect_gender_from_face(face_img):
    """Returns (gender_string, confidence_float)."""
    if gender_net is None or face_img is None or face_img.size == 0:
        return "Unknown", 0.0
    try:
        blob = cv2.dnn.blobFromImage(
            face_img, 1.0, (227, 227),
            (78.4263377603, 87.7689143744, 114.895847746),  # BGR mean
            swapRB=False, crop=False
        )
        gender_net.setInput(blob)
        preds = gender_net.forward()  # shape (1,2)
        idx = preds[0].argmax()
        conf = float(preds[0][idx])
        return GENDER_LABELS[idx], conf
    except Exception as e:
        print(f"[ERROR] Gender detection failed: {e}")
        return "Unknown", 0.0

def parse_gender_response(resp):
    if not resp:
        return None
    r = resp.lower()
    if any(k in r for k in ["sir", "bhai", "bro", "male", "man", "uncle"]):
        return "male"
    if any(k in r for k in ["mam", "ma'am", "madam", "madame", "female", "lady", "didi", "aunty", "auntie"]):
        return "female"
    return None

def title_from_gender(g):
    if g == "male": return "Sir"
    if g == "female": return "Mam"
    return ""

# ------------------------------------------------------------------
# Main: recognize face, ask name if new, detect/remember gender, greet
# Returns (name, user_type, gender_val)
# ------------------------------------------------------------------
def recognize_face():
    """
    Detects a face, matches against known encodings, collects name & gender if new,
    greets based on mood + visit frequency. Returns (name, user_type, gender_val).
    """
    if not FACE_RECOGNITION_AVAILABLE:
        # Fallback mode - directly ask for name and gender
        print("[LOG] Face recognition not available, using direct input mode")
        speak("Hello! Welcome to JARK Café!")
        
        # For testing/demo: use simple defaults instead of voice input
        try:
            # Ask for name
            name_resp = listen("May I know your good name?")
            if not name_resp:
                final_name = "Guest"
            else:
                final_name = name_resp.strip().title()
            
            # Ask for gender
            g_resp = listen(f"Thank you {final_name}. Should I address you as Sir or Mam?")
            gender_val = parse_gender_response(g_resp) or "male"
        except Exception as e:
            print(f"[LOG] Voice input failed: {e}, using defaults")
            final_name = "Demo Customer"
            gender_val = "male"
        
        # Simple visit tracking
        visit_log = load_visit_log()
        visit_log.setdefault(final_name, []).append(str(datetime.now()))
        save_visit_log(visit_log)
        
        gender_log = load_gender_log()
        gender_log[final_name] = gender_val
        save_gender_log(gender_log)
        
        user_type = classify_user(final_name, visit_log)
        
        # Simple greeting
        title = title_from_gender(gender_val)
        speak(f"How are you feeling today, {title}?")
        mood = listen() or "neutral"
        greeting = get_greeting(final_name, user_type, mood)
        speak(greeting)
        
        return final_name, user_type, gender_val
    
    # Original face recognition code
    known_faces = load_known_faces()
    visit_log   = load_visit_log()
    gender_log  = load_gender_log()

    cap = cv2.VideoCapture(0)
    recognized_name = None
    gender_val = None  # 'male' / 'female' / None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if not FACE_RECOGNITION_AVAILABLE:
            break
            
        # Only use face_recognition functions if available
        if face_recognition is not None:
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        else:
            break

        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            print("[LOG] Detected a face")

            # ----- Try gender model (we'll override for NEW guest after name) -----
            face_img = frame[top:bottom, left:right]
            g_guess, g_conf = detect_gender_from_face(face_img)
            if g_guess in ("Male", "Female") and g_conf >= 0.60:
                gender_val = g_guess.lower()  # 'male' or 'female'
            else:
                gender_val = None

            # ----- Face match -----
            found = False
            if face_recognition is not None:
                for name, known_encoding in known_faces.items():
                    match = face_recognition.compare_faces([known_encoding], encoding)[0]
                    if match:
                        recognized_name = name
                        found = True
                        break

            if not found:
                # ---------------- NEW CUSTOMER PATH ----------------
                temp_id = f"Customer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                recognized_name = temp_id
                known_faces[temp_id] = encoding  # temp store so we don't lose encoding

                # Save cropped face temp image
                temp_image_path = os.path.join(CUSTOMER_IMAGES_DIR, f"{temp_id}.jpg")
                cv2.imwrite(temp_image_path, face_img)

                # Close camera before interactive voice Q&A (prevents webcam hold)
                cap.release()
                cv2.destroyAllWindows()

                # Ask NAME FIRST (your requested change)
                name_resp = listen("Hello! May I know your good name?")
                if not name_resp:
                    final_name = temp_id  # fallback
                else:
                    final_name = name_resp.strip().title()
                    if final_name in known_faces:  # avoid overwrite
                        final_name = f"{final_name}_{datetime.now().strftime('%H%M%S')}"

                # Move encoding + visit log under real name
                known_faces[final_name] = known_faces.pop(temp_id)
                visit_log.setdefault(final_name, [])
                # move any existing temp log if was created (not strictly needed here)
                if temp_id in visit_log:
                    visit_log[final_name].extend(visit_log.pop(temp_id))

                # Rename saved face image
                new_image_path = os.path.join(CUSTOMER_IMAGES_DIR, f"{final_name}.jpg")
                try:
                    os.rename(temp_image_path, new_image_path)
                except Exception:
                    pass

                recognized_name = final_name

                # Ask SIR / MAM (always ask for new guest, even if model guessed)
                g_resp = listen(f"Thank you {recognized_name}. Should I address you as Sir or Mam?")
                gender_val = parse_gender_response(g_resp)
                # fallback to model guess if parse failed
                if gender_val is None and g_guess in ("Male", "Female"):
                    gender_val = g_guess.lower()
                # final fallback
                if gender_val is None:
                    gender_val = "male"  # default polite form (change if you prefer neutral)

                # Save gender memory
                gender_log[recognized_name] = gender_val

                # Save persistence
                save_known_faces(known_faces)
                save_visit_log(visit_log)
                save_gender_log(gender_log)

                # We are done capturing; continue to greeting logic below (skip rematch loop)
            else:
                # ---------------- RETURNING CUSTOMER PATH ----------------
                # Load stored gender if exists; if not, ask once
                if recognized_name in gender_log:
                    gender_val = gender_log[recognized_name]
                elif gender_val is None:
                    g_resp = listen(f"Should I address you as Sir or Mam?")
                    gender_val = parse_gender_response(g_resp) or gender_val or "male"
                    gender_log[recognized_name] = gender_val
                    save_gender_log(gender_log)

            # ----- Update visit log for this visit -----
            visit_log.setdefault(recognized_name, []).append(str(datetime.now()))
            save_visit_log(visit_log)

            # ----- Classify frequency -----
            user_type = classify_user(recognized_name, visit_log)

            # ----- Greeting -----
            title = title_from_gender(gender_val)
            if title:
                speak(f"How are you feeling today, {title}?")
            else:
                speak(f"How are you feeling today, {recognized_name}?")

            mood = listen()  # may be None
            if not mood:
                mood = "neutral"
            greeting = get_greeting(recognized_name, user_type, mood)
            speak(greeting)

            # Cleanup and return
            cap.release()
            cv2.destroyAllWindows()
            return recognized_name, user_type, gender_val

        # keep preview until a face is found
        cv2.imshow("🔍 JARK Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None, None, None

