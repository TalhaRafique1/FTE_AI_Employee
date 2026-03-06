"""
LinkedIn Post Helper - Easy Method

1. Opens LinkedIn in your browser
2. Shows you the post content to copy
3. You paste and post manually
"""

import webbrowser
import time
from pathlib import Path
import re
import sys
import io

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def find_linkedin_post():
    """Find the most recent LinkedIn post file."""
    for folder in ['Approved', 'Done', 'Social', 'Pending_Approval']:
        search_path = Path('AI_Employee_Vault') / folder
        if search_path.exists():
            matches = list(search_path.glob('*linkedin*.md'))
            if matches:
                return matches[0]
    return None

def extract_post_content(file_path):
    """Extract just the post content from the file."""
    content = file_path.read_text(encoding='utf-8', errors='replace')
    
    # Extract content between ## Post Content and next ## or ---
    match = re.search(r'## Post Content\s*\n+(.+?)(?=##|\n---|\Z)', content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # Fallback: return everything after frontmatter
    lines = content.split('\n')
    in_frontmatter = False
    post_lines = []
    
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False
                continue
        if not in_frontmatter and not line.startswith('---'):
            post_lines.append(line)
    
    return '\n'.join(post_lines).strip()

def main():
    print("\n" + "="*70)
    print("LINKEDIN POST HELPER - Easy Method")
    print("="*70)
    print()
    
    # Step 1: Open LinkedIn
    print("[Step 1/4] Opening LinkedIn in your browser...")
    webbrowser.open('https://www.linkedin.com/feed/')
    print("Done! LinkedIn should be opening now.")
    print()
    
    # Wait for browser
    print("Waiting 5 seconds for LinkedIn to load...")
    time.sleep(5)
    
    # Step 2: Find post file
    print("[Step 2/4] Finding post content...")
    post_file = find_linkedin_post()
    
    if not post_file:
        print("ERROR: No LinkedIn post file found!")
        print()
        print("Please create a post draft in AI_Employee_Vault/Social/ folder")
        return
    
    print(f"Found: {post_file}")
    print()
    
    # Step 3: Extract and display content
    print("[Step 3/4] POST CONTENT (Copy this):")
    print("="*70)
    print()
    
    post_content = extract_post_content(post_file)
    print(post_content)
    
    print()
    print("="*70)
    print()
    
    # Step 4: Instructions
    print("[Step 4/4] NEXT STEPS:")
    print("="*70)
    print()
    print("1. LinkedIn should be open in your browser")
    print("   If not, go to: https://www.linkedin.com/feed/")
    print()
    print("2. Click 'Start a post' button at the top of your feed")
    print()
    print("3. Copy the content above (Ctrl+A to select, Ctrl+C to copy)")
    print()
    print("4. Paste into LinkedIn post box (Ctrl+V)")
    print()
    print("5. Click 'Post' button")
    print()
    print("="*70)
    print()
    print(f"Post file: {post_file}")
    print()
    
    input("Press Enter when you've posted...")
    print()
    print("Great! Your post should be live on LinkedIn now!")
    print()

if __name__ == '__main__':
    main()
