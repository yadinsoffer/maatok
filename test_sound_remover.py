import os
from sound_remover import SoundRemover

def test_sound_remover():
    remover = SoundRemover()
    test_video = "test_videos/test.mp4"
    nonexistent_video = "test_videos/nonexistent.mp4"
    
    # Clean output directory before testing
    remover.clean_output_directory()
    
    # Test with nonexistent file
    try:
        remover.remove_audio(nonexistent_video)
        print("❌ Failed: Should raise FileNotFoundError for nonexistent file")
    except FileNotFoundError:
        print("✅ Passed: Correctly handled nonexistent file")
    
    # Test with valid file
    try:
        output_path = remover.remove_audio(test_video)
        
        # Check if output file exists
        if os.path.exists(output_path):
            print("✅ Passed: Successfully created output file")
        else:
            print("❌ Failed: Output file not created")
            
    except Exception as e:
        print(f"❌ Failed: Error removing audio: {str(e)}")
    
    # Test with custom output path
    try:
        custom_output = "test_videos/custom_muted.mp4"
        output_path = remover.remove_audio(test_video, custom_output)
        
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
    remover.clean_output_directory()

if __name__ == "__main__":
    test_sound_remover() 