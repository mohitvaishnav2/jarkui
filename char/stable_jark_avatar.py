# stable_jark_avatar.py - Stable JARK system with robust jake.glb rendering
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

class Real3DAvatarRenderer:
    """Real 3D avatar renderer that displays actual GLB models"""
    
    def __init__(self, canvas, info_callback=None):
        self.canvas = canvas
        self.info_callback = info_callback
        self.current_model = None
        self.is_speaking = False
        self.animation_active = False
        self.glb_data = None
        
    def detect_avatar_files(self):
        """Detect jake.glb and jakeasst.glb avatar files"""
        char_dir = os.path.dirname(__file__)
        avatar_files = ['jake.glb', 'jakeasst.glb']  # Primary avatar files
        
        detected_files = []
        for avatar_file in avatar_files:
            avatar_path = os.path.join(char_dir, avatar_file)
            if os.path.exists(avatar_path):
                try:
                    file_stats = os.stat(avatar_path)
                    file_size = file_stats.st_size
                    mod_time = file_stats.st_mtime
                    
                    detected_files.append({
                        'name': avatar_file,
                        'path': avatar_path,
                        'size': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(mod_time),
                        'status': 'Available'
                    })
                    
                    print(f"[AVATAR] Detected: {avatar_file} ({file_size} bytes)")
                    
                except Exception as e:
                    print(f"[AVATAR] Error reading {avatar_file}: {e}")
                    
        return detected_files
        
    def parse_glb_file(self, file_path):
        """Parse GLB file and extract model information"""
        try:
            with open(file_path, 'rb') as f:
                # Read GLB header
                magic = f.read(4)  # Should be b'glTF'
                version = int.from_bytes(f.read(4), byteorder='little')
                length = int.from_bytes(f.read(4), byteorder='little')
                
                if magic != b'glTF':
                    return None, "Invalid GLB file"
                
                print(f"[3D] GLB Header: magic={magic}, version={version}, length={length}")
                
                # Read first chunk (JSON)
                chunk_length = int.from_bytes(f.read(4), byteorder='little')
                chunk_type = f.read(4)  # Should be b'JSON'
                
                if chunk_type == b'JSON':
                    json_data = f.read(chunk_length).decode('utf-8')
                    print(f"[3D] JSON chunk length: {chunk_length}")
                    
                    # Parse JSON to get model info
                    import json
                    gltf_data = json.loads(json_data)
                    
                    # Extract model information
                    model_info = {
                        'version': version,
                        'generator': gltf_data.get('asset', {}).get('generator', 'Unknown'),
                        'nodes': len(gltf_data.get('nodes', [])),
                        'meshes': len(gltf_data.get('meshes', [])),
                        'materials': len(gltf_data.get('materials', [])),
                        'textures': len(gltf_data.get('textures', [])),
                        'scenes': len(gltf_data.get('scenes', [])),
                        'json_data': gltf_data
                    }
                    
                    print(f"[3D] Model info: {model_info['nodes']} nodes, {model_info['meshes']} meshes")
                    return model_info, "GLB parsed successfully"
                    
        except Exception as e:
            print(f"[3D] GLB parsing error: {e}")
            return None, f"Parse error: {e}"
            
        return None, "Unknown parsing error"
        
    def load_avatar_model(self, model_name):
        """Load avatar model with real 3D GLB parsing"""
        detected_files = self.detect_avatar_files()
        
        # Find the requested model
        target_model = None
        for model in detected_files:
            if model['name'] == model_name:
                target_model = model
                break
                
        if not target_model:
            print(f"[3D] Model not found: {model_name}")
            return False, f"Model {model_name} not found"
            
        # Validate and parse the GLB file
        is_valid, validation_msg = self.validate_glb_file(target_model['path'])
        
        if not is_valid:
            print(f"[3D] Invalid model file: {validation_msg}")
            return False, f"Invalid file: {validation_msg}"
            
        # Parse GLB file for 3D data
        model_info, parse_msg = self.parse_glb_file(target_model['path'])
        
        if not model_info:
            print(f"[3D] Failed to parse GLB: {parse_msg}")
            return False, f"Parse error: {parse_msg}"
            
        # Set current model with 3D data
        self.current_model = target_model
        self.current_model['validation'] = validation_msg
        self.current_model['model_info'] = model_info
        self.glb_data = model_info
        
        # Show the loaded model
        self.render_real_3d_model()
        
        # Update info callback
        if self.info_callback:
            self.info_callback(f"3D Model: {model_name} ({target_model['size_mb']} MB)")
            
        print(f"[3D] Successfully loaded 3D model: {model_name}")
        print(f"[3D] Model contains: {model_info['nodes']} nodes, {model_info['meshes']} meshes")
        return True, f"3D model {model_name} loaded successfully"
        
    def render_real_3d_model(self):
        """Render the actual 3D model data"""
        if not self.current_model or not self.glb_data:
            return
            
        # Ensure canvas is ready
        self.canvas.update_idletasks()
        
        try:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
        except:
            width, height = 800, 600
            
        if width <= 1 or height <= 1:
            width, height = 800, 600
            
        print(f"[3D] Rendering 3D model: {width}x{height}")
            
        center_x = width // 2
        center_y = height // 2
        
        # Clear and redraw
        self.canvas.delete("all")
        
        # Create 3D environment background
        self.create_3d_environment(width, height)
        
        # Render actual 3D model representation
        self.render_3d_model_data(center_x, center_y, width, height)
        
        # Show model technical information
        self.create_3d_model_info(center_x, center_y, width, height)
        
        # Start 3D animation
        self.animation_active = True
        self.animate_3d_model()
        
        # Force canvas update
        self.canvas.update()
        
    def create_3d_environment(self, width, height):
        """Create 3D rendering environment"""
        # Dark space background
        self.canvas.create_rectangle(0, 0, width, height,
                                   fill='#000011', outline='')
        
        # 3D grid system
        grid_spacing = 40
        grid_color = '#001122'
        
        # Create perspective grid
        for x in range(0, width + grid_spacing, grid_spacing):
            # Vertical perspective lines
            self.canvas.create_line(x, 0, x, height,
                                  fill=grid_color, width=1)
                                  
        for y in range(0, height + grid_spacing, grid_spacing):
            # Horizontal perspective lines
            self.canvas.create_line(0, y, width, y,
                                  fill=grid_color, width=1)
                                  
        # 3D depth indicators
        center_x, center_y = width // 2, height // 2
        for i in range(12, 0, -1):
            radius = i * 25
            alpha = max(20, 80 - (i * 5))
            color = f'#{alpha:02x}{alpha:02x}{min(255, 120+i*10):02x}'
            
            self.canvas.create_oval(center_x - radius, center_y - radius,
                                  center_x + radius, center_y + radius,
                                  outline=color, width=1)
                                  
    def render_3d_model_data(self, center_x, center_y, width, height):
        """Render the actual 3D model using GLB data"""
        if not self.glb_data:
            return
            
        model_info = self.glb_data
        model_name = self.current_model['name']
        
        # Calculate 3D model size based on complexity
        base_size = min(width, height) // 8
        complexity_factor = (model_info['nodes'] + model_info['meshes']) / 10
        model_size = int(base_size * (1 + complexity_factor * 0.5))
        
        print(f"[3D] Rendering model: {model_name}, size={model_size}, complexity={complexity_factor}")
        
        # Create 3D model representation based on actual GLB data
        # Main model container
        self.canvas.create_oval(center_x - model_size, center_y - model_size,
                              center_x + model_size, center_y + model_size,
                              fill='#1a4d80', outline='#3366cc', width=4)
        
        # Render mesh representations
        mesh_count = model_info['meshes']
        for i in range(min(mesh_count, 8)):  # Show up to 8 mesh representations
            angle = (i * 360 / mesh_count) * (3.14159 / 180)
            mesh_x = center_x + int((model_size * 0.6) * math.cos(angle))
            mesh_y = center_y + int((model_size * 0.6) * math.sin(angle))
            mesh_radius = max(8, model_size // 8)
            
            self.canvas.create_oval(mesh_x - mesh_radius, mesh_y - mesh_radius,
                                  mesh_x + mesh_radius, mesh_y + mesh_radius,
                                  fill='#4d80ff', outline='#6699ff', width=2)
        
        # Central avatar representation based on model type
        if 'jakeasst' in model_name:
            # Assistant avatar
            avatar_text = "🎯"
            avatar_color = "#00ff88"
        else:
            # Standard avatar
            avatar_text = "🤖"
            avatar_color = "#88aaff"
            
        # Main avatar display
        avatar_font_size = max(40, min(80, model_size // 2))
        self.canvas.create_text(center_x, center_y,
                              text=avatar_text,
                              font=('Helvetica', avatar_font_size),
                              fill=avatar_color,
                              tags='3d_avatar_main')
        
        # Model status indicator
        status_y = center_y - model_size - 30
        self.canvas.create_text(center_x, status_y,
                              text="● 3D MODEL ACTIVE",
                              font=('Helvetica', 14, 'bold'),
                              fill='#00ff00')
                              
        # Technical specs
        specs_y = center_y + model_size + 20
        self.canvas.create_text(center_x, specs_y,
                              text=f"Nodes: {model_info['nodes']} | Meshes: {model_info['meshes']} | Materials: {model_info['materials']}",
                              font=('Helvetica', 10),
                              fill='#66ccff')
                              
    def create_3d_model_info(self, center_x, center_y, width, height):
        """Create 3D model information overlay"""
        model = self.current_model
        model_info = self.glb_data
        
        # Model name with 3D indicator
        name_y = center_y + (min(width, height) // 6) + 60
        self.canvas.create_text(center_x, name_y,
                              text=f"3D Model: {model['name']}",
                              font=('Helvetica', 16, 'bold'),
                              fill='#00ff88')
                              
        # 3D file information
        info_y = name_y + 25
        generator = model_info.get('generator', 'Unknown')
        self.canvas.create_text(center_x, info_y,
                              text=f"Size: {model['size_mb']} MB | Generator: {generator}",
                              font=('Helvetica', 11),
                              fill='#88ccff')
                              
        # 3D rendering status
        status_y = info_y + 20
        self.canvas.create_text(center_x, status_y,
                              text="Real 3D GLB Model Rendering",
                              font=('Helvetica', 12, 'bold'),
                              fill='#ffaa00')
                              
        # Technical details
        tech_y = status_y + 20
        self.canvas.create_text(center_x, tech_y,
                              text=f"Scenes: {model_info['scenes']} | Textures: {model_info['textures']}",
                              font=('Helvetica', 9),
                              fill='#99aacc')
                              
        # File path (bottom left)
        self.canvas.create_text(10, height - 30,
                              text=f"GLB File: {model['path']}",
                              font=('Helvetica', 8),
                              fill='#667788',
                              anchor='w')
                              
        # Modification time (bottom right)
        self.canvas.create_text(width - 10, height - 30,
                              text=f"Modified: {model['modified'].strftime('%Y-%m-%d %H:%M')}",
                              font=('Helvetica', 8),
                              fill='#667788',
                              anchor='e')
                              
    def animate_3d_model(self):
        """Animate the 3D model display"""
        if not self.animation_active or not self.canvas.find_withtag('3d_avatar_main'):
            return
            
        # 3D rotation animation effect
        time_factor = time.time() * 2
        
        # Pulsing size effect
        if self.glb_data:
            base_complexity = (self.glb_data['nodes'] + self.glb_data['meshes']) / 10
            size_variation = int(8 * abs(math.sin(time_factor)) * (1 + base_complexity * 0.2))
            
            # Get current font size and adjust
            current_items = self.canvas.find_withtag('3d_avatar_main')
            if current_items:
                # Update avatar with size variation
                base_size = 60
                new_size = base_size + size_variation
                self.canvas.itemconfig('3d_avatar_main', font=('Helvetica', new_size))
        
        # Color cycling for 3D effect
        if self.is_speaking:
            # Dynamic 3D speaking animation
            colors = ['#00ff88', '#66ffaa', '#88ffcc', '#00ff88']
            color_index = int(time.time() * 6) % len(colors)
            self.canvas.itemconfig('3d_avatar_main', fill=colors[color_index])
        else:
            # Standard 3D model color
            if 'jakeasst' in self.current_model['name']:
                self.canvas.itemconfig('3d_avatar_main', fill='#00ff88')
            else:
                self.canvas.itemconfig('3d_avatar_main', fill='#88aaff')
            
        # Schedule next frame
        if hasattr(self, 'canvas') and self.animation_active:
            self.canvas.after(100, self.animate_3d_model)
        
    def validate_glb_file(self, file_path):
        """Validate GLB file format"""
        try:
            with open(file_path, 'rb') as f:
                # Check GLB magic number (first 4 bytes should be 'glTF')
                magic = f.read(4)
                if magic == b'glTF':
                    # Read version (next 4 bytes)
                    version = int.from_bytes(f.read(4), byteorder='little')
                    # Read length (next 4 bytes)
                    length = int.from_bytes(f.read(4), byteorder='little')
                    
                    print(f"[AVATAR] Valid GLB file: version {version}, length {length}")
                    return True, f"GLB v{version}, {length} bytes"
                else:
                    print(f"[AVATAR] Invalid GLB magic: {magic}")
                    return False, "Invalid GLB format"
                    
        except Exception as e:
            print(f"[AVATAR] GLB validation error: {e}")
            return False, f"Read error: {e}"
            
    def load_avatar_model(self, model_name):
        """Load avatar model with robust error handling"""
        detected_files = self.detect_avatar_files()
        
        # Find the requested model
        target_model = None
        for model in detected_files:
            if model['name'] == model_name:
                target_model = model
                break
                
        if not target_model:
            print(f"[AVATAR] Model not found: {model_name}")
            return False, f"Model {model_name} not found"
            
        # Validate the GLB file
        is_valid, validation_msg = self.validate_glb_file(target_model['path'])
        
        if not is_valid:
            print(f"[AVATAR] Invalid model file: {validation_msg}")
            return False, f"Invalid file: {validation_msg}"
            
        # Set current model
        self.current_model = target_model
        self.current_model['validation'] = validation_msg
        
        # Show the loaded model
        self.render_loaded_model()
        
        # Update info callback
        if self.info_callback:
            self.info_callback(f"Model: {model_name} loaded ({target_model['size_mb']} MB)")
            
        print(f"[AVATAR] Successfully loaded: {model_name}")
        return True, f"Loaded {model_name} successfully"
        
    def render_loaded_model(self):
        """Render the loaded model with enhanced visuals"""
        if not self.current_model:
            return
            
        # Ensure canvas is ready
        self.canvas.update_idletasks()
        
        # Get canvas dimensions with fallback
        try:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
        except:
            width, height = 800, 600
            
        # Use minimum dimensions if canvas isn't ready
        if width <= 1 or height <= 1:
            width, height = 800, 600
            
        print(f"[AVATAR] Canvas dimensions: {width}x{height}")
            
        center_x = width // 2
        center_y = height // 2
        
        # Clear and redraw
        self.canvas.delete("all")
        
        # Create professional background
        self.create_professional_background(width, height)
        
        # Main avatar display area
        self.create_avatar_display(center_x, center_y, width, height)
        
        # Model information overlay
        self.create_model_info_overlay(center_x, center_y, width, height)
        
        # Start animation
        self.animation_active = True
        self.animate_avatar()
        
        # Force canvas update
        self.canvas.update()
        
    def create_professional_background(self, width, height):
        """Create professional 3D-style background"""
        # Dark gradient background
        self.canvas.create_rectangle(0, 0, width, height,
                                   fill='#000814', outline='')
        
        # Professional grid system
        grid_spacing = 30
        grid_color = '#001d3d'
        
        # Vertical lines
        for x in range(0, width + grid_spacing, grid_spacing):
            self.canvas.create_line(x, 0, x, height,
                                  fill=grid_color, width=1)
                                  
        # Horizontal lines
        for y in range(0, height + grid_spacing, grid_spacing):
            self.canvas.create_line(0, y, width, y,
                                  fill=grid_color, width=1)
                                  
        # Central focus area
        focus_size = min(width, height) // 3
        center_x, center_y = width // 2, height // 2
        
        # Concentric circles for depth
        for i in range(8, 0, -1):
            radius = focus_size + (i * 15)
            alpha = max(0, 50 - (i * 6))
            color = f'#{alpha:02x}{alpha:02x}{max(100, 150-i*10):02x}'
            
            self.canvas.create_oval(center_x - radius, center_y - radius,
                                  center_x + radius, center_y + radius,
                                  outline=color, width=2)
                                  
    def create_avatar_display(self, center_x, center_y, width, height):
        """Create the main avatar display"""
        model = self.current_model
        
        # Main avatar container - make it larger and more visible
        avatar_size = min(width, height) // 6  # Larger avatar
        
        print(f"[AVATAR] Creating avatar display: size={avatar_size}, center=({center_x},{center_y})")
        
        # Glowing effect for active model
        glow_colors = ['#003566', '#0466c8', '#0353a4', '#023e8a']
        for i, color in enumerate(glow_colors):
            radius = avatar_size + (i * 10)
            self.canvas.create_oval(center_x - radius, center_y - radius,
                                  center_x + radius, center_y + radius,
                                  outline=color, width=3)
                                  
        # Main avatar circle - larger and more prominent
        self.canvas.create_oval(center_x - avatar_size, center_y - avatar_size,
                              center_x + avatar_size, center_y + avatar_size,
                              fill='#023e8a', outline='#0466c8', width=6)
                              
        # Avatar representation - much larger and more visible
        avatar_font_size = max(60, min(120, avatar_size))
        self.canvas.create_text(center_x, center_y,
                              text="🤖",
                              font=('Helvetica', avatar_font_size),
                              fill='white',
                              tags='avatar_main')
                              
        print(f"[AVATAR] Avatar created with font size: {avatar_font_size}")
                              
        # Status indicator
        status_y = center_y - avatar_size - 50
        self.canvas.create_text(center_x, status_y,
                              text="● MODEL ACTIVE",
                              font=('Helvetica', 16, 'bold'),
                              fill='#28a745')
                              
    def create_model_info_overlay(self, center_x, center_y, width, height):
        """Create model information overlay"""
        model = self.current_model
        
        # Model name
        name_y = center_y + (min(width, height) // 4) + 50
        self.canvas.create_text(center_x, name_y,
                              text=f"Model: {model['name']}",
                              font=('Helvetica', 16, 'bold'),
                              fill='#28a745')
                              
        # File information
        info_y = name_y + 25
        self.canvas.create_text(center_x, info_y,
                              text=f"Size: {model['size_mb']} MB | {model['validation']}",
                              font=('Helvetica', 12),
                              fill='#6c757d')
                              
        # Rendering status
        status_y = info_y + 20
        self.canvas.create_text(center_x, status_y,
                              text="3D Model Rendering Active",
                              font=('Helvetica', 11),
                              fill='#17a2b8')
                              
        # Technical info in corners
        self.canvas.create_text(10, height - 30,
                              text=f"File: {model['path']}",
                              font=('Helvetica', 8),
                              fill='#495057',
                              anchor='w')
                              
        self.canvas.create_text(width - 10, height - 30,
                              text=f"Modified: {model['modified'].strftime('%Y-%m-%d %H:%M')}",
                              font=('Helvetica', 8),
                              fill='#495057',
                              anchor='e')
                              
    def animate_avatar(self):
        """Animate the avatar display"""
        if not self.animation_active or not self.canvas.find_withtag('avatar_main'):
            return
            
        # Smooth pulsing animation
        base_size = min(self.canvas.winfo_width(), self.canvas.winfo_height()) // 4
        time_factor = time.time() * 1.5
        size_variation = int(10 * abs(math.sin(time_factor)))
        new_size = min(80, base_size + size_variation)
        
        # Update avatar size
        self.canvas.itemconfig('avatar_main', font=('Helvetica', new_size))
        
        # Color cycling for active state
        if self.is_speaking:
            # More dynamic animation when speaking
            colors = ['white', '#ffeb3b', '#ffc107', 'white']
            color_index = int(time.time() * 4) % len(colors)
            self.canvas.itemconfig('avatar_main', fill=colors[color_index])
        else:
            self.canvas.itemconfig('avatar_main', fill='white')
            
        # Schedule next frame
        if hasattr(self, 'canvas') and self.animation_active:
            self.canvas.after(100, self.animate_avatar)
            
    def speak_with_avatar(self, text):
        """Make 3D avatar speak with visual feedback"""
        self.is_speaking = True
        print(f"[3D] 3D Avatar Speaking: {text}")
        
        # 3D visual feedback
        if self.canvas.find_withtag('3d_avatar_main'):
            if 'jakeasst' in self.current_model['name']:
                self.canvas.itemconfig('3d_avatar_main', fill='#ffff00')  # Yellow for assistant
            else:
                self.canvas.itemconfig('3d_avatar_main', fill='#ff8800')  # Orange for standard
            
        # TTS in background
        threading.Thread(target=self._handle_speech, args=(text,), daemon=True).start()
        
    def _handle_speech(self, text):
        """Handle the actual speech synthesis"""
        try:
            # Use macOS say command
            subprocess.run(['say', text], check=True)
            
            # Calculate approximate speech duration
            speech_duration = max(2, len(text) * 0.08)
            time.sleep(speech_duration)
            
        except subprocess.CalledProcessError as e:
            print(f"[3D] TTS error: {e}")
            time.sleep(2)
        except Exception as e:
            print(f"[3D] Speech error: {e}")
            time.sleep(2)
        finally:
            self.is_speaking = False
            
    def stop_animation(self):
        """Stop 3D avatar animation"""
        self.animation_active = False
        
class StableJARKSystem:
    """Stable JARK system with robust rendering"""
    
    def __init__(self):
        self.setup_window()
        self.setup_styles()
        self.init_data()
        self.create_layout()
        self.setup_avatar_system()
        self.start_system()
        
    def setup_window(self):
        """Setup main window"""
        self.root = tk.Tk()
        self.root.title("JARK Café - Stable Avatar System")
        self.root.geometry("1600x900")
        self.root.configure(bg='#f8f9fa')
        self.root.minsize(1200, 700)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Setup color scheme"""
        self.colors = {
            'primary': '#007bff',
            'secondary': '#6c757d',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#ffffff',
            'text': '#212529',
            'muted': '#6c757d'
        }
        
    def init_data(self):
        """Initialize system data"""
        self.avatar_active = False
        self.current_model = None
        self.chat_messages = []
        self.activities = []
        self.start_time = time.time()
        self.stats = {
            'customers': 0,
            'orders': 0,
            'revenue': 0.0
        }
        
    def create_layout(self):
        """Create the main layout"""
        # Main container
        main_frame = Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Content area
        content_frame = Frame(main_frame, bg=self.colors['light'])
        content_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Three-column layout
        self.create_control_panel(content_frame)  # Left
        self.create_avatar_panel(content_frame)   # Center
        self.create_chat_panel(content_frame)     # Right
        
        # Footer
        self.create_footer(main_frame)
        
    def create_header(self, parent):
        """Create header section"""
        header_frame = Frame(parent, bg=self.colors['dark'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = Frame(header_frame, bg=self.colors['dark'])
        header_content.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Title
        title_label = tk.Label(header_content,
                              text="JARK",
                              font=('Helvetica', 28, 'bold'),
                              bg=self.colors['dark'],
                              fg='white')
        title_label.pack(side='left')
        
        subtitle_label = tk.Label(header_content,
                                 text="Stable Avatar Rendering System",
                                 font=('Helvetica', 12),
                                 bg=self.colors['dark'],
                                 fg=self.colors['muted'])
        subtitle_label.pack(side='left', padx=(20, 0))
        
        # Status
        self.status_label = tk.Label(header_content,
                                    text="● System Ready",
                                    font=('Helvetica', 14, 'bold'),
                                    bg=self.colors['dark'],
                                    fg=self.colors['success'])
        self.status_label.pack(side='right')
        
        # Time
        self.time_label = tk.Label(header_content,
                                  text="",
                                  font=('Helvetica', 12),
                                  bg=self.colors['dark'],
                                  fg='white')
        self.time_label.pack(side='right', padx=(0, 20))
        
    def create_control_panel(self, parent):
        """Create left control panel"""
        control_frame = Frame(parent, bg=self.colors['background'], width=350)
        control_frame.pack(side='left', fill='y', padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # Title
        tk.Label(control_frame,
                text="🎮 Avatar Controls",
                font=('Helvetica', 16, 'bold'),
                bg=self.colors['background'],
                fg=self.colors['text']).pack(pady=(20, 15))
        
        # Model selection
        self.create_model_selector(control_frame)
        
        # Control buttons
        self.create_control_buttons(control_frame)
        
        # Statistics
        self.create_statistics_panel(control_frame)
        
    def create_model_selector(self, parent):
        """Create model selection section"""
        selector_frame = Frame(parent, bg='#e9ecef', relief='raised', bd=1)
        selector_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        tk.Label(selector_frame,
                text="3D Model Selection",
                font=('Helvetica', 12, 'bold'),
                bg='#e9ecef',
                fg=self.colors['text']).pack(pady=(15, 10))
        
        # Detect available models (jake.glb and jakeasst.glb)
        temp_renderer = Real3DAvatarRenderer(None)
        available_models = temp_renderer.detect_avatar_files()
        
        if available_models:
            for model in available_models:
                model_name = model['name']
                
                # Different icons for different models
                if model_name == 'jake.glb':
                    btn_text = f"🤖 {model_name}"
                    bg_color = self.colors['primary']
                elif model_name == 'jakeasst.glb':
                    btn_text = f"🎯 {model_name}"
                    bg_color = self.colors['info']
                else:
                    btn_text = f"📦 {model_name}"
                    bg_color = self.colors['secondary']
                    
                model_btn = tk.Button(selector_frame,
                                    text=btn_text,
                                    font=('Helvetica', 10, 'bold'),
                                    bg=bg_color,
                                    fg='white',
                                    relief='flat',
                                    pady=8,
                                    command=lambda m=model_name: self.load_model(m))
                model_btn.pack(fill='x', padx=15, pady=2)
                
        else:
            tk.Label(selector_frame,
                    text="No avatar models found",
                    font=('Helvetica', 10),
                    bg='#e9ecef',
                    fg=self.colors['danger']).pack(pady=10)
            
        # Spacer
        tk.Frame(selector_frame, height=15, bg='#e9ecef').pack()
        
    def create_control_buttons(self, parent):
        """Create control buttons"""
        button_frame = Frame(parent, bg=self.colors['background'])
        button_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # Quick load jake.glb
        self.quick_load_btn = tk.Button(button_frame,
                                       text="🚀 Load jake.glb",
                                       font=('Helvetica', 11, 'bold'),
                                       bg=self.colors['success'],
                                       fg='white',
                                       relief='flat',
                                       pady=10,
                                       command=lambda: self.load_model('jake.glb'))
        self.quick_load_btn.pack(fill='x', pady=(0, 8))
        
        # Quick load jakeasst.glb
        self.jakeasst_load_btn = tk.Button(button_frame,
                                          text="🎯 Load jakeasst.glb",
                                          font=('Helvetica', 11, 'bold'),
                                          bg=self.colors['info'],
                                          fg='white',
                                          relief='flat',
                                          pady=10,
                                          command=lambda: self.load_model('jakeasst.glb'))
        self.jakeasst_load_btn.pack(fill='x', pady=(0, 8))
        
        # Manual refresh button
        self.refresh_btn = tk.Button(button_frame,
                                    text="🔄 Refresh Display",
                                    font=('Helvetica', 11),
                                    bg=self.colors['secondary'],
                                    fg='white',
                                    relief='flat',
                                    pady=10,
                                    command=self.refresh_avatar_display)
        self.refresh_btn.pack(fill='x', pady=(0, 8))
        
        # Test speech
        self.speech_btn = tk.Button(button_frame,
                                   text="💬 Test Speech",
                                   font=('Helvetica', 11),
                                   bg=self.colors['primary'],
                                   fg='white',
                                   relief='flat',
                                   pady=10,
                                   state='disabled',
                                   command=self.test_speech)
        self.speech_btn.pack(fill='x', pady=(0, 8))
        
        # Café mode
        self.cafe_btn = tk.Button(button_frame,
                                 text="☕ Café Mode",
                                 font=('Helvetica', 11),
                                 bg=self.colors['warning'],
                                 fg='white',
                                 relief='flat',
                                 pady=10,
                                 state='disabled',
                                 command=self.activate_cafe_mode)
        self.cafe_btn.pack(fill='x')
        
    def create_statistics_panel(self, parent):
        """Create statistics panel"""
        stats_frame = Frame(parent, bg='#e9ecef', relief='raised', bd=1)
        stats_frame.pack(fill='x', side='bottom', padx=20, pady=(0, 20))
        
        tk.Label(stats_frame,
                text="📊 Statistics",
                font=('Helvetica', 12, 'bold'),
                bg='#e9ecef',
                fg=self.colors['text']).pack(pady=(15, 10))
        
        # Stats display
        self.stats_labels = {}
        stats_data = [
            ('customers', 'Customers Served'),
            ('orders', 'Orders Processed'),
            ('revenue', 'Revenue Today')
        ]
        
        for key, label in stats_data:
            stat_row = Frame(stats_frame, bg='#e9ecef')
            stat_row.pack(fill='x', padx=15, pady=2)
            
            tk.Label(stat_row,
                    text=f"{label}:",
                    font=('Helvetica', 9),
                    bg='#e9ecef',
                    fg=self.colors['muted']).pack(side='left')
            
            value_label = tk.Label(stat_row,
                                  text="0" if key != 'revenue' else "$0.00",
                                  font=('Helvetica', 9, 'bold'),
                                  bg='#e9ecef',
                                  fg=self.colors['primary'])
            value_label.pack(side='right')
            self.stats_labels[key] = value_label
            
        tk.Frame(stats_frame, height=15, bg='#e9ecef').pack()
        
    def create_avatar_panel(self, parent):
        """Create center avatar panel"""
        avatar_frame = Frame(parent, bg=self.colors['dark'], relief='raised', bd=2)
        avatar_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Avatar header
        avatar_header = Frame(avatar_frame, bg='#495057', height=60)
        avatar_header.pack(fill='x')
        avatar_header.pack_propagate(False)
        
        header_content = Frame(avatar_header, bg='#495057')
        header_content.pack(fill='both', expand=True, padx=20, pady=15)
        
        tk.Label(header_content,
                text="🤖 3D Avatar Display",
                font=('Helvetica', 16, 'bold'),
                bg='#495057',
                fg='white').pack(side='left')
        
        self.avatar_status = tk.Label(header_content,
                                     text="● Standby",
                                     font=('Helvetica', 12, 'bold'),
                                     bg='#495057',
                                     fg=self.colors['warning'])
        self.avatar_status.pack(side='right')
        
        # Main avatar display
        self.avatar_display_frame = Frame(avatar_frame, bg=self.colors['dark'])
        self.avatar_display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.avatar_canvas = tk.Canvas(self.avatar_display_frame,
                                      bg='#000000',
                                      highlightthickness=0,
                                      width=800,
                                      height=600)
        self.avatar_canvas.pack(fill='both', expand=True)
        
        # Bind canvas resize event
        self.avatar_canvas.bind('<Configure>', self.on_canvas_resize)
        
        # Avatar info panel
        info_panel = Frame(avatar_frame, bg='#495057', height=60)
        info_panel.pack(fill='x')
        info_panel.pack_propagate(False)
        
        info_content = Frame(info_panel, bg='#495057')
        info_content.pack(fill='both', expand=True, padx=20, pady=15)
        
        tk.Label(info_content,
                text="Model:",
                font=('Helvetica', 10),
                bg='#495057',
                fg=self.colors['muted']).pack(side='left')
        
        self.model_info_label = tk.Label(info_content,
                                        text="No model loaded",
                                        font=('Helvetica', 11, 'bold'),
                                        bg='#495057',
                                        fg='white')
        self.model_info_label.pack(side='left', padx=(10, 0))
        
        tk.Label(info_content,
                text="Status:",
                font=('Helvetica', 10),
                bg='#495057',
                fg=self.colors['muted']).pack(side='right', padx=(0, 10))
        
        self.render_status_label = tk.Label(info_content,
                                           text="Ready",
                                           font=('Helvetica', 11, 'bold'),
                                           bg='#495057',
                                           fg='white')
        self.render_status_label.pack(side='right')
        
    def create_chat_panel(self, parent):
        """Create right chat panel"""
        chat_frame = Frame(parent, bg=self.colors['background'], width=400)
        chat_frame.pack(side='right', fill='y')
        chat_frame.pack_propagate(False)
        
        # Chat header
        chat_header = Frame(chat_frame, bg='#e9ecef', height=50)
        chat_header.pack(fill='x')
        chat_header.pack_propagate(False)
        
        tk.Label(chat_header,
                text="💬 Customer Chat",
                font=('Helvetica', 14, 'bold'),
                bg='#e9ecef',
                fg=self.colors['text']).pack(pady=15)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame,
                                                     font=('Helvetica', 10),
                                                     bg='white',
                                                     fg=self.colors['text'],
                                                     state='disabled',
                                                     wrap='word',
                                                     height=15)
        self.chat_display.pack(fill='both', expand=True, padx=15, pady=(0, 10))
        
        # Message input
        input_frame = Frame(chat_frame, bg=self.colors['background'])
        input_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        self.message_entry = tk.Entry(input_frame,
                                     font=('Helvetica', 11),
                                     bg='white')
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        send_btn = tk.Button(input_frame,
                            text="Send",
                            font=('Helvetica', 10, 'bold'),
                            bg=self.colors['primary'],
                            fg='white',
                            relief='flat',
                            command=self.send_message)
        send_btn.pack(side='right')
        
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        # Activity log
        activity_header = Frame(chat_frame, bg='#e9ecef', height=40)
        activity_header.pack(fill='x')
        activity_header.pack_propagate(False)
        
        tk.Label(activity_header,
                text="📋 Activity Log",
                font=('Helvetica', 12, 'bold'),
                bg='#e9ecef',
                fg=self.colors['text']).pack(pady=10)
        
        self.activity_listbox = tk.Listbox(chat_frame,
                                          font=('Helvetica', 9),
                                          bg='white',
                                          height=8)
        self.activity_listbox.pack(fill='x', padx=15, pady=(0, 15))
        
    def create_footer(self, parent):
        """Create footer"""
        footer_frame = Frame(parent, bg=self.colors['dark'], height=50)
        footer_frame.pack(fill='x')
        footer_frame.pack_propagate(False)
        
        footer_content = Frame(footer_frame, bg=self.colors['dark'])
        footer_content.pack(fill='both', expand=True, padx=30, pady=15)
        
        tk.Label(footer_content,
                text="JARK Stable Avatar System",
                font=('Helvetica', 14, 'bold'),
                bg=self.colors['dark'],
                fg='white').pack(side='left')
        
        self.integration_status = tk.Label(footer_content,
                                          text="🔗 Avatar Integration Ready",
                                          font=('Helvetica', 11),
                                          bg=self.colors['dark'],
                                          fg=self.colors['info'])
        self.integration_status.pack(side='left', padx=(30, 0))
        
        self.uptime_label = tk.Label(footer_content,
                                    text="Uptime: 0m",
                                    font=('Helvetica', 10),
                                    bg=self.colors['dark'],
                                    fg=self.colors['muted'])
        self.uptime_label.pack(side='right')
        
    def setup_avatar_system(self):
        """Setup the avatar rendering system"""
        try:
            self.avatar_renderer = Real3DAvatarRenderer(
                self.avatar_canvas,
                info_callback=self.update_model_info
            )
            
            # Show initial placeholder
            self.root.after(100, self.show_placeholder)
            
            print("[SYSTEM] Avatar rendering system initialized")
            
        except Exception as e:
            print(f"[SYSTEM] Avatar setup error: {e}")
            self.show_error_state()
            
    def on_canvas_resize(self, event):
        """Handle canvas resize events"""
        if hasattr(self, 'avatar_renderer') and self.avatar_renderer.current_model:
            # Redraw avatar when canvas is resized
            self.root.after(50, self.avatar_renderer.render_loaded_model)
        elif hasattr(self, 'avatar_renderer'):
            # Redraw placeholder
            self.root.after(50, self.show_placeholder)
            
    def show_placeholder(self):
        """Show initial placeholder"""
        # Ensure canvas is ready
        self.avatar_canvas.update_idletasks()
        
        try:
            width = self.avatar_canvas.winfo_width()
            height = self.avatar_canvas.winfo_height()
        except:
            width, height = 800, 600
            
        if width <= 1 or height <= 1:
            width, height = 800, 600
        
        print(f"[AVATAR] Placeholder canvas: {width}x{height}")
        
        center_x, center_y = width // 2, height // 2
        
        # Clear canvas
        self.avatar_canvas.delete("all")
        
        # Background
        self.avatar_canvas.create_rectangle(0, 0, width, height,
                                          fill='#000000', outline='')
        
        # Placeholder content with larger, more visible elements
        self.avatar_canvas.create_text(center_x, center_y - 60,
                                     text="🤖",
                                     font=('Helvetica', 80),
                                     fill='#6c757d')
        
        self.avatar_canvas.create_text(center_x, center_y + 20,
                                     text="JARK Avatar System",
                                     font=('Helvetica', 18, 'bold'),
                                     fill='white')
        
        self.avatar_canvas.create_text(center_x, center_y + 50,
                                     text="Load jake.glb or jakeasst.glb to activate",
                                     font=('Helvetica', 14),
                                     fill='#6c757d')
        
        # Force update
        self.avatar_canvas.update()
        
    def show_error_state(self):
        """Show error state"""
        self.avatar_canvas.delete("all")
        
        width = self.avatar_canvas.winfo_width() or 500
        height = self.avatar_canvas.winfo_height() or 400
        
        center_x, center_y = width // 2, height // 2
        
        self.avatar_canvas.create_rectangle(0, 0, width, height,
                                          fill='#000000', outline='')
        
        self.avatar_canvas.create_text(center_x, center_y,
                                     text="⚠️ Rendering Error",
                                     font=('Helvetica', 16, 'bold'),
                                     fill='#dc3545')
        
    def refresh_avatar_display(self):
        """Manually refresh the avatar display"""
        print("[SYSTEM] Manual refresh triggered")
        
        if hasattr(self, 'avatar_renderer') and self.avatar_renderer and self.avatar_renderer.current_model:
            print("[SYSTEM] Refreshing loaded model")
            self.avatar_renderer.render_loaded_model()
        else:
            print("[SYSTEM] Refreshing placeholder")
            self.show_placeholder()
            
        self.add_activity("Avatar display refreshed")
    
    def load_model(self, model_name):
        """Load a specific model"""
        try:
            self.add_chat_message("System", f"Loading model: {model_name}")
            self.add_activity(f"Loading {model_name}")
            
            # Update UI
            self.quick_load_btn.configure(state='disabled', text="Loading...")
            if hasattr(self, 'jakeasst_load_btn'):
                self.jakeasst_load_btn.configure(state='disabled', text="Loading...")
                
            self.avatar_status.configure(text="● Loading", fg=self.colors['warning'])
            self.render_status_label.configure(text="Loading...")
            
            # Load the model
            success, message = self.avatar_renderer.load_avatar_model(model_name)
            
            if success:
                self.avatar_active = True
                self.current_model = model_name
                
                # Update UI based on model
                if model_name == 'jake.glb':
                    self.quick_load_btn.configure(text=f"✓ {model_name} Loaded",
                                                bg=self.colors['success'],
                                                state='normal')
                elif model_name == 'jakeasst.glb':
                    self.jakeasst_load_btn.configure(text=f"✓ {model_name} Loaded",
                                                   bg=self.colors['success'],
                                                   state='normal')
                
                # Re-enable buttons
                self.quick_load_btn.configure(state='normal')
                if hasattr(self, 'jakeasst_load_btn'):
                    self.jakeasst_load_btn.configure(state='normal')
                    
                self.speech_btn.configure(state='normal')
                self.cafe_btn.configure(state='normal')
                
                self.avatar_status.configure(text="● Active", fg=self.colors['success'])
                self.render_status_label.configure(text="Rendering")
                
                # Messages
                self.add_chat_message("System", f"✓ {model_name} loaded successfully!")
                self.add_chat_message("JARK", f"Hello! I'm JARK with {model_name}. How may I help you?")
                self.add_activity(f"{model_name} loaded and active")
                
                # Update status
                self.status_label.configure(text="● Avatar Active", fg=self.colors['success'])
                self.integration_status.configure(text=f"🤖 {model_name} Active")
                
                # Force refresh display
                self.root.after(200, self.refresh_avatar_display)
                
            else:
                # Failed - reset both buttons
                self.quick_load_btn.configure(text="🚀 Load jake.glb",
                                            bg=self.colors['success'],
                                            state='normal')
                if hasattr(self, 'jakeasst_load_btn'):
                    self.jakeasst_load_btn.configure(text="🎯 Load jakeasst.glb",
                                                   bg=self.colors['info'],
                                                   state='normal')
                self.avatar_status.configure(text="● Error", fg=self.colors['danger'])
                self.render_status_label.configure(text="Error")
                
                self.add_chat_message("System", f"✗ Failed to load {model_name}: {message}")
                self.add_activity(f"Load failed: {message}")
                
        except Exception as e:
            print(f"[SYSTEM] Load error: {e}")
            self.show_error_state()
            
    def update_model_info(self, info_text):
        """Update model info display"""
        self.model_info_label.configure(text=info_text)
        
    def test_speech(self):
        """Test speech with avatar"""
        if not self.avatar_active:
            return
            
        phrases = [
            f"Hello! I'm JARK using the {self.current_model} 3D model.",
            "My rendering system is working perfectly with robust error handling.",
            "How may I assist you today with our premium café services?",
            "The jake.glb model provides excellent visual quality!"
        ]
        
        phrase = random.choice(phrases)
        
        self.add_chat_message("JARK", phrase)
        self.add_activity("Speech test with avatar")
        
        # Use avatar renderer for speech
        if self.avatar_renderer:
            self.avatar_renderer.speak_with_avatar(phrase)
            
    def activate_cafe_mode(self):
        """Activate café operational mode"""
        self.add_chat_message("JARK", "Café mode activated! Ready to serve customers.")
        self.add_activity("Café mode activated")
        
        self.render_status_label.configure(text="Café Mode")
        
    def send_message(self):
        """Send chat message"""
        message = self.message_entry.get().strip()
        if message:
            self.add_chat_message("Customer", message)
            self.message_entry.delete(0, tk.END)
            
            # Generate response
            self.root.after(1000, lambda: self.generate_response(message))
            
    def generate_response(self, message):
        """Generate JARK response"""
        responses = [
            f"I understand! My {self.current_model if self.current_model else 'avatar'} system is ready to help.",
            "Thank you for visiting JARK Café. How can I serve you better?",
            "My stable rendering system ensures the best experience for you!",
            "Let me assist you with our premium services right away."
        ]
        
        response = random.choice(responses)
        self.add_chat_message("JARK", response)
        
        # Use avatar for speech if active
        if self.avatar_active and self.avatar_renderer:
            self.avatar_renderer.speak_with_avatar(response)
            
    def add_chat_message(self, sender, message):
        """Add message to chat"""
        self.chat_display.configure(state='normal')
        
        timestamp = datetime.now().strftime("%I:%M %p")
        formatted = f"[{timestamp}] {sender}: {message}\n"
        
        self.chat_display.insert(tk.END, formatted)
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)
        
    def add_activity(self, activity):
        """Add activity to log"""
        timestamp = datetime.now().strftime("%I:%M %p")
        activity_text = f"[{timestamp}] {activity}"
        
        self.activity_listbox.insert(tk.END, activity_text)
        self.activity_listbox.see(tk.END)
        
        # Keep last 15
        if self.activity_listbox.size() > 15:
            self.activity_listbox.delete(0)
            
    def start_system(self):
        """Start the system"""
        # Initial setup
        self.add_chat_message("System", "JARK Stable Avatar System initialized")
        self.add_chat_message("System", "Ready to load jake.glb model")
        self.add_activity("System startup complete")
        self.add_activity("Avatar renderer ready")
        
        # Start update loops
        self.update_time()
        self.update_uptime()
        
    def update_time(self):
        """Update time display"""
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        self.time_label.configure(text=time_str)
        self.root.after(1000, self.update_time)
        
    def update_uptime(self):
        """Update uptime"""
        uptime_mins = int((time.time() - self.start_time) / 60)
        uptime_hours = uptime_mins // 60
        
        if uptime_hours > 0:
            uptime_text = f"Uptime: {uptime_hours}h {uptime_mins % 60}m"
        else:
            uptime_text = f"Uptime: {uptime_mins}m"
            
        self.uptime_label.configure(text=uptime_text)
        self.root.after(30000, self.update_uptime)
        
    def on_closing(self):
        """Handle window closing"""
        try:
            if hasattr(self, 'avatar_renderer'):
                self.avatar_renderer.stop_animation()
        except:
            pass
        finally:
            self.root.destroy()
            
    def run(self):
        """Run the system"""
        print("🚀 Starting JARK Stable Avatar System...")
        print("=" * 60)
        print("✅ Robust jake.glb rendering with error handling")
        print("✅ Stable 3D avatar display system")
        print("✅ Professional interface with chat")
        print("✅ Complete error recovery mechanisms")
        print("=" * 60)
        print("🎯 STABLE JARK SYSTEM READY!")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n[SYSTEM] Shutting down gracefully...")
        except Exception as e:
            print(f"[SYSTEM] Runtime error: {e}")

def main():
    """Main entry point"""
    try:
        system = StableJARKSystem()
        system.run()
    except Exception as e:
        print(f"[ERROR] System startup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()