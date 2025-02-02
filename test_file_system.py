import os
from file_system import get_video_files, validate_video_files

def test_file_system():
    # Test directory handling
    try:
        get_video_files("nonexistent_directory")
        print("❌ Failed: Should raise FileNotFoundError for nonexistent directory")
    except FileNotFoundError:
        print("✅ Passed: Correctly handled nonexistent directory")

    # Test empty directory
    test_dir = "test_videos"
    files = get_video_files(test_dir)
    if len(files) == 0:
        print("✅ Passed: Correctly handled empty directory")
    else:
        print("❌ Failed: Empty directory should return empty list")

    # Test file validation
    test_files = [
        "test_videos/test1.mp4",
        "test_videos/test2.txt",
        "test_videos/test3.mov"
    ]
    valid_files = validate_video_files(test_files)
    if len(valid_files) == 0:  # Since files don't exist
        print("✅ Passed: Correctly validated non-existent files")
    else:
        print("❌ Failed: Should not validate non-existent files")

if __name__ == "__main__":
    test_file_system() 