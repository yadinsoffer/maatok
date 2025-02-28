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
    
    def _preprocess_video(self, input_path: str, temp_dir: str) -> str:
        """
        Preprocess a video segment to ensure consistent format.
        
        Args:
            input_path (str): Path to input video
            temp_dir (str): Directory for temporary files
            
        Returns:
            str: Path to preprocessed video
        """
        output_path = os.path.join(
            temp_dir,
            f"prep_{os.path.basename(input_path)}"
        )
        
        # First check if input video has valid streams
        probe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',  # Select first video stream
            '-show_entries', 'stream=codec_type,width,height,duration',
            '-of', 'json',
            input_path
        ]
        
        try:
            probe_result = subprocess.run(
                probe_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # If we can't probe the file or no video stream found, skip preprocessing
            if "error" in probe_result.stderr.lower() or "video" not in probe_result.stdout.lower():
                print(f"Warning: Could not probe video stream in {input_path}: {probe_result.stderr}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to probe {input_path}: {e.stderr}")
            return None
        
        # Construct FFmpeg command with better error handling
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-i', input_path,
            '-vf', 'format=yuv420p',  # Force pixel format
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-fps_mode', 'cfr',  # Constant frame rate
            '-r', '30',       # Force 30fps
            '-movflags', '+faststart',
            '-an',           # Remove audio
            '-f', 'mp4',     # Force MP4 format
            output_path
        ]
        
        try:
            # Run FFmpeg with full error output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Verify the output was created and has valid video
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                verify_cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-select_streams', 'v:0',
                    '-show_entries', 'stream=codec_type',
                    '-of', 'json',
                    output_path
                ]
                
                verify_result = subprocess.run(
                    verify_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                if "codec_type" in verify_result.stdout and "video" in verify_result.stdout:
                    return output_path
            
            print(f"Warning: Failed to verify output for {input_path}")
            return None
            
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to preprocess {input_path}:")
            print(f"FFmpeg error: {e.stderr}")
            return None
    
    def concatenate_videos(self, video_files, output_path=None, loop_counts=None):
        """
        Concatenate multiple video files into one
        
        Args:
            video_files (list): List of video file paths to concatenate
            output_path (str): Path for output video. If None, will generate one
            loop_counts (list): How many times to loop each video. If None, play once
            
        Returns:
            str: Path to concatenated video
        """
        if not video_files:
            raise ValueError("No video files provided")
            
        if output_path is None:
            output_path = os.path.join(self.output_dir, "concatenated_video.mp4")
            
        if loop_counts is None:
            loop_counts = [1] * len(video_files)
            
        # Create temporary file with list of videos
        list_file = os.path.join(self.output_dir, "video_list.txt")
        with open(list_file, "w") as f:
            for video_path, count in zip(video_files, loop_counts):
                for _ in range(count):
                    f.write(f"file '{video_path}'\n")
                    
        # Build FFmpeg command with conservative resource settings
        command = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease',
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '23',
            '-maxrate', '8M',
            '-bufsize', '16M',
            '-max_muxing_queue_size', '1024',
            '-c:a', 'aac',
            output_path
        ]
        
        try:
            # Run FFmpeg command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            if not os.path.exists(output_path):
                raise RuntimeError("Failed to create output file")
            
            # Verify the output video
            probe_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                output_path
            ]
            
            probe_result = subprocess.run(
                probe_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            duration = float(probe_result.stdout.strip())
            if duration < 1:  # If video is too short, something went wrong
                raise RuntimeError("Output video duration is invalid")
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg error: {e.stderr}"
            if "Error opening filters!" in e.stderr:
                error_msg += "\nFilter chain error - check video compatibility"
            elif "Invalid data found" in e.stderr:
                error_msg += "\nCorrupt input data - check source videos"
            raise RuntimeError(f"Failed to concatenate videos: {error_msg}")
        
        except Exception as e:
            raise RuntimeError(f"Unexpected error during concatenation: {str(e)}")
    
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