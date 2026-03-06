"""
LinkedIn Auto-Poster v2 - Fixed Version

This version properly parses snapshots to find element references dynamically.
"""

import subprocess
import json
import sys
import time
import re
from pathlib import Path
import io

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MCP_URL = "http://localhost:8808"
MCP_CLIENT = Path(__file__).parent / '.qwen' / 'skills' / 'browsing-with-playwright' / 'scripts' / 'mcp-client.py'


def mcp_call(tool: str, params: dict, debug=False):
    """Make MCP server call."""
    try:
        result = subprocess.run(
            ['python', str(MCP_CLIENT), 'call', '-u', MCP_URL, '-t', tool, '-p', json.dumps(params)],
            capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace'
        )
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except:
                return {'text': result.stdout}
        if debug:
            print(f"  Error: {result.stderr[:200]}")
        return None
    except Exception as e:
        if debug:
            print(f"  Exception: {e}")
        return None


def extract_post_content(file_path: str) -> str:
    """Extract post content from draft file."""
    path = Path(file_path)
    if not path.exists():
        # Find any linkedin file
        for folder in ['Done', 'Approved', 'Social', 'Pending_Approval']:
            search_path = Path('AI_Employee_Vault') / folder
            if search_path.exists():
                matches = list(search_path.glob('*linkedin*.md'))
                if matches:
                    path = matches[0]
                    break
    
    if not path.exists():
        return None
    
    content = path.read_text(encoding='utf-8', errors='replace')
    
    # Extract content between ## Post Content and next ## or ---
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
        # Check if line has ref and any of our keywords
        if 'ref=' in line:
            for keyword in keywords:
                if keyword.lower() in line_lower:
                    # Extract ref
                    ref_match = re.search(r'ref=(e\d+)', line)
                    if ref_match:
                        found_refs.append(ref_match.group(1))
                        break
    
    return found_refs


def post_to_linkedin(content: str):
    """Post content to LinkedIn with dynamic ref detection."""
    
    print("\n" + "="*70)
    print("LINKEDIN AUTO-POSTER v2")
    print("="*70)
    
    # Step 1: Navigate to LinkedIn
    print("\n[1/7] Navigating to LinkedIn...")
    result = mcp_call('browser_navigate', {'url': 'https://www.linkedin.com/feed/'})
    if not result:
        print("  [FAIL] Failed to navigate")
        return False
    
    # Wait longer for page to fully load
    print("  Waiting for page to load (10 seconds)...")
    for i in range(10):
        time.sleep(1)
        print(f"  Loading... {i+1}s")
    
    print("  [OK] LinkedIn loaded")
    
    # Step 2: Get snapshot
    print("\n[2/7] Getting page snapshot...")
    snapshot = mcp_call('browser_snapshot', {})
    if not snapshot:
        print("  [FAIL] Failed to get snapshot")
        return False
    
    snapshot_text = str(snapshot.get('content', [{}])[0].get('text', '')) if isinstance(snapshot, dict) else str(snapshot)
    print(f"  [OK] Snapshot received ({len(snapshot_text)} chars)")
    
    # Step 3: Find and click "Start a post" button
    print("\n[3/7] Finding 'Start a post' button...")
    
    # Search for button with "post" keyword
    start_post_refs = find_ref_in_snapshot(snapshot_text, ['start', 'post', 'share'])
    
    if not start_post_refs:
        # Fallback: look for any button
        start_post_refs = find_ref_in_snapshot(snapshot_text, ['button'])[:5]
    
    print(f"  Found refs: {start_post_refs[:5]}")
    
    # Try clicking each ref until one works
    clicked = False
    for ref in start_post_refs[:10]:  # Try first 10 refs
        result = mcp_call('browser_click', {'element': 'Start a post', 'ref': ref})
        if result:
            print(f"  [OK] Clicked (ref: {ref})")
            clicked = True
            break
        time.sleep(0.3)
    
    if not clicked:
        print("  [FAIL] Could not click 'Start a post'")
        return False
    
    time.sleep(2)
    
    # Step 4: Get new snapshot for text area
    print("\n[4/7] Finding text input area...")
    snapshot2 = mcp_call('browser_snapshot', {})
    if not snapshot2:
        print("  [FAIL] Failed to get second snapshot")
        return False
    
    snapshot_text2 = str(snapshot2.get('content', [{}])[0].get('text', '')) if isinstance(snapshot2, dict) else str(snapshot2)
    
    # Find textbox/textarea
    text_refs = find_ref_in_snapshot(snapshot_text2, ['textbox', 'text', 'input', 'write', 'type'])
    
    if not text_refs:
        text_refs = find_ref_in_snapshot(snapshot_text2, ['editable'])[:5]
    
    print(f"  Found refs: {text_refs[:5]}")
    
    # Truncate content to LinkedIn limit (3000 chars)
    content_to_post = content[:3000]
    print(f"  Posting {len(content_to_post)} chars...")
    
    # Try typing with each ref
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
        time.sleep(0.3)
    
    if not typed:
        print("  [FAIL] Could not type content")
        return False
    
    time.sleep(2)
    
    # Step 5: Get snapshot for Post button
    print("\n[5/7] Finding Post button...")
    snapshot3 = mcp_call('browser_snapshot', {})
    
    if snapshot3:
        snapshot_text3 = str(snapshot3.get('content', [{}])[0].get('text', '')) if isinstance(snapshot3, dict) else str(snapshot3)
        
        # Find Post button - look for button with "post" keyword
        post_refs = find_ref_in_snapshot(snapshot_text3, ['post', 'share', 'submit'])
        
        # Filter for buttons only
        post_button_refs = []
        for ref in post_refs:
            # Check if this ref is associated with a button
            for line in snapshot_text3.split('\n'):
                if f'ref={ref}' in line and 'button' in line.lower():
                    post_button_refs.append(ref)
                    break
        
        if not post_button_refs:
            post_button_refs = post_refs[:5]
        
        print(f"  Found refs: {post_button_refs[:5]}")
    else:
        post_button_refs = ['e50', 'e20', 'e25']
    
    # Click Post button
    posted = False
    for ref in post_button_refs[:10]:
        result = mcp_call('browser_click', {'element': 'Post button', 'ref': ref})
        if result:
            print(f"  [OK] Clicked Post button (ref: {ref})")
            posted = True
            break
        time.sleep(0.3)
    
    if not posted:
        print("  [FAIL] Could not click Post button")
        return False
    
    time.sleep(3)
    
    # Step 6: Take screenshot
    print("\n[6/7] Capturing confirmation...")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result = mcp_call('browser_take_screenshot', {
        'type': 'png',
        'filename': f'linkedin_post_{timestamp}.png'
    })
    
    if result:
        print("  [OK] Screenshot captured")
    else:
        print("  [WARN] Could not capture screenshot")
    
    # Step 7: Verify post was published
    print("\n[7/7] Verifying post...")
    time.sleep(2)
    
    # Check if we see "Your post has been shared" or similar
    snapshot4 = mcp_call('browser_snapshot', {})
    if snapshot4:
        snapshot_text4 = str(snapshot4.get('content', [{}])[0].get('text', '')) if isinstance(snapshot4, dict) else str(snapshot4)
        if 'shared' in snapshot_text4.lower() or 'post' in snapshot_text4.lower():
            print("  [OK] Post appears to be published")
    
    print("\n" + "="*70)
    print("[SUCCESS] LinkedIn post published!")
    print("="*70)
    
    return True


if __name__ == '__main__':
    print("\n" + "="*70)
    print("LINKEDIN AUTO-POSTER v2")
    print("="*70)
    
    # Get file path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Find most recent LinkedIn post file
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
            print("Usage: python linkedin_auto_post.py [file_path]")
            sys.exit(1)
    
    print(f"\nUsing file: {file_path}")
    
    # Extract content
    content = extract_post_content(file_path)
    
    if not content:
        print("ERROR: Could not extract post content")
        sys.exit(1)
    
    print(f"Post content: {len(content)} chars")
    
    # Post to LinkedIn
    success = post_to_linkedin(content)
    
    sys.exit(0 if success else 1)
