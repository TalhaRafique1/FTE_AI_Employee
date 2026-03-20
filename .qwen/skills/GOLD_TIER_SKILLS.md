# Gold Tier Skills - AI Employee

This document describes all Gold Tier skills available to your AI Employee.

## Overview

Gold Tier adds these major capabilities:

| Skill | Description | Status |
|-------|-------------|--------|
| **Facebook Integration** | Post to Facebook, monitor notifications | ✅ Complete |
| **Odoo Accounting** | Invoicing, payments, financial reports | ✅ Complete |
| **Ralph Wiggum Loop** | Autonomous multi-step task completion | ✅ Complete |
| **CEO Briefings** | Weekly automated business audits | ✅ Complete |

---

## 1. Facebook Operations Skill (Graph API)

### Overview

Facebook integration uses **Facebook Graph API** (not Playwright) for reliable, official integration.

**Benefits:**
- ✅ Official API - no browser automation needed
- ✅ More reliable - no UI changes breaking integration
- ✅ Full features - posts, messages, insights, notifications
- ✅ Rate limited - protected from abuse

### Prerequisites

1. **Facebook Developer App** - See `facebook-mcp-server/README.md`
2. **Access Token** - User or Page access token
3. **Environment Variables**:
   ```bash
   FACEBOOK_APP_ID=your_app_id
   FACEBOOK_APP_SECRET=your_app_secret
   FACEBOOK_ACCESS_TOKEN=your_access_token
   FACEBOOK_PAGE_ID=your_page_id (optional)
   ```

### Available Tools

| Tool | Description |
|------|-------------|
| `facebook_connect` | Test connection and verify auth |
| `facebook_get_profile` | Get profile or page information |
| `facebook_post` | Create a post on Facebook |
| `facebook_post_photo` | Post a photo with caption |
| `facebook_get_notifications` | Get recent notifications |
| `facebook_get_messages` | Get recent messages |
| `facebook_get_posts` | Get recent posts |
| `facebook_get_insights` | Get page analytics |
| `facebook_send_message` | Send Messenger message |

### Usage Examples

#### Post to Facebook

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8809 ^
  -t facebook_post ^
  -p '{"message": "Hello from AI Employee! 🤖"}'
```

#### Post with Link

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8809 ^
  -t facebook_post ^
  -p '{"message": "Check out our latest product!", "link": "https://example.com"}'
```

#### Post Photo

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8809 ^
  -t facebook_post_photo ^
  -p '{"message": "New product launch!", "photo_url": "https://example.com/image.jpg"}'
```

#### Get Notifications

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8809 ^
  -t facebook_get_notifications ^
  -p '{"limit": 10}'
```

#### Get Page Insights

```bash
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8809 ^
  -t facebook_get_insights ^
  -p '{"metrics": ["page_impressions_unique", "page_engaged_users"], "period": "week"}'
```

### Approval Workflow

For automated posting with approval:

```markdown
---
type: approval_request
action: facebook_post
created: 2026-03-06T14:00:00
priority: normal
---

## Post Content
🎉 Exciting news! We just launched our new product line.

## Link
https://example.com/product

## To Approve
Move to /Approved folder
```

### Facebook Watcher

The Facebook Watcher (`watchers/facebook_watcher_api.py`):
- Monitors notifications every 5 minutes
- Creates action files for new notifications
- Flags urgent messages and mentions
- Uses Graph API (no browser needed)

**Start Watcher:**
```bash
python watchers\facebook_watcher_api.py
```

### Setup Guide

See `facebook-mcp-server/README.md` for complete setup instructions.

**Quick Start:**
```bash
# 1. Set environment variables
set FACEBOOK_ACCESS_TOKEN=your_token_here
set FACEBOOK_PAGE_ID=your_page_id_here

# 2. Start MCP server
cd facebook-mcp-server
python facebook_mcp_server.py

# 3. Test connection
python ..\.qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8809 ^
  -t facebook_connect ^
  -p '{}'
```

---

## 2. Odoo Accounting Skill

### Available Tools

| Tool | Description |
|------|-------------|
| `odoo_connect` | Connect and authenticate with Odoo |
| `odoo_get_account_summary` | Get receivables, payables, net position |
| `odoo_get_invoices` | List invoices (all, draft, posted, cancel) |
| `odoo_create_invoice` | Create new customer/vendor invoice |
| `odoo_get_partners` | Search customers/vendors |
| `odoo_create_partner` | Add new customer/vendor |
| `odoo_get_products` | Search products/services |
| `odoo_confirm_invoice` | Post/confirm an invoice |
| `odoo_register_payment` | Record payment against invoice |
| `odoo_search` | Generic search on any Odoo model |

### Usage Examples

#### Check Financial Status

```markdown
## Task: Review Company Finances

1. Call `odoo_get_account_summary`
2. Review:
   - Total Receivable (money owed to you)
   - Total Payable (money you owe)
   - Net Position
3. Update Dashboard.md with key metrics
4. Flag any concerns in CEO briefing
```

#### Create Invoice for Client

```markdown
## Task: Create Invoice

1. Search for client: `odoo_get_partners` with search_term="Client Name"
2. If not found: `odoo_create_partner` with client details
3. Create invoice: `odoo_create_invoice`
   ```json
   {
     "partner_id": 123,
     "invoice_type": "out_invoice",
     "lines": [
       {
         "name": "Consulting Services - January",
         "quantity": 1,
         "price_unit": 1500
       }
     ]
   }
   ```
4. Create approval request (REQUIRED before confirming)
5. After approval: `odoo_confirm_invoice`
```

#### Record Payment

```markdown
## Task: Record Customer Payment

1. Find invoice: `odoo_get_invoices` with state='posted'
2. Register payment: `odoo_register_payment`
   ```json
   {
     "invoice_id": 456,
     "amount": 1500,
     "payment_date": "2026-03-06"
   }
   ```
3. Log transaction in Accounting folder
```

### Approval Requirements

**ALWAYS require approval for:**
- Creating new invoices (any amount)
- Confirming/posting invoices
- Recording payments
- Creating new partners
- Any financial transaction

**NEVER auto-approve:**
- Payments to new vendors
- Invoices over $500
- Refunds or credits

---

## 3. Ralph Wiggum Loop Skill

### Overview

The Ralph Wiggum Loop enables autonomous multi-step task completion by:
1. Running Qwen Code with a task
2. Checking if task is complete
3. If not complete, re-injecting the prompt with previous output
4. Repeating until done or max iterations reached

### Usage

#### Start a Ralph Loop

```bash
# Basic usage
python ralph_wiggum_loop.py "Process all pending invoices and send reminders"

# With options
python ralph_wiggum_loop.py "Complete the monthly audit" \
  --vault "D:\FTE_AI_Employee\AI_Employee_Vault" \
  --max-iterations 15 \
  --completion-promise "TASK_COMPLETE" \
  --timeout 90
```

#### From Orchestrator

```bash
python orchestrator.py --ralph-loop "Generate and send all pending invoices"
```

#### Completion Detection

The loop detects completion via:

1. **Promise-based**: Output contains `<promise>TASK_COMPLETE</promise>`
2. **File-based**: All related files moved to `/Done`
3. **Plan-based**: All Plan.md checkboxes marked complete

### Example: Multi-Step Invoice Processing

```markdown
# Plan: Monthly Invoice Processing

## Objective
Generate and send all pending invoices for the month

## Steps (Ralph Wiggum Loop)
- [ ] Get list of unbilled projects from Plans
- [ ] For each project:
  - [ ] Find client in Odoo (or create)
  - [ ] Calculate billable amount
  - [ ] Create invoice in Odoo
  - [ ] Create approval request
  - [ ] After approval, confirm invoice
  - [ ] Send invoice via email
- [ ] Generate summary report
- [ ] Update Dashboard.md
- [ ] Move all files to Done
- [ ] Output: <promise>TASK_COMPLETE</promise>
```

### Best Practices

1. **Clear completion criteria**: Define what "done" looks like
2. **Reasonable max iterations**: Start with 10, adjust based on task
3. **Timeout protection**: Set appropriate timeout (default 60 min)
4. **State tracking**: Use state file for debugging
5. **Logging**: All iterations logged to `Logs/ralph_wiggum_*.log`

---

## 4. CEO Briefing Skill

### Overview

Automatically generates comprehensive weekly business briefings every Monday morning.

### Usage

#### Generate Briefing Manually

```bash
# Basic
python ceo_briefing_generator.py

# With Odoo integration
python ceo_briefing_generator.py --odoo

# Specific week
python ceo_briefing_generator.py --week-start 2026-03-01

# Dry run
python ceo_briefing_generator.py --dry-run
```

#### From Orchestrator

```bash
# Generate now
python orchestrator.py --generate-briefing

# With Odoo
python orchestrator.py --generate-briefing --odoo
```

#### Schedule Weekly Briefing

```bash
# Schedule for Monday at 7 AM
python orchestrator.py --schedule-briefing

# Or manually via Task Scheduler:
schtasks /create /tn "AI_Employee_CEO_Briefing" ^
  /tr "python ceo_briefing_generator.py --vault D:\FTE_AI_Employee\AI_Employee_Vault" ^
  /sc weekly /d MON /st 07:00 /rl highest /f
```

### Briefing Contents

Each briefing includes:

1. **Executive Summary**: High-level overview
2. **Revenue Analysis**: Income, expenses, net position
3. **Completed Tasks**: What was accomplished
4. **Bottlenecks**: Delayed or stuck tasks
5. **Subscription Audit**: Unused or wasteful spending
6. **Upcoming Deadlines**: Next 30 days
7. **Proactive Suggestions**: AI recommendations
8. **Focus Areas**: Recommended priorities

### Example Output

```markdown
# Monday Morning CEO Briefing

**Week of:** March 1, 2026 - March 7, 2026

## Executive Summary
Positive week with $2,450 net revenue. High productivity with 23 tasks completed.
2 critical bottlenecks require attention.

## Revenue
| Metric | This Week | Status |
|--------|-----------|--------|
| Revenue | $3,500.00 | 📈 Positive |
| Expenses | $1,050.00 | - |
| Net | $2,450.00 | 📈 Positive |

## Bottlenecks
| Task | Age (Days) | Severity |
|------|------------|----------|
| Client X Proposal | 8 | 🔴 high |

## Subscription Audit
| Service | Monthly Cost | Last Used | Status |
|---------|--------------|-----------|--------|
| Adobe CC | $54.99 | 45 days ago | ⚠️ unused_30_days |

## Proactive Suggestions

### 🟡 Review Adobe Creative Cloud subscription
**Type:** cost_optimization
No activity in 45 days. Cost: $54.99/month
**Recommended Action:** Consider canceling Adobe CC
```

### Integration Points

The briefing generator:

1. **Reads from:**
   - `/Done` folder for completed tasks
   - `/Logs` for transaction history
   - `Business_Goals.md` for targets and subscriptions
   - Odoo (if enabled) for financial data

2. **Updates:**
   - `Dashboard.md` with latest briefing link
   - `/Briefings` folder with new report

---

## 5. Combined Workflows

### Example: Complete Business Audit

```bash
# 1. Start Ralph Wiggum loop for comprehensive audit
python ralph_wiggum_loop.py "Complete full business audit" \
  --max-iterations 20

# The loop will:
# - Generate CEO briefing
# - Review Odoo financials
# - Identify bottlenecks
# - Create action plans
# - Update Dashboard
```

### Example: Social Media Campaign

```bash
# 1. Create posts in Needs_Action
# 2. Start Ralph loop
python ralph_wiggum_loop.py "Execute social media campaign"

# The loop will:
# - Review each post
# - Create approval requests
# - Post to LinkedIn (approved)
# - Post to Facebook (approved)
# - Log all posts
# - Generate engagement report
```

### Example: Month-End Closing

```bash
# 1. Start Ralph loop
python ralph_wiggum_loop.py "Complete month-end closing"

# The loop will:
# - Review all Odoo invoices
# - Record outstanding payments
# - Reconcile transactions
# - Generate financial report
# - Create CEO briefing
# - Update Business_Goals.md
```

---

## Configuration

### Environment Variables

```bash
# Odoo Configuration
export ODOO_URL=http://localhost:8069
export ODOO_DB=postgres
export ODOO_USER=admin
export ODOO_PASSWORD=admin

# MCP Servers
export PLAYWRIGHT_MCP_URL=http://localhost:8808
export ODOO_MCP_URL=http://localhost:8810

# Vault Configuration
export AI_EMPLOYEE_VAULT=D:\FTE_AI_Employee\AI_Employee_Vault
```

### Docker Compose (Odoo)

```yaml
# odoo/docker-compose.yml
services:
  odoo:
    image: odoo:17.0
    ports:
      - "8069:8069"
  odoo-mcp:
    build: ./odoo-mcp-server
    ports:
      - "8810:8810"
```

Start with:
```bash
cd odoo
docker-compose up -d
```

---

## Troubleshooting

### Facebook Posting Fails

1. Check MCP server is running: `npx @playwright/mcp@latest --port 8808`
2. Verify Facebook session is authenticated
3. Check logs: `Logs/facebook_*.log`

### Odoo Connection Issues

1. Verify Odoo is running: `curl http://localhost:8069`
2. Check credentials in environment variables
3. Test MCP connection:
   ```bash
   python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
     -u http://localhost:8810 \
     -t odoo_connect \
     -p '{}'
   ```

### Ralph Loop Stuck

1. Check logs: `Logs/ralph_wiggum_*.log`
2. Review state file: `.ralph_state.json`
3. Adjust max iterations or timeout
4. Manually verify completion criteria

### CEO Briefing Empty

1. Ensure tasks are moved to `/Done`
2. Check transaction logs exist
3. Verify Business_Goals.md has data
4. Enable Odoo for financial data

---

## Gold Tier Checklist

- [ ] Facebook Watcher running
- [ ] Odoo Docker containers up
- [ ] Odoo MCP server connected
- [ ] Ralph Wiggum script tested
- [ ] CEO Briefing generated successfully
- [ ] Weekly briefing scheduled
- [ ] All skills documented
- [ ] Approval workflow tested

---

*Gold Tier - AI Employee Project | Complete Autonomous Business Management*
