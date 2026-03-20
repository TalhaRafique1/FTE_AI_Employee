# Facebook Graph API Integration Guide

## Overview

This guide shows you how to set up Facebook Graph API integration for your AI Employee to:
- Post to Facebook automatically
- Monitor notifications
- Read messages
- Get page insights

---

## Prerequisites

- Facebook Developer Account
- Facebook Page (for business integration)
- Python 3.11+

---

## Step 1: Create Facebook App

### 1.1 Go to Facebook Developers

1. Visit: https://developers.facebook.com/
2. Click **My Apps** → **Create App**

### 1.2 Select App Type

Choose **Business** app type (recommended for pages) or **Other** → **Business**

### 1.3 Fill App Details

- **App Name**: AI Employee Facebook Integration
- **App Contact Email**: your-email@example.com
- Click **Create App**

---

## Step 2: Configure App Permissions

### 2.1 Add Facebook Login Product

1. In your app dashboard, click **Add Product**
2. Find **Facebook Login** and click **Set Up**
3. Select **Web** as the platform
4. Set Site URL: `https://localhost`

### 2.2 Configure Permissions

Go to **App Review** → **Permissions and Features**

Request these permissions:
- `pages_manage_posts` - Create posts on pages
- `pages_read_engagement` - Read page engagement
- `pages_read_user_content` - Read page content
- `publish_to_groups` - Post to groups
- `user_posts` - Read user posts
- `user_friends` - Access friend list

### 2.3 Submit for Review

For production use, submit your app for Facebook review.

**For development/testing**, you can use the app without review but only admin accounts can access it.

---

## Step 3: Get Access Tokens

### 3.1 Get User Access Token

1. Go to **Graph API Explorer**: https://developers.facebook.com/tools/explorer/
2. Select your app from dropdown
3. Click **Get Token** → **Get User Access Token**
4. Select permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `user_posts`
5. Click **Generate Token**
6. Complete login and grant permissions
7. Copy the access token

### 3.2 Get Page Access Token (Recommended)

For business pages, use a page access token:

1. In Graph API Explorer, run this query:
   ```
   GET /me/accounts
   ```
2. Find your page in the results
3. Copy the `access_token` value
4. This token doesn't expire (if you have `manage_pages` permission)

### 3.3 Get Page ID

From the same `/me/accounts` response, copy your page's `id`.

---

## Step 4: Configure Environment Variables

Create or edit `.env` file in project root:

```bash
# Facebook Graph API Configuration
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here
```

**Example:**
```bash
FACEBOOK_APP_ID=123456789012345
FACEBOOK_APP_SECRET=abc123def456...
FACEBOOK_ACCESS_TOKEN=EAABwzLixnjYBO...
FACEBOOK_PAGE_ID=987654321098765
```

---

## Step 5: Install Dependencies

```bash
cd D:\FTE_AI_Employee\facebook-mcp-server
pip install -r requirements.txt
```

---

## Step 6: Test Connection

### Test Facebook MCP Server

```bash
# Start MCP server
cd D:\FTE_AI_Employee\facebook-mcp-server
python facebook_mcp_server.py
```

### Test with MCP Client

In another terminal:

```bash
cd D:\FTE_AI_Employee
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call \
  -u http://localhost:8809 \
  -t facebook_connect \
  -p '{}'
```

Expected response:
```json
{
  "success": true,
  "profile": {
    "id": "123456789",
    "name": "Your Page Name"
  }
}
```

---

## Step 7: Start Facebook Watcher

```bash
python watchers\facebook_watcher_api.py
```

The watcher will:
- Check for new notifications every 5 minutes
- Create action files in `Needs_Action/`
- Flag urgent messages

---

## Usage Examples

### Post to Facebook

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call \
  -u http://localhost:8809 \
  -t facebook_post \
  -p '{"message": "Hello from AI Employee! 🤖"}'
```

### Post with Link

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call \
  -u http://localhost:8809 \
  -t facebook_post \
  -p '{"message": "Check out our latest product!", "link": "https://example.com"}'
```

### Post Photo

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call \
  -u http://localhost:8809 \
  -t facebook_post_photo \
  -p '{"message": "New product launch!", "photo_url": "https://example.com/image.jpg"}'
```

### Get Notifications

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call \
  -u http://localhost:8809 \
  -t facebook_get_notifications \
  -p '{"limit": 10}'
```

### Get Page Insights

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call \
  -u http://localhost:8809 \
  -t facebook_get_insights \
  -p '{"metrics": ["page_impressions_unique", "page_engaged_users"], "period": "week"}'
```

---

## Integration with Orchestrator

The orchestrator automatically uses Facebook MCP when:
1. Facebook watcher creates action file
2. File is moved to `/Approved`
3. Orchestrator executes the post

Example workflow:

```
1. Create approval file in Needs_Action/
2. Move to Approved/ folder
3. Orchestrator calls facebook_post tool
4. Post is published
5. Result logged to facebook_posts.md
```

---

## Token Management

### Token Expiration

- **User tokens**: ~60 days (can be extended)
- **Page tokens**: Don't expire (with proper permissions)

### Extend User Token

1. Go to Graph API Explorer
2. Run: `GET /oauth/access_token`
   ```
   ?grant_type=fb_exchange_token
   &client_id={app-id}
   &client_secret={app-secret}
   &fb_exchange_token={existing-access-token}
   ```

### Refresh Tokens

Set a reminder to refresh tokens monthly, or use page tokens which don't expire.

---

## Troubleshooting

### "Invalid Access Token"

**Solution:**
1. Check token in Graph API Explorer: https://developers.facebook.com/tools/debug/access_token/
2. Generate new token if expired
3. Verify environment variables are set

### "Permissions Error"

**Solution:**
1. Go to App Review → Permissions
2. Ensure required permissions are approved
3. For development, add your account as app admin

### "Page Not Found"

**Solution:**
1. Verify PAGE_ID is correct
2. Ensure you have admin access to the page
3. Use page access token, not user token

### MCP Server Won't Start

**Solution:**
```bash
# Check if port is available
netstat -an | findstr 8809

# Install dependencies
pip install mcp httpx python-dotenv

# Test manually
python facebook_mcp_server.py
```

---

## Security Best Practices

1. **Never commit tokens** to Git
2. **Use page tokens** for production (don't expire)
3. **Limit permissions** to what's needed
4. **Rotate tokens** regularly
5. **Use HTTPS** for all API calls
6. **Store tokens securely** (Windows Credential Manager)

---

## API Rate Limits

Facebook Graph API has rate limits:
- **200 calls per hour** per user/page
- Watcher uses ~12 calls/hour (every 5 min)
- Well within limits!

---

## Available Tools

| Tool | Description |
|------|-------------|
| `facebook_connect` | Test connection |
| `facebook_get_profile` | Get profile/page info |
| `facebook_post` | Create text post |
| `facebook_post_photo` | Post photo |
| `facebook_get_notifications` | Get notifications |
| `facebook_get_messages` | Get messages |
| `facebook_get_posts` | Get recent posts |
| `facebook_get_insights` | Get analytics |
| `facebook_send_message` | Send Messenger message |

---

## Next Steps

1. ✅ Set up Facebook app
2. ✅ Get access tokens
3. ✅ Configure environment variables
4. ✅ Test MCP server
5. ✅ Start Facebook watcher
6. ✅ Create first post via orchestrator

---

## Resources

- **Graph API Docs**: https://developers.facebook.com/docs/graph-api
- **API Explorer**: https://developers.facebook.com/tools/explorer/
- **Access Token Tool**: https://developers.facebook.com/tools/debug/access_token/
- **Rate Limits**: https://developers.facebook.com/docs/graph-api/overview/rate-limiting

---

*Facebook Graph API Integration - Gold Tier AI Employee*
