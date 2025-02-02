import os
import argparse
from typing import Optional
from pathlib import Path

from file_system import get_video_files
from random_selector import select_random_videos
from duration_controller import DurationController
from video_trimmer import VideoTrimmer
from video_connector import VideoConnector
from sound_remover import SoundRemover
from metadata_extractor import get_video_duration
from script_generator import generate_script
from text_to_speech import TextToSpeech
from audio_attacher import AudioAttacher

class VideoProcessor:
    def __init__(
        self,
        input_dir: str,
        output_dir: str = "output_videos",
        min_duration: float = 21.0,
        max_duration: float = 28.0,
        min_videos: int = 2,
        max_videos: int = 6,
        remove_audio: bool = True
    ):
        """
        Initialize the VideoProcessor.
        
        Args:
            input_dir (str): Directory containing input videos
            output_dir (str): Directory for output video (default: "output_videos")
            min_duration (float): Minimum target duration in seconds (default: 21.0)
            max_duration (float): Maximum target duration in seconds (default: 28.0)
            min_videos (int): Minimum number of videos to select (default: 2)
            max_videos (int): Maximum number of videos to select (default: 6)
            remove_audio (bool): Whether to remove audio from final video (default: True)
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.min_videos = min_videos
        self.max_videos = max_videos
        self.remove_audio = remove_audio
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        self.duration_controller = DurationController(min_duration, max_duration)
        self.trimmer = VideoTrimmer("trimmed_videos")
        self.connector = VideoConnector(output_dir)
        self.sound_remover = SoundRemover("muted_videos")
        self.tts = TextToSpeech()
        self.audio_attacher = AudioAttacher(output_dir)
    
    def process(self, output_path: Optional[str] = None) -> str:
        """
        Process videos from input directory to create final concatenated video.
        If videos are too short, they will be looped to reach the target duration.
        
        Args:
            output_path (Optional[str]): Path for final output video. If None, will generate one
            
        Returns:
            str: Path to the final output video
            
        Raises:
            FileNotFoundError: If input directory doesn't exist
            ValueError: If not enough valid videos found
            RuntimeError: If processing fails
        """
        # Clean up any previous files
        self.trimmer.clean_output_directory()
        self.connector.clean_output_directory()
        self.sound_remover.clean_output_directory()
        
        try:
            # Get list of video files
            print("Scanning for video files...")
            video_files = get_video_files(self.input_dir)
            if not video_files:
                raise ValueError(f"No video files found in {self.input_dir}")
            print(f"Found {len(video_files)} video files")
            
            # Randomly select videos
            print(f"Selecting {self.min_videos}-{self.max_videos} videos...")
            selected_videos = select_random_videos(
                video_files,
                self.min_videos,
                self.max_videos
            )
            print(f"Selected {len(selected_videos)} videos")
            
            # Calculate trim instructions
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
            
            # Generate script for the video
            print("\nGenerating voiceover script...")
            script = generate_script(final_video)
            if script:
                print("\nGenerated Script:")
                print("-" * 80)
                print(script)
                print("-" * 80)
                
                try:
                    # Create base names for output files
                    base_path = os.path.join(self.output_dir, "final_output")
                    script_path = f"{base_path}_script.txt"
                    audio_path = f"{base_path}_voice.mp3"
                    final_output_path = f"{base_path}_with_voice.mp4"
                    
                    # Save script to file
                    print(f"\nSaving script to: {script_path}")
                    with open(script_path, "w") as f:
                        f.write(script)
                    
                    # Generate voiceover audio
                    print("\nGenerating voiceover audio...")
                    self.tts.convert_text_to_speech(script, audio_path)
                    
                    # Attach voiceover to video
                    print("\nAttaching voiceover to video...")
                    final_video = self.audio_attacher.attach_audio(final_video, audio_path, final_output_path)
                    print(f"Final video with voiceover saved to: {final_video}")
                    
                except Exception as e:
                    print(f"Warning: Error during script/audio generation: {str(e)}")
                    print("Continuing with silent video...")
            
            return final_video
            
        except Exception as e:
            # Clean up on error
            self.trimmer.clean_output_directory()
            self.connector.clean_output_directory()
            self.sound_remover.clean_output_directory()
            raise

def main():
    parser = argparse.ArgumentParser(description="Process and concatenate random video segments")
    parser.add_argument("input_dir", help="Directory containing input videos")
    parser.add_argument("--output", "-o", help="Path for output video")
    parser.add_argument("--min-duration", type=float, default=21.0,
                      help="Minimum target duration in seconds (default: 21.0)")
    parser.add_argument("--max-duration", type=float, default=28.0,
                      help="Maximum target duration in seconds (default: 28.0)")
    parser.add_argument("--min-videos", type=int, default=2,
                      help="Minimum number of videos to select (default: 2)")
    parser.add_argument("--max-videos", type=int, default=6,
                      help="Maximum number of videos to select (default: 6)")
    parser.add_argument("--keep-audio", action="store_true",
                      help="Keep audio in the final video (default: remove audio)")
    
    args = parser.parse_args()
    
    processor = VideoProcessor(
        args.input_dir,
        min_duration=args.min_duration,
        max_duration=args.max_duration,
        min_videos=args.min_videos,
        max_videos=args.max_videos,
        remove_audio=not args.keep_audio
    )
    
    try:
        output_path = processor.process(args.output)
        print(f"\nSuccess! Final video saved to: {output_path}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 