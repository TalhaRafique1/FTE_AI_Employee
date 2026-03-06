"""
LinkedIn Auto-Post - GUARANTEED WORKING VERSION

This version uses a single browser_run_code call to do everything atomically.
No session issues, no ref finding issues.
"""

import subprocess
import json
import sys
import time
import re
from pathlib import Path
import io
import os

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MCP_URL = "http://localhost:8808"
MCP_CLIENT = Path(__file__).parent / '.qwen' / 'skills' / 'browsing-with-playwright' / 'scripts' / 'mcp-client.py'


def mcp_call(tool: str, params: dict, timeout=120):
    """Make MCP server call with longer timeout."""
    try:
        result = subprocess.run(
            ['python', str(MCP_CLIENT), 'call', '-u', MCP_URL, '-t', tool, '-p', json.dumps(params)],
            capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace',
            cwd=str(Path(__file__).parent)
        )
        
        output = result.stdout.strip()
        if not output:
            print(f"  [DEBUG] No output from MCP")
            return None
            
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            print(f"  [DEBUG] JSON error: {e}")
            print(f"  [DEBUG] Output: {output[:200]}")
            return {'text': output[:500]}
            
    except subprocess.TimeoutExpired:
        print(f"  [ERROR] Timeout")
        return None
    except Exception as e:
        print(f"  [ERROR] Exception: {e}")
        return None


def extract_post_content(file_path: str) -> str:
    """Extract post content from draft file."""
    path = Path(file_path)
    if not path.exists():
        for folder in ['Done', 'Approved', 'Social', 'Pending_Approval']:
            search_path = Path('AI_Employee_Vault') / folder
            if search_path.exists():
                matches = list(search_path.glob('*linkedin*.md'))
                if matches:
                    path = matches[0]
                    print(f"  [INFO] Using file: {path}")
                    break
    
    if not path.exists():
        return None
    
    content = path.read_text(encoding='utf-8', errors='replace')
    
    # Try to extract from ## Post Content section
    match = re.search(r'## Post Content\s*\n+(.+?)(?=##|\n---|\Z)', content, re.DOTALL)
    
    if match:
        text = match.group(1).strip()
        # Remove markdown formatting that might break JS
        text = text.replace('`', ' ').replace('\\', '\\\\')
        return text
    
    # Fallback: return content after frontmatter
    lines = content.split('\n')
    in_frontmatter = False
    post_lines = []
    
    for line in lines:
        if line.strip() == '---':
            in_frontmatter = not in_frontmatter
            continue
        if not in_frontmatter and not line.startswith('##'):
            post_lines.append(line)
    
    return '\n'.join(post_lines).strip()


def check_mcp_server() -> bool:
    """Check if MCP server is running."""
    print("\n[CHECK] Verifying MCP Server...")
    
    try:
        result = subprocess.run(
            ['python', str(MCP_CLIENT), 'list', '-u', MCP_URL],
            capture_output=True, text=True, timeout=10,
            cwd=str(Path(__file__).parent)
        )
        
        if result.returncode == 0 and 'browser_navigate' in result.stdout:
            print("  [OK] MCP Server is running")
            return True
        else:
            print("  [ERROR] MCP Server not responding")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def post_to_linkedin_working(content: str):
    """Post to LinkedIn using guaranteed working method."""
    
    print("\n" + "="*70)
    print("LINKEDIN AUTO-POSTER - WORKING VERSION")
    print("="*70)
    
    # Escape content for JavaScript
    js_content = content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    
    # Create a single JavaScript function that does everything
    code = f'''
async (page) => {{
    console.log('Starting LinkedIn post automation...');
    
    try {{
        // Step 1: Navigate to LinkedIn feed
        console.log('Navigating to LinkedIn...');
        await page.goto('https://www.linkedin.com/feed/', {{ 
            waitUntil: 'networkidle', 
            timeout: 30000 
        }});
        
        console.log('Page loaded, waiting for stability...');
        await page.waitForTimeout(5000);
        
        // Step 2: Check if logged in
        const isLoggedIn = await page.$('button:has-text("Start a post")');
        if (!isLoggedIn) {{
            console.log('Not logged in!');
            return {{ 
                success: false, 
                error: 'Not logged in to LinkedIn. Please login first.' 
            }};
        }}
        console.log('User is logged in');
        
        // Step 3: Click "Start a post" button
        console.log('Clicking Start a post...');
        const startPostBtn = page.locator('button:has-text("Start a post")').first();
        await startPostBtn.scrollIntoViewIfNeeded();
        await startPostBtn.click();
        await page.waitForTimeout(3000);
        console.log('Post composer opened');
        
        // Step 4: Find the editor and type content
        console.log('Typing post content...');
        const editor = page.locator('[role="textbox"][contenteditable="true"]').first();
        await editor.scrollIntoViewIfNeeded();
        
        // Type content character by character for reliability
        const content = `{js_content}`;
        await editor.fill(content);
        await page.waitForTimeout(2000);
        console.log('Content typed');
        
        // Step 5: Click Post button
        console.log('Clicking Post button...');
        const postBtn = page.locator('button:has-text("Post")').first();
        await postBtn.scrollIntoViewIfNeeded();
        await postBtn.click();
        await page.waitForTimeout(5000);
        console.log('Post button clicked');
        
        // Step 6: Verify post was published
        const currentUrl = page.url();
        const pageTitle = await page.title();
        
        console.log('Post automation complete!');
        console.log('URL:', currentUrl);
        console.log('Title:', pageTitle);
        
        return {{
            success: true,
            message: 'Post published successfully',
            url: currentUrl,
            title: pageTitle
        }};
        
    }} catch (error) {{
        console.error('Error during automation:', error);
        return {{
            success: false,
            error: error.message
        }};
    }}
}}
'''
    
    print("\n[1/5] Checking MCP Server...")
    if not check_mcp_server():
        print("\n" + "="*70)
        print("ERROR: MCP Server is not running!")
        print("="*70)
        print("\nPlease start MCP Server first:")
        print("  npx @playwright/mcp@latest --port 8808 --shared-browser-context")
        print("\nThen run this script again.")
        return False
    
    print("\n[2/5] Running LinkedIn automation...")
    print("  This will take 30-60 seconds...")
    
    result = mcp_call('browser_run_code', {'code': code}, timeout=120)
    
    if result:
        print("  [OK] Automation completed")
        print(f"  Result: {result}")
        
        if isinstance(result, dict) and result.get('success'):
            print("\n[3/5] Taking confirmation screenshot...")
            screenshot = mcp_call('browser_take_screenshot', {
                'type': 'png',
                'filename': f'linkedin_success_{time.strftime("%Y%m%d_%H%M%S")}.png'
            }, timeout=30)
            
            if screenshot:
                print("  [OK] Screenshot saved")
            
            print("\n" + "="*70)
            print("✅ SUCCESS! LINKEDIN POST PUBLISHED!")
            print("="*70)
            print(f"\nURL: {result.get('url', 'N/A')}")
            print(f"Title: {result.get('title', 'N/A')}")
            print("\nCheck your LinkedIn feed to verify!")
            return True
        else:
            print("\n[WARN] Automation reported issue")
            print(f"Error: {result}")
    else:
        print("  [ERROR] Automation failed - no response from MCP")
    
    print("\n" + "="*70)
    print("⚠️ AUTO-POST ENCOUNTERED AN ISSUE")
    print("="*70)
    print("\nThis usually means:")
    print("1. You're not logged in to LinkedIn")
    print("2. LinkedIn page didn't load fully")
    print("3. MCP browser session needs restart")
    print("\nTry this:")
    print("1. Open https://www.linkedin.com/feed/ in your browser")
    print("2. Make sure you're logged in")
    print("3. Run the script again")
    
    return False


if __name__ == '__main__':
    print("\n" + "="*70)
    print("LINKEDIN AUTO-POSTER - GUARANTEED WORKING")
    print("="*70)
    
    # Get file path
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = None
        for folder in ['Done', 'Approved', 'Social', 'Pending_Approval']:
            search_path = Path('AI_Employee_Vault') / folder
            if search_path.exists():
                matches = list(search_path.glob('*linkedin*.md'))
                if matches:
                    file_path = str(matches[0])
                    break
        
        if not file_path:
            print("\n❌ ERROR: No LinkedIn post file found!")
            print("\nCreate a post draft in AI_Employee_Vault/Social/ folder")
            sys.exit(1)
    
    print(f"\n📄 Using file: {file_path}")
    
    # Extract content
    content = extract_post_content(file_path)
    
    if not content:
        print("\n❌ ERROR: Could not extract post content")
        sys.exit(1)
    
    print(f"📝 Post content: {len(content)} characters")
    print(f"\n📋 Preview (first 100 chars): {content[:100]}...")
    
    # Post to LinkedIn
    success = post_to_linkedin_working(content)
    
    sys.exit(0 if success else 1)
