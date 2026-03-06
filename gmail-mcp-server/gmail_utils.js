/**
 * Gmail utilities for MCP server
 */

import { readFileSync } from 'fs';
import mime from 'mime-types';

/**
 * Create MIME message for Gmail API
 */
export function createMessage(to, subject, body, attachmentPath = null) {
  let message = '';
  message += `To: ${to}\n`;
  message += `Subject: ${subject}\n`;
  message += `MIME-Version: 1.0\n`;
  message += `Content-Type: multipart/mixed; boundary="boundary123456"\n\n`;
  
  // Message body
  message += `--boundary123456\n`;
  message += `Content-Type: text/plain; charset="UTF-8"\n\n`;
  message += `${body}\n\n`;
  
  // Attachment if provided
  if (attachmentPath) {
    try {
      const fileData = readFileSync(attachmentPath);
      const base64Data = fileData.toString('base64');
      const mimeType = mime.lookup(attachmentPath) || 'application/octet-stream';
      const fileName = attachmentPath.split(/[\\/]/).pop();
      
      message += `--boundary123456\n`;
      message += `Content-Type: ${mimeType}\n`;
      message += `Content-Disposition: attachment; filename="${fileName}"\n`;
      message += `Content-Transfer-Encoding: base64\n\n`;
      message += `${base64Data}\n\n`;
      message += `--boundary123456--\n`;
    } catch (error) {
      console.error('Error reading attachment:', error.message);
    }
  } else {
    message += `--boundary123456--\n`;
  }
  
  const encodedMessage = Buffer.from(message)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
  
  return {
    raw: encodedMessage,
  };
}
