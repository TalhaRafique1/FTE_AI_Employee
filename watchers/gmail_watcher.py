"""
Gmail Watcher Module - Silver Tier

Monitors Gmail for new unread/important emails and creates action files.
Requires Gmail API credentials setup.

Usage:
    python gmail_watcher.py [credentials_path]
    
Example:
    python gmail_watcher.py credentials.json
"""

import sys
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class GmailMessage:
    """Represents a Gmail message."""
    
    def __init__(self, message_id: str, snippet: str, headers: Dict[str, str], body: str = ""):
        self.message_id = message_id
        self.snippet = snippet
        self.from_email = headers.get('From', 'Unknown')
        self.subject = headers.get('Subject', 'No Subject')
        self.date = headers.get('Date', '')
        self.to = headers.get('To', '')
        self.headers = headers
        self.body = body
        
    def is_urgent(self) -> bool:
        """Check if message contains urgent keywords."""
        urgent_keywords = ['urgent', 'asap', 'emergency', 'important', 'priority', 'immediately']
        text = f"{self.subject} {self.snippet} {self.body}".lower()
        return any(kw in text for kw in urgent_keywords)
    
    def is_invoice_related(self) -> bool:
        """Check if message is invoice/payment related."""
        invoice_keywords = ['invoice', 'payment', 'bill', 'receipt', 'pay', 'amount due']
        text = f"{self.subject} {self.snippet}".lower()
        return any(kw in text for kw in invoice_keywords)


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new unread/important emails.
    
    When a new email is detected, it:
    1. Fetches full message details
    2. Creates an action file in Needs_Action
    3. Marks the email as processed
    """
    
    def __init__(self, vault_path: str, credentials_path: Optional[str] = None, 
                 check_interval: int = 120):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            credentials_path: Path to Gmail API credentials JSON
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        # Look for credentials in multiple locations
        self.credentials_path = self._find_credentials(credentials_path)
        self.service = None
        self.processed_ids: set = set()
        self.token_path = Path.home() / '.ai_employee' / 'gmail_token.pickle'
        
        # Ensure token directory exists
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load already processed IDs from file
        self._load_processed_ids()
        
        # VIP senders (loaded from Company_Handbook or .env)
        self.vip_senders = self._load_vip_senders()
        
        # Keywords that indicate action needed
        self.action_keywords = [
            'invoice', 'payment', 'urgent', 'asap', 'meeting',
            'deadline', 'review', 'approve', 'response needed',
            'question', 'help', 'support'
        ]
        
        self.logger.info(f'Credentials path: {self.credentials_path}')
        self.logger.info(f'Token path: {self.token_path}')
    
    def _find_credentials(self, provided_path: Optional[str]) -> Optional[Path]:
        """Find credentials.json in common locations."""
        possible_paths = []
        
        if provided_path:
            possible_paths.append(Path(provided_path))
        
        # Current directory
        possible_paths.append(Path.cwd() / 'credentials.json')
        
        # Project root
        possible_paths.append(Path(__file__).parent.parent / 'credentials.json')
        
        # Vault root
        possible_paths.append(Path(__file__).parent.parent / 'AI_Employee_Vault' / 'credentials.json')
        
        for path in possible_paths:
            if path.exists():
                self.logger.info(f'Found credentials at: {path}')
                return path
        
        self.logger.warning('credentials.json not found. Gmail watcher will not function.')
        return None
    
    def _load_processed_ids(self):
        """Load already processed email IDs from file."""
        processed_file = Path(__file__).parent.parent / 'AI_Employee_Vault' / '.processed_emails.json'
        if processed_file.exists():
            try:
                import json
                data = json.loads(processed_file.read_text())
                self.processed_ids = set(data.get('processed_ids', []))
                self.logger.info(f'Loaded {len(self.processed_ids)} previously processed email IDs')
            except Exception as e:
                self.logger.warning(f'Could not load processed emails: {e}')
                self.processed_ids = set()
        else:
            self.processed_ids = set()
    
    def _save_processed_ids(self):
        """Save processed email IDs to file."""
        processed_file = Path(__file__).parent.parent / 'AI_Employee_Vault' / '.processed_emails.json'
        try:
            import json
            data = {'processed_ids': list(self.processed_ids), 'updated': datetime.now().isoformat()}
            processed_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self.logger.error(f'Could not save processed emails: {e}')
    
    def _load_vip_senders(self) -> set:
        """Load VIP senders from Company Handbook or .env."""
        vip_senders = set()
        
        # Try to load from Company_Handbook.md
        handbook_path = Path(__file__).parent.parent / 'AI_Employee_Vault' / 'Company_Handbook.md'
        if handbook_path.exists():
            try:
                content = handbook_path.read_text(encoding='utf-8')
                # Look for VIP emails in the handbook
                import re
                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', content)
                # Add domain-specific emails as VIPs (you can customize this logic)
                for email in emails:
                    if any(kw in email.lower() for kw in ['client', 'partner', 'vip', 'important']):
                        vip_senders.add(email)
            except Exception as e:
                self.logger.warning(f'Could not read Company Handbook: {e}')
        
        # Try to load from .env
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            try:
                content = env_path.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    if line.startswith('VIP_SENDERS='):
                        emails = line.split('=', 1)[1].strip().split(',')
                        vip_senders.update(email.strip() for email in emails)
            except Exception as e:
                self.logger.warning(f'Could not read .env file: {e}')
        
        return vip_senders
    
    def _authenticate(self) -> bool:
        """Authenticate with Gmail API. Returns True if successful."""
        if not self.credentials_path:
            self.logger.error('No credentials file found')
            return False
        
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            creds = None
            
            # Load existing token
            if self.token_path.exists():
                try:
                    with open(self.token_path, 'rb') as token:
                        creds = pickle.load(token)
                    self.logger.info('Loaded existing Gmail token')
                except Exception as e:
                    self.logger.warning(f'Could not load token: {e}')
                    self.token_path.unlink(missing_ok=True)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        self.logger.info('Refreshed Gmail token')
                    except Exception as e:
                        self.logger.warning(f'Token refresh failed: {e}')
                        creds = None
                
                if not creds:
                    self.logger.info('Starting OAuth flow...')
                    self.logger.info('Opening browser for authentication...')
                    print('\n' + '='*60)
                    print('GMAIL AUTHENTICATION REQUIRED')
                    print('='*60)
                    print('A browser window should open for Gmail authentication.')
                    print('Please complete the authentication flow.')
                    print('='*60 + '\n')
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0, open_browser=True)
                    self.logger.info('OAuth flow completed successfully')
                
                # Save credentials
                with open(self.token_path, 'wb') as token:
                    pickle.dump(creds, token)
                self.logger.info(f'Saved Gmail token to: {self.token_path}')
            
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Gmail API authenticated successfully')
            return True
            
        except FileNotFoundError:
            self.logger.error(f'Credentials file not found: {self.credentials_path}')
            return False
        except Exception as e:
            self.logger.error(f'Gmail authentication failed: {e}')
            import traceback
            self.logger.debug(traceback.format_exc())
            return False
    
    def check_for_updates(self) -> List[GmailMessage]:
        """
        Check Gmail for new unread/important messages.
        
        Returns:
            List of new GmailMessage objects
        """
        if not self.service:
            if not self._authenticate():
                return []
        
        new_messages = []
        
        try:
            # Fetch unread messages
            self.logger.debug('Fetching unread messages from Gmail...')
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            self.logger.info(f'Found {len(messages)} unread message(s)')
            
            for message in messages:
                msg_id = message['id']
                
                # Skip if already processed
                if msg_id in self.processed_ids:
                    continue
                
                # Fetch full message details
                msg_details = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                # Extract headers
                headers = {}
                for header in msg_details['payload']['headers']:
                    headers[header['name']] = header['value']
                
                # Extract body
                body = self._extract_body(msg_details)
                
                # Create message object
                gmail_msg = GmailMessage(
                    message_id=msg_id,
                    snippet=msg_details.get('snippet', ''),
                    headers=headers,
                    body=body
                )
                
                new_messages.append(gmail_msg)
                self.processed_ids.add(msg_id)
                
                # Save processed IDs after each message
                self._save_processed_ids()
                
                # Limit to 5 new messages per check
                if len(new_messages) >= 5:
                    break
            
            if new_messages:
                self.logger.info(f'Found {len(new_messages)} new message(s) to process')
            
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            import traceback
            self.logger.debug(traceback.format_exc())
        
        return new_messages
    
    def _extract_body(self, msg_details: dict) -> str:
        """Extract the plain text body from a message."""
        def get_body_from_part(part):
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    import base64
                    data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    return data
            for child in part.get('parts', []):
                body = get_body_from_part(child)
                if body:
                    return body
            return ''
        
        return get_body_from_part(msg_details['payload'])
    
    def create_action_file(self, message: GmailMessage) -> Optional[Path]:
        """
        Create an action file for a Gmail message.
        
        Args:
            message: The GmailMessage to create an action file for
            
        Returns:
            Path to the created action file
        """
        try:
            # Determine priority
            is_urgent = message.is_urgent()
            is_vip = any(vip in message.from_email for vip in self.vip_senders)
            is_invoice = message.is_invoice_related()
            
            if is_vip:
                priority = 'high'
            elif is_urgent:
                priority = 'high'
            elif is_invoice:
                priority = 'high'
            else:
                priority = 'normal'
            
            # Generate frontmatter
            frontmatter = self.generate_frontmatter(
                item_type='email',
                from_email=f'"{message.from_email}"',
                subject=f'"{message.subject}"',
                received=datetime.now().isoformat(),
                priority=f'"{priority}"',
                message_id=f'"{message.message_id}"',
                status='pending',
                is_urgent=str(is_urgent).lower(),
                is_invoice_related=str(is_invoice).lower()
            )
            
            # Determine suggested actions based on content
            suggested_actions = self._get_suggested_actions(message)
            
            # Create action file content
            content = f'''{frontmatter}

# Email for Processing

## Email Details
- **From:** {message.from_email}
- **To:** {message.to}
- **Subject:** {message.subject}
- **Received:** {message.date or datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Priority:** {priority.title()}
- **Urgent:** {"Yes ⚠️" if is_urgent else "No"}
- **Invoice Related:** {"Yes 💰" if is_invoice else "No"}

## Email Preview
{message.snippet}

## Full Email Body
{message.body if message.body else "*No plain text body available*"}

## Suggested Actions
{chr(10).join(f'- [ ] {action}' for action in suggested_actions)}

## Response Draft
_Add your response draft here_

## Notes
_Add any notes or context_
'''
            
            # Generate filename
            safe_subject = ''.join(c for c in message.subject if c.isalnum() or c in '-_ ')[:30]
            sender_name = message.from_email.split('@')[0].split('<')[-1].strip()[:20]
            filename = self.safe_filename('EMAIL', f'{safe_subject}_{sender_name}')
            filepath = self.needs_action / filename
            
            filepath.write_text(content, encoding='utf-8')
            
            self.logger.info(f'Created action file for email from {message.from_email}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file for email: {e}')
            import traceback
            self.logger.debug(traceback.format_exc())
            return None
    
    def _get_suggested_actions(self, message: GmailMessage) -> List[str]:
        """Get suggested actions based on email content."""
        actions = []
        text = f"{message.subject} {message.snippet} {message.body}".lower()
        
        if message.is_invoice_related():
            actions.append('Process payment/invoice request')
            actions.append('Verify amount and details')
            actions.append('Create approval request (required for payments)')
        
        if any(kw in text for kw in ['meeting', 'schedule', 'calendar', 'appointment']):
            actions.append('Check calendar availability')
            actions.append('Draft response with available times')
            actions.append('Create calendar event after confirmation')
        
        if any(kw in text for kw in ['urgent', 'asap', 'emergency', 'immediately']):
            actions.append('⚠️ PRIORITIZE - Respond within 1 hour')
        
        if any(kw in text for kw in ['question', 'help', 'support', 'inquiry']):
            actions.append('Research and draft response')
        
        if any(kw in text for kw in ['proposal', 'quote', 'estimate']):
            actions.append('Prepare proposal/quote')
            actions.append('Create approval request before sending')
        
        # Default actions
        if not actions:
            actions.append('Read full email content')
            actions.append('Determine appropriate response')
        
        actions.append('Archive email after processing')
        
        return actions


if __name__ == '__main__':
    # Default vault path
    vault_path = r'D:\FTE_AI_Employee\AI_Employee_Vault'
    
    # Credentials path from command line
    credentials_path = None
    if len(sys.argv) > 1:
        credentials_path = sys.argv[1]
    
    watcher = GmailWatcher(vault_path, credentials_path, check_interval=120)
    print('\n' + '='*60)
    print('GMAIL WATCHER - Silver Tier')
    print('='*60)
    print(f'Vault: {vault_path}')
    print(f'Check interval: 120 seconds')
    print('Monitoring Gmail for new unread messages...')
    print('Press Ctrl+C to stop')
    print('='*60 + '\n')
    watcher.run()
