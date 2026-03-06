# Qwen Code Instructions for AI Employee

## When Processing Needs_Action Files

### Step 1: Read Company_Handbook.md First

Understand the rules for:
- What requires approval
- What can be auto-approved
- Priority levels

### Step 2: Process Each File

For EACH file in `Needs_Action/`:

#### A. Analyze the Content

Ask yourself:
1. Is this a payment/financial matter? → **REQUIRES APPROVAL**
2. Is this communication to a NEW contact? → **REQUIRES APPROVAL**
3. Is this a sensitive action? → **REQUIRES APPROVAL**
4. Does this have 3+ steps? → **CREATE PLAN**
5. Can this be done in 1-2 steps safely? → **DO IT**

#### B. Create Pending_Approval (When Required)

For actions requiring approval, CREATE THIS FILE:

```markdown
# /Pending_Approval/[TYPE]_[description]_[date].md
---
type: approval_request
action: [send_email|payment|social_post|file_operation]
created: [ISO timestamp]
expires: [ISO timestamp, usually +24 hours]
priority: [low|normal|high|urgent]
status: pending
---

## Action Required
[Clear description of what needs approval]

## Details
- **Item:** [relevant details]
- **Reason:** [why this action is needed]
- **Risk:** [any associated risks]

## [Action-Specific Details]

For emails:
- **To:** [email address]
- **Subject:** [subject line]
- **Content:** [draft email content]

For payments:
- **Amount:** [$XXX.XX]
- **Recipient:** [name]
- **Reference:** [invoice #]

## To Approve
Move this file to `/Approved` folder

## To Reject
Move this file to `/Rejected` folder or add comments below
```

#### C. Create Plan (For Multi-Step Tasks)

For tasks with 3+ steps:

```markdown
# /Plans/PLAN_[task]_[date].md
---
type: plan
status: in_progress
created: [timestamp]
source: [original file]
---

## Objective
[One sentence goal]

## Steps
- [ ] Step 1: [action]
- [ ] Step 2: [action]
- [ ] Step 3: [action]

## Completion Criteria
- [ ] All steps done
- [ ] Approvals obtained
- [ ] Moved to Done
```

#### D. Move to Done (When Complete)

After processing:
- Move original file to `Done/`
- Update Dashboard.md
- Log the action

### Step 3: Update Dashboard

Add to Recent Activity section:
```markdown
## Recent Activity
- [timestamp] Processed: [filename]
- [timestamp] Created approval: [filename]
- [timestamp] Completed: [filename]
```

---

## Examples

### Example 1: Email to New Client

**Input:** `Needs_Action/EMAIL_inquiry_new_client.md`

**Actions:**
1. Read email content
2. Identify as NEW contact → REQUIRES APPROVAL
3. Draft response
4. Create `Pending_Approval/EMAIL_response_new_client.md`
5. Move original to `Done/`

### Example 2: Invoice Payment Request

**Input:** `Needs_Action/EMAIL_invoice_payment.md`

**Actions:**
1. Read invoice details
2. Identify as PAYMENT → REQUIRES APPROVAL
3. Extract amount, recipient, invoice #
4. Create `Pending_Approval/PAYMENT_invoice_123.md`
5. Move original to `Done/`

### Example 3: Simple File Processing

**Input:** `Needs_Action/FILE_summary_request.md`

**Actions:**
1. Read file content
2. Identify as simple task (no approval needed)
3. Process the request
4. Create `Plans/PLAN_process_file.md` (if 3+ steps)
5. Move to `Done/` after completion

---

## NEVER DO

- ❌ Never send emails without approval for new contacts
- ❌ Never process payments without approval
- ❌ Never delete files without approval
- ❌ Never skip creating Pending_Approval when required

## ALWAYS DO

- ✅ Always check Company_Handbook rules
- ✅ Always create Pending_Approval for sensitive actions
- ✅ Always create Plans for multi-step tasks
- ✅ Always log actions
- ✅ Always update Dashboard

---

## Quick Reference

| Action Type | Approval Required? | Create Plan If |
|-------------|-------------------|----------------|
| Email to known contact | No | 3+ steps |
| Email to NEW contact | **YES** | Always |
| Payment (any amount) | **YES** | Always |
| Social media post | **YES** | Always |
| File create/read | No | 3+ steps |
| File delete | **YES** | Always |
| Calendar event | No | 3+ steps |
