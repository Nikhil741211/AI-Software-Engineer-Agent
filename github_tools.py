import os
import time
import base64
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


def get_latest_commit_sha(branch):
    url = f"{BASE_URL}/git/ref/heads/{branch}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["object"]["sha"]


def create_branch(new_branch):
    default_branch = get_default_branch()
    latest_sha = get_latest_commit_sha(default_branch)

    url = f"{BASE_URL}/git/refs"

    data = {
        "ref": f"refs/heads/{new_branch}",
        "sha": latest_sha
    }

    response = requests.post(url, headers=HEADERS, json=data)

    if response.status_code == 422:
        return {"message": "Branch already exists"}

    response.raise_for_status()
    return response.json()


def get_file_sha(file_path, branch):
    url = f"{BASE_URL}/contents/{file_path}?ref={branch}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()["sha"]


def commit_file(file_path, content, branch):
    url = f"{BASE_URL}/contents/{file_path}"

    encoded_content = base64.b64encode(
        content.encode("utf-8")
    ).decode("utf-8")

    file_sha = get_file_sha(file_path, branch)

    data = {
        "message": f"AI fix: update {file_path}",
        "content": encoded_content,
        "branch": branch
    }

    if file_sha:
        data["sha"] = file_sha

    response = requests.put(url, headers=HEADERS, json=data)
    response.raise_for_status()

    return response.json()


def create_pull_request(branch):
    default_branch = get_default_branch()

    url = f"{BASE_URL}/pulls"

    data = {
        "title": f"AI Agent Fix - {branch}",
        "head": branch,
        "base": default_branch,
        "body": "This pull request was created automatically by the AI Software Engineer Agent after human approval."
    }

    response = requests.post(url, headers=HEADERS, json=data)

    if response.status_code == 422:
        return {"message": "Pull request may already exist"}

    response.raise_for_status()
    return response.json()


def create_pr_after_approval():
    branch = f"ai-agent-fix-{int(time.time())}"

    create_branch(branch)

    with open("sample_code.py", "r") as f:
        fixed_code = f.read()

    commit_file(
        file_path="sample_code.py",
        content=fixed_code,
        branch=branch
    )

    pr = create_pull_request(branch)

    return pr
