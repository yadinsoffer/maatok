#!/usr/bin/env python3
import os
import sys
from datetime import datetime
from main import VideoProcessor

def main():
    # Configure logging to file
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Redirect stdout and stderr to log file
    sys.stdout = sys.stderr = open(log_file, 'w')
    
    try:
        print(f"Starting video processing at {datetime.now()}")
        
        # Get Google Drive folder URL from environment variable
        drive_folder_url = os.getenv('DRIVE_FOLDER_URL')
        if not drive_folder_url:
            raise ValueError("DRIVE_FOLDER_URL environment variable not set")
            
        # Initialize processor
        processor = VideoProcessor(
            input_source=drive_folder_url,
            output_dir="output_videos",
            min_videos=2,
            max_videos=6,
            remove_audio=True,
            is_drive_url=True
        )
        
        # Process videos
        output_path = processor.process()
        print(f"\nSuccess! Final video saved to: {output_path}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
        
    finally:
        # Close log file
        sys.stdout.close()
        sys.stderr.close()
        
if __name__ == "__main__":
    main() 