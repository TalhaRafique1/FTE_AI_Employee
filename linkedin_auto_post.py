"""
LinkedIn Auto-Poster - Posts content to LinkedIn using Playwright MCP

This script:
1. Opens LinkedIn
2. Gets page snapshot to find correct element refs
3. Clicks "Start a post"
4. Types the content
5. Clicks Post button
6. Takes screenshot confirmation

Usage:
    python linkedin_auto_post.py [post_file_path]
    
Example:
    python linkedin_auto_post.py AI_Employee_Vault\Done\DRAFT_linkedin_achievement_2026-02-26.md
"""

import subprocess
import json
import sys
import time
import re
from pathlib import Path

MCP_URL = "http://localhost:8808"
MCP_CLIENT = Path(__file__).parent / '.qwen' / 'skills' / 'browsing-with-playwright' / 'scripts' / 'mcp-client.py'


def mcp_call(tool: str, params: dict):
    """Make MCP server call."""
    try:
        result = subprocess.run(
            ['python', str(MCP_CLIENT), 'call', '-u', MCP_URL, '-t', tool, '-p', json.dumps(params)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        print(f"MCP call error: {e}")
        return None


def extract_post_content(file_path: str) -> str:
    """Extract post content from draft file."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)
    
    content = path.read_text(encoding='utf-8')
    
    # Extract content between ## Post Content and next ## or ---
    match = re.search(r'## Post Content\s*\n+(.+?)(?=##|\n---|\Z)', content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # Fallback: return everything after frontmatter
    lines = content.split('\n')
    in_frontmatter = False
    post_lines = []
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                return '\n'.join(lines[i+1:]).strip()
    
    return content.strip()


def find_element_ref(snapshot_text: str, element_name: str, possible_refs: list) -> str:
    """Find element ref from snapshot."""
    # Try each possible ref
    for ref in possible_refs:
        if f'ref={ref}' in snapshot_text and element_name.lower() in snapshot_text.lower():
            return ref
    return None


def post_to_linkedin(content: str):
    """Post content to LinkedIn."""
    
    print("\n" + "="*60)
    print("LINKEDIN AUTO-POSTER")
    print("="*60)
    print(f"\nPost content length: {len(content)} chars")
    print(f"First 100 chars: {content[:100]}...")
    print("\nStarting post process...")
    
    # Step 1: Navigate to LinkedIn
    print("\n[1/6] Navigating to LinkedIn...")
    result = mcp_call('browser_navigate', {'url': 'https://www.linkedin.com/feed/'})
    if not result:
        print("ERROR: Failed to navigate to LinkedIn")
        return False
    time.sleep(5)  # Wait for page to load
    print("✓ LinkedIn loaded")
    
    # Step 2: Get snapshot to find element refs
    print("\n[2/6] Getting page snapshot...")
    snapshot = mcp_call('browser_snapshot', {})
    if not snapshot:
        print("ERROR: Failed to get snapshot")
        return False
    
    # Extract snapshot text
    snapshot_text = str(snapshot)
    print("✓ Snapshot received")
    
    # Find "Start a post" button - look for it in snapshot
    # Common patterns: "Start a post", "Starta post"
    start_post_refs = []
    for line in snapshot_text.split('\n'):
        if 'start' in line.lower() and 'post' in line.lower() and 'ref=' in line:
            # Extract ref
            match = re.search(r'ref=(e\d+)', line)
            if match:
                start_post_refs.append(match.group(1))
    
    if not start_post_refs:
        # Fallback to common refs
        start_post_refs = ['e192', 'e42', 'e14', 'e10']
    
    print(f"  Found 'Start a post' refs: {start_post_refs}")
    
    # Step 3: Click "Start a post"
    print("\n[3/6] Opening post composer...")
    clicked = False
    for ref in start_post_refs:
        result = mcp_call('browser_click', {'element': 'Start a post', 'ref': ref})
        if result:
            print(f"✓ Clicked 'Start a post' (ref: {ref})")
            clicked = True
            break
        time.sleep(0.5)
    
    if not clicked:
        print("ERROR: Could not click 'Start a post'")
        return False
    
    time.sleep(2)  # Wait for composer to open
    
    # Step 4: Get new snapshot for text area
    print("\n[4/6] Finding text area...")
    snapshot2 = mcp_call('browser_snapshot', {})
    if not snapshot2:
        print("ERROR: Failed to get second snapshot")
        return False
    
    snapshot_text2 = str(snapshot2)
    
    # Find text area ref
    text_area_refs = []
    for line in snapshot_text2.split('\n'):
        if ('textbox' in line.lower() or 'textarea' in line.lower()) and 'ref=' in line:
            match = re.search(r'ref=(e\d+)', line)
            if match:
                text_area_refs.append(match.group(1))
    
    if not text_area_refs:
        text_area_refs = ['e45', 'e10', 'e15', 'e20']
    
    print(f"  Found text area refs: {text_area_refs}")
    
    # Type content (truncate to 3000 chars for LinkedIn limit)
    content_to_post = content[:3000]
    print(f"  Posting {len(content_to_post)} chars...")
    
    typed = False
    for ref in text_area_refs:
        result = mcp_call('browser_type', {
            'element': 'Post text area',
            'ref': ref,
            'text': content_to_post,
            'submit': False
        })
        if result:
            print(f"✓ Typed content (ref: {ref})")
            typed = True
            break
        time.sleep(0.5)
    
    if not typed:
        print("ERROR: Could not type content")
        return False
    
    time.sleep(2)  # Wait for text to be entered
    
    # Step 5: Click Post button
    print("\n[5/6] Publishing post...")
    snapshot3 = mcp_call('browser_snapshot', {})
    
    # Find Post button ref
    post_refs = []
    if snapshot3:
        snapshot_text3 = str(snapshot3)
        for line in snapshot_text3.split('\n'):
            if 'post' in line.lower() and 'button' in line.lower() and 'ref=' in line:
                match = re.search(r'ref=(e\d+)', line)
                if match:
                    post_refs.append(match.group(1))
    
    if not post_refs:
        post_refs = ['e50', 'e20', 'e25', 'e30']
    
    print(f"  Found Post button refs: {post_refs}")
    
    posted = False
    for ref in post_refs:
        result = mcp_call('browser_click', {'element': 'Post button', 'ref': ref})
        if result:
            print(f"✓ Clicked Post button (ref: {ref})")
            posted = True
            break
        time.sleep(0.5)
    
    if not posted:
        print("ERROR: Could not click Post button")
        return False
    
    time.sleep(3)  # Wait for post to publish
    
    # Step 6: Take screenshot
    print("\n[6/6] Capturing confirmation...")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result = mcp_call('browser_take_screenshot', {
        'type': 'png',
        'filename': f'linkedin_post_success_{timestamp}.png'
    })
    
    if result:
        print("✓ Screenshot captured")
    else:
        print("⚠ Could not capture screenshot")
    
    print("\n" + "="*60)
    print("✅ SUCCESS! LinkedIn post published!")
    print("="*60)
    
    return True


if __name__ == '__main__':
    print("\nLinkedIn Auto-Poster")
    print("="*60)
    
    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Find most recent LinkedIn post file
        for folder in ['Done', 'Approved', 'Social']:
            search_path = Path('AI_Employee_Vault') / folder
            if search_path.exists():
                matches = list(search_path.glob('*linkedin*.md'))
                if matches:
                    file_path = str(matches[0])
                    break
        else:
            print("ERROR: No LinkedIn post file found!")
            print("Usage: python linkedin_auto_post.py [file_path]")
            sys.exit(1)
    
    print(f"Using file: {file_path}")
    
    # Extract content
    content = extract_post_content(file_path)
    
    if not content:
        print("ERROR: Could not extract post content")
        sys.exit(1)
    
    # Post to LinkedIn
    success = post_to_linkedin(content)
    
    sys.exit(0 if success else 1)
