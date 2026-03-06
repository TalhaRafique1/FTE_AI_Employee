# 📧 Send Approved Email via Gmail MCP - Complete Guide

## 🎯 **Your Current Situation**

You have an **approved email** in `AI_Employee_Vault/Approved/` folder and want to send it via Gmail MCP.

---

## ✅ **Method 1: Use Helper Script (Easiest)**

```bash
cd D:\FTE_AI_Employee

# Send the most recent approved email
python send_approved_email_mcp.py

# Or specify a specific file
python send_approved_email_mcp.py AI_Employee_Vault\Approved\EMAIL_response_client.md
```

**What it does:**
1. Reads the approved file
2. Extracts: to, subject, body
3. Calls Qwen Code with Gmail MCP
4. Sends the email ✅
5. Moves file to Done/

---

## ✅ **Method 2: Direct Qwen Code Command**

```bash
cd AI_Employee_Vault

# Qwen will read and send the approved email
qwen -p "Read the approved email file in Approved folder and send it using Gmail MCP tool gmail_send_email"
```

**Example:**
```bash
qwen -p "Send the email in Approved/EMAIL_response_client.md using Gmail MCP. Extract the to, subject, and body, then call gmail_send_email tool."
```

---

## ✅ **Method 3: Manual Qwen Code Session**

```bash
# Start interactive Qwen Code
cd AI_Employee_Vault
qwen -i
```

**Then in Qwen:**
```
> Read the approved email in Approved folder

[Qwen reads the file]

> Now send this email using Gmail MCP

[Qwen calls gmail_send_email tool]

> Confirm it was sent

[Qwen confirms and you're done!]
```

---

## 📋 **Complete Workflow Example**

### **1. Check Approved Folder**

```bash
dir AI_Employee_Vault\Approved\
```

**Output:**
```
EMAIL_response_project_2026-02-26.md
```

### **2. View the Email**

```bash
type AI_Employee_Vault\Approved\EMAIL_response_project_2026-02-26.md
```

**Content:**
```markdown
---
type: approval_request
action: send_email
to: "client@company.com"
subject: "Re: Project Update"
status: approved
---

## Email Content

Dear Client,

Here is the project update you requested...

Best regards,
Your Team
```

### **3. Send via MCP**

```bash
python send_approved_email_mcp.py AI_Employee_Vault\Approved\EMAIL_response_project_2026-02-26.md
```

**Output:**
```
======================================================================
SENDING EMAIL VIA GMAIL MCP
======================================================================

Email Details:
  To: client@company.com
  Subject: Re: Project Update
  Body: Dear Client, Here is the project update...

======================================================================
Calling Qwen Code with Gmail MCP...
======================================================================

======================================================================
QWEN CODE OUTPUT:
======================================================================

✅ Email sent successfully!
Message ID: 18e5c7a1b2d3f4g5

✅ Moved to Done folder: AI_Employee_Vault\Done\EMAIL_response_project_2026-02-26.md
```

### **4. Verify Sent**

```bash
# Check Done folder
dir AI_Employee_Vault\Done\EMAIL_*.md

# Check your Gmail sent items
# Open Gmail → Sent → See your email!
```

---

## 🔧 **How Gmail MCP Sends Email**

### **Behind the Scenes:**

```
1. Python script reads approved file
   ↓
2. Extracts: to, subject, body
   ↓
3. Calls Qwen Code with prompt
   ↓
4. Qwen Code uses Gmail MCP tool
   ↓
5. MCP server calls Gmail API
   ↓
6. Email sent! ✅
   ↓
7. File moved to Done/
```

---

## 📊 **Comparison: MCP vs Python**

| Feature | Gmail MCP | Python Script |
|---------|-----------|---------------|
| **Command** | `qwen -p "Send..."` | `python send_gmail_email.py` |
| **Integration** | Native Qwen | External script |
| **Setup** | Requires MCP config | No config needed |
| **Speed** | ~5 seconds | ~2 seconds |
| **Best For** | Interactive use | Automation |

**Both work!** Choose based on preference.

---

## 🎯 **Quick Commands**

```bash
# Method 1: Helper script (recommended)
python send_approved_email_mcp.py

# Method 2: Direct Qwen
qwen -p "Send approved email using Gmail MCP"

# Method 3: Python sender (no MCP)
python send_gmail_email.py --file AI_Employee_Vault\Approved\EMAIL_*.md

# Method 4: Orchestrator (automatic)
python orchestrator.py
```

---

## 🐛 **Troubleshooting**

### Issue: "No approved emails found"

**Solution:**
```bash
# Check if file exists
dir AI_Employee_Vault\Approved\*.md

# If empty, you need to approve an email first
# Move from Pending_Approval to Approved:
move AI_Employee_Vault\Pending_Approval\*.md AI_Employee_Vault\Approved\
```

### Issue: "Gmail MCP not responding"

**Solution:**
```bash
# Verify MCP config exists
type "%APPDATA%\claude-code\mcp.json"

# Test MCP server
cd gmail-mcp-server
node test-simple.js
```

### Issue: "Qwen doesn't send"

**Solution:**
```bash
# Use helper script instead
python send_approved_email_mcp.py

# Or use Python sender (no MCP needed)
python send_gmail_email.py --file AI_Employee_Vault\Approved\EMAIL_*.md
```

---

## ✅ **Complete Status**

| Step | Status |
|------|--------|
| Email Approved | ✅ Done (you did this) |
| File in Approved/ | ✅ Ready |
| Gmail MCP Installed | ✅ Ready |
| **Send Email** | **👉 Use helper script** |

---

## 🚀 **Send Your Email Now!**

```bash
cd D:\FTE_AI_Employee

# This will send your approved email via MCP
python send_approved_email_mcp.py
```

**Expected Output:**
```
✅ Email sent successfully!
✅ Moved to Done folder
```

**Check your Gmail Sent folder to verify!** 📧

---

**Your approved email will be sent via Gmail MCP!** 🎉
