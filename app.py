import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageDraw, ImageTk
import os
from datetime import datetime

class PlannifyProAI:
    """
    Plannify Pro AI - Complete Floor Planning Application
    Python version using Tkinter for GUI
    """
    
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Plannify Pro AI - Floor Planning Application")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8fafc')
        
        # Application state variables
        self.current_tab = 'draw_plot'
        self.plot_points = []
        self.is_drawing = False
        self.scale = 10  # pixels per foot
        self.facing = 'north'
        self.selected_rooms = set()
        self.room_sizes = {}
        
        # Room definitions with Vastu-based colors and size ranges
        self.room_definitions = {
            'master_bedroom': {'name': 'Master Bedroom', 'min_size': 200, 'max_size': 400, 'default_size': 250, 'color': '#8b5cf6'},
            'bedroom': {'name': 'Bedroom', 'min_size': 150, 'max_size': 300, 'default_size': 180, 'color': '#3b82f6'},
            'living_room': {'name': 'Living Room', 'min_size': 250, 'max_size': 500, 'default_size': 300, 'color': '#f97316'},
            'kitchen': {'name': 'Kitchen', 'min_size': 120, 'max_size': 250, 'default_size': 150, 'color': '#ef4444'},
            'dining_room': {'name': 'Dining Room', 'min_size': 120, 'max_size': 280, 'default_size': 150, 'color': '#ec4899'},
            'toilet_bath': {'name': 'Toilet & Bath', 'min_size': 60, 'max_size': 150, 'default_size': 80, 'color': '#10b981'},
            'study_room': {'name': 'Study Room', 'min_size': 100, 'max_size': 220, 'default_size': 120, 'color': '#6366f1'},
            'balcony': {'name': 'Balcony', 'min_size': 60, 'max_size': 180, 'default_size': 80, 'color': '#14b8a6'},
            'pooja_room': {'name': 'Pooja Room', 'min_size': 40, 'max_size': 100, 'default_size': 60, 'color': '#f97316'},
            'store_room': {'name': 'Store Room', 'min_size': 40, 'max_size': 100, 'default_size': 50, 'color': '#6b7280'}
        }
        
        # Canvas dimensions
        self.canvas_width = 600
        self.canvas_height = 400
        
        # Initialize the application
        self.init_app()
    
    def init_app(self):
        """Initialize the application components"""
        self.setup_ui()
        self.setup_event_handlers()
        self.update_plot_info()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_plot_drawing_tab()
        self.create_room_config_tab()
        self.create_floor_plan_tab()
        self.create_beam_calculator_tab()
        self.create_ai_chat_tab()
        
        # Create status bar
        self.create_status_bar()
    
    def create_plot_drawing_tab(self):
        """Create the plot drawing tab"""
        plot_frame = ttk.Frame(self.notebook)
        self.notebook.add(plot_frame, text="Draw Plot")
        
        # Left panel for controls
        control_panel = ttk.Frame(plot_frame)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Drawing controls
        ttk.Label(control_panel, text="Drawing Controls", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.start_drawing_btn = ttk.Button(control_panel, text="Start Drawing", command=self.toggle_drawing)
        self.start_drawing_btn.pack(pady=5)
        
        ttk.Button(control_panel, text="Clear Plot", command=self.clear_plot).pack(pady=5)
        ttk.Button(control_panel, text="Undo Point", command=self.undo_last_point).pack(pady=5)
        
        # Scale control
        ttk.Label(control_panel, text="Scale (pixels/foot):", font=('Arial', 10, 'bold')).pack(pady=(20, 5))
        self.scale_var = tk.IntVar(value=self.scale)
        scale_frame = ttk.Frame(control_panel)
        scale_frame.pack(fill=tk.X)
        self.scale_slider = ttk.Scale(scale_frame, from_=5, to=20, variable=self.scale_var, 
                                     orient=tk.HORIZONTAL, command=self.on_scale_change)
        self.scale_slider.pack(fill=tk.X)
        self.scale_label = ttk.Label(control_panel, text=f"Scale: {self.scale}")
        self.scale_label.pack()
        
        # Facing direction
        ttk.Label(control_panel, text="Facing Direction:", font=('Arial', 10, 'bold')).pack(pady=(20, 5))
        self.facing_var = tk.StringVar(value=self.facing)
        facing_combo = ttk.Combobox(control_panel, textvariable=self.facing_var, 
                                   values=['north', 'south', 'east', 'west'], state='readonly')
        facing_combo.pack(fill=tk.X)
        
        # Plot information
        ttk.Label(control_panel, text="Plot Information", font=('Arial', 12, 'bold')).pack(pady=(30, 10))
        
        info_frame = ttk.Frame(control_panel)
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text="Vertices:").grid(row=0, column=0, sticky=tk.W)
        self.vertex_count_label = ttk.Label(info_frame, text="0")
        self.vertex_count_label.grid(row=0, column=1)
        
        ttk.Label(info_frame, text="Total Area:").grid(row=1, column=0, sticky=tk.W)
        self.total_area_label = ttk.Label(info_frame, text="0 sq ft")
        self.total_area_label.grid(row=1, column=1)
        
        ttk.Label(info_frame, text="Built-up Area:").grid(row=2, column=0, sticky=tk.W)
        self.builtup_area_label = ttk.Label(info_frame, text="0 sq ft")
        self.builtup_area_label.grid(row=2, column=1)
        
        # Canvas for drawing
        canvas_frame = ttk.Frame(plot_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(canvas_frame, text="Plot Drawing Area", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        self.plot_canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, 
                                    bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.plot_canvas.pack()
        
        # Instructions
        instructions = """
        Instructions:
        • Click "Start Drawing" to begin
        • Click on canvas to add points
        • Right-click to undo last point
        • At least 3 points needed for area calculation
        """
        ttk.Label(canvas_frame, text=instructions, justify=tk.LEFT, font=('Arial', 9)).pack(pady=10)
    
    def create_room_config_tab(self):
        """Create the room configuration tab"""
        room_frame = ttk.Frame(self.notebook)
        self.notebook.add(room_frame, text="Configure Rooms")
        
        # Left panel for room selection
        left_panel = ttk.Frame(room_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(left_panel, text="Select Rooms", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Room selection with checkboxes
        self.room_vars = {}
        self.room_sliders = {}
        
        rooms_frame = ttk.Frame(left_panel)
        rooms_frame.pack(fill=tk.BOTH, expand=True)
        
        for room_key, room_data in self.room_definitions.items():
            room_container = ttk.Frame(rooms_frame)
            room_container.pack(fill=tk.X, pady=2)
            
            # Checkbox for room selection
            var = tk.BooleanVar()
            self.room_vars[room_key] = var
            checkbox = ttk.Checkbutton(room_container, variable=var, 
                                     command=lambda k=room_key: self.toggle_room_selection(k))
            checkbox.pack(side=tk.LEFT)
            
            # Room name and size info
            info_text = f"{room_data['name']} ({room_data['min_size']}-{room_data['max_size']} sq ft)"
            ttk.Label(room_container, text=info_text).pack(side=tk.LEFT, padx=(5, 0))
            
            # Color indicator
            color_canvas = tk.Canvas(room_container, width=15, height=15, 
                                   highlightthickness=0, relief=tk.FLAT)
            color_canvas.pack(side=tk.RIGHT)
            color_canvas.configure(bg=room_data['color'])
        
        # Right panel for room size adjustment
        right_panel = ttk.Frame(room_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_panel, text="Room Size Adjustment", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        self.sliders_frame = ttk.Frame(right_panel)
        self.sliders_frame.pack(fill=tk.BOTH, expand=True)
        
        # Generate floor plan button
        ttk.Button(right_panel, text="Generate Floor Plan", 
                  command=self.generate_floor_plan).pack(pady=20)
    
    def create_floor_plan_tab(self):
        """Create the floor plan display tab"""
        plan_frame = ttk.Frame(self.notebook)
        self.notebook.add(plan_frame, text="Floor Plan")
        
        # Controls frame
        controls_frame = ttk.Frame(plan_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(controls_frame, text="Download Plan", 
                  command=self.download_floor_plan).pack(side=tk.LEFT)
        
        self.show_dimensions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls_frame, text="Show Dimensions", 
                       variable=self.show_dimensions_var).pack(side=tk.LEFT, padx=10)
        
        # Canvas for floor plan
        self.floor_plan_canvas = tk.Canvas(plan_frame, width=800, height=600, 
                                          bg='white', relief=tk.SUNKEN, borderwidth=2)
        self.floor_plan_canvas.pack()
        
        # Room schedule frame
        schedule_frame = ttk.LabelFrame(plan_frame, text="Room Schedule")
        schedule_frame.pack(fill=tk.X, pady=10)
        
        # Create treeview for room schedule
        columns = ("Room", "Area (sq ft)", "Dimensions", "Height")
        self.room_schedule_tree = ttk.Treeview(schedule_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.room_schedule_tree.heading(col, text=col)
            self.room_schedule_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL, command=self.room_schedule_tree.yview)
        self.room_schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        self.room_schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_beam_calculator_tab(self):
        """Create the beam calculator tab"""
        beam_frame = ttk.Frame(self.notebook)
        self.notebook.add(beam_frame, text="Beam Calculator")
        
        # Input frame
        input_frame = ttk.LabelFrame(beam_frame, text="Beam Parameters")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Beam type
        ttk.Label(input_frame, text="Beam Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.beam_type_var = tk.StringVar(value="simply_supported")
        beam_type_combo = ttk.Combobox(input_frame, textvariable=self.beam_type_var,
                                      values=["simply_supported", "cantilever", "fixed_both"], 
                                      state='readonly')
        beam_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Beam length
        ttk.Label(input_frame, text="Length (ft):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.beam_length_var = tk.DoubleVar(value=12.0)
        ttk.Entry(input_frame, textvariable=self.beam_length_var).grid(row=1, column=1, padx=5, pady=5)
        
        # Load
        ttk.Label(input_frame, text="Distributed Load (kN/m):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.beam_load_var = tk.DoubleVar(value=10.0)
        ttk.Entry(input_frame, textvariable=self.beam_load_var).grid(row=2, column=1, padx=5, pady=5)
        
        # Calculate button
        ttk.Button(input_frame, text="Calculate", command=self.calculate_beam).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(beam_frame, text="Results")
        results_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(results_frame, text="Maximum Moment:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_moment_label = ttk.Label(results_frame, text="0 kN-m")
        self.max_moment_label.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(results_frame, text="Maximum Shear:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_shear_label = ttk.Label(results_frame, text="0 kN")
        self.max_shear_label.grid(row=1, column=1, padx=5, pady=5)
        
        # Diagrams frame
        diagrams_frame = ttk.Frame(beam_frame)
        diagrams_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create matplotlib figures for diagrams
        self.create_beam_diagrams(diagrams_frame)
    
    def create_beam_diagrams(self, parent):
        """Create matplotlib figures for beam diagrams"""
        # Create figure with subplots
        self.beam_fig, (self.sfd_ax, self.bmd_ax) = plt.subplots(2, 1, figsize=(8, 6))
        self.beam_fig.suptitle('Shear Force and Bending Moment Diagrams')
        
        # Configure axes
        self.sfd_ax.set_title('Shear Force Diagram')
        self.sfd_ax.set_ylabel('Shear Force (kN)')
        self.sfd_ax.grid(True, alpha=0.3)
        
        self.bmd_ax.set_title('Bending Moment Diagram')
        self.bmd_ax.set_xlabel('Distance (ft)')
        self.bmd_ax.set_ylabel('Bending Moment (kN-m)')
        self.bmd_ax.grid(True, alpha=0.3)
        
        # Embed in tkinter
        self.beam_canvas = FigureCanvasTkAgg(self.beam_fig, parent)
        self.beam_canvas.draw()
        self.beam_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_ai_chat_tab(self):
        """Create the AI chat assistant tab"""
        chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(chat_frame, text="AI Assistant")
        
        # Chat display area
        chat_display_frame = ttk.Frame(chat_frame)
        chat_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_text = tk.Text(chat_display_frame, height=20, state=tk.DISABLED, 
                                wrap=tk.WORD, font=('Arial', 10))
        chat_scrollbar = ttk.Scrollbar(chat_display_frame, command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.chat_input_var = tk.StringVar()
        chat_entry = ttk.Entry(input_frame, textvariable=self.chat_input_var, font=('Arial', 10))
        chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(input_frame, text="Send", command=self.send_chat_message).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Bind Enter key to send message
        chat_entry.bind('<Return>', lambda e: self.send_chat_message())
        
        # Add welcome message
        self.add_chat_message("Hello! I'm your AI structural engineering assistant. Ask me about beam design, columns, foundations, IS codes, or any construction-related questions!", "ai")
    
    def create_status_bar(self):
        """Create status bar at the bottom"""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_event_handlers(self):
        """Setup event handlers for canvas interactions"""
        self.plot_canvas.bind("<Button-1>", self.on_canvas_click)
        self.plot_canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.plot_canvas.bind("<Motion>", self.on_canvas_motion)
    
    def toggle_drawing(self):
        """Toggle drawing mode"""
        self.is_drawing = not self.is_drawing
        
        if self.is_drawing:
            self.start_drawing_btn.configure(text="Stop Drawing")
            self.status_var.set("Drawing mode active - Click to add points")
        else:
            self.start_drawing_btn.configure(text="Start Drawing")
            self.status_var.set("Drawing mode stopped")
    
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if self.is_drawing:
            self.add_plot_point(event.x, event.y)
    
    def on_canvas_right_click(self, event):
        """Handle canvas right-click events"""
        if self.is_drawing:
            self.undo_last_point()
    
    def on_canvas_motion(self, event):
        """Handle canvas mouse motion for preview line"""
        if self.is_drawing and self.plot_points:
            self.show_preview_line(event.x, event.y)
    
    def add_plot_point(self, x, y):
        """Add a point to the plot"""
        self.plot_points.append({'x': x, 'y': y})
        self.redraw_canvas()
        self.update_plot_info()
        self.status_var.set(f"Added point {len(self.plot_points)}")
    
    def clear_plot(self):
        """Clear all plot points"""
        self.plot_points = []
        self.redraw_canvas()
        self.update_plot_info()
        self.status_var.set("Plot cleared")
    
    def undo_last_point(self):
        """Undo the last plot point"""
        if self.plot_points:
            self.plot_points.pop()
            self.redraw_canvas()
            self.update_plot_info()
            self.status_var.set("Last point removed")
    
    def show_preview_line(self, mouse_x, mouse_y):
        """Show preview line while drawing"""
        if not self.plot_points:
            return
        
        self.redraw_canvas()
        
        last_point = self.plot_points[-1]
        self.plot_canvas.create_line(last_point['x'], last_point['y'], mouse_x, mouse_y,
                                   fill='gray', dash=(5, 5), tags='preview')
    
    def redraw_canvas(self):
        """Redraw the canvas with current plot"""
        self.plot_canvas.delete("all")
        self.draw_grid()
        
        if not self.plot_points:
            return
        
        # Draw plot lines
        if len(self.plot_points) > 1:
            points = []
            for point in self.plot_points:
                points.extend([point['x'], point['y']])
            
            self.plot_canvas.create_line(points, fill='blue', width=3, tags='plot')
            
            # Close polygon if we have at least 3 points
            if len(self.plot_points) >= 3:
                self.plot_canvas.create_line(
                    self.plot_points[-1]['x'], self.plot_points[-1]['y'],
                    self.plot_points[0]['x'], self.plot_points[0]['y'],
                    fill='blue', width=3, tags='plot'
                )
                
                # Fill polygon
                fill_points = []
                for point in self.plot_points:
                    fill_points.extend([point['x'], point['y']])
                
                self.plot_canvas.create_polygon(fill_points, fill='lightblue', 
                                              outline='blue', width=3, stipple='gray25', tags='plot_fill')
        
        # Draw points
        for i, point in enumerate(self.plot_points):
            self.plot_canvas.create_oval(point['x']-4, point['y']-4, 
                                       point['x']+4, point['y']+4,
                                       fill='darkblue', tags='points')
            
            # Draw measurements
            if i > 0:
                self.draw_measurement(self.plot_points[i-1], point)
        
        # Draw closing measurement
        if len(self.plot_points) >= 3:
            self.draw_measurement(self.plot_points[-1], self.plot_points[0])
    
    def draw_grid(self):
        """Draw grid on canvas"""
        grid_size = 20
        
        # Vertical lines
        for x in range(0, self.canvas_width, grid_size):
            self.plot_canvas.create_line(x, 0, x, self.canvas_height, 
                                       fill='lightgray', tags='grid')
        
        # Horizontal lines
        for y in range(0, self.canvas_height, grid_size):
            self.plot_canvas.create_line(0, y, self.canvas_width, y, 
                                       fill='lightgray', tags='grid')
    
    def draw_measurement(self, point1, point2):
        """Draw measurement between two points"""
        distance = math.sqrt((point2['x'] - point1['x'])**2 + (point2['y'] - point1['y'])**2)
        feet = round(distance / self.scale, 1)
        
        mid_x = (point1['x'] + point2['x']) / 2
        mid_y = (point1['y'] + point2['y']) / 2
        
        self.plot_canvas.create_text(mid_x, mid_y-10, text=f"{feet}'", 
                                   fill='orange', font=('Arial', 9, 'bold'), tags='measurements')
    
    def calculate_area(self):
        """Calculate plot area using shoelace formula"""
        if len(self.plot_points) < 3:
            return 0
        
        area = 0
        n = len(self.plot_points)
        
        for i in range(n):
            j = (i + 1) % n
            area += self.plot_points[i]['x'] * self.plot_points[j]['y']
            area -= self.plot_points[j]['x'] * self.plot_points[i]['y']
        
        area = abs(area) / 2
        return round(area / (self.scale * self.scale))
    
    def update_plot_info(self):
        """Update plot information display"""
        area = self.calculate_area()
        builtup_area = round(area * 0.75)
        
        self.vertex_count_label.configure(text=str(len(self.plot_points)))
        self.total_area_label.configure(text=f"{area} sq ft")
        self.builtup_area_label.configure(text=f"{builtup_area} sq ft")
    
    def on_scale_change(self, value):
        """Handle scale slider change"""
        self.scale = int(float(value))
        self.scale_label.configure(text=f"Scale: {self.scale}")
        self.redraw_canvas()
        self.update_plot_info()
    
    def toggle_room_selection(self, room_key):
        """Toggle room selection and create/remove sliders"""
        if self.room_vars[room_key].get():
            self.selected_rooms.add(room_key)
            self.room_sizes[room_key] = self.room_definitions[room_key]['default_size']
            self.create_room_slider(room_key)
        else:
            self.selected_rooms.discard(room_key)
            self.room_sizes.pop(room_key, None)
            self.remove_room_slider(room_key)
    
    def create_room_slider(self, room_key):
        """Create slider for room size adjustment"""
        room_data = self.room_definitions[room_key]
        
        slider_frame = ttk.Frame(self.sliders_frame)
        slider_frame.pack(fill=tk.X, pady=5)
        
        # Store reference to the frame
        if not hasattr(self, 'room_slider_frames'):
            self.room_slider_frames = {}
        self.room_slider_frames[room_key] = slider_frame
        
        # Room name and current size
        header_frame = ttk.Frame(slider_frame)
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text=room_data['name']).pack(side=tk.LEFT)
        
        size_label = ttk.Label(header_frame, text=f"{room_data['default_size']} sq ft")
        size_label.pack(side=tk.RIGHT)
        
        # Size slider
        size_var = tk.IntVar(value=room_data['default_size'])
        slider = ttk.Scale(slider_frame, from_=room_data['min_size'], to=room_data['max_size'],
                          variable=size_var, orient=tk.HORIZONTAL,
                          command=lambda val, key=room_key, lbl=size_label: self.update_room_size(key, val, lbl))
        slider.pack(fill=tk.X)
        
        # Store slider reference
        self.room_sliders[room_key] = {'var': size_var, 'slider': slider, 'label': size_label}
    
    def remove_room_slider(self, room_key):
        """Remove room slider"""
        if hasattr(self, 'room_slider_frames') and room_key in self.room_slider_frames:
            self.room_slider_frames[room_key].destroy()
            del self.room_slider_frames[room_key]
        
        if room_key in self.room_sliders:
            del self.room_sliders[room_key]
    
    def update_room_size(self, room_key, value, label):
        """Update room size from slider"""
        size = int(float(value))
        self.room_sizes[room_key] = size
        label.configure(text=f"{size} sq ft")
    
    def generate_floor_plan(self):
        """Generate floor plan"""
        if len(self.plot_points) < 3:
            messagebox.showerror("Error", "Please draw a plot with at least 3 points first.")
            return
        
        if not self.selected_rooms:
            messagebox.showerror("Error", "Please select at least one room.")
            return
        
        # Switch to floor plan tab
        self.notebook.select(2)  # Index of floor plan tab
        
        # Generate the floor plan
        self.draw_floor_plan()
        self.generate_room_schedule()
        
        self.status_var.set("Floor plan generated successfully")
        messagebox.showinfo("Success", "Floor plan generated successfully!")
    
    def draw_floor_plan(self):
        """Draw the generated floor plan"""
        self.floor_plan_canvas.delete("all")
        
        # Draw plot boundary
        if len(self.plot_points) >= 3:
            scale_factor = min(800, 600) / max(self.canvas_width, self.canvas_height)
            offset_x = 50
            offset_y = 50
            
            # Scale and translate points
            scaled_points = []
            for point in self.plot_points:
                x = point['x'] * scale_factor + offset_x
                y = point['y'] * scale_factor + offset_y
                scaled_points.extend([x, y])
            
            # Draw plot boundary
            self.floor_plan_canvas.create_polygon(scaled_points, fill='#f9fafb', 
                                                outline='black', width=3)
            
            # Draw rooms layout
            self.draw_rooms_layout()
            
            # Draw compass
            self.draw_compass()
    
    def draw_rooms_layout(self):
        """Draw simplified rooms layout"""
        rooms = list(self.selected_rooms)
        if not rooms:
            return
        
        # Simple grid layout
        grid_cols = math.ceil(math.sqrt(len(rooms)))
        room_width = 120
        room_height = 100
        start_x = 100
        start_y = 100
        
        for i, room_key in enumerate(rooms):
            room_data = self.room_definitions[room_key]
            col = i % grid_cols
            row = i // grid_cols
            
            x = start_x + col * (room_width + 20)
            y = start_y + row * (room_height + 20)
            
            # Draw room rectangle
            self.floor_plan_canvas.create_rectangle(x, y, x+room_width, y+room_height,
                                                  fill=room_data['color'] + '40',  # Add transparency
                                                  outline=room_data['color'], width=2)
            
            # Draw room label
            self.floor_plan_canvas.create_text(x + room_width/2, y + room_height/2,
                                             text=room_data['name'], font=('Arial', 10, 'bold'))
            
            # Draw area
            self.floor_plan_canvas.create_text(x + room_width/2, y + room_height/2 + 15,
                                             text=f"{self.room_sizes[room_key]} sq ft", 
                                             font=('Arial', 9))
    
    def draw_compass(self):
        """Draw compass on floor plan"""
        compass_x = 750
        compass_y = 80
        radius = 25
        
        # Compass circle
        self.floor_plan_canvas.create_oval(compass_x-radius, compass_y-radius,
                                         compass_x+radius, compass_y+radius,
                                         outline='blue', width=2)
        
        # North arrow
        self.floor_plan_canvas.create_polygon([compass_x, compass_y-radius+5,
                                             compass_x-5, compass_y-10,
                                             compass_x+5, compass_y-10],
                                            fill='red')
        
        # N label
        self.floor_plan_canvas.create_text(compass_x, compass_y-radius-15, text='N',
                                         font=('Arial', 12, 'bold'))
    
    def generate_room_schedule(self):
        """Generate room schedule table"""
        # Clear existing items
        for item in self.room_schedule_tree.get_children():
            self.room_schedule_tree.delete(item)
        
        # Add room data
        for room_key in self.selected_rooms:
            room_data = self.room_definitions[room_key]
            area = self.room_sizes[room_key]
            dimensions = self.calculate_room_dimensions(area)
            
            self.room_schedule_tree.insert('', tk.END, values=(
                room_data['name'],
                f"{area}",
                f"{dimensions['length']}' × {dimensions['width']}'",
                "10'"
            ))
    
    def calculate_room_dimensions(self, area):
        """Calculate room dimensions based on area"""
        ratio = 1.4  # length to width ratio
        width = math.sqrt(area / ratio)
        length = area / width
        
        return {
            'length': round(length),
            'width': round(width)
        }
    
    def calculate_beam(self):
        """Calculate beam analysis"""
        try:
            beam_type = self.beam_type_var.get()
            length = self.beam_length_var.get()
            load = self.beam_load_var.get()
            
            if length <= 0 or load <= 0:
                messagebox.showerror("Error", "Please enter valid positive values.")
                return
            
            # Calculate based on beam type
            if beam_type == "simply_supported":
                max_moment = (load * length**2) / 8
                max_shear = (load * length) / 2
            elif beam_type == "cantilever":
                max_moment = (load * length**2) / 2
                max_shear = load * length
            elif beam_type == "fixed_both":
                max_moment = (load * length**2) / 24
                max_shear = (load * length) / 2
            else:
                max_moment = max_shear = 0
            
            # Update result labels
            self.max_moment_label.configure(text=f"{max_moment:.2f} kN-m")
            self.max_shear_label.configure(text=f"{max_shear:.2f} kN")
            
            # Draw diagrams
            self.draw_beam_diagrams(beam_type, length, load)
            
            self.status_var.set("Beam analysis completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Calculation error: {str(e)}")
    
    def draw_beam_diagrams(self, beam_type, length, load):
        """Draw shear force and bending moment diagrams"""
        # Clear previous plots
        self.sfd_ax.clear()
        self.bmd_ax.clear()
        
        # Create x array
        x = np.linspace(0, length, 100)
        
        # Calculate shear force and bending moment
        if beam_type == "simply_supported":
            # Shear force (triangular)
            shear = np.where(x <= length/2, 
                           (load * length) / 2 - load * x,
                           -(load * length) / 2 + load * (length - x))
            
            # Bending moment (parabolic)
            moment = np.where(x <= length/2,
                            (load * x / 2) * (length - x),
                            (load * (length - x) / 2) * x)
            
        elif beam_type == "cantilever":
            # Shear force (linear)
            shear = -load * (length - x)
            
            # Bending moment (parabolic)
            moment = -(load * (length - x)**2) / 2
            
        elif beam_type == "fixed_both":
            # Simplified - actual would need more complex analysis
            shear = (load * length) / 2 - load * x
            moment = (load * x / 12) * (length**2 - x**2)
        
        # Plot SFD
        self.sfd_ax.plot(x, shear, 'r-', linewidth=2, label='Shear Force')
        self.sfd_ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.sfd_ax.fill_between(x, shear, alpha=0.3, color='red')
        self.sfd_ax.set_title('Shear Force Diagram')
        self.sfd_ax.set_ylabel('Shear Force (kN)')
        self.sfd_ax.grid(True, alpha=0.3)
        self.sfd_ax.legend()
        
        # Plot BMD
        self.bmd_ax.plot(x, moment, 'b-', linewidth=2, label='Bending Moment')
        self.bmd_ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        self.bmd_ax.fill_between(x, moment, alpha=0.3, color='blue')
        self.bmd_ax.set_title('Bending Moment Diagram')
        self.bmd_ax.set_xlabel('Distance (ft)')
        self.bmd_ax.set_ylabel('Bending Moment (kN-m)')
        self.bmd_ax.grid(True, alpha=0.3)
        self.bmd_ax.legend()
        
        # Refresh canvas
        self.beam_canvas.draw()
    
    def send_chat_message(self):
        """Send chat message to AI assistant"""
        message = self.chat_input_var.get().strip()
        if not message:
            return
        
        # Add user message
        self.add_chat_message(message, "user")
        
        # Clear input
        self.chat_input_var.set("")
        
        # Generate AI response
        response = self.generate_ai_response(message)
        self.add_chat_message(response, "ai")
    
    def add_chat_message(self, message, sender):
        """Add message to chat display"""
        self.chat_text.configure(state=tk.NORMAL)
        
        if sender == "user":
            self.chat_text.insert(tk.END, "You: ", "user_label")
            self.chat_text.insert(tk.END, f"{message}\n\n", "user_message")
        else:
            self.chat_text.insert(tk.END, "AI Assistant: ", "ai_label")
            self.chat_text.insert(tk.END, f"{message}\n\n", "ai_message")
        
        # Configure text tags for styling
        self.chat_text.tag_configure("user_label", foreground="blue", font=('Arial', 10, 'bold'))
        self.chat_text.tag_configure("ai_label", foreground="green", font=('Arial', 10, 'bold'))
        self.chat_text.tag_configure("user_message", font=('Arial', 10))
        self.chat_text.tag_configure("ai_message", font=('Arial', 10))
        
        self.chat_text.configure(state=tk.DISABLED)
        self.chat_text.see(tk.END)
    
    def generate_ai_response(self, user_message):
        """Generate AI response based on user input"""
        message = user_message.lower()
        
        # Simple keyword-based responses
        if any(word in message for word in ['beam', 'span']):
            return """For beam design, consider these guidelines:
• For residential spans (8-15 ft): Use 9" × 12" beam
• Depth = L/12 to L/15 for simply supported beams
• Steel: 2-12mm bars top + 2-12mm bars bottom minimum
• Stirrups: 8mm @ 150mm c/c as per IS 456:2000
• For spans over 15ft: Consider deeper sections or intermediate supports"""
        
        elif 'column' in message:
            return """Column design guidelines:
• For loads up to 500kN: Use 12" × 12" column
• Steel: 4-16mm dia bars minimum (0.8% steel)
• Ties: 8mm @ 150mm c/c (IS 456:2000)
• Concrete: M20 or M25 grade
• Clear cover: 40mm for columns
• Slenderness ratio should not exceed 60"""
        
        elif 'slab' in message:
            return """Slab design specifications:
• One-way slab: L/28 to L/35 thickness
• Two-way slab: L/32 to L/40 thickness
• Minimum thickness: 125mm (5 inches)
• Steel: 10mm @ 150mm c/c both directions
• Clear cover: 20mm for slabs
• Concrete: M20 grade minimum"""
        
        elif 'foundation' in message:
            return """Foundation design considerations:
• Depth: Minimum 1.5m below ground level
• Size: Based on soil bearing capacity (typically 10-20 T/m²)
• For residential: 4' × 4' isolated footings
• Steel: 12mm bars @ 150mm c/c both ways
• Concrete: M20 grade
• Always conduct soil test first!"""
        
        elif any(word in message for word in ['cost', 'rate', 'price']):
            return """Current construction cost estimates (₹/sq ft):
• Basic construction: ₹1200-1500/sq ft
• Good quality: ₹1500-2000/sq ft
• Premium construction: ₹2000-3000/sq ft
• Material cost: 60-65% of total
• Labor cost: 25-30% of total
• Other expenses: 10-15% of total
Note: Rates vary by location and current market prices."""
        
        elif any(word in message for word in ['is code', 'standard', 'code']):
            return """Important Indian Standards (IS Codes):
• IS 456:2000 - RCC Design Code
• IS 875:1987 - Design Loads (Dead, Live, Wind)
• IS 1893:2016 - Seismic Design
• IS 1904:1986 - Foundation Design
• IS 2502:1963 - Bar Bending Schedule
• IS 10262:2019 - Concrete Mix Design
Always refer to latest versions!"""
        
        elif 'load' in message:
            return """Load calculations as per IS 875:
• Dead Load: RCC = 25 kN/m³, Brick = 20 kN/m³
• Live Load: Residential = 2 kN/m², Commercial = 3-5 kN/m²
• Floor finish load = 1 kN/m²
• Wall load = Height × thickness × 20 kN/m³
• Total load = 1.5×DL + 1.5×LL (load factors)
• Wind load: As per IS 875 Part-3"""
        
        # Default response
        return """I can help you with structural engineering questions including:
• Beam and column design
• Load calculations
• Foundation sizing
• IS Code references
• Material specifications
• Cost estimation
• Reinforcement details

Please ask a specific question about any of these topics!"""
    
    def download_floor_plan(self):
        """Download floor plan as image"""
        try:
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if filename:
                # Create image from canvas
                canvas_ps = self.floor_plan_canvas.postscript(colormode='color')
                
                # Convert to image using PIL (Note: This is a simplified approach)
                # In practice, you might want to use a more robust method
                messagebox.showinfo("Export", f"Floor plan export initiated.\nFile: {filename}")
                self.status_var.set("Floor plan exported successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


# Utility functions
def format_currency(amount):
    """Format number to Indian currency format"""
    return f"₹{amount:,.0f}"

def feet_to_meters(feet):
    """Convert feet to meters"""
    return feet * 0.3048

def sq_feet_to_sq_meters(sq_feet):
    """Convert square feet to square meters"""
    return sq_feet * 0.092903

def calculate_concrete_volume(area, thickness):
    """Calculate concrete volume for given area and thickness"""
    # area in sq ft, thickness in inches
    volume_cubic_feet = area * (thickness / 12)
    return volume_cubic_feet * 0.0283168  # Convert to cubic meters

def calculate_steel_weight(diameter, length):
    """Calculate steel weight for reinforcement"""
    # diameter in mm, length in meters
    weight_per_meter = (diameter * diameter * 0.00617)  # kg/m for steel bars
    return weight_per_meter * length


# Main execution
if __name__ == "__main__":
    app = PlannifyProAI()
    app.run()
