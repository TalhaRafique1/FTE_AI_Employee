---
name: approval-workflow
description: |
  Human-in-the-loop approval workflow for sensitive actions.
  Manages approval requests, tracks approvals, and executes approved actions.
  Essential for Silver tier compliance and safe automation.
---

# Approval Workflow Agent Skill (Silver Tier)

This skill implements the Human-in-the-Loop (HITL) pattern for safe automation of sensitive actions.

## Overview

The Approval Workflow skill provides:
- Create approval requests for sensitive actions
- Track pending approvals with expiration
- Execute approved actions automatically
- Audit trail for all approvals
- Rejection handling with feedback

## Folder Structure

```
/Vault/
├── Pending_Approval/    # Awaiting human decision
├── Approved/            # Approved, ready to execute
├── Rejected/            # Rejected with comments
└── Logs/
    └── approvals.md     # Approval audit log
```

## Approval Request Schema

```markdown
# /Pending_Approval/[TYPE]_[description]_[date].md
---
type: approval_request
action: <action_type>
created: <ISO_timestamp>
expires: <ISO_timestamp>
priority: <low|normal|high|urgent>
status: pending
---

## Action Required
<Clear description of what needs approval>

## Details
- **Item:** <relevant details>
- **Reason:** <why this action is needed>
- **Risk:** <any associated risks>
- **Impact:** <what happens if approved/rejected>

## Supporting Information
<Additional context, attachments, references>

## To Approve
Move this file to `/Approved` folder

## To Reject
Move this file to `/Rejected` folder or add comments below

## Comments
_Human can add comments here before deciding_
```

## Action Types

### Payment Approval

```markdown
---
type: approval_request
action: payment
amount: 500.00
currency: USD
recipient: "Client A"
recipient_account: "****1234"
created: 2026-02-25T10:30:00Z
expires: 2026-02-26T10:30:00Z
priority: high
status: pending
---

## Payment Details
- **Amount:** $500.00 USD
- **To:** Client A (Bank: ****1234)
- **Reference:** Invoice #1234
- **Due Date:** 2026-02-28

## Justification
Payment for services rendered in January 2026. Invoice verified against contract.

## Risk Assessment
- Low risk: Known client, valid invoice
- Amount within auto-approval threshold

## To Approve
Move to `/Approved` - Payment will be processed via bank MCP

## To Reject
Move to `/Rejected` - Add reason for rejection
```

### Email Send Approval

```markdown
---
type: approval_request
action: send_email
to: "client@example.com"
subject: "Invoice #1234 - Payment Due"
created: 2026-02-25T10:30:00Z
expires: 2026-02-26T10:30:00Z
priority: normal
status: pending
---

## Email Details
- **To:** client@example.com
- **Subject:** Invoice #1234 - Payment Due
- **Attachment:** /Vault/Invoices/2026-01_Client_A.pdf

## Content Preview
Dear Client,

Please find attached invoice #1234 for $1,500...

## Why Approval Required
First-time invoice to this client

## To Approve
Move to `/Approved`

## To Reject
Move to `/Rejected`
```

### Social Media Post Approval

```markdown
---
type: approval_request
action: social_post
platform: linkedin
content_type: business_update
created: 2026-02-25T10:30:00Z
expires: 2026-02-27T10:30:00Z
priority: low
status: pending
---

## Post Details
- **Platform:** LinkedIn
- **Type:** Business Update
- **Scheduled:** 2026-02-26 09:00 AM

## Content
🚀 Exciting news! We're launching our new AI Employee service...

## Image
/Vault/Social/posts/2026-02-25_linkedin.png

## To Approve
Move to `/Approved`

## To Reject
Move to `/Rejected`
```

### File Operation Approval

```markdown
---
type: approval_request
action: file_delete
file_path: /Vault/FileStorage/old_contract.pdf
created: 2026-02-25T10:30:00Z
expires: 2026-02-28T10:30:00Z
priority: low
status: pending
---

## Operation Details
- **Action:** Delete file
- **File:** old_contract.pdf
- **Reason:** Contract expired 2+ years ago

## To Approve
Move to `/Approved`

## To Reject
Move to `/Rejected`
```

## Approval Thresholds (from Company_Handbook)

| Action Type | Auto-Approve | Requires Approval |
|-------------|--------------|-------------------|
| Payments | Never | All payments |
| Email to known contacts | ✓ | New contacts, bulk |
| Social media drafts | ✓ | Actual posting |
| File create/read | ✓ | Delete, external copy |
| Calendar events | < $100 | > $100 or VIP |

## Workflow Process

### 1. AI Detects Action Needed

```markdown
# AI processes action file and determines approval needed

## Decision Log
- Action type: payment
- Amount: $500
- Threshold: $0 (all payments require approval)
- Decision: Create approval request
```

### 2. Create Approval Request

```bash
# AI creates file in /Pending_Approval/
# File naming: [TYPE]_[description]_[YYYY-MM-DD].md
```

### 3. Human Reviews

Human receives notification (email, desktop alert, etc.):

```
📋 Approval Required: PAYMENT_client_invoice_2026-02-25.md

Amount: $500.00 to Client A
Location: Pending_Approval/
Expires: 2026-02-26 10:30 AM

Review in Obsidian: vault://Pending_Approval/PAYMENT_...
```

### 4. Human Decides

**To Approve:**
```bash
# Move file to Approved folder
mv Pending_Approval/PAYMENT_*.md Approved/
```

**To Reject:**
```bash
# Add rejection reason in file
# Move to Rejected folder
mv Pending_Approval/PAYMENT_*.md Rejected/
```

### 5. Orchestrator Executes

```python
# Orchestrator watches /Approved/ folder
# When new file appears:
# 1. Parse action type
# 2. Execute via appropriate MCP
# 3. Log result
# 4. Move to /Done/
```

## Orchestrator Integration

```python
# In orchestrator.py

def process_approved_actions(self):
    """Process all approved actions in /Approved/ folder."""
    approved_folder = self.vault_path / 'Approved'
    
    for approval_file in approved_folder.glob('*.md'):
        try:
            content = approval_file.read_text()
            action_type = self._extract_action_type(content)
            
            if action_type == 'payment':
                self._execute_payment(approval_file)
            elif action_type == 'send_email':
                self._execute_email(approval_file)
            elif action_type == 'social_post':
                self._execute_social_post(approval_file)
            
            # Move to Done after successful execution
            approval_file.rename(self.done / approval_file.name)
            
        except Exception as e:
            self.logger.error(f'Error executing approval {approval_file}: {e}')
            # Move back to Pending_Approval on error
            approval_file.rename(self.pending_approval / approval_file.name)
```

## Approval Log Template

```markdown
# /Vault/Logs/approvals.md

## 2026-02-25

| Time | Type | Description | Decision | Executed By | Status |
|------|------|-------------|----------|-------------|--------|
| 10:45 | payment | $500 to Client A | Approved | orchestrator | ✅ Complete |
| 11:30 | email | Invoice to new client | Approved | orchestrator | ✅ Complete |
| 14:00 | social | LinkedIn post | Rejected | - | ❌ Rejected |
| 15:15 | file_delete | Old contract | Approved | orchestrator | ✅ Complete |

## Summary
- Total: 4
- Approved: 3
- Rejected: 1
- Pending: 0
```

## Expiration Handling

Approvals should expire to prevent stale actions:

```markdown
---
expires: 2026-02-26T10:30:00Z
---

## ⚠️ EXPIRED
This approval request expired on 2026-02-26 at 10:30 AM.

Action: Rejected due to expiration
Reason: No response within 24 hours

To re-submit, create a new approval request.
```

```python
def check_expired_approvals(self):
    """Move expired approvals to Rejected."""
    for approval_file in self.pending_approval.glob('*.md'):
        content = approval_file.read_text()
        expires = self._extract_expiry(content)
        
        if expires and datetime.now() > expires:
            # Add expiration notice
            content += f'\n\n## ⚠️ EXPIRED\nAuto-rejected due to expiration.'
            approval_file.write_text(content)
            
            # Move to Rejected
            approval_file.rename(self.rejected / approval_file.name)
            self.log_approval('expired', approval_file.name)
```

## Notification System

### Desktop Notification (Python)

```python
# Send desktop notification when approval needed
import plyer.notification

def notify_approval_needed(filename):
    plyer.notification.notify(
        title='📋 Approval Required',
        message=f'{filename} needs your review',
        app_name='AI Employee',
        timeout=10
    )
```

### Email Notification

```markdown
# /Pending_Approval/EMAIL_notification_approval_needed.md
---
type: notification
channel: email
recipient: human@company.com
---

Subject: 📋 AI Employee Approval Required

Hi,

You have {count} pending approval(s):

{list_of_approvals}

Review in Obsidian or respond to this email.
```

## Security Considerations

1. **Never auto-approve payments** - Always require human review
2. **Log all approvals** - Maintain audit trail
3. **Set expiration times** - Prevent stale approvals
4. **Verify file movement** - Only folder moves trigger execution
5. **Rate limit executions** - Max 10 actions per hour

## Best Practices

1. **Clear descriptions** - Make approval decisions easy
2. **Include context** - Why is this action needed?
3. **Set appropriate expiry** - 24h for normal, 1h for urgent
4. **Log everything** - Full audit trail
5. **Test workflow** - Regular approval drills

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not executing | Check file is in /Approved/ |
| Wrong action executed | Verify action_type in frontmatter |
| Approval expired too soon | Adjust expiry time in template |
| Notifications not working | Check notification permissions |

---

*Version: 0.2 (Silver Tier)*
*Last Updated: 2026-02-25*
