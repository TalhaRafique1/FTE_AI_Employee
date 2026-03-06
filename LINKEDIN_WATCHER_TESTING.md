# LinkedIn Watcher - Testing Guide

## Prerequisites Check

```bash
# 1. Verify Python files compile
python -m py_compile watchers\linkedin_watcher.py

# 2. Verify MCP client exists
dir .qwen\skills\browsing-with-playwright\scripts\mcp-client.py

# 3. Verify npx is available
where npx
```

## Step-by-Step Testing

### Step 1: Start Playwright MCP Server

Open **Terminal 1**:

```bash
cd D:\FTE_AI_Employee

# Start MCP server on port 8808
npx @playwright/mcp@latest --port 8808 --shared-browser-context
```

**Expected Output:**
```
Playwright MCP server started on port 8808
Browser context initialized
Waiting for connections...
```

**Keep this terminal running!**

### Step 2: Run LinkedIn Watcher

Open **Terminal 2**:

```bash
cd D:\FTE_AI_Employee

# Run LinkedIn watcher
python watchers\linkedin_watcher.py
```

**Expected Output:**
```
============================================================
LINKEDIN WATCHER - Silver Tier
============================================================
Vault: D:\FTE_AI_Employee\AI_Employee_Vault
Check interval: 300 seconds (5 minutes)
Monitoring LinkedIn for notifications and messages...
Press Ctrl+C to stop
============================================================

2026-02-26 14:00:00 - LinkedInWatcher - INFO - Starting LinkedInWatcher
2026-02-26 14:00:00 - LinkedInWatcher - INFO - Session path: C:\Users\...\linkedin_session
2026-02-26 14:00:00 - LinkedInWatcher - INFO - Starting Playwright MCP server...
```

### Step 3: First-Time Login (Manual)

**A browser window will open:**

1. **If you see LinkedIn homepage:**
   - Click "Sign in"
   - Enter your LinkedIn email and password
   - Complete any 2FA if enabled
   - Navigate to https://www.linkedin.com/feed/
   - The session will be saved automatically

2. **If browser doesn't open:**
   - The watcher uses persistent browser context
   - You may need to manually open Chrome/Edge
   - Navigate to LinkedIn and sign in
   - The session cookies will be saved

3. **After successful login:**
   - Browser stays open (for future auto-login)
   - Session saved to `~/.ai_employee/linkedin_session`
   - Watcher continues monitoring

### Step 4: Verify Monitoring Works

**In Terminal 2, you should see:**

```
2026-02-26 14:00:30 - LinkedInWatcher - INFO - MCP server started
2026-02-26 14:00:33 - LinkedInWatcher - INFO - Already logged in to LinkedIn
2026-02-26 14:00:35 - LinkedInWatcher - INFO - Checking notifications...
```

### Step 5: Check for Action Files

After the watcher runs, check for created files:

```bash
dir AI_Employee_Vault\Needs_Action\LINKEDIN_*.md
```

If notifications were found, you'll see files like:
```
LINKEDIN_comment_john_doe_20260226_140000.md
LINKEDIN_like_jane_smith_20260226_140000.md
LINKEDIN_connection_bob_wilson_20260226_140000.md
```

### Step 6: View Created Action File

```bash
type AI_Employee_Vault\Needs_Action\LINKEDIN_*.md
```

**Example content:**
```markdown
---
type: linkedin_notification
notification_type: "comment"
actor: "John Doe"
received: 2026-02-26T14:00:00
priority: "high"
---

# LinkedIn Notification for Processing

## Notification Details
- **Type:** Comment
- **From:** John Doe
- **Priority:** High
- **Business Related:** Yes 💼

## Content
John Doe commented on your post...

## Suggested Actions
- [ ] Review comment on post
- [ ] Engage with commenter
- [ ] 💼 POTENTIAL LEAD - Prioritize response
```

## Troubleshooting

### Issue: MCP Server Won't Start

```bash
# Try installing Playwright
npx playwright install

# Then start MCP server again
npx @playwright/mcp@latest --port 8808 --shared-browser-context
```

### Issue: Browser Doesn't Open

The LinkedIn Watcher uses persistent browser context. Try:

1. **Manual login first:**
   ```bash
   # Open browser manually
   # Go to https://linkedin.com
   # Sign in
   # Close browser
   ```

2. **Then run watcher:**
   ```bash
   python watchers\linkedin_watcher.py
   ```

### Issue: "Not Logged In" Error

```bash
# Delete session and re-authenticate
rmdir /s /q "%USERPROFILE%\.ai_employee\linkedin_session"

# Run watcher again
python watchers\linkedin_watcher.py
```

### Issue: No Notifications Found

This is normal if:
- You have no new LinkedIn activity
- Notifications are already processed
- LinkedIn changed their UI (parser needs update)

**To test, you can:**
1. Post something on LinkedIn
2. Ask a connection to like/comment
3. Run watcher again

## Quick Test Command

Run this to test MCP connection:

```bash
cd D:\FTE_AI_Employee

# Test MCP server connection (in Terminal 1, MCP server should be running)
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8808 ^
  -t browser_navigate ^
  -p '{"url": "https://www.linkedin.com"}'
```

**Expected:** Browser opens and navigates to LinkedIn

## Session Management

### View Saved Session

```bash
dir "%USERPROFILE%\.ai_employee\linkedin_session"
```

### Clear Session (Force Re-login)

```bash
rmdir /s /q "%USERPROFILE%\.ai_employee\linkedin_session"
```

### Check Processed Notifications

```bash
type AI_Employee_Vault\.processed_linkedin.json
```

## Integration with Orchestrator

Once LinkedIn Watcher creates action files, the orchestrator processes them:

```bash
# Run orchestrator to process LinkedIn notifications
python orchestrator.py
```

The orchestrator will:
1. Read LinkedIn action files
2. Create plans for responses
3. Draft reply messages
4. Request approval for actions
5. Update dashboard

## Complete Workflow Example

```
1. Someone comments on your LinkedIn post
   ↓
2. LinkedIn Watcher detects notification (every 5 min)
   ↓
3. Creates: Needs_Action/LINKEDIN_comment_*.md
   ↓
4. Orchestrator runs (every 60 sec)
   ↓
5. Qwen Code reads action file
   ↓
6. Creates plan: Plans/PLAN_respond_to_comment_*.md
   ↓
7. Drafts response in action file
   ↓
8. Creates approval: Pending_Approval/LINKEDIN_response_*.md
   ↓
9. Human reviews and approves (moves to Approved/)
   ↓
10. Orchestrator posts response via MCP
   ↓
11. Logs action, moves to Done/
```

## Performance Notes

| Setting | Default | Can Change |
|---------|---------|------------|
| Check Interval | 300s (5 min) | Yes, in code |
| Max Notifications/Check | 5 | Yes, in code |
| Session Persistence | Yes | N/A |
| Auto-login | Yes (after first) | N/A |

## Next Steps

After testing:

1. **Add to startup** (for continuous monitoring):
   ```bash
   # Windows Task Scheduler
   # Create task to run linkedin_watcher.py at login
   ```

2. **Configure notifications** (email/desktop alerts)

3. **Set up LinkedIn posting** approval workflow

4. **Integrate with CRM** (track leads from LinkedIn)

---

*For more details, see:*
- `skills/linkedin-posting.md` - Posting guide
- `skills/social-media-operations.md` - Social media operations
- `SILVER_TIER_README.md` - Complete Silver Tier documentation
