"""
LinkedIn Post Content Extractor

Reads a LinkedIn post draft file and displays clean content ready to copy-paste.

Usage:
    python extract_linkedin_post.py [file_path]
    
Example:
    python extract_linkedin_post.py AI_Employee_Vault/Done/DRAFT_linkedin_achievement_2026-02-26.md
"""

import sys
from pathlib import Path
import re

def extract_post_content(file_path: str) -> str:
    """Extract just the post content from a draft file."""
    
    path = Path(file_path)
    if not path.exists():
        # Try to find any LinkedIn post file
        for folder in ['Done', 'Approved', 'Social', 'Pending_Approval']:
            search_path = Path('AI_Employee_Vault') / folder / '*linkedin*.md'
            matches = list(search_path.parent.glob(search_path.name))
            if matches:
                path = matches[0]
                break
    
    if not path.exists():
        return "ERROR: No LinkedIn post file found!"
    
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
                # End of frontmatter, return rest
                return '\n'.join(lines[i+1:]).strip()
    
    return content.strip()


if __name__ == '__main__':
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    post_content = extract_post_content(file_path)
    
    print("\n" + "="*70)
    print("LINKEDIN POST CONTENT")
    print("="*70)
    print()
    print(post_content)
    print()
    print("="*70)
    print()
    print("To post:")
    print("1. Go to https://www.linkedin.com/feed/")
    print("2. Click 'Start a post'")
    print("3. Paste this content")
    print("4. Click 'Post'")
    print("="*70)
