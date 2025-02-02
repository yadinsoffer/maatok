import os
from video_connector import VideoConnector
from video_trimmer import VideoTrimmer
from metadata_extractor import get_video_duration

def test_video_connector():
    connector = VideoConnector()
    trimmer = VideoTrimmer()
    test_video = "test_videos/test.mp4"
    nonexistent_video = "test_videos/nonexistent.mp4"
    
    # Clean output directories before testing
    connector.clean_output_directory()
    trimmer.clean_output_directory()
    
    # Test with empty list
    try:
        connector.concatenate_videos([])
        print("❌ Failed: Should raise ValueError for empty list")
    except ValueError:
        print("✅ Passed: Correctly handled empty list")
    
    # Test with nonexistent file
    try:
        connector.concatenate_videos([nonexistent_video])
        print("❌ Failed: Should raise FileNotFoundError for nonexistent file")
    except FileNotFoundError:
        print("✅ Passed: Correctly handled nonexistent file")
    
    # Test concatenating multiple segments of the same video
    try:
        # Create three 1-second segments
        segment1 = trimmer.trim_video(test_video, 0, 1)
        segment2 = trimmer.trim_video(test_video, 1, 2)
        segment3 = trimmer.trim_video(test_video, 2, 3)
        
        # Concatenate the segments
        output_path = connector.concatenate_videos([segment1, segment2, segment3])
        
        # Check if output file exists
        if os.path.exists(output_path):
            print("✅ Passed: Successfully created output file")
        else:
            print("❌ Failed: Output file not created")
        
        # Check output file duration
        duration = get_video_duration(output_path)
        expected_duration = 3.0  # Three 1-second segments
        if abs(duration - expected_duration) < 0.1:  # Allow small margin of error
            print("✅ Passed: Correct output duration")
        else:
            print(f"❌ Failed: Wrong output duration: {duration}s (expected ~{expected_duration}s)")
            
    except Exception as e:
        print(f"❌ Failed: Error concatenating videos: {str(e)}")
    
    # Test with custom output path
    try:
        custom_output = "test_videos/custom_concat.mp4"
        output_path = connector.concatenate_videos([segment1, segment2], custom_output)
        
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
    connector.clean_output_directory()
    trimmer.clean_output_directory()

if __name__ == "__main__":
    test_video_connector() 