"""
LinkedIn Auto-Post with Login Check

Checks if logged in, logs in if needed, then posts automatically.
"""

import subprocess
import json
import sys
import time
import re
from pathlib import Path
import io

# Force UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MCP_URL = "http://localhost:8808"
MCP_CLIENT = Path(__file__).parent / '.qwen' / 'skills' / 'browsing-with-playwright' / 'scripts' / 'mcp-client.py'


def mcp_call(tool: str, params: dict, timeout=30):
    """Make MCP server call."""
    try:
        result = subprocess.run(
            ['python', str(MCP_CLIENT), 'call', '-u', MCP_URL, '-t', tool, '-p', json.dumps(params)],
            capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace'
        )
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except:
                return {'text': result.stdout}
        return None
    except Exception as e:
        return None


def check_if_logged_in(snapshot_text: str) -> bool:
    """Check if user is logged in to LinkedIn."""
    # Look for profile-related elements
    keywords = ['me', 'profile', 'notifications', 'messaging', 'feed']
    text_lower = snapshot_text.lower()
    
    for keyword in keywords:
        if keyword in text_lower:
            return True
    return False


def extract_post_content(file_path: str) -> str:
    """Extract post content from draft file."""
    path = Path(file_path)
    if not path.exists():
        for folder in ['Done', 'Approved', 'Social']:
            search_path = Path('AI_Employee_Vault') / folder
            if search_path.exists():
                matches = list(search_path.glob('*linkedin*.md'))
                if matches:
                    path = matches[0]
                    break
    
    if not path.exists():
        return None
    
    content = path.read_text(encoding='utf-8', errors='replace')
    match = re.search(r'## Post Content\s*\n+(.+?)(?=##|\n---|\Z)', content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    return content.strip()


def find_ref_in_snapshot(snapshot_text: str, keywords: list):
    """Find element ref in snapshot text by keywords."""
    lines = snapshot_text.split('\n')
    found_refs = []
    
    for line in lines:
        line_lower = line.lower()
        if 'ref=' in line:
            for keyword in keywords:
                if keyword.lower() in line_lower:
                    ref_match = re.search(r'ref=(e\d+)', line)
                    if ref_match:
                        found_refs.append(ref_match.group(1))
                        break
    
    return found_refs


def post_to_linkedin(content: str):
    """Post content to LinkedIn with login check."""
    
    print("\n" + "="*70)
    print("LINKEDIN AUTO-POSTER with Login Check")
    print("="*70)
    
    # Step 1: Navigate to LinkedIn
    print("\n[1/8] Navigating to LinkedIn...")
    result = mcp_call('browser_navigate', {'url': 'https://www.linkedin.com/'})
    if not result:
        print("  [FAIL] Failed to navigate")
        return False
    
    print("  Waiting for page to load (15 seconds)...")
    for i in range(15):
        time.sleep(1)
    
    # Step 2: Get snapshot and check if logged in
    print("\n[2/8] Checking login status...")
    snapshot = mcp_call('browser_snapshot', {})
    
    if not snapshot:
        print("  [FAIL] Failed to get snapshot")
        return False
    
    snapshot_text = str(snapshot.get('content', [{}])[0].get('text', '')) if isinstance(snapshot, dict) else str(snapshot)
    print(f"  Snapshot size: {len(snapshot_text)} chars")
    
    if len(snapshot_text) < 1000:
        print("  [WARN] Page may not be fully loaded")
    
    logged_in = check_if_logged_in(snapshot_text)
    
    if logged_in:
        print("  [OK] Already logged in to LinkedIn")
    else:
        print("  [WARN] Not logged in! Please login manually...")
        print("  A browser window is open. Please:")
        print("  1. Sign in to LinkedIn")
        print("  2. Wait for the feed to load")
        print("  3. Press Enter here to continue...")
        input()
        
        # Get new snapshot after login
        print("  Getting updated snapshot...")
        snapshot = mcp_call('browser_snapshot', {})
        if snapshot:
            snapshot_text = str(snapshot.get('content', [{}])[0].get('text', '')) if isinstance(snapshot, dict) else str(snapshot)
            print(f"  Snapshot size: {len(snapshot_text)} chars")
    
    # Step 3: Navigate to feed if needed
    print("\n[3/8] Navigating to feed...")
    mcp_call('browser_navigate', {'url': 'https://www.linkedin.com/feed/'})
    time.sleep(5)
    
    # Step 4: Get fresh snapshot
    print("\n[4/8] Getting feed snapshot...")
    snapshot = mcp_call('browser_snapshot', {})
    if not snapshot:
        print("  [FAIL] Failed to get snapshot")
        return False
    
    snapshot_text = str(snapshot.get('content', [{}])[0].get('text', '')) if isinstance(snapshot, dict) else str(snapshot)
    print(f"  [OK] Snapshot received ({len(snapshot_text)} chars)")
    
    # Step 5: Find and click "Start a post"
    print("\n[5/8] Finding 'Start a post' button...")
    start_post_refs = find_ref_in_snapshot(snapshot_text, ['start', 'post', 'share'])
    
    if not start_post_refs:
        start_post_refs = find_ref_in_snapshot(snapshot_text, ['button'])[:5]
    
    print(f"  Found refs: {start_post_refs[:5]}")
    
    clicked = False
    for ref in start_post_refs[:10]:
        result = mcp_call('browser_click', {'element': 'Start a post', 'ref': ref})
        if result:
            print(f"  [OK] Clicked (ref: {ref})")
            clicked = True
            break
        time.sleep(0.5)
    
    if not clicked:
        print("  [FAIL] Could not click 'Start a post'")
        print("  TIP: Make sure LinkedIn feed is fully loaded")
        return False
    
    time.sleep(3)
    
    # Step 6: Find text area and type content
    print("\n[6/8] Finding text input area...")
    snapshot2 = mcp_call('browser_snapshot', {})
    
    if not snapshot2:
        print("  [FAIL] Failed to get second snapshot")
        return False
    
    snapshot_text2 = str(snapshot2.get('content', [{}])[0].get('text', '')) if isinstance(snapshot2, dict) else str(snapshot2)
    text_refs = find_ref_in_snapshot(snapshot_text2, ['textbox', 'text', 'input', 'write', 'type', 'editable'])
    
    if not text_refs:
        print("  [FAIL] Could not find text area")
        return False
    
    print(f"  Found refs: {text_refs[:5]}")
    
    content_to_post = content[:3000]
    print(f"  Posting {len(content_to_post)} chars...")
    
    typed = False
    for ref in text_refs[:10]:
        result = mcp_call('browser_type', {
            'element': 'Post text area',
            'ref': ref,
            'text': content_to_post,
            'submit': False
        })
        if result:
            print(f"  [OK] Typed content (ref: {ref})")
            typed = True
            break
        time.sleep(0.5)
    
    if not typed:
        print("  [FAIL] Could not type content")
        return False
    
    time.sleep(3)
    
    # Step 7: Click Post button
    print("\n[7/8] Finding and clicking Post button...")
    snapshot3 = mcp_call('browser_snapshot', {})
    
    if snapshot3:
        snapshot_text3 = str(snapshot3.get('content', [{}])[0].get('text', '')) if isinstance(snapshot3, dict) else str(snapshot3)
        post_refs = find_ref_in_snapshot(snapshot_text3, ['post', 'share', 'submit'])
        
        post_button_refs = []
        for ref in post_refs:
            for line in snapshot_text3.split('\n'):
                if f'ref={ref}' in line and 'button' in line.lower():
                    post_button_refs.append(ref)
                    break
        
        if not post_button_refs:
            post_button_refs = post_refs[:5]
        
        print(f"  Found refs: {post_button_refs[:5]}")
    else:
        post_button_refs = ['e50', 'e20', 'e25']
    
    posted = False
    for ref in post_button_refs[:10]:
        result = mcp_call('browser_click', {'element': 'Post button', 'ref': ref})
        if result:
            print(f"  [OK] Clicked Post button (ref: {ref})")
            posted = True
            break
        time.sleep(0.5)
    
    if not posted:
        print("  [FAIL] Could not click Post button")
        return False
    
    time.sleep(5)
    
    # Step 8: Verify and screenshot
    print("\n[8/8] Verifying post...")
    snapshot4 = mcp_call('browser_snapshot', {})
    
    if snapshot4:
        snapshot_text4 = str(snapshot4.get('content', [{}])[0].get('text', '')) if isinstance(snapshot4, dict) else str(snapshot4)
        if 'shared' in snapshot_text4.lower() or 'post' in snapshot_text4.lower():
            print("  [OK] Post appears to be published")
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result = mcp_call('browser_take_screenshot', {
        'type': 'png',
        'filename': f'linkedin_post_{timestamp}.png'
    })
    
    if result:
        print("  [OK] Screenshot captured")
    
    print("\n" + "="*70)
    print("[SUCCESS] LinkedIn post published!")
    print("="*70)
    
    return True


if __name__ == '__main__':
    print("\n" + "="*70)
    print("LINKEDIN AUTO-POSTER with Login Check")
    print("="*70)
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = None
        for folder in ['Done', 'Approved', 'Social']:
            search_path = Path('AI_Employee_Vault') / folder
            if search_path.exists():
                matches = list(search_path.glob('*linkedin*.md'))
                if matches:
                    file_path = str(matches[0])
                    break
        
        if not file_path:
            print("\nERROR: No LinkedIn post file found!")
            sys.exit(1)
    
    print(f"\nUsing file: {file_path}")
    
    content = extract_post_content(file_path)
    
    if not content:
        print("ERROR: Could not extract post content")
        sys.exit(1)
    
    print(f"Post content: {len(content)} chars")
    
    success = post_to_linkedin(content)
    
    sys.exit(0 if success else 1)
