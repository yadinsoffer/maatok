from metadata_extractor import extract_video_metadata, get_video_duration

def test_metadata_extractor():
    test_video = "test_videos/test.mp4"
    nonexistent_video = "test_videos/nonexistent.mp4"
    
    # Test nonexistent file
    try:
        extract_video_metadata(nonexistent_video)
        print("❌ Failed: Should raise FileNotFoundError for nonexistent file")
    except FileNotFoundError:
        print("✅ Passed: Correctly handled nonexistent file")
    
    # Test metadata extraction
    try:
        metadata = extract_video_metadata(test_video)
        
        # Check if all required fields are present
        required_fields = ['duration', 'format', 'width', 'height']
        all_fields_present = all(field in metadata for field in required_fields)
        
        if all_fields_present:
            print("✅ Passed: Successfully extracted all required metadata fields")
        else:
            print("❌ Failed: Missing required metadata fields")
            
        # Check if values are reasonable
        if metadata['duration'] > 0:
            print("✅ Passed: Duration is positive")
        else:
            print("❌ Failed: Invalid duration value")
            
        if metadata['width'] == 1280 and metadata['height'] == 720:
            print("✅ Passed: Correct video dimensions")
        else:
            print("❌ Failed: Incorrect video dimensions")
            
    except Exception as e:
        print(f"❌ Failed: Error extracting metadata: {str(e)}")
    
    # Test duration extraction
    try:
        duration = get_video_duration(test_video)
        if 4.9 <= duration <= 5.1:  # Allow small margin of error
            print("✅ Passed: Correct video duration")
        else:
            print(f"❌ Failed: Incorrect duration: {duration}")
    except Exception as e:
        print(f"❌ Failed: Error getting duration: {str(e)}")

if __name__ == "__main__":
    test_metadata_extractor() 