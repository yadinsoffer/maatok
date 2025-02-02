from typing import List, Dict, Tuple
from metadata_extractor import get_video_duration
import math

class DurationController:
    def __init__(self, min_duration: float = 21.0, max_duration: float = 28.0):
        """
        Initialize the DurationController with target duration bounds.
        
        Args:
            min_duration (float): Minimum target duration in seconds (default: 21.0)
            max_duration (float): Maximum target duration in seconds (default: 28.0)
        """
        self.min_duration = min_duration
        self.max_duration = max_duration
    
    def calculate_trim_instructions(self, video_paths: List[str]) -> List[Dict[str, float]]:
        """
        Calculate trim instructions for a list of videos to achieve target duration.
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
        
        # If total duration is already within bounds, no trimming needed
        if self.min_duration <= total_duration <= self.max_duration:
            print("DEBUG: Duration already within bounds")
            return [
                {'start_time': 0, 'end_time': duration, 'loop_count': 1}
                for duration in durations
            ]
        
        # If total duration is too short, we need to loop some videos
        if total_duration < self.min_duration:
            print(f"DEBUG: Duration too short, need at least {self.min_duration:.2f}s")
            
            # First, try using the same number of loops for all videos
            base_loops = math.floor(self.min_duration / total_duration)
            base_duration = total_duration * base_loops
            remaining_needed = self.min_duration - base_duration
            
            print(f"DEBUG: Using {base_loops} loops as base, need {remaining_needed:.2f}s more")
            
            # Sort videos by duration, longest first
            sorted_indices = sorted(range(len(durations)), key=lambda k: durations[k], reverse=True)
            
            # Start with base loops for all videos
            instructions = [
                {'start_time': 0, 'end_time': duration, 'loop_count': base_loops}
                for duration in durations
            ]
            
            # Add extra loops to longest videos until we reach minimum duration
            current_duration = base_duration
            for idx in sorted_indices:
                if current_duration >= self.min_duration:
                    break
                    
                # Calculate how much more we need
                remaining = self.min_duration - current_duration
                
                # If adding one more complete loop of this video won't exceed max_duration
                if current_duration + durations[idx] <= self.max_duration:
                    instructions[idx]['loop_count'] += 1
                    current_duration += durations[idx]
                    print(f"DEBUG: Added full loop of video {idx} ({durations[idx]:.2f}s)")
                else:
                    # Add a partial loop
                    partial_duration = min(remaining, durations[idx])
                    instructions[idx]['loop_count'] += 1
                    instructions[idx]['end_time'] = partial_duration
                    current_duration += partial_duration
                    print(f"DEBUG: Added partial loop of video {idx} ({partial_duration:.2f}s)")
            
            # Calculate expected duration
            expected_duration = sum(
                (instr['end_time'] - instr['start_time']) * instr['loop_count']
                for instr in instructions
            )
            print(f"DEBUG: Expected final duration: {expected_duration:.2f}s")
            
            return instructions
        
        # If total duration is too long, we need to trim
        target_duration = (self.min_duration + self.max_duration) / 2
        excess_duration = total_duration - target_duration
        
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
        
        # Calculate expected duration
        expected_duration = sum(
            (instr['end_time'] - instr['start_time']) * instr['loop_count']
            for instr in trim_instructions
        )
        print(f"DEBUG: Expected final duration: {expected_duration:.2f}s")
        
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
        
        return self.min_duration <= total_duration <= self.max_duration 