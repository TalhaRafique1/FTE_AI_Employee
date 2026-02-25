# AI Employee - Bronze Tier

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

A Personal AI Employee built with Qwen Code and Obsidian that autonomously processes tasks, monitors inputs, and manages your digital affairs 24/7.

## 🏆 Bronze Tier Deliverables

This implementation completes all **Bronze Tier** requirements:

- ✅ Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- ✅ One working Watcher script (File System monitoring)
- ✅ Qwen Code integration for reading/writing to the vault
- ✅ Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- ✅ Agent Skill documentation for vault operations

## 📁 Project Structure

```
D:\FTE_AI_Employee\
├── AI_Employee_Vault/       # Obsidian vault (your AI's memory)
│   ├── Inbox/               # Drop folder for new files
│   ├── Needs_Action/        # Items awaiting processing
│   ├── Plans/               # Multi-step task plans
│   ├── Pending_Approval/    # Awaiting human approval
│   ├── Approved/            # Approved actions ready to execute
│   ├── Done/                # Completed tasks
│   ├── Rejected/            # Rejected items
│   ├── Logs/                # Activity logs
│   ├── Dashboard.md         # Real-time status dashboard
│   ├── Company_Handbook.md  # Rules of engagement
│   └── Business_Goals.md    # Objectives and metrics
│
├── watchers/
│   ├── base_watcher.py      # Abstract base class for all watchers
│   └── filesystem_watcher.py # File system monitoring implementation
│
├── skills/
│   └── vault-operations.md  # Agent Skill documentation
│
├── orchestrator.py          # Main coordination script
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |

### Installation

1. **Install Qwen Code:**
   ```bash
   # Follow Qwen Code installation instructions
   ```

2. **Verify Qwen Code:**
   ```bash
   qwen --version
   ```

3. **Open Obsidian Vault:**
   - Open Obsidian
   - Click "Open folder as vault"
   - Select `D:\FTE_AI_Employee\AI_Employee_Vault`

4. **Test Python Scripts:**
   ```bash
   cd D:\FTE_AI_Employee
   python --version  # Should be 3.13+
   ```

### Running the System

#### Option 1: File System Watcher (Continuous)

Monitors the `Inbox` folder for new files:

```bash
cd D:\FTE_AI_Employee
python watchers\filesystem_watcher.py
```

**What it does:**
- Watches `AI_Employee_Vault/Inbox/` for new files
- When a file is dropped, creates an action file in `Needs_Action/`
- Runs continuously until you press `Ctrl+C`

#### Option 2: Orchestrator (Single Run)

Processes all pending items:

```bash
cd D:\FTE_AI_Employee
python orchestrator.py
```

**What it does:**
- Reads all `.md` files in `Needs_Action/`
- Invokes Qwen Code to process items
- Creates plans, requests approvals, moves files to `Done`
- Updates `Dashboard.md`

#### Option 3: Orchestrator (Continuous Mode)

Runs processing cycles at regular intervals:

```bash
cd D:\FTE_AI_Employee
python orchestrator.py --continuous --interval 60
```

**What it does:**
- Runs a processing cycle every 60 seconds
- Automatically updates dashboard
- Press `Ctrl+C` to stop

#### Option 4: Manual Qwen Code

Direct interaction with the vault:

```bash
cd D:\FTE_AI_Employee\AI_Employee_Vault
qwen -p "Process all files in Needs_Action folder and create plans for each"
```

## 📖 Usage Guide

### Processing a File Drop

1. **Drop a file** in the Inbox:
   ```
   D:\FTE_AI_Employee\AI_Employee_Vault\Inbox\meeting_notes.txt
   ```

2. **Filesystem Watcher detects it** and creates:
   ```
   Needs_Action/FILE_meeting_notes_20260225_120000.md
   ```

3. **Orchestrator triggers Qwen Code** to:
   - Read the action file
   - Understand the content
   - Create a plan or take action
   - Move to `Done/` when complete

4. **Dashboard updates** with activity summary

### Creating an Approval Request

When Qwen detects a sensitive action needed:

1. **Qwen creates:**
   ```
   Pending_Approval/APPROVAL_payment_client_2026-02-25.md
   ```

2. **You review** the request in Obsidian

3. **To approve:** Move file to `Approved/`

4. **To reject:** Move file to `Rejected/` or add comments

5. **Orchestrator executes** approved actions on next cycle

### Viewing Activity Logs

```bash
# View today's orchestrator log
type AI_Employee_Vault\Logs\orchestrator_2026-02-25.log

# View watcher logs
type AI_Employee_Vault\Logs\watcher_2026-02-25.log
```

## 🧪 Testing the Bronze Tier

### Test 1: File Drop Processing

1. **Start the watcher** (in one terminal):
   ```bash
   python watchers\filesystem_watcher.py
   ```

2. **Create a test file** (in another terminal):
   ```bash
   echo "Please summarize this document and extract action items" > AI_Employee_Vault\Inbox\test_document.txt
   ```

3. **Watch the magic:**
   - Watcher log shows file detected
   - Action file created in `Needs_Action/`
   - File moved from `Inbox/` to `FileStorage/`

4. **Run the orchestrator:**
   ```bash
   python orchestrator.py
   ```

5. **Check results:**
   - Plan created in `Plans/` (by Qwen Code)
   - Dashboard updated
   - File moved to `Done/`

### Test 2: Direct Qwen Code

```bash
cd AI_Employee_Vault
qwen -p "Read Company_Handbook.md and summarize the rules for financial actions"
```

### Test 3: Dashboard Update

```bash
python orchestrator.py
type AI_Employee_Vault\Dashboard.md
```

## 📋 Configuration

### Customizing Watcher Settings

Edit `watchers\filesystem_watcher.py`:

```python
# Change check interval (default: 30 seconds)
watcher = FilesystemWatcher(vault_path, check_interval=60)

# Use custom drop folder
watcher = FilesystemWatcher(vault_path, drop_folder="D:\Custom\Drop\Folder")
```

### Customizing Orchestrator

```bash
# Run with custom vault path
python orchestrator.py --vault "D:\Custom\Vault"

# Dry run (log without executing)
python orchestrator.py --dry-run

# Continuous mode with 5-minute intervals
python orchestrator.py --continuous --interval 300
```

### Company Handbook Rules

Edit `AI_Employee_Vault\Company_Handbook.md` to customize:
- Approval thresholds
- Contact priority levels
- Communication guidelines
- Security rules

## 🔒 Security Best Practices

1. **Never commit credentials** - Use environment variables
2. **Enable audit logging** - All actions logged to `/Logs`
3. **Review approvals daily** - Check `Pending_Approval/` regularly
4. **Rotate secrets monthly** - Update any API keys periodically
5. **Backup your vault** - Use Git or cloud sync

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `qwen: command not found` | Install Qwen Code following official instructions |
| Watcher not detecting files | Check file permissions, ensure folder exists |
| Qwen Code timeout | Reduce file count or increase timeout in `orchestrator.py` |
| Dashboard not updating | Check write permissions on `Dashboard.md` |
| Python version error | Upgrade to Python 3.13+ |

## 📚 Learning Resources

- [Qwen Code Documentation](https://github.com/QwenLM/Qwen)
- [Obsidian Help](https://help.obsidian.md)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

## 🎯 Next Steps (Silver Tier)

After mastering Bronze tier, consider adding:

1. **Gmail Watcher** - Monitor email for urgent messages
2. **MCP Integration** - Connect to external services
3. **Approval Workflow** - Human-in-the-loop for sensitive actions
4. **Scheduled Tasks** - Cron-based daily briefings
5. **Plan.md Creation** - Multi-step task reasoning

## 📄 License

This project is part of the Personal AI Employee Hackathon 0.

---

**Built with ❤️ by the AI Employee Community**

*Version: 0.1 (Bronze Tier) | Last Updated: 2026-02-25*
