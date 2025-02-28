from postiz_handler import PostizHandler
from datetime import datetime, timedelta
import os

def main():
    video_path = os.path.join('output_videos', 'final_with_captions.mp4')
    
    # Initialize PostizHandler
    postiz = PostizHandler()
    
    try:
        # Step 1: Upload the video file
        print("\nStep 1: Uploading video file...")
        upload_result = postiz.upload_media(video_path)
        
        if not upload_result or 'id' not in upload_result:
            print("Upload failed - no file ID received")
            return
            
        media_id = upload_result['id']
        print(f"Video uploaded successfully with ID: {media_id}")
        
        # Step 2: Schedule the post (5 minutes from now)
        schedule_time = datetime.now() + timedelta(minutes=5)
        print(f"\nStep 2: Scheduling post for {schedule_time.isoformat()}")
        
        post_result = postiz.schedule_post(
            media_id=media_id,
            caption="Check out this amazing video! #viral #trending",
            schedule_time=schedule_time
        )
        
        if not post_result:
            print("Scheduling failed - no response received")
            return
            
        post_id = post_result.get('postId')
        if not post_id:
            print("Scheduling failed - no post ID received")
            return
            
        print(f"Post scheduled successfully!")
        print(f"Post ID: {post_id}")
        print(f"Integration ID: {post_result.get('integration')}")
        
        # Step 3: Check initial status
        print("\nStep 3: Checking initial post status...")
        status = postiz.check_post_status(post_id)
        print("Initial Status:", status)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 