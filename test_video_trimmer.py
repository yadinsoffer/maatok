import os
from video_trimmer import VideoTrimmer
from metadata_extractor import get_video_duration

def test_video_trimmer():
    trimmer = VideoTrimmer()
    test_video = "test_videos/test.mp4"
    nonexistent_video = "test_videos/nonexistent.mp4"
    
    # Clean output directory before testing
    trimmer.clean_output_directory()
    
    # Test with nonexistent file
    try:
        trimmer.trim_video(nonexistent_video, 0, 2)
        print("❌ Failed: Should raise FileNotFoundError for nonexistent file")
    except FileNotFoundError:
        print("✅ Passed: Correctly handled nonexistent file")
    
    # Test trimming with valid file
    try:
        # Trim to 2 seconds (1.5-3.5)
        output_path = trimmer.trim_video(test_video, 1.5, 3.5)
        
        # Check if output file exists
        if os.path.exists(output_path):
            print("✅ Passed: Successfully created output file")
        else:
            print("❌ Failed: Output file not created")
        
        # Check output file duration
        duration = get_video_duration(output_path)
        expected_duration = 2.0  # 3.5 - 1.5 = 2.0
        if abs(duration - expected_duration) < 0.1:  # Allow small margin of error
            print("✅ Passed: Correct output duration")
        else:
            print(f"❌ Failed: Wrong output duration: {duration}s (expected ~{expected_duration}s)")
            
    except Exception as e:
        print(f"❌ Failed: Error trimming video: {str(e)}")
    
    # Test with custom output path
    try:
        custom_output = "test_videos/custom_output.mp4"
        output_path = trimmer.trim_video(test_video, 0, 1, custom_output)
        
        if output_path == custom_output and os.path.exists(custom_output):
            print("✅ Passed: Successfully used custom output path")
        else:
            print("❌ Failed: Custom output path not used correctly")
            
        # Clean up custom output file
        if os.path.exists(custom_output):
            os.unlink(custom_output)
            
    except Exception as e:
        print(f"❌ Failed: Error with custom output path: {str(e)}")
    
    # Clean up
    trimmer.clean_output_directory()

if __name__ == "__main__":
    test_video_trimmer() 