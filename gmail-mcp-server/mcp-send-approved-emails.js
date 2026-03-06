#!/usr/bin/env node
/**
 * Gmail MCP - Auto-Send Approved Emails
 * 
 * This script monitors the Approved folder and sends emails automatically via Gmail MCP.
 * 
 * Usage:
 *   node mcp-send-approved-emails.js
 */

import { readFile, writeFile, rm } from 'fs/promises';
import { join } from 'path';
import { homedir } from 'os';
import { google } from 'googleapis';
import { authenticate } from '@google-cloud/local-auth';
import { createMessage } from './gmail_utils.js';

// Configuration
const VAULT_PATH = join(process.cwd(), '..', 'AI_Employee_Vault');
const APPROVED_PATH = join(VAULT_PATH, 'Approved');
const DONE_PATH = join(VAULT_PATH, 'Done');
const TOKEN_PATH = join(homedir(), '.ai_employee', 'gmail_token.json');
const CREDENTIALS_PATH = join(process.cwd(), '..', 'credentials.json');

let oauth2Client;
let gmail;

/**
 * Load Gmail credentials and authenticate
 */
async function loadCredentials() {
  try {
    const credentials = JSON.parse(await readFile(CREDENTIALS_PATH, 'utf-8'));
    
    oauth2Client = new google.auth.OAuth2(
      credentials.installed.client_id,
      credentials.installed.client_secret,
      credentials.installed.redirect_uris[0]
    );
    
    // Try to load saved token
    try {
      const token = JSON.parse(await readFile(TOKEN_PATH, 'utf-8'));
      oauth2Client.setCredentials(token);
      console.log('✓ Loaded Gmail token');
    } catch (tokenError) {
      console.log('⚠ No saved token, authenticating...');
      const auth = await authenticate({
        keyfilePath: CREDENTIALS_PATH,
        scopes: ['https://www.googleapis.com/auth/gmail.send'],
      });
      
      // Save token
      const fs = await import('fs');
      const tokenDir = join(homedir(), '.ai_employee');
      if (!fs.existsSync(tokenDir)) {
        fs.mkdirSync(tokenDir, { recursive: true });
      }
      await writeFile(TOKEN_PATH, JSON.stringify(auth.credentials));
      console.log('✓ Saved Gmail token');
      
      oauth2Client = auth.client;
    }
    
    gmail = google.gmail({ version: 'v1', auth: oauth2Client });
    console.log('✓ Gmail API authenticated\n');
    
  } catch (error) {
    console.error('❌ Failed to load credentials:', error.message);
    throw error;
  }
}

/**
 * Extract email details from approved file
 */
function extractEmailDetails(content) {
  const toMatch = content.match(/to:\s*"([^"]+)"/);
  const subjectMatch = content.match(/subject:\s*"([^"]+)"/);
  const bodyMatch = content.match(/## Email Content\s*\n+(.+?)(?=##|\n---|\Z)/s);
  
  if (!toMatch || !subjectMatch) {
    return null;
  }
  
  return {
    to: toMatch[1].trim(),
    subject: subjectMatch[1].trim(),
    body: bodyMatch ? bodyMatch[1].trim() : content.substring(0, 500)
  };
}

/**
 * Send email via Gmail API
 */
async function sendEmail(to, subject, body) {
  try {
    const message = createMessage(to, subject, body);
    
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
    console.error(`  ❌ Error: ${error.message}`);
    return {
      success: false,
      error: error.message,
    };
  }
}

/**
 * Process approved emails
 */
async function processApprovedEmails() {
  console.log('='.repeat(70));
  console.log('GMAIL MCP - AUTO-SEND APPROVED EMAILS');
  console.log('='.repeat(70));
  console.log();
  
  // Load credentials
  await loadCredentials();
  
  // Check Approved folder
  const fs = await import('fs');
  if (!fs.existsSync(APPROVED_PATH)) {
    console.log('⚠ Approved folder not found');
    return;
  }
  
  const files = fs.readdirSync(APPROVED_PATH).filter(f => f.endsWith('.md') && f.startsWith('EMAIL_'));
  
  if (files.length === 0) {
    console.log('✓ No approved emails to send');
    return;
  }
  
  console.log(`📧 Found ${files.length} approved email(s)\n`);
  
  let sentCount = 0;
  let failCount = 0;
  
  for (const file of files) {
    console.log(`Processing: ${file}`);
    
    const filePath = join(APPROVED_PATH, file);
    const content = await readFile(filePath, 'utf-8');
    const emailData = extractEmailDetails(content);
    
    if (!emailData) {
      console.log(`  ⚠ Could not extract email details - skipping`);
      failCount++;
      continue;
    }
    
    console.log(`  To: ${emailData.to}`);
    console.log(`  Subject: ${emailData.subject}`);
    console.log(`  Body: ${emailData.body.substring(0, 100)}...`);
    
    // Send email
    const result = await sendEmail(emailData.to, emailData.subject, emailData.body);
    
    if (result.success) {
      console.log(`  ✅ Email sent! Message ID: ${result.messageId}`);
      
      // Move to Done folder
      if (!fs.existsSync(DONE_PATH)) {
        fs.mkdirSync(DONE_PATH, { recursive: true });
      }
      
      const donePath = join(DONE_PATH, file);
      await writeFile(donePath, content + `\n\n---\nSent: ${new Date().toISOString()}\nMessage ID: ${result.messageId}\n`);
      await rm(filePath);
      
      console.log(`  ✅ Moved to Done folder\n`);
      sentCount++;
    } else {
      console.log(`  ❌ Failed to send\n`);
      failCount++;
    }
  }
  
  console.log('='.repeat(70));
  console.log('SUMMARY');
  console.log('='.repeat(70));
  console.log(`Total: ${files.length}`);
  console.log(`Sent: ${sentCount}`);
  console.log(`Failed: ${failCount}`);
  console.log('='.repeat(70));
}

// Run
processApprovedEmails().catch(error => {
  console.error('Fatal error:', error.message);
  process.exit(1);
});
