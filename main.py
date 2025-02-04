import os
import argparse
from typing import Optional, List
from pathlib import Path

from file_system import get_video_files
from random_selector import select_random_videos
from duration_controller import DurationController
from video_trimmer import VideoTrimmer
from video_connector import VideoConnector
from sound_remover import SoundRemover
from metadata_extractor import get_video_duration
from script_generator import generate_script_and_audio
from audio_attacher import AudioAttacher
from google_drive_handler import GoogleDriveHandler

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
            return self.drive_handler.download_videos(self.input_source)
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
            # Clean up any previous files
            self.trimmer.clean_output_directory()
            self.connector.clean_output_directory()
            self.sound_remover.clean_output_directory()
            
            # First generate script and audio
            print("\nGenerating script and audio...")
            script, audio_path, audio_duration = generate_script_and_audio(self.output_dir)
            print("\nGenerated Script:")
            print("-" * 80)
            print(script)
            print("-" * 80)
            print(f"Audio duration: {audio_duration:.2f} seconds")
            
            # Initialize duration controller with audio duration as target
            self.duration_controller = DurationController(audio_duration)
            
            # Get list of video files
            print("\nGetting video files...")
            video_files = self.get_video_files()
            if not video_files:
                raise ValueError(f"No video files found in {self.input_source}")
            print(f"Found {len(video_files)} video files")
            
            # Randomly select videos
            print(f"Selecting {self.min_videos}-{self.max_videos} videos...")
            selected_videos = select_random_videos(
                video_files,
                self.min_videos,
                self.max_videos
            )
            print(f"Selected {len(selected_videos)} videos")
            
            # Calculate trim instructions to match audio duration
            print("Calculating trim instructions...")
            trim_instructions = self.duration_controller.calculate_trim_instructions(selected_videos)
            print("Generated trim instructions")
            
            # Trim videos
            print("Trimming videos...")
            trimmed_videos = []
            loop_counts = []
            for video_path, instructions in zip(selected_videos, trim_instructions):
                trimmed_path = self.trimmer.trim_video(
                    video_path,
                    instructions['start_time'],
                    instructions['end_time']
                )
                trimmed_videos.append(trimmed_path)
                loop_counts.append(instructions['loop_count'])
            print(f"Trimmed {len(trimmed_videos)} videos")
            
            # Concatenate videos
            print("Concatenating videos...")
            concatenated_video = self.connector.concatenate_videos(
                trimmed_videos,
                None if self.remove_audio else output_path,  # Use temporary path if we need to remove audio
                loop_counts=loop_counts
            )
            
            # Remove audio if requested
            if self.remove_audio:
                print("Removing audio...")
                final_video = self.sound_remover.remove_audio(concatenated_video, output_path)
            else:
                final_video = concatenated_video
            
            # Verify final duration
            duration = get_video_duration(final_video)
            print(f"Created final video (duration: {duration:.2f}s)")
            
            # Attach the voiceover
            print("\nAttaching voiceover to video...")
            final_output_path = os.path.join(self.output_dir, "final_output_with_voice.mp4")
            final_video = self.audio_attacher.attach_audio(final_video, audio_path, final_output_path)
            print(f"Final video with voiceover saved to: {final_video}")
            
            return final_video
            
        finally:
            # Clean up
            self.cleanup()

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
    
    args = parser.parse_args()
    
    processor = VideoProcessor(
        args.input_source,
        min_videos=args.min_videos,
        max_videos=args.max_videos,
        remove_audio=not args.keep_audio,
        is_drive_url=args.drive_url
    )
    
    try:
        output_path = processor.process(args.output)
        print(f"\nSuccess! Final video saved to: {output_path}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 