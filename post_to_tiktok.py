from ayrshare_handler import AyrshareHandler
from datetime import datetime, timedelta
import os
import time
import json

def main():
    video_path = os.path.join('output_videos', 'final_with_captions.mp4')
    
    # Initialize AyrshareHandler
    ayrshare = AyrshareHandler()
    
    try:
        # Create and schedule the post
        schedule_time = datetime.now() + timedelta(minutes=5)
        print(f"\nCreating post scheduled for {schedule_time.isoformat()}")
        
        post_result = ayrshare.post_to_tiktok(
            video_path=video_path,
            caption="Check out this amazing video! #viral #trending",
            schedule_time=schedule_time
        )
        
        if not post_result:
            print("Post creation failed - no response received")
            return
            
        post_id = post_result.get('id')
        if not post_id:
            print("Post creation failed - no post ID received")
            return
            
        print(f"\nPost created successfully!")
        print(f"Post ID: {post_id}")
        print(json.dumps(post_result, indent=2))
        
        # Monitor post status
        print("\nMonitoring post status...")
        max_attempts = 12  # Monitor for up to 2 minutes
        attempt = 0
        
        while attempt < max_attempts:
            status = ayrshare.check_post_status(post_id)
            print(f"\nStatus Check {attempt + 1}:")
            print(json.dumps(status, indent=2))
            
            if status.get('status') == 'posted':
                print("\nPost has been published successfully!")
                break
            elif status.get('status') == 'failed':
                print(f"\nPost failed: {status.get('error')}")
                break
                
            attempt += 1
            if attempt < max_attempts:
                print("\nWaiting 10 seconds before next check...")
                time.sleep(10)
        
        if attempt >= max_attempts:
            print("\nTimeout waiting for post status. Please check the Ayrshare dashboard.")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 