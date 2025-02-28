import os
import argparse
from google_drive_handler import GoogleDriveHandler
from video_connector import VideoConnector
from dotenv import load_dotenv

def test_video_cuts(drive_url: str, target_duration: float = 30.0):
    """
    Test video cutting and concatenation with a fixed duration.
    
    Args:
        drive_url (str): Google Drive folder URL
        target_duration (float): Target duration in seconds (default: 30s)
    """
    try:
        print(f"\nStarting video cut test with target duration: {target_duration}s")
        print(f"Using Google Drive folder: {drive_url}")
        
        # Initialize handlers
        drive_handler = GoogleDriveHandler()
        connector = VideoConnector("output_videos")
        
        # Clean output directory
        connector.clean_output_directory()
        
        # Download and process video segments
        print("\nProcessing video segments...")
        video_segments = drive_handler.download_videos(
            folder_url=drive_url,
            target_duration=target_duration
        )
        
        # Concatenate segments
        print("\nConcatenating segments...")
        final_video = connector.concatenate_videos(video_segments)
        
        print(f"\nTest complete! Final video saved to: {final_video}")
        print("Please check the video for:")
        print("1. Correct duration")
        print("2. Smooth transitions between cuts")
        print("3. No frozen frames")
        print("4. All segments playing correctly")
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
    finally:
        # Clean up
        if 'drive_handler' in locals():
            drive_handler.cleanup()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test video cutting and concatenation")
    parser.add_argument("drive_url", help="Google Drive folder URL")
    parser.add_argument("--duration", type=float, default=30.0,
                      help="Target duration in seconds (default: 30.0)")
    
    args = parser.parse_args()
    test_video_cuts(args.drive_url, args.duration) 