import os

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from redis import Redis
from rq import Queue

from database import get_all_issues
from github_tools import create_pr_after_approval
from worker import process_issue
from monitoring import api_requests


API_SECRET_KEY = os.getenv("API_SECRET_KEY")


def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


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
    api_requests.inc()

    return {
        "message": "AI Software Engineer Agent Running"
    }


@app.post("/webhook")
async def github_webhook(request: Request):
    api_requests.inc()

    payload = await request.json()

    issue = payload.get("issue")
    repository = payload.get("repository", {})

    if issue:
        title = issue.get("title", "")

        repo_name = repository.get("name", os.getenv("GITHUB_REPO"))
        repo_full_name = repository.get(
            "full_name",
            f"{os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}"
        )
        clone_url = repository.get(
            "clone_url",
            f"https://github.com/{repo_full_name}.git"
        )

        job_payload = {
            "issue_title": title,
            "repo_name": repo_name,
            "repo_full_name": repo_full_name,
            "clone_url": clone_url
        }

        q.enqueue(process_issue, job_payload)

        return {
            "status": "queued",
            "issue": title,
            "repo_name": repo_name,
            "repo_full_name": repo_full_name,
            "clone_url": clone_url
        }

    return {
        "status": "ignored"
    }


@app.get("/issues")
def get_issues(x_api_key: str = Header(None)):
    api_requests.inc()
    verify_api_key(x_api_key)

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
def get_diff(x_api_key: str = Header(None)):
    api_requests.inc()
    verify_api_key(x_api_key)

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
def approve_fix(x_api_key: str = Header(None)):
    api_requests.inc()
    verify_api_key(x_api_key)

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
def reject_fix(x_api_key: str = Header(None)):
    api_requests.inc()
    verify_api_key(x_api_key)

    return {
        "status": "rejected",
        "message": "Fix rejected by reviewer"
    }


@app.get("/metrics")
def metrics():
    api_requests.inc()

    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )