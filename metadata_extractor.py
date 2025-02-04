import subprocess
import json
import os
from typing import Dict, Union, Optional

def extract_video_metadata(video_path: str) -> Dict[str, Union[float, str]]:
    """
    Extract metadata from a video file using ffprobe.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        Dict[str, Union[float, str]]: Dictionary containing video metadata
            {
                'duration': float,  # Duration in seconds
                'format': str,      # Video format
                'width': int,       # Video width
                'height': int       # Video height
            }
            
    Raises:
        FileNotFoundError: If the video file doesn't exist
        RuntimeError: If ffprobe fails to extract metadata
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    try:
        # Construct ffprobe command
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        # Run ffprobe command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse the JSON output
        probe_data = json.loads(result.stdout)
        
        # Extract video stream information
        video_stream = None
        for stream in probe_data['streams']:
            if stream['codec_type'] == 'video':
                video_stream = stream
                break
        
        if not video_stream:
            raise RuntimeError(f"No video stream found in {video_path}")
        
        # Get format information
        format_info = probe_data['format']
        
        # Extract relevant metadata
        metadata = {
            'duration': float(format_info.get('duration', 0)),
            'format': format_info.get('format_name', ''),
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0))
        }
        
        return metadata
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to extract metadata: {str(e)}")
    except (json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(f"Failed to parse metadata: {str(e)}")

def get_duration(file_path: str) -> float:
    """
    Get the duration of a media file (video or audio).
    
    Args:
        file_path (str): Path to the media file
        
    Returns:
        float: Duration in seconds
        
    Raises:
        ValueError: If duration cannot be extracted
    """
    try:
        # Use ffprobe to get media information
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise ValueError(f"ffprobe failed: {result.stderr}")
        
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        return duration
        
    except Exception as e:
        raise ValueError(f"Could not extract duration from {file_path}: {str(e)}")

def get_video_duration(file_path: str) -> float:
    """
    Get the duration of a video file.
    For backward compatibility, this now just calls get_duration.
    
    Args:
        file_path (str): Path to the video file
        
    Returns:
        float: Duration in seconds
    """
    return get_duration(file_path) 