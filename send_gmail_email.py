"""
Gmail Email Sender - Send emails via Gmail API

This script sends emails using the authenticated Gmail API token.
Used by the AI Employee to send approved emails.

Usage:
    python send_gmail_email.py --to recipient@example.com --subject "Subject" --body "Body text"
    python send_gmail_email.py --file AI_Employee_Vault/Approved/EMAIL_*.md
"""

import argparse
import base64
import json
import sys
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# Gmail API imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def load_gmail_credentials():
    """Load Gmail API credentials from token file."""
    token_path = Path.home() / '.ai_employee' / 'gmail_token.pickle'
    credentials_path = Path(__file__).parent / 'credentials.json'
    
    if not token_path.exists():
        print(f"ERROR: Token file not found: {token_path}")
        print("Please run authenticate_gmail.py first")
        return None
    
    try:
        import pickle
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        
        print(f"[OK] Loaded Gmail credentials for: {creds.id}")
        return creds
        
    except Exception as e:
        print(f"ERROR: Could not load credentials: {e}")
        return None


def send_email(to: str, subject: str, body: str, creds=None, attachment_path: str = None):
    """Send email using Gmail API."""
    
    if not creds:
        creds = load_gmail_credentials()
        if not creds:
            return False
    
    try:
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Create message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment_path and Path(attachment_path).exists():
            from email.mime.base import MIMEBase
            from email import encoders
            
            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={Path(attachment_path).name}'
                )
                message.attach(part)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        print(f"[OK] Email sent successfully!")
        print(f"     To: {to}")
        print(f"     Subject: {subject}")
        print(f"     Message ID: {sent_message['id']}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False


def extract_email_from_approved_file(file_path: str) -> dict:
    """Extract email details from approved action file."""
    path = Path(file_path)
    if not path.exists():
        return None
    
    content = path.read_text(encoding='utf-8', errors='replace')
    
    # Extract fields from frontmatter
    to_match = re.search(r'to:\s*"([^"]+)"', content)
    subject_match = re.search(r'subject:\s*"([^"]+)"', content)
    
    # Extract email body from content
    body_match = re.search(r'## Email Content\s*\n+(.+?)(?=##|\n---|\Z)', content, re.DOTALL)
    
    if not all([to_match, subject_match]):
        # Try alternative format
        to_match = re.search(r'To:\s*([^\n]+)', content)
        subject_match = re.search(r'Subject:\s*([^\n]+)', content)
        body_match = re.search(r'Content:\s*\n+(.+?)(?=##|\n---|\Z)', content, re.DOTALL)
    
    if not all([to_match, subject_match, body_match]):
        print("WARNING: Could not extract all email fields")
        return {
            'to': to_match.group(1).strip() if to_match else None,
            'subject': subject_match.group(1).strip() if subject_match else None,
            'body': body_match.group(1).strip() if body_match else content[:500]
        }
    
    return {
        'to': to_match.group(1).strip(),
        'subject': subject_match.group(1).strip(),
        'body': body_match.group(1).strip()
    }


def process_approved_folder():
    """Process all approved emails in Approved folder."""
    approved_folder = Path('AI_Employee_Vault') / 'Approved'
    
    if not approved_folder.exists():
        print("No Approved folder found")
        return 0
    
    approved_files = list(approved_folder.glob('EMAIL_*.md'))
    if not approved_files:
        print("No approved emails to send")
        return 0
    
    print(f"Found {len(approved_files)} approved email(s) to send")
    
    creds = load_gmail_credentials()
    if not creds:
        return 0
    
    sent_count = 0
    for file_path in approved_files:
        print(f"\nProcessing: {file_path.name}")
        
        email_data = extract_email_from_approved_file(str(file_path))
        
        if not email_data or not email_data['to']:
            print(f"  [SKIP] Could not extract email data")
            continue
        
        success = send_email(
            to=email_data['to'],
            subject=email_data['subject'],
            body=email_data['body'],
            creds=creds
        )
        
        if success:
            sent_count += 1
            # Move to Done
            done_folder = Path('AI_Employee_Vault') / 'Done'
            done_folder.mkdir(exist_ok=True)
            file_path.rename(done_folder / file_path.name)
            print(f"  [OK] Moved to Done folder")
        else:
            print(f"  [FAIL] Email send failed")
    
    print(f"\n{'='*60}")
    print(f"Sent {sent_count}/{len(approved_files)} emails")
    return sent_count


def main():
    parser = argparse.ArgumentParser(description='Send emails via Gmail API')
    
    parser.add_argument('--to', help='Recipient email address')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body text')
    parser.add_argument('--file', help='Approved action file to send')
    parser.add_argument('--attachment', help='Attachment file path')
    parser.add_argument('--process-approved', action='store_true', 
                       help='Process all approved emails in Approved folder')
    
    args = parser.parse_args()
    
    if args.process_approved:
        count = process_approved_folder()
        sys.exit(0 if count > 0 else 1)
    
    if args.file:
        # Send from approved file
        email_data = extract_email_from_approved_file(args.file)
        if not email_data:
            print("ERROR: Could not extract email data from file")
            sys.exit(1)
        
        creds = load_gmail_credentials()
        if not creds:
            sys.exit(1)
        
        success = send_email(
            to=email_data['to'],
            subject=email_data['subject'],
            body=email_data['body'],
            creds=creds,
            attachment_path=args.attachment
        )
        sys.exit(0 if success else 1)
    
    if args.to and args.subject:
        # Send direct email
        creds = load_gmail_credentials()
        if not creds:
            sys.exit(1)
        
        body = args.body or ""
        success = send_email(
            to=args.to,
            subject=args.subject,
            body=body,
            creds=creds,
            attachment_path=args.attachment
        )
        sys.exit(0 if success else 1)
    
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
