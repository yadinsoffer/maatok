from typing import List, Dict, Tuple
from metadata_extractor import get_video_duration
import math

class DurationController:
    def __init__(self, target_duration: float):
        """
        Initialize the DurationController with a target duration.
        
        Args:
            target_duration (float): Target duration in seconds to match the audio length
        """
        self.target_duration = target_duration
        # Allow a small margin of error (0.5 seconds)
        self.margin = 0.5
    
    def calculate_trim_instructions(self, video_paths: List[str]) -> List[Dict[str, float]]:
        """
        Calculate trim instructions for a list of videos to match target duration.
        If videos are too short, they will be looped to reach the target duration.
        
        Args:
            video_paths (List[str]): List of paths to video files
            
        Returns:
            List[Dict[str, float]]: List of trim instructions for each video
                [
                    {
                        'start_time': float,  # Start time in seconds
                        'end_time': float,    # End time in seconds
                        'loop_count': int     # Number of times to loop this segment
                    },
                    ...
                ]
        """
        # Get durations of all videos
        durations = [get_video_duration(path) for path in video_paths]
        total_duration = sum(durations)
        print(f"DEBUG: Individual video durations: {durations}")
        print(f"DEBUG: Total duration: {total_duration:.2f}s")
        print(f"DEBUG: Target duration: {self.target_duration:.2f}s")
        
        # If total duration is already within margin of target, no trimming needed
        if abs(total_duration - self.target_duration) <= self.margin:
            print("DEBUG: Duration already matches target within margin")
            return [
                {'start_time': 0, 'end_time': duration, 'loop_count': 1}
                for duration in durations
            ]
        
        # If total duration is too short, we need to loop some videos
        if total_duration < self.target_duration:
            print(f"DEBUG: Duration too short, need {self.target_duration:.2f}s")
            
            # First, try using the same number of loops for all videos
            base_loops = math.floor(self.target_duration / total_duration)
            base_duration = total_duration * base_loops
            remaining_needed = self.target_duration - base_duration
            
            print(f"DEBUG: Using {base_loops} loops as base, need {remaining_needed:.2f}s more")
            
            # Sort videos by duration, longest first
            sorted_indices = sorted(range(len(durations)), key=lambda k: durations[k], reverse=True)
            
            # Start with base loops for all videos
            instructions = [
                {'start_time': 0, 'end_time': duration, 'loop_count': base_loops}
                for duration in durations
            ]
            
            # Add extra loops to longest videos until we reach target duration
            current_duration = base_duration
            for idx in sorted_indices:
                if abs(current_duration - self.target_duration) <= self.margin:
                    break
                    
                # Calculate how much more we need
                remaining = self.target_duration - current_duration
                
                # If adding one more complete loop of this video won't exceed target by too much
                if abs((current_duration + durations[idx]) - self.target_duration) <= self.margin:
                    instructions[idx]['loop_count'] += 1
                    current_duration += durations[idx]
                    print(f"DEBUG: Added full loop of video {idx} ({durations[idx]:.2f}s)")
                else:
                    # Add a partial loop
                    partial_duration = remaining
                    instructions[idx]['loop_count'] += 1
                    instructions[idx]['end_time'] = partial_duration
                    current_duration += partial_duration
                    print(f"DEBUG: Added partial loop of video {idx} ({partial_duration:.2f}s)")
            
            return instructions
        
        # If total duration is too long, we need to trim
        excess_duration = total_duration - self.target_duration
        print(f"DEBUG: Duration too long, trimming {excess_duration:.2f}s")
        
        # Calculate trim ratios for each video proportionally
        trim_ratios = [duration / total_duration for duration in durations]
        trim_amounts = [ratio * excess_duration for ratio in trim_ratios]
        
        # Calculate final durations and create trim instructions
        trim_instructions = []
        for duration, trim_amount in zip(durations, trim_amounts):
            new_duration = duration - trim_amount
            
            # Trim from both start and end equally
            trim_per_side = trim_amount / 2
            start_time = trim_per_side
            end_time = duration - trim_per_side
            
            trim_instructions.append({
                'start_time': start_time,
                'end_time': end_time,
                'loop_count': 1
            })
        
        return trim_instructions
    
    def validate_trim_instructions(self, video_paths: List[str], instructions: List[Dict[str, float]]) -> bool:
        """
        Validate that trim instructions will achieve target duration.
        
        Args:
            video_paths (List[str]): List of video paths
            instructions (List[Dict[str, float]]): List of trim instructions
            
        Returns:
            bool: True if instructions are valid, False otherwise
        """
        if len(video_paths) != len(instructions):
            return False
        
        total_duration = sum(
            (instruction['end_time'] - instruction['start_time']) * instruction['loop_count']
            for instruction in instructions
        )
        
        return abs(total_duration - self.target_duration) <= self.margin 