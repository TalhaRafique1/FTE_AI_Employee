---
name: plan-creation
description: |
  Plan creation and reasoning skill for multi-step tasks.
  Creates structured Plan.md files with checkboxes, tracks progress,
  and ensures tasks are completed systematically.
---

# Plan Creation Agent Skill (Silver Tier)

This skill enables the AI Employee to break down complex tasks into manageable steps using Plan.md files.

## Overview

The Plan Creation skill provides:
- Analyze tasks and determine complexity
- Create structured Plan.md files
- Track progress with checkboxes
- Link related documents
- Update status as work progresses

## When to Create a Plan

Create a Plan.md when a task requires:
- **Multiple steps** (3 or more actions)
- **External dependencies** (waiting for responses, approvals)
- **Research needed** (gathering information before action)
- **Approval required** (sensitive actions needing human review)
- **Time-sensitive** (deadlines to track)

## Plan.md Schema

```markdown
# /Plans/PLAN_[task_description]_[YYYY-MM-DD].md
---
type: plan
status: in_progress
created: <ISO_timestamp>
updated: <ISO_timestamp>
due: <ISO_timestamp>
priority: <low|normal|high|urgent>
source: <source_action_file>
tags:
  - <tag1>
  - <tag2>
---

# Plan: [Clear Task Description]

## Objective
[One sentence describing what success looks like]

## Context
[Background information, why this task exists]

## Steps

- [ ] Step 1: [Actionable description]
  - Notes: _Optional notes_
  - Status: pending
  
- [ ] Step 2: [Actionable description]
  - Notes: _Optional notes_
  - Status: pending
  
- [ ] Step 3: [Actionable description]
  - Notes: _Optional notes_
  - Status: pending

## Dependencies
- [ ] Waiting on: [What/who we're waiting for]

## Resources
- [[Related Document 1]]
- [[Related Document 2]]
- [External Link](url)

## Notes
[Any observations, decisions, or context]

## Completion Criteria
- [ ] All steps completed
- [ ] Required approvals obtained
- [ ] Results verified
- [ ] Files moved to /Done

---
*Last Updated: <ISO_timestamp>*
```

## Example Plans

### Invoice Processing Plan

```markdown
# /Plans/PLAN_process_invoice_request_2026-02-25.md
---
type: plan
status: in_progress
created: 2026-02-25T10:30:00Z
updated: 2026-02-25T10:30:00Z
priority: high
source: Needs_Action/WHATSAPP_client_invoice_request.md
tags:
  - invoice
  - client
  - billing
---

# Plan: Process Invoice Request for Client A

## Objective
Generate and send invoice for January 2026 services to Client A.

## Context
Client A sent WhatsApp message requesting invoice for completed work.
Total amount: $1,500 for 10 hours of consulting at $150/hr.

## Steps

- [x] Step 1: Identify client and verify details
  - Notes: Client A - client_a@email.com, contract verified
  
- [x] Step 2: Calculate amount from records
  - Notes: 10 hours × $150/hr = $1,500
  
- [ ] Step 3: Generate invoice PDF
  - Notes: Use template in /Vault/Templates/invoice_template.md
  - Status: pending
  
- [ ] Step 4: Create approval request for email send
  - Notes: First-time invoice, requires approval
  - Status: pending
  
- [ ] Step 5: Send invoice via email
  - Notes: Waiting for approval
  - Status: pending
  
- [ ] Step 6: Log transaction in accounting
  - Notes: Update /Vault/Accounting/2026-02.md
  - Status: pending

## Dependencies
- [ ] Human approval for email send

## Resources
- [[Company_Handbook]] - Payment rules
- /Vault/Templates/invoice_template.md
- /Vault/Accounting/rates.md

## Notes
- Client is VIP, prioritize this task
- Payment terms: Net 30

## Completion Criteria
- [x] All steps completed
- [ ] Required approvals obtained
- [ ] Invoice sent and logged
- [ ] Files moved to /Done

---
*Last Updated: 2026-02-25T10:30:00Z*
```

### Email Response Plan

```markdown
# /Plans/PLAN_respond_to_inquiry_2026-02-25.md
---
type: plan
status: pending
created: 2026-02-25T11:00:00Z
updated: 2026-02-25T11:00:00Z
priority: normal
source: Needs_Action/EMAIL_sales_inquiry.md
tags:
  - email
  - sales
  - response
---

# Plan: Respond to Sales Inquiry

## Objective
Draft and send professional response to sales inquiry.

## Context
Received inquiry from potential client about AI Employee services.
Need to provide information and schedule demo call.

## Steps

- [x] Step 1: Read and understand inquiry
  - Notes: Interested in automation for customer support
  
- [x] Step 2: Research sender/company
  - Notes: Tech startup, 50 employees, good fit
  
- [ ] Step 3: Draft response email
  - Notes: Include service overview, pricing, demo offer
  - Status: pending
  
- [ ] Step 4: Review against Company_Handbook
  - Notes: Ensure tone and content align with guidelines
  - Status: pending
  
- [ ] Step 5: Create approval request
  - Notes: New contact, requires approval
  - Status: pending
  
- [ ] Step 6: Send email after approval
  - Status: pending

## Dependencies
- [ ] Approval for sending to new contact

## Resources
- [[Company_Handbook]] - Communication guidelines
- /Vault/Templates/sales_response.md

## Notes
- Hot lead, respond within 2 hours
- Offer 30-min demo call

---
*Last Updated: 2026-02-25T11:00:00Z*
```

### Social Media Post Plan

```markdown
# /Plans/PLAN_linkedin_post_2026-02-25.md
---
type: plan
status: in_progress
created: 2026-02-25T09:00:00Z
updated: 2026-02-25T09:15:00Z
priority: low
source: Business_Goals.md
tags:
  - social_media
  - linkedin
  - marketing
---

# Plan: Create and Schedule LinkedIn Post

## Objective
Create engaging LinkedIn post about AI Employee launch.

## Context
Part of Q1 marketing goals to increase social media presence.
Target: 500+ impressions, 20+ engagements.

## Steps

- [x] Step 1: Determine post topic
  - Notes: AI Employee service launch announcement
  
- [x] Step 2: Draft post content
  - Notes: Created draft in /Vault/Social/DRAFT_linkedin_2026-02-25.md
  
- [x] Step 3: Create/select image
  - Notes: launch_announcement.png created
  
- [ ] Step 4: Review content quality
  - Notes: Check tone, hashtags, length
  - Status: pending
  
- [ ] Step 5: Create approval request
  - Notes: All posts require approval
  - Status: pending
  
- [ ] Step 6: Schedule post
  - Notes: Target Tuesday 9:00 AM
  - Status: pending

## Dependencies
- [ ] Human approval before scheduling

## Resources
- [[Business_Goals]] - Q1 marketing objectives
- /Vault/Social/content_calendar_2026-02.md

## Notes
- Best posting time: Tuesday 9:00 AM
- Use 3-5 hashtags

---
*Last Updated: 2026-02-25T09:15:00Z*
```

## Reasoning Process

### Step 1: Analyze Task

```python
def should_create_plan(action_file) -> bool:
    """Determine if a task needs a plan."""
    content = action_file.read_text()
    
    # Check for multi-step indicators
    multi_step_keywords = ['invoice', 'payment', 'response', 'schedule', 'create']
    complex_keywords = ['approval', 'multiple', 'coordinate', 'research']
    
    # Count required actions
    action_count = count_required_actions(content)
    
    # Check if approval needed
    needs_approval = check_approval_required(content)
    
    # Create plan if:
    # - More than 2 steps required
    # - Approval needed
    # - Complex task detected
    return action_count > 2 or needs_approval or has_complex_keywords(content)
```

### Step 2: Break Down Steps

```python
def break_down_steps(task_type: str) -> List[dict]:
    """Generate steps based on task type."""
    
    step_templates = {
        'invoice': [
            {'action': 'Identify client', 'type': 'research'},
            {'action': 'Calculate amount', 'type': 'calculation'},
            {'action': 'Generate invoice', 'type': 'create'},
            {'action': 'Request approval', 'type': 'approval'},
            {'action': 'Send invoice', 'type': 'action'},
            {'action': 'Log transaction', 'type': 'record'}
        ],
        'email_response': [
            {'action': 'Read inquiry', 'type': 'research'},
            {'action': 'Research sender', 'type': 'research'},
            {'action': 'Draft response', 'type': 'create'},
            {'action': 'Review guidelines', 'type': 'verify'},
            {'action': 'Request approval', 'type': 'approval'},
            {'action': 'Send email', 'type': 'action'}
        ],
        'social_post': [
            {'action': 'Determine topic', 'type': 'planning'},
            {'action': 'Draft content', 'type': 'create'},
            {'action': 'Create image', 'type': 'create'},
            {'action': 'Review quality', 'type': 'verify'},
            {'action': 'Request approval', 'type': 'approval'},
            {'action': 'Schedule post', 'type': 'action'}
        ]
    }
    
    return step_templates.get(task_type, [])
```

### Step 3: Track Progress

```python
def update_plan_status(plan_path: Path, step_index: int, status: str):
    """Update the status of a step in the plan."""
    content = plan_path.read_text()
    
    # Update checkbox
    if status == 'completed':
        content = content.replace(
            f'- [ ] Step {step_index + 1}:',
            f'- [x] Step {step_index + 1}:'
        )
    elif status == 'in_progress':
        content = content.replace(
            f'Status: pending',
            f'Status: in_progress',
            step_index
        )
    
    # Update timestamp
    content = content.replace(
        '*Last Updated:*',
        f'*Last Updated: {datetime.now().isoformat()}*'
    )
    
    plan_path.write_text(content)
```

## Status Values

| Status | Description | Action |
|--------|-------------|--------|
| `pending` | Not started | Wait for turn |
| `in_progress` | Currently working | AI actively processing |
| `blocked` | Waiting on dependency | Note what's blocking |
| `completed` | Step finished | Check the box |
| `skipped` | Not needed | Document why |

## Integration with Orchestrator

```python
# In orchestrator.py

def process_with_planning(self):
    """Process items that need planning."""
    
    for action_file in self.needs_action.glob('*.md'):
        # Determine if plan needed
        if self.should_create_plan(action_file):
            # Create plan
            plan_path = self.create_plan(action_file)
            
            # Process steps iteratively
            while not self.is_plan_complete(plan_path):
                next_step = self.get_next_step(plan_path)
                self.execute_step(next_step, plan_path)
                
                # Check if approval needed
                if self.step_requires_approval(next_step):
                    self.create_approval_request(next_step, plan_path)
                    break  # Wait for approval
            
            # Move to done when complete
            if self.is_plan_complete(plan_path):
                self.complete_plan(plan_path, action_file)
```

## Best Practices

1. **Clear objectives** - One sentence, measurable outcome
2. **Actionable steps** - Start with verbs, specific actions
3. **Track everything** - Update status as you go
4. **Link documents** - Use [[wikilinks]] for related files
5. **Note decisions** - Document why choices were made
6. **Review regularly** - Check stalled plans daily

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plan not progressing | Check for blocked dependencies |
| Too many steps | Break into sub-plans |
| Steps unclear | Rewrite with specific actions |
| Plan abandoned | Review and update or close |

---

*Version: 0.2 (Silver Tier)*
*Last Updated: 2026-02-25*
