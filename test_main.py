import os
from main import VideoProcessor
from metadata_extractor import get_video_duration

def test_video_processor():
    # Test with our 5-second test video
    test_dir = "test_videos"
    test_video = "test_videos/test.mp4"
    
    # Ensure we have enough copies of the test video
    if not os.path.exists(test_video):
        print("❌ Failed: Test video not found")
        return
    
    processor = VideoProcessor(
        test_dir,
        min_duration=6.0,  # Use shorter duration for testing
        max_duration=8.0,
        min_videos=2,
        max_videos=3
    )
    
    try:
        # Process videos
        output_path = processor.process()
        
        # Check if output file exists
        if os.path.exists(output_path):
            print("✅ Passed: Successfully created output file")
        else:
            print("❌ Failed: Output file not created")
        
        # Check output duration
        duration = get_video_duration(output_path)
        if 6.0 <= duration <= 8.0:
            print("✅ Passed: Output video has correct duration")
        else:
            print(f"❌ Failed: Wrong output duration: {duration}s (expected 6-8s)")
        
        # Test with custom output path
        custom_output = "test_videos/final_output.mp4"
        output_path = processor.process(custom_output)
        
        if output_path == custom_output and os.path.exists(custom_output):
            print("✅ Passed: Successfully used custom output path")
        else:
            print("❌ Failed: Custom output path not used correctly")
        
        # Clean up custom output
        if os.path.exists(custom_output):
            os.unlink(custom_output)
            
    except Exception as e:
        print(f"❌ Failed: Error processing videos: {str(e)}")
    finally:
        # Clean up
        processor.trimmer.clean_output_directory()
        processor.connector.clean_output_directory()

if __name__ == "__main__":
    test_video_processor() 