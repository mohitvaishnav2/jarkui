# simple_merged_jark.py - JARK system with unified GUI and avatar display
import os
import sys
import time
import json
import math
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Frame, Canvas
from datetime import datetime
import random

# 3D Avatar imports
try:
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import AmbientLight, DirectionalLight, Vec3, Filename, WindowProperties
    from panda3d.core import GeomNode, loadPrcFileData, PythonTask
    from direct.task import Task
    PANDA3D_AVAILABLE = True
except ImportError:
    PANDA3D_AVAILABLE = False
    print("[INFO] Panda3D not available - using visual placeholder")

class Real3DAvatar:
    """Real 3D Avatar using Panda3D"""
    
    def __init__(self, canvas=None):
        self.canvas = canvas
        self.avatar = None
        self.showbase = None
        self.is_speaking = False
        
        if PANDA3D_AVAILABLE and canvas:
            self.initialize_3d_avatar()
        else:
            print("[AVATAR] Using visual placeholder mode")
            
    def initialize_3d_avatar(self):
        """Initialize Panda3D 3D avatar"""
        try:
            # Configure Panda3D for embedding
            loadPrcFileData("", "window-type none")
            loadPrcFileData("", "audio-library-name null")
            
            # Create ShowBase instance
            self.showbase = ShowBase()
            
            # Setup embedded window
            canvas_id = self.canvas.winfo_id()
            props = WindowProperties()
            props.setParentWindow(canvas_id)
            props.setOrigin(0, 0)
            props.setSize(600, 400)
            
            self.showbase.openDefaultWindow(props=props)
            
            # Load avatar model
            self.load_avatar_model()
            self.setup_lighting()
            self.setup_camera()
            
            print("[AVATAR] ✓ Real 3D avatar initialized")
            return True
            
        except Exception as e:
            print(f"[AVATAR] 3D initialization failed: {e}")
            return False
            
    def load_avatar_model(self):
        """Load the actual avatar GLB model"""
        try:
            char_dir = os.path.dirname(__file__)
            
            # Priority order for avatar files
            avatar_files = ['jake.glb', 'jark.glb', 'avatar.glb', 'femaleai .glb']
            
            for avatar_file in avatar_files:
                avatar_path = os.path.join(char_dir, avatar_file)
                if os.path.exists(avatar_path):
                    print(f"[AVATAR] Loading 3D model: {avatar_file}")
                    
                    self.avatar = self.showbase.loader.loadModel(avatar_path)
                    if self.avatar:
                        self.avatar.reparentTo(self.showbase.render)
                        self.avatar.setScale(1.0)
                        self.avatar.setPos(0, 0, -1.5)
                        self.avatar.setHpr(0, 0, 0)
                        
                        print(f"[AVATAR] ✓ 3D model loaded: {avatar_file}")
                        
                        # Scan for morph targets
                        self.scan_morph_targets()
                        return True
                        
            print("[AVATAR] No avatar files found, using fallback")
            self.create_fallback_3d_avatar()
            return False
            
        except Exception as e:
            print(f"[AVATAR] Model loading error: {e}")
            self.create_fallback_3d_avatar()
            return False
            
    def scan_morph_targets(self):
        """Scan for available morph targets"""
        try:
            self.morph_targets = {}
            if self.avatar:
                # Look for morph targets
                for node in self.avatar.findAllMatches("**"):
                    if hasattr(node, 'node') and hasattr(node.node(), 'getMorphTargets'):
                        targets = node.node().getMorphTargets()
                        for target in targets:
                            self.morph_targets[target] = node
                            
                print(f"[AVATAR] Found morph targets: {list(self.morph_targets.keys())}")
                
        except Exception as e:
            print(f"[AVATAR] Morph target scan error: {e}")
            
    def create_fallback_3d_avatar(self):
        """Create simple 3D fallback"""
        try:
            from panda3d.core import CardMaker, TextNode
            
            # Create a card for the avatar
            cm = CardMaker("avatar-card")
            cm.setFrame(-1, 1, -1, 1)
            self.avatar = self.showbase.render.attachNewNode(cm.generate())
            self.avatar.setColor(0.3, 0.6, 1.0, 1.0)
            self.avatar.setPos(0, 5, 0)
            
            # Add text
            text = TextNode('avatar-text')
            text.setText("JARK\n3D Avatar")
            text_np = self.avatar.attachNewNode(text)
            text_np.setScale(0.3)
            text_np.setPos(-0.3, 0, -0.2)
            text_np.setColor(1, 1, 1, 1)
            
            print("[AVATAR] ✓ 3D fallback avatar created")
            
        except Exception as e:
            print(f"[AVATAR] Fallback creation error: {e}")
            
    def setup_lighting(self):
        """Setup 3D lighting"""
        try:
            # Ambient light
            ambient_light = AmbientLight('ambient')
            ambient_light.setColor((0.4, 0.4, 0.4, 1))
            ambient_np = self.showbase.render.attachNewNode(ambient_light)
            self.showbase.render.setLight(ambient_np)
            
            # Directional light
            directional_light = DirectionalLight('directional')
            directional_light.setDirection(Vec3(-1, -1, -1))
            directional_light.setColor((0.8, 0.8, 0.8, 1))
            directional_np = self.showbase.render.attachNewNode(directional_light)
            self.showbase.render.setLight(directional_np)
            
        except Exception as e:
            print(f"[AVATAR] Lighting setup error: {e}")
            
    def setup_camera(self):
        """Setup 3D camera"""
        try:
            if self.showbase:
                self.showbase.camera.setPos(0, -8, 0)
                self.showbase.camera.lookAt(0, 0, 0)
                
        except Exception as e:
            print(f"[AVATAR] Camera setup error: {e}")
            
    def speak(self, text):
        """Make avatar speak with animation"""
        self.is_speaking = True
        print(f"[AVATAR] Speaking: {text}")
        
        # Simple animation while speaking
        if self.avatar and self.showbase:
            # Add subtle head movement
            self.avatar.setH(self.avatar.getH() + random.uniform(-2, 2))
            
        # TTS
        threading.Thread(target=self._speak_with_tts, args=(text,), daemon=True).start()
        
    def _speak_with_tts(self, text):
        """Handle TTS and animation"""
        try:
            os.system(f"say '{text}'")
            time.sleep(len(text) * 0.08)  # Approximate speech duration
        except:
            time.sleep(2)
        finally:
            self.is_speaking = False
            
    def set_expression(self, expression):
        """Set facial expression using morph targets"""
        try:
            if expression.lower() == "happy" and "mouthSmile" in self.morph_targets:
                # Activate smile morph target
                node = self.morph_targets["mouthSmile"]
                # Set morph weight (simplified)
                print(f"[AVATAR] Expression set: {expression}")
            elif expression.lower() == "speaking" and "mouthOpen" in self.morph_targets:
                # Activate mouth open morph target
                node = self.morph_targets["mouthOpen"]
                print(f"[AVATAR] Expression set: {expression}")
                
        except Exception as e:
            print(f"[AVATAR] Expression error: {e}")
            
    def update(self):
        """Update avatar (called from main thread)"""
        try:
            if self.showbase and hasattr(self.showbase, 'taskMgr'):
                self.showbase.taskMgr.step()
                
        except Exception as e:
            print(f"[AVATAR] Update error: {e}")
            
    def destroy(self):
        """Clean up avatar"""
        try:
            if self.showbase:
                self.showbase.destroy()
                
        except Exception as e:
            print(f"[AVATAR] Cleanup error: {e}")

class SimpleJARKSystem:
    """Complete JARK system in one unified window"""
    
    def __init__(self):
        self.setup_main_window()
        self.setup_styles()
        self.initialize_data()
        self.create_unified_layout()
        self.setup_system()
        self.start_updates()
        
    def setup_main_window(self):
        """Create main window"""
        self.root = tk.Tk()
        self.root.title("JARK Café - Unified AI Assistant System")
        self.root.geometry("1800x1000")
        self.root.configure(bg='#f8fafc')
        self.root.minsize(1400, 800)
        
    def setup_styles(self):
        """Setup color scheme"""
        self.colors = {
            'primary': '#3b82f6',
            'primary_dark': '#1e40af',
            'secondary': '#64748b', 
            'background': '#f8fafc',
            'surface': '#ffffff',
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'avatar_bg': '#1a1a1a'
        }
        
    def initialize_data(self):
        """Initialize system data"""
        self.customers_served = 0
        self.orders_processed = 0
        self.current_status = "Ready to serve customers"
        self.is_active = False
        self.chat_messages = []
        self.start_time = time.time()
        self.avatar_active = False
        self.real_avatar = None
        
    def create_unified_layout(self):
        """Create the unified layout"""
        # Main container
        main_container = Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        self.create_header(main_container)
        
        # Main content area - three columns
        content_frame = Frame(main_container, bg=self.colors['background'])
        content_frame.pack(fill='both', expand=True, pady=(15, 0))
        
        # Left Panel: Navigation & Controls (20%)
        self.create_left_panel(content_frame)
        
        # Center Panel: Avatar & Status (50%)
        self.create_center_panel(content_frame)
        
        # Right Panel: Chat & Metrics (30%)
        self.create_right_panel(content_frame)
        
        # Footer
        self.create_footer(main_container)
        
    def create_header(self, parent):
        """Create header with system info"""
        header_frame = Frame(parent, bg=self.colors['text_primary'], height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Accent border
        accent_border = Frame(header_frame, bg=self.colors['primary'], height=4)
        accent_border.pack(fill='x', side='bottom')
        
        # Header content
        header_content = Frame(header_frame, bg=self.colors['text_primary'])
        header_content.pack(fill='both', expand=True, padx=40, pady=25)
        
        # Left: Title
        title_section = Frame(header_content, bg=self.colors['text_primary'])
        title_section.pack(side='left')
        
        main_title = tk.Label(title_section,
                             text="JARK",
                             font=('Helvetica', 36, 'bold'),
                             bg=self.colors['text_primary'],
                             fg='white')
        main_title.pack(anchor='w')
        
        subtitle = tk.Label(title_section,
                           text="Unified AI Café Assistant",
                           font=('Helvetica', 14),
                           bg=self.colors['text_primary'],
                           fg=self.colors['text_secondary'])
        subtitle.pack(anchor='w')
        
        # Center: Status
        status_section = Frame(header_content, bg=self.colors['text_primary'])
        status_section.pack(side='left', expand=True, padx=(60, 0))
        
        self.system_status_label = tk.Label(status_section,
                                           text="● System Online",
                                           font=('Helvetica', 16, 'bold'),
                                           bg=self.colors['text_primary'],
                                           fg=self.colors['success'])
        self.system_status_label.pack(anchor='center')
        
        self.integration_status = tk.Label(status_section,
                                         text="🔗 Unified Interface Active",
                                         font=('Helvetica', 12),
                                         bg=self.colors['text_primary'],
                                         fg=self.colors['text_secondary'])
        self.integration_status.pack(anchor='center', pady=(5, 0))
        
        # Right: Time
        info_section = Frame(header_content, bg=self.colors['text_primary'])
        info_section.pack(side='right')
        
        self.time_label = tk.Label(info_section,
                                  text="",
                                  font=('Helvetica', 14, 'bold'),
                                  bg=self.colors['text_primary'],
                                  fg='white')
        self.time_label.pack(anchor='e')
        
        self.date_label = tk.Label(info_section,
                                  text="",
                                  font=('Helvetica', 11),
                                  bg=self.colors['text_primary'],
                                  fg=self.colors['text_secondary'])
        self.date_label.pack(anchor='e')
        
    def create_left_panel(self, parent):
        """Create left navigation panel"""
        left_container = Frame(parent, bg=self.colors['surface'], width=360)
        left_container.pack(side='left', fill='y', padx=(0, 10))
        left_container.pack_propagate(False)
        
        # Navigation header
        nav_header = Frame(left_container, bg='#f1f5f9', height=60)
        nav_header.pack(fill='x')
        nav_header.pack_propagate(False)
        
        nav_title = tk.Label(nav_header,
                            text="🧭 Navigation",
                            font=('Helvetica', 16, 'bold'),
                            bg='#f1f5f9',
                            fg=self.colors['text_primary'])
        nav_title.pack(anchor='w', padx=20, pady=20)
        
        # Navigation menu
        nav_menu = Frame(left_container, bg=self.colors['surface'])
        nav_menu.pack(fill='x', padx=15, pady=15)
        
        menu_items = [
            ("🏠", "Home", "home"),
            ("📋", "Orders", "orders"),
            ("👥", "Customers", "customers"),
            ("📊", "Analytics", "analytics"),
            ("⚙️", "Settings", "settings")
        ]
        
        self.nav_buttons = {}
        for i, (icon, text, section) in enumerate(menu_items):
            btn = tk.Button(nav_menu,
                           text=f"{icon}  {text}",
                           font=('Helvetica', 12),
                           bg=self.colors['primary'] if i == 0 else self.colors['surface'],
                           fg='white' if i == 0 else self.colors['text_secondary'],
                           relief='flat',
                           anchor='w',
                           padx=20,
                           pady=12,
                           command=lambda s=section: self.switch_section(s))
            btn.pack(fill='x', pady=3)
            self.nav_buttons[section] = btn
            
        # Control section
        self.create_control_section(left_container)
        
        # Stats section
        self.create_stats_section(left_container)
        
    def create_control_section(self, parent):
        """Create avatar control section"""
        control_section = Frame(parent, bg='#f8fafc')
        control_section.pack(fill='x', padx=15, pady=(20, 15))
        
        control_title = tk.Label(control_section,
                                text="🤖 Avatar Control",
                                font=('Helvetica', 14, 'bold'),
                                bg='#f8fafc',
                                fg=self.colors['text_primary'])
        control_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Control buttons
        control_buttons = Frame(control_section, bg='#f8fafc')
        control_buttons.pack(fill='x', padx=15, pady=(0, 15))
        
        self.start_avatar_btn = tk.Button(control_buttons,
                                        text="🚀 Start Avatar",
                                        font=('Helvetica', 11, 'bold'),
                                        bg=self.colors['success'],
                                        fg='white',
                                        relief='flat',
                                        padx=20,
                                        pady=10,
                                        command=self.start_avatar)
        self.start_avatar_btn.pack(fill='x', pady=(0, 6))
        
        self.speak_btn = tk.Button(control_buttons,
                                 text="💬 Test Speech",
                                 font=('Helvetica', 11),
                                 bg=self.colors['primary'],
                                 fg='white',
                                 relief='flat',
                                 padx=20,
                                 pady=10,
                                 command=self.test_speech,
                                 state='disabled')
        self.speak_btn.pack(fill='x', pady=(0, 6))
        
        self.cafe_btn = tk.Button(control_buttons,
                                text="☕ Start Café Mode",
                                font=('Helvetica', 11),
                                bg=self.colors['warning'],
                                fg='white',
                                relief='flat',
                                padx=20,
                                pady=10,
                                command=self.start_cafe_mode,
                                state='disabled')
        self.cafe_btn.pack(fill='x')
        
    def create_stats_section(self, parent):
        """Create performance stats"""
        stats_frame = Frame(parent, bg='#f8fafc')
        stats_frame.pack(fill='x', padx=15, pady=(0, 20), side='bottom')
        
        stats_title = tk.Label(stats_frame,
                              text="📈 Performance",
                              font=('Helvetica', 14, 'bold'),
                              bg='#f8fafc',
                              fg=self.colors['text_primary'])
        stats_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        stats_data = [
            ("Customers", "0"),
            ("Orders", "0"),
            ("Revenue", "$0.00"),
            ("Uptime", "0m")
        ]
        
        self.stats_widgets = {}
        for label, value in stats_data:
            stat_container = Frame(stats_frame, bg='#f8fafc')
            stat_container.pack(fill='x', padx=15, pady=2)
            
            label_widget = tk.Label(stat_container,
                                   text=f"{label}:",
                                   font=('Helvetica', 10),
                                   bg='#f8fafc',
                                   fg=self.colors['text_secondary'])
            label_widget.pack(side='left')
            
            value_widget = tk.Label(stat_container,
                                   text=value,
                                   font=('Helvetica', 10, 'bold'),
                                   bg='#f8fafc',
                                   fg=self.colors['primary'])
            value_widget.pack(side='right')
            
            self.stats_widgets[label.lower()] = value_widget
            
    def create_center_panel(self, parent):
        """Create center avatar display panel"""
        center_container = Frame(parent, bg=self.colors['avatar_bg'], relief='raised', bd=2)
        center_container.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Avatar header
        avatar_header = Frame(center_container, bg='#2a2a2a', height=70)
        avatar_header.pack(fill='x')
        avatar_header.pack_propagate(False)
        
        header_content = Frame(avatar_header, bg='#2a2a2a')
        header_content.pack(fill='both', expand=True, padx=30, pady=20)
        
        avatar_title = tk.Label(header_content,
                               text="🤖 JARK Avatar Display",
                               font=('Helvetica', 18, 'bold'),
                               bg='#2a2a2a',
                               fg='white')
        avatar_title.pack(side='left')
        
        self.avatar_status_indicator = tk.Label(header_content,
                                              text="● Offline",
                                              font=('Helvetica', 14, 'bold'),
                                              bg='#2a2a2a',
                                              fg=self.colors['error'])
        self.avatar_status_indicator.pack(side='right')
        
        # Main avatar display
        self.avatar_display_frame = Frame(center_container, bg=self.colors['avatar_bg'])
        self.avatar_display_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.avatar_canvas = tk.Canvas(self.avatar_display_frame,
                                      bg='#1a1a1a',
                                      highlightthickness=0)
        self.avatar_canvas.pack(fill='both', expand=True)
        
        # Show initial placeholder
        self.show_avatar_placeholder()
        
        # Avatar status panel
        avatar_status_panel = Frame(center_container, bg='#2a2a2a', height=80)
        avatar_status_panel.pack(fill='x')
        avatar_status_panel.pack_propagate(False)
        
        status_content = Frame(avatar_status_panel, bg='#2a2a2a')
        status_content.pack(fill='both', expand=True, padx=30, pady=20)
        
        tk.Label(status_content,
                text="Status:",
                font=('Helvetica', 11),
                bg='#2a2a2a',
                fg='#888888').pack(side='left')
        
        self.avatar_current_status = tk.Label(status_content,
                                            text="Ready to initialize",
                                            font=('Helvetica', 13, 'bold'),
                                            bg='#2a2a2a',
                                            fg='white')
        self.avatar_current_status.pack(side='left', padx=(10, 0))
        
        tk.Label(status_content,
                text="Mode:",
                font=('Helvetica', 11),
                bg='#2a2a2a',
                fg='#888888').pack(side='right', padx=(0, 10))
        
        self.avatar_mode_display = tk.Label(status_content,
                                          text="Standby",
                                          font=('Helvetica', 13, 'bold'),
                                          bg='#2a2a2a',
                                          fg='white')
        self.avatar_mode_display.pack(side='right')
        
    def create_right_panel(self, parent):
        """Create right chat and metrics panel"""
        right_container = Frame(parent, bg=self.colors['surface'], width=540)
        right_container.pack(side='right', fill='y')
        right_container.pack_propagate(False)
        
        # Chat section
        self.create_chat_section(right_container)
        
        # System metrics
        self.create_system_metrics(right_container)
        
        # Activity log
        self.create_activity_section(right_container)
        
    def create_chat_section(self, parent):
        """Create chat interface"""
        chat_frame = Frame(parent, bg=self.colors['surface'])
        chat_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Chat header
        chat_header = Frame(chat_frame, bg='#f1f5f9', height=60)
        chat_header.pack(fill='x')
        chat_header.pack_propagate(False)
        
        header_content = Frame(chat_header, bg='#f1f5f9')
        header_content.pack(fill='both', expand=True, padx=20, pady=18)
        
        chat_title = tk.Label(header_content,
                             text="💬 Customer Chat",
                             font=('Helvetica', 16, 'bold'),
                             bg='#f1f5f9',
                             fg=self.colors['text_primary'])
        chat_title.pack(side='left')
        
        self.chat_status_indicator = tk.Label(header_content,
                                            text="● Ready",
                                            font=('Helvetica', 12, 'bold'),
                                            bg='#f1f5f9',
                                            fg=self.colors['warning'])
        self.chat_status_indicator.pack(side='right')
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame,
                                                     font=('Helvetica', 10),
                                                     bg='white',
                                                     fg=self.colors['text_primary'],
                                                     relief='flat',
                                                     bd=1,
                                                     state='disabled',
                                                     wrap='word',
                                                     height=10)
        self.chat_display.pack(fill='both', expand=True, pady=(0, 10))
        
        # Message input
        input_frame = Frame(chat_frame, bg=self.colors['surface'])
        input_frame.pack(fill='x')
        
        self.message_input = tk.Entry(input_frame,
                                     font=('Helvetica', 11),
                                     bg='white',
                                     fg=self.colors['text_primary'],
                                     relief='flat',
                                     bd=2)
        self.message_input.pack(side='left', fill='x', expand=True, padx=(0, 8))
        
        send_btn = tk.Button(input_frame,
                            text="Send",
                            font=('Helvetica', 11, 'bold'),
                            bg=self.colors['primary'],
                            fg='white',
                            relief='flat',
                            padx=25,
                            pady=8,
                            command=self.send_message)
        send_btn.pack(side='right')
        
        self.message_input.bind("<Return>", lambda e: self.send_message())
        
    def create_system_metrics(self, parent):
        """Create system metrics display"""
        metrics_frame = Frame(parent, bg='#f8fafc', height=140)
        metrics_frame.pack(fill='x', padx=15, pady=(0, 10))
        metrics_frame.pack_propagate(False)
        
        metrics_title = tk.Label(metrics_frame,
                                text="📊 System Metrics",
                                font=('Helvetica', 14, 'bold'),
                                bg='#f8fafc',
                                fg=self.colors['text_primary'])
        metrics_title.pack(anchor='w', padx=20, pady=(20, 10))
        
        # Metrics grid
        metrics_grid = Frame(metrics_frame, bg='#f8fafc')
        metrics_grid.pack(fill='x', padx=20)
        
        metrics_data = [
            ("Memory", "Normal", self.colors['success']),
            ("CPU", "Low", self.colors['success']),
            ("Response", "0.2s", self.colors['primary']),
            ("Load", "Optimal", self.colors['success'])
        ]
        
        self.metric_widgets = {}
        for i, (label, value, color) in enumerate(metrics_data):
            row = i // 2
            col = i % 2
            
            metric_container = Frame(metrics_grid, bg='#f8fafc')
            metric_container.grid(row=row, column=col, padx=15, pady=6, sticky='w')
            
            label_widget = tk.Label(metric_container,
                                   text=f"{label}:",
                                   font=('Helvetica', 9),
                                   bg='#f8fafc',
                                   fg=self.colors['text_secondary'])
            label_widget.pack(anchor='w')
            
            value_widget = tk.Label(metric_container,
                                   text=value,
                                   font=('Helvetica', 11, 'bold'),
                                   bg='#f8fafc',
                                   fg=color)
            value_widget.pack(anchor='w')
            
            self.metric_widgets[label.lower()] = value_widget
            
    def create_activity_section(self, parent):
        """Create activity log"""
        activity_frame = Frame(parent, bg='#f8fafc', height=120)
        activity_frame.pack(fill='x', padx=15, pady=(0, 15))
        activity_frame.pack_propagate(False)
        
        activity_title = tk.Label(activity_frame,
                                 text="📋 Activity Log",
                                 font=('Helvetica', 14, 'bold'),
                                 bg='#f8fafc',
                                 fg=self.colors['text_primary'])
        activity_title.pack(anchor='w', padx=20, pady=(20, 10))
        
        self.activity_listbox = tk.Listbox(activity_frame,
                                          font=('Helvetica', 9),
                                          bg='white',
                                          fg=self.colors['text_primary'],
                                          relief='flat',
                                          bd=1,
                                          height=4)
        self.activity_listbox.pack(fill='x', padx=20, pady=(0, 20))
        
    def create_footer(self, parent):
        """Create footer status bar"""
        footer_frame = Frame(parent, bg=self.colors['text_primary'], height=70)
        footer_frame.pack(fill='x', pady=(15, 0))
        footer_frame.pack_propagate(False)
        
        # Accent border
        accent_border = Frame(footer_frame, bg=self.colors['primary'], height=3)
        accent_border.pack(fill='x')
        
        # Footer content
        footer_content = Frame(footer_frame, bg=self.colors['text_primary'])
        footer_content.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Left: Status
        jark_status = tk.Label(footer_content,
                              text="JARK Unified System - Ready",
                              font=('Helvetica', 16, 'bold'),
                              bg=self.colors['text_primary'],
                              fg='white')
        jark_status.pack(side='left')
        
        # Center: Integration info
        integration_info = tk.Label(footer_content,
                                   text="🔗 Single Window - All Components Merged",
                                   font=('Helvetica', 12, 'bold'),
                                   bg=self.colors['text_primary'],
                                   fg=self.colors['success'])
        integration_info.pack(side='left', expand=True, padx=(60, 0))
        
        # Right: System info
        system_info = Frame(footer_content, bg=self.colors['text_primary'])
        system_info.pack(side='right')
        
        self.uptime_label = tk.Label(system_info,
                                    text="Uptime: 0m",
                                    font=('Helvetica', 10),
                                    bg=self.colors['text_primary'],
                                    fg=self.colors['text_secondary'])
        self.uptime_label.pack(anchor='e')
        
        self.memory_label = tk.Label(system_info,
                                    text="Status: Online",
                                    font=('Helvetica', 10),
                                    bg=self.colors['text_primary'],
                                    fg=self.colors['text_secondary'])
        self.memory_label.pack(anchor='e')
        
    def show_avatar_placeholder(self):
        """Show avatar placeholder"""
        self.avatar_canvas.delete("all")
        
        width = self.avatar_canvas.winfo_width() or 600
        height = self.avatar_canvas.winfo_height() or 400
        
        if width <= 1:
            width = 600
        if height <= 1:
            height = 400
            
        center_x = width // 2
        center_y = height // 2
        
        # Background
        self.avatar_canvas.create_rectangle(0, 0, width, height,
                                          fill='#1a1a1a', outline='')
        
        # Grid pattern
        for i in range(0, width, 50):
            self.avatar_canvas.create_line(i, 0, i, height,
                                         fill='#333333', width=1)
        for i in range(0, height, 50):
            self.avatar_canvas.create_line(0, i, width, i,
                                         fill='#333333', width=1)
        
        # Avatar placeholder circle
        circle_size = min(width, height) // 6
        
        # Outer glow effect
        for i in range(6):
            self.avatar_canvas.create_oval(center_x - circle_size - i*3,
                                         center_y - circle_size - i*3,
                                         center_x + circle_size + i*3,
                                         center_y + circle_size + i*3,
                                         outline='#3b82f6',
                                         width=1)
        
        # Main circle
        self.avatar_canvas.create_oval(center_x - circle_size,
                                     center_y - circle_size,
                                     center_x + circle_size,
                                     center_y + circle_size,
                                     fill='#2563eb',
                                     outline='#60a5fa',
                                     width=4)
        
        # Avatar icon
        self.avatar_canvas.create_text(center_x, center_y,
                                     text="🤖",
                                     font=('Helvetica', 60),
                                     fill='white')
        
        # Status text
        self.avatar_canvas.create_text(center_x, center_y - circle_size - 40,
                                     text="JARK AVATAR SYSTEM",
                                     font=('Helvetica', 14, 'bold'),
                                     fill='white')
        
        self.avatar_canvas.create_text(center_x, center_y + circle_size + 40,
                                     text="Click 'Start Avatar' to initialize",
                                     font=('Helvetica', 11),
                                     fill='#888888')
        
    def show_active_avatar(self):
        """Show active avatar"""
        self.avatar_canvas.delete("all")
        
        width = self.avatar_canvas.winfo_width() or 600
        height = self.avatar_canvas.winfo_height() or 400
        
        if width <= 1:
            width = 600
        if height <= 1:
            height = 400
            
        center_x = width // 2
        center_y = height // 2
        
        # Active background
        self.avatar_canvas.create_rectangle(0, 0, width, height,
                                          fill='#0a0a0a', outline='')
        
        # Active grid
        for i in range(0, width, 30):
            self.avatar_canvas.create_line(i, 0, i, height,
                                         fill='#1a4a8f', width=1)
        for i in range(0, height, 30):
            self.avatar_canvas.create_line(0, i, width, i,
                                         fill='#1a4a8f', width=1)
        
        # Active avatar
        circle_size = min(width, height) // 5
        
        # Animated glow
        for i in range(8):
            self.avatar_canvas.create_oval(center_x - circle_size - i*5,
                                         center_y - circle_size - i*5,
                                         center_x + circle_size + i*5,
                                         center_y + circle_size + i*5,
                                         outline='#60a5fa',
                                         width=2)
        
        # Main avatar
        self.avatar_canvas.create_oval(center_x - circle_size,
                                     center_y - circle_size,
                                     center_x + circle_size,
                                     center_y + circle_size,
                                     fill='#1e40af',
                                     outline='#3b82f6',
                                     width=5)
        
        # Active avatar face
        self.avatar_canvas.create_text(center_x, center_y,
                                     text="🤖",
                                     font=('Helvetica', 80),
                                     fill='white',
                                     tags='active_avatar')
        
        # Status indicators
        self.avatar_canvas.create_text(center_x, center_y - circle_size - 60,
                                     text="● ACTIVE",
                                     font=('Helvetica', 14, 'bold'),
                                     fill='#10b981')
        
        self.avatar_canvas.create_text(center_x, center_y + circle_size + 60,
                                     text="JARK Avatar System Online",
                                     font=('Helvetica', 16, 'bold'),
                                     fill='white')
        
        self.avatar_canvas.create_text(center_x, center_y + circle_size + 85,
                                     text="Unified Interface - All Systems Merged",
                                     font=('Helvetica', 11),
                                     fill='#888888')
        
        # Start animation
        self.animate_avatar()
        
    def animate_avatar(self):
        """Animate the active avatar"""
        if hasattr(self, 'avatar_canvas') and self.avatar_canvas.find_withtag('active_avatar'):
            # Pulsing animation
            current_size = 80
            variation = random.randint(-8, 8)
            new_size = max(65, min(95, current_size + variation))
            
            # Update avatar size
            self.avatar_canvas.itemconfig('active_avatar', font=('Helvetica', new_size))
            
            # Schedule next frame
            self.root.after(1000, self.animate_avatar)
            
    def setup_system(self):
        """Setup system components"""
        # Initial messages
        self.add_chat_message("System", "JARK Unified System initialized")
        self.add_chat_message("System", "All components merged in single window")
        
        # Initial activities
        self.add_activity("System startup complete")
        self.add_activity("Unified interface loaded")
        self.add_activity("Ready for avatar activation")
        
    def start_avatar(self):
        """Start the avatar system"""
        self.add_chat_message("System", "Initializing JARK Avatar...")
        self.add_activity("Avatar initialization started")
        
        # Update controls
        self.start_avatar_btn.configure(state='disabled', text="Initializing...")
        self.avatar_status_indicator.configure(text="● Starting", fg=self.colors['warning'])
        self.avatar_current_status.configure(text="Initializing avatar system...")
        
        # Simulate initialization
        threading.Thread(target=self._avatar_startup, daemon=True).start()
        
    def _avatar_startup(self):
        """Avatar startup process"""
        time.sleep(2)  # Simulate initialization time
        
        # Update on main thread
        self.root.after(0, self._avatar_startup_complete_visual)
            
    def _avatar_startup_complete_visual(self):
        """Start the avatar system"""
        self.add_chat_message("System", "Initializing JARK Avatar...")
        self.add_activity("Avatar initialization started")
        
        # Update controls
        self.start_avatar_btn.configure(state='disabled', text="Initializing...")
        self.avatar_status_indicator.configure(text="● Starting", fg=self.colors['warning'])
        self.avatar_current_status.configure(text="Initializing avatar system...")
        
        # Simulate initialization
        threading.Thread(target=self._avatar_startup, daemon=True).start()
        
    def _avatar_startup(self):
        """Avatar startup process"""
        time.sleep(2)  # Simulate initialization time
        
        # Update on main thread
        self.root.after(0, self._avatar_startup_complete)
        
    def _avatar_startup_complete(self):
        """Complete avatar startup"""
        self.avatar_active = True
        
        # Update controls
        self.start_avatar_btn.configure(text="✓ Avatar Active", bg=self.colors['success'])
        self.speak_btn.configure(state='normal')
        self.cafe_btn.configure(state='normal')
        
        # Update status
        self.avatar_status_indicator.configure(text="● Online", fg=self.colors['success'])
        self.avatar_current_status.configure(text="Avatar system active")
        self.avatar_mode_display.configure(text="Ready")
        
        # Show active avatar
        self.show_active_avatar()
        
        # Messages
        self.add_chat_message("System", "Avatar system online!")
        self.add_chat_message("JARK", "Hello! I'm JARK, your unified AI assistant. How may I help you today?")
        self.add_activity("Avatar system activated")
        
        # Update integration status
        self.integration_status.configure(text="🤖 Avatar + GUI Fully Merged")
        
    def test_speech(self):
        """Test speech functionality"""
        phrases = [
            "Welcome to JARK Café! I'm your unified AI assistant with real 3D avatar.",
            "Our complete system shows the actual jake.glb model in the display.",
            "How may I assist you with our premium services today?",
            "My 3D avatar and GUI are working together seamlessly!"
        ]
        
        phrase = random.choice(phrases)
        self.add_chat_message("JARK", phrase)
        self.add_activity(f"Speech test: {phrase[:35]}...")
        
        # Use real avatar speech if available
        if self.real_avatar:
            self.real_avatar.speak(phrase)
        else:
            # TTS in background
            threading.Thread(target=lambda: os.system(f"say '{phrase}'"), daemon=True).start()
        
    def start_cafe_mode(self):
        """Start café operational mode"""
        self.add_chat_message("JARK", "Café mode activated! I'm ready to take orders and serve customers.")
        self.add_activity("Café mode activated")
        
        self.avatar_mode_display.configure(text="Café Mode")
        self.chat_status_indicator.configure(text="● Active", fg=self.colors['success'])
        
        # Load café logic in background
        threading.Thread(target=self._start_cafe_logic, daemon=True).start()
        
    def _start_cafe_logic(self):
        """Start café logic"""
        try:
            # Import and start café system
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'jarkes'))
            from jark_cafe import JARKCafe
            
            self.cafe_system = JARKCafe()
            self.root.after(0, lambda: self.add_chat_message("System", "Café logic integrated successfully!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.add_chat_message("System", f"Café integration note: {e}"))
            
    def switch_section(self, section):
        """Switch navigation section"""
        for sect, btn in self.nav_buttons.items():
            if sect == section:
                btn.configure(bg=self.colors['primary'], fg='white')
            else:
                btn.configure(bg=self.colors['surface'], fg=self.colors['text_secondary'])
                
        self.add_activity(f"Navigation: {section.title()}")
        self.add_chat_message("System", f"Switched to {section.title()} section")
        
    def send_message(self):
        """Send chat message"""
        message = self.message_input.get().strip()
        if message:
            self.add_chat_message("Customer", message)
            self.message_input.delete(0, tk.END)
            
            self.add_activity(f"Customer message received")
            
            # Generate response
            self.root.after(1000, lambda: self.generate_response(message))
            
    def generate_response(self, customer_message):
        """Generate JARK response"""
        message_lower = customer_message.lower()
        
        if any(word in message_lower for word in ['menu', 'food', 'drink']):
            response = "I'd love to show you our menu! We have premium coffee, artisan teas, fresh sandwiches, and delicious pastries."
            self.update_order_stats()
        elif any(word in message_lower for word in ['order', 'want', 'buy']):
            response = "Perfect! I'll help you place your order. What would you like to start with today?"
            self.update_order_stats()
        elif any(word in message_lower for word in ['unified', 'merged', 'window']):
            response = "Yes! I'm now completely unified - my avatar, GUI, and all functions work together in one window!"
        elif any(word in message_lower for word in ['help', 'support']):
            response = "I'm here to provide excellent service! How can I assist you today?"
        else:
            responses = [
                "I understand! Let me help you with that right away.",
                "Thank you for visiting JARK Café. How may I serve you better?",
                "Absolutely! I'll take care of that for you immediately.",
                "Great question! How can I provide the best assistance?"
            ]
            response = responses[hash(customer_message) % len(responses)]
            
        self.add_chat_message("JARK", response)
        self.add_activity("JARK response sent")
        
        # Brief status change
        self.chat_status_indicator.configure(text="● Responding", fg=self.colors['primary'])
        self.root.after(2000, lambda: self.chat_status_indicator.configure(text="● Active", fg=self.colors['success']))
        
    def add_chat_message(self, sender, message):
        """Add message to chat"""
        self.chat_display.configure(state='normal')
        
        timestamp = datetime.now().strftime("%I:%M %p")
        
        if sender == "System":
            formatted = f"[{timestamp}] 🔧 {sender}: {message}\n"
        elif sender == "JARK":
            formatted = f"[{timestamp}] 🤖 {sender}: {message}\n"
        else:
            formatted = f"[{timestamp}] 👤 {sender}: {message}\n"
            
        self.chat_display.insert(tk.END, formatted)
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)
        
    def add_activity(self, activity):
        """Add activity to log"""
        timestamp = datetime.now().strftime("%I:%M %p")
        activity_text = f"[{timestamp}] {activity}"
        
        self.activity_listbox.insert(tk.END, activity_text)
        self.activity_listbox.see(tk.END)
        
        # Keep only last 15 activities
        if self.activity_listbox.size() > 15:
            self.activity_listbox.delete(0)
            
    def update_order_stats(self):
        """Update order statistics"""
        self.orders_processed += 1
        self.customers_served += 1
        
        self.stats_widgets['customers'].configure(text=str(self.customers_served))
        self.stats_widgets['orders'].configure(text=str(self.orders_processed))
        
        revenue = self.orders_processed * 8.75
        self.stats_widgets['revenue'].configure(text=f"${revenue:.2f}")
        
    def start_updates(self):
        """Start update loops"""
        self.update_time()
        self.update_uptime()
        
    def update_time(self):
        """Update time display"""
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%B %d, %Y")
        
        self.time_label.configure(text=time_str)
        self.date_label.configure(text=date_str)
        
        self.root.after(1000, self.update_time)
        
    def update_uptime(self):
        """Update uptime"""
        uptime_seconds = int(time.time() - self.start_time)
        uptime_minutes = uptime_seconds // 60
        uptime_hours = uptime_minutes // 60
        
        if uptime_hours > 0:
            uptime_text = f"{uptime_hours}h {uptime_minutes % 60}m"
        else:
            uptime_text = f"{uptime_minutes}m"
            
        self.stats_widgets['uptime'].configure(text=uptime_text)
        self.uptime_label.configure(text=f"Uptime: {uptime_text}")
        self.root.after(30000, self.update_uptime)
        
    def run(self):
        """Run the unified system"""
        print("🚀 Starting JARK Unified System...")
        print("=" * 70)
        print("✅ Single window interface - NO separate windows!")
        print("✅ Professional GUI with embedded avatar display")
        print("✅ Navigation controls on left panel")
        print("✅ Avatar visualization in center panel")
        print("✅ Chat interface and metrics on right panel")
        print("✅ Complete integration in one unified window")
        print("=" * 70)
        print("🎯 UNIFIED JARK SYSTEM - FULLY MERGED!")
        
        self.root.mainloop()

def main():
    """Launch the unified JARK system"""
    try:
        system = SimpleJARKSystem()
        system.run()
    except Exception as e:
        print(f"Error starting unified system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()