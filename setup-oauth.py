#!/usr/bin/env python3
"""
Gmail Digest Bot - OAuth Setup Helper

This script helps you set up Google OAuth and obtain the necessary tokens
for the Gmail Digest Bot to access Gmail API.
"""

import os
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def setup_oauth():
    """Set up OAuth and get refresh token."""
    
    print("Gmail Digest Bot - OAuth Setup")
    print("=" * 40)
    
    # Check for client secrets file
    client_secrets_file = input("Path to Google OAuth client secrets JSON file: ").strip()
    
    if not os.path.exists(client_secrets_file):
        print(f"Error: File {client_secrets_file} not found!")
        print("\nTo get this file:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Create a new project or select existing one")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop application)")
        print("5. Download the JSON file")
        return
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, SCOPES)
        
        print("\nStarting OAuth flow...")
        print("A browser window will open for authentication.")
        
        creds = flow.run_local_server(port=0)
        
        # Extract important information
        with open(client_secrets_file, 'r') as f:
            client_config = json.load(f)
        
        client_id = client_config['installed']['client_id']
        client_secret = client_config['installed']['client_secret']
        refresh_token = creds.refresh_token
        
        print("\n" + "=" * 50)
        print("SUCCESS! OAuth setup completed.")
        print("=" * 50)
        print("\nAdd these environment variables to your Azure App Service:")
        print(f"GOOGLE_CLIENT_ID={client_id}")
        print(f"GOOGLE_CLIENT_SECRET={client_secret}")
        print(f"GMAIL_REFRESH_TOKEN={refresh_token}")
        
        # Save to .env file
        env_content = f"""# Generated OAuth configuration
GOOGLE_CLIENT_ID={client_id}
GOOGLE_CLIENT_SECRET={client_secret}
GMAIL_REFRESH_TOKEN={refresh_token}
"""
        
        with open('.env.oauth', 'w') as f:
            f.write(env_content)
        
        print(f"\nConfiguration also saved to: .env.oauth")
        print("\nYou can now use these values in your Azure deployment!")
        
    except Exception as e:
        print(f"Error during OAuth setup: {e}")
        print("\nPlease check:")
        print("1. The client secrets file is valid")
        print("2. Gmail API is enabled in your Google Cloud project")
        print("3. OAuth consent screen is configured")

if __name__ == "__main__":
    setup_oauth()

