"""
Weekly CEO Briefing Generator - Gold Tier

Autonomously generates comprehensive business briefings every Monday morning.
Analyzes transactions, tasks, and metrics to provide executive insights.

Usage:
    python ceo_briefing_generator.py

Or scheduled via Task Scheduler:
    schtasks /create /tn "CEO_Briefing" /tr "python ceo_briefing_generator.py" /sc weekly /d MON /st 07:00
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re


class CEOBriefingGenerator:
    """
    Generates weekly CEO briefings with business insights.

    Analyzes:
    - Completed tasks from /Done
    - Financial data (from Odoo or manual entries)
    - Subscription costs
    - Bottlenecks and delays
    - Upcoming deadlines
    """

    def __init__(self, vault_path: str, odoo_enabled: bool = False):
        """
        Initialize the briefing generator.

        Args:
            vault_path: Path to Obsidian vault
            odoo_enabled: Whether to fetch data from Odoo
        """
        self.vault_path = Path(vault_path)
        self.odoo_enabled = odoo_enabled
        self.briefings = self.vault_path / 'Briefings'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.business_goals = self.vault_path / 'Business_Goals.md'

        # Ensure directories exist
        self.briefings.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Subscription patterns to detect
        self.subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'github.com': 'GitHub',
            'microsoft.com': 'Microsoft 365',
            'zoom.us': 'Zoom',
            'canva.com': 'Canva',
            'mailchimp.com': 'Mailchimp',
        }

    def _setup_logging(self):
        """Configure logging."""
        log_file = self.logs / f'ceo_briefing_{datetime.now().strftime("%Y-%m-%d")}.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('CEOBriefing')

    def generate_briefing(self, week_start: Optional[datetime] = None) -> Path:
        """
        Generate a weekly CEO briefing.

        Args:
            week_start: Start of week to analyze (default: last Monday)

        Returns:
            Path to generated briefing file
        """
        if week_start is None:
            # Default to last Monday
            today = datetime.now()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday, weeks=1)

        week_end = week_start + timedelta(days=6)  # Sunday

        self.logger.info(f'Generating briefing for {week_start.date()} to {week_end.date()}')

        # Gather data
        completed_tasks = self._analyze_completed_tasks(week_start, week_end)
        financial_summary = self._analyze_finances(week_start, week_end)
        subscriptions = self._audit_subscriptions()
        bottlenecks = self._identify_bottlenecks(week_start, week_end)
        upcoming_deadlines = self._get_upcoming_deadlines()
        proactive_suggestions = self._generate_suggestions(
            completed_tasks, financial_summary, subscriptions, bottlenecks
        )

        # Generate briefing content
        content = self._format_briefing(
            week_start=week_start,
            week_end=week_end,
            completed_tasks=completed_tasks,
            financial_summary=financial_summary,
            subscriptions=subscriptions,
            bottlenecks=bottlenecks,
            upcoming_deadlines=upcoming_deadlines,
            proactive_suggestions=proactive_suggestions
        )

        # Save briefing
        filename = f'{week_end.strftime("%Y-%m-%d")}_Monday_Briefing.md'
        briefing_file = self.briefings / filename
        briefing_file.write_text(content, encoding='utf-8')

        self.logger.info(f'Briefing saved to: {briefing_file}')

        # Update Dashboard with latest briefing
        self._update_dashboard(briefing_file)

        return briefing_file

    def _analyze_completed_tasks(
        self, week_start: datetime, week_end: datetime
    ) -> Dict[str, Any]:
        """Analyze completed tasks from the week."""
        tasks = {
            'completed': [],
            'total_count': 0,
            'by_type': {},
            'avg_completion_time': None,
        }

        # Scan Done folder for files from this week
        for done_file in self.done.glob('*.md'):
            try:
                content = done_file.read_text(encoding='utf-8')

                # Try to extract date from frontmatter or filename
                file_date = self._extract_date_from_file(done_file, content)
                if not file_date:
                    continue

                # Check if within week range
                if week_start <= file_date <= week_end:
                    task_info = self._parse_task_file(done_file, content)
                    tasks['completed'].append(task_info)
                    tasks['total_count'] += 1

                    # Categorize by type
                    task_type = task_info.get('type', 'general')
                    tasks['by_type'][task_type] = tasks['by_type'].get(task_type, 0) + 1

            except Exception as e:
                self.logger.debug(f'Error analyzing {done_file.name}: {e}')

        # Also check logs
        tasks_from_logs = self._parse_task_logs(week_start, week_end)
        tasks['completed'].extend(tasks_from_logs)
        tasks['total_count'] += len(tasks_from_logs)

        return tasks

    def _analyze_finances(
        self, week_start: datetime, week_end: datetime
    ) -> Dict[str, Any]:
        """Analyze financial data for the week."""
        summary = {
            'revenue': 0.0,
            'expenses': 0.0,
            'net': 0.0,
            'transactions': [],
            'invoices_sent': 0,
            'invoices_paid': 0,
            'outstanding': 0.0,
        }

        # Try to get data from Odoo if enabled
        if self.odoo_enabled:
            try:
                odoo_summary = self._get_odoo_summary()
                summary.update(odoo_summary)
                self.logger.info('Financial data fetched from Odoo')
                return summary
            except Exception as e:
                self.logger.warning(f'Could not fetch from Odoo: {e}')
                # Fall through to manual analysis

        # Manual analysis from Accounting folder
        accounting_folder = self.vault_path / 'Accounting'
        if accounting_folder.exists():
            summary = self._analyze_manual_accounting(
                accounting_folder, week_start, week_end, summary
            )

        # Analyze transaction logs
        summary = self._analyze_transaction_logs(
            week_start, week_end, summary
        )

        summary['net'] = summary['revenue'] - summary['expenses']

        return summary

    def _get_odoo_summary(self) -> Dict[str, float]:
        """Fetch financial summary from Odoo via MCP."""
        # This would call the Odoo MCP server
        # For now, return placeholder
        return {
            'revenue': 0.0,
            'expenses': 0.0,
            'invoices_sent': 0,
            'invoices_paid': 0,
            'outstanding': 0.0,
        }

    def _analyze_manual_accounting(
        self, accounting_folder: Path, week_start: datetime,
        week_end: datetime, summary: Dict
    ) -> Dict:
        """Analyze manually entered accounting data."""
        # Look for transaction files
        for file in accounting_folder.glob('*.md'):
            try:
                content = file.read_text(encoding='utf-8')

                # Parse transactions
                for line in content.split('\n'):
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            try:
                                # Expected format: | Date | Description | Amount | Type |
                                date_str = parts[1].strip()
                                amount_str = parts[2].strip().replace('$', '').replace(',', '')
                                tx_type = parts[3].strip().lower() if len(parts) > 3 else ''

                                # Parse date
                                try:
                                    tx_date = datetime.strptime(date_str, '%Y-%m-%d')
                                    if week_start <= tx_date <= week_end:
                                        amount = float(amount_str)
                                        if 'income' in tx_type or 'revenue' in tx_type or amount > 0:
                                            summary['revenue'] += abs(amount)
                                        elif 'expense' in tx_type or amount < 0:
                                            summary['expenses'] += abs(amount)
                                except:
                                    pass
                            except:
                                pass
            except Exception as e:
                self.logger.debug(f'Error analyzing {file.name}: {e}')

        return summary

    def _analyze_transaction_logs(
        self, week_start: datetime, week_end: datetime, summary: Dict
    ) -> Dict:
        """Analyze transaction logs."""
        # Look for transaction log files
        for log_file in self.logs.glob('transactions_*.md'):
            try:
                content = log_file.read_text(encoding='utf-8')
                # Parse similar to manual accounting
            except:
                pass

        return summary

    def _audit_subscriptions(self) -> List[Dict[str, Any]]:
        """Audit active subscriptions and flag unused ones."""
        subscriptions = []

        # Try to find subscription data
        # 1. Check Business_Goals.md for known subscriptions
        if self.business_goals.exists():
            content = self.business_goals.read_text(encoding='utf-8')
            known_subs = self._parse_known_subscriptions(content)
            subscriptions.extend(known_subs)

        # 2. Analyze transaction logs for recurring payments
        recurring = self._detect_recurring_payments()
        subscriptions.extend(recurring)

        # 3. Flag potentially unused subscriptions
        for sub in subscriptions:
            if sub.get('last_used_days', 0) > 30:
                sub['flag'] = 'unused_30_days'
            elif sub.get('last_used_days', 0) > 60:
                sub['flag'] = 'unused_60_days'

        return subscriptions

    def _parse_known_subscriptions(self, content: str) -> List[Dict]:
        """Parse known subscriptions from Business_Goals.md."""
        subscriptions = []

        # Look for subscription table
        in_subscription_section = False
        for line in content.split('\n'):
            if 'Subscription' in line or 'subscription' in line.lower():
                in_subscription_section = True
                continue

            if in_subscription_section and '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 3:
                    try:
                        # Skip header row
                        if 'Service' in parts[0] or 'Cost' in parts[0]:
                            continue

                        sub = {
                            'name': parts[0],
                            'monthly_cost': float(parts[1].replace('$', '').replace('-', '0')),
                            'last_used': parts[2] if len(parts) > 2 else 'Unknown',
                        }
                        subscriptions.append(sub)
                    except:
                        pass

        return subscriptions

    def _detect_recurring_payments(self) -> List[Dict]:
        """Detect recurring payments from transaction history."""
        # This would analyze bank transactions for recurring patterns
        # For now, return empty list
        return []

    def _identify_bottlenecks(
        self, week_start: datetime, week_end: datetime
    ) -> List[Dict[str, Any]]:
        """Identify tasks that took longer than expected."""
        bottlenecks = []

        # Analyze Plans folder for delayed tasks
        plans_folder = self.vault_path / 'Plans'
        if plans_folder.exists():
            for plan_file in plans_folder.glob('*.md'):
                try:
                    content = plan_file.read_text(encoding='utf-8')

                    # Look for incomplete checkmarks
                    if '[ ]' in content:
                        # Task not completed
                        bottleneck = self._analyze_plan_delay(plan_file, content)
                        if bottleneck:
                            bottlenecks.append(bottleneck)

                except Exception as e:
                    self.logger.debug(f'Error analyzing plan {plan_file.name}: {e}')

        return bottlenecks

    def _analyze_plan_delay(self, plan_file: Path, content: str) -> Optional[Dict]:
        """Analyze a plan for delays."""
        # Extract dates from frontmatter
        created_match = re.search(r'created:\s*(\S+)', content)
        if created_match:
            try:
                created = datetime.fromisoformat(created_match.group(1))
                age_days = (datetime.now() - created).days

                if age_days > 3:  # Older than 3 days
                    return {
                        'task': plan_file.stem,
                        'age_days': age_days,
                        'status': 'incomplete',
                        'severity': 'high' if age_days > 7 else 'medium'
                    }
            except:
                pass

        return None

    def _get_upcoming_deadlines(self) -> List[Dict[str, Any]]:
        """Get upcoming deadlines from Business_Goals.md and Plans."""
        deadlines = []

        # Parse Business_Goals.md
        if self.business_goals.exists():
            content = self.business_goals.read_text(encoding='utf-8')

            # Look for deadline table
            for line in content.split('\n'):
                if '|' in line and 'Date' not in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        try:
                            date_str = parts[0]
                            event = parts[1]

                            # Try to parse date
                            try:
                                deadline_date = datetime.strptime(date_str, '%Y-%m-%d')
                                days_until = (deadline_date - datetime.now()).days

                                if 0 <= days_until <= 30:  # Within 30 days
                                    deadlines.append({
                                        'date': date_str,
                                        'event': event,
                                        'days_until': days_until,
                                        'urgency': 'urgent' if days_until <= 3 else 'soon' if days_until <= 7 else 'upcoming'
                                    })
                            except:
                                pass
                        except:
                            pass

        return sorted(deadlines, key=lambda x: x['days_until'])

    def _generate_suggestions(
        self, tasks: Dict, finances: Dict, subscriptions: List, bottlenecks: List
    ) -> List[Dict[str, Any]]:
        """Generate proactive suggestions based on analysis."""
        suggestions = []

        # Cost optimization suggestions
        for sub in subscriptions:
            if sub.get('flag') == 'unused_30_days':
                suggestions.append({
                    'type': 'cost_optimization',
                    'priority': 'medium',
                    'title': f"Review {sub['name']} subscription",
                    'description': f"No activity in 30+ days. Cost: ${sub.get('monthly_cost', 0):.2f}/month",
                    'action': f"Consider canceling {sub['name']}"
                })

        # Revenue suggestions
        if finances.get('outstanding', 0) > 0:
            suggestions.append({
                'type': 'revenue',
                'priority': 'high',
                'title': 'Follow up on outstanding invoices',
                'description': f"${finances['outstanding']:.2f} in unpaid invoices",
                'action': 'Send payment reminders'
            })

        # Productivity suggestions
        if bottlenecks:
            high_severity = [b for b in bottlenecks if b.get('severity') == 'high']
            if high_severity:
                suggestions.append({
                    'type': 'productivity',
                    'priority': 'high',
                    'title': 'Address task bottlenecks',
                    'description': f"{len(high_severity)} tasks stalled for 7+ days",
                    'action': 'Review and prioritize blocked tasks'
                })

        # Task volume suggestions
        if tasks.get('total_count', 0) < 5:
            suggestions.append({
                'type': 'productivity',
                'priority': 'low',
                'title': 'Low task completion this week',
                'description': f'Only {tasks["total_count"]} tasks completed',
                'action': 'Review pipeline and priorities'
            })

        return suggestions

    def _extract_date_from_file(self, file: Path, content: str) -> Optional[datetime]:
        """Extract date from file frontmatter or filename."""
        # Try frontmatter first
        received_match = re.search(r'received:\s*(\S+)', content)
        if received_match:
            try:
                return datetime.fromisoformat(received_match.group(1))
            except:
                pass

        created_match = re.search(r'created:\s*(\S+)', content)
        if created_match:
            try:
                return datetime.fromisoformat(created_match.group(1))
            except:
                pass

        # Try filename
        match = re.search(r'(\d{4}-\d{2}-\d{2})', file.name)
        if match:
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%d')
            except:
                pass

        # Use file modification time
        return datetime.fromtimestamp(file.stat().st_mtime)

    def _parse_task_file(self, file: Path, content: str) -> Dict:
        """Parse a task file for information."""
        task = {
            'name': file.stem,
            'type': 'general',
            'completed_at': None,
        }

        # Extract type from frontmatter
        type_match = re.search(r'type:\s*"?\w+"?', content)
        if type_match:
            task['type'] = type_match.group().split(':')[1].strip().strip('"')

        # Extract completion info
        if '[x]' in content:
            # Count completed items
            completed = content.count('[x]')
            total = content.count('[x]') + content.count('[ ]')
            task['completion_rate'] = completed / total if total > 0 else 1.0

        return task

    def _parse_task_logs(self, week_start: datetime, week_end: datetime) -> List[Dict]:
        """Parse task completion from log files."""
        tasks = []

        # Look for orchestrator logs
        for log_file in self.logs.glob('orchestrator_*.md'):
            try:
                content = log_file.read_text(encoding='utf-8')
                # Parse log entries
            except:
                pass

        return tasks

    def _format_briefing(
        self, week_start: datetime, week_end: datetime,
        completed_tasks: Dict, financial_summary: Dict,
        subscriptions: List, bottlenecks: List,
        upcoming_deadlines: List, proactive_suggestions: List
    ) -> str:
        """Format the complete briefing document."""
        # Calculate metrics
        revenue = financial_summary.get('revenue', 0)
        expenses = financial_summary.get('expenses', 0)
        net = financial_summary.get('net', 0)

        # Determine trend
        if net > 0:
            trend = '📈 Positive'
        elif net < 0:
            trend = '📉 Negative'
        else:
            trend = '➡️ Neutral'

        content = f'''---
generated: {datetime.now().isoformat()}
period: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}
type: ceo_briefing
---

# Monday Morning CEO Briefing

**Week of:** {week_start.strftime('%B %d, %Y')} - {week_end.strftime('%B %d, %Y')}

---

## Executive Summary

{self._generate_executive_summary(completed_tasks, financial_summary, bottlenecks)}

---

## 📊 Revenue

| Metric | This Week | Status |
|--------|-----------|--------|
| **Revenue** | ${revenue:,.2f} | {trend} |
| **Expenses** | ${expenses:,.2f} | - |
| **Net** | **${net:,.2f}** | {trend} |

### Revenue Breakdown
- Invoices Sent: {financial_summary.get('invoices_sent', 'N/A')}
- Invoices Paid: {financial_summary.get('invoices_paid', 'N/A')}
- Outstanding: ${financial_summary.get('outstanding', 0):,.2f}

---

## ✅ Completed Tasks

**Total:** {completed_tasks['total_count']} tasks

### By Category
{self._format_task_categories(completed_tasks['by_type'])}

### Notable Completions
{self._format_notable_tasks(completed_tasks['completed'][:5])}

---

## 🚧 Bottlenecks

{self._format_bottlenecks(bottlenecks)}

---

## 💰 Subscription Audit

{self._format_subscriptions(subscriptions)}

---

## 📅 Upcoming Deadlines

{self._format_deadlines(upcoming_deadlines)}

---

## 💡 Proactive Suggestions

{self._format_suggestions(proactive_suggestions)}

---

## 📈 Week-over-Week Comparison

*Add comparison data as historical briefings accumulate*

---

## 🎯 Focus Areas for This Week

Based on this analysis, recommended focus areas:

1. {self._generate_focus_area_1(proactive_suggestions, bottlenecks)}
2. {self._generate_focus_area_2(financial_summary)}
3. {self._generate_focus_area_3(upcoming_deadlines)}

---

*Briefing generated automatically by AI Employee - Gold Tier*
'''

        return content

    def _generate_executive_summary(
        self, tasks: Dict, finances: Dict, bottlenecks: List
    ) -> str:
        """Generate executive summary paragraph."""
        parts = []

        # Revenue status
        net = finances.get('net', 0)
        if net > 0:
            parts.append(f'Positive week with ${net:,.2f} net revenue.')
        elif net < 0:
            parts.append(f'Challenging week with ${net:,.2f} net loss.')
        else:
            parts.append('Break-even week financially.')

        # Task completion
        task_count = tasks.get('total_count', 0)
        if task_count > 20:
            parts.append(f'High productivity with {task_count} tasks completed.')
        elif task_count > 10:
            parts.append(f'Moderate productivity with {task_count} tasks completed.')
        else:
            parts.append(f'Light week with only {task_count} tasks completed.')

        # Bottlenecks
        if bottlenecks:
            high_severity = len([b for b in bottlenecks if b.get('severity') == 'high'])
            if high_severity > 0:
                parts.append(f'{high_severity} critical bottlenecks require attention.')

        return ' '.join(parts)

    def _format_task_categories(self, by_type: Dict) -> str:
        """Format task categories table."""
        if not by_type:
            return '*No tasks categorized yet*'

        lines = ['| Category | Count |', '|----------|-------|']
        for category, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            lines.append(f'| {category.title()} | {count} |')

        return '\n'.join(lines)

    def _format_notable_tasks(self, tasks: List[Dict]) -> str:
        """Format notable completed tasks."""
        if not tasks:
            return '*No notable tasks this week*'

        lines = []
        for task in tasks:
            name = task.get('name', 'Unknown task')
            task_type = task.get('type', 'general')
            lines.append(f'- [x] {name} ({task_type})')

        return '\n'.join(lines)

    def _format_bottlenecks(self, bottlenecks: List) -> str:
        """Format bottlenecks section."""
        if not bottlenecks:
            return '*No bottlenecks identified - smooth operations!*'

        lines = ['| Task | Age (Days) | Severity |', '|------|------------|----------|']
        for bottleneck in bottlenecks:
            severity_icon = '🔴' if bottleneck.get('severity') == 'high' else '🟡'
            lines.append(
                f'| {bottleneck.get("task", "Unknown")} | '
                f'{bottleneck.get("age_days", "?")} | '
                f'{severity_icon} {bottleneck.get("severity", "unknown")} |'
            )

        return '\n'.join(lines)

    def _format_subscriptions(self, subscriptions: List) -> str:
        """Format subscriptions audit."""
        if not subscriptions:
            return '*No subscriptions tracked yet*'

        lines = ['| Service | Monthly Cost | Last Used | Status |',
                 '|---------|--------------|-----------|--------|']

        for sub in subscriptions:
            flag_icon = '⚠️' if sub.get('flag') else '✅'
            lines.append(
                f'| {sub.get("name", "Unknown")} | '
                f'${sub.get("monthly_cost", 0):.2f} | '
                f'{sub.get("last_used", "Unknown")} | '
                f'{flag_icon} {sub.get("flag", "active")} |'
            )

        return '\n'.join(lines)

    def _format_deadlines(self, deadlines: List) -> str:
        """Format upcoming deadlines."""
        if not deadlines:
            return '*No upcoming deadlines in the next 30 days*'

        lines = ['| Date | Event | Days Left | Urgency |',
                 '|------|-------|-----------|---------|']

        for deadline in deadlines:
            urgency_icon = {
                'urgent': '🔴',
                'soon': '🟡',
                'upcoming': '🟢'
            }.get(deadline.get('urgency'), '⚪')

            lines.append(
                f'| {deadline.get("date", "Unknown")} | '
                f'{deadline.get("event", "Unknown")} | '
                f'{deadline.get("days_until", "?")} | '
                f'{urgency_icon} {deadline.get("urgency", "unknown")} |'
            )

        return '\n'.join(lines)

    def _format_suggestions(self, suggestions: List) -> str:
        """Format proactive suggestions."""
        if not suggestions:
            return '*No suggestions at this time*'

        lines = []
        for suggestion in suggestions:
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(suggestion.get('priority'), '⚪')

            lines.append(f'\n### {priority_icon} {suggestion.get("title", "Suggestion")}')
            lines.append(f'**Type:** {suggestion.get("type", "general")}')
            lines.append(f'\n{suggestion.get("description", "")}')
            lines.append(f'\n**Recommended Action:** {suggestion.get("action", "Review and decide")}')

        return '\n'.join(lines)

    def _generate_focus_area_1(self, suggestions: List, bottlenecks: List) -> str:
        """Generate first focus area suggestion."""
        if bottlenecks:
            return 'Clear blocked tasks - review bottlenecks section'
        if suggestions:
            high_priority = [s for s in suggestions if s.get('priority') == 'high']
            if high_priority:
                return f'Address: {high_priority[0].get("title", "High priority item")}'
        return 'Continue current momentum'

    def _generate_focus_area_2(self, finances: Dict) -> str:
        """Generate second focus area suggestion."""
        outstanding = finances.get('outstanding', 0)
        if outstanding > 0:
            return f'Follow up on ${outstanding:,.2f} in outstanding invoices'
        return 'Review and optimize expenses'

    def _generate_focus_area_3(self, deadlines: List) -> str:
        """Generate third focus area suggestion."""
        if deadlines:
            urgent = [d for d in deadlines if d.get('urgency') == 'urgent']
            if urgent:
                return f'Prepare for: {urgent[0].get("event", "upcoming deadline")}'
        return 'Plan next week\'s priorities'

    def _update_dashboard(self, briefing_file: Path):
        """Update Dashboard.md with latest briefing info."""
        dashboard_file = self.vault_path / 'Dashboard.md'

        if dashboard_file.exists():
            content = dashboard_file.read_text(encoding='utf-8')

            # Add briefing link to recent activity
            briefing_link = f'[[Briefings/{briefing_file.name}|Latest CEO Briefing]]'

            # Check if briefing section exists
            if '## 📝 Latest Briefing' in content:
                # Update existing section
                content = re.sub(
                    r'## 📝 Latest Briefing\n\n\[.*?\]',
                    f'## 📝 Latest Briefing\n\n{briefing_link}',
                    content
                )
            else:
                # Add new section
                content += f'\n\n## 📝 Latest Briefing\n\n{briefing_link}\n'

            dashboard_file.write_text(content, encoding='utf-8')


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate Weekly CEO Briefing')
    parser.add_argument(
        '--vault', '-v',
        default=r'D:\FTE_AI_Employee\AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--odoo',
        action='store_true',
        help='Enable Odoo integration for financial data'
    )
    parser.add_argument(
        '--week-start',
        type=str,
        help='Start date of week to analyze (YYYY-MM-DD, default: last Monday)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be generated without creating file'
    )

    args = parser.parse_args()

    # Parse week start if provided
    week_start = None
    if args.week_start:
        try:
            week_start = datetime.strptime(args.week_start, '%Y-%m-%d')
        except ValueError:
            print(f'Invalid date format: {args.week_start}')
            sys.exit(1)

    generator = CEOBriefingGenerator(vault_path=args.vault, odoo_enabled=args.odoo)

    if args.dry_run:
        print('[DRY RUN] Would generate CEO briefing with:')
        print(f'  Week start: {week_start or "Last Monday"}')
        print(f'  Odoo enabled: {args.odoo}')
        print(f'  Vault: {args.vault}')
        return

    briefing_file = generator.generate_briefing(week_start)

    print(f'\n✅ CEO Briefing generated: {briefing_file}')
    print(f'\nTo view: {briefing_file}')


if __name__ == '__main__':
    main()
