import os
from dotenv import load_dotenv
import requests
import json
import webbrowser
import secrets

def test_credentials():
    # Force reload of environment variables
    load_dotenv(override=True)
    
    client_key = os.getenv('TIKTOK_CLIENT_KEY')
    client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
    redirect_uri = os.getenv('TIKTOK_REDIRECT_URI')
    
    print("\nTikTok Credentials Test")
    print("======================")
    print(f"Client Key: {client_key}")
    print(f"Client Secret: {client_secret}")
    print(f"Redirect URI: {redirect_uri}")
    
    if not all([client_key, client_secret, redirect_uri]):
        print("\nError: Missing required credentials in .env file")
        return
    
    # Generate state for security
    state = secrets.token_urlsafe(16)
    
    # Construct the authorization URL
    auth_params = {
        'client_key': client_key,
        'response_type': 'code',
        'scope': 'user.info.basic,video.upload',
        'redirect_uri': redirect_uri,
        'state': state
    }
    
    auth_url = 'https://www.tiktok.com/v2/auth/authorize?' + '&'.join([f"{k}={v}" for k, v in auth_params.items()])
    
    print("\nTesting TikTok OAuth Flow")
    print("========================")
    print(f"1. Opening authorization URL in your browser...")
    print(f"2. State value (save this): {state}")
    print(f"3. After authorization, you will be redirected to {redirect_uri}")
    print("\nAuthorization URL:")
    print(auth_url)
    
    # Open the URL in the default browser
    webbrowser.open(auth_url)

if __name__ == '__main__':
    test_credentials() 