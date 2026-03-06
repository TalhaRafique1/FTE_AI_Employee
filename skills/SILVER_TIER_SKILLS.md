# Silver Tier Agent Skills - Overview

This document provides an overview of all Agent Skills required for the **Silver Tier** of the Personal AI Employee Hackathon.

## Silver Tier Requirements Recap

| # | Requirement | Skill(s) Used | Status |
|---|-------------|---------------|--------|
| 1 | All Bronze requirements | vault-operations | ✅ Complete |
| 2 | Two or more Watcher scripts | filesystem_watcher, gmail_watcher | ✅ Complete |
| 3 | Post on LinkedIn | social-media-operations | ✅ Complete |
| 4 | Plan.md reasoning loop | plan-creation | ✅ Complete |
| 5 | MCP server for external action | email-operations | ✅ Complete |
| 6 | Human-in-the-loop approval | approval-workflow | ✅ Complete |
| 7 | Basic scheduling | scheduling-operations | ✅ Complete |

## Agent Skills Inventory

### 1. Vault Operations (Bronze + Silver)

**File:** `skills/vault-operations.md`

**Purpose:** Core file system operations for the Obsidian vault.

**Capabilities:**
- Read pending items from `/Needs_Action`
- Create plans in `/Plans`
- Move completed tasks to `/Done`
- Create approval requests in `/Pending_Approval`
- Update Dashboard.md

**Usage:**
```bash
qwen -p "Process all files in Needs_Action and move completed items to Done"
```

---

### 2. Email Operations (Silver)

**File:** `skills/email-operations.md`

**Purpose:** Handle email communications via Gmail MCP.

**Capabilities:**
- Send emails to contacts
- Create draft emails for review
- Search and read emails
- Handle attachments
- Approval workflow for sensitive emails

**Prerequisites:**
- Gmail MCP server configured
- OAuth 2.0 credentials set up

**Usage:**
```bash
qwen -p "Send email to client@example.com with subject 'Meeting' and body 'Confirming our meeting tomorrow.'"
```

**Approval Required:**
- First-time contacts
- Financial matters (invoices, payments)
- Bulk emails (>5 recipients)

---

### 3. Approval Workflow (Silver)

**File:** `skills/approval-workflow.md`

**Purpose:** Human-in-the-loop pattern for sensitive actions.

**Capabilities:**
- Create approval requests
- Track pending approvals with expiration
- Execute approved actions automatically
- Maintain audit trail
- Handle rejections with feedback

**Folder Structure:**
```
/Vault/
├── Pending_Approval/
├── Approved/
├── Rejected/
└── Logs/approvals.md
```

**Usage:**
```markdown
# Create approval request in /Pending_Approval/
# Human moves to /Approved/ or /Rejected/
# Orchestrator executes approved actions
```

---

### 4. Social Media Operations (Silver)

**File:** `skills/social-media-operations.md`

**Purpose:** Manage LinkedIn presence for business growth.

**Capabilities:**
- Create business update posts
- Schedule posts for optimal times
- Auto-generate content from activities
- Approval workflow for all posts
- Track engagement metrics

**Prerequisites:**
- Browser MCP (Playwright) or LinkedIn MCP
- LinkedIn account authenticated

**Usage:**
```markdown
# Create draft in /Vault/Social/DRAFT_*.md
# Move to /Pending_Approval/ for review
# After approval, schedule via MCP
```

**Post Types:**
- Business updates
- Achievements/milestones
- Educational content
- Lead generation

---

### 5. Plan Creation (Silver)

**File:** `skills/plan-creation.md`

**Purpose:** Break down complex tasks into manageable steps.

**Capabilities:**
- Analyze task complexity
- Create structured Plan.md files
- Track progress with checkboxes
- Link related documents
- Update status as work progresses

**When to Create Plans:**
- 3+ steps required
- External dependencies
- Approval needed
- Time-sensitive deadlines

**Usage:**
```markdown
# /Plans/PLAN_task_description_2026-02-25.md
---
type: plan
status: in_progress
---

# Plan: [Task Description]

## Steps
- [ ] Step 1: [Action]
- [ ] Step 2: [Action]
- [ ] Step 3: [Action]
```

---

### 6. Scheduling Operations (Silver)

**File:** `skills/scheduling-operations.md`

**Purpose:** Handle time-based operations and calendar management.

**Capabilities:**
- Create calendar events
- Set reminders and alerts
- Schedule recurring tasks
- Generate daily/weekly briefings
- Cron/Task Scheduler integration

**Prerequisites:**
- Calendar MCP (optional)
- System scheduler access

**Usage:**
```bash
# Windows Task Scheduler
# Create task for daily briefing at 8 AM

# Linux/Mac cron
0 8 * * * python orchestrator.py --daily-briefing
```

**Scheduled Tasks:**
- Daily Briefing (8 AM)
- Weekly Review (Monday 9 AM)
- Hourly Quick Check

---

## Watcher Scripts

### Filesystem Watcher (Bronze + Silver)

**File:** `watchers/filesystem_watcher.py`

**Purpose:** Monitor drop folder for new files.

**Triggers:**
- New files in `/Inbox`
- Non-.md files only

**Output:**
- Creates action file in `/Needs_Action`
- Copies file to `/FileStorage`

---

### Gmail Watcher (Silver)

**File:** `watchers/gmail_watcher.py`

**Purpose:** Monitor Gmail for new unread/important emails.

**Triggers:**
- Unread emails
- Important标记 emails

**Output:**
- Creates action file in `/Needs_Action`
- Marks email as processed

**Prerequisites:**
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Watchers Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ Filesystem      │  │ Gmail           │                   │
│  │ Watcher         │  │ Watcher         │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
└───────────┼────────────────────┼────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   Needs_Action Folder                        │
│  - FILE_*.md (from filesystem)                               │
│  - EMAIL_*.md (from Gmail)                                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator                              │
│  - Triggers Qwen Code                                        │
│  - Routes to appropriate skill                               │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│ Vault           │ │ Plan        │ │ Approval        │
│ Operations      │ │ Creation    │ │ Workflow        │
└─────────────────┘ └─────────────┘ └────────┬────────┘
                                             │
                            ┌────────────────┼────────────────┐
                            │                │                │
                            ▼                ▼                ▼
                   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
                   │ Email       │ │ Social      │ │ Scheduling  │
                   │ Operations  │ │ Media       │ │ Operations  │
                   └─────────────┘ └─────────────┘ └─────────────┘
```

## Quick Start Guide

### 1. Setup Prerequisites

```bash
# Install Python dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Install Node.js dependencies (for MCP servers)
npm install -g @playwright/mcp

# Verify Qwen Code
qwen --version
```

### 2. Configure Credentials

```bash
# Gmail API
# 1. Create project in Google Cloud Console
# 2. Enable Gmail API
# 3. Download credentials.json
# 4. Place in secure location
# 5. Run gmail_watcher.py to authenticate
```

### 3. Start Watchers

```bash
# Terminal 1: Filesystem Watcher
python watchers/filesystem_watcher.py

# Terminal 2: Gmail Watcher
python watchers/gmail_watcher.py /path/to/credentials.json
```

### 4. Run Orchestrator

```bash
# Single run
python orchestrator.py

# Continuous mode
python orchestrator.py --continuous --interval 60
```

### 5. Set Up Scheduling

**Windows:**
```powershell
# Daily Briefing at 8 AM
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "orchestrator.py --daily-briefing" `
    -WorkingDirectory "D:\FTE_AI_Employee"
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" `
    -Action $action -Trigger $trigger
```

**Linux/Mac:**
```bash
crontab -e
# Add: 0 8 * * * cd /path && python orchestrator.py --daily-briefing
```

## Testing Checklist

### Bronze Tier (Prerequisites)
- [ ] File dropped in Inbox creates action file
- [ ] Orchestrator processes action file
- [ ] Dashboard updates correctly
- [ ] Files move to Done after completion

### Silver Tier
- [ ] Gmail watcher detects new emails
- [ ] Email action files created correctly
- [ ] Plan.md created for multi-step tasks
- [ ] Approval requests created for sensitive actions
- [ ] Approved actions execute automatically
- [ ] Social media posts require approval
- [ ] Daily briefing generates on schedule
- [ ] Weekly review generates on Monday

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Gmail watcher not authenticating | Check credentials.json path and scopes |
| Approval not executing | Verify file moved to /Approved/ |
| Plan not progressing | Check for blocked dependencies |
| Social post failing | Verify LinkedIn session is valid |
| Scheduled task not running | Check scheduler service status |

## Next Steps (Gold Tier)

After completing Silver tier, consider:
1. **Odoo Integration** - Accounting system via MCP
2. **WhatsApp Watcher** - Monitor WhatsApp Web
3. **Twitter/X Integration** - Post tweets
4. **Facebook/Instagram** - Social media expansion
5. **Ralph Wiggum Loop** - Autonomous multi-step completion
6. **Comprehensive Audit Logging** - Full activity tracking

---

*Silver Tier Skills Documentation*
*Version: 0.1 | Last Updated: 2026-02-25*
