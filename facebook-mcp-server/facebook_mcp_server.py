"""
Facebook MCP Server - Gold Tier

Model Context Protocol server for Facebook Graph API integration.
Provides posting, notifications, and page management capabilities.

Usage:
    python facebook_mcp_server.py

Configuration:
    Set environment variables:
    - FACEBOOK_APP_ID
    - FACEBOOK_APP_SECRET
    - FACEBOOK_ACCESS_TOKEN
    - FACEBOOK_PAGE_ID (for business pages)
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('facebook-mcp-server')


class FacebookGraphClient:
    """Client for Facebook Graph API."""

    def __init__(self, access_token: str, page_id: Optional[str] = None):
        """
        Initialize Facebook Graph API client.

        Args:
            access_token: Facebook access token with appropriate permissions
            page_id: Facebook Page ID (for business pages)
        """
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make GET request to Graph API."""
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        params['access_token'] = self.access_token

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Facebook API error: {e}")
            raise

    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make POST request to Graph API."""
        url = f"{self.base_url}/{endpoint}"
        if data is None:
            data = {}
        data['access_token'] = self.access_token

        try:
            response = await self.client.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Facebook API error: {e}")
            raise

    async def get_profile(self) -> Dict:
        """Get current user profile or page info."""
        if self.page_id:
            return await self.get(self.page_id, {
                'fields': 'id,name,username,about,fan_count,website'
            })
        else:
            return await self.get('me', {
                'fields': 'id,name,email,picture'
            })

    async def post_to_feed(self, message: str, link: Optional[str] = None,
                           photo_url: Optional[str] = None) -> Dict:
        """
        Post to Facebook feed.

        Args:
            message: Post message
            link: Optional link to share
            photo_url: Optional photo URL

        Returns:
            Post ID
        """
        endpoint = f"{self.page_id}/feed" if self.page_id else 'me/feed'

        data = {'message': message}
        if link:
            data['link'] = link
        if photo_url:
            data['picture'] = photo_url

        return await self.post(endpoint, data)

    async def post_photo(self, message: str, photo_url: str) -> Dict:
        """
        Post photo to Facebook.

        Args:
            message: Caption for the photo
            photo_url: URL of the photo

        Returns:
            Post ID
        """
        endpoint = f"{self.page_id}/photos" if self.page_id else 'me/photos'

        data = {
            'message': message,
            'url': photo_url
        }

        return await self.post(endpoint, data)

    async def get_notifications(self, limit: int = 10) -> List[Dict]:
        """Get recent notifications."""
        result = await self.get('me/notifications', {
            'limit': limit,
            'fields': 'from,message,created_time,unread,type'
        })
        return result.get('data', [])

    async def get_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages (requires page access token for pages)."""
        if self.page_id:
            result = await self.get(f"{self.page_id}/conversations", {
                'limit': limit,
                'fields': 'messages{from,message,created_time},updated_time'
            })
        else:
            result = await self.get('me/conversations', {
                'limit': limit,
                'fields': 'messages{from,message,created_time},updated_time'
            })
        return result.get('data', [])

    async def get_page_insights(self, metrics: Optional[List[str]] = None,
                                period: str = 'day') -> Dict:
        """
        Get page insights (analytics).

        Args:
            metrics: List of metrics to fetch
            period: Time period (day, week, month)

        Returns:
            Insights data
        """
        if not self.page_id:
            return {'error': 'Page ID required for insights'}

        if metrics is None:
            metrics = [
                'page_impressions_unique',
                'page_engaged_users',
                'page_post_engagements',
                'page_likes',
                'page_follows'
            ]

        result = await self.get(f"{self.page_id}/insights", {
            'metric': ','.join(metrics),
            'period': period
        })
        return result.get('data', [])

    async def get_posts(self, limit: int = 10) -> List[Dict]:
        """Get recent posts."""
        endpoint = f"{self.page_id}/feed" if self.page_id else 'me/feed'
        result = await self.get(endpoint, {
            'limit': limit,
            'fields': 'id,message,created_time,updated_time,likes,comments,shares'
        })
        return result.get('data', [])

    async def send_message(self, recipient_id: str, message: str) -> Dict:
        """
        Send message via Messenger (requires page access token).

        Args:
            recipient_id: Recipient's Facebook ID
            message: Message text

        Returns:
            Message ID
        """
        if not self.page_id:
            return {'error': 'Page access token required'}

        data = {
            'recipient': {'id': recipient_id},
            'message': {'text': message},
            'messaging_type': 'RESPONSE'
        }

        return await self.post(f"{self.page_id}/messages", data)


# Create MCP server
server = Server('facebook-mcp')

# Global Facebook client (will be initialized from env vars)
fb_client: Optional[FacebookGraphClient] = None


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Facebook tools."""
    return [
        Tool(
            name='facebook_connect',
            description='Connect to Facebook and verify authentication',
            inputSchema={
                'type': 'object',
                'properties': {}
            }
        ),
        Tool(
            name='facebook_get_profile',
            description='Get Facebook profile or page information',
            inputSchema={
                'type': 'object',
                'properties': {}
            }
        ),
        Tool(
            name='facebook_post',
            description='Create a post on Facebook',
            inputSchema={
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': 'Post message/content'
                    },
                    'link': {
                        'type': 'string',
                        'description': 'Optional link to share'
                    },
                    'photo_url': {
                        'type': 'string',
                        'description': 'Optional photo URL'
                    }
                },
                'required': ['message']
            }
        ),
        Tool(
            name='facebook_post_photo',
            description='Post a photo to Facebook',
            inputSchema={
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'description': 'Photo caption'
                    },
                    'photo_url': {
                        'type': 'string',
                        'description': 'URL of the photo'
                    }
                },
                'required': ['message', 'photo_url']
            }
        ),
        Tool(
            name='facebook_get_notifications',
            description='Get recent Facebook notifications',
            inputSchema={
                'type': 'object',
                'properties': {
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of notifications to fetch',
                        'default': 10
                    }
                }
            }
        ),
        Tool(
            name='facebook_get_messages',
            description='Get recent Facebook messages',
            inputSchema={
                'type': 'object',
                'properties': {
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of conversations to fetch',
                        'default': 10
                    }
                }
            }
        ),
        Tool(
            name='facebook_get_posts',
            description='Get recent posts from profile or page',
            inputSchema={
                'type': 'object',
                'properties': {
                    'limit': {
                        'type': 'integer',
                        'description': 'Number of posts to fetch',
                        'default': 10
                    }
                }
            }
        ),
        Tool(
            name='facebook_get_insights',
            description='Get page insights/analytics (requires page access)',
            inputSchema={
                'type': 'object',
                'properties': {
                    'metrics': {
                        'type': 'array',
                        'description': 'Metrics to fetch',
                        'items': {'type': 'string'}
                    },
                    'period': {
                        'type': 'string',
                        'description': 'Time period',
                        'enum': ['day', 'week', 'month'],
                        'default': 'day'
                    }
                }
            }
        ),
        Tool(
            name='facebook_send_message',
            description='Send message via Messenger (requires page access)',
            inputSchema={
                'type': 'object',
                'properties': {
                    'recipient_id': {
                        'type': 'string',
                        'description': 'Recipient Facebook ID'
                    },
                    'message': {
                        'type': 'string',
                        'description': 'Message text'
                    }
                },
                'required': ['recipient_id', 'message']
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    global fb_client

    try:
        if name == 'facebook_connect':
            if not fb_client:
                return [TextContent(type='text', text='Error: Facebook client not initialized')]

            profile = await fb_client.get_profile()
            return [TextContent(
                type='text',
                text=json.dumps({
                    'success': True,
                    'profile': profile
                }, indent=2)
            )]

        elif name == 'facebook_get_profile':
            if not fb_client:
                return [TextContent(type='text', text='Error: Not connected to Facebook')]

            profile = await fb_client.get_profile()
            return [TextContent(
                type='text',
                text=json.dumps(profile, indent=2)
            )]

        elif name == 'facebook_post':
            if not fb_client:
                return [TextContent(type='text', text='Error: Not connected to Facebook')]

            message = arguments.get('message')
            link = arguments.get('link')
            photo_url = arguments.get('photo_url')

            result = await fb_client.post_to_feed(message, link, photo_url)
            return [TextContent(
                type='text',
                text=json.dumps({
                    'success': True,
                    'post_id': result.get('id'),
                    'message': 'Post created successfully'
                }, indent=2)
            )]

        elif name == 'facebook_post_photo':
            if not fb_client:
                return [TextContent(type='text', text='Error: Not connected to Facebook')]

            message = arguments.get('message')
            photo_url = arguments.get('photo_url')

            result = await fb_client.post_photo(message, photo_url)
            return [TextContent(
                type='text',
                text=json.dumps({
                    'success': True,
                    'post_id': result.get('id'),
                    'message': 'Photo posted successfully'
                }, indent=2)
            )]

        elif name == 'facebook_get_notifications':
            if not fb_client:
                return [TextContent(type='text', text='Error: Not connected to Facebook')]

            limit = arguments.get('limit', 10)
            notifications = await fb_client.get_notifications(limit)
            return [TextContent(
                type='text',
                text=json.dumps({'notifications': notifications}, indent=2)
            )]

        elif name == 'facebook_get_messages':
            if not fb_client:
                return [TextContent(type='text', text='Error: Not connected to Facebook')]

            limit = arguments.get('limit', 10)
            messages = await fb_client.get_messages(limit)
            return [TextContent(
                type='text',
                text=json.dumps({'messages': messages}, indent=2)
            )]

        elif name == 'facebook_get_posts':
            if not fb_client:
                return [TextContent(type='text', text='Error: Not connected to Facebook')]

            limit = arguments.get('limit', 10)
            posts = await fb_client.get_posts(limit)
            return [TextContent(
                type='text',
                text=json.dumps({'posts': posts}, indent=2)
            )]

        elif name == 'facebook_get_insights':
            if not fb_client:
                return [TextContent(type='text', text='Error: Not connected to Facebook')]

            metrics = arguments.get('metrics')
            period = arguments.get('period', 'day')
            insights = await fb_client.get_page_insights(metrics, period)
            return [TextContent(
                type='text',
                text=json.dumps({'insights': insights}, indent=2)
            )]

        elif name == 'facebook_send_message':
            if not fb_client:
                return [TextContent(type='text', text='Error: Not connected to Facebook')]

            recipient_id = arguments.get('recipient_id')
            message = arguments.get('message')

            result = await fb_client.send_message(recipient_id, message)
            return [TextContent(
                type='text',
                text=json.dumps(result, indent=2)
            )]

        else:
            return [TextContent(type='text', text=f'Unknown tool: {name}')]

    except Exception as e:
        logger.error(f'Error in tool call {name}: {e}')
        return [TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]


def initialize_facebook_client():
    """Initialize Facebook client from environment variables."""
    global fb_client

    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    page_id = os.getenv('FACEBOOK_PAGE_ID')
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')

    if not access_token:
        logger.error('FACEBOOK_ACCESS_TOKEN not set')
        logger.info('Please set Facebook environment variables:')
        logger.info('  - FACEBOOK_APP_ID')
        logger.info('  - FACEBOOK_APP_SECRET')
        logger.info('  - FACEBOOK_ACCESS_TOKEN')
        logger.info('  - FACEBOOK_PAGE_ID (optional, for business pages)')
        return False

    logger.info(f'Initializing Facebook client')
    if page_id:
        logger.info(f'Using Page ID: {page_id}')

    fb_client = FacebookGraphClient(access_token, page_id)
    return True


async def main():
    """Run the MCP server."""
    # Initialize Facebook client
    if not initialize_facebook_client():
        logger.error('Failed to initialize Facebook client')
        logger.info('Server will start but Facebook tools will not work')
        # Create a dummy client to prevent crashes
        fb_client = None

    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == '__main__':
    asyncio.run(main())
