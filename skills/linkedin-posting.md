---
name: linkedin-posting
description: |
  LinkedIn posting skill using Playwright MCP.
  Create, schedule, and publish posts on LinkedIn for business growth.
  Includes approval workflow for all posts before publishing.
---

# LinkedIn Posting Agent Skill (Silver Tier)

This skill enables the AI Employee to post content on LinkedIn using Playwright MCP for browser automation.

## Overview

The LinkedIn Posting skill provides:
- Create business update posts
- Publish posts directly via browser automation
- Schedule posts for optimal times
- Approval workflow for all posts
- Track engagement metrics

## Prerequisites

### Playwright MCP Setup

```bash
# Install Playwright MCP
npx @playwright/mcp@latest --port 8808 --shared-browser-context

# Or use the helper scripts
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
```

### LinkedIn Authentication

LinkedIn session is managed via persistent browser context:
- First login is manual
- Session saved in `~/.ai_employee/linkedin_session`
- Subsequent runs auto-login

## Usage Patterns

### Post to LinkedIn (Direct)

```bash
# Start MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Post content
python3 .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 \
  -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://linkedin.com/feed\"); await page.click(\"[aria-label=\\\"Start a post\\\"]\"); await page.fill(\"[role=\\\"textbox\\\"]\", \"Your post content here\"); await page.click(\"button:has-text(\\\"Post\\\")\"); }"}'
```

### Create Post Draft (For Approval)

```markdown
# /Vault/Social/DRAFT_linkedin_post_2026-02-25.md
---
type: linkedin_post_draft
created: 2026-02-25T09:00:00Z
status: draft
scheduled: 2026-02-26T09:00:00Z
---

## Post Content

🚀 Exciting News!

We're thrilled to announce the launch of our AI Employee service!

Key features:
✅ 24/7 operation
✅ Email & WhatsApp integration
✅ Human-in-the-loop approvals

#AIEmployee #Automation #BusinessGrowth

## Media
- Image: /Vault/Social/images/launch_announcement.png

## To Approve
Move to /Pending_Approval/ for review before posting
```

### Execute LinkedIn Post (After Approval)

```markdown
# /Approved/LINKEDIN_post_2026-02-25.md
---
type: approval_request
action: linkedin_post
content: "🚀 Exciting News!..."
media_path: "/Vault/Social/images/launch_announcement.png"
scheduled_time: 2026-02-26T09:00:00Z
created: 2026-02-25T10:00:00Z
approved: 2026-02-25T14:00:00Z
status: approved
---

## Post Details
- **Platform:** LinkedIn
- **Content:** See above
- **Media:** Attached
- **Scheduled:** Feb 26, 2026 at 9:00 AM

## Execution
Post will be published via Playwright MCP when this file is in /Approved/
```

## Playwright MCP Functions

### Navigate to LinkedIn Feed

```python
# Navigate to LinkedIn
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_navigate \
  -p '{"url": "https://www.linkedin.com/feed/"}'
```

### Get Page Snapshot

```python
# Get accessibility snapshot
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_snapshot \
  -p '{}'
```

### Click "Start a Post"

```python
# Click the post composer button
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_click \
  -p '{"element": "Start a post button", "ref": "e42"}'
```

### Fill Post Content

```python
# Fill the post text area
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_type \
  -p '{"element": "Post text area", "ref": "e45", "text": "Your post content here", "submit": false}'
```

### Add Media (Optional)

```python
# Upload image
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_file_upload \
  -p '{"paths": ["/path/to/image.png"]}'
```

### Click Post Button

```python
# Publish the post
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_click \
  -p '{"element": "Post button", "ref": "e50"}'
```

### Take Screenshot (Verification)

```python
# Capture confirmation
python3 scripts/mcp-client.py call -u http://localhost:8808 \
  -t browser_take_screenshot \
  -p '{"type": "png", "filename": "linkedin_post_confirmation.png"}'
```

## Complete Posting Workflow

```python
# linkedin_post_helper.py

import subprocess
import json
import time

MCP_URL = "http://localhost:8808"

def mcp_call(tool: str, params: dict) -> dict:
    """Make MCP server call."""
    result = subprocess.run(
        ['python3', 'scripts/mcp-client.py', 'call',
         '-u', MCP_URL, '-t', tool, '-p', json.dumps(params)],
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.returncode == 0 else None

def post_to_linkedin(content: str, image_path: str = None):
    """Post content to LinkedIn."""
    
    # 1. Navigate to LinkedIn
    print("Navigating to LinkedIn...")
    mcp_call('browser_navigate', {'url': 'https://www.linkedin.com/feed/'})
    time.sleep(3)
    
    # 2. Click "Start a post"
    print("Opening post composer...")
    snapshot = mcp_call('browser_snapshot', {})
    # Find the post button ref from snapshot
    mcp_call('browser_click', {'element': 'Start a post', 'ref': 'e42'})
    time.sleep(2)
    
    # 3. Fill content
    print("Filling post content...")
    mcp_call('browser_type', {
        'element': 'Post text area',
        'ref': 'e45',
        'text': content,
        'submit': False
    })
    time.sleep(1)
    
    # 4. Add image if provided
    if image_path:
        print("Uploading image...")
        mcp_call('browser_file_upload', {'paths': [image_path]})
        time.sleep(2)
    
    # 5. Click Post
    print("Publishing post...")
    mcp_call('browser_click', {'element': 'Post button', 'ref': 'e50'})
    time.sleep(3)
    
    # 6. Take screenshot
    print("Capturing confirmation...")
    mcp_call('browser_take_screenshot', {
        'type': 'png',
        'filename': 'linkedin_post_confirmation.png'
    })
    
    print("Post published successfully!")
    return True

# Usage
post_to_linkedin(
    content="🚀 Exciting announcement! Our AI Employee service is now live...",
    image_path="/path/to/image.png"
)
```

## Post Templates

### Business Update

```
📢 Business Update

[Headline about your business news]

Key points:
• [Point 1]
• [Point 2]
• [Point 3]

[Call to action or link]

#BusinessUpdate #Industry #Growth
```

### Achievement/Milestone

```
🏆 Achievement Unlocked!

[Celebrate a milestone]

What this means:
• [Impact 1]
• [Impact 2]

Thank you to [team/clients/partners]!

#Achievement #Milestone #Success
```

### Educational Content

```
💡 Quick Tip: [Topic]

[Share valuable insight]

Why it matters:
[Brief explanation]

Try it and let me know how it goes!

#Tips #Learning #ProfessionalDevelopment
```

### Lead Generation

```
🤔 Are you struggling with [problem]?

Many [audience] face this:
• [Pain point 1]
• [Pain point 2]

Good news: There's a better way.

[Your solution] helps you:
✅ [Benefit 1]
✅ [Benefit 2]

Comment "INFO" or DM me to learn more!

#ProblemSolving #Business #Solution
```

## Approval Workflow

```
┌─────────────────────────────────────────────────────────┐
│              Create Post Draft                          │
│         /Vault/Social/DRAFT_linkedin_*.md               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Move to /Pending_Approval/                      │
│    Human reviews content, timing, media                 │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   Approve                    Reject
        │                         │
        ▼                         ▼
   /Approved/                /Rejected/
        │                         │
        ▼                         ▼
┌──────────────────┐      Add Feedback
│ Orchestrator     │
│ executes via MCP │
│ Posts to LinkedIn│
└──────────────────┘
```

## Logging

```markdown
# /Vault/Logs/linkedin_posts.md

## 2026-02 Posts

| Date | Content | Status | Engagement |
|------|---------|--------|------------|
| Feb 25 | AI Employee Launch | ✅ Posted | 45 likes, 12 comments |
| Feb 26 | Automation Tips | ✅ Posted | 32 likes, 8 comments |

## Metrics
- Total posts: 2
- Total impressions: 2,126
- Total engagements: 97
- CTR: 3.2%
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login required | Manual login needed first time |
| Post button not found | Refresh snapshot, get new ref |
| Image upload fails | Check file path and format |
| Rate limited | Wait 24 hours between posts |
| Session expired | Re-authenticate via browser |

## Best Practices

1. **Always use approval workflow** - Never auto-publish
2. **Optimal timing** - Post Tue-Thu 9-11 AM
3. **Use visuals** - Images get 2x engagement
4. **Engage with comments** - Respond within 24 hours
5. **Track metrics** - Review performance weekly
6. **Mix content types** - Educational, promotional, social proof

---

*Version: 0.2 (Silver Tier)*
*Last Updated: 2026-02-25*
