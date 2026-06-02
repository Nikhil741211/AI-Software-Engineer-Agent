import sqlite3

DB_NAME = "agent.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_title TEXT,
        reasoning_log TEXT,
        approval_status TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_issue(issue_title, reasoning_log, approval_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO issues
    (issue_title, reasoning_log, approval_status)
    VALUES (?, ?, ?)
    """, (issue_title, reasoning_log, approval_status))

    conn.commit()
    conn.close()


def get_all_issues():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM issues")
    rows = cursor.fetchall()

    conn.close()

    return rows