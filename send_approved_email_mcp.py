"""
Send Approved Email via Gmail MCP

This script reads an approved email file and sends it using Qwen Code + Gmail MCP.

Usage:
    python send_approved_email_mcp.py AI_Employee_Vault/Approved/EMAIL_*.md
"""

import subprocess
import sys
from pathlib import Path
import re


def extract_email_details(file_path: str) -> dict:
    """Extract email details from approved file."""
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: File not found: {path}")
        return None
    
    content = path.read_text(encoding='utf-8', errors='replace')
    
    # Extract fields
    to_match = re.search(r'to:\s*"([^"]+)"', content)
    subject_match = re.search(r'subject:\s*"([^"]+)"', content)
    body_match = re.search(r'## Email Content\s*\n+(.+?)(?=##|\n---|\Z)', content, re.DOTALL)
    
    if not all([to_match, subject_match, body_match]):
        print("WARNING: Could not extract all fields, using fallback")
        return {
            'to': to_match.group(1).strip() if to_match else None,
            'subject': subject_match.group(1).strip() if subject_match else 'No Subject',
            'body': content[:500]
        }
    
    return {
        'to': to_match.group(1).strip(),
        'subject': subject_match.group(1).strip(),
        'body': body_match.group(1).strip()
    }


def send_via_mcp(file_path: str):
    """Send email using Qwen Code + Gmail MCP."""
    
    print("\n" + "="*70)
    print("SENDING EMAIL VIA GMAIL MCP")
    print("="*70)
    print(f"\nFile: {file_path}")
    
    # Extract details
    email_data = extract_email_details(file_path)
    
    if not email_data or not email_data['to']:
        print("\n❌ ERROR: Could not extract email details")
        print("File may not be in correct format")
        return False
    
    print(f"\nEmail Details:")
    print(f"  To: {email_data['to']}")
    print(f"  Subject: {email_data['subject']}")
    print(f"  Body: {email_data['body'][:100]}...")
    
    # Build Qwen Code command
    prompt = f'''You are an AI Employee assistant. Send an approved email using Gmail MCP.

Email Details:
- To: {email_data['to']}
- Subject: {email_data['subject']}
- Body: {email_data['body'][:500]}

Use the Gmail MCP tool 'gmail_send_email' to send this email now.

After sending, confirm the email was sent successfully and report the message ID.'''
    
    print("\n" + "="*70)
    print("Calling Qwen Code with Gmail MCP...")
    print("="*70)
    
    # Run Qwen Code
    result = subprocess.run(
        ['qwen', '-p', prompt],
        capture_output=True, text=True, timeout=120,
        encoding='utf-8', errors='replace'
    )
    
    print("\n" + "="*70)
    print("QWEN CODE OUTPUT:")
    print("="*70)
    print(result.stdout)
    
    if result.returncode == 0:
        print("\n✅ Email send command executed!")
        
        # Move to Done folder
        done_folder = Path('AI_Employee_Vault') / 'Done'
        done_folder.mkdir(exist_ok=True)
        
        source_path = Path(file_path)
        dest_path = done_folder / source_path.name
        
        try:
            source_path.rename(dest_path)
            print(f"✅ Moved to Done folder: {dest_path}")
        except Exception as e:
            print(f"⚠️ Could not move file: {e}")
        
        return True
    else:
        print(f"\n❌ Qwen Code failed with code {result.returncode}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return False


def main():
    if len(sys.argv) < 2:
        # Find most recent approved email
        approved_folder = Path('AI_Employee_Vault') / 'Approved'
        if not approved_folder.exists():
            print("ERROR: Approved folder not found")
            sys.exit(1)
        
        approved_files = list(approved_folder.glob('EMAIL_*.md'))
        if not approved_files:
            print("ERROR: No approved emails found")
            sys.exit(1)
        
        file_path = str(approved_files[0])
        print(f"Using most recent approved email: {file_path}")
    else:
        file_path = sys.argv[1]
    
    success = send_via_mcp(file_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
