import os
import time
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")

BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def get_default_branch():
    response = requests.get(BASE_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json()["default_branch"]


def create_pull_request(branch):
    default_branch = get_default_branch()

    url = f"{BASE_URL}/pulls"

    data = {
        "title": f"AI Agent Fix - {branch}",
        "head": branch,
        "base": default_branch,
        "body": """
This pull request was created automatically by the AI Software Engineer Agent after human approval.

Workflow:
- Human reviewed the AI reasoning
- Human approved the fix
- Agent created a branch
- Agent committed changed files
- Agent pushed the branch
- Agent opened this pull request
"""
    }

    response = requests.post(
        url,
        headers=HEADERS,
        json=data
    )

    if response.status_code == 422:
        return {
            "message": "Pull request may already exist",
            "status_code": response.status_code,
            "details": response.text
        }

    response.raise_for_status()
    return response.json()


def create_pr_after_approval():
    repo_path = "workspace/AI-Software-Engineer-Agent"
    branch = f"ai-agent-fix-{int(time.time())}"

    if not os.path.exists(repo_path):
        return {
            "error": "Repository not found",
            "message": f"{repo_path} does not exist. Clone the repository first."
        }

    subprocess.run(
        ["git", "-C", repo_path, "checkout", "main"],
        check=False
    )

    subprocess.run(
        ["git", "-C", repo_path, "pull"],
        check=False
    )

    subprocess.run(
        ["git", "-C", repo_path, "checkout", "-B", branch],
        check=True
    )

    subprocess.run(
        ["git", "-C", repo_path, "add", "."],
        check=True
    )

    subprocess.run(
        ["git", "-C", repo_path, "config", "user.email", "ai-agent@example.com"],
        check=True
    )

    subprocess.run(
        ["git", "-C", repo_path, "config", "user.name", "AI Software Engineer Agent"],
        check=True
    )

    commit_result = subprocess.run(
        [
            "git",
            "-C",
            repo_path,
            "commit",
            "-m",
            "AI Agent Approved Fix"
        ],
        capture_output=True,
        text=True
    )

    if commit_result.returncode != 0:
        return {
            "error": "Nothing to commit or commit failed",
            "details": commit_result.stdout + commit_result.stderr
        }

    auth_remote = (
        f"https://{GITHUB_TOKEN}@github.com/"
        f"{GITHUB_OWNER}/{GITHUB_REPO}.git"
    )

    subprocess.run(
        [
            "git",
            "-C",
            repo_path,
            "remote",
            "set-url",
            "origin",
            auth_remote
        ],
        check=True
    )

    push_result = subprocess.run(
        [
            "git",
            "-C",
            repo_path,
            "push",
            "-u",
            "origin",
            branch
        ],
        capture_output=True,
        text=True
    )

    if push_result.returncode != 0:
        return {
            "error": "Git push failed",
            "details": push_result.stdout + push_result.stderr
        }

    pr = create_pull_request(branch)

    return pr