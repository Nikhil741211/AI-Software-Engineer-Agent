import os
import psycopg2


DB_NAME = os.getenv("DB_NAME", "ai_agent_db")
DB_USER = os.getenv("DB_USER", "lalitha13")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        id SERIAL PRIMARY KEY,
        issue_title TEXT,
        reasoning_log TEXT,
        approval_status TEXT,
        pr_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


def save_issue(issue_title, reasoning_log, approval_status, pr_url=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO issues
        (issue_title, reasoning_log, approval_status, pr_url)
        VALUES (%s, %s, %s, %s)
        """,
        (issue_title, reasoning_log, approval_status, pr_url)
    )

    conn.commit()
    cur.close()
    conn.close()


def get_all_issues():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        id,
        issue_title,
        reasoning_log,
        approval_status,
        pr_url,
        created_at
    FROM issues
    ORDER BY id DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows