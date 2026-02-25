# FTE AI Employee Project

## Project Overview

This is a **Personal AI Employee** hackathon project focused on building an autonomous "Digital FTE" (Full-Time Equivalent) that operates 24/7 to manage personal and business affairs. The architecture follows a **local-first, agent-driven, human-in-the-loop** approach.

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Qwen Code | Reasoning engine for decision-making and task execution |
| **Memory/GUI** | Obsidian (Markdown) | Dashboard, knowledge base, and long-term memory |
| **Senses** | Python Watcher Scripts | Monitor Gmail, WhatsApp, filesystems to trigger AI actions |
| **Hands** | MCP Servers | Model Context Protocol for external system interactions |

### Key Concepts

- **Watcher Pattern**: Lightweight Python scripts continuously monitor inputs (email, messaging, files) and create actionable `.md` files in `/Needs_Action` folders
- **Ralph Wiggum Loop**: A persistence pattern using stop hooks to keep the agent iterating until multi-step tasks are complete
- **Human-in-the-Loop**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Business Handover**: Autonomous weekly audits generating "Monday Morning CEO Briefing" reports

## Directory Structure

```
D:\FTE_AI_Employee\
├── .qwen/skills/              # Qwen skill configurations
│   └── browsing-with-playwright/
│       ├── SKILL.md           # Browser automation skill documentation
│       ├── scripts/           # MCP server management scripts
│       └── references/        # Tool reference documentation
├── Personal AI Employee Hackathon 0_*.md  # Main hackathon blueprint (1201 lines)
├── skills-lock.json           # Skill version tracking
└── QWEN.md                    # This file
```

## Key Files

| File | Description |
|------|-------------|
| `Personal AI Employee Hackathon 0_*.md` | Comprehensive architectural blueprint with tiered deliverables (Bronze/Silver/Gold/Platinum), implementation templates, and code examples |
| `.qwen/skills/browsing-with-playwright/SKILL.md` | Browser automation skill using Playwright MCP |
| `skills-lock.json` | Tracks installed skill versions and sources |

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Qwen Code | Latest | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers & automation |

### Running the AI Employee

**Process pending items with Qwen Code:**
```bash
cd D:\FTE_AI_Employee
python orchestrator.py
```

**Run in continuous mode:**
```bash
python orchestrator.py --continuous --interval 60
```

**Direct Qwen Code interaction:**
```bash
cd AI_Employee_Vault
qwen -p "Process all files in Needs_Action"
```

## Development Conventions

### Folder Structure (Obsidian Vault)

```
/Vault/
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Items requiring processing
├── In_Progress/<agent>/ # Claimed tasks (prevents double-work)
├── Pending_Approval/   # Awaiting human approval
├── Approved/           # Approved actions ready for execution
├── Done/               # Completed tasks
├── Plans/              # Multi-step task plans (Plan.md)
├── Briefings/          # CEO briefing reports
├── Business_Goals.md   # Objectives and metrics
└── Company_Handbook.md # Rules of engagement
```

### Agent Skills

All AI functionality should be implemented as Agent Skills following the pattern in `.qwen/skills/browsing-with-playwright/SKILL.md`.

### MCP Tool Usage

Use the Playwright MCP tools via `mcp-client.py`:
```bash
python3 scripts/mcp-client.py call -u http://localhost:8808 -t <tool_name> -p '<json_params>'
```

Available tools: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_fill_form`, `browser_take_screenshot`, `browser_evaluate`, `browser_run_code`, etc.

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12h | Obsidian dashboard, 1 watcher, basic folder structure |
| **Silver** | 20-30h | Multiple watchers, MCP integration, approval workflow |
| **Gold** | 40+h | Full integration, Odoo accounting, social media, Ralph Wiggum loop |
| **Platinum** | 60+h | Cloud deployment, domain specialization, A2A sync |

## Resources

- **Weekly Meetings**: Wednesdays 10:00 PM PKT on Zoom (starting Jan 7, 2026)
- **YouTube**: [@panaversity](https://www.youtube.com/@panaversity)
- **Qwen Code**: https://github.com/QwenLM/Qwen
- **Ralph Wiggum Reference**: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
