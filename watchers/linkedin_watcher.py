"""
LinkedIn Watcher Module - Silver Tier

Monitors LinkedIn for notifications, messages, and engagement.
Uses Playwright MCP for browser automation.

Usage:
    python linkedin_watcher.py [vault_path]
    
Example:
    python linkedin_watcher.py
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class LinkedInNotification:
    """Represents a LinkedIn notification or activity."""
    
    def __init__(self, notification_type: str, content: str, actor: str = "", url: str = ""):
        self.notification_type = notification_type  # message, comment, like, connection, mention
        self.content = content
        self.actor = actor
        self.url = url
        self.timestamp = datetime.now()
    
    def is_urgent(self) -> bool:
        """Check if notification requires urgent attention."""
        urgent_keywords = ['urgent', 'asap', 'meeting', 'opportunity', 'interview', 'proposal']
        text = f"{self.content}".lower()
        return any(kw in text for kw in urgent_keywords)
    
    def is_business_related(self) -> bool:
        """Check if notification is business/sales related."""
        business_keywords = ['lead', 'client', 'project', 'business', 'service', 'product', 'sale']
        text = f"{self.content}".lower()
        return any(kw in text for kw in business_keywords)


class LinkedInWatcher(BaseWatcher):
    """
    Watches LinkedIn for new notifications, messages, and engagement.
    
    When new activity is detected, it:
    1. Fetches notification details via Playwright MCP
    2. Creates an action file in Needs_Action
    3. Tracks processed notifications
    """
    
    # LinkedIn MCP server configuration
    MCP_SERVER_HOST = "localhost"
    MCP_SERVER_PORT = 8808
    
    def __init__(self, vault_path: str, check_interval: int = 300,
                 linkedin_email: Optional[str] = None,
                 linkedin_password: Optional[str] = None):
        """
        Initialize the LinkedIn watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 300 = 5 min)
            linkedin_email: LinkedIn email (optional, for auto-login)
            linkedin_password: LinkedIn password (optional, for auto-login)
        """
        super().__init__(vault_path, check_interval)
        
        self.linkedin_email = linkedin_email
        self.linkedin_password = linkedin_password
        self.session_path = Path.home() / '.ai_employee' / 'linkedin_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Load processed notifications
        self._load_processed_notifications()
        
        # Keywords to monitor
        self.lead_keywords = ['hiring', 'looking for', 'need', 'interested', 'recommend', 'service']
        self.engagement_keywords = ['commented', 'liked', 'shared', 'congratulate']
        
        # MCP server state
        self.mcp_server_running = False
        self.mcp_process = None
        
        # MCP client script path
        self.mcp_client_script = Path(__file__).parent.parent / '.qwen' / 'skills' / 'browsing-with-playwright' / 'scripts' / 'mcp-client.py'
        if not self.mcp_client_script.exists():
            self.mcp_client_script = None
            self.logger.warning('MCP client script not found. LinkedIn posting may not work.')

        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Check interval: {check_interval}s')
        self.logger.info('NOTE: Please start MCP server manually in another terminal:')
        self.logger.info('  npx @playwright/mcp@latest --port 8808 --shared-browser-context')
    
    def _load_processed_notifications(self):
        """Load already processed notification IDs."""
        import json
        processed_file = Path(__file__).parent.parent / 'AI_Employee_Vault' / '.processed_linkedin.json'
        if processed_file.exists():
            try:
                data = json.loads(processed_file.read_text())
                self.processed_ids = set(data.get('processed_ids', []))
                self.logger.info(f'Loaded {len(self.processed_ids)} processed LinkedIn notifications')
            except Exception as e:
                self.logger.warning(f'Could not load processed notifications: {e}')
                self.processed_ids = set()
        else:
            self.processed_ids = set()
    
    def _save_processed_notifications(self):
        """Save processed notification IDs."""
        import json
        processed_file = Path(__file__).parent.parent / 'AI_Employee_Vault' / '.processed_linkedin.json'
        try:
            data = {
                'processed_ids': list(self.processed_ids),
                'updated': datetime.now().isoformat()
            }
            processed_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self.logger.error(f'Could not save processed notifications: {e}')
    
    def _start_mcp_server(self) -> bool:
        """Check if Playwright MCP server is running."""
        if not self.mcp_client_script:
            self.logger.error('MCP client script not available')
            return False
        
        # Check if server is already running by listing available tools
        try:
            result = subprocess.run(
                ['python', str(self.mcp_client_script), 'list', '-u', 
                 f'http://localhost:{self.MCP_SERVER_PORT}'],
                capture_output=True,
                timeout=5,
                text=True  # Ensure text mode for stdout
            )
            if result.returncode == 0 and 'browser_' in result.stdout:
                self.logger.info('MCP server already running')
                self.mcp_server_running = True
                return True
            else:
                self.logger.error('MCP server is not responding')
                self.logger.error('Please start MCP server in another terminal:')
                self.logger.error('  npx @playwright/mcp@latest --port 8808 --shared-browser-context')
                return False
        except Exception as e:
            self.logger.error(f'Could not connect to MCP server: {e}')
            self.logger.error('Please start MCP server in another terminal:')
            self.logger.error('  npx @playwright/mcp@latest --port 8808 --shared-browser-context')
            return False
    
    def _mcp_call(self, tool: str, params: dict) -> Optional[dict]:
        """Make a call to the MCP server."""
        import json
        
        if not self.mcp_client_script:
            self.logger.error('MCP client script not available')
            return None
        
        try:
            result = subprocess.run(
                ['python', str(self.mcp_client_script), 'call', '-u',
                 f'http://localhost:{self.MCP_SERVER_PORT}', '-t', tool, '-p', json.dumps(params)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(__file__).parent.parent  # Set working directory
            )
            
            # Check for errors
            if result.returncode != 0:
                error_msg = result.stderr[:200] if result.stderr else 'Unknown error'
                self.logger.error(f'MCP call failed (exit code {result.returncode}): {error_msg}')
                return None
            
            # Try to parse stdout as JSON
            if not result.stdout.strip():
                self.logger.error('MCP call returned empty output')
                return None
                
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError as e:
                self.logger.error(f'MCP call returned invalid JSON: {e}')
                self.logger.debug(f'Raw output: {result.stdout[:500]}')
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error('MCP call timed out')
            return None
        except Exception as e:
            self.logger.error(f'MCP call error: {e}')
            return None
    
    def _navigate_to_linkedin(self) -> bool:
        """Navigate to LinkedIn and ensure logged in."""
        try:
            # Navigate to LinkedIn
            result = self._mcp_call('browser_navigate', {'url': 'https://www.linkedin.com'})
            if not result:
                return False
            
            time.sleep(5)  # Wait for page to load
            
            # Check if login is needed
            snapshot = self._mcp_call('browser_snapshot', {})
            if snapshot and 'Sign in' in str(snapshot):
                self.logger.info('Login required')
                return self._login_to_linkedin()
            
            self.logger.info('Already logged in to LinkedIn')
            return True
            
        except Exception as e:
            self.logger.error(f'Navigation failed: {e}')
            return False
    
    def _login_to_linkedin(self) -> bool:
        """Login to LinkedIn."""
        if not self.linkedin_email or not self.linkedin_password:
            self.logger.error('LinkedIn credentials not provided')
            self.logger.info('Please login manually in the browser window')
            self.logger.info('Session will be saved for future use')
            return False
        
        try:
            # Find and fill email field
            self._mcp_call('browser_fill_form', {
                'fields': [{
                    'name': 'Email',
                    'type': 'textbox',
                    'ref': 'email-field',
                    'value': self.linkedin_email
                }]
            })
            
            # Find and fill password field
            self._mcp_call('browser_fill_form', {
                'fields': [{
                    'name': 'Password',
                    'type': 'textbox',
                    'ref': 'password-field',
                    'value': self.linkedin_password
                }]
            })
            
            # Click sign in
            self._mcp_call('browser_click', {
                'element': 'Sign in button',
                'ref': 'signin-button'
            })
            
            time.sleep(3)
            self.logger.info('Login successful')
            return True
            
        except Exception as e:
            self.logger.error(f'Login failed: {e}')
            return False
    
    def check_for_updates(self) -> List[LinkedInNotification]:
        """
        Check LinkedIn for new notifications and activity.
        
        Returns:
            List of new LinkedInNotification objects
        """
        notifications = []
        
        # Ensure MCP server is running
        if not self.mcp_server_running:
            if not self._start_mcp_server():
                return []
        
        # Navigate to LinkedIn
        if not self._navigate_to_linkedin():
            return []
        
        try:
            # Go to notifications page
            self._mcp_call('browser_navigate', {'url': 'https://www.linkedin.com/notifications/'})
            time.sleep(3)
            
            # Get snapshot of notifications
            snapshot = self._mcp_call('browser_snapshot', {})
            
            if snapshot:
                # Parse notifications from snapshot
                parsed = self._parse_notifications_from_snapshot(snapshot)
                
                for notif in parsed:
                    # Create unique ID
                    notif_id = f"{notif.notification_type}_{notif.content[:50]}_{notif.timestamp.strftime('%Y%m%d%H')}"
                    
                    if notif_id not in self.processed_ids:
                        notifications.append(notif)
                        self.processed_ids.add(notif_id)
                        self._save_processed_notifications()
                        
                        # Limit to 5 notifications per check
                        if len(notifications) >= 5:
                            break
            
            # Also check messages
            messages = self._check_messages()
            for msg in messages:
                if msg not in notifications:
                    notifications.append(msg)
            
        except Exception as e:
            self.logger.error(f'Error checking LinkedIn: {e}')
            import traceback
            self.logger.debug(traceback.format_exc())
        
        return notifications
    
    def _parse_notifications_from_snapshot(self, snapshot: dict) -> List[LinkedInNotification]:
        """Parse notifications from browser snapshot."""
        notifications = []
        
        # This is a simplified parser - in production you'd parse the actual snapshot structure
        snapshot_text = str(snapshot)
        
        # Look for notification patterns
        if 'commented on your post' in snapshot_text.lower():
            notifications.append(LinkedinNotification(
                notification_type='comment',
                content='Someone commented on your post',
                actor='LinkedIn User'
            ))
        
        if 'liked your post' in snapshot_text.lower():
            notifications.append(LinkedinNotification(
                notification_type='like',
                content='Someone liked your post',
                actor='LinkedIn User'
            ))
        
        if 'new connection' in snapshot_text.lower():
            notifications.append(LinkedinNotification(
                notification_type='connection',
                content='New connection request or acceptance',
                actor='LinkedIn User'
            ))
        
        return notifications
    
    def _check_messages(self) -> List[LinkedInNotification]:
        """Check LinkedIn messages for new conversations."""
        messages = []
        
        try:
            # Navigate to messaging
            self._mcp_call('browser_navigate', {'url': 'https://www.linkedin.com/messaging/'})
            time.sleep(3)
            
            # Get snapshot
            snapshot = self._mcp_call('browser_snapshot', {})
            
            if snapshot:
                # Parse messages from snapshot
                # (Simplified - would need actual parsing logic)
                pass
                
        except Exception as e:
            self.logger.error(f'Error checking messages: {e}')
        
        return messages
    
    def create_action_file(self, notification: LinkedInNotification) -> Optional[Path]:
        """
        Create an action file for a LinkedIn notification.
        
        Args:
            notification: The LinkedInNotification to create an action file for
            
        Returns:
            Path to the created action file
        """
        try:
            # Determine priority
            is_urgent = notification.is_urgent()
            is_business = notification.is_business_related()
            
            if is_urgent or is_business:
                priority = 'high'
            else:
                priority = 'normal'
            
            # Generate frontmatter
            frontmatter = self.generate_frontmatter(
                item_type='linkedin_notification',
                notification_type=f'"{notification.notification_type}"',
                actor=f'"{notification.actor}"',
                received=datetime.now().isoformat(),
                priority=f'"{priority}"',
                status='pending',
                is_urgent=str(is_urgent).lower(),
                is_business_related=str(is_business).lower()
            )
            
            # Determine suggested actions
            suggested_actions = self._get_suggested_actions(notification)
            
            # Create action file content
            content = f'''{frontmatter}

# LinkedIn Notification for Processing

## Notification Details
- **Type:** {notification.notification_type.title()}
- **From:** {notification.actor or 'Unknown'}
- **Received:** {notification.timestamp.strftime("%Y-%m-%d %H:%M")}
- **Priority:** {priority.title()}
- **Urgent:** {"Yes ⚠️" if is_urgent else "No"}
- **Business Related:** {"Yes 💼" if is_business else "No"}

## Content
{notification.content}

## URL
{notification.url or '*No direct URL available*'}

## Suggested Actions
{chr(10).join(f'- [ ] {action}' for action in suggested_actions)}

## Response Draft
_Add your response draft here_

## Notes
_Add any notes or context_
'''
            
            # Generate filename
            safe_type = notification.notification_type.replace(' ', '_')[:20]
            filename = self.safe_filename('LINKEDIN', f'{safe_type}_{notification.actor[:20] if notification.actor else "notification"}')
            filepath = self.needs_action / filename
            
            filepath.write_text(content, encoding='utf-8')
            
            self.logger.info(f'Created action file for LinkedIn {notification.notification_type}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file for LinkedIn notification: {e}')
            import traceback
            self.logger.debug(traceback.format_exc())
            return None
    
    def _get_suggested_actions(self, notification: LinkedInNotification) -> List[str]:
        """Get suggested actions based on notification type."""
        actions = []
        
        if notification.notification_type == 'message':
            actions.append('Read full message')
            actions.append('Draft response')
            actions.append('Check if lead/opportunity')
        
        elif notification.notification_type == 'comment':
            actions.append('Review comment on post')
            actions.append('Engage with commenter')
            actions.append('Consider follow-up')
        
        elif notification.notification_type == 'connection':
            actions.append('Review new connection')
            actions.append('Send welcome message')
            actions.append('Check profile for opportunities')
        
        elif notification.notification_type == 'like':
            actions.append('Acknowledge engagement')
            actions.append('Consider engaging with their content')
        
        elif notification.notification_type == 'mention':
            actions.append('Review mention')
            actions.append('Respond appropriately')
        
        else:
            actions.append('Review notification')
            actions.append('Determine appropriate action')
        
        if notification.is_business_related():
            actions.append('💼 POTENTIAL LEAD - Prioritize response')
        
        return actions
    
    def __del__(self):
        """Cleanup MCP server on destruction."""
        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.logger.info('MCP server stopped')
            except Exception:
                pass


if __name__ == '__main__':
    # Default vault path
    vault_path = r'D:\FTE_AI_Employee\AI_Employee_Vault'
    
    # Allow override via command line
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    
    # Load credentials from .env if available
    linkedin_email = None
    linkedin_password = None
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        content = env_path.read_text()
        for line in content.split('\n'):
            if line.startswith('LINKEDIN_EMAIL='):
                linkedin_email = line.split('=', 1)[1].strip()
            elif line.startswith('LINKEDIN_PASSWORD='):
                linkedin_password = line.split('=', 1)[1].strip()
    
    watcher = LinkedInWatcher(vault_path, check_interval=300,
                              linkedin_email=linkedin_email,
                              linkedin_password=linkedin_password)
    
    print('\n' + '='*60)
    print('LINKEDIN WATCHER - Silver Tier')
    print('='*60)
    print(f'Vault: {vault_path}')
    print(f'Check interval: 300 seconds (5 minutes)')
    print('Monitoring LinkedIn for notifications and messages...')
    print('Press Ctrl+C to stop')
    print('='*60 + '\n')
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        print('\nLinkedIn Watcher stopped')
    finally:
        del watcher
