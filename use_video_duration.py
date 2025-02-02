from metadata_extractor import get_video_duration
import argparse

def main():
    parser = argparse.ArgumentParser(description="Get and use video duration")
    parser.add_argument("video_path", help="Path to the video file")
    
    args = parser.parse_args()
    
    try:
        # Get the video duration
        duration = get_video_duration(args.video_path)
        print(f"Video duration: {duration:.2f} seconds")
        
        # Example of using the duration in different ways:
        
        # 1. Convert to minutes and seconds
        minutes = int(duration // 60)
        seconds = duration % 60
        print(f"Duration in min:sec format: {minutes}:{seconds:05.2f}")
        
        # 2. Calculate number of frames (assuming 30fps)
        frames = int(duration * 30)
        print(f"Approximate number of frames (30fps): {frames}")
        
        # 3. Example of using duration in a calculation
        bytes_per_second = 1920 * 1080 * 3  # Example for 1080p RGB video
        total_uncompressed_size = bytes_per_second * duration / (1024 * 1024)  # Size in MB
        print(f"Theoretical uncompressed size: {total_uncompressed_size:.2f} MB")
        
        # You can use the duration variable for your own calculations here
        # For example:
        # your_calculation = duration * your_factor
        # your_function(duration)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 