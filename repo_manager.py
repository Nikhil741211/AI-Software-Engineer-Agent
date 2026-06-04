import os
import shutil
import subprocess


WORKSPACE_DIR = "workspace"


def ensure_workspace():
    os.makedirs(WORKSPACE_DIR, exist_ok=True)


def clone_or_update_repo(repo_url, repo_name):
    ensure_workspace()

    repo_path = os.path.join(WORKSPACE_DIR, repo_name)

    if os.path.exists(repo_path):
        subprocess.run(
            ["git", "-C", repo_path, "pull"],
            check=False
        )
        return repo_path

    subprocess.run(
        ["git", "clone", repo_url, repo_path],
        check=True
    )

    return repo_path


def reset_repo(repo_name):
    repo_path = os.path.join(WORKSPACE_DIR, repo_name)

    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    return True


def create_branch(repo_path, branch_name):
    subprocess.run(
        ["git", "-C", repo_path, "checkout", "-B", branch_name],
        check=True
    )


def commit_changes(repo_path, message):
    subprocess.run(
        ["git", "-C", repo_path, "add", "."],
        check=True
    )

    result = subprocess.run(
        ["git", "-C", repo_path, "commit", "-m", message],
        capture_output=True,
        text=True
    )

    return result.stdout + result.stderr


def push_branch(repo_path, branch_name):
    subprocess.run(
        ["git", "-C", repo_path, "push", "-u", "origin", branch_name],
        check=True
    )
