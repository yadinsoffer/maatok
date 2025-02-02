from duration_controller import DurationController

def test_duration_controller():
    controller = DurationController()
    test_video = "test_videos/test.mp4"  # Our 5-second test video
    
    # Test with single video (should raise ValueError as it's too short)
    try:
        controller.calculate_trim_instructions([test_video])
        print("❌ Failed: Should raise ValueError for too short duration")
    except ValueError:
        print("✅ Passed: Correctly handled too short duration")
    
    # Test with multiple copies of the same video (total 25s, should work)
    video_paths = [test_video] * 5  # 5 videos * 5 seconds = 25s (within 21-28s range)
    try:
        instructions = controller.calculate_trim_instructions(video_paths)
        
        # Check if we got instructions for each video
        if len(instructions) == len(video_paths):
            print("✅ Passed: Generated instructions for each video")
        else:
            print("❌ Failed: Wrong number of instructions generated")
        
        # Check if instructions are valid
        if controller.validate_trim_instructions(video_paths, instructions):
            print("✅ Passed: Generated valid trim instructions")
        else:
            print("❌ Failed: Generated invalid trim instructions")
        
        # Check if each instruction has required fields
        all_valid = all(
            'start_time' in inst and 'end_time' in inst
            for inst in instructions
        )
        if all_valid:
            print("✅ Passed: All instructions have required fields")
        else:
            print("❌ Failed: Missing required fields in instructions")
        
        # Check if timings are reasonable
        all_reasonable = all(
            0 <= inst['start_time'] <= inst['end_time'] <= 5.0
            for inst in instructions
        )
        if all_reasonable:
            print("✅ Passed: All timing values are reasonable")
        else:
            print("❌ Failed: Invalid timing values in instructions")
            
    except Exception as e:
        print(f"❌ Failed: Error calculating trim instructions: {str(e)}")
    
    # Test validation with mismatched lists
    if not controller.validate_trim_instructions([test_video], []):
        print("✅ Passed: Correctly rejected mismatched instructions")
    else:
        print("❌ Failed: Should reject mismatched instructions")

if __name__ == "__main__":
    test_duration_controller() 