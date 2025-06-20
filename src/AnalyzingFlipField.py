"""
BEAD FLIP DETECTION SYSTEM - GUI Compatible Version
======================================================

Author: Daniel Lo
Date: 2025
"""

import pandas as pd
import numpy as np
import os
import sys

# Configure pandas for better display
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

class FlipFieldAnalyzer:
    """
    Flip field analyzer that can be configured and called from GUI.
    """
    
    def __init__(self, file_path, video_duration_min=2.8833333333, 
                 frame_analysis_start=80, frame_analysis_end=82,
                 min_position_change=2, frame_skip=2, max_recent_flip_distance=8,
                 min_significant_movement=3, max_group_distance=5,
                 min_pair_spacing=40, max_pair_spacing=50,
                 output_dir=None):
        
        # File and video parameters
        self.FILE_PATH = file_path
        self.VIDEO_DURATION_MIN = video_duration_min
        self.FRAME_ANALYSIS_START = frame_analysis_start
        self.FRAME_ANALYSIS_END = frame_analysis_end
        
        # Flip detection parameters
        self.MIN_POSITION_CHANGE = min_position_change
        self.FRAME_SKIP = frame_skip
        self.MAX_RECENT_FLIP_DISTANCE = max_recent_flip_distance
        self.MIN_SIGNIFICANT_MOVEMENT = min_significant_movement
        
        # Pairing parameters
        self.MAX_GROUP_DISTANCE = max_group_distance
        self.MIN_PAIR_SPACING = min_pair_spacing
        self.MAX_PAIR_SPACING = max_pair_spacing
        
        # Directory setup - only use user-selected output directory
        if not output_dir:
            raise ValueError("output_dir must be specified")
        self.ANALYSIS_DIR = output_dir
        
        # Results storage
        self.df = None
        self.all_groups = []
        self.paired_groups = []
        self.orphaned_groups = []
    
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        for directory in [self.ANALYSIS_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def load_and_preprocess_data(self):
        """
        Load bead tracking data and add calculated columns.
        
        Returns:
            tuple: (pd.DataFrame, frame_rate)
        """
        # Load data
        column_names = ['Frames', 'X Position (px)', 'Y Position (px)', 'Angle (deg)']
        self.df = pd.read_fwf(self.FILE_PATH, skiprows=1, names=column_names)
        
        # Update frame numbering to be continuous
        self.df['Frames'] = range(1, len(self.df) + 1)
        
        # Calculate video properties
        video_duration_sec = self.VIDEO_DURATION_MIN * 60
        total_frames = len(self.df)
        frame_rate = total_frames / video_duration_sec
        
        # Convert position columns to float
        self.df['X Position (px)'] = pd.to_numeric(self.df['X Position (px)'])
        self.df['Y Position (px)'] = pd.to_numeric(self.df['Y Position (px)'])
        
        # Calculate movement metrics
        self.df['X_velocity'] = self.df['X Position (px)'].diff()
        self.df['Y_velocity'] = self.df['Y Position (px)'].diff()
        self.df['Speed'] = np.sqrt(self.df['X_velocity']**2 + self.df['Y_velocity']**2)
        
        # Add time formatting
        def format_time(frame):
            total_seconds = frame / frame_rate
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
        
        self.df['Minutes'] = self.df['Frames'].apply(format_time)
        
        # Initialize flip detection columns
        self.df['Flip Field X'] = False
        self.df['Flip Field Y'] = False
        
        print(f"\nVideo Analysis Setup:")
        print(f"Duration: {self.VIDEO_DURATION_MIN} minutes")
        print(f"Total frames: {total_frames}")
        print(f"Frame rate: {frame_rate:.2f} frames/second")
        print(f"Analysis window: frames {self.FRAME_ANALYSIS_START} to {total_frames - self.FRAME_ANALYSIS_END}")
        
        return self.df, frame_rate
    
    def has_recent_flip(self, index, axis, lookback_frames=None):
        """
        Check if there was a recent flip detection to avoid rapid consecutive flips.
        
        Args:
            index (int): Current frame index
            axis (str): 'X' or 'Y' axis
            lookback_frames (int): Number of frames to look back
            
        Returns:
            bool: True if recent flip detected
        """
        if lookback_frames is None:
            lookback_frames = self.MAX_RECENT_FLIP_DISTANCE
            
        start_check = max(0, index - lookback_frames)
        return self.df[f'Flip Field {axis}'].iloc[start_check:index].any()
    
    def detect_raw_flips(self):
        """
        Detect raw flip events using basic criteria with refinements.
        
        Returns:
            tuple: (x_flip_count, y_flip_count, exclusion_stats)
        """
        print(f"\n=== Basic Flip Detection ===")
        
        # Analysis bounds
        start_idx = self.FRAME_ANALYSIS_START
        end_idx = len(self.df) - self.FRAME_ANALYSIS_END
        
        # Tracking variables
        flip_count_x = 0
        flip_count_y = 0
        excluded_stats = {
            'x_consecutive': 0, 'x_lowspeed': 0,
            'y_consecutive': 0, 'y_lowspeed': 0
        }
        
        # X-axis flip detection
        for i in range(start_idx, end_idx):
            current_x = self.df['X Position (px)'].iloc[i]
            next_x = self.df['X Position (px)'].iloc[i + self.FRAME_SKIP]
            position_change = abs(next_x - current_x)
            
            if position_change >= self.MIN_POSITION_CHANGE:
                # Refinement 1: Avoid rapid consecutive flips
                if self.has_recent_flip(i, 'X'):
                    excluded_stats['x_consecutive'] += 1
                    continue
                    
                # Refinement 2: Skip low-speed noise
                current_speed = self.df['Speed'].iloc[i]
                if current_speed == 0.0 and position_change < self.MIN_SIGNIFICANT_MOVEMENT:
                    excluded_stats['x_lowspeed'] += 1
                    continue
                
                # Mark as flip
                self.df.loc[i:i+self.FRAME_SKIP, 'Flip Field X'] = True
                flip_count_x += 1
        
        # Y-axis flip detection (same logic)
        for i in range(start_idx, end_idx):
            current_y = self.df['Y Position (px)'].iloc[i]
            next_y = self.df['Y Position (px)'].iloc[i + self.FRAME_SKIP]
            position_change = abs(next_y - current_y)
            
            if position_change >= self.MIN_POSITION_CHANGE:
                if self.has_recent_flip(i, 'Y'):
                    excluded_stats['y_consecutive'] += 1
                    continue
                    
                current_speed = self.df['Speed'].iloc[i]
                if current_speed == 0.0 and position_change < self.MIN_SIGNIFICANT_MOVEMENT:
                    excluded_stats['y_lowspeed'] += 1
                    continue
                
                self.df.loc[i:i+self.FRAME_SKIP, 'Flip Field Y'] = True
                flip_count_y += 1
        
        # Print results
        print(f"X-axis flip events: {flip_count_x}")
        print(f"Y-axis flip events: {flip_count_y}")
        print(f"Total events before pairing: {flip_count_x + flip_count_y}")
        
        print(f"\nRefinement Filters Applied:")
        print(f"X-axis excluded (consecutive): {excluded_stats['x_consecutive']}")
        print(f"X-axis excluded (low speed): {excluded_stats['x_lowspeed']}")
        print(f"Y-axis excluded (consecutive): {excluded_stats['y_consecutive']}")
        print(f"Y-axis excluded (low speed): {excluded_stats['y_lowspeed']}")
        
        total_excluded = sum(excluded_stats.values())
        print(f"Total excluded by refinements: {total_excluded}")
        
        return flip_count_x, flip_count_y, excluded_stats
    
    def form_flip_groups(self):
        """
        Group nearby flip detections into coherent flip events.
        
        Returns:
            list: List of group dictionaries with frame information
        """
        # Get all flip frames (combine X and Y)
        all_flips = self.df[(self.df['Flip Field X'] == True) | (self.df['Flip Field Y'] == True)]
        flip_frames = sorted(all_flips.index.tolist())
        
        if len(flip_frames) == 0:
            return []
        
        print(f"\n=== Group Formation ===")
        print(f"Total flip frames detected: {len(flip_frames)}")
        
        # Group nearby flips (within MAX_GROUP_DISTANCE frames)
        groups = []
        used_frames = set()
        
        for i, frame in enumerate(flip_frames):
            if frame in used_frames:
                continue
                
            # Start a new group
            group_frames = [frame]
            used_frames.add(frame)
            
            # Look for nearby frames to add to group
            for j in range(i+1, len(flip_frames)):
                other_frame = flip_frames[j]
                if other_frame in used_frames:
                    continue
                if other_frame - frame <= self.MAX_GROUP_DISTANCE:
                    group_frames.append(other_frame)
                    used_frames.add(other_frame)
                else:
                    break  # Frames are sorted, no more close ones
            
            # Create group metadata
            groups.append({
                'frames': group_frames,
                'start_frame': min(group_frames),
                'end_frame': max(group_frames),
                'center_frame': sum(group_frames) // len(group_frames)
            })
        
        print(f"Groups formed: {len(groups)}")
        self.all_groups = groups
        return groups
    
    def create_exclusive_pairs(self):
        """
        Create exclusive pairs from groups using specified frame spacing.
        Each group can only be paired with ONE other group.
        
        Returns:
            tuple: (all_groups, paired_groups, orphaned_groups)
        """
        print(f"\n=== Exclusive Pairing Analysis ===")
        
        if len(self.all_groups) == 0:
            return self.all_groups, [], []
        
        paired_groups = []
        used_group_indices = set()
        
        # Find best exclusive pairs
        for i in range(len(self.all_groups)):
            if i in used_group_indices:
                continue
                
            current_group = self.all_groups[i]
            best_partner = None
            best_partner_idx = None
            best_spacing = None
            
            # Look for the best partner with valid spacing
            for j in range(i+1, len(self.all_groups)):
                if j in used_group_indices:
                    continue
                    
                partner_group = self.all_groups[j]
                spacing = partner_group['center_frame'] - current_group['center_frame']
                
                # Check if spacing is valid
                if self.MIN_PAIR_SPACING <= spacing <= self.MAX_PAIR_SPACING:
                    if best_partner is None or spacing < best_spacing:
                        best_partner = partner_group
                        best_partner_idx = j
                        best_spacing = spacing
            
            # If valid partner found, create exclusive pair
            if best_partner is not None:
                used_group_indices.add(i)
                used_group_indices.add(best_partner_idx)
                
                paired_groups.append(current_group)
                paired_groups.append(best_partner)
                
                print(f"  Pairing: Group {i+1} (center {current_group['center_frame']}) ↔ "
                      f"Group {best_partner_idx+1} (center {best_partner['center_frame']}) "
                      f"[{best_spacing} frames]")
        
        # Identify orphaned groups
        orphaned_groups = [self.all_groups[i] for i in range(len(self.all_groups)) if i not in used_group_indices]
        
        if orphaned_groups:
            print(f"  Orphaned groups (eliminated): {len(orphaned_groups)}")
            for group in orphaned_groups:
                original_idx = self.all_groups.index(group)
                print(f"    Group {original_idx+1} (center {group['center_frame']}) - no partner found")
        
        print(f"\nPairing Results:")
        print(f"Total groups: {len(self.all_groups)}")
        print(f"Successfully paired: {len(paired_groups)}")
        print(f"Orphaned (eliminated): {len(orphaned_groups)}")
        
        self.paired_groups = paired_groups
        self.orphaned_groups = orphaned_groups
        
        return self.all_groups, paired_groups, orphaned_groups
    
    def update_flip_booleans_for_pairs(self):
        """
        Reset boolean columns to only mark frames within legitimate pairs.
        Preserves ALL frames within each paired flip event.
        """
        print(f"\n=== Final Boolean Update ===")
        
        # Reset all flip columns
        self.df.loc[:, 'Flip Field X'] = False
        self.df.loc[:, 'Flip Field Y'] = False
        
        print(f"Marking ALL frames within {len(self.paired_groups)} paired groups as True")
        
        # Mark all frames within paired groups
        for pair in self.paired_groups:
            start_frame = min(pair['frames'])
            end_frame = max(pair['frames'])
            
            print(f"  Processing: frames {start_frame}-{end_frame} ({len(pair['frames'])} total frames)")
            
            # Mark every frame in the range that shows flip behavior
            for frame_idx in range(start_frame, end_frame + 1):
                if frame_idx < len(self.df) and frame_idx + self.FRAME_SKIP < len(self.df):
                    current_x = self.df['X Position (px)'].iloc[frame_idx]
                    current_y = self.df['Y Position (px)'].iloc[frame_idx]
                    next_x = self.df['X Position (px)'].iloc[frame_idx + self.FRAME_SKIP]
                    next_y = self.df['Y Position (px)'].iloc[frame_idx + self.FRAME_SKIP]
                    
                    # Apply flip criteria to determine axis
                    if abs(next_x - current_x) >= self.MIN_POSITION_CHANGE:
                        self.df.loc[frame_idx, 'Flip Field X'] = True
                    if abs(next_y - current_y) >= self.MIN_POSITION_CHANGE:
                        self.df.loc[frame_idx, 'Flip Field Y'] = True
    
    def export_results(self, export_txt=True, export_csv=True, export_debug=False, export_summary=True):
        """
        Export the final results to files based on settings.
        
        Args:
            export_txt (bool): Export TXT file
            export_csv (bool): Export CSV file
            export_debug (bool): Export debug file
            export_summary (bool): Export simplified flip summary
        """
        print(f"\n=== Exporting Results ===")
        
        # Create export copy with formatted numbers
        export_df = self.df.copy()
        export_df['X Position (px)'] = export_df['X Position (px)'].round(6).astype(str)
        export_df['Y Position (px)'] = export_df['Y Position (px)'].round(6).astype(str)
        
        # Generate base name
        base_name = os.path.splitext(os.path.basename(self.FILE_PATH))[0]
        
        exported_files = []
        
        if export_txt:
            txt_output = os.path.join(self.ANALYSIS_DIR, f'{base_name}_flip_field_analysis.txt')
            export_df.to_csv(txt_output, sep='\t', index=False)
            exported_files.append(f"TXT: {txt_output}")
        
        if export_csv:
            csv_output = os.path.join(self.ANALYSIS_DIR, f'{base_name}_flip_field_analysis.csv')
            export_df.to_csv(csv_output, index=False)
            exported_files.append(f"CSV: {csv_output}")
        
        if export_summary:
            summary_output = os.path.join(self.ANALYSIS_DIR, f'{base_name}_flipfield_summary.txt')
            self.export_flip_summary(summary_output)
            exported_files.append(f"SUMMARY: {summary_output}")
        
        # Always create debug log file
        debug_output = os.path.join(self.ANALYSIS_DIR, f'{base_name}_flipfield_analysis_debug_log.txt')
        self.export_debug_log(debug_output)
        exported_files.append(f"DEBUG_LOG: {debug_output}")
        
        if export_debug:
            debug_output = os.path.join(self.ANALYSIS_DIR, f'{base_name}_debug_info.txt')
            with open(debug_output, 'w') as f:
                f.write("FLIP FIELD ANALYSIS DEBUG INFORMATION\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"File: {self.FILE_PATH}\n")
                f.write(f"Video Duration: {self.VIDEO_DURATION_MIN} minutes\n")
                f.write(f"Total Groups: {len(self.all_groups)}\n")
                f.write(f"Paired Groups: {len(self.paired_groups)}\n")
                f.write(f"Orphaned Groups: {len(self.orphaned_groups)}\n\n")
                
                if self.paired_groups:
                    f.write("PAIRED GROUPS:\n")
                    for i, group in enumerate(self.paired_groups):
                        f.write(f"  Group {i+1}: Frames {group['frames']}, Center: {group['center_frame']}\n")
                
                if self.orphaned_groups:
                    f.write("\nORPHANED GROUPS:\n")
                    for i, group in enumerate(self.orphaned_groups):
                        f.write(f"  Group {i+1}: Frames {group['frames']}, Center: {group['center_frame']}\n")
            
            exported_files.append(f"DEBUG: {debug_output}")
        
        print("Results exported to:")
        for file_info in exported_files:
            print(f"  {file_info}")
        
        return exported_files
    
    def export_flip_summary(self, output_path):
        """
        Export a simplified flip summary showing which beads flipped at each Oe.
        
        Args:
            output_path (str): Path to save the summary file
        """
        with open(output_path, 'w') as f:
            f.write("BEAD FLIP SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            # File information
            f.write(f"File: {os.path.basename(self.FILE_PATH)}\n")
            f.write(f"Video Duration: {self.VIDEO_DURATION_MIN:.2f} minutes\n")
            f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Results summary
            total_flip_events = len(self.paired_groups) // 2
            f.write(f"RESULTS SUMMARY:\n")
            f.write(f"Total Flip Pairs Detected: {total_flip_events}\n")
            f.write(f"Expected Flip Pairs: 10\n")
            
            # Quality assessment
            if total_flip_events == 10:
                quality = "PERFECT"
            elif 8 <= total_flip_events <= 12:
                quality = "EXCELLENT"
            elif 6 <= total_flip_events <= 14:
                quality = "GOOD"
            else:
                quality = "FAIR"
            
            f.write(f"Quality Assessment: {quality}\n\n")
            
            # Flip events by Oe level (estimated)
            f.write("FLIP EVENTS BY ESTIMATED Oe LEVEL:\n")
            f.write("-" * 40 + "\n")
            
            if len(self.paired_groups) > 0:
                # Estimate Oe levels based on timing (assuming 10 planned flip events)
                # This is a simplified approach - in reality, Oe levels would be known from experimental setup
                total_duration_frames = len(self.df)
                expected_intervals = 10
                
                f.write("Oe Field | Frame Range | Status | Time\n")
                f.write("-" * 40 + "\n")
                
                flip_events = []
                for i in range(0, len(self.paired_groups), 2):
                    if i+1 < len(self.paired_groups):
                        group1 = self.paired_groups[i]
                        group2 = self.paired_groups[i+1]
                        event_center = (group1['center_frame'] + group2['center_frame']) // 2
                        flip_events.append({
                            'event_num': i//2 + 1,
                            'frame': event_center,
                            'group1_frame': group1['center_frame'],
                            'group2_frame': group2['center_frame']
                        })
                
                # Sort by frame number
                flip_events.sort(key=lambda x: x['frame'])
                
                # Map to estimated Oe levels
                for i, event in enumerate(flip_events):
                    oe_value = (i + 1) * 10  # 10 Oe, 20 Oe, 30 Oe, etc.
                    oe_level = f"{oe_value} Oe"
                    frame_range = f"{event['group1_frame']}-{event['group2_frame']}"
                    
                    # Convert frame to time
                    frame_rate = len(self.df) / (self.VIDEO_DURATION_MIN * 60)
                    time_sec = event['frame'] / frame_rate
                    time_str = f"{int(time_sec//60):02d}:{int(time_sec%60):02d}"
                    
                    f.write(f"{oe_level:8} | {frame_range:11} | FLIPPED | {time_str}\n")
                
                # Show any missing flip events (up to 10 expected)
                missing_count = 10 - len(flip_events)
                if missing_count > 0:
                    for i in range(len(flip_events), 10):
                        oe_value = (i + 1) * 10  # Continue the sequence
                        oe_level = f"{oe_value} Oe"
                        f.write(f"{oe_level:8} | {'---':11} | NO FLIP | ---\n")
            
            else:
                f.write("No flip events detected.\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("END OF SUMMARY\n")
    
    def export_debug_log(self, output_path):
        """
        Export the debug analysis log to a text file.
        
        Args:
            output_path (str): Path to save the debug log file
        """
        with open(output_path, 'w') as f:
            f.write("FLIPFIELD ANALYSIS DEBUG LOG\n")
            f.write("=" * 80 + "\n\n")
            
            # File information
            f.write(f"File: {os.path.basename(self.FILE_PATH)}\n")
            f.write(f"Full Path: {self.FILE_PATH}\n")
            f.write(f"Video Duration: {self.VIDEO_DURATION_MIN:.4f} minutes\n")
            f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Analysis parameters
            f.write("ANALYSIS PARAMETERS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Frame Analysis Start: {self.FRAME_ANALYSIS_START}\n")
            f.write(f"Frame Analysis End: {self.FRAME_ANALYSIS_END}\n")
            f.write(f"Min Position Change: {self.MIN_POSITION_CHANGE}\n")
            f.write(f"Frame Skip: {self.FRAME_SKIP}\n")
            f.write(f"Max Recent Flip Distance: {self.MAX_RECENT_FLIP_DISTANCE}\n")
            f.write(f"Min Significant Movement: {self.MIN_SIGNIFICANT_MOVEMENT}\n")
            f.write(f"Max Group Distance: {self.MAX_GROUP_DISTANCE}\n")
            f.write(f"Min Pair Spacing: {self.MIN_PAIR_SPACING}\n")
            f.write(f"Max Pair Spacing: {self.MAX_PAIR_SPACING}\n\n")
            
            # Results summary
            total_flip_events = len(self.paired_groups) // 2
            f.write("ANALYSIS RESULTS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Groups Detected: {len(self.all_groups)}\n")
            f.write(f"Successfully Paired Groups: {len(self.paired_groups)}\n")
            f.write(f"Orphaned Groups: {len(self.orphaned_groups)}\n")
            f.write(f"Final Flip Pairs: {total_flip_events}\n")
            f.write(f"Expected Flip Pairs: 10\n")
            
            # Quality assessment
            if total_flip_events == 10:
                quality = "PERFECT"
            elif 8 <= total_flip_events <= 12:
                quality = "EXCELLENT"
            elif 6 <= total_flip_events <= 14:
                quality = "GOOD"
            else:
                quality = "FAIR"
            
            f.write(f"Quality Assessment: {quality}\n\n")
            
            # Detailed flip events
            if len(self.paired_groups) > 0:
                f.write("DETECTED FLIP EVENTS:\n")
                f.write("-" * 40 + "\n")
                
                flip_events = []
                for i in range(0, len(self.paired_groups), 2):
                    if i+1 < len(self.paired_groups):
                        group1 = self.paired_groups[i]
                        group2 = self.paired_groups[i+1]
                        flip_events.append({
                            'event_num': i//2 + 1,
                            'group1': group1,
                            'group2': group2,
                            'spacing': group2['center_frame'] - group1['center_frame']
                        })
                
                # Sort by frame number
                flip_events.sort(key=lambda x: x['group1']['center_frame'])
                
                for event in flip_events:
                    f.write(f"Event {event['event_num']}: Frames {event['group1']['center_frame']} ↔ "
                           f"{event['group2']['center_frame']} [{event['spacing']} frames apart]\n")
                    f.write(f"  Group 1 frames: {event['group1']['frames']}\n")
                    f.write(f"  Group 2 frames: {event['group2']['frames']}\n\n")
            
            # Orphaned groups (false positives)
            if self.orphaned_groups:
                f.write("ELIMINATED FALSE POSITIVES:\n")
                f.write("-" * 40 + "\n")
                for i, group in enumerate(self.orphaned_groups):
                    original_idx = self.all_groups.index(group) + 1
                    frames_str = ', '.join(map(str, group['frames']))
                    f.write(f"Group {original_idx}: Frames [{frames_str}] "
                           f"(center: {group['center_frame']}) - No valid pair\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("END OF DEBUG LOG\n")
    
    def analyze_flip_patterns(self):
        """
        Analyze and report on flip patterns and results.
        """
        print(f"\n=== Pattern Analysis ===")
        
        # Count final results
        all_flip_frames = self.df[(self.df['Flip Field X'] == True) | (self.df['Flip Field Y'] == True)]
        total_flip_events = len(self.paired_groups) // 2
        total_frames_marked = len(all_flip_frames)
        
        print(f"Final Results:")
        print(f"  Flip pairs detected: {total_flip_events}")
        print(f"  Total frames marked True: {total_frames_marked}")
        print(f"  Expected pairs: 10")
        
        # Quality assessment
        if total_flip_events == 10:
            quality = "PERFECT"
        elif 8 <= total_flip_events <= 12:
            quality = "EXCELLENT"
        elif 6 <= total_flip_events <= 14:
            quality = "GOOD"
        else:
            quality = "FAIR"
        
        print(f"  Quality assessment: {quality}")
        
        # Show legitimate pairs
        if len(self.paired_groups) > 0:
            print(f"\nLegitimate Flip Events (Paired Only):")
            for i in range(0, len(self.paired_groups), 2):
                group1 = self.paired_groups[i]
                group2 = self.paired_groups[i+1] if i+1 < len(self.paired_groups) else None
                
                if group2:
                    spacing = group2['center_frame'] - group1['center_frame']
                    print(f"  Event {i//2 + 1}: Frames {group1['center_frame']} ↔ "
                          f"{group2['center_frame']} [{spacing} frames apart]")
        
        # Show eliminated false positives
        if self.orphaned_groups:
            print(f"\nEliminated False Positives:")
            for i, group in enumerate(self.orphaned_groups):
                original_idx = self.all_groups.index(group) + 1
                frames_str = ', '.join(map(str, group['frames']))
                print(f"  Group {original_idx}: Frames [{frames_str}] "
                      f"(center: {group['center_frame']}) - No valid pair")
        
        # Summary statistics
        print(f"\nSummary Statistics:")
        print(f"  Groups eliminated: {len(self.orphaned_groups)}")
        print(f"  False positive reduction: Exclusive pairing logic")
        print(f"  Missed flip recovery: Automatic through pairing")
        
        return {
            'total_flip_events': total_flip_events,
            'total_frames_marked': total_frames_marked,
            'quality': quality,
            'groups_eliminated': len(self.orphaned_groups)
        }
    
    def run_complete_analysis(self, export_txt=True, export_csv=True, export_debug=False, export_summary=True):
        """
        Run the complete analysis pipeline.
        
        Args:
            export_txt (bool): Export TXT file
            export_csv (bool): Export CSV file
            export_debug (bool): Export debug file
            export_summary (bool): Export simplified flip summary
            
        Returns:
            dict: Analysis results and statistics
        """
        # Capture debug output
        debug_output = []
        original_print = print
        
        def capture_print(*args, **kwargs):
            # Call original print
            original_print(*args, **kwargs)
            # Capture for debug output
            if args:
                debug_output.append(' '.join(str(arg) for arg in args))
        
        # Replace print temporarily
        import builtins
        builtins.print = capture_print
        
        try:
            print("=" * 80)
            print("BEAD FLIP DETECTION SYSTEM")
            print("=" * 80)
            
            # Setup
            self.setup_directories()
            
            # Stage 1: Load and preprocess data
            df, frame_rate = self.load_and_preprocess_data()
            
            # Stage 2: Detect raw flips with basic refinements
            x_flips, y_flips, exclusion_stats = self.detect_raw_flips()
            
            # Stage 3: Form groups from nearby detections
            all_groups = self.form_flip_groups()
            
            # Stage 4: Create exclusive pairs
            all_groups, paired_groups, orphaned_groups = self.create_exclusive_pairs()
            
            # Stage 5: Update booleans for only paired groups
            self.update_flip_booleans_for_pairs()
            
            # Stage 6: Export results
            exported_files = self.export_results(export_txt, export_csv, export_debug, export_summary)
            
            # Stage 7: Analysis and reporting
            pattern_results = self.analyze_flip_patterns()
            
            print("\n" + "=" * 80)
            print("✅ FLIP DETECTION COMPLETE")
            print("=" * 80)
            
            return {
                'success': True,
                'dataframe': self.df,
                'all_groups': self.all_groups,
                'paired_groups': self.paired_groups,
                'orphaned_groups': self.orphaned_groups,
                'pattern_results': pattern_results,
                'exported_files': exported_files,
                'frame_rate': frame_rate,
                'debug_output': '\n'.join(debug_output),
                'summary_file': os.path.join(self.ANALYSIS_DIR, f'{os.path.splitext(os.path.basename(self.FILE_PATH))[0]}_flipfield_summary.txt') if export_summary else None
            }
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'debug_output': '\n'.join(debug_output)
            }
        finally:
            # Restore original print function
            builtins.print = original_print


def run_gui_analysis(file_path, video_duration_min=2.8833333333, 
                    frame_analysis_start_seconds=None, frame_analysis_end_seconds=None,
                    min_position_change=2,
                    export_txt=True, export_csv=True, export_debug=False,
                    export_summary=True, output_dir=None):
    """
    Entry point for GUI to run analysis with custom parameters.
    
    Args:
        file_path (str): Path to the input file
        video_duration_min (float): Video duration in minutes
        frame_analysis_start_seconds (float): Seconds to skip at start (converted to frames)
        frame_analysis_end_seconds (float): Seconds to skip at end (converted to frames)
        min_position_change (float): Minimum pixel movement to detect flip
        export_txt (bool): Export TXT file
        export_csv (bool): Export CSV file
        export_debug (bool): Export debug file
        export_summary (bool): Export simplified flip summary
        output_dir (str): Custom output directory
        
    Returns:
        dict: Analysis results
    """
    # Calculate frame rate first to convert seconds to frames
    # Load data temporarily to get frame count
    column_names = ['Frames', 'X Position (px)', 'Y Position (px)', 'Angle (deg)']
    temp_df = pd.read_fwf(file_path, skiprows=1, names=column_names)
    total_frames = len(temp_df)
    video_duration_sec = video_duration_min * 60
    frame_rate = total_frames / video_duration_sec
    
    # Convert seconds to frames, with defaults
    if frame_analysis_start_seconds is None:
        frame_analysis_start = 80  # Default frames
    else:
        frame_analysis_start = max(0, int(frame_analysis_start_seconds * frame_rate))
    
    if frame_analysis_end_seconds is None:
        frame_analysis_end = 82  # Default frames
    else:
        frame_analysis_end = max(0, int(frame_analysis_end_seconds * frame_rate))
    
    analyzer = FlipFieldAnalyzer(
        file_path=file_path,
        video_duration_min=video_duration_min,
        frame_analysis_start=frame_analysis_start,
        frame_analysis_end=frame_analysis_end,
        min_position_change=min_position_change,
        output_dir=output_dir
    )
    
    return analyzer.run_complete_analysis(export_txt, export_csv, export_debug, export_summary)


# Maintain compatibility with original script
def main():
    """Main function for command-line usage (backward compatibility)."""
    file_path = 'Movie_2601.aviNB2.txt'
    return run_gui_analysis(file_path)


if __name__ == "__main__":
    main() 