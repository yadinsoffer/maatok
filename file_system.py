import os
from pathlib import Path
from typing import List

VALID_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.wmv'}

def get_video_files(directory: str) -> List[str]:
    """
    Scan a directory and return a list of valid video file paths.
    
    Args:
        directory (str): Path to the directory to scan
        
    Returns:
        List[str]: List of absolute paths to video files
        
    Raises:
        FileNotFoundError: If the directory doesn't exist
        NotADirectoryError: If the path is not a directory
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    
    video_files = []
    directory_path = Path(directory)
    
    for file_path in directory_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in VALID_VIDEO_EXTENSIONS:
            video_files.append(str(file_path.absolute()))
    
    return video_files

def validate_video_files(video_files: List[str]) -> List[str]:
    """
    Validate that all files in the list exist and are valid video files.
    
    Args:
        video_files (List[str]): List of video file paths
        
    Returns:
        List[str]: List of valid video file paths
    """
    valid_files = []
    for file_path in video_files:
        path = Path(file_path)
        if path.exists() and path.is_file() and path.suffix.lower() in VALID_VIDEO_EXTENSIONS:
            valid_files.append(str(path.absolute()))
    return valid_files 