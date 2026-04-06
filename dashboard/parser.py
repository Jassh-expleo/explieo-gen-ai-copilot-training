"""
Markdown parser for Explieo agent workflow files.
Parses approval-board.md, planning-review.md, architecture-review.md, implementation-review.md.
"""
import re
from pathlib import Path


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _strip_markdown_bold(text: str) -> str:
    return re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text).strip()


def _strip_emojis(text: str) -> str:
    for ch in ['✅', '⏳', '❌', '⚠️', '🔄', '⏸', '▶', '●', '○']:
        text = text.replace(ch, '')
    return text.strip()


def _normalize_status(raw: str) -> str:
    s = _strip_markdown_bold(_strip_emojis(raw)).lower()
    if 'approved' in s:
        return 'approved'
    if 'awaiting' in s or 'pending' in s:
        return 'awaiting'
    if 'in progress' in s:
        return 'in_progress'
    if 'changes' in s or 'rejected' in s or 'request' in s:
        return 'changes_requested'
    if 'hold' in s:
        return 'on_hold'
    if s in ('-', '', 'not started'):
        return 'not_started'
    return 'not_started'


def _parse_table_block(block: str) -> list:
    """Parse a markdown table string into a list of row dicts."""
    lines = [l.strip() for l in block.strip().split('\n') if l.strip().startswith('|')]
    if len(lines) < 3:
        return []

    def cells(line):
        parts = line.split('|')
        return [p.strip() for p in parts[1:-1]]

    headers = cells(lines[0])
    rows = []
    for line in lines[2:]:  # skip separator
        vals = cells(line)
        while len(vals) < len(headers):
            vals.append('')
        rows.append({headers[i]: vals[i] for i in range(len(headers))})
    return rows


def _find_section(content: str, heading: str) -> str:
    """Return text content under a markdown heading (stops at next heading)."""
    pattern = rf'(?:^|\n)#+\s*{re.escape(heading)}\s*\n([\s\S]*?)(?=\n#+\s|\Z)'
    m = re.search(pattern, content, re.IGNORECASE)
    return m.group(1) if m else ''


def _extract_table(section_text: str) -> list:
    """Find the first markdown table in a section and parse it."""
    m = re.search(r'(\|[^\n]+\n\|[-| :]+\n(?:\|[^\n]+\n?)+)', section_text)
    if not m:
        return []
    return _parse_table_block(m.group(1))


# ─── Approval Board ───────────────────────────────────────────────────────────

def _parse_approval_board(content: str) -> dict:
    result = {
        'metadata': {},
        'stages': {
            'architecture': {'status': 'not_started', 'owner': '', 'summary': '', 'decision': ''},
            'planning':     {'status': 'not_started', 'owner': '', 'summary': '', 'decision': ''},
            'implementation': {'status': 'not_started', 'owner': '', 'summary': '', 'decision': ''},
        },
        'board_tasks': [],
        'approval_log': {'architecture_approved': False, 'planning_approved': False, 'implementation_approved': False},
        'open_questions': [],
    }

    # Workflow metadata (bullet list)
    meta_section = _find_section(content, 'Workflow Metadata')
    for line in meta_section.split('\n'):
        line = line.strip()
        if line.startswith('- '):
            parts = line[2:].split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip().lower().replace(' ', '_')
                val = parts[1].strip().strip('`')
                result['metadata'][key] = val

    # Stage Status table
    stage_section = _find_section(content, 'Stage Status')
    for row in _extract_table(stage_section):
        name = _strip_emojis(row.get('Stage', '')).lower().strip()
        if name in result['stages']:
            result['stages'][name] = {
                'status': _normalize_status(row.get('Status', '')),
                'owner': _strip_emojis(row.get('Owner', '')),
                'summary': row.get('Summary', ''),
                'decision': _strip_markdown_bold(row.get('Decision', '')),
            }

    # Task Tracking table
    task_section = _find_section(content, 'Task Tracking')
    for row in _extract_table(task_section):
        result['board_tasks'].append({
            'id': row.get('Task ID', ''),
            'title': row.get('Title', ''),
            'status': _normalize_status(row.get('Status', 'not_started')),
            'validation': row.get('Validation', ''),
            'notes': row.get('Notes', ''),
        })

    # Approval Log checkboxes
    for m in re.finditer(r'- \[([ xX])\] (.*?)$', content, re.MULTILINE):
        checked = m.group(1).lower() == 'x'
        label = m.group(2).strip().lower().replace(' ', '_')
        result['approval_log'][label] = checked

    # Open Questions
    q_section = _find_section(content, 'Open Questions')
    for line in q_section.split('\n'):
        line = line.strip()
        if line.startswith('- '):
            result['open_questions'].append(line[2:])

    return result


# ─── Planning Review ──────────────────────────────────────────────────────────

def _parse_planning_review(content: str) -> dict:
    result = {'tasks': [], 'risks': [], 'definition_of_done': []}

    # Task List
    task_section = _find_section(content, 'Task List')
    for row in _extract_table(task_section):
        result['tasks'].append({
            'id': row.get('ID', ''),
            'title': row.get('Title', ''),
            'complexity': row.get('Complexity', ''),
            'depends_on': row.get('Depends On', ''),
            'status': 'not_started',
        })

    # Key Risks
    risk_section = _find_section(content, 'Key Risks')
    for row in _extract_table(risk_section):
        result['risks'].append({
            'id': row.get('ID', ''),
            'risk': row.get('Risk', ''),
            'mitigation': row.get('Mitigation', ''),
        })

    # Definition of Done checkboxes
    dod_section = _find_section(content, 'Definition of Done')
    for m in re.finditer(r'- \[([ xX])\] (.*?)$', dod_section, re.MULTILINE):
        result['definition_of_done'].append({
            'done': m.group(1).lower() == 'x',
            'item': m.group(2).strip(),
        })

    return result


# ─── Architecture Review ──────────────────────────────────────────────────────

def _parse_architecture_review(content: str) -> dict:
    result = {'sections': {}}
    headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
    for h in headings:
        section_text = _find_section(content, h).strip()
        if section_text:
            result['sections'][h] = section_text[:800]  # cap for UI
    return result


# ─── Implementation Review ───────────────────────────────────────────────────

def _parse_implementation_review(content: str) -> dict:
    result = {'sections': {}}
    headings = re.findall(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
    for h in headings:
        section_text = _find_section(content, h).strip()
        if section_text:
            result['sections'][h] = section_text[:800]
    return result


# ─── Public API ───────────────────────────────────────────────────────────────

def parse_run(run_path: Path) -> dict:
    """Parse all markdown files in a run directory into a unified dict."""
    run = {
        'path': str(run_path),
        'display_name': run_path.name,
        'name': run_path.name,
        'status': 'unknown',
        'metadata': {},
        'stages': {
            'architecture': {'status': 'not_started', 'owner': '', 'summary': '', 'decision': ''},
            'planning':     {'status': 'not_started', 'owner': '', 'summary': '', 'decision': ''},
            'implementation': {'status': 'not_started', 'owner': '', 'summary': '', 'decision': ''},
        },
        'tasks': [],
        'risks': [],
        'approval_log': {},
        'open_questions': [],
        'definition_of_done': [],
        'available_files': [],
        'last_modified': 0,
    }

    # Discover files
    for f in run_path.iterdir():
        if f.suffix == '.md':
            run['available_files'].append(f.stem)
            mtime = f.stat().st_mtime
            if mtime > run['last_modified']:
                run['last_modified'] = mtime

    # Parse approval board
    board_path = run_path / 'approval-board.md'
    if board_path.exists():
        board = _parse_approval_board(board_path.read_text())
        run['metadata'] = board['metadata']
        run['stages'] = board['stages']
        run['approval_log'] = board['approval_log']
        run['open_questions'] = board['open_questions']
        run['status'] = board['metadata'].get('status', 'unknown')
        run['name'] = board['metadata'].get('run_name', run_path.name)
        # Use board tasks as fallback
        if board['board_tasks']:
            run['tasks'] = board['board_tasks']

    # Parse planning review (richer task data)
    planning_path = run_path / 'planning-review.md'
    if planning_path.exists():
        planning = _parse_planning_review(planning_path.read_text())
        if planning['tasks']:
            # Merge status from board tasks
            board_status = {t['id']: t['status'] for t in run['tasks']}
            for task in planning['tasks']:
                task['status'] = board_status.get(task['id'], 'not_started')
            run['tasks'] = planning['tasks']
        if planning['risks']:
            run['risks'] = planning['risks']
        if planning['definition_of_done']:
            run['definition_of_done'] = planning['definition_of_done']

    return run


def list_runs(runs_dir: Path) -> list:
    """Return a summary list of all runs, sorted by last modified (newest first)."""
    if not runs_dir.exists():
        return []

    runs = []
    for path in runs_dir.iterdir():
        if path.is_dir() and not path.name.startswith('.'):
            try:
                run = parse_run(path)
                runs.append({
                    'name': run['name'],
                    'display_name': run['display_name'],
                    'status': run['status'],
                    'stages': run['stages'],
                    'last_modified': run['last_modified'],
                    'metadata': run['metadata'],
                })
            except Exception as e:
                runs.append({
                    'name': path.name,
                    'display_name': path.name,
                    'status': 'error',
                    'stages': {},
                    'last_modified': 0,
                    'metadata': {},
                    'error': str(e),
                })

    return sorted(runs, key=lambda r: r['last_modified'], reverse=True)
