import os
import subprocess
from typing import Optional

class VideoTrimmer:
    def __init__(self, output_dir: str = "trimmed_videos"):
        """
        Initialize the VideoTrimmer.
        
        Args:
            output_dir (str): Directory to store trimmed videos (default: "trimmed_videos")
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def trim_video(
        self,
        input_path: str,
        start_time: float,
        end_time: float,
        output_path: Optional[str] = None
    ) -> str:
        """
        Trim a video file to the specified duration.
        
        Args:
            input_path (str): Path to the input video file
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            output_path (Optional[str]): Path for the output file. If None, will generate one
            
        Returns:
            str: Path to the trimmed video file
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            RuntimeError: If trimming fails
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        if output_path is None:
            # Generate output path in the output directory
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(
                self.output_dir,
                f"{name}_trimmed{ext}"
            )
        
        try:
            # Construct ffmpeg command with re-encoding for accurate trimming
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ss', str(start_time),
                '-t', str(end_time - start_time),
                '-c:v', 'libx264',  # Re-encode video
                '-c:a', 'aac',      # Re-encode audio
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
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to trim video: {str(e)}")
    
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