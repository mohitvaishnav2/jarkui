# jark_gui.py - Modern GUI for JARK Café System
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime

class JARKGUIOverlay:
    def __init__(self, master=None):
        if master is None:
            self.root = tk.Tk()
            self.root.title("JARK Café - AI Assistant")
            self.root.geometry("1200x800")
            self.root.configure(bg='#f8fafc')
        else:
            self.root = master
            
        self.setup_styles()
        self.create_layout()
        self.setup_sample_data()
        
    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', 
                       font=('SF Pro Display', 24, 'bold'),
                       background='#1e293b',
                       foreground='white')
        
        style.configure('Menu.TButton',
                       font=('SF Pro Text', 12),
                       padding=(20, 15),
                       relief='flat')
        
        style.configure('Chat.TFrame',
                       background='#ffffff',
                       relief='flat',
                       borderwidth=1)
        
    def create_layout(self):
        """Create the main GUI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#f8fafc')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Top Bar
        self.create_top_bar(main_frame)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg='#f8fafc')
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Left Panel (Menu)
        self.create_left_panel(content_frame)
        
        # Right Panel (Conversation)
        self.create_right_panel(content_frame)
        
        # Bottom Center (Avatar Status)
        self.create_bottom_panel(main_frame)
        
    def create_top_bar(self, parent):
        """Create the top header bar"""
        header_frame = tk.Frame(parent, bg='#1e293b', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, 
                              text="JARK", 
                              font=('SF Pro Display', 28, 'bold'),
                              bg='#1e293b', 
                              fg='white')
        title_label.pack(expand=True)
        
        # Subtitle
        subtitle_label = tk.Label(header_frame, 
                                 text="AI-Powered Café Assistant", 
                                 font=('SF Pro Text', 12),
                                 bg='#1e293b', 
                                 fg='#94a3b8')
        subtitle_label.pack()
        
    def create_left_panel(self, parent):
        """Create the left menu panel"""
        left_frame = tk.Frame(parent, bg='#ffffff', width=280)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Add shadow effect with a border frame
        shadow_frame = tk.Frame(left_frame, bg='#e2e8f0', height=2)
        shadow_frame.pack(fill='x', side='bottom')
        
        # Menu title
        menu_title = tk.Label(left_frame, 
                             text="Navigation", 
                             font=('SF Pro Display', 16, 'bold'),
                             bg='#ffffff', 
                             fg='#1e293b',
                             pady=20)
        menu_title.pack(fill='x')
        
        # Menu items
        menu_items = [
            ("🏠 Home", self.on_home_click),
            ("📋 Orders", self.on_orders_click),
            ("👤 Customers", self.on_customers_click),
            ("📊 Analytics", self.on_analytics_click),
            ("⚙️ Settings", self.on_settings_click),
            ("ℹ️ About", self.on_about_click)
        ]
        
        self.menu_buttons = {}
        for item_text, command in menu_items:
            btn = tk.Button(left_frame,
                           text=item_text,
                           font=('SF Pro Text', 12),
                           bg='#ffffff',
                           fg='#475569',
                           relief='flat',
                           anchor='w',
                           padx=20,
                           pady=15,
                           command=command,
                           cursor='hand2')
            btn.pack(fill='x', padx=10, pady=2)
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: self.on_button_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self.on_button_hover(b, False))
            
            self.menu_buttons[item_text] = btn
            
        # Set Home as active
        self.set_active_menu("🏠 Home")
        
    def create_right_panel(self, parent):
        """Create the conversation panel"""
        right_frame = tk.Frame(parent, bg='#ffffff')
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Chat header
        chat_header = tk.Frame(right_frame, bg='#f1f5f9', height=60)
        chat_header.pack(fill='x')
        chat_header.pack_propagate(False)
        
        chat_title = tk.Label(chat_header, 
                             text="Customer Conversation", 
                             font=('SF Pro Display', 16, 'bold'),
                             bg='#f1f5f9', 
                             fg='#1e293b')
        chat_title.pack(side='left', padx=20, pady=20)
        
        # Status indicator
        self.status_label = tk.Label(chat_header, 
                                   text="● Active", 
                                   font=('SF Pro Text', 10),
                                   bg='#f1f5f9', 
                                   fg='#10b981')
        self.status_label.pack(side='right', padx=20, pady=20)
        
        # Chat area
        chat_frame = tk.Frame(right_frame, bg='#ffffff')
        chat_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Scrollable chat area
        self.chat_canvas = tk.Canvas(chat_frame, bg='#ffffff', highlightthickness=0)
        chat_scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_content = tk.Frame(self.chat_canvas, bg='#ffffff')
        
        self.chat_content.bind("<Configure>", 
                              lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        
        self.chat_canvas.create_window((0, 0), window=self.chat_content, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        chat_scrollbar.pack(side="right", fill="y")
        
        # Input area
        input_frame = tk.Frame(right_frame, bg='#f8fafc', height=80)
        input_frame.pack(fill='x', padx=20, pady=(0, 20))
        input_frame.pack_propagate(False)
        
        self.message_entry = tk.Entry(input_frame, 
                                     font=('SF Pro Text', 12),
                                     bg='#ffffff',
                                     relief='flat',
                                     bd=1)
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(10, 5), pady=20)
        
        send_btn = tk.Button(input_frame,
                           text="Send",
                           font=('SF Pro Text', 12, 'bold'),
                           bg='#3b82f6',
                           fg='white',
                           relief='flat',
                           padx=20,
                           command=self.send_message,
                           cursor='hand2')
        send_btn.pack(side='right', padx=(5, 10), pady=20)
        
        # Bind Enter key
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
    def create_bottom_panel(self, parent):
        """Create the bottom avatar status panel"""
        bottom_frame = tk.Frame(parent, bg='#1e293b', height=120)
        bottom_frame.pack(fill='x', pady=(20, 0))
        bottom_frame.pack_propagate(False)
        
        # Avatar placeholder (circular)
        avatar_frame = tk.Frame(bottom_frame, bg='#3b82f6', width=80, height=80)
        avatar_frame.pack(side='left', padx=30, pady=20)
        avatar_frame.pack_propagate(False)
        
        # Make it circular by creating a canvas
        canvas = tk.Canvas(avatar_frame, width=80, height=80, bg='#1e293b', highlightthickness=0)
        canvas.pack()
        canvas.create_oval(5, 5, 75, 75, fill='#3b82f6', outline='#60a5fa', width=2)
        canvas.create_text(40, 40, text="🤖", font=('SF Pro Display', 24), fill='white')
        
        # Status info
        status_frame = tk.Frame(bottom_frame, bg='#1e293b')
        status_frame.pack(side='left', fill='both', expand=True, pady=20)
        
        status_title = tk.Label(status_frame, 
                               text="JARK Assistant Status", 
                               font=('SF Pro Display', 14, 'bold'),
                               bg='#1e293b', 
                               fg='white')
        status_title.pack(anchor='w')
        
        self.avatar_status = tk.Label(status_frame, 
                                    text="Ready to serve customers", 
                                    font=('SF Pro Text', 11),
                                    bg='#1e293b', 
                                    fg='#94a3b8')
        self.avatar_status.pack(anchor='w', pady=(5, 0))
        
        # Performance stats
        stats_frame = tk.Frame(bottom_frame, bg='#1e293b')
        stats_frame.pack(side='right', padx=30, pady=20)
        
        self.stats_label = tk.Label(stats_frame, 
                                   text="Customers Served: 0\nOrders Processed: 0", 
                                   font=('SF Pro Text', 10),
                                   bg='#1e293b', 
                                   fg='#94a3b8',
                                   justify='right')
        self.stats_label.pack()
        
    def setup_sample_data(self):
        """Add sample chat messages"""
        sample_messages = [
            ("JARK", "Welcome to JARK Café! How may I assist you today?", "10:30 AM"),
            ("Customer", "Hi! I'd like to see your menu please.", "10:31 AM"),
            ("JARK", "Of course! We have a variety of coffee, tea, sandwiches, and pastries. What type of beverage are you in the mood for?", "10:31 AM"),
            ("Customer", "I'd love a cappuccino and maybe a croissant.", "10:32 AM"),
            ("JARK", "Excellent choice! One cappuccino and a croissant. That will be $7.50. Your order will be ready in 5 minutes.", "10:32 AM")
        ]
        
        for sender, message, timestamp in sample_messages:
            self.add_chat_message(sender, message, timestamp)
            
    def add_chat_message(self, sender, message, timestamp):
        """Add a message to the chat"""
        message_frame = tk.Frame(self.chat_content, bg='#ffffff')
        message_frame.pack(fill='x', padx=10, pady=5)
        
        is_jark = sender == "JARK"
        
        # Message bubble
        bubble_frame = tk.Frame(message_frame, bg='#3b82f6' if is_jark else '#e5e7eb')
        if is_jark:
            bubble_frame.pack(anchor='w', fill='x', padx=(0, 80))
        else:
            bubble_frame.pack(anchor='e', fill='x', padx=(80, 0))
        
        # Sender name
        sender_label = tk.Label(bubble_frame, 
                               text=sender, 
                               font=('SF Pro Text', 10, 'bold'),
                               bg='#3b82f6' if is_jark else '#e5e7eb',
                               fg='white' if is_jark else '#374151')
        sender_label.pack(anchor='w', padx=15, pady=(10, 2))
        
        # Message text
        message_label = tk.Label(bubble_frame, 
                                text=message, 
                                font=('SF Pro Text', 11),
                                bg='#3b82f6' if is_jark else '#e5e7eb',
                                fg='white' if is_jark else '#1f2937',
                                wraplength=400,
                                justify='left')
        message_label.pack(anchor='w', padx=15, pady=(0, 5))
        
        # Timestamp
        time_label = tk.Label(bubble_frame, 
                             text=timestamp, 
                             font=('SF Pro Text', 9),
                             bg='#3b82f6' if is_jark else '#e5e7eb',
                             fg='#bfdbfe' if is_jark else '#6b7280')
        time_label.pack(anchor='e', padx=15, pady=(0, 10))
        
        # Auto-scroll to bottom
        self.root.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)
        
    def send_message(self):
        """Send a message from the input field"""
        message = self.message_entry.get().strip()
        if message:
            current_time = datetime.now().strftime("%I:%M %p")
            self.add_chat_message("Customer", message, current_time)
            self.message_entry.delete(0, tk.END)
            
            # Simulate JARK response after a delay
            self.root.after(1000, lambda: self.simulate_jark_response(message))
            
    def simulate_jark_response(self, customer_message):
        """Simulate a response from JARK"""
        responses = [
            "Thank you for your message. How can I help you further?",
            "I understand. Let me process that for you.",
            "Great choice! Is there anything else you'd like to add?",
            "I'm here to assist you. What would you like to know?",
            "Perfect! I'll take care of that right away."
        ]
        
        import random
        response = random.choice(responses)
        current_time = datetime.now().strftime("%I:%M %p")
        self.add_chat_message("JARK", response, current_time)
        
    def on_button_hover(self, button, entering):
        """Handle button hover effects"""
        if entering:
            button.configure(bg='#f1f5f9')
        else:
            # Check if it's the active button
            if button['bg'] != '#3b82f6':
                button.configure(bg='#ffffff')
                
    def set_active_menu(self, menu_text):
        """Set the active menu item"""
        for text, btn in self.menu_buttons.items():
            if text == menu_text:
                btn.configure(bg='#3b82f6', fg='white')
            else:
                btn.configure(bg='#ffffff', fg='#475569')
                
    def update_status(self, status_text):
        """Update the avatar status"""
        self.avatar_status.configure(text=status_text)
        
    def update_stats(self, customers=0, orders=0):
        """Update performance statistics"""
        stats_text = f"Customers Served: {customers}\nOrders Processed: {orders}"
        self.stats_label.configure(text=stats_text)
        
    def update_activity_status(self, is_active=True):
        """Update the activity status indicator"""
        if is_active:
            self.status_label.configure(text="● Active", fg='#10b981')
        else:
            self.status_label.configure(text="● Idle", fg='#f59e0b')
            
    # Menu click handlers
    def on_home_click(self):
        self.set_active_menu("🏠 Home")
        self.update_status("Home dashboard active")
        
    def on_orders_click(self):
        self.set_active_menu("📋 Orders")
        self.update_status("Viewing order management")
        
    def on_customers_click(self):
        self.set_active_menu("👤 Customers")
        self.update_status("Customer database accessed")
        
    def on_analytics_click(self):
        self.set_active_menu("📊 Analytics")
        self.update_status("Analytics dashboard loaded")
        
    def on_settings_click(self):
        self.set_active_menu("⚙️ Settings")
        self.update_status("Settings panel opened")
        
    def on_about_click(self):
        self.set_active_menu("ℹ️ About")
        self.update_status("About JARK Café system")
        
    def run(self):
        """Start the GUI main loop"""
        if hasattr(self, 'root'):
            self.root.mainloop()

# Integration functions for the main application
def create_gui_window():
    """Create and return a GUI window instance"""
    return JARKGUIOverlay()

def run_gui_thread(gui_instance):
    """Run the GUI in a separate thread"""
    gui_instance.run()

if __name__ == "__main__":
    # Test the GUI independently
    gui = JARKGUIOverlay()
    gui.run()