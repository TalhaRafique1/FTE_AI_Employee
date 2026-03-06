#!/usr/bin/env node
/**
 * Gmail MCP Server
 * 
 * Provides email capabilities to Qwen Code via Model Context Protocol.
 * - Send emails
 * - Read emails
 * - Search emails
 * - Manage labels
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { readFile } from 'fs/promises';
import { homedir } from 'os';
import { join } from 'path';
import { google } from 'googleapis';
import { authenticate } from '@google-cloud/local-auth';

// Gmail API credentials
let oauth2Client;
let gmail;

/**
 * Load Gmail API credentials and authenticate
 */
async function loadCredentials() {
  try {
    // Try to load token first
    const tokenPath = join(homedir(), '.ai_employee', 'gmail_token.json');
    const credentialsPath = join(process.cwd(), 'credentials.json');
    
    let credentials;
    try {
      credentials = JSON.parse(await readFile(credentialsPath, 'utf-8'));
    } catch (error) {
      console.error('Error reading credentials:', error.message);
      throw new Error('credentials.json not found');
    }
    
    oauth2Client = new google.auth.OAuth2(
      credentials.installed.client_id,
      credentials.installed.client_secret,
      credentials.installed.redirect_uris[0]
    );
    
    // Try to load saved token
    try {
      const token = JSON.parse(await readFile(tokenPath, 'utf-8'));
      oauth2Client.setCredentials(token);
      console.error('Loaded saved Gmail token');
    } catch (tokenError) {
      // Need to authenticate
      console.error('No saved token, please authenticate...');
      const auth = await authenticate({
        keyfilePath: credentialsPath,
        scopes: ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly'],
      });
      
      // Save token for future use
      const fs = await import('fs');
      const tokenDir = join(homedir(), '.ai_employee');
      if (!fs.existsSync(tokenDir)) {
        fs.mkdirSync(tokenDir, { recursive: true });
      }
      fs.writeFileSync(tokenPath, JSON.stringify(auth.credentials));
      console.error('Saved Gmail token to:', tokenPath);
      
      oauth2Client = auth.client;
    }
    
    gmail = google.gmail({ version: 'v1', auth: oauth2Client });
    console.error('Gmail API authenticated successfully');
    
  } catch (error) {
    console.error('Failed to load Gmail credentials:', error.message);
    throw error;
  }
}

/**
 * Send email via Gmail API
 */
async function sendEmail(to, subject, body, attachmentPath = null) {
  try {
    const { createMessage } = await import('./gmail_utils.js');
    const message = createMessage(to, subject, body, attachmentPath);
    
    const response = await gmail.users.messages.send({
      userId: 'me',
      requestBody: message,
    });
    
    return {
      success: true,
      messageId: response.data.id,
      threadId: response.data.threadId,
    };
  } catch (error) {
    console.error('Error sending email:', error.message);
    return {
      success: false,
      error: error.message,
    };
  }
}

/**
 * Read emails from Gmail
 */
async function readEmails(query = 'is:unread', maxResults = 10) {
  try {
    const response = await gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: maxResults,
    });
    
    const messages = response.data.messages || [];
    const emails = [];
    
    for (const message of messages) {
      const fullMessage = await gmail.users.messages.get({
        userId: 'me',
        id: message.id,
        format: 'metadata',
        metadataHeaders: ['From', 'To', 'Subject', 'Date'],
      });
      
      const headers = fullMessage.data.payload.headers;
      emails.push({
        id: message.id,
        from: headers.find(h => h.name === 'From')?.value || 'Unknown',
        to: headers.find(h => h.name === 'To')?.value || 'Unknown',
        subject: headers.find(h => h.name === 'Subject')?.value || 'No Subject',
        date: headers.find(h => h.name === 'Date')?.value || 'Unknown',
      });
    }
    
    return {
      success: true,
      emails: emails,
      count: emails.length,
    };
  } catch (error) {
    console.error('Error reading emails:', error.message);
    return {
      success: false,
      error: error.message,
    };
  }
}

/**
 * Mark email as read
 */
async function markAsRead(messageId) {
  try {
    await gmail.users.messages.modify({
      userId: 'me',
      id: messageId,
      requestBody: {
        removeLabelIds: ['UNREAD'],
      },
    });
    
    return {
      success: true,
      messageId: messageId,
    };
  } catch (error) {
    console.error('Error marking email as read:', error.message);
    return {
      success: false,
      error: error.message,
    };
  }
}

// Create MCP server
const server = new Server(
  {
    name: 'gmail-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'gmail_send_email',
        description: 'Send an email via Gmail API. Requires authentication.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject',
            },
            body: {
              type: 'string',
              description: 'Email body text',
            },
            attachment: {
              type: 'string',
              description: 'Optional attachment file path',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'gmail_read_emails',
        description: 'Read emails from Gmail. Can filter by query.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Gmail search query (e.g., "is:unread", "from:boss@company.com")',
              default: 'is:unread',
            },
            maxResults: {
              type: 'number',
              description: 'Maximum number of emails to return',
              default: 10,
            },
          },
        },
      },
      {
        name: 'gmail_mark_read',
        description: 'Mark an email as read',
        inputSchema: {
          type: 'object',
          properties: {
            messageId: {
              type: 'string',
              description: 'Gmail message ID to mark as read',
            },
          },
          required: ['messageId'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    // Ensure authenticated
    if (!gmail) {
      await loadCredentials();
    }
    
    switch (name) {
      case 'gmail_send_email': {
        const { to, subject, body, attachment } = args;
        const result = await sendEmail(to, subject, body, attachment);
        
        if (result.success) {
          return {
            content: [
              {
                type: 'text',
                text: `✅ Email sent successfully!\nMessage ID: ${result.messageId}\nThread ID: ${result.threadId}`,
              },
            ],
          };
        } else {
          return {
            content: [
              {
                type: 'text',
                text: `❌ Failed to send email\nError: ${result.error}`,
              },
            ],
            isError: true,
          };
        }
      }
      
      case 'gmail_read_emails': {
        const { query, maxResults } = args;
        const result = await readEmails(query, maxResults);
        
        if (result.success) {
          const emailList = result.emails.map(e => 
            `From: ${e.from}\nSubject: ${e.subject}\nDate: ${e.date}\n---`
          ).join('\n');
          
          return {
            content: [
              {
                type: 'text',
                text: `📧 Found ${result.count} emails:\n\n${emailList}`,
              },
            ],
          };
        } else {
          return {
            content: [
              {
                type: 'text',
                text: `❌ Failed to read emails\nError: ${result.error}`,
              },
            ],
            isError: true,
          };
        }
      }
      
      case 'gmail_mark_read': {
        const { messageId } = args;
        const result = await markAsRead(messageId);
        
        if (result.success) {
          return {
            content: [
              {
                type: 'text',
                text: `✅ Email marked as read\nMessage ID: ${result.messageId}`,
              },
            ],
          };
        } else {
          return {
            content: [
              {
                type: 'text',
                text: `❌ Failed to mark email as read\nError: ${result.error}`,
              },
            ],
            isError: true,
          };
        }
      }
      
      default:
        return {
          content: [
            {
              type: 'text',
              text: `Unknown tool: ${name}`,
            },
          ],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  console.error('Starting Gmail MCP Server...');
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('Gmail MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
