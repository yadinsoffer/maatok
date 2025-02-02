import random
from typing import List

def select_random_videos(video_files: List[str], min_count: int = 2, max_count: int = 6) -> List[str]:
    """
    Randomly select between min_count and max_count videos from the provided list.
    
    Args:
        video_files (List[str]): List of video file paths to choose from
        min_count (int): Minimum number of videos to select (default: 2)
        max_count (int): Maximum number of videos to select (default: 6)
        
    Returns:
        List[str]: List of randomly selected video file paths
        
    Raises:
        ValueError: If video_files is empty or if min_count > max_count
        ValueError: If len(video_files) < min_count
    """
    if not video_files:
        raise ValueError("No video files provided")
    
    if min_count > max_count:
        raise ValueError(f"min_count ({min_count}) cannot be greater than max_count ({max_count})")
    
    if len(video_files) < min_count:
        raise ValueError(f"Not enough video files. Need at least {min_count}, but only {len(video_files)} provided")
    
    # Determine how many videos to select
    selection_count = random.randint(min_count, min(max_count, len(video_files)))
    
    # Randomly select the videos
    selected_videos = random.sample(video_files, selection_count)
    
    return selected_videos 