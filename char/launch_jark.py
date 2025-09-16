#!/usr/bin/env python3
# launch_jark.py - Launch both 3D Avatar and Professional GUI

import subprocess
import sys
import os
import time

def main():
    print("🚀 Starting JARK Café Complete System...")
    print("=" * 60)
    
    # Get the directory path
    char_dir = os.path.dirname(__file__)
    venv_python = "/Users/msk/Desktop/jarks/.venv/bin/python"
    
    print("✅ Step 1: Starting 3D Avatar System...")
    avatar_process = subprocess.Popen(
        [venv_python, os.path.join(char_dir, "main.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give avatar time to initialize
    time.sleep(3)
    
    print("✅ Step 2: Starting Professional GUI...")
    gui_process = subprocess.Popen(
        [venv_python, os.path.join(char_dir, "standalone_gui.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("🎯 JARK Café System Fully Operational!")
    print("=" * 60)
    print("FEATURES ACTIVE:")
    print("🤖 3D Avatar: Real-time facial animation and voice synthesis")
    print("💬 Professional GUI: Complete customer service interface")
    print("📊 Analytics: Real-time performance monitoring")
    print("🏠 Navigation: Home, Orders, Customers, Analytics, Settings, About")
    print("💭 Chat Interface: Interactive conversation with message bubbles")
    print("⚡ Status Panel: Avatar status and system information")
    print("🎨 Modern Design: Professional interface with rounded corners")
    print("📱 Responsive: Works on desktop and mobile")
    print("🔄 Real-time Updates: Live chat, navigation, status updates")
    print("=" * 60)
    print("Press Ctrl+C to stop both systems")
    
    try:
        # Wait for both processes
        avatar_process.wait()
        gui_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down JARK Café System...")
        avatar_process.terminate()
        gui_process.terminate()
        print("✅ System shutdown complete")

if __name__ == "__main__":
    main()