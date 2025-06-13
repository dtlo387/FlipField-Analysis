"""
🧬 BEAD FLIP DETECTION SYSTEM - GUI APPLICATION
==============================================

Advanced desktop GUI for analyzing bead flip events from video tracking data.

Features:
- Cross-platform compatibility (macOS, Windows, Linux)
- Real-time analysis progress
- Interactive parameter adjustment
- Flip timeline visualization
- Comprehensive results dashboard
- Export options for all result types

Author: Daniel Lo - dlo@hillsdale.edu
Contributors: Claude 4.0
Date: 2025
Platform: Desktop (tkinter + matplotlib)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as patches
import threading
import queue
import os
import sys
from datetime import datetime

# Import our analysis functions
from AnalyzingFlipField_Clean import *

class FlipFieldGUI:
    """Main GUI application for bead flip detection analysis."""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_layout()
        self.setup_progress_queue()
        
        # Analysis state
        self.current_file = None
        self.analysis_results = None
        self.is_analyzing = False
        
    def setup_window(self):
        """Configure the main window."""
        self.root.title("🧬 Bead Flip Detection System - Advanced Dashboard")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set icon and style
        try:
            self.root.tk.call('tk', 'scaling', 1.2)  # Better scaling for high DPI
        except:
            pass
    
    def setup_variables(self):
        """Initialize tkinter variables."""
        # File and video parameters
        self.file_path = tk.StringVar()
        self.video_duration = tk.DoubleVar(value=2.88)
        
        # Analysis parameters
        self.frame_start = tk.IntVar(value=80)
        self.frame_end = tk.IntVar(value=82)
        self.min_position_change = tk.IntVar(value=2)
        self.pair_spacing_min = tk.IntVar(value=40)
        self.pair_spacing_max = tk.IntVar(value=50)
        
        # Display options
        self.show_details = tk.BooleanVar(value=True)
        self.show_debug = tk.BooleanVar(value=False)
        
        # Export options
        self.export_csv = tk.BooleanVar(value=True)
        self.export_categorization = tk.BooleanVar(value=True)
        self.export_summary = tk.BooleanVar(value=True)
        
        # Progress tracking
        self.progress_value = tk.DoubleVar()
        self.progress_text = tk.StringVar(value="Ready to analyze...")
    
    def setup_layout(self):
        """Create the main GUI layout."""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🧬 Bead Flip Detection Dashboard", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")
        
        # Left Panel - Input and Controls
        self.setup_left_panel(main_frame)
        
        # Right Panel - Results and Visualization
        self.setup_right_panel(main_frame)
        
        # Bottom Panel - Progress and Status
        self.setup_bottom_panel(main_frame)
    
    def setup_left_panel(self, parent):
        """Create the left control panel."""
        left_frame = ttk.LabelFrame(parent, text="📁 Input & Parameters", padding="10")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # File Selection
        ttk.Label(left_frame, text="Tracking File:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(0, 5))
        row += 1
        
        file_frame = ttk.Frame(left_frame)
        file_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        file_frame.grid_columnconfigure(0, weight=1)
        
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, state="readonly")
        self.file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(row=0, column=1)
        row += 1
        
        # Video Parameters
        ttk.Label(left_frame, text="📹 Video Parameters:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(10, 5))
        row += 1
        
        ttk.Label(left_frame, text="Duration (minutes):").grid(row=row, column=0, sticky="w")
        duration_spin = ttk.Spinbox(left_frame, from_=0.1, to=10.0, increment=0.1, 
                                   textvariable=self.video_duration, width=10)
        duration_spin.grid(row=row, column=1, sticky="w", padx=(5, 0))
        row += 1
        
        ttk.Label(left_frame, text="Analysis Start (frame):").grid(row=row, column=0, sticky="w")
        start_spin = ttk.Spinbox(left_frame, from_=0, to=200, increment=10, 
                                textvariable=self.frame_start, width=10)
        start_spin.grid(row=row, column=1, sticky="w", padx=(5, 0))
        row += 1
        
        ttk.Label(left_frame, text="Analysis End (skip frames):").grid(row=row, column=0, sticky="w")
        end_spin = ttk.Spinbox(left_frame, from_=0, to=200, increment=10, 
                              textvariable=self.frame_end, width=10)
        end_spin.grid(row=row, column=1, sticky="w", padx=(5, 0))
        row += 1
        
        # Detection Parameters
        ttk.Label(left_frame, text="🔍 Detection Parameters:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(15, 5))
        row += 1
        
        ttk.Label(left_frame, text="Min Position Change (px):").grid(row=row, column=0, sticky="w")
        pos_spin = ttk.Spinbox(left_frame, from_=1, to=10, textvariable=self.min_position_change, width=10)
        pos_spin.grid(row=row, column=1, sticky="w", padx=(5, 0))
        row += 1
        
        ttk.Label(left_frame, text="Pair Spacing Min (frames):").grid(row=row, column=0, sticky="w")
        min_spin = ttk.Spinbox(left_frame, from_=20, to=80, textvariable=self.pair_spacing_min, width=10)
        min_spin.grid(row=row, column=1, sticky="w", padx=(5, 0))
        row += 1
        
        ttk.Label(left_frame, text="Pair Spacing Max (frames):").grid(row=row, column=0, sticky="w")
        max_spin = ttk.Spinbox(left_frame, from_=30, to=100, textvariable=self.pair_spacing_max, width=10)
        max_spin.grid(row=row, column=1, sticky="w", padx=(5, 0))
        row += 1
        
        # Analysis Button
        analyze_btn = ttk.Button(left_frame, text="🔍 Analyze Flips", command=self.start_analysis,
                               style="Accent.TButton")
        analyze_btn.grid(row=row, column=0, columnspan=2, pady=(20, 10), sticky="ew")
        row += 1
        
        # Display Options
        ttk.Label(left_frame, text="🔧 Display Options:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(10, 5))
        row += 1
        
        ttk.Checkbutton(left_frame, text="Show detailed analysis", 
                       variable=self.show_details).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1
        
        ttk.Checkbutton(left_frame, text="Enable debug mode", 
                       variable=self.show_debug).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1
        
        # Export Options
        ttk.Label(left_frame, text="💾 Export Options:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(15, 5))
        row += 1
        
        ttk.Checkbutton(left_frame, text="CSV Data", 
                       variable=self.export_csv).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1
        
        ttk.Checkbutton(left_frame, text="Field Categorization", 
                       variable=self.export_categorization).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1
        
        ttk.Checkbutton(left_frame, text="Analysis Summary", 
                       variable=self.export_summary).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1
        
        # Export Button
        export_btn = ttk.Button(left_frame, text="💾 Export Results", command=self.export_results)
        export_btn.grid(row=row, column=0, columnspan=2, pady=(10, 0), sticky="ew")
    
    def setup_right_panel(self, parent):
        """Create the right results panel."""
        right_frame = ttk.LabelFrame(parent, text="📊 Results & Visualization", padding="10")
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Results Notebook (tabs)
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Tab 1: Field Strength Results
        self.setup_results_tab()
        
        # Tab 2: Timeline Visualization
        self.setup_timeline_tab()
        
        # Tab 3: Detailed Analysis
        self.setup_details_tab()
        
        # Analysis Log
        log_frame = ttk.LabelFrame(right_frame, text="📝 Analysis Log", padding="5")
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky="nsew")
    
    def setup_results_tab(self):
        """Create the field strength results tab."""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="🎯 Field Strength Results")
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Results table
        columns = ("Field (Oe)", "Status", "Frame", "Success")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.results_tree.heading("Field (Oe)", text="Field Strength (Oe)")
        self.results_tree.heading("Status", text="Flip Status")
        self.results_tree.heading("Frame", text="Frame Number")
        self.results_tree.heading("Success", text="Success Rate")
        
        self.results_tree.column("Field (Oe)", width=120, anchor="center")
        self.results_tree.column("Status", width=100, anchor="center")
        self.results_tree.column("Frame", width=100, anchor="center")
        self.results_tree.column("Success", width=100, anchor="center")
        
        # Scrollbar for table
        tree_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll.grid(row=0, column=1, sticky="ns")
        
        # Summary frame
        summary_frame = ttk.LabelFrame(results_frame, text="📈 Summary Statistics", padding="10")
        summary_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.summary_labels = {}
        labels = ["Total Tests", "Successful Flips", "Success Rate", "Quality Assessment"]
        for i, label in enumerate(labels):
            ttk.Label(summary_frame, text=f"{label}:").grid(row=0, column=i*2, sticky="w", padx=(0, 5))
            self.summary_labels[label] = ttk.Label(summary_frame, text="--", font=("Arial", 9, "bold"))
            self.summary_labels[label].grid(row=0, column=i*2+1, sticky="w", padx=(0, 20))
    
    def setup_timeline_tab(self):
        """Create the timeline visualization tab."""
        timeline_frame = ttk.Frame(self.notebook)
        self.notebook.add(timeline_frame, text="📈 Flip Timeline")
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, timeline_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize empty plot
        self.update_timeline_plot()
    
    def setup_details_tab(self):
        """Create the detailed analysis tab."""
        details_frame = ttk.Frame(self.notebook)
        self.notebook.add(details_frame, text="🔍 Detailed Analysis")
        
        details_frame.grid_rowconfigure(0, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, font=("Courier", 9))
        self.details_text.grid(row=0, column=0, sticky="nsew")
    
    def setup_bottom_panel(self, parent):
        """Create the bottom progress panel."""
        progress_frame = ttk.LabelFrame(parent, text="⚡ Analysis Progress", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        progress_frame.grid_columnconfigure(1, weight=1)
        
        # Progress bar
        ttk.Label(progress_frame, text="Status:").grid(row=0, column=0, sticky="w")
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_value, 
                                          maximum=100, mode="determinate")
        self.progress_bar.grid(row=0, column=1, sticky="ew", padx=(10, 10))
        
        # Progress text
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_text)
        self.progress_label.grid(row=0, column=2, sticky="w")
    
    def setup_progress_queue(self):
        """Setup queue for thread communication."""
        self.progress_queue = queue.Queue()
        self.check_progress_queue()
    
    def check_progress_queue(self):
        """Check for progress updates from analysis thread."""
        try:
            while True:
                message = self.progress_queue.get_nowait()
                self.handle_progress_message(message)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_progress_queue)
    
    def handle_progress_message(self, message):
        """Handle progress message from analysis thread."""
        msg_type = message.get("type")
        
        if msg_type == "progress":
            self.progress_value.set(message["value"])
            self.progress_text.set(message["text"])
        elif msg_type == "log":
            self.log_message(message["text"])
        elif msg_type == "complete":
            self.analysis_complete(message["results"])
        elif msg_type == "error":
            self.analysis_error(message["error"])
    
    def browse_file(self):
        """Open file dialog to select tracking data file."""
        file_path = filedialog.askopenfilename(
            title="Select Tracking Data File",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path.set(file_path)
            self.current_file = file_path
            self.log_message(f"Selected file: {os.path.basename(file_path)}")
    
    def start_analysis(self):
        """Start the flip analysis in a separate thread."""
        if not self.current_file:
            messagebox.showerror("Error", "Please select a tracking data file first.")
            return
        
        if self.is_analyzing:
            messagebox.showwarning("Warning", "Analysis is already in progress.")
            return
        
        # Reset GUI state
        self.is_analyzing = True
        self.progress_value.set(0)
        self.progress_text.set("Starting analysis...")
        self.clear_results()
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=self.run_analysis, daemon=True)
        analysis_thread.start()
    
    def run_analysis(self):
        """Run the flip analysis (called in separate thread)."""
        try:
            # Send progress updates
            self.send_progress(10, "Loading data...")
            
            # Update configuration with GUI parameters
            config = self.create_analysis_config()
            
            # Run analysis with progress callbacks
            results = self.run_flip_analysis(config)
            
            # Send completion message
            self.progress_queue.put({
                "type": "complete",
                "results": results
            })
            
        except Exception as e:
            self.progress_queue.put({
                "type": "error", 
                "error": str(e)
            })
    
    def create_analysis_config(self):
        """Create analysis configuration from GUI parameters."""
        return {
            "file_path": self.current_file,
            "video_duration": self.video_duration.get(),
            "frame_start": self.frame_start.get(),
            "frame_end": self.frame_end.get(),
            "min_position_change": self.min_position_change.get(),
            "pair_spacing_min": self.pair_spacing_min.get(),
            "pair_spacing_max": self.pair_spacing_max.get(),
            "show_debug": self.show_debug.get()
        }
    
    def run_flip_analysis(self, config):
        """Run the actual flip analysis with custom parameters."""
        # Update global configuration with GUI parameters
        global FRAME_ANALYSIS_START, FRAME_ANALYSIS_END, MIN_POSITION_CHANGE
        global MIN_PAIR_SPACING, MAX_PAIR_SPACING, VIDEO_DURATION_MIN
        
        FRAME_ANALYSIS_START = config["frame_start"]
        FRAME_ANALYSIS_END = config["frame_end"]
        MIN_POSITION_CHANGE = config["min_position_change"]
        MIN_PAIR_SPACING = config["pair_spacing_min"]
        MAX_PAIR_SPACING = config["pair_spacing_max"]
        VIDEO_DURATION_MIN = config["video_duration"]
        
        try:
            # Step 1: Load and preprocess data
            self.send_progress(15, "Loading tracking data...")
            df, frame_rate = load_and_preprocess_data(config["file_path"])
            
            # Step 2: Detect raw flips
            self.send_progress(30, "Detecting raw flips...")
            x_flip_count, y_flip_count, exclusion_stats = detect_raw_flips(df)
            
            # Step 3: Form groups
            self.send_progress(50, "Forming flip groups...")
            x_groups, y_groups = form_flip_groups(df)
            all_groups = x_groups + y_groups
            
            # Step 4: Create exclusive pairs
            self.send_progress(70, "Creating exclusive pairs...")
            paired_groups, orphaned_groups = create_exclusive_pairs(all_groups)
            
            # Step 5: Update flip booleans
            self.send_progress(80, "Updating flip markers...")
            update_flip_booleans_for_pairs(df, paired_groups)
            
            # Step 6: Categorize by field strength
            self.send_progress(90, "Categorizing by field strength...")
            categorization_results = categorize_flips_by_field_strength(paired_groups, orphaned_groups)
            
            # Step 7: Generate final results
            self.send_progress(95, "Generating results...")
            
            # Calculate success metrics
            total_pairs = len(paired_groups)
            field_results = {}
            
            # Extract field strength results from categorization
            if categorization_results and "Field Strength Analysis" in categorization_results:
                field_analysis = categorization_results["Field Strength Analysis"]
                for field_oe, data in field_analysis.items():
                    field_results[field_oe] = {
                        "flipped": data.get("has_flip", False),
                        "center_frame": data.get("center_frame", None)
                    }
            
            # Fallback: Create results from paired groups if categorization doesn't provide field mapping
            if not field_results and paired_groups:
                # Map paired groups to field strengths (10 Oe increments)
                field_strengths = list(range(10, 110, 10))  # 10, 20, 30, ..., 100 Oe
                
                for i, (group1, group2) in enumerate(paired_groups):
                    if i < len(field_strengths):
                        field_oe = field_strengths[i]
                        center_frame = (group1["center"] + group2["center"]) // 2
                        field_results[field_oe] = {
                            "flipped": True,
                            "center_frame": center_frame
                        }
                
                # Fill in remaining fields as not flipped
                for field_oe in field_strengths:
                    if field_oe not in field_results:
                        field_results[field_oe] = {
                            "flipped": False,
                            "center_frame": None
                        }
            
            # Calculate final metrics
            successful_flips = sum(1 for result in field_results.values() if result["flipped"])
            total_tests = len(field_results) if field_results else 10
            success_rate = (successful_flips / total_tests * 100) if total_tests > 0 else 0
            
            # Determine quality assessment
            if success_rate >= 90:
                quality = "PERFECT"
            elif success_rate >= 70:
                quality = "EXCELLENT"
            elif success_rate >= 50:
                quality = "GOOD"
            else:
                quality = "NEEDS IMPROVEMENT"
            
            self.send_progress(100, "Analysis complete!")
            
            return {
                "success": True,
                "field_results": field_results,
                "total_flips": successful_flips,
                "total_tests": total_tests,
                "success_rate": success_rate,
                "quality": quality,
                "paired_groups": paired_groups,
                "orphaned_groups": orphaned_groups,
                "raw_detections": {"x": x_flip_count, "y": y_flip_count},
                "exclusion_stats": exclusion_stats,
                "dataframe": df,
                "frame_rate": frame_rate
            }
            
        except Exception as e:
            self.send_progress(100, f"Analysis failed: {str(e)}")
            raise e
    
    def send_progress(self, value, text):
        """Send progress update to GUI thread."""
        self.progress_queue.put({
            "type": "progress",
            "value": value,
            "text": text
        })
        
        self.progress_queue.put({
            "type": "log",
            "text": f"[{datetime.now().strftime('%H:%M:%S')}] {text}"
        })
    
    def analysis_complete(self, results):
        """Handle completed analysis."""
        self.is_analyzing = False
        self.analysis_results = results
        
        if results["success"]:
            self.update_results_display(results)
            self.log_message("✅ Analysis completed successfully!")
        else:
            self.log_message("❌ Analysis completed with errors.")
    
    def analysis_error(self, error):
        """Handle analysis error."""
        self.is_analyzing = False
        self.progress_text.set("Analysis failed")
        self.log_message(f"❌ Error: {error}")
        messagebox.showerror("Analysis Error", f"Analysis failed:\n{error}")
    
    def update_results_display(self, results):
        """Update the GUI with analysis results."""
        # Update results table
        self.clear_results_table()
        
        field_results = results["field_results"]
        for field_oe in sorted(field_results.keys()):
            result = field_results[field_oe]
            status = "✅ FLIPPED" if result["flipped"] else "❌ NO FLIP"
            frame = result.get("center_frame", "--")
            
            self.results_tree.insert("", "end", values=(
                f"{field_oe} Oe",
                status,
                frame if frame != "--" else "--",
                "100%" if result["flipped"] else "0%"
            ))
        
        # Update summary
        self.summary_labels["Total Tests"].config(text=str(results.get("total_tests", 10)))
        self.summary_labels["Successful Flips"].config(text=str(results["total_flips"]))
        self.summary_labels["Success Rate"].config(text=f"{results['success_rate']:.1f}%")
        self.summary_labels["Quality Assessment"].config(text=results["quality"])
        
        # Update timeline plot
        self.update_timeline_plot(field_results)
        
        # Update details
        self.update_details_display(results)
    
    def update_timeline_plot(self, field_results=None):
        """Update the flip timeline visualization."""
        self.ax.clear()
        
        if field_results is None:
            self.ax.text(0.5, 0.5, "No data to display\nRun analysis to see timeline", 
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, alpha=0.6)
        else:
            # Create timeline plot
            field_strengths = sorted(field_results.keys())
            
            # Separate successful and failed flips
            successful_fields = []
            successful_frames = []
            failed_fields = []
            
            for field in field_strengths:
                result = field_results[field]
                if result["flipped"] and result["center_frame"] is not None:
                    successful_fields.append(field)
                    successful_frames.append(result["center_frame"])
                else:
                    failed_fields.append(field)
            
            # Plot successful flips
            if successful_frames:
                self.ax.scatter(successful_frames, successful_fields, 
                               c='green', s=120, alpha=0.8, label='Successful Flips', 
                               marker='o', edgecolors='darkgreen', linewidths=2)
                
                # Add field strength labels for successful flips
                for field, frame in zip(successful_fields, successful_frames):
                    self.ax.annotate(f'{field} Oe', (frame, field), 
                                   xytext=(10, 5), textcoords='offset points', 
                                   fontsize=9, fontweight='bold', color='darkgreen')
            
            # Plot failed attempts (if any)
            if failed_fields:
                # Place failed attempts at x=0 for visualization
                self.ax.scatter([0] * len(failed_fields), failed_fields, 
                               c='red', s=80, alpha=0.6, label='No Flip Detected', 
                               marker='x', linewidths=3)
                
                for field in failed_fields:
                    self.ax.annotate(f'{field} Oe', (0, field), 
                                   xytext=(10, 5), textcoords='offset points', 
                                   fontsize=9, color='red')
            
            # Add timeline visualization if we have successful flips
            if len(successful_frames) > 1:
                # Draw connecting lines between consecutive flips
                for i in range(len(successful_frames) - 1):
                    self.ax.plot([successful_frames[i], successful_frames[i+1]], 
                                [successful_fields[i], successful_fields[i+1]], 
                                'b--', alpha=0.5, linewidth=1)
            
            # Formatting
            self.ax.set_xlabel('Frame Number')
            self.ax.set_ylabel('Magnetic Field Strength (Oe)')
            self.ax.set_title('🧬 Flip Events Timeline - Real-time Progress')
            self.ax.grid(True, alpha=0.3)
            
            # Set axis limits
            if successful_frames:
                self.ax.set_xlim(0, max(successful_frames) * 1.1)
            self.ax.set_ylim(min(field_strengths) - 5, max(field_strengths) + 5)
            
            # Legend
            self.ax.legend(loc='upper right')
            
            # Add statistics text box
            success_rate = len(successful_fields) / len(field_strengths) * 100
            stats_text = f"Success Rate: {success_rate:.1f}%\nFlips Detected: {len(successful_fields)}/{len(field_strengths)}"
            self.ax.text(0.02, 0.98, stats_text, transform=self.ax.transAxes, 
                        fontsize=10, verticalalignment='top', 
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        self.canvas.draw()
    
    def update_details_display(self, results):
        """Update the detailed analysis display."""
        total_tests = results.get("total_tests", len(results["field_results"]))
        
        details = f"""🧬 DETAILED ANALYSIS RESULTS
{'='*60}

📁 INPUT PARAMETERS:
- File: {os.path.basename(self.current_file)}
- Video Duration: {self.video_duration.get()} minutes
- Analysis Window: Frame {self.frame_start.get()} to end-{self.frame_end.get()}
- Min Position Change: {self.min_position_change.get()} pixels
- Pair Spacing Range: {self.pair_spacing_min.get()}-{self.pair_spacing_max.get()} frames

📊 RESULTS SUMMARY:
- Total Field Strengths Tested: {total_tests}
- Successful Flips: {results['total_flips']}/{total_tests}
- Success Rate: {results['success_rate']:.1f}%
- Quality Assessment: {results['quality']}

🎯 FIELD-BY-FIELD RESULTS:
{'-'*50}
"""
        
        field_results = results["field_results"]
        for field_oe in sorted(field_results.keys()):
            result = field_results[field_oe]
            status = "✅ FLIPPED" if result["flipped"] else "❌ NO FLIP"
            frame_info = f"(Frame {result['center_frame']})" if result["flipped"] and result["center_frame"] else ""
            details += f"  {field_oe:3d} Oe: {status:<12} {frame_info}\n"
        
        # Add additional analysis information if available
        if "raw_detections" in results:
            raw = results["raw_detections"]
            details += f"\n🔍 RAW DETECTION STATISTICS:\n"
            details += f"- X-axis raw detections: {raw.get('x', 0)}\n"
            details += f"- Y-axis raw detections: {raw.get('y', 0)}\n"
        
        if "paired_groups" in results:
            paired = results["paired_groups"]
            orphaned = results.get("orphaned_groups", [])
            details += f"\n📊 GROUP ANALYSIS:\n"
            details += f"- Legitimate flip pairs: {len(paired)}\n"
            details += f"- Orphaned groups (filtered): {len(orphaned)}\n"
        
        if "exclusion_stats" in results:
            exclusions = results["exclusion_stats"]
            details += f"\n🚫 NOISE FILTERING:\n"
            details += f"- Consecutive flip exclusions: {exclusions.get('x_consecutive', 0) + exclusions.get('y_consecutive', 0)}\n"
            details += f"- Low-speed noise exclusions: {exclusions.get('x_lowspeed', 0) + exclusions.get('y_lowspeed', 0)}\n"
        
        # Add timing information
        details += f"\n⏰ ANALYSIS METADATA:\n"
        details += f"- Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        details += f"- Analysis method: Exclusive pairing with biological constraints\n"
        details += f"- Frame rate: {results.get('frame_rate', 'N/A'):.2f} fps\n" if 'frame_rate' in results else ""
        
        # Add quality assessment explanation
        details += f"\n📈 QUALITY ASSESSMENT CRITERIA:\n"
        details += f"- PERFECT: ≥90% success rate\n"
        details += f"- EXCELLENT: 70-89% success rate\n"
        details += f"- GOOD: 50-69% success rate\n"
        details += f"- NEEDS IMPROVEMENT: <50% success rate\n"
        
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
    
    def clear_results(self):
        """Clear all results displays."""
        self.clear_results_table()
        
        for label in self.summary_labels.values():
            label.config(text="--")
        
        self.update_timeline_plot()
        
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, "Run analysis to see detailed results...")
    
    def clear_results_table(self):
        """Clear the results table."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
    
    def export_results(self):
        """Export analysis results based on selected options."""
        if not self.analysis_results:
            messagebox.showwarning("Warning", "No analysis results to export. Run analysis first.")
            return
        
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            return
        
        exported_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Export CSV data
            if self.export_csv.get():
                csv_path = os.path.join(export_dir, f"flip_analysis_data_{timestamp}.csv")
                self.export_csv_data(csv_path)
                exported_files.append(csv_path)
            
            # Export field categorization
            if self.export_categorization.get():
                cat_path = os.path.join(export_dir, f"field_strength_categorization_{timestamp}.txt")
                self.export_categorization_data(cat_path)
                exported_files.append(cat_path)
            
            # Export analysis summary
            if self.export_summary.get():
                summary_path = os.path.join(export_dir, f"analysis_summary_{timestamp}.txt")
                self.export_summary_data(summary_path)
                exported_files.append(summary_path)
            
            # Export timeline plot
            if exported_files:  # Only if at least one export option is selected
                plot_path = os.path.join(export_dir, f"flip_timeline_{timestamp}.png")
                self.export_timeline_plot(plot_path)
                exported_files.append(plot_path)
            
            messagebox.showinfo("Export Complete", 
                               f"Results exported successfully!\n\nFiles created:\n" + 
                               "\n".join([f"• {os.path.basename(f)}" for f in exported_files]))
            
            self.log_message(f"✅ Results exported to {export_dir}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results:\n{str(e)}")
            self.log_message(f"❌ Export failed: {str(e)}")
    
    def export_csv_data(self, file_path):
        """Export the dataframe as CSV."""
        if "dataframe" in self.analysis_results:
            df = self.analysis_results["dataframe"]
            df.to_csv(file_path, index=False)
        else:
            # Create basic CSV from field results
            field_results = self.analysis_results["field_results"]
            data = []
            for field_oe, result in field_results.items():
                data.append({
                    "Field_Strength_Oe": field_oe,
                    "Flip_Detected": result["flipped"],
                    "Center_Frame": result["center_frame"] if result["flipped"] else None
                })
            import pandas as pd
            pd.DataFrame(data).to_csv(file_path, index=False)
    
    def export_categorization_data(self, file_path):
        """Export field strength categorization."""
        results = self.analysis_results
        field_results = results["field_results"]
        
        content = f"""FIELD STRENGTH CATEGORIZATION REPORT
{'='*50}

Analysis File: {os.path.basename(self.current_file)}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FIELD STRENGTH MAPPING:
"""
        
        for field_oe in sorted(field_results.keys()):
            result = field_results[field_oe]
            status = "FLIP DETECTED" if result["flipped"] else "NO FLIP"
            frame_info = f" at frame {result['center_frame']}" if result["flipped"] and result["center_frame"] else ""
            content += f"{field_oe:3d} Oe: {status}{frame_info}\n"
        
        content += f"\nSUMMARY:\n"
        content += f"Total field strengths tested: {len(field_results)}\n"
        content += f"Successful flips: {results['total_flips']}\n"
        content += f"Success rate: {results['success_rate']:.1f}%\n"
        content += f"Quality assessment: {results['quality']}\n"
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    def export_summary_data(self, file_path):
        """Export comprehensive analysis summary."""
        # Get the detailed text from the GUI
        detailed_content = self.details_text.get(1.0, tk.END)
        
        with open(file_path, 'w') as f:
            f.write(detailed_content)
    
    def export_timeline_plot(self, file_path):
        """Export the timeline plot as PNG."""
        self.fig.savefig(file_path, dpi=300, bbox_inches='tight', 
                        facecolor='white', edgecolor='none')
    
    def log_message(self, message):
        """Add message to the analysis log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

def main():
    """Main application entry point."""
    root = tk.Tk()
    
    # Configure ttk styles
    style = ttk.Style()
    
    # Try to use a modern theme
    try:
        style.theme_use('clam')  # Cross-platform modern theme
    except:
        pass
    
    # Create and run the application
    app = FlipFieldGUI(root)
    
    # Handle window close
    def on_closing():
        if app.is_analyzing:
            if messagebox.askokcancel("Quit", "Analysis is in progress. Are you sure you want to quit?"):
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main() 