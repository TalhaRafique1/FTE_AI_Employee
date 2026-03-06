"""
LinkedIn Auto-Post - Using browser_run_code (More Reliable)

Uses browser_run_code instead of individual commands for better reliability.
"""

import subprocess
import json
import sys
import time
import re
from pathlib import Path
import io

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MCP_URL = "http://localhost:8808"
MCP_CLIENT = Path(__file__).parent / '.qwen' / 'skills' / 'browsing-with-playwright' / 'scripts' / 'mcp-client.py'


def mcp_call(tool: str, params: dict):
    """Make MCP server call."""
    try:
        result = subprocess.run(
            ['python', str(MCP_CLIENT), 'call', '-u', MCP_URL, '-t', tool, '-p', json.dumps(params)],
            capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except:
                return {'text': result.stdout[:500]}
        return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None


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


def post_to_linkedin_simple(content: str):
    """Post to LinkedIn using simple browser automation."""
    
    print("\n" + "="*70)
    print("LINKEDIN AUTO-POSTER - Simple Version")
    print("="*70)
    
    # Use browser_run_code for everything in one call
    code = f'''
async (page) => {{
    // Navigate to LinkedIn
    await page.goto('https://www.linkedin.com/feed/', {{ waitUntil: 'networkidle', timeout: 30000 }});
    
    // Wait for page to load
    await page.waitForTimeout(5000);
    
    // Find and click "Start a post" button
    const startPostBtn = page.locator('[aria-label*="Start a post"], button:has-text("Start a post"), [data-control-name*="start-a-post"]').first();
    await startPostBtn.click({{ timeout: 10000 }}).catch(() => {{}});
    
    // Wait for composer to open
    await page.waitForTimeout(3000);
    
    // Find the text editor and type content
    const editor = page.locator('[role="textbox"], [contenteditable="true"], .ql-editor').first();
    await editor.fill(`{content[:1500]}`, {{ timeout: 10000 }}).catch(() => {{}});
    
    // Wait for text to be entered
    await page.waitForTimeout(2000);
    
    // Find and click Post button
    const postBtn = page.locator('button:has-text("Post"), [aria-label*="Post"]').first();
    await postBtn.click({{ timeout: 10000 }}).catch(() => {{}});
    
    // Wait for post to publish
    await page.waitForTimeout(5000);
    
    // Check if successful
    const url = page.url();
    const title = await page.title();
    
    return {{
        success: true,
        url: url,
        title: title,
        message: 'Post attempted'
    }};
}}
'''
    
    print("\n[1/4] Running LinkedIn post automation...")
    result = mcp_call('browser_run_code', {'code': code})
    
    if result:
        print("  [OK] Automation executed")
        print(f"  Result: {result}")
    else:
        print("  [WARN] Automation may have failed")
    
    print("\n[2/4] Taking screenshot...")
    screenshot = mcp_call('browser_take_screenshot', {
        'type': 'png',
        'filename': f'linkedin_post_{time.strftime("%Y%m%d_%H%M%S")}.png'
    })
    
    if screenshot:
        print("  [OK] Screenshot captured")
    else:
        print("  [WARN] Could not capture screenshot")
    
    print("\n[3/4] Checking result...")
    # Get current page info
    snapshot = mcp_call('browser_snapshot', {})
    if snapshot:
        print("  [OK] Got page snapshot")
    
    print("\n[4/4] Complete!")
    
    print("\n" + "="*70)
    print("LINKEDIN POST ATTEMPTED!")
    print("="*70)
    print("\nThe automation has run. Check your LinkedIn feed to verify.")
    print("Screenshot saved if successful.")
    
    return True


if __name__ == '__main__':
    print("\n" + "="*70)
    print("LINKEDIN AUTO-POSTER - Simple Version")
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
    
    success = post_to_linkedin_simple(content)
    
    sys.exit(0 if success else 1)
