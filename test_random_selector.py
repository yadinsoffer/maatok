from random_selector import select_random_videos

def test_random_selector():
    # Test empty list
    try:
        select_random_videos([])
        print("❌ Failed: Should raise ValueError for empty list")
    except ValueError:
        print("✅ Passed: Correctly handled empty list")

    # Test list with insufficient videos
    test_files = ["video1.mp4"]
    try:
        select_random_videos(test_files)
        print("❌ Failed: Should raise ValueError for insufficient videos")
    except ValueError:
        print("✅ Passed: Correctly handled insufficient videos")

    # Test normal case
    test_files = [f"video{i}.mp4" for i in range(10)]
    selected = select_random_videos(test_files)
    if 2 <= len(selected) <= 6:
        print("✅ Passed: Selected correct number of videos")
    else:
        print("❌ Failed: Selected wrong number of videos")

    # Test with custom min/max
    try:
        selected = select_random_videos(test_files, min_count=3, max_count=4)
        if 3 <= len(selected) <= 4:
            print("✅ Passed: Respected custom min/max counts")
        else:
            print("❌ Failed: Did not respect custom min/max counts")
    except ValueError:
        print("❌ Failed: Error with valid custom min/max counts")

    # Test invalid min/max
    try:
        select_random_videos(test_files, min_count=6, max_count=2)
        print("❌ Failed: Should raise ValueError for invalid min/max")
    except ValueError:
        print("✅ Passed: Correctly handled invalid min/max")

if __name__ == "__main__":
    test_random_selector() 