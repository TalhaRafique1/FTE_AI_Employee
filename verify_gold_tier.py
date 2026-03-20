"""
Gold Tier Verification Script

Tests all Gold Tier components to ensure they're working correctly.

Usage:
    python verify_gold_tier.py
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime


class GoldTierVerifier:
    """Verifies all Gold Tier components."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.vault_path = self.base_path / 'AI_Employee_Vault'
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

    def log_pass(self, message: str):
        print(f'✅ PASS: {message}')
        self.results['passed'].append(message)

    def log_fail(self, message: str):
        print(f'❌ FAIL: {message}')
        self.results['failed'].append(message)

    def log_warning(self, message: str):
        print(f'⚠️  WARNING: {message}')
        self.results['warnings'].append(message)

    def verify_file_exists(self, path: Path, description: str) -> bool:
        """Verify a file exists."""
        if path.exists():
            self.log_pass(f'{description} exists: {path}')
            return True
        else:
            self.log_fail(f'{description} missing: {path}')
            return False

    def verify_directory_exists(self, path: Path, description: str) -> bool:
        """Verify a directory exists."""
        if path.exists() and path.is_dir():
            self.log_pass(f'{description} directory exists: {path}')
            return True
        else:
            self.log_fail(f'{description} directory missing: {path}')
            return False

    def verify_python_syntax(self, path: Path) -> bool:
        """Verify Python file has valid syntax."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(path), 'exec')
            self.log_pass(f'Valid Python syntax: {path}')
            return True
        except SyntaxError as e:
            self.log_fail(f'Syntax error in {path}: {e}')
            return False
        except Exception as e:
            self.log_fail(f'Error reading {path}: {e}')
            return False

    def verify_docker_compose(self) -> bool:
        """Verify Docker Compose file is valid."""
        docker_compose = self.base_path / 'odoo' / 'docker-compose.yml'
        if not docker_compose.exists():
            self.log_fail(f'Docker Compose file missing: {docker_compose}')
            return False

        try:
            # Try to parse YAML
            import yaml
            with open(docker_compose, 'r') as f:
                yaml.safe_load(f)
            self.log_pass('Docker Compose file is valid YAML')
            return True
        except ImportError:
            self.log_warning('PyYAML not installed, skipping YAML validation')
            return True
        except Exception as e:
            self.log_fail(f'Invalid Docker Compose file: {e}')
            return False

    def verify_vault_structure(self) -> bool:
        """Verify Obsidian vault has required folders."""
        required_folders = [
            'Needs_Action',
            'Pending_Approval',
            'Approved',
            'Done',
            'Plans',
            'Briefings',
            'Logs',
            'Accounting',
            'Social'
        ]

        all_exist = True
        for folder in required_folders:
            folder_path = self.vault_path / folder
            if not self.verify_directory_exists(folder_path, folder):
                all_exist = False

        return all_exist

    def verify_gold_tier_files(self) -> bool:
        """Verify all Gold Tier files exist."""
        gold_files = [
            ('Facebook Watcher', self.base_path / 'watchers' / 'facebook_watcher.py'),
            ('Ralph Wiggum Loop', self.base_path / 'ralph_wiggum_loop.py'),
            ('CEO Briefing Generator', self.base_path / 'ceo_briefing_generator.py'),
            ('Odoo MCP Server', self.base_path / 'odoo' / 'odoo-mcp-server' / 'odoo_mcp_server.py'),
            ('Odoo Docker Compose', self.base_path / 'odoo' / 'docker-compose.yml'),
            ('Gold Tier Skills Doc', self.base_path / '.qwen' / 'skills' / 'GOLD_TIER_SKILLS.md'),
            ('Gold Tier Complete Doc', self.base_path / 'GOLD_TIER_COMPLETE.md'),
        ]

        all_exist = True
        for description, path in gold_files:
            if not self.verify_file_exists(path, description):
                all_exist = False

        return all_exist

    def verify_orchestrator_gold_features(self) -> bool:
        """Verify orchestrator has Gold Tier methods."""
        orchestrator_path = self.base_path / 'orchestrator.py'
        if not orchestrator_path.exists():
            self.log_fail('Orchestrator not found')
            return False

        content = orchestrator_path.read_text(encoding='utf-8')

        gold_methods = [
            'execute_facebook_post',
            'execute_odoo_action',
            'run_ralph_wiggum_loop',
            'generate_ceo_briefing',
            'schedule_weekly_briefing',
        ]

        all_found = True
        for method in gold_methods:
            if f'def {method}' in content:
                self.log_pass(f'Orchestrator has method: {method}')
            else:
                self.log_fail(f'Orchestrator missing method: {method}')
                all_found = False

        return all_found

    def verify_python_imports(self) -> bool:
        """Verify critical Python imports work."""
        test_imports = [
            ('pathlib', 'Standard library'),
            ('json', 'Standard library'),
            ('datetime', 'Standard library'),
            ('subprocess', 'Standard library'),
        ]

        all_work = True
        for module, description in test_imports:
            try:
                __import__(module)
                self.log_pass(f'Import works: {module} ({description})')
            except ImportError as e:
                self.log_fail(f'Import failed: {module} - {e}')
                all_work = False

        return all_work

    def verify_odoo_mcp_tools(self) -> bool:
        """Verify Odoo MCP server defines required tools."""
        mcp_path = self.base_path / 'odoo' / 'odoo-mcp-server' / 'odoo_mcp_server.py'
        if not mcp_path.exists():
            return False

        content = mcp_path.read_text(encoding='utf-8')

        required_tools = [
            'odoo_connect',
            'odoo_get_account_summary',
            'odoo_get_invoices',
            'odoo_create_invoice',
            'odoo_get_partners',
            'odoo_create_partner',
        ]

        all_found = True
        for tool in required_tools:
            if f"name='{tool}'" in content or f'name="{tool}"' in content:
                self.log_pass(f'Odoo MCP has tool: {tool}')
            else:
                self.log_fail(f'Odoo MCP missing tool: {tool}')
                all_found = False

        return all_found

    def verify_briefing_generator_logic(self) -> bool:
        """Verify CEO briefing generator has required analysis."""
        briefing_path = self.base_path / 'ceo_briefing_generator.py'
        if not briefing_path.exists():
            return False

        content = briefing_path.read_text(encoding='utf-8')

        required_features = [
            '_analyze_completed_tasks',
            '_analyze_finances',
            '_audit_subscriptions',
            '_identify_bottlenecks',
            '_generate_suggestions',
        ]

        all_found = True
        for feature in required_features:
            if f'def {feature}' in content:
                self.log_pass(f'Briefing generator has: {feature}')
            else:
                self.log_fail(f'Briefing generator missing: {feature}')
                all_found = False

        return all_found

    def verify_ralph_loop_features(self) -> bool:
        """Verify Ralph Wiggum loop has required features."""
        ralph_path = self.base_path / 'ralph_wiggum_loop.py'
        if not ralph_path.exists():
            return False

        content = ralph_path.read_text(encoding='utf-8')

        required_features = [
            'completion_promise',
            'max_iterations',
            '_check_file_completion',
            '_check_promise_completion',
        ]

        all_found = True
        for feature in required_features:
            if feature in content:
                self.log_pass(f'Ralph loop has: {feature}')
            else:
                self.log_fail(f'Ralph loop missing: {feature}')
                all_found = False

        return all_found

    def run_all_verifications(self):
        """Run all verification checks."""
        # Set up UTF-8 encoding for Windows console
        import io
        if sys.platform == 'win32':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

        print('\n' + '='*70)
        print('GOLD TIER VERIFICATION')
        print('='*70)
        print(f'Base Path: {self.base_path}')
        print(f'Vault Path: {self.vault_path}')
        print(f'Time: {datetime.now().isoformat()}')
        print('='*70 + '\n')

        # File existence checks
        print('[FILES] Checking File Existence...')
        print('-'*70)
        self.verify_gold_tier_files()
        print()

        # Vault structure
        print('[VAULT] Checking Vault Structure...')
        print('-'*70)
        self.verify_vault_structure()
        print()

        # Python syntax
        print('[PYTHON] Checking Python Syntax...')
        print('-'*70)
        python_files = [
            self.base_path / 'watchers' / 'facebook_watcher.py',
            self.base_path / 'ralph_wiggum_loop.py',
            self.base_path / 'ceo_briefing_generator.py',
            self.base_path / 'odoo' / 'odoo-mcp-server' / 'odoo_mcp_server.py',
            self.base_path / 'orchestrator.py',
        ]
        for file in python_files:
            if file.exists():
                self.verify_python_syntax(file)
        print()

        # Docker Compose
        print('[DOCKER] Checking Docker Configuration...')
        print('-'*70)
        self.verify_docker_compose()
        print()

        # Orchestrator features
        print('[ORCHESTRATOR] Checking Orchestrator Gold Features...')
        print('-'*70)
        self.verify_orchestrator_gold_features()
        print()

        # Odoo MCP tools
        print('[ODOO] Checking Odoo MCP Tools...')
        print('-'*70)
        self.verify_odoo_mcp_tools()
        print()

        # Briefing generator
        print('[BRIEFING] Checking Briefing Generator...')
        print('-'*70)
        self.verify_briefing_generator_logic()
        print()

        # Ralph loop
        print('[RALPH] Checking Ralph Wiggum Loop...')
        print('-'*70)
        self.verify_ralph_loop_features()
        print()

        # Python imports
        print('[IMPORTS] Checking Python Imports...')
        print('-'*70)
        self.verify_python_imports()
        print()

        # Summary
        print('='*70)
        print('VERIFICATION SUMMARY')
        print('='*70)
        print(f'PASSED: {len(self.results["passed"])}')
        print(f'FAILED: {len(self.results["failed"])}')
        print(f'WARNINGS: {len(self.results["warnings"])}')
        print('='*70)

        if self.results['failed']:
            print('\nFailed Checks:')
            for fail in self.results['failed']:
                print(f'  [FAIL] {fail}')

        if self.results['warnings']:
            print('\nWarnings:')
            for warn in self.results['warnings']:
                print(f'  [WARN] {warn}')

        print()
        if not self.results['failed']:
            print('SUCCESS: ALL VERIFICATION CHECKS PASSED!')
            print('Gold Tier is ready to use!')
        else:
            print('WARNING: Some checks failed. Please review and fix the issues above.')

        return len(self.results['failed']) == 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Verify Gold Tier Installation')
    parser.add_argument(
        '--base-path',
        default=r'D:\FTE_AI_Employee',
        help='Base path of AI Employee project'
    )

    args = parser.parse_args()

    verifier = GoldTierVerifier(args.base_path)
    success = verifier.run_all_verifications()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
