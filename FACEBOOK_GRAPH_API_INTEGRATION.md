# Facebook Graph API Integration - Summary

## ✅ What Changed

Facebook integration has been **upgraded from Playwright (browser automation) to Facebook Graph API** (official API).

---

## 🎯 Benefits of Graph API

| Feature | Playwright (Old) | Graph API (New) |
|---------|------------------|-----------------|
| **Reliability** | ❌ Breaks with UI changes | ✅ Stable API |
| **Speed** | ⚠️ Slow (browser) | ✅ Fast (HTTP) |
| **Features** | ⚠️ Limited to UI | ✅ Full API access |
| **Rate Limiting** | ❌ None (can be blocked) | ✅ Protected |
| **Official Support** | ❌ No | ✅ Yes |
| **Authentication** | ⚠️ Session cookies | ✅ OAuth tokens |
| **Maintenance** | ⚠️ High | ✅ Low |

---

## 📁 New Files Created

```
D:\FTE_AI_Employee\
├── facebook-mcp-server/
│   ├── facebook_mcp_server.py      # MCP server using Graph API
│   ├── requirements.txt            # Python dependencies
│   ├── README.md                   # Setup guide
│   └── start-facebook-mcp.bat      # Launcher script
│
└── watchers/
    └── facebook_watcher_api.py     # Watcher using Graph API
```

---

## 🚀 Quick Start

### Step 1: Get Facebook Access Token

1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app (or create one)
3. Click **Get Token** → **Get User Access Token**
4. Select permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_read_user_content`
5. Click **Generate Token** and copy it

### Step 2: Set Environment Variables

```bash
set FACEBOOK_ACCESS_TOKEN=your_token_here
set FACEBOOK_PAGE_ID=your_page_id_here (optional)
```

Or add to `.env` file:
```bash
FACEBOOK_ACCESS_TOKEN=EAABwzLixnjYBO...
FACEBOOK_PAGE_ID=123456789012345
```

### Step 3: Install Dependencies

```bash
cd facebook-mcp-server
pip install -r requirements.txt
```

### Step 4: Start Facebook MCP Server

```bash
# Option 1: Use batch file
start-facebook-mcp.bat

# Option 2: Run directly
python facebook_mcp_server.py
```

### Step 5: Test Connection

```bash
python ..\.qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8809 ^
  -t facebook_connect ^
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

### Step 6: Start Facebook Watcher

```bash
python watchers\facebook_watcher_api.py
```

---

## 📊 Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| `facebook_connect` | Test connection | `{}` |
| `facebook_get_profile` | Get profile info | `{}` |
| `facebook_post` | Create post | `{"message": "Hello!"}` |
| `facebook_post_photo` | Post photo | `{"message": "Pic", "photo_url": "..."}` |
| `facebook_get_notifications` | Get notifications | `{"limit": 10}` |
| `facebook_get_messages` | Get messages | `{"limit": 10}` |
| `facebook_get_posts` | Get recent posts | `{"limit": 10}` |
| `facebook_get_insights` | Get analytics | `{"metrics": [...]}` |
| `facebook_send_message` | Send message | `{"recipient_id": "...", "message": "..."}` |

---

## 🔄 Integration with Orchestrator

The orchestrator automatically uses Facebook MCP when:

1. Facebook watcher creates action file in `Needs_Action/`
2. User moves file to `/Approved` folder
3. Orchestrator executes `facebook_post` tool
4. Post is published
5. Result logged to `Logs/facebook_posts.md`

---

## 📝 Example Workflow

### Post to Facebook via Approval

**1. Create approval file:**

```markdown
---
type: approval_request
action: facebook_post
created: 2026-03-06T15:00:00
priority: normal
---

## Post Content
🎉 Exciting news! We just launched our new product line.
Check it out at our website!

## Link
https://example.com/product

## To Approve
Move to /Approved folder
```

**2. Move to Approved folder**

**3. Orchestrator posts automatically**

**4. Check result:**
```
Logs/facebook_posts.md
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
FACEBOOK_ACCESS_TOKEN=your_access_token

# Optional (for business pages)
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_PAGE_ID=your_page_id
```

### MCP Server Port

Facebook MCP server runs on **port 8809** (different from Playwright MCP on 8808).

---

## 🛠️ Troubleshooting

### "Invalid Access Token"

**Solution:**
1. Check token: https://developers.facebook.com/tools/debug/access_token/
2. Generate new token if expired
3. Verify environment variable is set

### "Permissions Error"

**Solution:**
1. Go to App Review → Permissions
2. Ensure required permissions are granted
3. For development, add your account as app admin

### "MCP Server Won't Start"

**Solution:**
```bash
# Check dependencies
pip install mcp httpx python-dotenv

# Check port
netstat -an | findstr 8809

# Run manually
python facebook_mcp_server.py
```

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `facebook-mcp-server/README.md` | Complete setup guide |
| `facebook-mcp-server/` | MCP server directory |
| `.qwen/skills/GOLD_TIER_SKILLS.md` | Skills reference |
| `GOLD_TIER_README.md` | Gold Tier overview |

---

## ✅ Migration Checklist

If you were using the old Playwright-based Facebook integration:

- [ ] Remove old Facebook watcher code
- [ ] Set up Facebook Developer App
- [ ] Get access token
- [ ] Install new dependencies
- [ ] Start new MCP server
- [ ] Test with `facebook_connect`
- [ ] Update orchestrator config (if needed)
- [ ] Test posting workflow

---

## 🎯 Next Steps

1. ✅ Set up Facebook app and get token
2. ✅ Install dependencies
3. ✅ Start MCP server
4. ✅ Test connection
5. ✅ Start watcher
6. ✅ Create first post

---

## 🔗 Resources

- **Graph API Docs**: https://developers.facebook.com/docs/graph-api
- **API Explorer**: https://developers.facebook.com/tools/explorer/
- **Access Token Debug**: https://developers.facebook.com/tools/debug/access_token/
- **App Dashboard**: https://developers.facebook.com/apps/

---

*Facebook Graph API Integration - Gold Tier AI Employee*
