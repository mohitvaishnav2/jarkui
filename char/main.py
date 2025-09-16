# main.py - JARK desktop app using Panda3D, pyttsx3, and placeholder for lip sync
# Requirements: Python 3.10+, panda3d, panda3d-gltf, pyttsx3

import os
import sys
import time
import json
import threading
import subprocess
import numpy as np
from queue import SimpleQueue
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, Vec3, Filename, WindowProperties
from panda3d.core import GeomNode

# Additional imports at top
import random
try:
    from enhanced_jark_gui import JARKProfessionalGUI
    ENHANCED_GUI_AVAILABLE = True
    print("✅ Enhanced Professional GUI loaded successfully")
except ImportError:
    try:
        from jark_gui import JARKGUIOverlay
        ENHANCED_GUI_AVAILABLE = False
        print("✅ Basic GUI loaded as fallback")
    except ImportError:
        print("GUI overlay not available - continuing with basic mode")
        ENHANCED_GUI_AVAILABLE = None

# --- CONFIG ---
CHAR_DIR = os.path.dirname(__file__)
# Try multiple avatar files, prioritizing avatar.glb and jark.glb
AVATAR_FILES = ['avatar.glb', 'jark.glb', 'jake.glb', 'femaleai .glb']
AVATAR_PATH = None
for avatar_file in AVATAR_FILES:
    potential_path = os.path.join(CHAR_DIR, avatar_file)
    if os.path.exists(potential_path):
        AVATAR_PATH = potential_path
        print(f"[CONFIG] Using avatar file: {avatar_file}")
        break

if not AVATAR_PATH:
    AVATAR_PATH = os.path.join(CHAR_DIR, 'avatar.glb')  # Default fallback
    print(f"[CONFIG] No avatar file found, will try: avatar.glb")

AUDIO_PATH = os.path.join(CHAR_DIR, 'speech.wav')
LIPSYNC_PATH = os.path.join(CHAR_DIR, 'lipsync.json')
RHUBARB_PATH = os.path.join(CHAR_DIR, 'rhubarb')  # or just 'rhubarb' if in PATH

# Expand phoneme→viseme/morph mapping to match common GLB exports (Three.js style)
PHONEME_TO_MORPH = {
    'A': ['viseme_AA', 'AA', 'A', 'mouth_A'],
    'E': ['viseme_E', 'E', 'EH_AE_AH', 'mouth_E'],
    'O': ['viseme_O', 'O', 'OH', 'mouth_O'],
    'B': ['viseme_BMP', 'BMP', 'M', 'P', 'B', 'mouth_B'],
    'C': ['viseme_CH_J_SH', 'CH_J_SH', 'CH', 'J', 'SH', 'mouth_C'],
    'D': ['viseme_D_T_S_Z', 'D_T_S_Z', 'D', 'T', 'S', 'Z', 'mouth_D'],
    'F': ['viseme_FV', 'FV', 'F', 'V', 'mouth_F'],
    'G': ['viseme_G_K_NG', 'G_K_NG', 'G', 'K', 'NG', 'mouth_G'],
    'H': ['viseme_OH', 'OH', 'mouth_H'],
    'X': ['rest', 'neutral', 'mouth_X'],
}

# After PHONEME_TO_MORPH add optional jaw/eyelid aliases and phoneme multipliers
JAW_MORPHS = ['jawOpen', 'JawOpen', 'jaw_open', 'mouthOpen', 'MouthOpen']
EYELID_MORPHS = ['eyeBlinkLeft', 'eyeBlinkRight', 'BlinkLeft', 'BlinkRight', 'blink', 'Blink']
PHONEME_MULTIPLIER = {
    'A': 1.0,  # wide open
    'E': 0.9,
    'O': 0.9,
    'C': 0.6,
    'D': 0.7,
    'F': 0.8,
    'G': 0.7,
    'H': 0.5,
    'B': 0.6,
    'X': 0.3,
}

# Feature flags
ENABLE_HEAD_MICRO_MOTION = False  # keep head still while speaking
ENABLE_FALLBACK_HEAD_ROTATION = False  # no fallback head rotation if no morphs

# Jaw strength scaler
JAW_MULTIPLIER = 1.8  # stronger jaw opening for clearer mouth motion

# Add a simple audio envelope sampler
class AudioEnvelope:
    def __init__(self, wav_path):
        try:
            import soundfile as sf
            data, fs = sf.read(wav_path, dtype='float32')
            if data.ndim == 2:
                data = data.mean(axis=1)
            hop = int(fs * 0.02)  # 20ms hops 
            if hop <= 0:
                hop = 1
            self.times = []
            self.values = []
            for i in range(0, len(data), hop):
                chunk = data[i:i+hop]
                if len(chunk) == 0:
                    continue
                rms = float(np.sqrt(np.mean(chunk**2)))
                t = i / fs
                self.times.append(t)
                self.values.append(rms)
            # normalize
            m = max(self.values) if self.values else 1.0
            self.values = [v / m for v in self.values] if m > 0 else self.values
        except Exception:
            self.times = [0.0]
            self.values = [1.0]

    def at(self, t):
        if not self.times:
            return 1.0
        # binary search nearest
        import bisect
        idx = bisect.bisect_left(self.times, t)
        if idx <= 0:
            return self.values[0]
        if idx >= len(self.values):
            return self.values[-1]
        t0, t1 = self.times[idx-1], self.times[idx]
        v0, v1 = self.values[idx-1], self.values[idx]
        if t1 == t0:
            return v0
        a = (t - t0) / (t1 - t0)
        return v0 * (1 - a) + v1 * a

# --- TTS and Audio Generation ---
def tts(text, wav_path):
    """
    Generate speech using macOS 'say' command directly to WAV.
    Skip ffmpeg conversion to avoid dependency issues.
    """
    print(f"[TTS] Generating speech for: {text}")
    # Generate WAV directly using macOS TTS
    try:
        subprocess.run(['say', text, '-o', wav_path, '--data-format=LEF32@22050'], check=True)
        print(f"[TTS] Audio saved as {wav_path}")
    except Exception as e:
        print(f"[TTS] Error: {e}")
        # Fallback: create a simple WAV file or skip audio
        print("[TTS] Skipping audio generation due to error")

# --- Rhubarb Lip Sync ---
def run_rhubarb(audio_path, output_json, rhubarb_path):
    print("[Rhubarb] Running lip sync analysis...")
    try:
        subprocess.run([rhubarb_path, "-o", output_json, "-f", "json", audio_path], check=True)
        print(f"[Rhubarb] Output: {output_json}")
    except Exception as e:
        print("[Rhubarb] Error running Rhubarb:", e)
        sys.exit(1)

# --- Audio Playback ---
def play_audio(wav_path):
    import sounddevice as sd
    import soundfile as sf
    print(f"[Audio] Playing {wav_path}...")
    data, fs = sf.read(wav_path, dtype='float32')
    sd.play(data, fs)
    sd.wait()

# --- Panda3D App ---
class JARKApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARK - Panda3D Avatar App")
        self.disableMouse()
        self.lipsync_queue = SimpleQueue()
        self.morph_names_present = set()
        self.slider_tables = []  # list of (GeomVertexData.slider_table)
        self.current_morph_weights = {}  # name -> weight [0..1]
        self.fallback_jaw_amount = 0.0   # 0..1 (used when no morphs found)
        self.setup_scene()
        # process lipsync events each frame
        self.taskMgr.add(self._process_lipsync_events, 'process_lipsync_events')
        # view presets
        self._install_view_shortcuts()
        self._schedule_next_blink()
        self.taskMgr.add(self._blink_task, 'blink_task')

    def _install_view_shortcuts(self):
        # 1 = passport (close-up headshot), 2 = full-body
        self.accept('1', self.set_view_passport)
        self.accept('2', self.set_view_full)
        # +/- to zoom in/out a bit
        self.accept('+', lambda: self._nudge_zoom(-0.5))
        self.accept('=', lambda: self._nudge_zoom(-0.5))  # shift+='+'
        self.accept('-', lambda: self._nudge_zoom(+0.5))
        # mouse wheel
        self.accept('wheel_up', lambda: self._nudge_zoom(-0.5))
        self.accept('wheel_down', lambda: self._nudge_zoom(+0.5))

    def _nudge_zoom(self, dy):
        # Move camera along Y axis towards/away from avatar
        pos = self.camera.getPos()
        self.camera.setPos(pos.x, pos.y + dy, pos.z)
        self.camera.lookAt(0, 10, 1.6)
        print(f"[View] Zoom {'in' if dy < 0 else 'out'}: camera Y={self.camera.getY():.2f}")

    def set_view_passport(self):
        # Tight head/shoulders framing (passport-like)
        lens = self.camLens
        lens.setFov(30)
        # Camera closer and slightly above, looking at head
        self.camera.setPos(0, 7.8, 1.6)
        self.camera.lookAt(0, 10, 1.6)
        if hasattr(self, 'avatar'):
            self.avatar.setScale(1.0)
        print("[View] Passport close-up")

    def set_view_full(self):
        # Wider view for full/upper body
        lens = self.camLens
        lens.setFov(50)
        # Pull camera back
        self.camera.setPos(0, 0, 2.2)
        self.camera.lookAt(0, 10, 1.6)
        if hasattr(self, 'avatar'):
            self.avatar.setScale(1.0)
        print("[View] Full-body view")

    def setWindowTitle(self, title):
        props = WindowProperties()
        props.setTitle(title)
        self.win.requestProperties(props)

    def setup_scene(self):
        # Load avatar
        if not os.path.exists(AVATAR_PATH):
            print(f"[3D] Avatar file not found: {AVATAR_PATH}")
            return
        self.avatar = self.loader.loadModel(Filename.fromOsSpecific(AVATAR_PATH))
        self.avatar.reparentTo(self.render)
        self.avatar.setPos(0, 10, 0)
        self.avatar.setScale(1.0)
        # Camera (default to passport close-up)
        self.set_view_passport()
        # Lighting
        ambient = AmbientLight('ambient')
        ambient.setColor((0.4, 0.4, 0.4, 1))
        ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_np)
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.9, 0.9, 0.9, 1))
        dlight_np = self.render.attachNewNode(dlight)
        dlight_np.setHpr(0, -60, 0)
        self.render.setLight(dlight_np)
        # Discover morph targets (blendshapes) if any
        self._discover_morph_targets()

    def _discover_morph_targets(self):
        print("[3D] Scanning for morph targets (blendshapes)...")
        # traverse GeomNodes
        for np in self.avatar.find_all_matches('**/+GeomNode'):
            gnode = np.node()
            if not isinstance(gnode, GeomNode):
                continue
            for i in range(gnode.get_num_geoms()):
                geom = gnode.get_geom(i)
                vdata = geom.get_vertex_data()
                table = vdata.get_slider_table()
                if table:
                    self.slider_tables.append(table)
                    for si in range(table.get_num_sliders()):
                        name = table.get_slider(si).get_name()
                        self.morph_names_present.add(name)
        if self.morph_names_present:
            print("[3D] Found morph targets:", sorted(self.morph_names_present))
            if any(n in self.morph_names_present for n in JAW_MORPHS):
                print("[3D] Jaw morph detected. Will drive jaw alongside phonemes.")
            else:
                print("[3D] No jaw morph detected. Using fallback head/jaw motion.")
        else:
            print("[3D] No morph targets found in model.")

    def set_morph_weight(self, morph_name, weight):
        # Clamp and store target weight for smooth application
        weight = max(0.0, min(1.0, float(weight)))
        self.current_morph_weights[morph_name] = max(weight, self.current_morph_weights.get(morph_name, 0.0))

    def _apply_morph_weights(self):
        decay = 0.85  # stronger persistence for coarticulation
        next_weights = {}
        active_jaw = 0.0
        for name, w in self.current_morph_weights.items():
            # Apply to all slider tables
            for table in self.slider_tables:
                for si in range(table.get_num_sliders()):
                    slider = table.get_slider(si)
                    if slider.get_name() == name:
                        slider.set_slider(w)
            # accumulate jaw intent from any active mouth
            active_jaw = max(active_jaw, w)
            # Decay
            w *= decay
            if w > 0.01:
                next_weights[name] = w
        # Apply jaw morph if present
        if self._has_any(JAW_MORPHS):
            jaw_weight = min(1.0, active_jaw)
            for table in self.slider_tables:
                for si in range(table.get_num_sliders()):
                    slider = table.get_slider(si)
                    if slider.get_name() in JAW_MORPHS:
                        slider.set_slider(jaw_weight)
        self.current_morph_weights = next_weights

    def _apply_fallback_motion(self):
        # Disabled: avoid moving whole character/head
        if not ENABLE_FALLBACK_HEAD_ROTATION:
            return
        if not hasattr(self, 'avatar'):
            return
        base_pitch = 0.0
        pitch_range = 6.0
        pitch = base_pitch - pitch_range * self.fallback_jaw_amount
        h, p, r = self.avatar.getHpr()
        self.avatar.setHpr(h, pitch, r)
        self.fallback_jaw_amount *= 0.90
        if self.fallback_jaw_amount < 0.01:
            self.fallback_jaw_amount = 0.0

    def _process_lipsync_events(self, task):
        micro_intensity = 0.0
        while not self.lipsync_queue.empty():
            phoneme, strength = self.lipsync_queue.get()
            # Use Three.js-style application: decay previous, set current visemes, and drive jaw
            apply_phoneme_three_style(self, phoneme, strength)
            micro_intensity = max(micro_intensity, strength)
        if self.morph_names_present:
            self._apply_morph_weights()
        else:
            self._apply_fallback_motion()  # will no-op if flag disabled
        if ENABLE_HEAD_MICRO_MOTION and micro_intensity > 0:
            self._apply_head_micro_motion(micro_intensity)
        return task.cont

    def _has_any(self, names):
        return any(n in self.morph_names_present for n in names)

    def _apply_head_micro_motion(self, intensity):
        # Disabled: avoid moving whole character/head
        if not ENABLE_HEAD_MICRO_MOTION:
            return
        if not hasattr(self, 'avatar'):
            return
        h, p, r = self.avatar.getHpr()
        self.avatar.setHpr(h, -intensity * 4.0, r)

    def _schedule_next_blink(self):
        self._blink_time = time.time() + random.uniform(2.0, 5.0)
        self._blink_state = 0.0

    def _blink_task(self, task):
        now = time.time()
        if now >= getattr(self, '_blink_time', 0):
            # perform a quick blink if eyelid morphs exist
            if self._has_any(EYELID_MORPHS):
                phase = getattr(self, '_blink_state', 0.0)
                phase += 0.3
                amt = 1.0 - abs(phase - 1.0)  # up-down triangle
                amt = max(0.0, min(1.0, amt))
                for table in self.slider_tables:
                    for si in range(table.get_num_sliders()):
                        slider = table.get_slider(si)
                        if slider.get_name() in EYELID_MORPHS:
                            slider.set_slider(amt)
                if phase >= 2.0:
                    self._schedule_next_blink()
                else:
                    self._blink_state = phase
            else:
                # reschedule if no eyelid morphs
                self._schedule_next_blink()
        return task.cont

# Helpers to mirror Three.js style API
def _iter_sliders(app: 'JARKApp'):
    for table in app.slider_tables:
        for si in range(table.get_num_sliders()):
            yield table.get_slider(si)

def set_viseme(app: 'JARKApp', name: str, value: float):
    value = max(0.0, min(1.0, float(value)))
    for slider in _iter_sliders(app):
        if slider.get_name() == name:
            slider.set_slider(value)

def clear_all_visemes(app: 'JARKApp', decay: float = 0.85):
    # Decay current morph weights we track
    for k, v in list(app.current_morph_weights.items()):
        nv = v * decay
        if nv < 0.01:
            del app.current_morph_weights[k]
        else:
            app.current_morph_weights[k] = nv
    # Also lightly decay any unknown sliders for safety
    for slider in _iter_sliders(app):
        # No direct getter for current weight; we only reliably manage those we set via current_morph_weights
        # So we rely on tracked decay above; unknown sliders are left untouched
        pass

# Apply a phoneme like in the Three.js example: decay then set mapped visemes and jaw
def apply_phoneme_three_style(app: 'JARKApp', phoneme: str, strength: float):
    clear_all_visemes(app, decay=0.80)
    names = PHONEME_TO_MORPH.get(phoneme, [])
    applied = False
    for n in names:
        if n in app.morph_names_present:
            set_viseme(app, n, min(1.0, 0.7 * strength))
            app.current_morph_weights[n] = max(app.current_morph_weights.get(n, 0.0), 0.7 * strength)
            applied = True
    # Strong jaw open/close
    if any(n in app.morph_names_present for n in JAW_MORPHS):
        jaw_val = max(0.0, min(1.0, 0.9 * strength * JAW_MULTIPLIER))
        for jn in JAW_MORPHS:
            if jn in app.morph_names_present:
                set_viseme(app, jn, jaw_val)
    if not applied and 'rest' in app.morph_names_present:
        set_viseme(app, 'rest', 0.3)
        app.current_morph_weights['rest'] = max(app.current_morph_weights.get('rest', 0.0), 0.3)

# --- Lip Sync feeder (reads JSON, enqueues events) ---
def enqueue_lipsync_events(json_path, start_time, app: JARKApp, envelope: 'AudioEnvelope'):
    with open(json_path, 'r') as f:
        data = json.load(f)
    cues = data.get('mouthCues', [])
    print("[LipSync] Phoneme events:")
    for cue in cues:
        t = float(cue['start'])
        phoneme = cue['value']
        print(f"  t={t:.2f}s: {phoneme}")
        now = time.time()
        wait = start_time + t - now
        if wait > 0:
            time.sleep(wait)
        amp = envelope.at(t)
        mul = PHONEME_MULTIPLIER.get(phoneme, 0.7)
        strength = max(0.2, min(1.0, amp * mul))
        app.lipsync_queue.put((phoneme, strength))

# --- Main Demo Flow ---
def generate_order_id():
    return random.randint(1000, 9999)

def main():
    print("[MAIN] Starting JARK Café Avatar System...")
    
    # --- Show avatar GUI first ---
    app = JARKApp()
    print("[MAIN] Avatar GUI initialized")
    
    # --- Create Enhanced Professional GUI ---
    professional_gui = None
    gui_process = None
    
    if ENHANCED_GUI_AVAILABLE is True:
        print("[MAIN] Starting Enhanced Professional GUI...")
        try:
            # Launch GUI as separate process to avoid tkinter/Panda3D conflicts on macOS
            import subprocess
            import sys
            gui_script = os.path.join(os.path.dirname(__file__), 'standalone_gui.py')
            gui_process = subprocess.Popen([sys.executable, gui_script], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
            print("[MAIN] ✅ Enhanced Professional GUI running in separate process")
            print("[MAIN] Professional GUI Features:")
            print("  ✅ Top Bar: Clean header with 'JARK' title")
            print("  ✅ Left Panel: Navigation menu (Home, Orders, Customers, Analytics, Settings, About)")
            print("  ✅ Right Panel: Chat conversation interface with message bubbles")
            print("  ✅ Bottom Panel: Avatar status and system information")
            print("  ✅ Modern Design: Minimal, professional with rounded corners and shadows")
            print("  ✅ Responsive: Works on desktop and mobile")
            print("  ✅ Interactive: Real-time chat, menu navigation, status updates")
            print("[MAIN] 🎯 Both 3D Avatar and Professional GUI are now running!")
        except Exception as e:
            print(f"[MAIN] Enhanced GUI failed to start: {e}")
            gui_process = None
    elif ENHANCED_GUI_AVAILABLE is False:
        print("[MAIN] Using basic GUI fallback")
    else:
        print("[MAIN] No GUI available - avatar only mode")
    
    # --- Create GUI Interface in simple mode ---
    print("[MAIN] Web GUI also available at: file:///Users/msk/Desktop/jarks/char/jark_web_gui.html")
    
    # --- Run café logic with avatar as GUI ---
    print("[MAIN] Setting up café module imports...")
    import importlib.util
    import sys
    
    # Import café modules using correct path
    jarkes_path = os.path.join(os.path.dirname(__file__), '../jarkes')
    print(f"[MAIN] Adding path: {jarkes_path}")
    sys.path.insert(0, jarkes_path)
    
    # Import modules with error handling
    print("[MAIN] Importing café modules...")
    
    # Import with individual try-catch for each module
    recognize_face = None
    take_order = None
    handle_feedback = None
    speak = None
    
    try:
        print("[MAIN] Importing order_manager...")
        from order_manager import take_order, speak, show_menu_console_and_speak  # type: ignore
        print("[MAIN] ✓ order_manager imported")
    except Exception as e:
        print(f"[MAIN] order_manager import failed: {e}")
        
    try:
        print("[MAIN] Importing feedback_manager...")
        from feedback_manager import handle_feedback  # type: ignore
        print("[MAIN] ✓ feedback_manager imported")
    except Exception as e:
        print(f"[MAIN] feedback_manager import failed: {e}")
        
    try:
        print("[MAIN] Importing face_recognizer (this may take a moment)...")
        # Skip the problematic face_recognizer for now and use fallback
        raise ImportError("Skipping face_recognizer due to import issues")
        from recognizer.face_recognizer import recognize_face  # type: ignore
        print("[MAIN] ✓ face_recognizer imported")
    except Exception as e:
        print(f"[MAIN] face_recognizer import failed: {e}")
        print("[MAIN] Using fallback recognition...")
        def recognize_face():
            return "Demo Customer", "new", "male"
    
    # Provide fallbacks for any missing functions
    if not take_order:
        def take_order(customer_name, gender):
            print(f"[DEMO] Taking order for {customer_name}")
            speak("Welcome! Here's our menu...")
            speak("We have coffee, tea, sandwiches, and pastries.")
            speak("For this demo, I'll prepare a coffee for you.")
            speak("Your order is being prepared!")
            time.sleep(2)
            speak("Your order is ready! Enjoy your coffee!")
    if not handle_feedback:
        def handle_feedback(order_id):
            print(f"[DEMO] Handling feedback for order {order_id}")
    if not speak:
        def speak(text):
            print(f"[SPEAK] {text}")
    
   

    
    # Run café logic in a separate thread while avatar GUI is running
    def run_cafe_logic():
        try:
            print("[CAFE] Starting café logic thread...")
            
            time.sleep(2)  # Give avatar GUI time to fully initialize
            
            speak("[LOG] Welcome to JARK Café!")
            
            print("[LOG] Starting face recognition...")
            current_customer_name, user_type, current_gender = recognize_face()
            print(f"[LOG] Name: {current_customer_name}, User Type: {user_type}, Gender: {current_gender}")
            
            if not current_customer_name:
                speak("Sorry, I couldn't detect you. Please try again.")
            else:
                take_order(customer_name=current_customer_name, gender=current_gender)

            speak("Sir, before you leave, could you please share your feedback?")
                
            handle_feedback(order_id=generate_order_id())

            speak("Thank you for visiting JARK Café! Have a great day!")
            speak("[LOG] Goodbye!")
            time.sleep(3)
            
        except Exception as e:
            print(f"[CAFE ERROR] Exception in café logic: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("[CAFE] Café logic thread completed")
            # Don't close the GUI automatically - let user interact
    
    # Start café logic in background thread
    print("[MAIN] Creating café logic thread...")
    cafe_thread = threading.Thread(target=run_cafe_logic)
    cafe_thread.daemon = True  # Thread will close when main program exits
    print("[MAIN] Starting café logic thread...")
    cafe_thread.start()
    
    print("[MAIN] Avatar GUI starting...")
    print("[MAIN] Access the web GUI at: file:///Users/msk/Desktop/jarks/char/jark_web_gui.html")
    
    # Run avatar GUI (this will block until userExit() is called)
    try:
        app.run()
    except KeyboardInterrupt:
        print("[MAIN] Interrupted by user")
    
    print("[MAIN] Avatar GUI closed, waiting for threads...")
    # Wait for café logic to complete
    cafe_thread.join(timeout=2)
    print("[MAIN] JARK Café system shutdown complete")

if __name__ == '__main__':
    main()
