import os
import subprocess


WORKSPACE_DIR = "workspace"


def ensure_workspace():
    os.makedirs(WORKSPACE_DIR, exist_ok=True)


def get_repo_path(repo_name="test_repo"):
    ensure_workspace()
    return os.path.join(WORKSPACE_DIR, repo_name)


def clone_repo(repo_url, repo_name):
    ensure_workspace()

    target_path = get_repo_path(repo_name)

    if os.path.exists(target_path) and os.listdir(target_path):
        return target_path

    subprocess.run(
        ["git", "clone", repo_url, target_path],
        check=True
    )

    return target_path


def list_workspace_files(repo_name="test_repo"):
    repo_path = get_repo_path(repo_name)
    files = []

    for root, dirs, filenames in os.walk(repo_path):
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(os.path.join(root, filename))

    return files
