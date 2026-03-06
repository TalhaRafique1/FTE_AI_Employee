# 📧 Gmail MCP - Auto-Send Approved Emails

## 🎯 **How It Works**

```
1. Email approved (moved to Approved/ folder)
   ↓
2. Run MCP auto-send script
   ↓
3. Script finds all EMAIL_*.md files in Approved/
   ↓
4. Extracts: to, subject, body
   ↓
5. Sends via Gmail API (using MCP)
   ↓
6. Moves sent email to Done/ folder
   ↓
7. Email sent! ✅
```

---

## 🚀 **Quick Start**

### **Method 1: Use Batch File (Easiest)**

```bash
cd D:\FTE_AI_Employee
send_approved_emails.bat
```

### **Method 2: Run Directly**

```bash
cd D:\FTE_AI_Employee\gmail-mcp-server
node mcp-send-approved-emails.js
```

---

## 📋 **Complete Workflow**

### **Step 1: Approve Email**

```bash
# Move from Pending_Approval to Approved
move AI_Employee_Vault\Pending_Approval\EMAIL_response_client.md AI_Employee_Vault\Approved\
```

### **Step 2: Send via MCP**

```bash
cd D:\FTE_AI_Employee
send_approved_emails.bat
```

**What happens:**
```
============================================================
GMAIL MCP - AUTO-SEND APPROVED EMAILS
============================================================

📧 Found 1 approved email(s)

Processing: EMAIL_response_client_2026-02-26.md
  To: client@example.com
  Subject: Re: Project Inquiry
  Body: Dear Client, Thank you for your inquiry...

  ✅ Email sent! Message ID: 18e5c7a1b2d3f4g5
  ✅ Moved to Done folder

============================================================
SUMMARY
============================================================
Total: 1
Sent: 1
Failed: 0
============================================================
```

### **Step 3: Verify**

```bash
# Check Done folder
dir AI_Employee_Vault\Done\EMAIL_*.md

# Check Gmail Sent folder
# Open Gmail → Sent → See your email!
```

---

## 📁 **File Structure**

```
gmail-mcp-server/
├── mcp-send-approved-emails.js  ← Auto-send script
├── index.js                      ← MCP server
├── gmail_utils.js                ← Gmail utilities
└── package.json                  ← Dependencies
```

---

## 🎯 **Approved Email Format**

Your approved email file should look like:

```markdown
---
type: approval_request
action: send_email
to: "client@example.com"
subject: "Re: Project Inquiry"
created: 2026-02-26T15:00:00Z
status: approved
---

## Email Content

Dear Client,

Thank you for your inquiry. We'd be happy to help...

Best regards,
Your Team
```

**Required fields:**
- `to:` - Recipient email
- `subject:` - Email subject
- `## Email Content` - Email body

---

## 🔄 **Complete Workflow Example**

### **1. Email Arrives**

```
Gmail Watcher → Creates action file
Needs_Action/EMAIL_client_inquiry.md
```

### **2. Qwen Code Processes**

```bash
python orchestrator.py
```

**Creates:**
```
Pending_Approval/EMAIL_response_client.md
```

### **3. You Approve**

```bash
move Pending_Approval\EMAIL_*.md Approved\
```

### **4. MCP Sends Email**

```bash
send_approved_emails.bat
```

**Output:**
```
📧 Found 1 approved email(s)

Processing: EMAIL_response_client.md
  To: client@example.com
  Subject: Re: Project Inquiry
  
  ✅ Email sent! Message ID: 18e5c7a1b2d3f4g5
  ✅ Moved to Done folder
```

### **5. Verify**

- Check console for success message
- Check Gmail Sent folder
- Check file moved to Done/

---

## ⚙️ **Configuration**

### **Credentials Location:**

```
D:\FTE_AI_Employee\credentials.json
```

### **Token Location:**

```
%USERPROFILE%\.ai_employee\gmail_token.json
```

### **Vault Paths:**

```javascript
VAULT_PATH = "D:\FTE_AI_Employee\AI_Employee_Vault"
APPROVED_PATH = "VAULT_PATH\Approved"
DONE_PATH = "VAULT_PATH\Done"
```

---

## 🐛 **Troubleshooting**

### Issue: "No approved emails found"

**Solution:**
```bash
# Check if files exist
dir AI_Employee_Vault\Approved\EMAIL_*.md

# If empty, approve an email first
move AI_Employee_Vault\Pending_Approval\*.md AI_Employee_Vault\Approved\
```

### Issue: "Credentials not found"

**Solution:**
```bash
# Verify credentials.json exists
dir D:\FTE_AI_Employee\credentials.json

# If missing, download from Google Cloud Console
```

### Issue: "Authentication failed"

**Solution:**
```bash
# Delete token and re-authenticate
del "%USERPROFILE%\.ai_employee\gmail_token.json"

# Run script again - will authenticate
send_approved_emails.bat
```

---

## 📊 **Comparison: MCP vs Python**

| Feature | MCP Auto-Send | Python Sender |
|---------|---------------|---------------|
| **Command** | `send_approved_emails.bat` | `send_gmail_email.py` |
| **Language** | Node.js | Python |
| **Integration** | Native MCP | Direct API |
| **Batch Send** | ✅ Yes | ✅ Yes |
| **Auto Move** | ✅ Yes | ✅ Yes |
| **Speed** | ~2 sec/email | ~1 sec/email |

**Both work!** Use whichever you prefer.

---

## ✅ **Quick Reference**

```bash
# Send all approved emails
send_approved_emails.bat

# Or run directly
cd gmail-mcp-server
node mcp-send-approved-emails.js

# Check approved folder
dir AI_Employee_Vault\Approved\EMAIL_*.md

# Check done folder
dir AI_Employee_Vault\Done\EMAIL_*.md
```

---

## 🎉 **Your Complete Email System**

**Now you have 3 ways to send approved emails:**

| Method | Command | When to Use |
|--------|---------|-------------|
| **MCP Auto-Send** | `send_approved_emails.bat` | ✅ Recommended - batch send |
| **Python Sender** | `python send_gmail_email.py` | Single email |
| **Orchestrator** | `python orchestrator.py` | Automated workflow |

**All methods work!** Choose based on your needs.

---

## 🧪 **Test It Now**

```bash
# 1. Create test approved email
echo ---
type: approval_request
action: send_email
to: "your-email@gmail.com"
subject: "MCP Auto-Send Test"
status: approved
---

## Email Content

This email was sent via Gmail MCP auto-send!

If you receive this, MCP auto-send is working!

Best,
AI Employee
> AI_Employee_Vault\Approved\EMAIL_test_mcp_auto.md

# 2. Send it
send_approved_emails.bat

# 3. Check your Gmail!
```

---

**Gmail MCP Auto-Send is ready!** 🚀

**Run `send_approved_emails.bat` to send all approved emails!** 📧
