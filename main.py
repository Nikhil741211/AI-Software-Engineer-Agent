from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from rq import Queue

from worker import process_issue
from database import get_all_issues
from github_tools import create_pr_after_approval

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_conn = Redis()
q = Queue(connection=redis_conn)


@app.get("/")
def home():
    return {
        "message": "AI Software Engineer Agent Running"
    }


@app.post("/webhook")
def webhook(data: dict):
    issue = data.get("issue")

    if not issue and "issue" in data:
        issue = data["issue"].get("title", "No issue title")

    job = q.enqueue(process_issue, issue)

    return {
        "status": "queued",
        "job_id": job.id,
        "issue": issue
    }


@app.get("/reasoning-log")
def get_reasoning_log():
    try:
        with open("reasoning_log.txt", "r") as f:
            log = f.read()

        return {
            "status": "success",
            "log": log
        }

    except FileNotFoundError:
        return {
            "status": "empty",
            "log": "No reasoning log found yet"
        }


@app.get("/issues")
def get_issues():
    rows = get_all_issues()

    issues = []

    for row in rows:
        issues.append({
            "id": row[0],
            "issue_title": row[1],
            "reasoning_log": row[2],
            "approval_status": row[3]
        })

    return {
        "issues": issues
    }


@app.post("/approve")
def approve_fix():
    with open("approval_status.txt", "w") as f:
        f.write("approved")

    pr = create_pr_after_approval()

    return {
        "status": "approved",
        "message": "Fix approved and PR created",
        "pr_url": pr.get("html_url", pr)
    }


@app.post("/reject")
def reject_fix():
    with open("approval_status.txt", "w") as f:
        f.write("rejected")

    return {
        "status": "rejected",
        "message": "Fix rejected by human reviewer"
    }


@app.get("/approval-status")
def approval_status():
    try:
        with open("approval_status.txt", "r") as f:
            status = f.read()

        return {
            "status": status
        }

    except FileNotFoundError:
        return {
            "status": "waiting_for_review"
        }