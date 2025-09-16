# standalone_gui.py - Run professional GUI as standalone process
#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    try:
        from enhanced_jark_gui import JARKProfessionalGUI
        
        print("[STANDALONE GUI] Starting JARK Professional GUI...")
        
        # Create and run the GUI
        gui = JARKProfessionalGUI()
        
        print("[STANDALONE GUI] Professional GUI Features Active:")
        print("  ✅ Top Bar: Clean header with 'JARK' title")
        print("  ✅ Left Panel: Navigation menu (Home, Orders, Customers, Analytics, Settings, About)")
        print("  ✅ Right Panel: Chat conversation interface with message bubbles")
        print("  ✅ Bottom Panel: Avatar status and system information")
        print("  ✅ Modern Design: Minimal, professional with rounded corners and shadows")
        print("  ✅ Responsive: Works on desktop and mobile")
        print("  ✅ Interactive: Real-time chat, menu navigation, status updates")
        print("[STANDALONE GUI] Professional GUI ready!")
        
        # Add welcome message
        gui.add_system_message("JARK Professional System ready! The 3D avatar will appear separately.")
        gui.update_avatar_status("Connected to 3D avatar system")
        
        # Run the GUI
        gui.run()
        
    except Exception as e:
        print(f"[STANDALONE GUI] Error: {e}")
        import traceback
        traceback.print_exc()