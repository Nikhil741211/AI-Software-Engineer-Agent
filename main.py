from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
def home():
    return {
        "message": "AI Software Engineer Agent Running"
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
            "pr_url": row[4],
            "created_at": str(row[5])
        })

    return {
        "issues": issues
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