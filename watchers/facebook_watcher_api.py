"""
Facebook Watcher Module - Gold Tier (Graph API)

Monitors Facebook for notifications, messages, and page insights.
Uses Facebook Graph API for integration.

Usage:
    python facebook_watcher.py

Requirements:
    - Facebook Graph API credentials
    - Environment variables: FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID
"""

import sys
import os
import json
import httpx
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class FacebookNotification:
    """Represents a Facebook notification."""

    def __init__(self, notification_id: str, notification_type: str,
                 content: str, timestamp: datetime, actor: str = "",
                 unread: bool = True):
        self.notification_id = notification_id
        self.notification_type = notification_type
        self.content = content
        self.timestamp = timestamp
        self.actor = actor
        self.unread = unread
        self.is_urgent = self._check_urgency()

    def _check_urgency(self) -> bool:
        """Check if notification requires urgent attention."""
        urgent_keywords = ['message', 'urgent', 'important', 'mention']
        text = f"{self.content}".lower()
        return any(kw in text for kw in urgent_keywords)


class FacebookGraphClient:
    """Client for Facebook Graph API."""

    def __init__(self, access_token: str, page_id: Optional[str] = None):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.client = httpx.Client(timeout=30.0)

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to Graph API."""
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        params['access_token'] = self.access_token

        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make POST request to Graph API."""
        url = f"{self.base_url}/{endpoint}"
        if data is None:
            data = {}
        data['access_token'] = self.access_token

        response = self.client.post(url, data=data)
        response.raise_for_status()
        return response.json()

    def get_profile(self) -> Dict:
        """Get current user profile or page info."""
        if self.page_id:
            return self.get(self.page_id, {
                'fields': 'id,name,username,about,fan_count,website'
            })
        else:
            return self.get('me', {
                'fields': 'id,name,email,picture'
            })

    def post_to_feed(self, message: str, link: Optional[str] = None,
                     photo_url: Optional[str] = None) -> Dict:
        """Post to Facebook feed."""
        endpoint = f"{self.page_id}/feed" if self.page_id else 'me/feed'
        data = {'message': message}
        if link:
            data['link'] = link
        if photo_url:
            data['picture'] = photo_url
        return self.post(endpoint, data)

    def get_notifications(self, limit: int = 10) -> List[Dict]:
        """Get recent notifications."""
        result = self.get('me/notifications', {
            'limit': limit,
            'fields': 'from,message,created_time,unread,type'
        })
        return result.get('data', [])

    def get_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages."""
        if self.page_id:
            result = self.get(f"{self.page_id}/conversations", {
                'limit': limit,
                'fields': 'messages{from,message,created_time},updated_time'
            })
        else:
            result = self.get('me/conversations', {
                'limit': limit,
                'fields': 'messages{from,message,created_time},updated_time'
            })
        return result.get('data', [])

    def get_posts(self, limit: int = 10) -> List[Dict]:
        """Get recent posts."""
        endpoint = f"{self.page_id}/feed" if self.page_id else 'me/feed'
        result = self.get(endpoint, {
            'limit': limit,
            'fields': 'id,message,created_time,updated_time'
        })
        return result.get('data', [])


class FacebookWatcher(BaseWatcher):
    """
    Watches Facebook for notifications and messages using Graph API.
    """

    def __init__(self, vault_path: str, check_interval: int = 300):
        """
        Initialize the Facebook watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 300)
        """
        super().__init__(vault_path, check_interval)

        # Initialize Facebook client
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.client = None

        if self.access_token:
            self.client = FacebookGraphClient(self.access_token, self.page_id)
            self.logger.info('Facebook client initialized')
        else:
            self.logger.warning('FACEBOOK_ACCESS_TOKEN not set')

        self.processed_notification_ids: set = set()
        self._load_processed_notifications()

        # Keywords that indicate action needed
        self.action_keywords = [
            'message', 'comment', 'mention', 'review',
            'question', 'inquiry', 'complaint', 'praise'
        ]

    def _load_processed_notifications(self):
        """Load already processed notification IDs from file."""
        processed_file = Path(__file__).parent.parent / 'AI_Employee_Vault' / '.processed_facebook.json'
        if processed_file.exists():
            try:
                data = json.loads(processed_file.read_text())
                self.processed_notification_ids = set(data.get('processed_ids', []))
                self.logger.info(f'Loaded {len(self.processed_notification_ids)} processed notifications')
            except Exception as e:
                self.logger.warning(f'Could not load processed notifications: {e}')
                self.processed_notification_ids = set()
        else:
            self.processed_notification_ids = set()

    def _save_processed_notifications(self):
        """Save processed notification IDs to file."""
        processed_file = Path(__file__).parent.parent / 'AI_Employee_Vault' / '.processed_facebook.json'
        try:
            data = {
                'processed_ids': list(self.processed_notification_ids),
                'updated': datetime.now().isoformat()
            }
            processed_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self.logger.error(f'Could not save processed notifications: {e}')

    def check_for_updates(self) -> List[FacebookNotification]:
        """Check Facebook for new notifications."""
        if not self.client:
            self.logger.error('Facebook client not initialized')
            return []

        new_notifications = []

        try:
            self.logger.info('Fetching Facebook notifications...')
            notifications_data = self.client.get_notifications(limit=20)

            for notif_data in notifications_data:
                notif_id = notif_data.get('id', '')

                # Skip if already processed
                if notif_id in self.processed_notification_ids:
                    continue

                # Parse notification
                from_name = notif_data.get('from', {}).get('name', 'Unknown')
                message = notif_data.get('message', '')
                notif_type = notif_data.get('type', 'unknown')
                created_time = notif_data.get('created_time', '')
                unread = notif_data.get('unread', False)

                # Parse timestamp
                try:
                    timestamp = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.now()

                # Create notification object
                notification = FacebookNotification(
                    notification_id=notif_id,
                    notification_type=notif_type,
                    content=message,
                    timestamp=timestamp,
                    actor=from_name,
                    unread=unread
                )

                new_notifications.append(notification)
                self.processed_notification_ids.add(notif_id)

                # Save processed IDs
                self._save_processed_notifications()

                # Limit to 10 new notifications per check
                if len(new_notifications) >= 10:
                    break

            if new_notifications:
                self.logger.info(f'Found {len(new_notifications)} new notification(s)')

        except Exception as e:
            self.logger.error(f'Error checking Facebook: {e}')

        return new_notifications

    def create_action_file(self, notification: FacebookNotification) -> Optional[Path]:
        """Create an action file for a Facebook notification."""
        try:
            # Determine priority
            if notification.is_urgent or notification.unread:
                priority = 'high'
            elif notification.notification_type in ['message', 'mention']:
                priority = 'high'
            elif notification.notification_type == 'comment':
                priority = 'normal'
            else:
                priority = 'low'

            # Generate frontmatter
            frontmatter = self.generate_frontmatter(
                item_type='facebook_notification',
                notification_id=f'"{notification.notification_id}"',
                notification_type=f'"{notification.notification_type}"',
                actor=f'"{notification.actor}"',
                received=datetime.now().isoformat(),
                priority=f'"{priority}"',
                status='pending',
                is_urgent=str(notification.is_urgent).lower(),
                unread=str(notification.unread).lower()
            )

            # Determine suggested actions
            suggested_actions = self._get_suggested_actions(notification)

            # Create action file content
            content = f'''{frontmatter}

# Facebook Notification for Processing

## Notification Details
- **Type:** {notification.notification_type.replace('_', ' ').title()}
- **From:** {notification.actor or 'Unknown'}
- **Received:** {notification.timestamp.strftime("%Y-%m-%d %H:%M")}
- **Priority:** {priority.title()}
- **Urgent:** {"Yes ⚠️" if notification.is_urgent else "No"}
- **Unread:** {"Yes" if notification.unread else "No"}

## Notification Content
{notification.content}

## Suggested Actions
{chr(10).join(f'- [ ] {action}' for action in suggested_actions)}

## Response Draft
_Add your response draft here_

## Notes
_Add any notes or context_
'''

            # Generate filename
            safe_content = ''.join(c for c in notification.content if c.isalnum() or c in '-_ ')[:30]
            filename = self.safe_filename('FACEBOOK', f'{notification.notification_type}_{safe_content}')
            filepath = self.needs_action / filename

            filepath.write_text(content, encoding='utf-8')

            self.logger.info(f'Created action file for Facebook {notification.notification_type}')
            return filepath

        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None

    def _get_suggested_actions(self, notification: FacebookNotification) -> List[str]:
        """Get suggested actions based on notification type."""
        actions = []

        if notification.notification_type == 'message':
            actions.append('Read message content')
            actions.append('Draft response (requires approval before sending)')
            actions.append('Create approval request for response')

        elif notification.notification_type == 'comment':
            actions.append('Review comment on post')
            actions.append('Determine if response needed')
            actions.append('Draft response if appropriate (requires approval)')

        elif notification.notification_type == 'mention':
            actions.append('Review mention context')
            actions.append('Consider engaging with mention')
            actions.append('Draft thank you or response (requires approval)')

        elif notification.notification_type == 'page_review':
            actions.append('Read review content')
            actions.append('Draft professional response (requires approval)')
            actions.append('Log review for business insights')

        else:
            actions.append('Review notification')
            actions.append('Determine appropriate action')

        if notification.is_urgent:
            actions.insert(0, '⚠️ PRIORITIZE - Respond within 1 hour')

        return actions

    def post_to_facebook(self, content: str, link: Optional[str] = None,
                         photo_url: Optional[str] = None) -> bool:
        """
        Post content to Facebook via Graph API.

        Args:
            content: The post content
            link: Optional link to share
            photo_url: Optional photo URL

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            self.logger.error('Facebook client not initialized')
            return False

        try:
            self.logger.info(f'Posting to Facebook: {content[:100]}...')

            result = self.client.post_to_feed(content, link, photo_url)

            if result.get('id'):
                self.logger.info(f'Facebook post published successfully! ID: {result["id"]}')
                self._log_facebook_post(content, result.get('id'))
                return True
            else:
                self.logger.error('Facebook post failed - no ID returned')
                return False

        except Exception as e:
            self.logger.error(f'Failed to post to Facebook: {e}')
            return False

    def _log_facebook_post(self, content: str, post_id: str):
        """Log Facebook post to log file."""
        log_file = self.vault_path / 'Logs' / 'facebook_posts.md'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        log_entry = f'\n| {timestamp} | {content[:50]}... | ✅ Posted | ID: {post_id} |\n'

        if not log_file.exists():
            log_file.write_text('# Facebook Posts Log\n\n| Date | Content | Status | Post ID |\n|------|---------|--------|------------|\n')

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)


if __name__ == '__main__':
    # Default vault path
    vault_path = r'D:\FTE_AI_Employee\AI_Employee_Vault'

    # Check for credentials
    if not os.getenv('FACEBOOK_ACCESS_TOKEN'):
        print('\n' + '='*60)
        print('FACEBOOK WATCHER - Gold Tier')
        print('='*60)
        print('\nERROR: FACEBOOK_ACCESS_TOKEN not set!')
        print('\nPlease set environment variables:')
        print('  - FACEBOOK_APP_ID')
        print('  - FACEBOOK_APP_SECRET')
        print('  - FACEBOOK_ACCESS_TOKEN')
        print('  - FACEBOOK_PAGE_ID (optional, for business pages)')
        print('\nSee facebook-mcp-server/README.md for setup guide.')
        print('='*60)
        sys.exit(1)

    watcher = FacebookWatcher(vault_path, check_interval=300)
    print('\n' + '='*60)
    print('FACEBOOK WATCHER - Gold Tier (Graph API)')
    print('='*60)
    print(f'Vault: {vault_path}')
    print(f'Check interval: 300 seconds')
    print('Monitoring Facebook for notifications...')
    print('Press Ctrl+C to stop')
    print('='*60 + '\n')
    watcher.run()
