# enhanced_jark_gui.py - Professional GUI with all requested features
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
import json
import os

class JARKProfessionalGUI:
    def __init__(self, master=None):
        if master is None:
            import tkinter as tk
            self.root = tk.Tk()
            self.root.title("JARK Café - Professional AI Assistant")
            self.root.geometry("1400x900")
            self.root.configure(bg='#f8fafc')
            self.root.minsize(1200, 800)
            self.is_standalone = True
        else:
            self.root = master
            self.is_standalone = False
            
        # Initialize data
        self.customers_served = 0
        self.orders_processed = 0
        self.current_status = "Ready to serve customers"
        self.is_active = False
        self.chat_messages = []
        
        self.setup_styles()
        self.create_main_layout()
        self.load_sample_data()
        
    def setup_styles(self):
        """Configure modern styling with custom colors and fonts"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define color scheme
        self.colors = {
            'primary': '#3b82f6',      # Blue
            'primary_dark': '#1e40af',  # Dark Blue
            'secondary': '#64748b',     # Slate
            'background': '#f8fafc',    # Light Gray
            'surface': '#ffffff',       # White
            'text_primary': '#1e293b',  # Dark Slate
            'text_secondary': '#64748b', # Medium Slate
            'success': '#10b981',       # Green
            'warning': '#f59e0b',       # Amber
            'error': '#ef4444',         # Red
        }
        
        # Configure custom styles
        style.configure('Title.TLabel', 
                       font=('Helvetica', 28, 'bold'),
                       background=self.colors['text_primary'],
                       foreground='white')
        
        style.configure('Subtitle.TLabel',
                       font=('Helvetica', 12),
                       background=self.colors['text_primary'],
                       foreground=self.colors['text_secondary'])
        
        style.configure('Menu.TButton',
                       font=('Helvetica', 11),
                       padding=(20, 12),
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Active.TButton',
                       font=('Helvetica', 11, 'bold'),
                       padding=(20, 12),
                       relief='flat',
                       borderwidth=0)
        
    def create_main_layout(self):
        """Create the complete professional layout"""
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Top Bar
        self.create_top_bar(main_container)
        
        # Content Area
        content_frame = tk.Frame(main_container, bg=self.colors['background'])
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Create three-column layout
        self.create_left_panel(content_frame)      # Navigation
        self.create_center_panel(content_frame)    # Chat
        self.create_right_panel(content_frame)     # Analytics/Info
        
        # Bottom Panel
        self.create_bottom_panel(main_container)
        
    def create_top_bar(self, parent):
        """Create professional top header with gradient effect"""
        # Header frame with gradient-like effect
        header_frame = tk.Frame(parent, bg=self.colors['text_primary'], height=100)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Add subtle border
        border_frame = tk.Frame(header_frame, bg=self.colors['primary'], height=3)
        border_frame.pack(fill='x', side='bottom')
        
        # Content container
        header_content = tk.Frame(header_frame, bg=self.colors['text_primary'])
        header_content.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Left side - Title and subtitle
        title_frame = tk.Frame(header_content, bg=self.colors['text_primary'])
        title_frame.pack(side='left', fill='y')
        
        title_label = tk.Label(title_frame, 
                              text="JARK", 
                              font=('Helvetica', 32, 'bold'),
                              bg=self.colors['text_primary'], 
                              fg='white')
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(title_frame, 
                                 text="Professional AI-Powered Café Assistant", 
                                 font=('Helvetica', 12),
                                 bg=self.colors['text_primary'], 
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(anchor='w')
        
        # Right side - Status indicators
        status_frame = tk.Frame(header_content, bg=self.colors['text_primary'])
        status_frame.pack(side='right', fill='y')
        
        # System status
        self.system_status_label = tk.Label(status_frame,
                                           text="● System Online",
                                           font=('Helvetica', 11, 'bold'),
                                           bg=self.colors['text_primary'],
                                           fg=self.colors['success'])
        self.system_status_label.pack(anchor='e')
        
        # Current time
        self.time_label = tk.Label(status_frame,
                                  text="",
                                  font=('Helvetica', 10),
                                  bg=self.colors['text_primary'],
                                  fg=self.colors['text_secondary'])
        self.time_label.pack(anchor='e', pady=(5, 0))
        
        # Update time every second
        self.update_time()
        
    def create_left_panel(self, parent):
        """Create navigation menu with modern design"""
        # Left panel container
        left_frame = tk.Frame(parent, bg=self.colors['surface'], width=300)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Add shadow effect
        shadow_frame = tk.Frame(left_frame, bg='#e2e8f0', height=1)
        shadow_frame.pack(fill='x', side='bottom')
        
        # Navigation header
        nav_header = tk.Frame(left_frame, bg=self.colors['surface'])
        nav_header.pack(fill='x', padx=20, pady=(20, 10))
        
        nav_title = tk.Label(nav_header, 
                            text="Navigation", 
                            font=('Helvetica', 16, 'bold'),
                            bg=self.colors['surface'], 
                            fg=self.colors['text_primary'])
        nav_title.pack(anchor='w')
        
        # Menu items with icons
        menu_items = [
            ("🏠", "Home", "home", "Dashboard and overview"),
            ("📋", "Orders", "orders", "Manage customer orders"),
            ("👥", "Customers", "customers", "Customer database"),
            ("📊", "Analytics", "analytics", "Performance metrics"),
            ("💰", "Revenue", "revenue", "Financial reports"),
            ("⚙️", "Settings", "settings", "System configuration"),
            ("ℹ️", "About", "about", "About JARK system")
        ]
        
        self.menu_buttons = {}
        self.current_section = "home"
        
        for icon, text, section_id, description in menu_items:
            btn_frame = tk.Frame(left_frame, bg=self.colors['surface'])
            btn_frame.pack(fill='x', padx=15, pady=2)
            
            btn = tk.Button(btn_frame,
                           text=f"{icon}  {text}",
                           font=('Helvetica', 12),
                           bg=self.colors['surface'],
                           fg=self.colors['text_secondary'],
                           relief='flat',
                           anchor='w',
                           padx=20,
                           pady=12,
                           cursor='hand2',
                           command=lambda s=section_id, t=text: self.switch_section(s, t))
            
            btn.pack(fill='x')
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: self.on_menu_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_menu_hover(b, False))
            
            self.menu_buttons[section_id] = btn
            
        # Set Home as active
        self.switch_section("home", "Home")
        
        # Statistics panel
        self.create_stats_panel(left_frame)
        
    def create_center_panel(self, parent):
        """Create chat conversation interface"""
        # Center panel container
        center_frame = tk.Frame(parent, bg=self.colors['surface'])
        center_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Chat header
        chat_header = tk.Frame(center_frame, bg='#f1f5f9', height=70)
        chat_header.pack(fill='x')
        chat_header.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(chat_header, bg='#f1f5f9')
        header_content.pack(fill='both', expand=True, padx=25, pady=15)
        
        chat_title = tk.Label(header_content, 
                             text="Customer Conversation", 
                             font=('Helvetica', 18, 'bold'),
                             bg='#f1f5f9', 
                             fg=self.colors['text_primary'])
        chat_title.pack(side='left')
        
        # Status and controls
        status_controls = tk.Frame(header_content, bg='#f1f5f9')
        status_controls.pack(side='right')
        
        self.activity_status = tk.Label(status_controls, 
                                      text="● Ready", 
                                      font=('Helvetica', 11, 'bold'),
                                      bg='#f1f5f9', 
                                      fg=self.colors['warning'])
        self.activity_status.pack(side='right', padx=(0, 15))
        
        clear_btn = tk.Button(status_controls,
                             text="Clear Chat",
                             font=('Helvetica', 10),
                             bg=self.colors['secondary'],
                             fg='white',
                             relief='flat',
                             padx=15,
                             pady=5,
                             cursor='hand2',
                             command=self.clear_chat)
        clear_btn.pack(side='right', padx=(0, 10))
        
        # Chat area with scrolling
        chat_container = tk.Frame(center_frame, bg=self.colors['surface'])
        chat_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create scrollable chat area
        self.chat_canvas = tk.Canvas(chat_container, bg=self.colors['surface'], highlightthickness=0)
        chat_scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_canvas.yview)
        self.chat_content = tk.Frame(self.chat_canvas, bg=self.colors['surface'])
        
        self.chat_content.bind("<Configure>", 
                              lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        
        self.chat_canvas.create_window((0, 0), window=self.chat_content, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        chat_scrollbar.pack(side="right", fill="y")
        
        # Message input area
        self.create_message_input(center_frame)
        
    def create_right_panel(self, parent):
        """Create analytics and information panel"""
        # Right panel container
        right_frame = tk.Frame(parent, bg=self.colors['surface'], width=320)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)
        
        # Panel header
        panel_header = tk.Frame(right_frame, bg=self.colors['surface'])
        panel_header.pack(fill='x', padx=20, pady=(20, 15))
        
        panel_title = tk.Label(panel_header, 
                              text="System Information", 
                              font=('Helvetica', 16, 'bold'),
                              bg=self.colors['surface'], 
                              fg=self.colors['text_primary'])
        panel_title.pack(anchor='w')
        
        # Performance metrics
        self.create_metrics_panel(right_frame)
        
        # Recent activity
        self.create_activity_panel(right_frame)
        
        # System health
        self.create_health_panel(right_frame)
        
    def create_bottom_panel(self, parent):
        """Create avatar status and system information panel"""
        # Bottom panel with gradient
        bottom_frame = tk.Frame(parent, bg=self.colors['text_primary'], height=130)
        bottom_frame.pack(fill='x', pady=(20, 0))
        bottom_frame.pack_propagate(False)
        
        # Add accent border
        accent_border = tk.Frame(bottom_frame, bg=self.colors['primary'], height=4)
        accent_border.pack(fill='x')
        
        # Content area
        content_area = tk.Frame(bottom_frame, bg=self.colors['text_primary'])
        content_area.pack(fill='both', expand=True, padx=40, pady=20)
        
        # Avatar section
        avatar_section = tk.Frame(content_area, bg=self.colors['text_primary'])
        avatar_section.pack(side='left', fill='y')
        
        # Create circular avatar with border
        avatar_container = tk.Frame(avatar_section, bg=self.colors['text_primary'])
        avatar_container.pack(side='left', padx=(0, 25))
        
        # Avatar canvas for circular shape
        avatar_canvas = tk.Canvas(avatar_container, width=90, height=90, 
                                 bg=self.colors['text_primary'], highlightthickness=0)
        avatar_canvas.pack()
        
        # Draw circular avatar with border
        avatar_canvas.create_oval(5, 5, 85, 85, fill=self.colors['primary'], 
                                 outline='#60a5fa', width=3)
        avatar_canvas.create_text(45, 45, text="🤖", font=('Helvetica', 28), fill='white')
        
        # Avatar info
        avatar_info = tk.Frame(avatar_section, bg=self.colors['text_primary'])
        avatar_info.pack(side='left', fill='y', pady=10)
        
        avatar_name = tk.Label(avatar_info, 
                              text="JARK Assistant", 
                              font=('Helvetica', 16, 'bold'),
                              bg=self.colors['text_primary'], 
                              fg='white')
        avatar_name.pack(anchor='w')
        
        self.avatar_status_label = tk.Label(avatar_info, 
                                          text=self.current_status, 
                                          font=('Helvetica', 11),
                                          bg=self.colors['text_primary'], 
                                          fg=self.colors['text_secondary'])
        self.avatar_status_label.pack(anchor='w', pady=(3, 0))
        
        # System metrics
        metrics_section = tk.Frame(content_area, bg=self.colors['text_primary'])
        metrics_section.pack(side='right', fill='y', pady=10)
        
        # Create metrics grid
        metrics_grid = tk.Frame(metrics_section, bg=self.colors['text_primary'])
        metrics_grid.pack(anchor='e')
        
        metrics_data = [
            ("Uptime", "2h 45m"),
            ("Response Time", "0.2s"),
            ("Memory Usage", "45%"),
            ("CPU Usage", "12%")
        ]
        
        for i, (label, value) in enumerate(metrics_data):
            row = i // 2
            col = i % 2
            
            metric_frame = tk.Frame(metrics_grid, bg=self.colors['text_primary'])
            metric_frame.grid(row=row, column=col, padx=15, pady=3, sticky='e')
            
            metric_label = tk.Label(metric_frame, 
                                   text=f"{label}:", 
                                   font=('Helvetica', 9),
                                   bg=self.colors['text_primary'], 
                                   fg=self.colors['text_secondary'])
            metric_label.pack(anchor='e')
            
            metric_value = tk.Label(metric_frame, 
                                   text=value, 
                                   font=('Helvetica', 10, 'bold'),
                                   bg=self.colors['text_primary'], 
                                   fg='white')
            metric_value.pack(anchor='e')
            
    def create_stats_panel(self, parent):
        """Create statistics panel in left navigation"""
        stats_frame = tk.Frame(parent, bg='#f8fafc')
        stats_frame.pack(fill='x', padx=15, pady=20, side='bottom')
        
        stats_title = tk.Label(stats_frame, 
                              text="Today's Performance", 
                              font=('Helvetica', 12, 'bold'),
                              bg='#f8fafc', 
                              fg=self.colors['text_primary'])
        stats_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Stats data
        stats_data = [
            ("Customers Served", self.customers_served, self.colors['success']),
            ("Orders Processed", self.orders_processed, self.colors['primary']),
            ("Revenue Generated", "$0.00", self.colors['warning'])
        ]
        
        for label, value, color in stats_data:
            stat_item = tk.Frame(stats_frame, bg='#f8fafc')
            stat_item.pack(fill='x', padx=15, pady=2)
            
            stat_label = tk.Label(stat_item, 
                                 text=label, 
                                 font=('Helvetica', 10),
                                 bg='#f8fafc', 
                                 fg=self.colors['text_secondary'])
            stat_label.pack(side='left')
            
            stat_value = tk.Label(stat_item, 
                                 text=str(value), 
                                 font=('Helvetica', 10, 'bold'),
                                 bg='#f8fafc', 
                                 fg=color)
            stat_value.pack(side='right')
            
    def create_metrics_panel(self, parent):
        """Create performance metrics panel"""
        metrics_frame = tk.Frame(parent, bg='#f8fafc')
        metrics_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        metrics_title = tk.Label(metrics_frame, 
                                text="Performance Metrics", 
                                font=('Helvetica', 12, 'bold'),
                                bg='#f8fafc', 
                                fg=self.colors['text_primary'])
        metrics_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Metrics with progress bars
        metrics = [
            ("System Load", 45, self.colors['success']),
            ("Memory Usage", 32, self.colors['primary']),
            ("Network Activity", 78, self.colors['warning'])
        ]
        
        for label, percentage, color in metrics:
            metric_container = tk.Frame(metrics_frame, bg='#f8fafc')
            metric_container.pack(fill='x', padx=15, pady=5)
            
            metric_header = tk.Frame(metric_container, bg='#f8fafc')
            metric_header.pack(fill='x')
            
            tk.Label(metric_header, text=label, font=('Helvetica', 9),
                    bg='#f8fafc', fg=self.colors['text_secondary']).pack(side='left')
            tk.Label(metric_header, text=f"{percentage}%", font=('Helvetica', 9, 'bold'),
                    bg='#f8fafc', fg=color).pack(side='right')
            
            # Progress bar
            progress_bg = tk.Frame(metric_container, bg='#e2e8f0', height=6)
            progress_bg.pack(fill='x', pady=(3, 0))
            
            progress_fill = tk.Frame(progress_bg, bg=color, height=6)
            progress_fill.place(x=0, y=0, relwidth=percentage/100)
            
    def create_activity_panel(self, parent):
        """Create recent activity panel"""
        activity_frame = tk.Frame(parent, bg='#f8fafc')
        activity_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        activity_title = tk.Label(activity_frame, 
                                 text="Recent Activity", 
                                 font=('Helvetica', 12, 'bold'),
                                 bg='#f8fafc', 
                                 fg=self.colors['text_primary'])
        activity_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Activity items
        activities = [
            ("Customer served", "2 min ago", "🟢"),
            ("Order completed", "5 min ago", "🔵"),
            ("System startup", "45 min ago", "🟡")
        ]
        
        for activity, time_ago, indicator in activities:
            activity_item = tk.Frame(activity_frame, bg='#f8fafc')
            activity_item.pack(fill='x', padx=15, pady=3)
            
            tk.Label(activity_item, text=indicator, font=('Helvetica', 8),
                    bg='#f8fafc').pack(side='left', padx=(0, 8))
            
            tk.Label(activity_item, text=activity, font=('Helvetica', 9),
                    bg='#f8fafc', fg=self.colors['text_primary']).pack(side='left')
            
            tk.Label(activity_item, text=time_ago, font=('Helvetica', 8),
                    bg='#f8fafc', fg=self.colors['text_secondary']).pack(side='right')
            
    def create_health_panel(self, parent):
        """Create system health panel"""
        health_frame = tk.Frame(parent, bg='#f8fafc')
        health_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        health_title = tk.Label(health_frame, 
                               text="System Health", 
                               font=('Helvetica', 12, 'bold'),
                               bg='#f8fafc', 
                               fg=self.colors['text_primary'])
        health_title.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Health indicators
        health_items = [
            ("Database", "Online", self.colors['success']),
            ("AI Engine", "Active", self.colors['success']),
            ("Voice System", "Ready", self.colors['warning']),
            ("Camera", "Standby", self.colors['secondary'])
        ]
        
        for component, status, color in health_items:
            health_item = tk.Frame(health_frame, bg='#f8fafc')
            health_item.pack(fill='x', padx=15, pady=2)
            
            tk.Label(health_item, text=component, font=('Helvetica', 9),
                    bg='#f8fafc', fg=self.colors['text_secondary']).pack(side='left')
            
            tk.Label(health_item, text=status, font=('Helvetica', 9, 'bold'),
                    bg='#f8fafc', fg=color).pack(side='right')
            
    def create_message_input(self, parent):
        """Create message input area with enhanced design"""
        input_container = tk.Frame(parent, bg=self.colors['surface'], height=80)
        input_container.pack(fill='x', padx=20, pady=(0, 20))
        input_container.pack_propagate(False)
        
        # Input frame with border
        input_frame = tk.Frame(input_container, bg='#f1f5f9')
        input_frame.pack(fill='both', expand=True, padx=5, pady=15)
        
        # Message entry
        self.message_entry = tk.Entry(input_frame, 
                                     font=('Helvetica', 12),
                                     bg='white',
                                     fg=self.colors['text_primary'],
                                     relief='flat',
                                     bd=1,
                                     insertbackground=self.colors['primary'])
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(15, 10), pady=15)
        
        # Send button with hover effect
        self.send_btn = tk.Button(input_frame,
                                 text="Send Message",
                                 font=('Helvetica', 11, 'bold'),
                                 bg=self.colors['primary'],
                                 fg='white',
                                 relief='flat',
                                 padx=25,
                                 pady=8,
                                 cursor='hand2',
                                 command=self.send_message)
        self.send_btn.pack(side='right', padx=(0, 15), pady=15)
        
        # Bind Enter key
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        self.message_entry.bind("<FocusIn>", self.on_entry_focus)
        self.message_entry.bind("<FocusOut>", self.on_entry_blur)
        
        # Send button hover effects
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.configure(bg=self.colors['primary_dark']))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.configure(bg=self.colors['primary']))
        
    def load_sample_data(self):
        """Load sample chat messages and data"""
        sample_messages = [
            ("JARK", "Welcome to JARK Café! I'm your professional AI assistant. How may I help you today?", "10:30 AM"),
            ("Customer", "Hi! I'd like to see your menu please.", "10:31 AM"),
            ("JARK", "Of course! We have a variety of premium coffee, artisan tea, gourmet sandwiches, and fresh pastries. What type of beverage are you in the mood for?", "10:31 AM"),
            ("Customer", "I'd love a cappuccino and maybe a croissant.", "10:32 AM"),
            ("JARK", "Excellent choice! One cappuccino and a fresh croissant. That will be $7.50. Your order will be ready in approximately 5 minutes.", "10:32 AM")
        ]
        
        for sender, message, timestamp in sample_messages:
            self.add_chat_message(sender, message, timestamp, animate=False)
            
    # Event handlers and utility methods
    def on_menu_hover(self, button, entering):
        """Handle menu button hover effects"""
        if entering:
            if button['bg'] != self.colors['primary']:
                button.configure(bg='#f1f5f9')
        else:
            if button['bg'] != self.colors['primary']:
                button.configure(bg=self.colors['surface'])
                
    def on_entry_focus(self, event):
        """Handle message entry focus"""
        self.message_entry.configure(relief='solid', bd=2, highlightcolor=self.colors['primary'])
        
    def on_entry_blur(self, event):
        """Handle message entry blur"""
        self.message_entry.configure(relief='flat', bd=1)
        
    def switch_section(self, section_id, section_name):
        """Switch between different sections"""
        # Update menu buttons
        for sid, btn in self.menu_buttons.items():
            if sid == section_id:
                btn.configure(bg=self.colors['primary'], fg='white')
            else:
                btn.configure(bg=self.colors['surface'], fg=self.colors['text_secondary'])
                
        self.current_section = section_id
        self.update_avatar_status(f"{section_name} section active")
        
        # Add section-specific functionality here
        if section_id == "analytics":
            self.show_analytics_notification()
        elif section_id == "orders":
            self.show_orders_notification()
            
    def show_analytics_notification(self):
        """Show analytics notification"""
        self.add_system_message("Analytics dashboard loaded. Viewing performance metrics.")
        
    def show_orders_notification(self):
        """Show orders notification"""
        self.add_system_message("Orders management system accessed. Ready to process new orders.")
        
    def add_chat_message(self, sender, message, timestamp, animate=True):
        """Add a message to the chat with enhanced styling"""
        message_frame = tk.Frame(self.chat_content, bg=self.colors['surface'])
        message_frame.pack(fill='x', padx=15, pady=8)
        
        is_jark = sender == "JARK"
        is_system = sender == "System"
        
        # Choose colors based on sender
        if is_jark:
            bubble_color = self.colors['primary']
            text_color = 'white'
            align = 'w'
            padx_config = (0, 100)
        elif is_system:
            bubble_color = self.colors['warning']
            text_color = 'white' 
            align = 'center'
            padx_config = (100, 100)
        else:
            bubble_color = '#e5e7eb'
            text_color = self.colors['text_primary']
            align = 'e'
            padx_config = (100, 0)
        
        # Message bubble with rounded corners effect
        bubble_frame = tk.Frame(message_frame, bg=bubble_color)
        bubble_frame.pack(anchor=align, fill='x', padx=padx_config)
        
        # Add padding frame for rounded effect
        padding_frame = tk.Frame(bubble_frame, bg=bubble_color)
        padding_frame.pack(fill='both', padx=15, pady=12)
        
        # Sender name (smaller, semi-transparent)
        if not is_system:
            sender_label = tk.Label(padding_frame, 
                                   text=sender, 
                                   font=('Helvetica', 9, 'bold'),
                                   bg=bubble_color,
                                   fg=text_color if is_jark else '#6b7280')
            sender_label.pack(anchor='w', pady=(0, 3))
        
        # Message text with word wrapping
        message_label = tk.Label(padding_frame, 
                                text=message, 
                                font=('Helvetica', 11),
                                bg=bubble_color,
                                fg=text_color,
                                wraplength=400,
                                justify='left')
        message_label.pack(anchor='w', pady=(0, 3))
        
        # Timestamp
        time_label = tk.Label(padding_frame, 
                             text=timestamp, 
                             font=('Helvetica', 8),
                             bg=bubble_color,
                             fg=text_color if is_jark else '#9ca3af')
        time_label.pack(anchor='e')
        
        # Auto-scroll to bottom
        self.root.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
        
        # Store message
        self.chat_messages.append({
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        })
        
    def add_system_message(self, message):
        """Add a system message"""
        current_time = datetime.now().strftime("%I:%M %p")
        self.add_chat_message("System", message, current_time)
        
    def send_message(self):
        """Send a message from the input field"""
        message = self.message_entry.get().strip()
        if message:
            current_time = datetime.now().strftime("%I:%M %p")
            self.add_chat_message("Customer", message, current_time)
            self.message_entry.delete(0, tk.END)
            
            # Simulate JARK response after a delay
            self.root.after(1200, lambda: self.simulate_jark_response(message))
            
    def simulate_jark_response(self, customer_message):
        """Simulate an intelligent response from JARK"""
        # Enhanced responses based on keywords
        message_lower = customer_message.lower()
        
        if any(word in message_lower for word in ['menu', 'food', 'drink', 'eat']):
            response = "I'd be happy to help you with our menu! We offer premium coffee, artisan teas, gourmet sandwiches, and fresh pastries. Would you like me to recommend something specific?"
        elif any(word in message_lower for word in ['order', 'want', 'buy', 'get']):
            response = "Perfect! I'll help you place your order. What would you like to start with today?"
        elif any(word in message_lower for word in ['price', 'cost', 'how much']):
            response = "Our prices are very competitive. Coffee ranges from $3-6, sandwiches $8-12, and pastries $2-4. Would you like specific pricing for any items?"
        elif any(word in message_lower for word in ['help', 'support', 'assistance']):
            response = "I'm here to provide you with the best service possible! How can I assist you today?"
        elif any(word in message_lower for word in ['thanks', 'thank you']):
            response = "You're very welcome! It's my pleasure to serve you. Is there anything else I can help you with?"
        else:
            responses = [
                "I understand. Let me help you with that right away.",
                "That's a great question! How can I provide you with the best assistance?",
                "I'm here to make your experience exceptional. What would you like to know?",
                "Absolutely! I'll take care of that for you immediately.",
                "Thank you for choosing JARK Café. How may I serve you better?"
            ]
            response = responses[hash(customer_message) % len(responses)]
        
        current_time = datetime.now().strftime("%I:%M %p")
        self.add_chat_message("JARK", response, current_time)
        
        # Update activity status
        self.update_activity_status(True)
        
    def clear_chat(self):
        """Clear all chat messages"""
        for widget in self.chat_content.winfo_children():
            widget.destroy()
        self.chat_messages = []
        self.add_system_message("Chat cleared. Ready for new conversation.")
        
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%I:%M %p | %B %d, %Y")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
        
    def update_avatar_status(self, status_text):
        """Update the avatar status"""
        self.current_status = status_text
        if hasattr(self, 'avatar_status_label') and self.avatar_status_label:
            self.avatar_status_label.configure(text=status_text)
        
    def update_stats(self, customers=None, orders=None):
        """Update performance statistics"""
        if customers is not None:
            self.customers_served = customers
        if orders is not None:
            self.orders_processed = orders
            
        # Refresh stats display
        # This would update the stats panel if needed
        
    def update_activity_status(self, is_active=True):
        """Update the activity status indicator"""
        self.is_active = is_active
        if hasattr(self, 'activity_status') and self.activity_status:
            if is_active:
                self.activity_status.configure(text="● Active", fg=self.colors['success'])
            else:
                self.activity_status.configure(text="● Ready", fg=self.colors['warning'])
            
    def run(self):
        """Start the GUI main loop"""
        if hasattr(self, 'root') and self.root:
            # Show welcome message
            self.add_system_message("JARK Professional System initialized. Ready to serve customers!")
            if hasattr(self, 'is_standalone') and self.is_standalone:
                self.root.mainloop()
            else:
                return self.root

# Integration functions
def create_professional_gui():
    """Create and return a professional GUI instance"""
    return JARKProfessionalGUI()

def run_gui_in_thread(gui_instance):
    """Run the GUI in a separate thread"""
    gui_instance.run()

if __name__ == "__main__":
    # Test the professional GUI
    gui = JARKProfessionalGUI()
    gui.run()