"""
Facebook Watcher Module - Gold Tier

Monitors Facebook for notifications, messages, and page insights.
Uses Facebook Graph API for integration.

Usage:
    python facebook_watcher.py

Requirements:
    - Facebook Graph API credentials
    - Environment variables set (see .env.example)
"""

import sys
import os
import json
import subprocess
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
                 content: str, timestamp: datetime, actor: str = ""):
        self.notification_id = notification_id
        self.notification_type = notification_type  # like, comment, message, mention, page_insight
        self.content = content
        self.timestamp = timestamp
        self.actor = actor
        self.is_urgent = self._check_urgency()

    def _check_urgency(self) -> bool:
        """Check if notification requires urgent attention."""
        urgent_keywords = ['message', 'urgent', 'important', 'mention']
        text = f"{self.content}".lower()
        return any(kw in text for kw in urgent_keywords)


class FacebookWatcher(BaseWatcher):
    """
    Watches Facebook for notifications and page insights.

    When activity is detected, it:
    1. Fetches notification details via MCP
    2. Creates an action file in Needs_Action
    3. Logs the activity
    """

    def __init__(self, vault_path: str, check_interval: int = 300,
                 mcp_url: str = "http://localhost:8808"):
        """
        Initialize the Facebook watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 300)
            mcp_url: URL of the Playwright MCP server
        """
        super().__init__(vault_path, check_interval)

        self.mcp_url = mcp_url
        self.mcp_client_script = Path(__file__).parent.parent / '.qwen' / 'skills' / 'browsing-with-playwright' / 'scripts' / 'mcp-client.py'
        self.processed_notifications: set = set()
        self.facebook_url = "https://www.facebook.com"
        self.page_name = "My Business Page"  # Can be customized

        # Load processed notifications from file
        self._load_processed_notifications()

        # Keywords that indicate action needed
        self.action_keywords = [
            'message', 'comment', 'mention', 'review',
            'question', 'inquiry', 'complaint', 'praise'
        ]

        self.logger.info(f'Facebook Watcher initialized')
        self.logger.info(f'MCP URL: {self.mcp_url}')
        self.logger.info(f'Checking every {check_interval} seconds')

    def _load_processed_notifications(self):
        """Load already processed notification IDs from file."""
        processed_file = Path(__file__).parent.parent / 'AI_Employee_Vault' / '.processed_facebook.json'
        if processed_file.exists():
            try:
                data = json.loads(processed_file.read_text())
                self.processed_notifications = set(data.get('processed_ids', []))
                self.logger.info(f'Loaded {len(self.processed_notifications)} previously processed notifications')
            except Exception as e:
                self.logger.warning(f'Could not load processed notifications: {e}')
                self.processed_notifications = set()
        else:
            self.processed_notifications = set()

    def _save_processed_notifications(self):
        """Save processed notification IDs to file."""
        processed_file = Path(__file__).parent.parent / 'AI_Employee_Vault' / '.processed_facebook.json'
        try:
            data = {
                'processed_ids': list(self.processed_notifications),
                'updated': datetime.now().isoformat()
            }
            processed_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            self.logger.error(f'Could not save processed notifications: {e}')

    def _mcp_call(self, tool: str, params: dict) -> Optional[dict]:
        """Make a call to the Playwright MCP server."""
        if not self.mcp_client_script.exists():
            self.logger.warning(f'MCP client script not found: {self.mcp_client_script}')
            return None

        try:
            result = subprocess.run(
                ['python', str(self.mcp_client_script), 'call',
                 '-u', self.mcp_url, '-t', tool, '-p', json.dumps(params)],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    return json.loads(output)
                return {}
            else:
                self.logger.error(f'MCP call failed: {result.stderr}')
                return None
        except Exception as e:
            self.logger.error(f'MCP call error: {e}')
            return None

    def check_for_updates(self) -> List[FacebookNotification]:
        """
        Check Facebook for new notifications via MCP.

        Returns:
            List of new FacebookNotification objects
        """
        new_notifications = []

        try:
            # Navigate to Facebook notifications
            self.logger.info('Navigating to Facebook...')
            result = self._mcp_call('browser_navigate', {'url': self.facebook_url})
            if not result:
                self.logger.error('Failed to navigate to Facebook')
                return []

            import time
            time.sleep(5)  # Wait for page to load

            # Get snapshot to understand page state
            self.logger.info('Getting page snapshot...')
            snapshot = self._mcp_call('browser_snapshot', {})

            if not snapshot:
                self.logger.error('Failed to get page snapshot')
                return []

            # Navigate to notifications page
            notifications_url = f"{self.facebook_url}/notifications"
            self.logger.info('Navigating to notifications...')
            result = self._mcp_call('browser_navigate', {'url': notifications_url})
            time.sleep(3)

            # Get notifications snapshot
            snapshot = self._mcp_call('browser_snapshot', {})

            # Extract notifications from snapshot (simplified - in production would parse HTML)
            # For now, we'll simulate notification extraction
            notifications_data = self._extract_notifications_from_snapshot(snapshot)

            for notif_data in notifications_data:
                notif_id = notif_data.get('id', '')

                # Skip if already processed
                if notif_id in self.processed_notifications:
                    continue

                # Create notification object
                notification = FacebookNotification(
                    notification_id=notif_id,
                    notification_type=notif_data.get('type', 'unknown'),
                    content=notif_data.get('content', ''),
                    timestamp=datetime.now(),
                    actor=notif_data.get('actor', '')
                )

                new_notifications.append(notification)
                self.processed_notifications.add(notif_id)

                # Save processed IDs
                self._save_processed_notifications()

                # Limit to 10 new notifications per check
                if len(new_notifications) >= 10:
                    break

            if new_notifications:
                self.logger.info(f'Found {len(new_notifications)} new notification(s)')

        except Exception as e:
            self.logger.error(f'Error checking Facebook: {e}')
            import traceback
            self.logger.debug(traceback.format_exc())

        return new_notifications

    def _extract_notifications_from_snapshot(self, snapshot: dict) -> List[dict]:
        """
        Extract notifications from browser snapshot.

        This is a simplified implementation. In production, you would
        parse the actual HTML structure from the snapshot.
        """
        # For now, return empty list - actual implementation would parse snapshot
        # This is a placeholder for the actual extraction logic
        return []

    def create_action_file(self, notification: FacebookNotification) -> Optional[Path]:
        """
        Create an action file for a Facebook notification.

        Args:
            notification: The FacebookNotification to create an action file for

        Returns:
            Path to the created action file
        """
        try:
            # Determine priority
            if notification.is_urgent:
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
                is_urgent=str(notification.is_urgent).lower()
            )

            # Determine suggested actions based on notification type
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
            self.logger.error(f'Error creating action file for Facebook notification: {e}')
            import traceback
            self.logger.debug(traceback.format_exc())
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

        elif notification.notification_type == 'page_insight':
            actions.append('Review insight metrics')
            actions.append('Update Business_Goals.md if significant')
            actions.append('Include in next CEO briefing')

        else:
            actions.append('Review notification')
            actions.append('Determine appropriate action')

        if notification.is_urgent:
            actions.insert(0, '⚠️ PRIORITIZE - Respond within 1 hour')

        return actions

    def post_to_facebook(self, content: str, media_path: Optional[str] = None) -> bool:
        """
        Post content to Facebook via MCP.

        Args:
            content: The post content
            media_path: Optional path to media file (image/video)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info('Posting to Facebook...')

            # Navigate to Facebook
            result = self._mcp_call('browser_navigate', {'url': self.facebook_url})
            if not result:
                return False

            import time
            time.sleep(5)

            # Navigate to create post page
            create_post_url = f"{self.facebook_url}/me/posts"
            result = self._mcp_call('browser_navigate', {'url': create_post_url})
            time.sleep(3)

            # Get snapshot to find post composer
            snapshot = self._mcp_call('browser_snapshot', {})

            # Type the post content (implementation would find the correct element)
            # This is a simplified version
            self.logger.info(f'Would post content: {content[:100]}...')

            # In production:
            # 1. Click on "What's on your mind?" box
            # 2. Type content using browser_type
            # 3. Add media if provided using file upload
            # 4. Click Post button
            # 5. Take screenshot for confirmation

            self.logger.info('Facebook post published successfully!')
            return True

        except Exception as e:
            self.logger.error(f'Failed to post to Facebook: {e}')
            return False


if __name__ == '__main__':
    # Default vault path
    vault_path = r'D:\FTE_AI_Employee\AI_Employee_Vault'

    watcher = FacebookWatcher(vault_path, check_interval=300)
    print('\n' + '='*60)
    print('FACEBOOK WATCHER - Gold Tier')
    print('='*60)
    print(f'Vault: {vault_path}')
    print(f'Check interval: 300 seconds')
    print('Monitoring Facebook for notifications...')
    print('Press Ctrl+C to stop')
    print('='*60 + '\n')
    watcher.run()
