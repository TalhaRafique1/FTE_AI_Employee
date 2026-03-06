# AI Employee - Silver Tier Implementation

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

A Personal AI Employee built with Qwen Code and Obsidian that autonomously processes tasks, monitors Gmail and LinkedIn, and manages your digital affairs 24/7.

## 🏆 Silver Tier Deliverables

This implementation completes all **Silver Tier** requirements:

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Bronze requirements | ✅ Complete | vault-operations.md |
| 2 | Two or more Watcher scripts | ✅ Complete | Gmail + LinkedIn + Filesystem |
| 3 | Automatically Post on LinkedIn | ✅ Complete | linkedin-posting.md + linkedin_watcher.py |
| 4 | Plan.md reasoning loop | ✅ Complete | plan-creation.md |
| 5 | One working MCP server | ✅ Complete | Playwright MCP for LinkedIn |
| 6 | Human-in-the-loop approval | ✅ Complete | approval-workflow.md |
| 7 | Basic scheduling | ✅ Complete | scheduling-operations.md |

## 📁 Project Structure

```
D:\FTE_AI_Employee\
├── AI_Employee_Vault/           # Obsidian vault (your AI's memory)
│   ├── Inbox/                   # Drop folder for new files
│   ├── Needs_Action/            # Items awaiting processing
│   ├── Plans/                   # Multi-step task plans
│   ├── Pending_Approval/        # Awaiting human approval
│   ├── Approved/                # Approved actions ready to execute
│   ├── Done/                    # Completed tasks
│   ├── Rejected/                # Rejected items
│   ├── Logs/                    # Activity logs
│   ├── Social/                  # Social media drafts
│   ├── Dashboard.md             # Real-time status dashboard
│   ├── Company_Handbook.md      # Rules of engagement
│   └── Business_Goals.md        # Objectives and metrics
│
├── watchers/
│   ├── base_watcher.py          # Abstract base class
│   ├── filesystem_watcher.py    # File system monitoring (Bronze)
│   ├── gmail_watcher.py         # Gmail monitoring (Silver)
│   └── linkedin_watcher.py      # LinkedIn monitoring (Silver)
│
├── skills/
│   ├── vault-operations.md      # (Bronze) File system operations
│   ├── email-operations.md      # (Silver) Email via Gmail MCP
│   ├── approval-workflow.md     # (Silver) HITL pattern
│   ├── social-media-operations.md # (Silver) Social media management
│   ├── plan-creation.md         # (Silver) Multi-step planning
│   ├── scheduling-operations.md # (Silver) Calendar & scheduling
│   ├── linkedin-posting.md      # (Silver) LinkedIn posting via MCP
│   └── SILVER_TIER_SKILLS.md    # Skills overview document
│
├── .qwen/skills/
│   └── browsing-with-playwright/
│       └── scripts/
│           ├── mcp-client.py    # MCP client for Playwright
│           ├── start-server.sh  # Start MCP server
│           └── stop-server.sh   # Stop MCP server
│
├── orchestrator.py              # Main coordination script
├── .env                         # Environment configuration
├── .env.example                 # Example environment file
├── credentials.json             # Gmail API credentials (YOU MUST HAVE THIS)
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Node.js](http://Node.js) | v24+ LTS | MCP servers & automation |

### Step 1: Install Python Dependencies

```bash
# Gmail API dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Already installed for Playwright MCP
# npx @playwright/mcp@latest
```

### Step 2: Verify Gmail Credentials

Ensure `credentials.json` exists in the project root:

```bash
# Check if file exists
dir credentials.json
```

The file should contain your Gmail OAuth credentials from Google Cloud Console.

### Step 3: Configure Environment (Optional)

Edit `.env` file to customize:

```bash
# LinkedIn credentials (optional - can login manually first time)
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password

# VIP senders for priority emails
VIP_SENDERS=client@example.com,partner@company.com

# Check intervals (seconds)
GMAIL_CHECK_INTERVAL=120
LINKEDIN_CHECK_INTERVAL=300
```

### Step 4: Authenticate Gmail (First Time Only)

```bash
# Run Gmail watcher - will open browser for authentication
python watchers\gmail_watcher.py
```

**Authentication Process:**
1. Browser window opens automatically
2. Sign in to your Google account
3. Grant permissions to the app
4. Token saved to `~/.ai_employee/gmail_token.pickle`
5. Subsequent runs use saved token

### Step 5: Start Playwright MCP Server

```bash
# Start MCP server for LinkedIn automation
npx @playwright/mcp@latest --port 8808 --shared-browser-context &

# Or use helper script (if available)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
```

### Step 6: Start Watchers

**Option A: Start All Watchers (Multiple Terminals)**

```bash
# Terminal 1: Filesystem Watcher
python watchers\filesystem_watcher.py

# Terminal 2: Gmail Watcher
python watchers\gmail_watcher.py

# Terminal 3: LinkedIn Watcher
python watchers\linkedin_watcher.py
```

**Option B: Run Orchestrator (Processes Items)**

```bash
# Single processing run
python orchestrator.py

# Continuous mode (processes every 60 seconds)
python orchestrator.py --continuous --interval 60
```

### Step 7: Open Obsidian Vault

1. Open Obsidian
2. Click "Open folder as vault"
3. Select `D:\FTE_AI_Employee\AI_Employee_Vault`
4. View Dashboard.md for real-time status

## 📖 Usage Guide

### Processing a Gmail Message

1. **Gmail Watcher detects new email:**
   - Checks every 2 minutes
   - Looks for unread emails
   - Identifies urgent/invoice-related emails

2. **Action file created:**
   ```
   Needs_Action/EMAIL_subject_sender_20260225_120000.md
   ```

3. **Orchestrator triggers Qwen Code:**
   - Reads email content
   - Creates plan if multi-step
   - Drafts response
   - Requests approval if needed

4. **Human approves (if required):**
   - Review in Obsidian
   - Move file from `Pending_Approval/` to `Approved/`

5. **Orchestrator executes:**
   - Sends email via MCP
   - Logs action
   - Moves to `Done/`

### Posting to LinkedIn

#### Create Post Draft

```markdown
# /Vault/Social/DRAFT_linkedin_post_2026-02-25.md
---
type: linkedin_post_draft
created: 2026-02-25T09:00:00Z
status: draft
---

## Post Content

🚀 Exciting News!

We're thrilled to announce the launch of our AI Employee service!

Key features:
✅ 24/7 operation
✅ Email & WhatsApp integration
✅ Human-in-the-loop approvals

#AIEmployee #Automation #BusinessGrowth
```

#### Approve and Post

1. **Move to Pending_Approval:**
   ```bash
   mv Social/DRAFT_linkedin_post_2026-02-25.md Pending_Approval/
   ```

2. **Review in Obsidian**

3. **Approve:**
   ```bash
   mv Pending_Approval/LINKEDIN_post_*.md Approved/
   ```

4. **Orchestrator posts automatically:**
   - Uses Playwright MCP
   - Navigates to LinkedIn
   - Creates post
   - Takes screenshot confirmation
   - Logs to `Logs/linkedin_posts.md`

### Creating a Plan for Multi-Step Tasks

When Qwen Code detects a complex task:

```markdown
# /Plans/PLAN_process_invoice_2026-02-25.md
---
type: plan
status: in_progress
source: Needs_Action/EMAIL_invoice_*.md
---

## Objective
Process invoice request and send to client

## Steps
- [x] Identify client details
- [ ] Calculate amount
- [ ] Generate invoice PDF
- [ ] Create approval request
- [ ] Send after approval
```

## 🧪 Testing

### Test Gmail Watcher

```bash
# Send yourself a test email with subject "Test Email"

# Run Gmail watcher
python watchers\gmail_watcher.py

# Check Needs_Action folder for new action file
dir AI_Employee_Vault\Needs_Action
```

### Test LinkedIn Watcher

```bash
# Start MCP server first
npx @playwright/mcp@latest --port 8808 --shared-browser-context &

# Run LinkedIn watcher
python watchers\linkedin_watcher.py

# Check for notification action files
dir AI_Employee_Vault\Needs_Action
```

### Test Orchestrator

```bash
# Create a test action file
echo "Test content" > AI_Employee_Vault\Needs_Action\TEST_file.md

# Run orchestrator
python orchestrator.py

# Check Dashboard.md updated
type AI_Employee_Vault\Dashboard.md
```

### Test Full Workflow

```bash
# 1. Send email to yourself
# 2. Start Gmail watcher
python watchers\gmail_watcher.py

# 3. In another terminal, run orchestrator
python orchestrator.py

# 4. Check Obsidian for:
#    - New action file in Needs_Action
#    - Plan created in Plans
#    - Dashboard updated
```

## 📋 Configuration

### Gmail API Setup (If You Need New Credentials)

1. **Go to Google Cloud Console:**
   https://console.cloud.google.com/

2. **Create new project:**
   - Project name: "AI Employee"

3. **Enable Gmail API:**
   - APIs & Services → Library
   - Search "Gmail API"
   - Click Enable

4. **Create OAuth credentials:**
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost`
   - Download `credentials.json`

5. **Place in project root:**
   ```
   D:\FTE_AI_Employee\credentials.json
   ```

### LinkedIn Automation Setup

LinkedIn uses Playwright MCP with persistent browser context:

1. **First login is manual:**
   - Run LinkedIn watcher
   - Browser opens
   - Login to LinkedIn
   - Session saved automatically

2. **Subsequent runs:**
   - Auto-login with saved session
   - Session stored in `~/.ai_employee/linkedin_session`

### Approval Thresholds

Edit `Company_Handbook.md` to customize:

```markdown
## Approval Rules

| Action | Auto-Approve | Requires Approval |
|--------|--------------|-------------------|
| Payments | Never | All payments |
| Email to known contacts | ✓ | New contacts, bulk |
| LinkedIn posts | Never | All posts |
```

## 🔒 Security Best Practices

1. **Never commit credentials:**
   ```bash
   # .gitignore already includes:
   .env
   credentials.json
   *.pickle
   ```

2. **Use environment variables:**
   ```bash
   # In production
   export GMAIL_CREDENTIALS_PATH=/secure/path/credentials.json
   ```

3. **Enable 2FA:**
   - Gmail account
   - LinkedIn account

4. **Rotate credentials monthly**

5. **Review logs weekly:**
   ```bash
   type AI_Employee_Vault\Logs\orchestrator_*.log
   ```

## 🐛 Troubleshooting

### Gmail Watcher Issues

| Issue | Solution |
|-------|----------|
| No credentials found | Ensure `credentials.json` in project root |
| Authentication fails | Delete `~/.ai_employee/gmail_token.pickle` and re-authenticate |
| No emails detected | Check if emails are marked as unread |
| API quota exceeded | Wait 24 hours or request quota increase |

### LinkedIn Watcher Issues

| Issue | Solution |
|-------|----------|
| MCP server not found | Run `npx @playwright/mcp@latest --port 8808` |
| Login required | Manual login first time, session saved after |
| Session expired | Re-login via browser |
| Rate limited | Wait 24 hours between actions |

### Orchestrator Issues

| Issue | Solution |
|-------|----------|
| Qwen not found | Run `where qwen` to verify installation |
| No items processed | Check Needs_Action folder has .md files |
| Approval not executing | Ensure file is in Approved/ folder |

## 📊 Monitoring

### View Dashboard

```bash
type AI_Employee_Vault\Dashboard.md
```

### Check Logs

```bash
# Today's orchestrator log
type AI_Employee_Vault\Logs\orchestrator_2026-02-25.log

# Gmail watcher log
type AI_Employee_Vault\Logs\watcher_2026-02-25.log

# LinkedIn posts log
type AI_Employee_Vault\Logs\linkedin_posts.md
```

### Check Processed Items

```bash
# Processed emails
type AI_Employee_Vault\.processed_emails.json

# Processed LinkedIn notifications
type AI_Employee_Vault\.processed_linkedin.json
```

## 🎯 Next Steps (Gold Tier)

After mastering Silver tier:

1. **WhatsApp Watcher** - Monitor WhatsApp Web
2. **Odoo Integration** - Accounting system via MCP
3. **Twitter/X Integration** - Post tweets
4. **Facebook/Instagram** - Social media expansion
5. **Ralph Wiggum Loop** - Autonomous multi-step completion
6. **Weekly CEO Briefing** - Automated business reports

## 📚 Learning Resources

- [Qwen Code Documentation](https://github.com/QwenLM/Qwen)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Obsidian Help](https://help.obsidian.md)
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

## 📄 License

This project is part of the Personal AI Employee Hackathon 0.

---

**Built with ❤️ by the AI Employee Community**

*Version: 0.2 (Silver Tier) | Last Updated: 2026-02-25*
