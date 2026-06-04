import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from redis import Redis
from rq import Queue

from database import get_all_issues
from github_tools import create_pr_after_approval
from worker import process_issue


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_conn = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT
)

q = Queue(connection=redis_conn)


@app.get("/")
def home():
    return {
        "message": "AI Software Engineer Agent Running"
    }


@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()

    issue = payload.get("issue")

    if issue:
        title = issue.get("title", "")

        q.enqueue(process_issue, title)

        return {
            "status": "queued",
            "issue": title
        }

    return {
        "status": "ignored"
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
            "approval_status": row[3],
            "job_status": row[4],
            "pr_url": row[5],
            "created_at": str(row[6])
        })

    return {
        "issues": issues
    }


@app.get("/diff")
def get_diff():
    try:
        with open("reasoning_log.txt", "r") as f:
            content = f.read()

        return {
            "status": "success",
            "diff": content
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "message": "No reasoning log found yet"
        }


@app.post("/approve")
def approve_fix():
    pr = create_pr_after_approval()

    pr_url = (
        pr.get("html_url")
        if isinstance(pr, dict)
        else str(pr)
    )

    return {
        "status": "approved",
        "message": "Fix approved and PR created",
        "pr_url": pr_url
    }


@app.post("/reject")
def reject_fix():
    return {
        "status": "rejected",
        "message": "Fix rejected by reviewer"
    }