---
name: email-operations
description: |
  Email operations for the AI Employee using Gmail MCP.
  Send, draft, search, and manage emails for business communications.
  Includes human-in-the-loop approval for sensitive emails.
---

# Email Operations Agent Skill (Silver Tier)

This skill enables the AI Employee to handle email communications via Gmail MCP.

## Overview

The Email Operations skill provides:
- Send emails to contacts
- Create draft emails for review
- Search and read emails
- Handle attachments
- Approval workflow for sensitive emails

## Prerequisites

### Gmail MCP Server Setup

1. **Install Gmail MCP:**
   ```bash
   npm install -g @anthropic/email-mcp
   ```

2. **Configure Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json`

3. **Configure in Qwen Code:**
   ```json
   {
     "servers": [
       {
         "name": "gmail",
         "command": "node",
         "args": ["/path/to/email-mcp/index.js"],
         "env": {
           "GMAIL_CREDENTIALS": "/path/to/credentials.json"
         }
       }
     ]
   }
   ```

## Usage Patterns

### Send Email (Auto-Approved)

For routine communications to known contacts:

```bash
# Send a simple email
qwen -p "Send email to client@example.com with subject 'Meeting Confirmation' and body 'Looking forward to our meeting tomorrow at 2 PM.'"
```

### Send Email (Requires Approval)

For sensitive emails (new contacts, financial matters, bulk sends):

```markdown
# Create approval request in /Pending_Approval/

# /Pending_Approval/EMAIL_client_invoice_2026-02-25.md
---
type: approval_request
action: send_email
to: "client@example.com"
subject: "Invoice #1234 - Payment Due"
priority: high
created: 2026-02-25T10:00:00Z
status: pending
---

## Email Details
- **To:** client@example.com
- **Subject:** Invoice #1234 - Payment Due
- **Attachment:** /Vault/Invoices/2026-01_Client_A.pdf

## Content Preview
Dear Client,

Please find attached invoice #1234 for $1,500...

## To Approve
Move this file to `/Approved` folder

## To Reject
Move to `/Rejected` or add comments
```

### Create Draft Email

For emails that need human review before sending:

```markdown
# /Vault/Drafts/DRAFT_proposal_2026-02-25.md
---
type: email_draft
to: "prospect@example.com"
subject: "Project Proposal - Q1 2026"
created: 2026-02-25T10:00:00Z
status: draft
---

## Draft Content

Dear Prospect,

Thank you for your interest in our services...

## Next Steps
- [ ] Review content
- [ ] Edit as needed
- [ ] Move to /Approved to send
- [ ] Move to /Rejected to discard
```

### Search Emails

```bash
# Search for unread important emails
qwen -p "Search Gmail for unread emails marked as important from the last 24 hours"
```

### Process Email Responses

```markdown
# When email response is received:

## Action Taken
1. Read email from Needs_Action/EMAIL_response_*.md
2. Categorize response type (inquiry, complaint, payment, etc.)
3. Create appropriate response draft
4. Request approval if needed
5. Log interaction in /Vault/Logs/email_log.md
```

## Email Templates

### Invoice Email Template

```markdown
Subject: Invoice #[INVOICE_NUMBER] - [AMOUNT] Due [DUE_DATE]

Dear [CLIENT_NAME],

Please find attached invoice #[INVOICE_NUMBER] for [AMOUNT].

Payment is due by [DUE_DATE]. You can pay via:
- Bank transfer: [ACCOUNT_DETAILS]
- Credit card: [PAYMENT_LINK]

Thank you for your business!

Best regards,
[YOUR_NAME]
```

### Meeting Confirmation Template

```markdown
Subject: Meeting Confirmation - [DATE] at [TIME]

Dear [ATTENDEE_NAME],

This confirms our meeting scheduled for:
- Date: [DATE]
- Time: [TIME]
- Location: [LOCATION/VIDEO_LINK]

Agenda:
1. [ITEM_1]
2. [ITEM_2]
3. [ITEM_3]

Looking forward to speaking with you.

Best regards,
[YOUR_NAME]
```

### Follow-up Template

```markdown
Subject: Following up on [TOPIC]

Dear [CONTACT_NAME],

I wanted to follow up on [PREVIOUS_TOPIC] from [DATE].

[CONTEXT_OR_QUESTION]

Please let me know if you need any additional information.

Best regards,
[YOUR_NAME]
```

## Approval Rules

### Auto-Approve (No Approval Needed)
- Replies to known contacts (in Company_Handbook contact list)
- Meeting confirmations
- Status updates to internal team

### Requires Approval
- First-time contact with new person/company
- Any email mentioning payments, invoices, or financial matters
- Bulk emails (more than 5 recipients)
- Emails with attachments over 5MB
- Responses to complaints or sensitive topics

## Integration with Watchers

### Gmail Watcher Integration

```python
# gmail_watcher.py creates action files like:

---
type: email
from: sender@example.com
subject: Urgent: Project Update Needed
received: 2026-02-25T10:30:00Z
priority: high
status: pending
---

## Email Content
[Email body text]

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to team
- [ ] Archive after processing
```

## Logging

All email actions should be logged:

```markdown
# /Vault/Logs/email_log.md

## 2026-02-25

| Time | To/From | Subject | Action | Status |
|------|---------|---------|--------|--------|
| 10:30 | client@example.com | Invoice #1234 | Sent | Delivered |
| 11:45 | prospect@example.com | Proposal | Draft Created | Pending Review |
```

## Error Handling

| Error | Recovery |
|-------|----------|
| Gmail API quota exceeded | Queue email, retry in 1 hour |
| Invalid recipient | Flag for human review |
| Attachment too large | Compress or use cloud link |
| Authentication failed | Alert human, pause email operations |

## Security Considerations

1. **Never log email passwords or tokens**
2. **Redact sensitive information** in logs (account numbers, PII)
3. **Use OAuth 2.0** for Gmail authentication
4. **Enable 2FA** on Gmail account
5. **Review sent emails** weekly for accuracy

## Best Practices

1. **Always BCC yourself** on important business emails
2. **Use templates** for consistency
3. **Proofread** before sending (use approval workflow)
4. **Track responses** in the vault
5. **Archive processed emails** to maintain clean inbox

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Gmail MCP not connecting | Check credentials.json path |
| Emails not sending | Verify OAuth token is valid |
| Attachments failing | Check file path and size limits |
| Rate limiting | Wait 1 hour between bulk sends |

---

*Version: 0.2 (Silver Tier)*
*Last Updated: 2026-02-25*
