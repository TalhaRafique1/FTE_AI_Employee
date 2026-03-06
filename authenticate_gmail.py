"""
Gmail Authentication Script

Run this script once to authenticate with Gmail API and generate the token file.
The token will be saved to ~/.ai_employee/gmail_token.pickle

Usage:
    python authenticate_gmail.py [credentials_path]
    
Example:
    python authenticate_gmail.py credentials.json
"""

import os
import sys
import pickle
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def authenticate_gmail(credentials_path: str):
    """Authenticate with Gmail API and save token."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    token_path = Path.home() / '.ai_employee' / 'gmail_token.pickle'
    
    # Ensure directory exists
    token_path.parent.mkdir(parents=True, exist_ok=True)
    
    creds = None
    
    # Load existing token if available
    if token_path.exists():
        print(f"Found existing token at: {token_path}")
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
            print("Loaded existing Gmail token")
        except Exception as e:
            print(f"Could not load token: {e}")
            print("Will create new token...")
            token_path.unlink(missing_ok=True)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing existing token...")
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                print("Token refreshed successfully!")
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            print("\n" + "="*60)
            print("GMAIL API AUTHENTICATION")
            print("="*60)
            print(f"\nUsing credentials file: {credentials_path}")
            print("\nA browser window will open for authentication.")
            print("Please sign in with your Gmail account and grant permissions.")
            print("="*60 + "\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0, open_browser=True)
            
            print("\n✓ Authentication successful!")
        
        # Save credentials
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print(f"✓ Token saved to: {token_path}")
    
    print("\n" + "="*60)
    print("AUTHENTICATION COMPLETE")
    print("="*60)
    print(f"\nGmail API is now authenticated!")
    print(f"Token location: {token_path}")
    print("\nYou can now run the Gmail watcher:")
    print("  python watchers\\gmail_watcher.py")
    print("="*60 + "\n")
    
    # Test the connection
    try:
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        
        # Get profile to test connection
        profile = service.users().getProfile(userId='me').execute()
        print(f"Connected to Gmail account: {profile['emailAddress']}")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"Error testing connection: {e}")
        return False


if __name__ == '__main__':
    # Find credentials file
    credentials_path = None
    
    if len(sys.argv) > 1:
        credentials_path = sys.argv[1]
    else:
        # Look for credentials.json in common locations
        possible_paths = [
            Path.cwd() / 'credentials.json',
            Path(__file__).parent / 'credentials.json',
            Path.home() / 'credentials.json'
        ]
        
        for path in possible_paths:
            if path.exists():
                credentials_path = str(path)
                break
    
    if not credentials_path:
        print("ERROR: credentials.json not found!")
        print("\nPlease provide the path to your Gmail OAuth credentials file:")
        print("  python authenticate_gmail.py path\\to\\credentials.json")
        print("\nOr place credentials.json in the current directory.")
        sys.exit(1)
    
    if not Path(credentials_path).exists():
        print(f"ERROR: Credentials file not found: {credentials_path}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("GMAIL API AUTHENTICATION SCRIPT")
    print("="*60)
    print(f"Credentials: {credentials_path}")
    print("="*60 + "\n")
    
    success = authenticate_gmail(credentials_path)
    sys.exit(0 if success else 1)
