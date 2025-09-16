# unified_jark_system.py - Single integrated JARK system with 3D avatar + Professional GUI
import os
import sys
import time
import json
import threading
import subprocess
import numpy as np
from queue import SimpleQueue
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Frame
from datetime import datetime
import random

# Panda3D imports for 3D avatar
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, Vec3, Filename, WindowProperties
from panda3d.core import GeomNode

class UnifiedJARKSystem:
    def __init__(self):
        self.setup_window()
        self.setup_styles()
        self.initialize_data()
        self.create_layout()
        self.setup_avatar_integration()
        
    def setup_window(self):
        """Create the main unified window"""
        self.root = tk.Tk()
        self.root.title("JARK Café - Unified AI Assistant & 3D Avatar")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f8fafc')
        self.root.minsize(1400, 900)
        
    def setup_styles(self):
        """Configure modern styling"""
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
        }
        
    def initialize_data(self):
        """Initialize system data"""
        self.customers_served = 0
        self.orders_processed = 0
        self.current_status = "Ready to serve customers"
        self.is_active = False
        self.chat_messages = []
        self.avatar_process = None
        
    def create_layout(self):
        """Create the unified layout with avatar viewport and GUI"""
        # Main container
        main_container = Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top header
        self.create_header(main_container)
        
        # Content area - split into avatar and GUI sections
        content_frame = Frame(main_container, bg=self.colors['background'])
        content_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Left side: 3D Avatar viewport (larger)
        self.create_avatar_section(content_frame)
        
        # Right side: Professional GUI controls
        self.create_gui_section(content_frame)
        
        # Bottom status bar
        self.create_status_bar(main_container)
        
    def create_header(self, parent):
        """Create unified header"""
        header_frame = Frame(parent, bg=self.colors['text_primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = Frame(header_frame, bg=self.colors['text_primary'])
        header_content.pack(fill='both', expand=True, padx=30, pady=15)
        
        # Title
        title_label = tk.Label(header_content, 
                              text="JARK", 
                              font=('Helvetica', 28, 'bold'),
                              bg=self.colors['text_primary'], 
                              fg='white')
        title_label.pack(side='left')
        
        subtitle_label = tk.Label(header_content, 
                                 text="Unified AI Assistant & 3D Avatar System", 
                                 font=('Helvetica', 12),
                                 bg=self.colors['text_primary'], 
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(side='left', padx=(15, 0))
        
        # Status indicators
        status_frame = Frame(header_content, bg=self.colors['text_primary'])
        status_frame.pack(side='right')
        
        self.system_status_label = tk.Label(status_frame,
                                           text="● System Online",
                                           font=('Helvetica', 11, 'bold'),
                                           bg=self.colors['text_primary'],
                                           fg=self.colors['success'])
        self.system_status_label.pack(anchor='e')
        
        self.time_label = tk.Label(status_frame,
                                  text="",
                                  font=('Helvetica', 10),
                                  bg=self.colors['text_primary'],
                                  fg=self.colors['text_secondary'])
        self.time_label.pack(anchor='e', pady=(5, 0))
        
        self.update_time()
        
    def create_avatar_section(self, parent):
        """Create 3D avatar viewport section"""
        # Avatar container (left side - 60% width)
        avatar_container = Frame(parent, bg='#2a2a2a', relief='sunken', bd=2)
        avatar_container.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Avatar header
        avatar_header = Frame(avatar_container, bg='#1a1a1a', height=40)
        avatar_header.pack(fill='x')
        avatar_header.pack_propagate(False)
        
        avatar_title = tk.Label(avatar_header,
                               text="🤖 3D Avatar - JARK Assistant",
                               font=('Helvetica', 12, 'bold'),
                               bg='#1a1a1a',
                               fg='white')
        avatar_title.pack(side='left', padx=15, pady=10)
        
        # Avatar controls
        avatar_controls = Frame(avatar_header, bg='#1a1a1a')
        avatar_controls.pack(side='right', padx=15, pady=5)
        
        self.avatar_start_btn = tk.Button(avatar_controls,
                                        text="Start Avatar",
                                        font=('Helvetica', 9, 'bold'),
                                        bg=self.colors['success'],
                                        fg='white',
                                        relief='flat',
                                        padx=15,
                                        pady=5,
                                        command=self.start_avatar)
        self.avatar_start_btn.pack(side='left', padx=(0, 5))
        
        self.avatar_stop_btn = tk.Button(avatar_controls,
                                       text="Stop Avatar",
                                       font=('Helvetica', 9, 'bold'),
                                       bg=self.colors['error'],
                                       fg='white',
                                       relief='flat',
                                       padx=15,
                                       pady=5,
                                       command=self.stop_avatar,
                                       state='disabled')
        self.avatar_stop_btn.pack(side='left')
        
        # Avatar viewport (this will contain the 3D avatar window)
        self.avatar_viewport = Frame(avatar_container, bg='#2a2a2a')
        self.avatar_viewport.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Avatar status display
        avatar_status_frame = Frame(self.avatar_viewport, bg='#2a2a2a')
        avatar_status_frame.pack(expand=True)
        
        self.avatar_display_label = tk.Label(avatar_status_frame,
                                           text="🤖 Avatar Ready\nClick 'Start Avatar' to begin",
                                           font=('Helvetica', 16),
                                           bg='#2a2a2a',
                                           fg='white',
                                           justify='center')
        self.avatar_display_label.pack(expand=True)
        
    def create_gui_section(self, parent):
        """Create professional GUI controls section"""
        # GUI container (right side - 40% width)
        gui_container = Frame(parent, bg=self.colors['surface'], width=600)
        gui_container.pack(side='right', fill='both', padx=(5, 0))
        gui_container.pack_propagate(False)
        
        # Navigation menu
        self.create_navigation(gui_container)
        
        # Chat interface
        self.create_chat_interface(gui_container)
        
        # Performance metrics
        self.create_metrics_panel(gui_container)
        
    def create_navigation(self, parent):
        """Create navigation menu"""
        nav_frame = Frame(parent, bg='#f1f5f9', height=200)
        nav_frame.pack(fill='x', padx=10, pady=(10, 5))
        nav_frame.pack_propagate(False)
        
        nav_title = tk.Label(nav_frame,
                            text="Navigation",
                            font=('Helvetica', 14, 'bold'),
                            bg='#f1f5f9',
                            fg=self.colors['text_primary'])
        nav_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Menu buttons
        menu_items = [
            ("🏠 Home", "home"),
            ("📋 Orders", "orders"),
            ("👥 Customers", "customers"),
            ("📊 Analytics", "analytics"),
            ("⚙️ Settings", "settings")
        ]
        
        button_frame = Frame(nav_frame, bg='#f1f5f9')
        button_frame.pack(fill='x', padx=15)
        
        self.nav_buttons = {}
        for i, (text, section) in enumerate(menu_items):
            btn = tk.Button(button_frame,
                           text=text,
                           font=('Helvetica', 10),
                           bg='white' if i == 0 else '#f1f5f9',
                           fg=self.colors['primary'] if i == 0 else self.colors['text_secondary'],
                           relief='flat',
                           anchor='w',
                           padx=10,
                           pady=8,
                           command=lambda s=section: self.switch_section(s))
            btn.pack(fill='x', pady=2)
            self.nav_buttons[section] = btn
            
    def create_chat_interface(self, parent):
        """Create chat interface"""
        chat_frame = Frame(parent, bg=self.colors['surface'])
        chat_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Chat header
        chat_header = Frame(chat_frame, bg='#f1f5f9', height=50)
        chat_header.pack(fill='x')
        chat_header.pack_propagate(False)
        
        chat_title = tk.Label(chat_header,
                             text="💬 Customer Conversation",
                             font=('Helvetica', 14, 'bold'),
                             bg='#f1f5f9',
                             fg=self.colors['text_primary'])
        chat_title.pack(side='left', padx=15, pady=15)
        
        # Activity indicator
        self.activity_indicator = tk.Label(chat_header,
                                         text="● Ready",
                                         font=('Helvetica', 10, 'bold'),
                                         bg='#f1f5f9',
                                         fg=self.colors['warning'])
        self.activity_indicator.pack(side='right', padx=15, pady=15)
        
        # Chat area
        self.chat_text = scrolledtext.ScrolledText(chat_frame,
                                                  font=('Helvetica', 10),
                                                  bg='white',
                                                  fg=self.colors['text_primary'],
                                                  relief='flat',
                                                  bd=1,
                                                  state='disabled',
                                                  wrap='word')
        self.chat_text.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        
        # Message input
        input_frame = Frame(chat_frame, bg=self.colors['surface'])
        input_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        self.message_entry = tk.Entry(input_frame,
                                     font=('Helvetica', 11),
                                     bg='white',
                                     fg=self.colors['text_primary'],
                                     relief='flat',
                                     bd=1)
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        send_btn = tk.Button(input_frame,
                            text="Send",
                            font=('Helvetica', 10, 'bold'),
                            bg=self.colors['primary'],
                            fg='white',
                            relief='flat',
                            padx=20,
                            command=self.send_message)
        send_btn.pack(side='right')
        
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
    def create_metrics_panel(self, parent):
        """Create performance metrics panel"""
        metrics_frame = Frame(parent, bg='#f1f5f9', height=150)
        metrics_frame.pack(fill='x', padx=10, pady=(5, 10))
        metrics_frame.pack_propagate(False)
        
        metrics_title = tk.Label(metrics_frame,
                                text="📊 System Performance",
                                font=('Helvetica', 14, 'bold'),
                                bg='#f1f5f9',
                                fg=self.colors['text_primary'])
        metrics_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Metrics grid
        metrics_grid = Frame(metrics_frame, bg='#f1f5f9')
        metrics_grid.pack(fill='x', padx=15)
        
        # Performance data
        metrics_data = [
            ("Customers Served", "0", self.colors['success']),
            ("Orders Processed", "0", self.colors['primary']),
            ("Avatar Status", "Offline", self.colors['error']),
            ("System Load", "Low", self.colors['success'])
        ]
        
        self.metric_labels = {}
        for i, (label, value, color) in enumerate(metrics_data):
            row = i // 2
            col = i % 2
            
            metric_container = Frame(metrics_grid, bg='#f1f5f9')
            metric_container.grid(row=row, column=col, padx=10, pady=5, sticky='w')
            
            label_widget = tk.Label(metric_container,
                                   text=f"{label}:",
                                   font=('Helvetica', 9),
                                   bg='#f1f5f9',
                                   fg=self.colors['text_secondary'])
            label_widget.pack(anchor='w')
            
            value_widget = tk.Label(metric_container,
                                   text=value,
                                   font=('Helvetica', 10, 'bold'),
                                   bg='#f1f5f9',
                                   fg=color)
            value_widget.pack(anchor='w')
            
            self.metric_labels[label.lower().replace(' ', '_')] = value_widget
            
    def create_status_bar(self, parent):
        """Create bottom status bar"""
        status_frame = Frame(parent, bg=self.colors['text_primary'], height=60)
        status_frame.pack(fill='x', pady=(10, 0))
        status_frame.pack_propagate(False)
        
        status_content = Frame(status_frame, bg=self.colors['text_primary'])
        status_content.pack(fill='both', expand=True, padx=30, pady=15)
        
        # JARK status
        jark_info = Frame(status_content, bg=self.colors['text_primary'])
        jark_info.pack(side='left')
        
        jark_name = tk.Label(jark_info,
                            text="JARK Assistant",
                            font=('Helvetica', 14, 'bold'),
                            bg=self.colors['text_primary'],
                            fg='white')
        jark_name.pack(anchor='w')
        
        self.jark_status = tk.Label(jark_info,
                                   text=self.current_status,
                                   font=('Helvetica', 10),
                                   bg=self.colors['text_primary'],
                                   fg=self.colors['text_secondary'])
        self.jark_status.pack(anchor='w')
        
        # System metrics
        metrics_info = Frame(status_content, bg=self.colors['text_primary'])
        metrics_info.pack(side='right')
        
        self.uptime_label = tk.Label(metrics_info,
                                    text="Uptime: 0m",
                                    font=('Helvetica', 9),
                                    bg=self.colors['text_primary'],
                                    fg=self.colors['text_secondary'])
        self.uptime_label.pack(anchor='e')
        
        self.memory_label = tk.Label(metrics_info,
                                    text="Memory: Normal",
                                    font=('Helvetica', 9),
                                    bg=self.colors['text_primary'],
                                    fg=self.colors['text_secondary'])
        self.memory_label.pack(anchor='e')
        
    def setup_avatar_integration(self):
        """Setup integration with 3D avatar system"""
        self.start_time = time.time()
        self.update_uptime()
        self.load_sample_messages()
        
    def start_avatar(self):
        """Start the 3D avatar system"""
        try:
            self.add_chat_message("System", "Starting 3D Avatar system...", "system")
            
            # Update UI
            self.avatar_start_btn.configure(state='disabled')
            self.avatar_stop_btn.configure(state='normal')
            self.avatar_display_label.configure(text="🤖 Avatar Starting...\nInitializing 3D engine...")
            
            # Start avatar process
            char_dir = os.path.dirname(__file__)
            main_py = os.path.join(char_dir, 'main.py')
            venv_python = "/Users/msk/Desktop/jarks/.venv/bin/python"
            
            self.avatar_process = subprocess.Popen(
                [venv_python, main_py],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Update status
            self.update_metric('avatar_status', 'Online', self.colors['success'])
            self.update_status("3D Avatar system active")
            self.activity_indicator.configure(text="● Active", fg=self.colors['success'])
            self.avatar_display_label.configure(text="🤖 Avatar Active\n3D system running in separate window")
            
            self.add_chat_message("System", "3D Avatar system started successfully!", "system")
            self.add_chat_message("JARK", "Hello! I'm JARK, your AI assistant. How may I help you today?", "jark")
            
        except Exception as e:
            self.add_chat_message("System", f"Error starting avatar: {e}", "error")
            self.avatar_start_btn.configure(state='normal')
            self.avatar_stop_btn.configure(state='disabled')
            
    def stop_avatar(self):
        """Stop the 3D avatar system"""
        try:
            if self.avatar_process:
                self.avatar_process.terminate()
                self.avatar_process = None
                
            # Update UI
            self.avatar_start_btn.configure(state='normal')
            self.avatar_stop_btn.configure(state='disabled')
            self.avatar_display_label.configure(text="🤖 Avatar Stopped\nClick 'Start Avatar' to begin")
            
            # Update status
            self.update_metric('avatar_status', 'Offline', self.colors['error'])
            self.update_status("Ready to serve customers")
            self.activity_indicator.configure(text="● Ready", fg=self.colors['warning'])
            
            self.add_chat_message("System", "3D Avatar system stopped", "system")
            
        except Exception as e:
            self.add_chat_message("System", f"Error stopping avatar: {e}", "error")
            
    def switch_section(self, section):
        """Switch navigation sections"""
        # Update button states
        for sect, btn in self.nav_buttons.items():
            if sect == section:
                btn.configure(bg='white', fg=self.colors['primary'])
            else:
                btn.configure(bg='#f1f5f9', fg=self.colors['text_secondary'])
                
        self.add_chat_message("System", f"Switched to {section.title()} section", "system")
        
    def send_message(self):
        """Send a message in chat"""
        message = self.message_entry.get().strip()
        if message:
            current_time = datetime.now().strftime("%I:%M %p")
            self.add_chat_message("Customer", message, "customer")
            self.message_entry.delete(0, tk.END)
            
            # Simulate JARK response
            self.root.after(1500, lambda: self.simulate_jark_response(message))
            
    def simulate_jark_response(self, customer_message):
        """Generate JARK response"""
        message_lower = customer_message.lower()
        
        if any(word in message_lower for word in ['menu', 'food', 'drink']):
            response = "I'd be happy to show you our menu! We have premium coffee, artisan teas, gourmet sandwiches, and fresh pastries."
        elif any(word in message_lower for word in ['order', 'want', 'buy']):
            response = "Perfect! I'll help you place your order. What would you like to start with today?"
            self.update_orders()
        elif any(word in message_lower for word in ['help', 'support']):
            response = "I'm here to provide excellent service! How can I assist you today?"
        else:
            responses = [
                "I understand. Let me help you with that right away.",
                "That's a great question! How can I provide the best assistance?",
                "Absolutely! I'll take care of that for you."
            ]
            response = responses[hash(customer_message) % len(responses)]
            
        self.add_chat_message("JARK", response, "jark")
        
    def add_chat_message(self, sender, message, msg_type):
        """Add message to chat"""
        self.chat_text.configure(state='normal')
        
        current_time = datetime.now().strftime("%I:%M %p")
        
        # Format message based on sender
        if msg_type == "system":
            formatted_msg = f"[{current_time}] 🔧 {sender}: {message}\n"
            color = '#666666'
        elif msg_type == "jark":
            formatted_msg = f"[{current_time}] 🤖 {sender}: {message}\n"
            color = '#3b82f6'
        elif msg_type == "error":
            formatted_msg = f"[{current_time}] ❌ {sender}: {message}\n"
            color = '#ef4444'
        else:
            formatted_msg = f"[{current_time}] 👤 {sender}: {message}\n"
            color = '#64748b'
            
        self.chat_text.insert(tk.END, formatted_msg)
        self.chat_text.configure(state='disabled')
        self.chat_text.see(tk.END)
        
    def update_metric(self, metric_name, value, color):
        """Update a performance metric"""
        if metric_name in self.metric_labels:
            self.metric_labels[metric_name].configure(text=value, fg=color)
            
    def update_status(self, status):
        """Update JARK status"""
        self.current_status = status
        self.jark_status.configure(text=status)
        
    def update_orders(self):
        """Update order count"""
        self.orders_processed += 1
        self.customers_served += 1
        self.update_metric('customers_served', str(self.customers_served), self.colors['success'])
        self.update_metric('orders_processed', str(self.orders_processed), self.colors['primary'])
        
    def update_time(self):
        """Update time display"""
        current_time = datetime.now().strftime("%I:%M %p | %B %d, %Y")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
        
    def update_uptime(self):
        """Update uptime display"""
        uptime_seconds = int(time.time() - self.start_time)
        uptime_minutes = uptime_seconds // 60
        uptime_hours = uptime_minutes // 60
        
        if uptime_hours > 0:
            uptime_text = f"Uptime: {uptime_hours}h {uptime_minutes % 60}m"
        else:
            uptime_text = f"Uptime: {uptime_minutes}m"
            
        self.uptime_label.configure(text=uptime_text)
        self.root.after(60000, self.update_uptime)  # Update every minute
        
    def load_sample_messages(self):
        """Load sample conversation"""
        sample_messages = [
            ("System", "JARK Unified System initialized", "system"),
            ("System", "Ready to serve customers", "system")
        ]
        
        for sender, message, msg_type in sample_messages:
            self.add_chat_message(sender, message, msg_type)
            
    def run(self):
        """Start the unified system"""
        print("🚀 Starting JARK Unified System...")
        print("✅ 3D Avatar integration ready")
        print("✅ Professional GUI loaded")
        print("✅ Chat interface active")
        print("✅ Performance monitoring enabled")
        print("🎯 Unified system ready!")
        
        self.root.mainloop()
        
        # Cleanup on exit
        if self.avatar_process:
            self.avatar_process.terminate()

def main():
    """Launch the unified JARK system"""
    try:
        system = UnifiedJARKSystem()
        system.run()
    except Exception as e:
        print(f"Error starting unified system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()