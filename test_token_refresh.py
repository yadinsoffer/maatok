import os
from dotenv import load_dotenv
from upload_video_to_tiktok import send_tiktok_request

def test_token_refresh_flow():
    """Test function to simulate token refresh flow"""
    print("\nTesting token refresh flow...")
    
    # Deliberately use an invalid token
    invalid_token = "invalid_token_to_trigger_401"
    
    # Test URL - using the video init endpoint
    test_url = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
    headers = {
        "Authorization": f"Bearer {invalid_token}",
        "Content-Type": "application/json"
    }
    
    # Sample data for the request
    test_data = {
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": 1000,
            "chunk_size": 1000,
            "total_chunk_count": 1
        }
    }
    
    try:
        # This should trigger a 401, causing a token refresh
        response = send_tiktok_request(test_url, "POST", headers, test_data)
        print("\nResponse:", response.json())
    except Exception as e:
        print(f"\nError occurred (expected during testing): {str(e)}")

def main():
    # Force reload of environment variables
    load_dotenv(override=True)
    
    print("\n=== Starting Token Refresh Flow Test ===")
    test_token_refresh_flow()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 