import os
import tempfile
import subprocess
from typing import List, Optional, Dict

class VideoConnector:
    def __init__(self, output_dir: str = "output_videos"):
        """
        Initialize the VideoConnector.
        
        Args:
            output_dir (str): Directory to store output videos (default: "output_videos")
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def concatenate_videos(
        self,
        video_paths: List[str],
        output_path: Optional[str] = None,
        loop_counts: Optional[List[int]] = None
    ) -> str:
        """
        Concatenate multiple video files into a single video, with optional looping.
        
        Args:
            video_paths (List[str]): List of video file paths to concatenate
            output_path (Optional[str]): Path for the output file. If None, will generate one
            loop_counts (Optional[List[int]]): List of how many times to loop each video
            
        Returns:
            str: Path to the concatenated video file
            
        Raises:
            ValueError: If video_paths is empty
            FileNotFoundError: If any input file doesn't exist
            RuntimeError: If concatenation fails
        """
        if not video_paths:
            raise ValueError("No video paths provided")
        
        # Verify all input files exist
        for path in video_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Video file not found: {path}")
        
        if output_path is None:
            # Generate output path
            output_path = os.path.join(
                self.output_dir,
                "concatenated_video.mp4"
            )
        
        # Default to no looping if not specified
        if loop_counts is None:
            loop_counts = [1] * len(video_paths)
        
        try:
            # Create a temporary file listing the videos to concatenate
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for video_path, loop_count in zip(video_paths, loop_counts):
                    # Add the video path loop_count times
                    for _ in range(loop_count):
                        f.write(f"file '{os.path.abspath(video_path)}'\n")
                concat_list_path = f.name
            
            try:
                # Construct ffmpeg command
                cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_list_path,
                    '-c:v', 'libx264',  # Use H.264 codec for video
                    '-c:a', 'aac',      # Use AAC codec for audio
                    '-y',               # Overwrite output file if it exists
                    output_path
                ]
                
                # Run ffmpeg command
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                if not os.path.exists(output_path):
                    raise RuntimeError("Failed to create output file")
                
                return output_path
                
            finally:
                # Clean up the temporary file
                os.unlink(concat_list_path)
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to concatenate videos: {str(e)}")
    
    def clean_output_directory(self):
        """
        Remove all files from the output directory.
        """
        if os.path.exists(self.output_dir):
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {str(e)}") 