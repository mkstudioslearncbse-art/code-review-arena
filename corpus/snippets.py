# corpus/snippets.py
"""
18 original Python code snippets for CodeReviewArena.
15 standard snippets + 3 long-horizon multi-bug files.
"""
from __future__ import annotations
from typing import List, Dict

SNIPPETS_RAW: List[Dict] = [

    # ── TASK 1 EASY (4 snippets) ─────────────────────────────────────────

    {
        "id": "s001",
        "title": "Calculate list average",
        "language": "python",
        "clean_code": "def calculate_average(numbers):\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)",
        "buggy_code": "def calculate_average(numbers):\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers) - 1",
        "bug_type": "off_by_one",
        "bug_line": 4,
        "severity": "medium",
        "ground_truth_fix": "return sum(numbers) / len(numbers)",
        "explanation": "Subtracting 1 from the average is incorrect",
        "is_hallucination_trap": False,
    },
    {
        "id": "s002",
        "title": "Find maximum value in list",
        "language": "python",
        "clean_code": "def find_max(numbers):\n    if not numbers:\n        return None\n    max_val = numbers[0]\n    for n in numbers[1:]:\n        if n > max_val:\n            max_val = n\n    return max_val",
        "buggy_code": "def find_max(numbers):\n    if not numbers:\n        return None\n    max_val = numbers[0]\n    for n in numbers[1:]:\n        if n < max_val:\n            max_val = n\n    return max_val",
        "bug_type": "wrong_operator",
        "bug_line": 6,
        "severity": "medium",
        "ground_truth_fix": "if n > max_val:",
        "explanation": "Using < instead of > finds minimum not maximum",
        "is_hallucination_trap": False,
    },
    {
        "id": "s003",
        "title": "Get user display name",
        "language": "python",
        "clean_code": "def get_display_name(user):\n    if user is None:\n        return 'Anonymous'\n    return user.get('name', 'Anonymous')",
        "buggy_code": "def get_display_name(user):\n    return user.get('name', 'Anonymous')",
        "bug_type": "null_pointer",
        "bug_line": 2,
        "severity": "high",
        "ground_truth_fix": "if user is None:\n    return 'Anonymous'",
        "explanation": "Missing None check causes AttributeError when user is None",
        "is_hallucination_trap": False,
    },
    {
        "id": "s004",
        "title": "Count items in category",
        "language": "python",
        "clean_code": "def count_items(items, category):\n    count = 0\n    for item in items:\n        if item['category'] == category:\n            count += 1\n    return count",
        "buggy_code": "def count_items(items, category):\n    count = 0\n    for item in items:\n        if item['category'] == category:\n            count += 1\n    return count - 1",
        "bug_type": "off_by_one",
        "bug_line": 6,
        "severity": "medium",
        "ground_truth_fix": "return count",
        "explanation": "Subtracting 1 from count gives wrong result",
        "is_hallucination_trap": False,
    },

    # ── TASK 2 MEDIUM (8 snippets) ───────────────────────────────────────

    {
        "id": "s005",
        "title": "Calculate class grade average",
        "language": "python",
        "clean_code": "def grade_average(scores):\n    if not scores:\n        return 0.0\n    return sum(scores) / float(len(scores))",
        "buggy_code": "def grade_average(scores):\n    if not scores:\n        return 0.0\n    return sum(scores) // len(scores)",
        "bug_type": "integer_overflow",
        "bug_line": 4,
        "severity": "medium",
        "ground_truth_fix": "return sum(scores) / float(len(scores))",
        "explanation": "Integer division truncates decimal places in average",
        "is_hallucination_trap": False,
    },
    {
        "id": "s006",
        "title": "Remove duplicates from list",
        "language": "python",
        "clean_code": "def remove_duplicates(items):\n    seen = set()\n    result = []\n    for item in items:\n        if item not in seen:\n            seen.add(item)\n            result.append(item)\n    return result",
        "buggy_code": "def remove_duplicates(items):\n    seen = set()\n    for item in items:\n        if item not in seen:\n            seen.add(item)\n            items.remove(item)\n    return items",
        "bug_type": "mutable_default",
        "bug_line": 3,
        "severity": "medium",
        "ground_truth_fix": "result = []\nfor item in items:\n    if item not in seen:\n        seen.add(item)\n        result.append(item)\nreturn result",
        "explanation": "Mutating list during iteration causes unpredictable behavior",
        "is_hallucination_trap": False,
    },
    {
        "id": "s007",
        "title": "Add tag to post",
        "language": "python",
        "clean_code": "def add_tag(post, tag, tags=None):\n    if tags is None:\n        tags = []\n    tags.append(tag)\n    post['tags'] = tags\n    return post",
        "buggy_code": "def add_tag(post, tag, tags=[]):\n    tags.append(tag)\n    post['tags'] = tags\n    return post",
        "bug_type": "mutable_default",
        "bug_line": 1,
        "severity": "medium",
        "ground_truth_fix": "def add_tag(post, tag, tags=None):\n    if tags is None:\n        tags = []",
        "explanation": "Mutable default argument shared across all function calls",
        "is_hallucination_trap": False,
    },
    {
        "id": "s008",
        "title": "Check if user is admin",
        "language": "python",
        "clean_code": "def is_admin(user):\n    if user is None:\n        return False\n    return user.get('role') == 'admin'",
        "buggy_code": "def is_admin(user):\n    if user == None:\n        return False\n    return user.get('role') == 'admin'",
        "bug_type": "wrong_comparison",
        "bug_line": 2,
        "severity": "low",
        "ground_truth_fix": "if user is None:",
        "explanation": "Should use 'is None' not '== None' for None comparison",
        "is_hallucination_trap": False,
    },

    # ── HALLUCINATION TRAPS ──────────────────────────────────────────────

    {
        "id": "s009",
        "title": "Generate session token",
        "language": "python",
        "clean_code": "import secrets\ndef generate_token():\n    return secrets.token_hex(32)",
        "buggy_code": "import random\ndef generate_token():\n    return str(random.randint(0, 999999))",
        "bug_type": "insecure_random",
        "bug_line": 3,
        "severity": "high",
        "ground_truth_fix": "import secrets\ndef generate_token():\n    return secrets.token_hex(32)",
        "explanation": "Using random module for tokens is insecure",
        "is_hallucination_trap": True,
        "trap_cve": "CVE-2024-99999",
    },
    {
        "id": "s010",
        "title": "Get user from database",
        "language": "python",
        "clean_code": "def get_user(db, user_id):\n    query = 'SELECT * FROM users WHERE id = %s'\n    return db.execute(query, (user_id,)).fetchone()",
        "buggy_code": "def get_user(db, user_id):\n    query = 'SELECT * FROM users WHERE id = ' + str(user_id)\n    return db.execute(query).fetchone()",
        "bug_type": "sql_injection",
        "bug_line": 2,
        "severity": "critical",
        "ground_truth_fix": "query = 'SELECT * FROM users WHERE id = %s'\nreturn db.execute(query, (user_id,)).fetchone()",
        "explanation": "String concatenation in SQL allows injection attacks",
        "is_hallucination_trap": True,
        "trap_cve": "CVE-2025-00001",
    },

    # ── TASK 3 HARD (5 more snippets) ────────────────────────────────────

    {
        "id": "s011",
        "title": "Read uploaded file",
        "language": "python",
        "clean_code": "import os\ndef read_upload(filename):\n    safe_path = os.path.join('/uploads', os.path.basename(filename))\n    with open(safe_path) as f:\n        return f.read()",
        "buggy_code": "def read_upload(filename):\n    with open('/uploads/' + filename) as f:\n        return f.read()",
        "bug_type": "path_traversal",
        "bug_line": 2,
        "severity": "critical",
        "ground_truth_fix": "safe_path = os.path.join('/uploads', os.path.basename(filename))",
        "explanation": "Path traversal allows reading arbitrary files",
        "is_hallucination_trap": False,
    },
    {
        "id": "s012",
        "title": "Increment thread-safe counter",
        "language": "python",
        "clean_code": "import threading\nlock = threading.Lock()\ncounter = 0\ndef increment():\n    global counter\n    with lock:\n        counter += 1",
        "buggy_code": "import threading\ncounter = 0\ndef increment():\n    global counter\n    counter += 1",
        "bug_type": "race_condition",
        "bug_line": 5,
        "severity": "high",
        "ground_truth_fix": "lock = threading.Lock()\ndef increment():\n    global counter\n    with lock:\n        counter += 1",
        "explanation": "Counter increment is not atomic — race condition in multi-threaded use",
        "is_hallucination_trap": False,
    },
    {
        "id": "s013",
        "title": "Search users by name",
        "language": "python",
        "clean_code": "def search_users(db, name):\n    query = 'SELECT * FROM users WHERE name LIKE %s'\n    return db.execute(query, ('%' + name + '%',)).fetchall()",
        "buggy_code": "def search_users(db, name):\n    query = f'SELECT * FROM users WHERE name LIKE %{name}%'\n    return db.execute(query).fetchall()",
        "bug_type": "sql_injection",
        "bug_line": 2,
        "severity": "critical",
        "ground_truth_fix": "query = 'SELECT * FROM users WHERE name LIKE %s'\nreturn db.execute(query, ('%' + name + '%',)).fetchall()",
        "explanation": "F-string SQL query allows injection via name parameter",
        "is_hallucination_trap": False,
    },
    {
        "id": "s014",
        "title": "Generate password reset code",
        "language": "python",
        "clean_code": "import secrets\ndef generate_reset_code():\n    return secrets.token_urlsafe(32)",
        "buggy_code": "import random\nimport string\ndef generate_reset_code():\n    chars = string.ascii_letters + string.digits\n    return ''.join(random.choice(chars) for _ in range(32))",
        "bug_type": "insecure_random",
        "bug_line": 4,
        "severity": "high",
        "ground_truth_fix": "import secrets\ndef generate_reset_code():\n    return secrets.token_urlsafe(32)",
        "explanation": "random module is not cryptographically secure for password resets",
        "is_hallucination_trap": False,
    },
    {
        "id": "s015",
        "title": "Get user profile picture",
        "language": "python",
        "clean_code": "import os\ndef get_profile_pic(user_id):\n    filename = f'profile_{user_id}.jpg'\n    safe_path = os.path.join('/static/pics', filename)\n    if os.path.exists(safe_path):\n        return safe_path\n    return '/static/pics/default.jpg'",
        "buggy_code": "def get_profile_pic(user_id):\n    filename = f'../../../etc/passwd'\n    path = '/static/pics/' + filename\n    if os.path.exists(path):\n        return path\n    return '/static/pics/default.jpg'",
        "bug_type": "path_traversal",
        "bug_line": 2,
        "severity": "critical",
        "ground_truth_fix": "filename = f'profile_{user_id}.jpg'\nsafe_path = os.path.join('/static/pics', filename)",
        "explanation": "Path traversal vulnerability allows accessing system files",
        "is_hallucination_trap": False,
    },

    # ── TASK 4 LONG-HORIZON (multi-bug files) ────────────────────────────

    {
        "id": "lh001",
        "title": "Payment Processor — 4 connected bugs",
        "language": "python",
        "clean_code": "class PaymentProcessor:\n    def __init__(self):\n        self.transactions = []\n        self.total = 0.0\n\n    def add_payment(self, amount, currency='USD'):\n        if amount <= 0:\n            raise ValueError('Amount must be positive')\n        self.transactions.append(amount)\n        self.total += amount\n\n    def get_average(self):\n        if not self.transactions:\n            return 0.0\n        return self.total / len(self.transactions)\n\n    def process_refund(self, amount):\n        if amount > self.total:\n            return False\n        self.total -= amount\n        return True",
        "buggy_code": "class PaymentProcessor:\n    def __init__(self):\n        self.transactions = []\n        self.total = 0.0\n\n    def add_payment(self, amount, currency='USD'):\n        self.transactions.append(amount)\n        self.total = self.total + amount\n\n    def get_average(self):\n        return self.total / len(self.transactions)\n\n    def process_refund(self, amount):\n        self.total = self.total - amount\n        return True",
        "bug_type": "null_pointer",
        "bug_line": 7,
        "severity": "high",
        "ground_truth_fix": "if amount <= 0:\n    raise ValueError('Amount must be positive')",
        "explanation": "Missing input validation, division by zero, no refund check — 4 connected bugs requiring sequential analysis",
        "is_hallucination_trap": False,
        "is_multi_bug": True,
        "total_bugs": 4,
        "bug_locations": [7, 11, 14, 17],
    },
    {
        "id": "lh002",
        "title": "User Authentication System — 4 security bugs",
        "language": "python",
        "clean_code": "import hashlib\nimport secrets\n\nclass AuthSystem:\n    def __init__(self):\n        self.users = {}\n\n    def register(self, username, password):\n        if username in self.users:\n            raise ValueError('User already exists')\n        salt = secrets.token_hex(16)\n        hashed = hashlib.sha256((password + salt).encode()).hexdigest()\n        self.users[username] = {'hash': hashed, 'salt': salt}\n        return True\n\n    def login(self, username, password):\n        if username not in self.users:\n            return False\n        user = self.users[username]\n        salt = user['salt']\n        hashed = hashlib.sha256((password + salt).encode()).hexdigest()\n        return hashed == user['hash']",
        "buggy_code": "import hashlib\nimport random\n\nclass AuthSystem:\n    def __init__(self):\n        self.users = {}\n\n    def register(self, username, password):\n        salt = str(random.randint(0, 9999))\n        hashed = hashlib.md5(password.encode()).hexdigest()\n        self.users[username] = {'hash': hashed, 'salt': salt}\n        return True\n\n    def login(self, username, password):\n        user = self.users[username]\n        hashed = hashlib.md5(password.encode()).hexdigest()\n        return hashed == user['hash']",
        "bug_type": "insecure_random",
        "bug_line": 9,
        "severity": "critical",
        "ground_truth_fix": "import secrets\nsalt = secrets.token_hex(16)\nhashed = hashlib.sha256((password + salt).encode()).hexdigest()",
        "explanation": "Insecure random, weak MD5 hash, missing duplicate check, no KeyError handling — 4 connected security bugs",
        "is_hallucination_trap": False,
        "is_multi_bug": True,
        "total_bugs": 4,
        "bug_locations": [9, 10, 15, 16],
    },
    {
        "id": "lh003",
        "title": "File Upload Handler — 4 path traversal bugs",
        "language": "python",
        "clean_code": "import os\nimport hashlib\n\nUPLOAD_DIR = '/uploads'\nMAX_SIZE = 10 * 1024 * 1024\n\ndef save_upload(filename, content, user_id):\n    if not filename or '..' in filename:\n        raise ValueError('Invalid filename')\n    safe_name = os.path.basename(filename)\n    ext = os.path.splitext(safe_name)[1].lower()\n    if ext not in ['.jpg', '.png', '.pdf']:\n        raise ValueError('Invalid file type')\n    if len(content) > MAX_SIZE:\n        raise ValueError('File too large')\n    unique_name = hashlib.md5(f'{user_id}{safe_name}'.encode()).hexdigest() + ext\n    path = os.path.join(UPLOAD_DIR, unique_name)\n    with open(path, 'wb') as f:\n        f.write(content)\n    return unique_name",
        "buggy_code": "import os\n\nUPLOAD_DIR = '/uploads'\n\ndef save_upload(filename, content, user_id):\n    path = UPLOAD_DIR + '/' + filename\n    with open(path, 'wb') as f:\n        f.write(content)\n    return filename",
        "bug_type": "path_traversal",
        "bug_line": 6,
        "severity": "critical",
        "ground_truth_fix": "safe_name = os.path.basename(filename)\npath = os.path.join(UPLOAD_DIR, safe_name)",
        "explanation": "Path traversal, no file type check, no size limit, no unique naming — 4 connected security bugs",
        "is_hallucination_trap": False,
        "is_multi_bug": True,
        "total_bugs": 4,
        "bug_locations": [6, 7, 8, 9],
    },
]


def get_snippets_for_task(task_id: str):
    from models import CodeSnippet, BugType, Severity
    slices = {
        "task1_easy":    SNIPPETS_RAW[:4],
        "task2_medium":  SNIPPETS_RAW[:8],
        "task3_hard":    SNIPPETS_RAW[:15],
        "task4_longhor": [s for s in SNIPPETS_RAW if s.get("is_multi_bug")],
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