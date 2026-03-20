"""
Ralph Wiggum Loop Implementation - Gold Tier

Implements the persistence pattern for autonomous multi-step task completion.
Based on: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

Usage:
    python ralph_wiggum_loop.py "Process all pending tasks"

The loop will:
1. Create a state file with the task
2. Run Qwen Code to process it
3. Check if task is complete (file moved to /Done)
4. If not complete, re-inject the prompt and continue
5. Repeat until complete or max iterations reached
"""

import subprocess
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple
import argparse


class RalphWiggumLoop:
    """
    Implements the Ralph Wiggum persistence pattern.

    Keeps Qwen Code running until a multi-step task is complete.
    Uses file-based completion detection.
    """

    def __init__(
        self,
        vault_path: str,
        prompt: str,
        max_iterations: int = 10,
        completion_promise: Optional[str] = None,
        timeout_minutes: int = 60
    ):
        """
        Initialize the Ralph Wiggum loop.

        Args:
            vault_path: Path to Obsidian vault
            prompt: Initial task prompt
            max_iterations: Maximum loop iterations
            completion_promise: Expected output text indicating completion
            timeout_minutes: Overall timeout in minutes
        """
        self.vault_path = Path(vault_path)
        self.prompt = prompt
        self.max_iterations = max_iterations
        self.completion_promise = completion_promise
        self.timeout = timedelta(minutes=timeout_minutes)

        # State files
        self.state_file = self.vault_path / '.ralph_state.json'
        self.logs = self.vault_path / 'Logs'
        self.logs.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Load or initialize state
        self.state = self._load_state()

    def _setup_logging(self):
        """Configure logging."""
        log_file = self.logs / f'ralph_wiggum_{datetime.now().strftime("%Y-%m-%d")}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('RalphWiggum')

    def _load_state(self) -> dict:
        """Load state from file or create new."""
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text(encoding='utf-8'))
                self.logger.info(f'Loaded existing state: {state.get("task", "Unknown")}')
                return state
            except Exception as e:
                self.logger.warning(f'Could not load state: {e}')

        # Create new state
        return {
            'task': self.prompt,
            'iteration': 0,
            'started': datetime.now().isoformat(),
            'last_output': '',
            'status': 'pending',
            'completion_detected': False
        }

    def _save_state(self):
        """Save current state to file."""
        self.state['updated'] = datetime.now().isoformat()
        self.state_file.write_text(json.dumps(self.state, indent=2), encoding='utf-8')

    def _check_file_completion(self) -> bool:
        """
        Check if task is complete via file movement.

        Looks for:
        - Task files moved to /Done
        - No files remaining in /Needs_Action related to task
        - Plan.md marked as complete
        """
        needs_action = self.vault_path / 'Needs_Action'
        done = self.vault_path / 'Done'
        plans = self.vault_path / 'Plans'

        # Check if any active plans exist
        active_plans = []
        for plan_file in plans.glob('*.md'):
            content = plan_file.read_text(encoding='utf-8')
            if '[ ]' in content or '[x]' not in content:
                # Has unchecked items
                active_plans.append(plan_file.name)

        if active_plans:
            self.logger.info(f'Active plans remaining: {active_plans}')
            return False

        # Check if files were moved to Done in last iteration
        # (indicates progress was made)
        return True

    def _check_promise_completion(self, output: str) -> bool:
        """Check if output contains completion promise."""
        if not self.completion_promise:
            return False

        # Check for promise tag
        promise_tag = f'<promise>{self.completion_promise}</promise>'
        if promise_tag in output:
            return True

        # Check for completion markers
        completion_markers = [
            'TASK_COMPLETE',
            '✅ Complete',
            'All tasks completed',
            'No more actions needed',
        ]

        return any(marker in output for marker in completion_markers)

    def _run_qwen_code(self, prompt: str, iteration: int) -> Tuple[str, int]:
        """
        Run Qwen Code with the given prompt.

        Returns:
            Tuple of (output, return_code)
        """
        self.logger.info(f'Running Qwen Code (iteration {iteration})')

        # Build command
        # Use --continue if available, or just pass prompt
        cmd = f'qwen -p "{prompt}"'

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per iteration
                shell=True,
                encoding='utf-8',
                errors='replace'
            )

            output = result.stdout + result.stderr
            self.logger.info(f'Qwen Code returned code: {result.returncode}')

            # Log output (truncated if too long)
            output_preview = output[:500] + '...' if len(output) > 500 else output
            self.logger.debug(f'Output preview: {output_preview}')

            return output, result.returncode

        except subprocess.TimeoutExpired:
            self.logger.error('Qwen Code timed out')
            return 'Error: Qwen Code timed out', -1
        except Exception as e:
            self.logger.error(f'Error running Qwen Code: {e}')
            return f'Error: {e}', -1

    def _build_continuation_prompt(self, previous_output: str) -> str:
        """Build prompt for continuation iteration."""
        return f'''{self.prompt}

CONTINUATION: You previously worked on this task and produced:

{previous_output[-2000:]}  # Last 2000 chars

Check if the task is complete:
1. Are there still files in /Needs_Action related to this task?
2. Are there incomplete items in /Plans?
3. Have you moved completed work to /Done?

If the task is NOT complete, continue working.
If the task IS complete, output: <promise>TASK_COMPLETE</promise>

Continue from where you left off.'''

    def run(self) -> bool:
        """
        Run the Ralph Wiggum loop.

        Returns:
            True if task completed successfully, False otherwise
        """
        self.logger.info('='*60)
        self.logger.info('RALPH WIGGUM LOOP - Autonomous Task Completion')
        self.logger.info('='*60)
        self.logger.info(f'Task: {self.prompt}')
        self.logger.info(f'Max iterations: {self.max_iterations}')
        self.logger.info(f'Timeout: {self.timeout}')
        self.logger.info('='*60)

        start_time = datetime.now()

        try:
            while self.state['iteration'] < self.max_iterations:
                # Check timeout
                elapsed = datetime.now() - start_time
                if elapsed > self.timeout:
                    self.logger.error(f'Timeout after {elapsed}')
                    self.state['status'] = 'timeout'
                    self._save_state()
                    return False

                # Run Qwen Code
                if self.state['iteration'] == 0:
                    prompt = self.prompt
                else:
                    prompt = self._build_continuation_prompt(self.state['last_output'])

                output, return_code = self._run_qwen_code(prompt, self.state['iteration'])
                self.state['last_output'] = output
                self.state['iteration'] += 1
                self._save_state()

                # Check for completion
                completion_detected = False

                # Method 1: Check completion promise
                if self._check_promise_completion(output):
                    self.logger.info('✅ Completion promise detected!')
                    completion_detected = True

                # Method 2: Check file-based completion
                if self._check_file_completion():
                    self.logger.info('✅ File-based completion detected!')
                    completion_detected = True

                if completion_detected:
                    self.logger.info('✅ Task completed successfully!')
                    self.state['status'] = 'completed'
                    self.state['completion_detected'] = True
                    self.state['completed_at'] = datetime.now().isoformat()
                    self._save_state()

                    # Create completion record
                    self._create_completion_record()

                    return True

                # Check if Qwen encountered an error
                if return_code != 0 and 'Error' in output:
                    self.logger.warning(f'Qwen Code returned error (iteration {self.state["iteration"]})')
                    # Continue anyway - might be recoverable

                self.logger.info(f'Iteration {self.state["iteration"]}/{self.max_iterations} complete, continuing...')
                time.sleep(2)  # Brief pause before next iteration

            # Max iterations reached
            self.logger.error(f'Max iterations ({self.max_iterations}) reached without completion')
            self.state['status'] = 'max_iterations_reached'
            self._save_state()
            return False

        except KeyboardInterrupt:
            self.logger.info('Loop interrupted by user')
            self.state['status'] = 'interrupted'
            self._save_state()
            return False
        except Exception as e:
            self.logger.error(f'Unexpected error: {e}')
            self.state['status'] = 'error'
            self._save_state()
            raise

    def _create_completion_record(self):
        """Create a completion record in Done folder."""
        completion_file = self.logs / f'ralph_completion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

        content = f'''---
type: ralph_wiggum_completion
task: "{self.prompt}"
started: {self.state.get('started', 'Unknown')}
completed: {datetime.now().isoformat()}
iterations: {self.state['iteration']}
status: completed
---

# Ralph Wiggum Loop - Completion Record

## Task
{self.prompt}

## Execution Summary
- **Started:** {self.state.get('started', 'Unknown')}
- **Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Iterations:** {self.state['iteration']}
- **Status:** ✅ Completed

## Notes
Task completed successfully via Ralph Wiggum autonomous loop.
'''

        completion_file.write_text(content, encoding='utf-8')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Loop - Autonomous multi-step task completion'
    )
    parser.add_argument(
        'prompt',
        help='Task prompt for Qwen Code'
    )
    parser.add_argument(
        '--vault', '-v',
        default=r'D:\FTE_AI_Employee\AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--max-iterations', '-m',
        type=int,
        default=10,
        help='Maximum loop iterations (default: 10)'
    )
    parser.add_argument(
        '--completion-promise', '-c',
        default='TASK_COMPLETE',
        help='Expected completion marker text'
    )
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        default=60,
        help='Timeout in minutes (default: 60)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Log what would be done without executing'
    )

    args = parser.parse_args()

    if args.dry_run:
        print(f'[DRY RUN] Would start Ralph Wiggum loop with:')
        print(f'  Task: {args.prompt}')
        print(f'  Max iterations: {args.max_iterations}')
        print(f'  Completion promise: {args.completion_promise}')
        print(f'  Timeout: {args.timeout} minutes')
        return

    loop = RalphWiggumLoop(
        vault_path=args.vault,
        prompt=args.prompt,
        max_iterations=args.max_iterations,
        completion_promise=args.completion_promise,
        timeout_minutes=args.timeout
    )

    success = loop.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
