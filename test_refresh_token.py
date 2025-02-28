from dotenv import load_dotenv
import os
from tiktok_auth import TikTokAuth
from upload_video_to_tiktok import refresh_token_and_update_env

def test_refresh_flow():
    """Test the TikTok token refresh flow"""
    
    # Force reload of environment variables
    load_dotenv(override=True)
    
    # Get current tokens
    old_access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
    old_refresh_token = os.getenv('TIKTOK_REFRESH_TOKEN')
    client_key = os.getenv('TIKTOK_CLIENT_KEY')
    client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
    
    print("\nCurrent Token Status:")
    print(f"Access Token: {old_access_token[:10]}... (truncated)")
    print(f"Refresh Token: {old_refresh_token[:10]}... (truncated)")
    print(f"Client Key: {client_key[:5]}... (truncated)")
    
    try:
        # Attempt to refresh the token
        print("\nAttempting token refresh...")
        new_token = refresh_token_and_update_env()
        
        print("\nNew Token Status:")
        print(f"New Access Token: {new_token[:10]}... (truncated)")
        
        # Load the updated refresh token
        load_dotenv(override=True)
        new_refresh_token = os.getenv('TIKTOK_REFRESH_TOKEN')
        print(f"New Refresh Token: {new_refresh_token[:10]}... (truncated)")
        
        if new_token != old_access_token:
            print("\n✅ Success: Token was successfully refreshed!")
        else:
            print("\n⚠️ Warning: New token is identical to old token")
            
    except Exception as e:
        print(f"\n❌ Error during refresh test: {str(e)}")
        if hasattr(e, 'response'):
            print("Response:", e.response.text)
        raise

if __name__ == "__main__":
    test_refresh_flow() 