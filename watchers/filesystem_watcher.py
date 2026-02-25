"""
File System Watcher Module

Monitors a drop folder for new files and creates action files for processing.
This is the simplest watcher to set up and test for the Bronze tier.
"""

import shutil
import hashlib
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class FileDropItem:
    """Represents a file dropped for processing."""
    
    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.name = source_path.name
        self.size = source_path.stat().st_size
        self.content_hash = self._calculate_hash()
        
    def _calculate_hash(self) -> str:
        """Calculate MD5 hash of file content."""
        hash_md5 = hashlib.md5()
        with open(self.source_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


class FilesystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files.
    
    When a file is detected, it:
    1. Copies the file to the vault
    2. Creates a metadata .md file in Needs_Action
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None, check_interval: int = 30):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            drop_folder: Path to the drop folder (defaults to vault/Inbox)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Use Inbox as drop folder by default
        self.drop_folder = Path(drop_folder) if drop_folder else self.inbox
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash to avoid duplicates
        self.processed_files: set = set()
        
        # Keywords that trigger urgency
        self.urgent_keywords = ['urgent', 'asap', 'emergency', 'important', 'priority']
        
        self.logger.info(f'Drop folder: {self.drop_folder}')
    
    def check_for_updates(self) -> List[FileDropItem]:
        """
        Check the drop folder for new files.
        
        Returns:
            List of new FileDropItem objects
        """
        new_items = []
        
        try:
            for file_path in self.drop_folder.iterdir():
                if file_path.is_file() and not file_path.suffix == '.md':
                    item = FileDropItem(file_path)
                    
                    # Skip if already processed
                    if item.content_hash in self.processed_files:
                        continue
                    
                    new_items.append(item)
                    self.processed_files.add(item.content_hash)
                    
        except Exception as e:
            self.logger.error(f'Error checking drop folder: {e}')
        
        return new_items
    
    def create_action_file(self, item: FileDropItem) -> Optional[Path]:
        """
        Create an action file for a dropped file.
        
        Args:
            item: The FileDropItem to create an action file for
            
        Returns:
            Path to the created action file
        """
        try:
            # Copy file to vault storage
            storage_folder = self.vault_path / 'FileStorage'
            storage_folder.mkdir(parents=True, exist_ok=True)
            dest_path = storage_folder / item.name
            
            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = Path(item.name).stem
                suffix = Path(item.name).suffix
                dest_path = storage_folder / f'{stem}_{counter}{suffix}'
                counter += 1
            
            shutil.copy2(item.source_path, dest_path)
            
            # Check for urgent keywords in filename
            is_urgent = any(kw in item.name.lower() for kw in self.urgent_keywords)
            priority = 'high' if is_urgent else 'normal'
            
            # Generate frontmatter
            frontmatter = self.generate_frontmatter(
                item_type='file_drop',
                original_name=f'"{item.name}"',
                size=item.size,
                priority=f'"{priority}"',
                storage_path=f'"{dest_path}"',
                content_hash=f'"{item.content_hash}"'
            )
            
            # Create action file content
            content = f'''{frontmatter}

# File Drop for Processing

## File Details
- **Original Name:** {item.name}
- **Size:** {self._format_size(item.size)}
- **Priority:** {priority.title()}
- **Storage Location:** `{dest_path}`

## Content Preview
'''
            # Add content preview for text files
            if item.source_path.suffix.lower() in ['.txt', '.md', '.csv', '.json', '.py', '.js']:
                try:
                    with open(item.source_path, 'r', encoding='utf-8') as f:
                        preview = f.read(500)  # First 500 chars
                        content += f'```\n{preview}\n'
                        if len(preview) >= 500:
                            content += '...\n'
                        content += '```\n'
                except Exception as e:
                    content += f'*Could not read file content: {e}*\n'
            else:
                content += f'*Binary file - cannot preview*\n'
            
            content += '''
## Suggested Actions
- [ ] Review file contents
- [ ] Categorize file type
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Notes
_Add any notes here_
'''
            
            # Write action file
            filename = self.safe_filename('FILE', item.name)
            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')
            
            # Remove original from drop folder (we've processed it)
            item.source_path.unlink()
            
            self.logger.info(f'Processed file drop: {item.name} -> {filepath.name}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file for {item.name}: {e}')
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'


if __name__ == '__main__':
    import sys
    
    # Default vault path
    vault_path = r'D:\FTE_AI_Employee\AI_Employee_Vault'
    
    # Allow override via command line
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    
    watcher = FilesystemWatcher(vault_path, check_interval=30)
    print(f'Filesystem Watcher starting...')
    print(f'Watching: {watcher.drop_folder}')
    print(f'Press Ctrl+C to stop')
    print('-' * 50)
    watcher.run()
