import os
import argparse
from typing import Optional, List
from pathlib import Path
import time
import requests
import json
from dotenv import load_dotenv
import subprocess
import logging
import psutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('processing.log'),
        logging.StreamHandler()
    ]
)

def log_system_info():
    """Log system resource usage"""
    process = psutil.Process()
    mem_info = process.memory_info()
    logging.info(f"Memory usage: {mem_info.rss / 1024 / 1024:.2f} MB")
    logging.info(f"CPU percent: {process.cpu_percent()}%")
    logging.info(f"Disk usage: {psutil.disk_usage('/').percent}%")

from file_system import get_video_files
from random_selector import select_random_videos
from duration_controller import DurationController, get_video_duration
from video_trimmer import VideoTrimmer
from video_connector import VideoConnector
from sound_remover import SoundRemover
from metadata_extractor import get_video_duration
from script_generator import generate_script_and_audio
from audio_attacher import AudioAttacher
from google_drive_handler import GoogleDriveHandler
from zapcap_handler import ZapCapHandler
from postiz_handler import PostizHandler
from upload_video_to_tiktok import upload_video

class VideoProcessor:
    def __init__(
        self,
        input_source: str,
        output_dir: str = "output_videos",
        min_videos: int = 2,
        max_videos: int = 6,
        remove_audio: bool = True,
        is_drive_url: bool = False
    ):
        """
        Initialize the VideoProcessor.
        
        Args:
            input_source (str): Directory containing input videos or Google Drive folder URL
            output_dir (str): Directory for output video (default: "output_videos")
            min_videos (int): Minimum number of videos to select (default: 2)
            max_videos (int): Maximum number of videos to select (default: 6)
            remove_audio (bool): Whether to remove audio from final video (default: True)
            is_drive_url (bool): Whether input_source is a Google Drive URL (default: False)
        """
        self.input_source = input_source
        self.output_dir = output_dir
        self.min_videos = min_videos
        self.max_videos = max_videos
        self.remove_audio = remove_audio
        self.is_drive_url = is_drive_url
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        self.trimmer = VideoTrimmer("trimmed_videos")
        self.connector = VideoConnector(output_dir)
        self.sound_remover = SoundRemover("muted_videos")
        self.audio_attacher = AudioAttacher(output_dir)
        
        if is_drive_url:
            self.drive_handler = GoogleDriveHandler()
        
    def get_video_files(self) -> List[str]:
        """Get video files from either local directory or Google Drive"""
        if self.is_drive_url:
            return self.drive_handler.download_videos(
                self.input_source,
                min_videos=self.min_videos,
                max_videos=self.max_videos
            )
        else:
            return get_video_files(self.input_source)
        
    def cleanup(self):
        """Clean up temporary files"""
        if self.is_drive_url and hasattr(self, 'drive_handler'):
            self.drive_handler.cleanup()
        
    def process(self, output_path: Optional[str] = None) -> str:
        """
        Process videos from input source to create final concatenated video.
        First generates script and audio, then matches video length to audio length.
        
        Args:
            output_path (Optional[str]): Path for final output video. If None, will generate one
            
        Returns:
            str: Path to the final output video
            
        Raises:
            FileNotFoundError: If input source doesn't exist
            ValueError: If not enough valid videos found
            RuntimeError: If processing fails
        """
        try:
            logging.info("Starting video processing")
            log_system_info()
            
            # Clean up any previous files
            logging.info("Cleaning up previous files")
            self.trimmer.clean_output_directory()
            self.connector.clean_output_directory()
            self.sound_remover.clean_output_directory()
            
            # First generate script and audio
            logging.info("Generating script and audio...")
            script, audio_path, audio_duration = generate_script_and_audio(self.output_dir)
            logging.info(f"Generated script (length: {len(script)} chars)")
            logging.info(f"Audio duration: {audio_duration:.2f} seconds")
            log_system_info()
            
            # Get list of video files
            logging.info("Getting video files...")
            if self.is_drive_url:
                video_files = self.drive_handler.download_videos(
                    self.input_source,
                    target_duration=audio_duration
                )
            else:
                video_files = get_video_files(self.input_source)
                
            if not video_files:
                raise ValueError(f"No video files found in {self.input_source}")
            logging.info(f"Found {len(video_files)} video files")
            
            # If using local files, we still need to select and trim them
            if not self.is_drive_url:
                # Initialize duration controller with audio duration as target
                self.duration_controller = DurationController(audio_duration)
                
                # Randomly select videos
                logging.info(f"Selecting {self.min_videos}-{self.max_videos} videos...")
                selected_videos = select_random_videos(
                    video_files,
                    self.min_videos,
                    self.max_videos
                )
                logging.info(f"Selected {len(selected_videos)} videos")
                
                # Calculate trim instructions to match audio duration
                logging.info("Calculating trim instructions...")
                trim_instructions = self.duration_controller.calculate_trim_instructions(selected_videos)
                logging.info("Generated trim instructions")
                
                # Trim videos
                logging.info("Trimming videos...")
                trimmed_videos = []
                loop_counts = []
                for i, (video_path, instructions) in enumerate(zip(selected_videos, trim_instructions), 1):
                    logging.info(f"Processing segment {i}/{len(selected_videos)}: {os.path.basename(video_path)}")
                    logging.info(f"Trim range: {instructions['start_time']:.2f}s to {instructions['end_time']:.2f}s")
                    log_system_info()
                    
                    trimmed_path = self.trimmer.trim_video(
                        video_path,
                        instructions['start_time'],
                        instructions['end_time']
                    )
                    trimmed_videos.append(trimmed_path)
                    loop_counts.append(instructions['loop_count'])
                    logging.info(f"Completed segment {i}")
                
                video_files = trimmed_videos
            
            # Concatenate videos
            logging.info("Concatenating videos...")
            log_system_info()
            concatenated_video = self.connector.concatenate_videos(
                video_files,
                None if self.remove_audio else output_path,  # Use temporary path if we need to remove audio
                loop_counts=[1] * len(video_files)  # Add each video once
            )
            
            # Remove audio if requested
            if self.remove_audio:
                logging.info("Removing audio...")
                log_system_info()
                final_video = self.sound_remover.remove_audio(concatenated_video, output_path)
            else:
                final_video = concatenated_video
            
            # Verify final duration
            duration = get_video_duration(final_video)
            logging.info(f"Created final video (duration: {duration:.2f}s)")
            
            # Attach the voiceover
            logging.info("Attaching voiceover to video...")
            log_system_info()
            final_output_path = os.path.join(self.output_dir, "final_output_with_voice.mp4")
            final_video = self.audio_attacher.attach_audio(final_video, audio_path, final_output_path)
            logging.info(f"Final video with voiceover saved to: {final_video}")
            
            logging.info("Video processing completed successfully")
            log_system_info()
            return final_video
            
        except Exception as e:
            logging.error(f"Error during video processing: {str(e)}", exc_info=True)
            raise
        finally:
            # Clean up
            self.cleanup()

class VideoTrimmer:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def clean_output_directory(self):
        """Clean up any existing files in the output directory"""
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    def trim_video(self, video_path, start_time, end_time):
        """Trim video to specified time range and optionally adjust speed"""
        # Create output filename
        output_filename = f"segment_{os.path.basename(video_path)}"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Build FFmpeg command with resolution scaling for high-res videos
        command = [
            'ffmpeg', '-i', video_path,
            '-ss', str(start_time),
            '-t', str(end_time - start_time),
            '-vf', 'scale=min(1920,iw):min(1080,ih):force_original_aspect_ratio=decrease',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-c:a', 'aac',
            '-progress', 'pipe:1',  # Output progress to stdout
            '-nostats',             # Disable default stats
            output_path
        ]
        
        try:
            logging.info(f"Starting FFmpeg: {' '.join(command)}")
            start_time = time.time()
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Monitor progress
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    logging.debug(f"FFmpeg progress: {line.strip()}")
            
            # Get any errors
            _, stderr = process.communicate()
            if stderr:
                logging.info(f"FFmpeg output: {stderr}")
            
            end_time = time.time()
            duration = end_time - start_time
            logging.info(f"FFmpeg completed in {duration:.2f} seconds")
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)
                
            return output_path
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Error trimming video: {e}", exc_info=True)
            raise
        except Exception as e:
            logging.error(f"Unexpected error trimming video: {e}", exc_info=True)
            raise

def main():
    parser = argparse.ArgumentParser(description="Process and concatenate random video segments")
    parser.add_argument("input_source", help="Directory containing input videos or Google Drive folder URL")
    parser.add_argument("--output", "-o", help="Path for output video")
    parser.add_argument("--min-videos", type=int, default=2,
                      help="Minimum number of videos to select (default: 2)")
    parser.add_argument("--max-videos", type=int, default=6,
                      help="Maximum number of videos to select (default: 6)")
    parser.add_argument("--keep-audio", action="store_true",
                      help="Keep audio in the final video (default: remove audio)")
    parser.add_argument("--drive-url", action="store_true",
                      help="Treat input source as Google Drive folder URL")
    parser.add_argument("--add-captions", action="store_true",
                      help="Add captions to the video using ZapCap and upload to TikTok")
    
    args = parser.parse_args()
    
    processor = VideoProcessor(
        args.input_source,
        min_videos=args.min_videos,
        max_videos=args.max_videos,
        remove_audio=not args.keep_audio,
        is_drive_url=args.drive_url
    )
    
    try:
        # Process the video
        final_output = processor.process(args.output)
        print(f"\nVideo processing completed! Final video saved to: {final_output}")
        
        # Only proceed with captions and TikTok upload if --add-captions is specified
        if args.add_captions:
            # Send to ZapCap for captions
            print("\nSending to ZapCap for captions...")
            zapcap_api_key = os.getenv('ZAPCAP_API_KEY')
            if not zapcap_api_key:
                raise ValueError("Missing ZAPCAP_API_KEY in .env file")
            
            zapcap = ZapCapHandler(zapcap_api_key)
            template_id = "07ffd4b8-4e1a-4ee3-8921-d58802953bcd"

            # Upload video to ZapCap
            upload_result = zapcap.upload_video(final_output)
            video_id = upload_result.get("id")
            print("Upload to ZapCap successful!")
            print("Video ID:", video_id)
            
            # Create captioning task
            task_result = zapcap.create_task(video_id, template_id, language="en", top_position=30)
            task_id = task_result.get("taskId")
            print("Captioning task created!")
            print("Task ID:", task_id)
            
            # Monitor task progress
            transcript_approved = False
            captioned_video_url = None
            while True:
                task_status = zapcap.get_task_status(video_id, task_id)
                status = task_status.get("status")
                print(f"ZapCap Status: {status}")
                
                if status == "transcriptionCompleted" and not transcript_approved:
                    print("Approving transcript...")
                    zapcap.approve_transcript(video_id, task_id)
                    transcript_approved = True
                    print("Transcript approved!")
                elif status == "completed":
                    print("Video captioning completed!")
                    captioned_video_url = task_status.get("downloadUrl")
                    print("Download URL:", captioned_video_url)
                    break
                elif status in ["failed", "error"]:
                    print("Captioning task failed:", task_status.get("error"))
                    break
                    
                time.sleep(5)  # Wait 5 seconds before checking again

            # If we have a captioned video, download it and upload to TikTok
            if captioned_video_url:
                print("\nDownloading captioned video...")
                response = requests.get(captioned_video_url)
                captioned_video_path = os.path.join(processor.output_dir, "final_with_captions.mp4")
                with open(captioned_video_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded captioned video to: {captioned_video_path}")
                
                # Get access token for TikTok upload
                access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
                if not access_token:
                    raise ValueError("Missing TIKTOK_ACCESS_TOKEN in .env file")
                
                # Upload to TikTok
                print("\nUploading to TikTok...")
                print(f"Using access token: {access_token}")
                upload_video(captioned_video_path, access_token)

        print("\nProcess completed successfully!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 