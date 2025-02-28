import os
import subprocess
from typing import Optional
import logging

class AudioAttacher:
    def __init__(self, output_dir: str = "output_videos"):
        """
        Initialize AudioAttacher
        
        Args:
            output_dir (str): Directory for output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def attach_audio(self, video_path: str, audio_path: str, output_path: Optional[str] = None) -> str:
        """
        Attach audio file to video file using FFmpeg
        
        Args:
            video_path (str): Path to the input video file
            audio_path (str): Path to the audio file to attach
            output_path (Optional[str]): Path for the output video. If None, will generate one
            
        Returns:
            str: Path to the output video with attached audio
            
        Raises:
            FileNotFoundError: If input files don't exist
            RuntimeError: If audio attachment fails
        """
        try:
            # Check if input files exist
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Generate output path if not provided
            if output_path is None:
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_path = os.path.join(self.output_dir, f"{base_name}_with_voiceover.mp4")
            
            logging.info(f"Attaching audio to video using FFmpeg...")
            logging.info(f"Video: {video_path}")
            logging.info(f"Audio: {audio_path}")
            logging.info(f"Output: {output_path}")
            
            # Build FFmpeg command
            command = [
                'ffmpeg',
                '-i', video_path,      # Input video
                '-i', audio_path,      # Input audio
                '-c:v', 'copy',        # Copy video stream without re-encoding
                '-c:a', 'aac',         # Convert audio to AAC
                '-shortest',           # Match duration to shortest stream
                output_path
            ]
            
            # Run FFmpeg
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Get output
            _, stderr = process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {stderr}")
            
            logging.info("Successfully attached audio to video")
            return output_path
            
        except Exception as e:
            error_msg = f"Failed to attach audio: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)

def main():
    import argparse
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Attach audio to video file')
    parser.add_argument('video_path', help='Path to the input video file')
    parser.add_argument('audio_path', help='Path to the audio file to attach')
    parser.add_argument('--output', '-o', help='Path for output video (optional)')
    
    args = parser.parse_args()
    
    attacher = AudioAttacher()
    try:
        output_path = attacher.attach_audio(args.video_path, args.audio_path, args.output)
        logging.info(f"Success! Final video saved to: {output_path}")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 