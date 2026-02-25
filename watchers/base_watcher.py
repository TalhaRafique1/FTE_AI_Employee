"""
Base Watcher Module

Abstract base class for all watcher scripts in the AI Employee system.
Watchers monitor external inputs and create actionable .md files in the Needs_Action folder.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    Watchers run continuously in the background, monitoring specific inputs
    (email, files, APIs) and creating action files when new items are detected.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
    def _setup_logging(self):
        """Configure logging to file and console."""
        log_file = self.logs / f'watcher_{datetime.now().strftime("%Y-%m-%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items to process.
        
        Returns:
            List of new items that need action files created
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create an action file for a detected item.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to created file, or None if creation failed
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        pass
    
    def run(self):
        """
        Main run loop. Continuously checks for updates and creates action files.
        
        This method runs indefinitely until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                if filepath:
                                    self.logger.info(f'Created action file: {filepath.name}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new items')
                        
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise
    
    def generate_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Generate YAML frontmatter for action files.
        
        Args:
            item_type: Type of item (email, file_drop, whatsapp, etc.)
            **kwargs: Additional frontmatter fields
            
        Returns:
            Formatted YAML frontmatter string
        """
        frontmatter = [
            '---',
            f'type: {item_type}',
            f'created: {datetime.now().isoformat()}',
            'status: pending',
        ]
        
        for key, value in kwargs.items():
            frontmatter.append(f'{key}: {value}')
        
        frontmatter.append('---')
        return '\n'.join(frontmatter)
    
    def safe_filename(self, prefix: str, identifier: str) -> str:
        """
        Generate a safe filename from prefix and identifier.
        
        Args:
            prefix: File prefix (e.g., EMAIL, FILE_DROP)
            identifier: Unique identifier (will be sanitized)
            
        Returns:
            Safe filename with .md extension
        """
        # Remove or replace unsafe characters
        safe_id = identifier.replace('/', '_').replace('\\', '_')
        safe_id = ''.join(c for c in safe_id if c.isalnum() or c in '-_')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{prefix}_{safe_id}_{timestamp}.md'


if __name__ == '__main__':
    # This is an abstract class - cannot be instantiated directly
    print("BaseWatcher is an abstract base class.")
    print("Subclass it and implement check_for_updates() and create_action_file().")
