# How to Use Qwen Code with AI Employee

## ✅ Correct Commands

### **Option 1: Use the Batch File (Easiest)**

```bash
cd D:\FTE_AI_Employee
process_with_qwen.bat
```

This will:
- Check for files in Needs_Action
- Run Qwen Code with the correct prompt
- Guide you through the process

---

### **Option 2: Run Qwen Code Directly**

```bash
cd D:\FTE_AI_Employee\AI_Employee_Vault

# Interactive mode (recommended)
qwen -i -p "Process all files in Needs_Action folder. Read Company_Handbook.md first. Create Pending_Approval for payments and new contacts."

# Or one-shot mode
qwen "Process all files in Needs_Action folder"
```

---

### **Option 3: Use Orchestrator**

```bash
cd D:\FTE_AI_Employee
python orchestrator.py
```

This will:
- Count pending items
- Build proper prompt for Qwen Code
- Run Qwen Code automatically
- Update Dashboard

---

## ❌ Wrong Commands (Don't Use)

```bash
# This doesn't exist:
qwen -p "..." --continuous-until-done  ❌

# This doesn't exist:
qwen -p "..." --ralph-loop  ❌
```

---

## 📋 Expected Workflow

### **1. Email Arrives**

Gmail Watcher creates:
```
Needs_Action/EMAIL_client_inquiry.md
```

### **2. Run Qwen Code**

```bash
python orchestrator.py
```

### **3. Qwen Code Creates:**

**For new contact emails:**
```
Pending_Approval/EMAIL_response_client.md
```

**For multi-step tasks:**
```
Plans/PLAN_process_inquiry.md
```

**After processing:**
```
Done/EMAIL_client_inquiry.md
```

### **4. You Review**

Check `Pending_Approval/` folder for items needing your approval.

### **5. Approve or Reject**

```bash
# To approve - move to Approved/
move Pending_Approval\*.md Approved\

# To reject - move to Rejected/
move Pending_Approval\*.md Rejected\
```

---

## 🎯 Qwen Code Will Create Pending_Approval When:

| Action | Creates Approval? |
|--------|------------------|
| Email to NEW contact | ✅ YES |
| Email to KNOWN contact | ❌ NO (can draft directly) |
| Payment (any amount) | ✅ YES |
| Social media post | ✅ YES |
| File delete | ✅ YES |
| File create/read | ❌ NO (safe) |
| Calendar event | ❌ NO (unless >$100) |

---

## 📝 Example Session

```bash
# Start processing
D:\FTE_AI_Employee> python orchestrator.py

2026-02-26 15:00:00 - Starting processing run
2026-02-26 15:00:00 - Needs Action: 2, Pending Approval: 0, Approved: 0
2026-02-26 15:00:00 - Invoking Qwen Code...

# Qwen Code runs and:
# - Reads Company_Handbook.md
# - Processes Needs_Action files
# - Creates Pending_Approval for new contacts
# - Creates Plans for multi-step tasks
# - Moves completed to Done

2026-02-26 15:02:00 - Qwen Code processing completed
2026-02-26 15:02:00 - Dashboard updated

# Check results
D:\FTE_AI_Employee> dir AI_Employee_Vault\Pending_Approval

# If items need approval, review and approve
D:\FTE_AI_Employee> move AI_Employee_Vault\Pending_Approval\*.md AI_Employee_Vault\Approved\
```

---

## 🔧 Troubleshooting

### Issue: "Qwen doesn't create Pending_Approval"

**Solution:**
1. Make sure Company_Handbook.md exists
2. Use the updated orchestrator (has better prompt)
3. Run: `process_with_qwen.bat` (has explicit instructions)

### Issue: "Qwen only creates Plans"

**Solution:**
- Plans are for multi-step tasks
- Pending_Approval is for sensitive actions
- Both can be created for the same item

### Issue: "Nothing happens"

**Solution:**
```bash
# Check if Needs_Action has files
dir AI_Employee_Vault\Needs_Action\*.md

# If empty, no files to process
# Drop a test file:
echo "Test content" > AI_Employee_Vault\Inbox\test.txt

# Wait for watcher to create action file
# Then run orchestrator
python orchestrator.py
```

---

## ✅ Quick Reference

| Command | Use When |
|---------|----------|
| `process_with_qwen.bat` | **Recommended - easiest** |
| `python orchestrator.py` | Automated processing |
| `qwen -i -p "..."` | Manual interactive mode |
| `qwen "..."` | Quick one-shot |

---

**Your AI Employee is working correctly!** 

- ✅ Plans are created for multi-step tasks
- ✅ Pending_Approval created for sensitive actions
- ✅ Done folder for completed items

**Use `process_with_qwen.bat` for best results!**
