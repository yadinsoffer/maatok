from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import os
from typing import Optional

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
        Attach audio file to video file
        
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
            # Generate output path if not provided
            if output_path is None:
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_path = os.path.join(self.output_dir, f"{base_name}_with_voiceover.mp4")
            
            # Load video and audio
            print(f"Loading video: {video_path}")
            video = VideoFileClip(video_path)
            print(f"Loading audio: {audio_path}")
            audio = AudioFileClip(audio_path)
            
            # Create composite with audio
            print("Attaching audio to video...")
            final_video = video.set_audio(audio)
            
            # Write output file
            print(f"Writing output to: {output_path}")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Close clips to free up resources
            video.close()
            audio.close()
            
            print("Successfully attached audio to video")
            return output_path
            
        except Exception as e:
            print(f"An error occurred while attaching audio: {str(e)}")
            # Clean up resources in case of error
            try:
                video.close()
                audio.close()
            except:
                pass
            raise RuntimeError(f"Failed to attach audio: {str(e)}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Attach audio to video file')
    parser.add_argument('video_path', help='Path to the input video file')
    parser.add_argument('audio_path', help='Path to the audio file to attach')
    parser.add_argument('--output', '-o', help='Path for output video (optional)')
    
    args = parser.parse_args()
    
    attacher = AudioAttacher()
    try:
        output_path = attacher.attach_audio(args.video_path, args.audio_path, args.output)
        print(f"\nSuccess! Final video saved to: {output_path}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 