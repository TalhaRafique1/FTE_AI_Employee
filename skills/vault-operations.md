---
name: vault-operations
description: |
  File system operations for the AI Employee Obsidian vault.
  Read, write, move, and organize markdown files for task processing.
  Use for managing Needs_Action, Plans, Done, and approval workflows.
---

# Vault Operations Agent Skill

This skill provides file system operations specifically for the AI Employee vault workflow.

## Overview

The Vault Operations skill enables Claude Code to:
- Read pending action files from `/Needs_Action`
- Create plan files in `/Plans`
- Move completed tasks to `/Done`
- Create approval requests in `/Pending_Approval`
- Update the Dashboard.md

## Installation

Add to your Claude Code configuration or invoke directly using the filesystem MCP.

## Usage Patterns

### Read Pending Items

```bash
# List all pending items
ls Needs_Action/*.md

# Read a specific action file
cat Needs_Action/FILE_example_20260225_120000.md
```

### Create a Plan

When a task requires multiple steps, create a plan file:

```markdown
# /Plans/PLAN_process_file_drop_2026-02-25.md
---
created: 2026-02-25T12:00:00Z
status: in_progress
source: Needs_Action/FILE_example_20260225_120000.md
---

## Objective
Process the dropped file and take appropriate action

## Steps
- [x] Read the file contents
- [ ] Categorize the file type
- [ ] Determine required action
- [ ] Execute action (or request approval)
- [ ] Move source file to /Done

## Notes
_Add observations here_
```

### Request Approval

For sensitive actions, create an approval request:

```markdown
# /Pending_Approval/APPROVAL_action_description_2026-02-25.md
---
type: approval_request
action: <action_type>
created: 2026-02-25T12:00:00Z
expires: 2026-02-26T12:00:00Z
status: pending
---

## Action Required
Describe what action needs approval

## Details
- **Item:** Relevant details
- **Reason:** Why this action is needed
- **Risk:** Any associated risks

## To Approve
Move this file to `/Approved` folder

## To Reject
Move this file to `/Rejected` folder or add comments
```

### Complete a Task

After processing, move files to Done:

```bash
# Move action file to Done
mv Needs_Action/FILE_example_20260225_120000.md Done/
mv Plans/PLAN_process_file_2026-02-25.md Done/
```

### Update Dashboard

After processing, update the dashboard summary:

```markdown
## Recent Activity
- [2026-02-25 12:30] Processed file drop: example.txt
- [2026-02-25 12:25] Created plan for multi-step task
- [2026-02-25 12:20] Requested approval for sensitive action
```

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Action File | `TYPE_identifier_TIMESTAMP.md` | `FILE_report_20260225_120000.md` |
| Plan | `PLAN_description_DATE.md` | `PLAN_process_invoice_2026-02-25.md` |
| Approval | `APPROVAL_action_description_DATE.md` | `APPROVAL_payment_client_a_2026-02-25.md` |
| Log | `component_YYYY-MM-DD.log` | `orchestrator_2026-02-25.log` |

## Workflow Example

1. **Watcher creates action file** in `/Needs_Action`
2. **Orchestrator triggers Claude** to process pending items
3. **Claude reads action file** and Company_Handbook.md for context
4. **Claude creates plan** in `/Plans` if multi-step
5. **Claude executes** or creates approval request
6. **Claude moves files** to `/Done` when complete
7. **Dashboard updated** with activity summary

## Best Practices

1. **Always log actions** - Every file movement should be logged
2. **Preserve original data** - Copy files, don't move, until processing is confirmed
3. **Use frontmatter** - Include type, status, and timestamps in YAML frontmatter
4. **Atomic operations** - Complete all steps or none (use plans for tracking)
5. **Human review** - When in doubt, create an approval request

## Error Handling

If processing fails:
1. Log the error in the file's notes section
2. Move to `/Needs_Action` with `status: error`
3. Add `error_message` to frontmatter
4. Continue with other items

## Security Considerations

- Never log sensitive data (passwords, API keys, PII)
- Redact financial information in logs
- Use environment variables for credentials
- Maintain audit trail in `/Logs`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| File not found | Check case sensitivity and path |
| Permission denied | Verify file isn't locked by another process |
| Duplicate names | Add timestamp or counter to filename |
| Processing stuck | Check for circular dependencies in plans |

---

*Version: 0.1 (Bronze Tier)*
*Last Updated: 2026-02-25*
