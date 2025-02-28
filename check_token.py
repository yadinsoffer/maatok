import os
import json
import requests
from dotenv import load_dotenv

def check_creator_info(access_token):
    """Check creator info to verify token validity and permissions"""
    url = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    try:
        response = requests.post(url, headers=headers)
        print("\nResponse Headers:")
        print(json.dumps(dict(response.headers), indent=2))
        
        print("\nResponse Status Code:", response.status_code)
        
        print("\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        return response.json()
    except Exception as e:
        print(f"\nError: {str(e)}")
        if hasattr(e, 'response'):
            print("Response:", e.response.text)
        raise

def main():
    # Load environment variables
    load_dotenv()
    
    # Get access token
    access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
    if not access_token:
        raise ValueError("Missing TIKTOK_ACCESS_TOKEN in .env file")
    
    print(f"\nChecking token: {access_token}")
    result = check_creator_info(access_token)

if __name__ == "__main__":
    main() 