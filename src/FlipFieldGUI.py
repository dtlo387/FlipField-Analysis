#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import json
import platform
from tkinter import font as tkFont

# Import the analysis module
try:
    from AnalyzingFlipField import run_gui_analysis
except ImportError:
    print("Warning: AnalyzingFlipField module not found")
    run_gui_analysis = None



class FlipFieldGUI:
    """Main GUI application."""
    
    def __init__(self, root):
        self.root = root
        self.selected_input_file = None
        self.selected_output_dir = None
        self.is_running = False
        
        # Platform detection for keyboard shortcuts
        self.is_mac = platform.system() == 'Darwin'
        self.cmd_key = "Cmd" if self.is_mac else "Ctrl"
        
        # Settings for export, analysis, and UI state
        self.settings = {
            # Export settings
            'export_txt': False,
            'export_csv': False,
            'export_summary': True,
            # Analysis settings
            'analysis_start_seconds': 3.0,  # Default equivalent to ~80 frames
            'analysis_end_seconds': 3.0,    # Default equivalent to ~82 frames  
            'min_movement_pixels': 2.0,
            # UI state
            'window_width': 600,
            'window_height': 400,
            'window_x': None,
            'window_y': None,
            'last_input_dir': '',
            'last_output_dir': '',
            'recent_files': []
        }
        
        # Load settings from config file
        self.load_settings()
        
        self.setup_window()
        self.setup_menu()
        self.setup_ui()
        self.setup_keyboard_shortcuts()
        self.setup_drag_drop()
    
    def load_settings(self):
        """Load settings from config file if it exists."""
        config_file = os.path.join(os.path.expanduser("~"), ".flipfield_config.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"Could not load settings: {e}")
    
    def save_settings(self):
        """Save settings to config file."""
        # Update window state before saving
        try:
            self.settings['window_width'] = self.root.winfo_width()
            self.settings['window_height'] = self.root.winfo_height()
            self.settings['window_x'] = self.root.winfo_x()
            self.settings['window_y'] = self.root.winfo_y()
        except:
            pass  # Ignore if window is being destroyed
            
        config_file = os.path.join(os.path.expanduser("~"), ".flipfield_config.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Could not save settings: {e}")
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title("FlipField Analysis")
        
        # Restore window size and position
        width = self.settings.get('window_width', 600)
        height = self.settings.get('window_height', 400)
        x = self.settings.get('window_x')
        y = self.settings.get('window_y')
        
        if x is not None and y is not None:
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.root.geometry(f"{width}x{height}")
            self.center_window()
        
        self.root.minsize(600, 400)  # Set minimum window size
        self.root.resizable(True, True)
        
        # Set app icon for title bar and dock
        try:
            # Try .icns file first (macOS preferred)
            icon_path = os.path.join(os.path.dirname(__file__), "FlipField.icns")
            if os.path.exists(icon_path):
                # Use wm_iconbitmap for better macOS support
                self.root.wm_iconbitmap(icon_path)
            else:
                # Fallback to PNG icon
                png_icon_path = os.path.join(os.path.dirname(__file__), "FlipField_256x256.png")
                if os.path.exists(png_icon_path):
                    icon_img = tk.PhotoImage(file=png_icon_path)
                    self.root.iconphoto(True, icon_img)
                    # Keep a reference to prevent garbage collection
                    self.root.icon_img = icon_img
        except Exception as e:
            print(f"Could not load app icon: {e}")
    
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File...", command=self.browse_input_file, 
                             accelerator=f"{self.cmd_key}+O")
        file_menu.add_command(label="Open Output Folder...", command=self.browse_output_folder,
                             accelerator=f"{self.cmd_key}+Shift+O")
        file_menu.add_separator()
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, 
                             accelerator=f"{self.cmd_key}+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Settings...", command=self.open_settings,
                             accelerator=f"{self.cmd_key}+,")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Recent Files", command=self.clear_recent_files)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Reset Window Size", command=self.reset_window_size)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About FlipField", command=self.show_about)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts."""
        if self.is_mac:
            self.root.bind('<Command-o>', lambda e: self.browse_input_file())
            self.root.bind('<Command-O>', lambda e: self.browse_output_folder())
            self.root.bind('<Command-r>', lambda e: self.start_analysis())
            self.root.bind('<Command-comma>', lambda e: self.open_settings())
            self.root.bind('<Command-q>', lambda e: self.on_closing())
        else:
            self.root.bind('<Control-o>', lambda e: self.browse_input_file())
            self.root.bind('<Control-O>', lambda e: self.browse_output_folder())
            self.root.bind('<Control-r>', lambda e: self.start_analysis())
            self.root.bind('<Control-comma>', lambda e: self.open_settings())
            self.root.bind('<Control-q>', lambda e: self.on_closing())
        
        self.root.bind('<F5>', lambda e: self.start_analysis())
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality."""
        # Note: Basic drag and drop support - may vary by platform
        # For now, we'll rely on the file dialog and recent files functionality
        # Advanced drag and drop would require additional libraries like tkdnd
        pass
    
    def on_drop_enter(self, event):
        """Handle drag enter event."""
        pass
    
    def on_drop_leave(self, event):
        """Handle drag leave event."""
        pass
    
    def on_drop(self, event):
        """Handle file drop event."""
        # This would be implemented with a proper drag and drop library
        pass
    
    def center_window(self):
        """Center the main window on screen."""
        self.root.update_idletasks()
        width = self.settings.get('window_width', 600)
        height = self.settings.get('window_height', 400)
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def add_recent_file(self, file_path):
        """Add a file to the recent files list."""
        if file_path in self.settings['recent_files']:
            self.settings['recent_files'].remove(file_path)
        
        self.settings['recent_files'].insert(0, file_path)
        
        # Keep only the last 10 files
        if len(self.settings['recent_files']) > 10:
            self.settings['recent_files'] = self.settings['recent_files'][:10]
        
        self.update_recent_menu()
        self.save_settings()
    
    def update_recent_menu(self):
        """Update the recent files menu."""
        self.recent_menu.delete(0, 'end')
        
        if not self.settings['recent_files']:
            self.recent_menu.add_command(label="No recent files", state='disabled')
        else:
            for i, file_path in enumerate(self.settings['recent_files']):
                if os.path.exists(file_path):
                    display_name = f"{i+1}. {os.path.basename(file_path)}"
                    self.recent_menu.add_command(label=display_name, 
                                               command=lambda fp=file_path: self.open_recent_file(fp))
    
    def open_recent_file(self, file_path):
        """Open a recent file."""
        if os.path.exists(file_path):
            self.selected_input_file = file_path
            display_path = self.truncate_path(file_path)
            self.input_path_label.configure(text=display_path, fg='black')
            
            # Remember the directory for next time
            self.settings['last_input_dir'] = os.path.dirname(file_path)
            self.save_settings()
            
            # Add to recent files
            self.add_recent_file(file_path)
        else:
            self.update_status(f"File not found: {os.path.basename(file_path)}", error=True)
            # Remove from recent files
            if file_path in self.settings['recent_files']:
                self.settings['recent_files'].remove(file_path)
                self.update_recent_menu()
                self.save_settings()
    
    def clear_recent_files(self):
        """Clear the recent files list."""
        self.settings['recent_files'] = []
        self.update_recent_menu()
        self.save_settings()
    
    def reset_window_size(self):
        """Reset window to default size and center it."""
        self.root.geometry("600x400")
        self.center_window()
    
    def show_about(self):
        """Show about dialog."""
        about_text = """FlipField Analysis

Features:
• Flip detection algorithms
• Customizable analysis parameters  
• Multiple export formats
• Recent files support

Author: Daniel Lo
Version: 2.0"""
        
        messagebox.showinfo("About FlipField", about_text)
    
    def is_valid_tracking_file(self, file_path):
        """Check if the file appears to be a valid tracking data file."""
        try:
            with open(file_path, 'r') as f:
                # Read first few lines
                lines = [f.readline().strip() for _ in range(5)]
                
                # Check for expected column headers or data patterns
                header_keywords = ['frame', 'position', 'angle', 'x', 'y']
                first_line = lines[0].lower() if lines else ''
                
                # Look for tracking data patterns
                has_header = any(keyword in first_line for keyword in header_keywords)
                
                # Check for numeric data in subsequent lines
                has_numeric_data = False
                for line in lines[1:]:
                    if line and any(char.isdigit() for char in line):
                        has_numeric_data = True
                        break
                
                return has_header or has_numeric_data
                
        except Exception:
            return False
    
    def setup_ui(self):
        """Setup the user interface."""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=40, pady=35)
        
        # Configure main_frame to expand properly
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Input file section
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill='x', pady=(0, 25))
        
        tk.Label(input_frame, text="Choose Input File:", font=('SF Pro', 12, 'bold')).pack(anchor='w', pady=(0, 8))
        
        input_row = tk.Frame(input_frame)
        input_row.pack(fill='x', pady=(0, 0))
        
        # Frame with border for file path - make it accept drops
        path_frame = tk.Frame(input_row, relief='solid', bd=1, bg='white')
        path_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.input_path_label = tk.Label(path_frame, text="No file selected", 
                                        font=('SF Pro', 12), anchor='w', fg='gray', 
                                        bg='white', padx=8, pady=4)
        self.input_path_label.pack(fill='both', expand=True)
        
        self.input_browse_btn = tk.Button(input_row, text="Browse", 
                                         command=self.browse_input_file,
                                         font=('SF Pro', 12), width=10,
                                         relief='solid', bd=1)
        self.input_browse_btn.pack(side='right')
        
        # Output folder section
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill='x', pady=(0, 25))
        
        tk.Label(output_frame, text="Choose Output Folder:", font=('SF Pro', 12, 'bold')).pack(anchor='w', pady=(0, 8))
        
        output_row = tk.Frame(output_frame)
        output_row.pack(fill='x', pady=(0, 0))
        
        # Frame with border for output path - make it accept drops
        output_path_frame = tk.Frame(output_row, relief='solid', bd=1, bg='white')
        output_path_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        self.output_path_label = tk.Label(output_path_frame, text="No folder selected", 
                                         font=('SF Pro', 12), anchor='w', fg='gray',
                                         bg='white', padx=8, pady=4)
        self.output_path_label.pack(fill='both', expand=True)
        
        self.output_browse_btn = tk.Button(output_row, text="Browse",
                                          command=self.browse_output_folder,
                                          font=('SF Pro', 12), width=10,
                                          relief='solid', bd=1)
        self.output_browse_btn.pack(side='right')
        
        # Video length section
        video_frame = tk.Frame(main_frame)
        video_frame.pack(fill='x', pady=(0, 35))
        
        tk.Label(video_frame, text="Video Length:", font=('SF Pro', 12, 'bold')).pack(anchor='w', pady=(0, 8))
        
        time_input_frame = tk.Frame(video_frame)
        time_input_frame.pack(anchor='w', pady=(0, 0))
        
        self.minutes_var = tk.IntVar()
        self.seconds_var = tk.IntVar()
        
        tk.Spinbox(time_input_frame, from_=0, to=10, increment=1,
                  textvariable=self.minutes_var, width=5,
                  font=('SF Pro', 12)).pack(side='left')
        tk.Label(time_input_frame, text="min", font=('SF Pro', 12)).pack(side='left', padx=(5, 15))
        
        tk.Spinbox(time_input_frame, from_=0, to=59, increment=1,
                  textvariable=self.seconds_var, width=5,
                  font=('SF Pro', 12)).pack(side='left')
        tk.Label(time_input_frame, text="sec", font=('SF Pro', 12)).pack(side='left', padx=(5, 0))
        
        # Action buttons (same vertical level, separate frames, toward center)
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(30, 0))
        
        # Configure button frame for proper spacing
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Settings button (left side, toward center)
        self.settings_btn = tk.Button(button_frame, text="Settings",
                                     command=self.open_settings,
                                     font=('SF Pro', 12),
                                     relief='solid', bd=1)
        self.settings_btn.grid(row=0, column=0, sticky='e', padx=(0, 15))
        
        # Analyze button (right side, toward center)
        self.analyze_btn = tk.Button(button_frame, text="Analyze",
                                    command=self.start_analysis,
                                    font=('SF Pro', 12),
                                    relief='solid', bd=1)
        self.analyze_btn.grid(row=0, column=1, sticky='w', padx=(15, 0))

    def truncate_path(self, path, max_length=40):
        """Truncate long paths with ... in the middle."""
        if len(path) <= max_length:
            return path
        
        # Show beginning and end with ... in middle
        start_len = max_length // 2 - 2
        end_len = max_length - start_len - 3
        return f"{path[:start_len]}...{path[-end_len:]}"
    
    def browse_input_file(self):
        """Handle input file selection."""
        # Use last input directory if available
        initial_dir = self.settings.get('last_input_dir', '')
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")
        
        file_path = filedialog.askopenfilename(
            title="Select tracking data file",
            initialdir=initial_dir,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_input_file = file_path
            display_path = self.truncate_path(file_path)
            self.input_path_label.configure(text=display_path, fg='black')
            
            # Remember the directory for next time
            self.settings['last_input_dir'] = os.path.dirname(file_path)
            self.save_settings()
            
            # Add to recent files
            self.add_recent_file(file_path)
    
    def browse_output_folder(self):
        """Handle output folder selection."""
        # Use last output directory if available
        initial_dir = self.settings.get('last_output_dir', '')
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")
            
        folder_path = filedialog.askdirectory(
            title="Select output folder",
            initialdir=initial_dir
        )
        
        if folder_path:
            self.selected_output_dir = folder_path
            display_path = self.truncate_path(folder_path)
            self.output_path_label.configure(text=display_path, fg='black')
            
            # Remember the directory for next time
            self.settings['last_output_dir'] = folder_path
            self.save_settings()
    
    def open_settings(self):
        """Open the unified settings window with export and analysis options."""
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return
            
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("FlipField Settings")
        self.settings_window.geometry("550x550")
        self.settings_window.resizable(False, False)
        
        # Set app icon for settings window
        try:
            # Try .icns file first (macOS preferred)
            icon_path = os.path.join(os.path.dirname(__file__), "FlipField.icns")
            if os.path.exists(icon_path):
                self.settings_window.wm_iconbitmap(icon_path)
            else:
                # Fallback to PNG icon
                png_icon_path = os.path.join(os.path.dirname(__file__), "FlipField_256x256.png")
                if os.path.exists(png_icon_path):
                    icon_img = tk.PhotoImage(file=png_icon_path)
                    self.settings_window.iconphoto(True, icon_img)
                    # Keep a reference to prevent garbage collection
                    self.settings_window.icon_img = icon_img
        except Exception as e:
            print(f"Could not load settings window icon: {e}")
        
        # Make it modal
        self.settings_window.transient(self.root)
        self.settings_window.grab_set()
        
        # Center the window
        self.center_settings_window()
        
        main_frame = tk.Frame(self.settings_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="FlipField Settings", 
                              font=('SF Pro', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Export Options Section
        export_section = tk.LabelFrame(main_frame, text="Export Options", 
                                     font=('SF Pro', 13, 'bold'), padx=10, pady=10)
        export_section.pack(fill='x', pady=(0, 15))
        
        # CSV export option
        csv_frame = tk.Frame(export_section)
        csv_frame.pack(fill='x', pady=2)
        
        self.export_csv_var = tk.BooleanVar(value=self.settings['export_csv'])
        csv_check = tk.Checkbutton(csv_frame, text="Export CSV files", 
                                  variable=self.export_csv_var,
                                  font=('SF Pro', 12))
        csv_check.pack(side='left')
        
        csv_help = tk.Label(csv_frame, text="ⓘ", font=('SF Pro', 10), fg='blue')
        csv_help.pack(side='left', padx=(5, 0))
        self.create_tooltip(csv_help, "Export CSV file for debugging.")
        
        # TXT export option
        txt_frame = tk.Frame(export_section)
        txt_frame.pack(fill='x', pady=2)
        
        self.export_txt_var = tk.BooleanVar(value=self.settings['export_txt'])
        txt_check = tk.Checkbutton(txt_frame, text="Export TXT files", 
                                  variable=self.export_txt_var,
                                  font=('SF Pro', 12))
        txt_check.pack(side='left')
        
        txt_help = tk.Label(txt_frame, text="ⓘ", font=('SF Pro', 10), fg='blue')
        txt_help.pack(side='left', padx=(5, 0))
        self.create_tooltip(txt_help, "Export TXT file for debugging.")
        
        # Summary export option
        summary_frame = tk.Frame(export_section)
        summary_frame.pack(fill='x', pady=2)
        
        self.export_summary_var = tk.BooleanVar(value=self.settings['export_summary'])
        summary_check = tk.Checkbutton(summary_frame, text="Export Flip Summary", 
                                      variable=self.export_summary_var,
                                      font=('SF Pro', 12))
        summary_check.pack(side='left')
        
        summary_help = tk.Label(summary_frame, text="ⓘ", font=('SF Pro', 10), fg='blue')
        summary_help.pack(side='left', padx=(5, 0))
        self.create_tooltip(summary_help, "Export simplified flip summary showing results by magnetic field strength (recommended)")
        
        # Advanced Analysis Section
        analysis_section = tk.LabelFrame(main_frame, text="Advanced Analysis Parameters", 
                                       font=('SF Pro', 13, 'bold'), padx=10, pady=10)
        analysis_section.pack(fill='x', pady=(0, 15))
        
        # Start skip time
        start_frame = tk.Frame(analysis_section)
        start_frame.pack(fill='x', pady=5)
        
        tk.Label(start_frame, text="Skip at start (seconds):", 
                font=('SF Pro', 12)).pack(side='left')
        
        # Create tooltip for start skip
        start_help = tk.Label(start_frame, text="ⓘ", font=('SF Pro', 10), fg='blue')
        start_help.pack(side='right', padx=(5, 0))
        self.create_tooltip(start_help, "Number of seconds to skip at the beginning of the video to avoid false positives")
        
        self.start_seconds_var = tk.DoubleVar(value=self.settings['analysis_start_seconds'])
        start_spinbox = tk.Spinbox(start_frame, from_=0, to=10, increment=0.5, 
                                  textvariable=self.start_seconds_var, width=8,
                                  font=('SF Pro', 12))
        start_spinbox.pack(side='right', padx=(10, 0))
        
        # End skip time
        end_frame = tk.Frame(analysis_section)
        end_frame.pack(fill='x', pady=5)
        
        tk.Label(end_frame, text="Skip at end (seconds):", 
                font=('SF Pro', 12)).pack(side='left')
        
        end_help = tk.Label(end_frame, text="ⓘ", font=('SF Pro', 10), fg='blue')
        end_help.pack(side='right', padx=(5, 0))
        self.create_tooltip(end_help, "Number of seconds to skip at the end of the video to avoid false positives")
        
        self.end_seconds_var = tk.DoubleVar(value=self.settings['analysis_end_seconds'])
        end_spinbox = tk.Spinbox(end_frame, from_=0, to=10, increment=0.5,
                                textvariable=self.end_seconds_var, width=8,
                                font=('SF Pro', 12))
        end_spinbox.pack(side='right', padx=(10, 0))
        
        # Minimum movement
        movement_frame = tk.Frame(analysis_section)
        movement_frame.pack(fill='x', pady=5)
        
        tk.Label(movement_frame, text="Minimum Movement (pixels):", 
                font=('SF Pro', 12)).pack(side='left')
        
        movement_help = tk.Label(movement_frame, text="ⓘ", font=('SF Pro', 10), fg='blue')
        movement_help.pack(side='right', padx=(5, 0))
        self.create_tooltip(movement_help, "Minimum pixel movement per frame required to detect a bead flip. Lower = more sensitive")
        
        self.movement_var = tk.DoubleVar(value=self.settings['min_movement_pixels'])
        movement_spinbox = tk.Spinbox(movement_frame, from_=0.1, to=5.0, increment=0.1,
                                     textvariable=self.movement_var, width=8,
                                     font=('SF Pro', 12))
        movement_spinbox.pack(side='right', padx=(10, 0))
        
        # Reset defaults button
        reset_frame = tk.Frame(analysis_section)
        reset_frame.pack(fill='x', pady=(10, 0))
        
        reset_btn = tk.Button(reset_frame, text="Reset Analysis Defaults", 
                             command=self.reset_analysis_defaults,
                             font=('SF Pro', 12),
                             relief='solid', bd=1)
        reset_btn.pack(side='right')
        
        # Main buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=self.settings_window.destroy,
                              font=('SF Pro', 13),
                              relief='solid', bd=1)
        cancel_btn.pack(side='right', padx=(10, 0))
        
        ok_btn = tk.Button(button_frame, text="Save", 
                          command=self.save_all_settings,
                          font=('SF Pro', 13),
                          relief='solid', bd=1)
        ok_btn.pack(side='right')
    
    def center_settings_window(self):
        """Center the settings window."""
        self.settings_window.update_idletasks()
        x = (self.settings_window.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.settings_window.winfo_screenheight() // 2) - (550 // 2)
        self.settings_window.geometry(f"550x550+{x}+{y}")
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root+10}")
            
            # Create frame with border for better visibility
            frame = tk.Frame(tooltip, background="black", relief="solid", bd=1)
            frame.pack()
            
            label = tk.Label(frame, text=text, 
                           background="lightyellow", 
                           foreground="black",
                           font=('SF Pro', 11, 'normal'), 
                           wraplength=250,
                           padx=8, pady=6,
                           justify="left")
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def reset_analysis_defaults(self):
        """Reset analysis parameters to default values."""
        self.start_seconds_var.set(3.0)
        self.end_seconds_var.set(3.0)
        self.movement_var.set(2.0)
    
    def save_all_settings(self):
        """Save all settings and close the settings window."""
        # Validate inputs
        try:
            start_val = self.start_seconds_var.get()
            end_val = self.end_seconds_var.get()
            movement_val = self.movement_var.get()
            
            # Validation
            if not (0 <= start_val <= 10):
                raise ValueError("Start skip time must be between 0-10 seconds")
            if not (0 <= end_val <= 10):
                raise ValueError("End skip time must be between 0-10 seconds")
            if not (0.1 <= movement_val <= 5):
                raise ValueError("Minimum movement must be between 0.1-5 pixels")
            
            # Save settings
            self.settings['export_csv'] = self.export_csv_var.get()
            self.settings['export_txt'] = self.export_txt_var.get()
            self.settings['export_summary'] = self.export_summary_var.get()
            self.settings['analysis_start_seconds'] = start_val
            self.settings['analysis_end_seconds'] = end_val
            self.settings['min_movement_pixels'] = movement_val
            
            # Save to config file
            self.save_settings()
            
            self.settings_window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
    
    def get_video_length_minutes(self):
        """Convert minutes and seconds to total minutes."""
        try:
            minutes = float(self.minutes_var.get())
            seconds = float(self.seconds_var.get())
            return minutes + (seconds / 60.0)
        except (ValueError, tk.TclError):
            return None
    
    def start_analysis(self):
        """Start the analysis process."""
        # Validation
        if not self.selected_input_file:
            messagebox.showerror("Error", "Please select an input file!")
            return
        
        if not self.selected_output_dir:
            messagebox.showerror("Error", "Please select an output folder!")
            return
        
        video_length = self.get_video_length_minutes()
        if video_length is None or video_length <= 0:
            messagebox.showerror("Error", "Please enter a valid video length!")
            return
        
        if not run_gui_analysis:
            messagebox.showerror("Error", "Analysis module not available!")
            return
        
        # Update UI
        self.is_running = True
        self.analyze_btn.configure(state='disabled', text="Analyzing...")
        
        # Start analysis in background thread
        thread = threading.Thread(target=self.run_analysis, args=(video_length,))
        thread.daemon = True
        thread.start()
    
    def run_analysis(self, video_length):
        """Run analysis in background thread."""
        try:
            # Run the analysis
            result = run_gui_analysis(
                file_path=self.selected_input_file,
                video_duration_min=video_length,
                frame_analysis_start_seconds=self.settings['analysis_start_seconds'],
                frame_analysis_end_seconds=self.settings['analysis_end_seconds'],
                min_position_change=self.settings['min_movement_pixels'],
                export_txt=self.settings['export_txt'],
                export_csv=self.settings['export_csv'],
                export_debug=False,
                export_summary=self.settings['export_summary'],
                output_dir=self.selected_output_dir
            )
            
            # Update UI on main thread
            self.root.after(0, self.analysis_complete, result)
            
        except Exception as e:
            self.root.after(0, self.analysis_error, str(e))
    
    def analysis_complete(self, result):
        """Handle analysis completion."""
        self.is_running = False
        self.analyze_btn.configure(state='normal', text="Analyze")
        
        success = result.get('success', False)
        summary_file = result.get('summary_file')
        
        if success:
            # Auto-open summary file if it exists
            if summary_file and os.path.exists(summary_file):
                try:
                    import subprocess
                    
                    # Open file with system default application
                    if self.is_mac:  # macOS
                        subprocess.run(['open', summary_file])
                    else:  # Windows
                        subprocess.run(['start', summary_file], shell=True)
                        
                except Exception as e:
                    # Fallback: show file path if opening fails
                    messagebox.showinfo("Analysis Complete", 
                                      f"Analysis completed successfully!\n\nSummary file created:\n{summary_file}\n\n(Could not auto-open file: {str(e)})")
            else:
                # No summary file to open
                messagebox.showinfo("Analysis Complete", 
                                  f"Analysis completed successfully!\nResults saved to:\n{self.selected_output_dir}")
        else:
            # Show error message
            error_msg = result.get('error', 'Unknown error')
            messagebox.showerror("Analysis Failed", f"Analysis failed: {error_msg}\n\nCheck the debug log file for details.")
    
    def analysis_error(self, error_msg):
        """Handle analysis error."""
        self.is_running = False
        self.analyze_btn.configure(state='normal', text="Analyze")
        messagebox.showerror("Error", f"Analysis failed:\n{error_msg}")

    def on_closing(self):
        """Handle window closing."""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Analysis is running. Do you want to quit anyway?"):
                self.save_settings()
                self.root.destroy()
        else:
            self.save_settings()
            self.root.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = FlipFieldGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main() 