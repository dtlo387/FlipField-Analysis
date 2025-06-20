#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import json

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
        
        # Settings for export and analysis
        self.settings = {
            # Export settings
            'export_txt': False,
            'export_csv': False,
            'export_summary': True,
            # Analysis settings
            'analysis_start_seconds': 3.0,  # Default equivalent to ~80 frames
            'analysis_end_seconds': 3.0,    # Default equivalent to ~82 frames  
            'min_movement_pixels': 2.0
        }
        
        # Load settings from config file
        self.load_settings()
        
        self.setup_window()
        self.setup_ui()
    
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
        config_file = os.path.join(os.path.expanduser("~"), ".flipfield_config.json")
        try:
            with open(config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Could not save settings: {e}")
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title("FlipField Analysis")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        self.center_window()
    
    def center_window(self):
        """Center the main window on screen."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"600x400+{x}+{y}")
    
    def setup_ui(self):
        """Setup the user interface."""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Input file section
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(input_frame, text="Choose Input File:", font=('SF Pro', 12)).pack(anchor='w')
        
        input_row = tk.Frame(input_frame)
        input_row.pack(fill='x', pady=(5, 0))
        
        # Frame with border for file path
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
        output_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(output_frame, text="Choose Output Folder:", font=('SF Pro', 12)).pack(anchor='w')
        
        output_row = tk.Frame(output_frame)
        output_row.pack(fill='x', pady=(5, 0))
        
        # Frame with border for output path
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
        video_frame.pack(fill='x', pady=(0, 30))
        
        tk.Label(video_frame, text="Video Length:", font=('SF Pro', 12)).pack(anchor='w')
        
        time_input_frame = tk.Frame(video_frame)
        time_input_frame.pack(anchor='w', pady=(5, 0))
        
        self.minutes_var = tk.StringVar()
        self.seconds_var = tk.StringVar()
        
        tk.Entry(time_input_frame, textvariable=self.minutes_var, width=5,
                font=('SF Pro', 12)).pack(side='left')
        tk.Label(time_input_frame, text="min", font=('SF Pro', 12)).pack(side='left', padx=(5, 15))
        
        tk.Entry(time_input_frame, textvariable=self.seconds_var, width=5,
                font=('SF Pro', 12)).pack(side='left')
        tk.Label(time_input_frame, text="sec", font=('SF Pro', 12)).pack(side='left', padx=(5, 0))
        
        # Action buttons (same vertical level, separate frames, toward center)
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        # Settings button (left side, toward center)
        self.settings_btn = tk.Button(button_frame, text="Settings",
                                     command=self.open_settings,
                                     font=('SF Pro', 12),
                                     relief='solid', bd=1)
        self.settings_btn.pack(side='left', padx=(80, 0))
        
        # Analyze button (right side, toward center)
        self.analyze_btn = tk.Button(button_frame, text="Analyze",
                                    command=self.start_analysis,
                                    font=('SF Pro', 12),
                                    relief='solid', bd=1)
        self.analyze_btn.pack(side='right', padx=(0, 80))
    
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
        file_path = filedialog.askopenfilename(
            title="Select tracking data file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_input_file = file_path
            display_path = self.truncate_path(file_path)
            self.input_path_label.configure(text=display_path, fg='black')
    
    def browse_output_folder(self):
        """Handle output folder selection."""
        folder_path = filedialog.askdirectory(title="Select output folder")
        
        if folder_path:
            self.selected_output_dir = folder_path
            display_path = self.truncate_path(folder_path)
            self.output_path_label.configure(text=display_path, fg='black')
    
    def open_settings(self):
        """Open the unified settings window with export and analysis options."""
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return
            
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("FlipField Settings")
        self.settings_window.geometry("500x500")
        self.settings_window.resizable(False, False)
        
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
                                     font=('SF Pro', 12, 'bold'), padx=10, pady=10)
        export_section.pack(fill='x', pady=(0, 15))
        
        self.export_csv_var = tk.BooleanVar(value=self.settings['export_csv'])
        csv_check = tk.Checkbutton(export_section, text="Export CSV files", 
                                  variable=self.export_csv_var,
                                  font=('SF Pro', 11))
        csv_check.pack(anchor='w', pady=2)
        
        self.export_txt_var = tk.BooleanVar(value=self.settings['export_txt'])
        txt_check = tk.Checkbutton(export_section, text="Export TXT files", 
                                  variable=self.export_txt_var,
                                  font=('SF Pro', 11))
        txt_check.pack(anchor='w', pady=2)
        
        self.export_summary_var = tk.BooleanVar(value=self.settings['export_summary'])
        summary_check = tk.Checkbutton(export_section, text="Export Flip Summary", 
                                      variable=self.export_summary_var,
                                      font=('SF Pro', 11))
        summary_check.pack(anchor='w', pady=2)
        
        # Advanced Analysis Section
        analysis_section = tk.LabelFrame(main_frame, text="Advanced Analysis Parameters", 
                                       font=('SF Pro', 12, 'bold'), padx=10, pady=10)
        analysis_section.pack(fill='x', pady=(0, 15))
        
        # Start skip time
        start_frame = tk.Frame(analysis_section)
        start_frame.pack(fill='x', pady=5)
        
        tk.Label(start_frame, text="Skip at start (seconds):", 
                font=('SF Pro', 11)).pack(side='left')
        
        # Create tooltip for start skip
        start_help = tk.Label(start_frame, text="ⓘ", font=('SF Pro', 10), fg='blue', cursor='hand2')
        start_help.pack(side='right', padx=(5, 0))
        self.create_tooltip(start_help, "Number of seconds to skip at the beginning of the video to avoid startup artifacts")
        
        self.start_seconds_var = tk.DoubleVar(value=self.settings['analysis_start_seconds'])
        start_spinbox = tk.Spinbox(start_frame, from_=0, to=10, increment=0.5, 
                                  textvariable=self.start_seconds_var, width=8,
                                  font=('SF Pro', 11))
        start_spinbox.pack(side='right', padx=(10, 0))
        
        # End skip time
        end_frame = tk.Frame(analysis_section)
        end_frame.pack(fill='x', pady=5)
        
        tk.Label(end_frame, text="Skip at end (seconds):", 
                font=('SF Pro', 11)).pack(side='left')
        
        end_help = tk.Label(end_frame, text="ⓘ", font=('SF Pro', 10), fg='blue', cursor='hand2')
        end_help.pack(side='right', padx=(5, 0))
        self.create_tooltip(end_help, "Number of seconds to skip at the end of the video to avoid ending artifacts")
        
        self.end_seconds_var = tk.DoubleVar(value=self.settings['analysis_end_seconds'])
        end_spinbox = tk.Spinbox(end_frame, from_=0, to=10, increment=0.5,
                                textvariable=self.end_seconds_var, width=8,
                                font=('SF Pro', 11))
        end_spinbox.pack(side='right', padx=(10, 0))
        
        # Minimum movement
        movement_frame = tk.Frame(analysis_section)
        movement_frame.pack(fill='x', pady=5)
        
        tk.Label(movement_frame, text="Minimum Movement (pixels):", 
                font=('SF Pro', 11)).pack(side='left')
        
        movement_help = tk.Label(movement_frame, text="ⓘ", font=('SF Pro', 10), fg='blue', cursor='hand2')
        movement_help.pack(side='right', padx=(5, 0))
        self.create_tooltip(movement_help, "Minimum pixel movement required to detect a bead flip. Lower = more sensitive")
        
        self.movement_var = tk.DoubleVar(value=self.settings['min_movement_pixels'])
        movement_entry = tk.Entry(movement_frame, textvariable=self.movement_var, 
                                 width=8, font=('SF Pro', 11))
        movement_entry.pack(side='right', padx=(10, 0))
        
        # Reset defaults button
        reset_frame = tk.Frame(analysis_section)
        reset_frame.pack(fill='x', pady=(10, 0))
        
        reset_btn = tk.Button(reset_frame, text="Reset Analysis Defaults", 
                             command=self.reset_analysis_defaults,
                             font=('SF Pro', 10))
        reset_btn.pack(side='right')
        
        # Main buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        cancel_btn = tk.Button(button_frame, text="Cancel", 
                              command=self.settings_window.destroy,
                              font=('SF Pro', 12))
        cancel_btn.pack(side='right', padx=(10, 0))
        
        ok_btn = tk.Button(button_frame, text="Save", 
                          command=self.save_all_settings,
                          font=('SF Pro', 12))
        ok_btn.pack(side='right')
    
    def center_settings_window(self):
        """Center the settings window."""
        self.settings_window.update_idletasks()
        x = (self.settings_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.settings_window.winfo_screenheight() // 2) - (500 // 2)
        self.settings_window.geometry(f"500x500+{x}+{y}")
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           font=('SF Pro', 9), wraplength=200)
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
            minutes = float(self.minutes_var.get() or 0)
            seconds = float(self.seconds_var.get() or 0)
            return minutes + (seconds / 60.0)
        except ValueError:
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
                    import platform
                    
                    # Open file with system default application
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', summary_file])
                    elif platform.system() == 'Windows':
                        subprocess.run(['start', summary_file], shell=True)
                    else:  # Linux
                        subprocess.run(['xdg-open', summary_file])
                        
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


def main():
    """Main entry point."""
    root = tk.Tk()
    app = FlipFieldGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("Quit", "Analysis is running. Do you want to quit anyway?"):
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main() 