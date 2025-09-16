import json
import os
import speech_recognition as sr
import pyttsx3
from datetime import datetime
from rapidfuzz import fuzz, process  # For fuzzy matching
import time
import re
from voice.tts import speak
from feedback_manager import handle_feedback

# File Paths
DATA_DIR = os.path.dirname(__file__)
MENU_PATH = os.path.join(DATA_DIR, 'menu.json')
ORDERS_LOG_PATH = os.path.join(DATA_DIR, 'orders_log.json')

# Initialize TTS
engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('volume', 1.0)


def extract_order_items_with_quantities(order_text, menu_items):
    """
    Extracts (item_name, quantity) pairs from freeform order text.
    Supports fuzzy matching and quantity extraction.
    """
    if isinstance(menu_items, dict):
        menu_items = flatten_menu(menu_items)

    item_names = [item['name'].lower() for item in menu_items]

    word_to_num = {
        "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    text = order_text.lower()
    text = re.sub(r'[\,]', ' and ', text)
    phrases = re.split(r'\band\b', text)

    extracted_items = []

    for phrase in phrases:
        phrase = phrase.strip()
        qty = 1

        # Check quantity by word
        for word, num in word_to_num.items():
            if re.search(r'\b' + word + r'\b', phrase):
                qty = num
                phrase = re.sub(r'\b' + word + r'\b', '', phrase).strip()
                break

        # Check quantity by digit
        digit_match = re.search(r'\b(\d+)\b', phrase)
        if digit_match:
            qty = int(digit_match.group(1))
            phrase = re.sub(r'\b' + str(qty) + r'\b', '', phrase).strip()

        # Match best item using token_sort_ratio
        match = process.extractOne(phrase, item_names, scorer=fuzz.token_sort_ratio)

        print(f"[DEBUG] Phrase: '{phrase}' | Qty: {qty} | Match: {match}")  # 👀 Debug info

        if match and match[1] >= 65:  # Lowered threshold
            matched_name = match[0]
            proper_name = next(
                (item['name'] for item in menu_items if item['name'].lower() == matched_name),
                matched_name
            )
            extracted_items.append((proper_name, qty))
        else:
            print(f"[WARN] Could not match '{phrase}' to any menu item.")

    return extracted_items



def extract_quantity(text):
    """Extract quantity from text, supports words and digits."""
    if not text:
        return 1

    text = text.lower()
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    # Check if spoken number word is present
    for word, num in word_to_num.items():
        if word in text:
            return num

    # Fallback to digits
    digits = ''.join(filter(str.isdigit, text))
    if digits:
        try:
            return max(1, int(digits))
        except:
            return 1

    return 1


def listen(prompt=None):
    if prompt:
        speak(prompt)
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=0.4)
        except Exception:
            pass
        print("🎤 Listening...")
        try:
            audio = r.listen(source, phrase_time_limit=15) # timeout=15 hataya hai
        except Exception as e:
            print(f"[ASR ERROR] listen failed: {e}")
            return None
    try:
        return r.recognize_google(audio)
    except Exception as e:
        print(f"[ASR ERROR] recognize failed: {e}")
        return None



def load_menu():
    if os.path.exists(MENU_PATH):
        with open(MENU_PATH, 'r') as f:
            if os.path.getsize(MENU_PATH) > 0:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print("[ERROR] menu.json is invalid JSON.")
                    return {}
            else:
                print("[WARNING] menu.json is empty.")
    return {}


def save_order(customer_name, order_items):
    order = {
        "customer": customer_name,
        "items": order_items,
        "timestamp": str(datetime.now())
    }
    orders = []
    if os.path.exists(ORDERS_LOG_PATH):
        with open(ORDERS_LOG_PATH, 'r') as f:
            if os.path.getsize(ORDERS_LOG_PATH) > 0:
                orders = json.load(f)
    orders.append(order)
    with open(ORDERS_LOG_PATH, 'w') as f:
        json.dump(orders, f, indent=4)

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def normalize_text(t: str) -> str:
    return t.lower().strip()

def show_menu_console_and_speak(customer_name=None, polite=None):
    menu = load_menu()
    print("\n=== JARK CAFÉ MENU ===")
    for category, items in menu.items():
        print(f"\n--- {category} ---")
        for item in items:
            print(f"- {item['name']} : ₹{item['price']}")

    print("======================\n")

    if customer_name:
        # speak(f"Here is our menu today, {customer_name}:")
         speak(f"Here is our menu today {polite}:")
    else:
        speak("Here is our menu:")

    for category, items in menu.items():
        print(f"\n--- {category} ---")
        for item in items:
            print(f"- {item['name']} : ₹{item['price']}")

def flatten_menu(menu_dict):
    return [item for category_items in menu_dict.values() for item in category_items]



def find_best_menu_match(order_text, full_menu):
    if not order_text:
        return None

    # Make sure full_menu is flattened
    if isinstance(full_menu, dict):
        full_menu = flatten_menu(full_menu)

    text_l = order_text.lower()

    # Direct substring match
    for item in full_menu:
        if item['name'].lower() in text_l:
            return item

    # Fuzzy match
    # names = [m['name'] for m in full_menu]
    # result = process.extractOne(order_text, names, scorer=fuzz.partial_ratio)
    # if result and result[1] >= 70:
    #     match_name = result[0]
    #     for item in full_menu:
    #         if item['name'] == match_name:
    #             return item

    return None
def fuzzy_match_items(text, menu_items, threshold=70):
    matched_items = set()
    for menu_item in menu_items:
        score = fuzz.partial_ratio(text.lower(), menu_item.lower())
        if score >= threshold:
            matched_items.add(menu_item)
    return list(matched_items)


# ---------------------------
# MAIN ORDER LOGIC
# ---------------------------
def take_order(customer_name, gender=None):
    """
    Multi-item + quantity order flow.
    - Ask if guest wants menu (only once)
    - Accept multiple items in one spoken line
    - Ask quantity per matched item
    - Confirm batch
    - Loop: would you like anything else? (yes -> new batch, no -> finish)
    """
    menu = load_menu()
    orders = []

    polite = "Sir" if gender == "male" else "Mam" if gender == "female" else customer_name

    # Build name:price and name:proper-case maps
    price_map = {
        item['name'].lower(): item['price']
        for category_items in menu.values()
        for item in category_items
    }
    name_map = {
        item['name'].lower(): item['name']
        for category_items in menu.values()
        for item in category_items
    }

    # Ask menu
    speak(f"{polite}, would you like to hear our menu?")
    resp = listen()
    if resp and any(k in resp.lower() for k in ["yes", "show", "menu"]):
        print("\n=== JARK CAFÉ MENU ===")
        for category, items in menu.items():
            print(f"\n--- {category} ---")
            for item in items:
                print(f"- {item['name']} : ₹{item['price']}")
        speak("Take your time to decide. I will wait for a moment before taking your order.")
        time.sleep(15)

    # Order loop
    while True:
        speak(f"What would you like to have, {polite}? You can say multiple items together.")
        order_text = listen()
        if not order_text:
            speak("Sorry, I didn't hear that. Please say again.")
            continue

        print(f"[ORDER RAW TEXT]: {order_text}")
        o_l = order_text.lower()
        flat_menu = flatten_menu(menu)
        used_text = o_l
        batch_items = []

        # Sort by name length (desc) and match with word boundaries
        sorted_menu = sorted(flat_menu, key=lambda x: len(x['name']), reverse=True)

        for item in sorted_menu:
            item_name = item['name'].lower()
            pattern = r'\b' + re.escape(item_name) + r'\b'
            if re.search(pattern, used_text):
                batch_items.append(item['name'])
                used_text = re.sub(pattern, '', used_text, count=1)  # remove to avoid duplicates

        if not batch_items:
            speak("I didn't catch any items from our menu in that. Say 'menu' to hear it again.")
            continue

        # Ask quantity for each
        extracted = extract_order_items_with_quantities(order_text, flat_menu)
        if not extracted:
            speak("I didn't catch any items with quantity. Please try again.")
            continue

        this_batch_display = []
        temp_batch_data = []
        for item_name, qty in extracted:
            price_each = price_map[item_name.lower()]
            temp_batch_data.append((item_name, qty, price_each))
            this_batch_display.append(f"{qty} {item_name}")


        # Confirm batch
        speak(f"You want {', '.join(this_batch_display)}. Shall I confirm?")
        c_resp = listen()
        if c_resp and any(k in c_resp.lower() for k in [
            "yes", "confirm", "ok", "okay", "confirm my order", "yes confirm please"
        ]):
            orders.extend(temp_batch_data)
            speak(f"Confirmed {', '.join(this_batch_display)}.")
        else:
            speak("Okay, not adding that batch. Let's try again.")
            continue

        # Ask if more
        speak("Would you like to order anything else?")
        more_resp = listen()
        if more_resp and any(k in more_resp.lower() for k in ["no", "nothing", "done", "that's all", "thats all"]):
            break
        if more_resp and "menu" in more_resp.lower():
            show_menu_console_and_speak(polite)

    # Final summary & billing
    if orders:
        total = 0
        summary_bits = []
        for name, qty, price_each in orders:
            subtotal = qty * price_each
            total += subtotal
            summary_bits.append(f"{qty} {name}")

        save_order(customer_name, summary_bits)

        speak(f"Thank you {polite}! Your orders have been placed: {', '.join(summary_bits)}.")
        speak(f"Your total bill is {total} rupees. Please pay at the counter and wait shortly — your order will be prepared and served to your table.")
    else:
        speak("No order placed. Let me know if you need anything.")

def complete_order(order_id):
    # existing order complete code
    print(f"✅ Order {order_id} delivered!")

    # Trigger feedback
    handle_feedback(order_id)