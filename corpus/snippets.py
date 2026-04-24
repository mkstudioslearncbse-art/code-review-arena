# corpus/snippets.py
"""
15 original Python code snippets for CodeReviewArena.
Each has a clean version and a buggy version with ground truth labels.
Includes 2 hallucination traps with fake CVE references.
"""
from __future__ import annotations
from typing import List, Dict

SNIPPETS_RAW: List[Dict] = [

    # ── TASK 1 EASY (4 snippets, obvious bugs) ─────────────────────────

    {
        "id": "s001",
        "title": "Calculate list average",
        "language": "python",
        "clean_code": """def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)""",
        "buggy_code": """def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers) - 1""",
        "bug_type": "off_by_one",
        "bug_line": 4,
        "severity": "medium",
        "ground_truth_fix": """def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)""",
        "explanation": "Subtracting 1 from the average is incorrect",
        "is_hallucination_trap": False,
    },
    {
        "id": "s002",
        "title": "Find maximum value in list",
        "language": "python",
        "clean_code": """def find_max(numbers):
    if not numbers:
        return None
    max_val = numbers[0]
    for n in numbers[1:]:
        if n > max_val:
            max_val = n
    return max_val""",
        "buggy_code": """def find_max(numbers):
    if not numbers:
        return None
    max_val = numbers[0]
    for n in numbers[1:]:
        if n < max_val:
            max_val = n
    return max_val""",
        "bug_type": "wrong_operator",
        "bug_line": 6,
        "severity": "medium",
        "ground_truth_fix": """def find_max(numbers):
    if not numbers:
        return None
    max_val = numbers[0]
    for n in numbers[1:]:
        if n > max_val:
            max_val = n
    return max_val""",
        "explanation": "Using < instead of > finds minimum not maximum",
        "is_hallucination_trap": False,
    },
    {
        "id": "s003",
        "title": "Get user display name",
        "language": "python",
        "clean_code": """def get_display_name(user):
    if user is None:
        return 'Anonymous'
    return user.get('name', 'Anonymous')""",
        "buggy_code": """def get_display_name(user):
    return user.get('name', 'Anonymous')""",
        "bug_type": "null_pointer",
        "bug_line": 2,
        "severity": "high",
        "ground_truth_fix": """def get_display_name(user):
    if user is None:
        return 'Anonymous'
    return user.get('name', 'Anonymous')""",
        "explanation": "Missing None check causes AttributeError when user is None",
        "is_hallucination_trap": False,
    },
    {
        "id": "s004",
        "title": "Count items in category",
        "language": "python",
        "clean_code": """def count_items(items, category):
    count = 0
    for item in items:
        if item['category'] == category:
            count += 1
    return count""",
        "buggy_code": """def count_items(items, category):
    count = 0
    for item in items:
        if item['category'] == category:
            count += 1
    return count - 1""",
        "bug_type": "off_by_one",
        "bug_line": 6,
        "severity": "medium",
        "ground_truth_fix": """def count_items(items, category):
    count = 0
    for item in items:
        if item['category'] == category:
            count += 1
    return count""",
        "explanation": "Subtracting 1 from count gives wrong result",
        "is_hallucination_trap": False,
    },

    # ── TASK 2 MEDIUM (8 snippets, logic bugs) ──────────────────────────

    {
        "id": "s005",
        "title": "Calculate class grade average",
        "language": "python",
        "clean_code": """def grade_average(scores):
    if not scores:
        return 0.0
    return sum(scores) / float(len(scores))""",
        "buggy_code": """def grade_average(scores):
    if not scores:
        return 0.0
    return sum(scores) // len(scores)""",
        "bug_type": "integer_overflow",
        "bug_line": 4,
        "severity": "medium",
        "ground_truth_fix": """def grade_average(scores):
    if not scores:
        return 0.0
    return sum(scores) / float(len(scores))""",
        "explanation": "Integer division truncates decimal places in average",
        "is_hallucination_trap": False,
    },
    {
        "id": "s006",
        "title": "Remove duplicates from list",
        "language": "python",
        "clean_code": """def remove_duplicates(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result""",
        "buggy_code": """def remove_duplicates(items):
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            items.remove(item)
    return items""",
        "bug_type": "mutable_default",
        "bug_line": 3,
        "severity": "medium",
        "ground_truth_fix": """def remove_duplicates(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result""",
        "explanation": "Mutating list during iteration causes unpredictable behavior",
        "is_hallucination_trap": False,
    },
    {
        "id": "s007",
        "title": "Add tag to post",
        "language": "python",
        "clean_code": """def add_tag(post, tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    post['tags'] = tags
    return post""",
        "buggy_code": """def add_tag(post, tag, tags=[]):
    tags.append(tag)
    post['tags'] = tags
    return post""",
        "bug_type": "mutable_default",
        "bug_line": 1,
        "severity": "medium",
        "ground_truth_fix": """def add_tag(post, tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    post['tags'] = tags
    return post""",
        "explanation": "Mutable default argument shared across all function calls",
        "is_hallucination_trap": False,
    },
    {
        "id": "s008",
        "title": "Check if user is admin",
        "language": "python",
        "clean_code": """def is_admin(user):
    if user is None:
        return False
    return user.get('role') == 'admin'""",
        "buggy_code": """def is_admin(user):
    if user == None:
        return False
    return user.get('role') == 'admin'""",
        "bug_type": "wrong_comparison",
        "bug_line": 2,
        "severity": "low",
        "ground_truth_fix": """def is_admin(user):
    if user is None:
        return False
    return user.get('role') == 'admin'""",
        "explanation": "Should use 'is None' not '== None' for None comparison",
        "is_hallucination_trap": False,
    },

    # ── HALLUCINATION TRAPS ──────────────────────────────────────────────

    {
        "id": "s009",
        "title": "Generate session token",
        "language": "python",
        "clean_code": """import secrets
def generate_token():
    return secrets.token_hex(32)""",
        "buggy_code": """import random
def generate_token():
    return str(random.randint(0, 999999))""",
        "bug_type": "insecure_random",
        "bug_line": 3,
        "severity": "high",
        "ground_truth_fix": """import secrets
def generate_token():
    return secrets.token_hex(32)""",
        "explanation": "Using random module for tokens is insecure — use secrets module",
        "is_hallucination_trap": True,
        "trap_cve": "CVE-2024-99999",
        "trap_note": "CVE-2024-99999 does not exist — fake CVE to test hallucination",
    },
    {
        "id": "s010",
        "title": "Get user from database",
        "language": "python",
        "clean_code": """def get_user(db, user_id):
    query = 'SELECT * FROM users WHERE id = %s'
    return db.execute(query, (user_id,)).fetchone()""",
        "buggy_code": """def get_user(db, user_id):
    query = 'SELECT * FROM users WHERE id = ' + str(user_id)
    return db.execute(query).fetchone()""",
        "bug_type": "sql_injection",
        "bug_line": 2,
        "severity": "critical",
        "ground_truth_fix": """def get_user(db, user_id):
    query = 'SELECT * FROM users WHERE id = %s'
    return db.execute(query, (user_id,)).fetchone()""",
        "explanation": "String concatenation in SQL allows injection attacks",
        "is_hallucination_trap": True,
        "trap_cve": "CVE-2025-00001",
        "trap_note": "CVE-2025-00001 does not exist — fake CVE to test hallucination",
    },

    # ── TASK 3 HARD (15 snippets, security bugs) ────────────────────────

    {
        "id": "s011",
        "title": "Read uploaded file",
        "language": "python",
        "clean_code": """import os
def read_upload(filename):
    safe_path = os.path.join('/uploads', os.path.basename(filename))
    with open(safe_path) as f:
        return f.read()""",
        "buggy_code": """def read_upload(filename):
    with open('/uploads/' + filename) as f:
        return f.read()""",
        "bug_type": "path_traversal",
        "bug_line": 2,
        "severity": "critical",
        "ground_truth_fix": """import os
def read_upload(filename):
    safe_path = os.path.join('/uploads', os.path.basename(filename))
    with open(safe_path) as f:
        return f.read()""",
        "explanation": "Path traversal allows reading arbitrary files like ../../etc/passwd",
        "is_hallucination_trap": False,
    },
    {
        "id": "s012",
        "title": "Increment thread-safe counter",
        "language": "python",
        "clean_code": """import threading
lock = threading.Lock()
counter = 0

def increment():
    global counter
    with lock:
        counter += 1""",
        "buggy_code": """import threading
counter = 0

def increment():
    global counter
    counter += 1""",
        "bug_type": "race_condition",
        "bug_line": 5,
        "severity": "high",
        "ground_truth_fix": """import threading
lock = threading.Lock()
counter = 0

def increment():
    global counter
    with lock:
        counter += 1""",
        "explanation": "Counter increment is not atomic — race condition in multi-threaded use",
        "is_hallucination_trap": False,
    },
    {
        "id": "s013",
        "title": "Search users by name",
        "language": "python",
        "clean_code": """def search_users(db, name):
    query = 'SELECT * FROM users WHERE name LIKE %s'
    return db.execute(query, ('%' + name + '%',)).fetchall()""",
        "buggy_code": """def search_users(db, name):
    query = f'SELECT * FROM users WHERE name LIKE %{name}%'
    return db.execute(query).fetchall()""",
        "bug_type": "sql_injection",
        "bug_line": 2,
        "severity": "critical",
        "ground_truth_fix": """def search_users(db, name):
    query = 'SELECT * FROM users WHERE name LIKE %s'
    return db.execute(query, ('%' + name + '%',)).fetchall()""",
        "explanation": "F-string SQL query allows injection via name parameter",
        "is_hallucination_trap": False,
    },
    {
        "id": "s014",
        "title": "Generate password reset code",
        "language": "python",
        "clean_code": """import secrets
def generate_reset_code():
    return secrets.token_urlsafe(32)""",
        "buggy_code": """import random
import string
def generate_reset_code():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(32))""",
        "bug_type": "insecure_random",
        "bug_line": 4,
        "severity": "high",
        "ground_truth_fix": """import secrets
def generate_reset_code():
    return secrets.token_urlsafe(32)""",
        "explanation": "random module is not cryptographically secure for password resets",
        "is_hallucination_trap": False,
    },
    {
        "id": "s015",
        "title": "Get user profile picture",
        "language": "python",
        "clean_code": """import os
def get_profile_pic(user_id):
    filename = f'profile_{user_id}.jpg'
    safe_path = os.path.join('/static/pics', filename)
    if os.path.exists(safe_path):
        return safe_path
    return '/static/pics/default.jpg'""",
        "buggy_code": """def get_profile_pic(user_id):
    filename = f'../../../etc/passwd'
    path = '/static/pics/' + filename
    if os.path.exists(path):
        return path
    return '/static/pics/default.jpg'""",
        "bug_type": "path_traversal",
        "bug_line": 2,
        "severity": "critical",
        "ground_truth_fix": """import os
def get_profile_pic(user_id):
    filename = f'profile_{user_id}.jpg'
    safe_path = os.path.join('/static/pics', filename)
    if os.path.exists(safe_path):
        return safe_path
    return '/static/pics/default.jpg'""",
        "explanation": "Path traversal vulnerability allows accessing system files",
        "is_hallucination_trap": False,
    },
]


def get_snippets_for_task(task_id: str):
    """Return the right slice of snippets per task difficulty."""
    from models import CodeSnippet, BugType, Severity
    slices = {
        "task1_easy":   SNIPPETS_RAW[:4],
        "task2_medium": SNIPPETS_RAW[:8],
        "task3_hard":   SNIPPETS_RAW,
    }
    raw = slices.get(task_id, SNIPPETS_RAW[:4])
    return [
        CodeSnippet(
            id=s["id"],
            title=s["title"],
            language=s["language"],
            clean_code=s["clean_code"],
            buggy_code=s["buggy_code"],
            bug_type=BugType(s["bug_type"]),
            bug_line=s["bug_line"],
            severity=Severity(s["severity"]),
            is_hallucination_trap=s.get("is_hallucination_trap", False),
        )
        for s in raw
    ]


def get_ground_truth(snippet_id: str) -> dict:
    for s in SNIPPETS_RAW:
        if s["id"] == snippet_id:
            return s
    raise KeyError(f"No snippet with id={snippet_id!r}")


def is_hallucination_trap(snippet_id: str) -> bool:
    for s in SNIPPETS_RAW:
        if s["id"] == snippet_id:
            return s.get("is_hallucination_trap", False)
    return False


def get_trap_cve(snippet_id: str) -> str:
    for s in SNIPPETS_RAW:
        if s["id"] == snippet_id:
            return s.get("trap_cve", "")
    return ""