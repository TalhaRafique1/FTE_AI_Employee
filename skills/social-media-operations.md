---
name: social-media-operations
description: |
  Social media operations for the AI Employee.
  Create, schedule, and post content on LinkedIn for business growth.
  Includes approval workflow for all public posts.
---

# Social Media Operations Agent Skill (Silver Tier)

This skill enables the AI Employee to manage social media presence, specifically LinkedIn for business growth.

## Overview

The Social Media Operations skill provides:
- Create business update posts
- Schedule posts for optimal times
- Auto-generate content from business activities
- Approval workflow for all posts
- Track engagement metrics

## Platform Support

| Platform | Status | Use Case |
|----------|--------|----------|
| LinkedIn | ✅ Silver Tier | Business updates, lead generation |
| Twitter/X | ⏳ Gold Tier | Quick updates, engagement |
| Facebook | ⏳ Gold Tier | Business page management |
| Instagram | ⏳ Gold Tier | Visual content |

## Prerequisites

### LinkedIn MCP Setup

1. **Install LinkedIn MCP (or use Browser MCP):**
   ```bash
   # Option 1: Dedicated LinkedIn MCP (if available)
   npm install -g linkedin-mcp
   
   # Option 2: Use Browser MCP with Playwright
   npx @playwright/mcp@latest
   ```

2. **Configure LinkedIn Authentication:**
   - Use browser session for LinkedIn
   - Store session securely
   - Never commit credentials

## Usage Patterns

### Create Post (Draft)

```markdown
# /Vault/Social/DRAFT_linkedin_2026-02-25.md
---
type: social_post_draft
platform: linkedin
created: 2026-02-25T09:00:00Z
status: draft
scheduled: 2026-02-26T09:00:00Z
---

## Post Content

🚀 Exciting News!

We're thrilled to announce the launch of our AI Employee service! 

This autonomous agent helps businesses automate routine tasks, manage communications, and focus on what matters most.

Key features:
✅ 24/7 operation
✅ Email & WhatsApp integration
✅ Human-in-the-loop approvals
✅ Local-first privacy

Learn more: [Your Website]

#AIEmployee #Automation #BusinessGrowth #Innovation

## Media
- Image: /Vault/Social/images/launch_announcement.png

## Posting Notes
- Best time: Tuesday 9:00 AM
- Target audience: Business owners, entrepreneurs
- Expected reach: 500-1000 impressions

## To Approve
Move to /Pending_Approval for review before scheduling
```

### Schedule Post (Requires Approval)

```markdown
# /Pending_Approval/SOCIAL_linkedin_post_2026-02-25.md
---
type: approval_request
action: schedule_social_post
platform: linkedin
scheduled_time: 2026-02-26T09:00:00Z
created: 2026-02-25T10:00:00Z
expires: 2026-02-26T08:00:00Z
priority: normal
status: pending
---

## Post Details
- **Platform:** LinkedIn
- **Scheduled:** Feb 26, 2026 at 9:00 AM
- **Type:** Business Update

## Content Preview
🚀 Exciting News!

We're thrilled to announce the launch of our AI Employee service!
...

## Media Attached
- launch_announcement.png (1200x627px)

## Why Approval Required
All public posts require human review before publishing

## To Approve
Move to `/Approved` - Post will be scheduled

## To Reject
Move to `/Rejected` - Add feedback in comments
```

### Auto-Generate from Business Activity

```markdown
# AI generates post from completed milestones

## Trigger
Task completed: "Project Alpha milestone 2 delivered"

## Generated Post

📍 Milestone Achieved!

Just completed Milestone 2 of Project Alpha! 

Our team delivered:
✅ Feature X implementation
✅ Integration with client systems
✅ User training sessions

Next up: Final testing and deployment

#ProjectManagement #Milestone #Delivery

## Action
Created draft in /Vault/Social/DRAFT_milestone_alpha_2026-02-25.md
```

## Post Templates

### Business Update Template

```markdown
📢 Business Update

[Headline about your business news]

Key points:
• [Point 1]
• [Point 2]
• [Point 3]

[Call to action or link]

#BusinessUpdate #[YourIndustry] #Growth
```

### Achievement Template

```markdown
🏆 Achievement Unlocked!

[Celebrate a milestone or achievement]

What this means:
• [Impact 1]
• [Impact 2]

Thank you to [team/clients/partners]!

#Achievement #Milestone #Success
```

### Educational Content Template

```markdown
💡 Quick Tip: [Topic]

[Share valuable insight or tip]

Why it matters:
[Brief explanation]

Try it and let me know how it goes!

#Tips #[Topic] #Learning
```

### Lead Generation Template

```markdown
🤔 Are you struggling with [common problem]?

Many [target audience] face this challenge:
• [Pain point 1]
• [Pain point 2]
• [Pain point 3]

Good news: There's a better way.

[Your solution] helps you:
✅ [Benefit 1]
✅ [Benefit 2]
✅ [Benefit 3]

Comment "INFO" or DM me to learn more!

#ProblemSolving #Business #Solution
```

## Content Calendar

```markdown
# /Vault/Social/content_calendar_2026-02.md

## February 2026

| Date | Type | Topic | Status | Posted |
|------|------|-------|--------|--------|
| Feb 25 | Business Update | AI Employee Launch | ✅ Approved | ⏳ Scheduled |
| Feb 26 | Educational | Automation Tips | 📝 Draft | - |
| Feb 27 | Achievement | Client Milestone | 📝 Draft | - |
| Feb 28 | Lead Gen | Problem/Solution | 📝 Draft | - |

## Posting Schedule
- **Best times:** Tue-Thu 9:00 AM, 12:00 PM
- **Frequency:** 3-4 posts per week
- **Mix:** 40% educational, 30% business, 20% social proof, 10% promotional
```

## Approval Workflow

### All Posts Require Approval

```
┌─────────────────────────────────────────────────────────┐
│                    Post Creation                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Draft Created in /Vault/Social/            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Move to /Pending_Approval/ for Review           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │  Human Review  │
            └───────┬────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
   Approve                  Reject
        │                       │
        ▼                       ▼
   /Approved/              /Rejected/
        │                       │
        ▼                       ▼
   Schedule Post          Add Feedback
```

## Browser MCP Integration (Playwright)

```python
# Post to LinkedIn using Playwright MCP

async def post_to_linkedin(content: str, image_path: str = None):
    """Post content to LinkedIn using browser automation."""
    
    code = f'''
    async (page) => {{
        // Navigate to LinkedIn
        await page.goto('https://www.linkedin.com/feed/');
        
        // Wait for post composer
        await page.waitForSelector('[aria-label="Start a post"]');
        await page.click('[aria-label="Start a post"]');
        
        // Wait for editor
        await page.waitForSelector('[role="textbox"]');
        await page.fill('[role="textbox"]', `{content}`);
        
        // Add image if provided
        {"await page.click('[data-id="media-upload"]'); await page.setInputFiles('input[type=\\"file\\"]", `' + image_path + '`);"}
        
        // Post
        await page.click('button:has-text("Post")');
        
        // Wait for confirmation
        await page.waitForSelector('text="Your post has been shared"');
        
        return {{ success: true }};
    }}
    '''
    
    result = await browser_mcp.evaluate(code)
    return result
```

## Engagement Tracking

```markdown
# /Vault/Social/engagement_log.md

## 2026-02 Posts

| Date | Post | Impressions | Likes | Comments | Shares | CTR |
|------|------|-------------|-------|----------|--------|-----|
| Feb 25 | AI Employee Launch | 1,234 | 45 | 12 | 8 | 3.2% |
| Feb 26 | Automation Tips | 892 | 32 | 8 | 5 | 2.1% |

## Insights
- Best performing: Business updates (avg 1000+ impressions)
- Best time: Tuesday 9:00 AM
- Top hashtags: #Automation #BusinessGrowth

## Actions
- Increase business update frequency
- Test video content
- Engage more with comments
```

## Response Handling

```markdown
# When someone comments on a post:

## Process
1. Notification received (via watcher or manual check)
2. Create action file in /Needs_Action/
3. AI drafts response
4. Human approves response
5. Response posted

## Response Templates

### Thank You
```
Thank you for your interest! Feel free to DM me if you'd like to learn more.
```

### Question Response
```
Great question! [Brief answer]. I'd be happy to discuss further - sending you a DM!
```

### Lead Capture
```
Thanks for commenting! I've sent you a connection request and will follow up with details.
```
```

## Best Practices

1. **Always approve before posting** - Never auto-publish
2. **Maintain brand voice** - Professional, helpful, authentic
3. **Engage with comments** - Respond within 24 hours
4. **Track metrics** - Review engagement weekly
5. **Mix content types** - Educational, promotional, social proof
6. **Use visuals** - Posts with images get 2x engagement
7. **Optimal timing** - Post when audience is active
8. **Hashtag strategy** - 3-5 relevant hashtags per post

## Security Considerations

1. **Never auto-post** - Always require approval
2. **Secure session** - Store LinkedIn session securely
3. **Rate limiting** - Max 3 posts per day
4. **Monitor for issues** - Check for negative responses
5. **Backup content** - Keep copies of all posts

## Troubleshooting

| Issue | Solution |
|-------|----------|
| LinkedIn session expired | Re-authenticate via browser |
| Post not publishing | Check content length (<3000 chars) |
| Image upload failing | Verify image format (PNG/JPG) |
| Rate limited | Wait 24 hours before next post |

---

*Version: 0.2 (Silver Tier)*
*Last Updated: 2026-02-25*
