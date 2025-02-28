import requests
from urllib.parse import urlencode, quote_plus
import json
from datetime import datetime, timedelta
import secrets
import os
import time

class TikTokAuth:
    def __init__(self, client_key, client_secret, redirect_uri):
        self.client_key = client_key
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://open.tiktokapis.com/v2"
        
    def get_auth_url(self):
        """Generate the authorization URL for users to grant permission"""
        base_auth_url = "https://www.tiktok.com/v2/auth/authorize/"
        # Generate a secure random state
        state = secrets.token_urlsafe(16)
        
        params = {
            "client_key": self.client_key,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": "user.info.basic,video.upload"
        }
        auth_url = f"{base_auth_url}?{urlencode(params, quote_via=quote_plus)}"
        print("\nState value (save this):", state)
        return auth_url
        
    def get_access_token(self, code):
        """Exchange authorization code for access token"""
        url = "https://open.tiktokapis.com/v2/oauth/token/"
        
        # Prepare form data exactly as in documentation
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        # URL encode the data
        encoded_data = urlencode(data, quote_via=quote_plus)
        
        # Headers exactly as in documentation
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache"
        }
        
        try:
            print("\nSending token request...")
            print("URL:", url)
            print("Headers:", headers)
            print("Encoded data:", encoded_data)
            
            response = requests.post(
                url,
                data=encoded_data,
                headers=headers,
                verify=True
            )
            
            print("\nResponse status:", response.status_code)
            print("Response headers:", dict(response.headers))
            print("Response body:", response.text)
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json() if response.text else {"error": "Unknown error"}
                print("\nError response:", json.dumps(error_data, indent=2))
                return error_data
                
        except requests.exceptions.RequestException as e:
            print(f"\nRequest error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print("Error response:", e.response.text)
            raise

    def refresh_access_token(self, refresh_token, max_retries=3):
        """Refresh an expired access token"""
        url = "https://open.tiktokapis.com/v2/oauth/token/"
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        # URL encode the data
        encoded_data = urlencode(data, quote_via=quote_plus)
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache"
        }
        
        last_error = None
        for attempt in range(max_retries):
            try:
                print(f"\nSending refresh token request (attempt {attempt + 1}/{max_retries})...")
                print("URL:", url)
                print("Headers:", headers)
                print("Encoded data:", encoded_data)
                
                response = requests.post(url, data=encoded_data, headers=headers)
                
                print("\nResponse status:", response.status_code)
                print("Response headers:", dict(response.headers))
                print("Response body:", response.text)
                
                response_data = response.json()
                
                # Check for internal server error in response body
                if "data" in response_data and "description" in response_data["data"] and response_data["data"]["description"] == "internal server error":
                    print(f"\nTikTok internal server error in response body (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        print("Waiting 10 seconds before retry...")  # Increased wait time
                        time.sleep(10)
                        continue
                    else:
                        raise Exception("TikTok internal server error persisted after all retries")
                
                # Check for access token in response
                if "access_token" in response_data:
                    return response_data
                else:
                    error_msg = response_data.get("data", {}).get("description", "Unknown error")
                    print("\nError refreshing token:", json.dumps(response_data, indent=2))
                    if attempt < max_retries - 1:
                        print("Waiting 10 seconds before retry...")
                        time.sleep(10)
                        continue
                    return response_data
                    
            except requests.exceptions.RequestException as e:
                print(f"\nNetwork error refreshing token (attempt {attempt + 1}): {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    print("Error response:", e.response.text)
                last_error = e
                if attempt < max_retries - 1:
                    print("Waiting 10 seconds before retry...")
                    time.sleep(10)
                    continue
                raise
        
        # If we've exhausted all retries
        if last_error:
            if isinstance(last_error, dict):
                raise Exception(f"Failed to refresh token after {max_retries} attempts: {last_error.get('error', 'Unknown error')}")
            else:
                raise last_error

def main():
    # Example usage
    client_key = os.getenv('TIKTOK_CLIENT_KEY')
    client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
    redirect_uri = os.getenv('TIKTOK_REDIRECT_URI')
    
    if not all([client_key, client_secret, redirect_uri]):
        raise ValueError("Missing required TikTok credentials in .env file")
    
    auth = TikTokAuth(client_key, client_secret, redirect_uri)
    
    # Use the provided authorization code
    code = "pa08Ry4RhcN3deEyaHFRcvDyNf2kBRPsnxhZ1alojG2lxI-3WpRy-nK78blMUmRoT6kcE4-v5eOSPnu3m0e3_D7MJuZMIHoi7cnYR9yReyJuUhFbr5RLnbT0wAhmHcKxTrCCXhbvBT_v0aZv_nAtqxIu1K6Fi-d6Fd1ctPIIgkkoqjaNuhX01Sx-BPBSZFf9*1!6378.u1"
    
    try:
        # Exchange code for access token
        token_info = auth.get_access_token(code)
        print("\nToken Information:")
        print(json.dumps(token_info, indent=2))
        
        if 'access_token' in token_info:
            # Update the .env file with the new access token
            with open('.env', 'r') as f:
                env_lines = f.readlines()
            
            access_token_updated = False
            refresh_token_updated = False
            
            for i, line in enumerate(env_lines):
                if line.startswith('TIKTOK_ACCESS_TOKEN='):
                    env_lines[i] = f'TIKTOK_ACCESS_TOKEN={token_info["access_token"]}\n'
                    access_token_updated = True
                elif line.startswith('TIKTOK_REFRESH_TOKEN=') and 'refresh_token' in token_info:
                    env_lines[i] = f'TIKTOK_REFRESH_TOKEN={token_info["refresh_token"]}\n'
                    refresh_token_updated = True
            
            if not access_token_updated:
                env_lines.append(f'TIKTOK_ACCESS_TOKEN={token_info["access_token"]}\n')
            if not refresh_token_updated and 'refresh_token' in token_info:
                env_lines.append(f'TIKTOK_REFRESH_TOKEN={token_info["refresh_token"]}\n')
            
            with open('.env', 'w') as f:
                f.writelines(env_lines)
            print("\nTokens have been updated in .env file")
        
    except Exception as e:
        print(f"Error getting access token: {str(e)}")

if __name__ == "__main__":
    main() 
