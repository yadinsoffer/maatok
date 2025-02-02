import os
import subprocess
from typing import Optional

class SoundRemover:
    def __init__(self, output_dir: str = "muted_videos"):
        """
        Initialize the SoundRemover.
        
        Args:
            output_dir (str): Directory to store muted videos (default: "muted_videos")
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def remove_audio(
        self,
        input_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Remove audio from a video file.
        
        Args:
            input_path (str): Path to the input video file
            output_path (Optional[str]): Path for the output file. If None, will generate one
            
        Returns:
            str: Path to the muted video file
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            RuntimeError: If audio removal fails
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        if output_path is None:
            # Generate output path in the output directory
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(
                self.output_dir,
                f"{name}_muted{ext}"
            )
        
        try:
            # Construct ffmpeg command to remove audio
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'copy',     # Copy video stream without re-encoding
                '-an',              # Remove audio
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
            raise RuntimeError(f"Failed to remove audio: {str(e)}")
    
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