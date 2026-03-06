# Gmail MCP Server

Gmail integration for Qwen Code via Model Context Protocol (MCP).

## Features

- ✅ Send emails
- ✅ Read emails
- ✅ Mark emails as read
- ✅ Search emails
- ✅ OAuth2 authentication

## Installation

### Quick Install

```bash
cd D:\FTE_AI_Employee
install_gmail_mcp.bat
```

This will:
1. Install npm dependencies
2. Create MCP configuration
3. Test the installation

### Manual Install

```bash
cd gmail-mcp-server
npm install
```

## Configuration

The installer creates this config at `%APPDATA%\claude-code\mcp.json`:

```json
{
  "servers": {
    "gmail": {
      "command": "node",
      "args": ["D:/FTE_AI_Employee/gmail-mcp-server/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "D:/FTE_AI_Employee/credentials.json"
      }
    }
  }
}
```

## Usage with Qwen Code

### Send Email

```bash
qwen -p "Send an email to client@example.com with subject 'Meeting' and body 'Let's meet tomorrow at 2 PM'"
```

### Read Emails

```bash
qwen -p "Read my unread emails"
```

### Search Emails

```bash
qwen -p "Search for emails from boss@company.com"
```

## Available Tools

### gmail_send_email

Send an email via Gmail API.

**Parameters:**
- `to` (required): Recipient email address
- `subject` (required): Email subject
- `body` (required): Email body text
- `attachment` (optional): Attachment file path

**Example:**
```bash
qwen -p "Send email to test@example.com subject 'Hello' body 'This is a test'"
```

### gmail_read_emails

Read emails from Gmail.

**Parameters:**
- `query` (optional): Gmail search query (default: "is:unread")
- `maxResults` (optional): Maximum results (default: 10)

**Example:**
```bash
qwen -p "Read my last 5 emails from clients"
```

### gmail_mark_read

Mark an email as read.

**Parameters:**
- `messageId` (required): Gmail message ID

**Example:**
```bash
qwen -p "Mark message 123abc as read"
```

## Authentication

First time you use Gmail MCP, it will:
1. Open browser for OAuth authentication
2. Ask you to sign in to Google
3. Save token to `~/.ai_employee/gmail_token.json`
4. Use saved token for future requests

## Troubleshooting

### "credentials.json not found"

**Solution:**
```bash
# Make sure credentials.json exists
dir D:\FTE_AI_Employee\credentials.json

# If missing, download from Google Cloud Console
```

### "Authentication failed"

**Solution:**
```bash
# Delete saved token and re-authenticate
del "%USERPROFILE%\.ai_employee\gmail_token.json"

# Try again
qwen -p "Send test email"
```

### "MCP server not responding"

**Solution:**
```bash
# Test server manually
cd gmail-mcp-server
node index.js

# Should show: "Gmail MCP Server running on stdio"
```

## Testing

```bash
# Test installation
cd gmail-mcp-server
npm test

# Or test manually
node test.js
```

## File Structure

```
gmail-mcp-server/
├── index.js           # Main MCP server
├── gmail_utils.js     # Gmail utilities
├── package.json       # Dependencies
├── test.js           # Test script
└── README.md         # This file
```

## Security

- ✅ OAuth2 authentication (no passwords stored)
- ✅ Token saved securely in user profile
- ✅ Read-only or send-only scopes (configurable)
- ✅ Credentials never logged

## License

MIT
