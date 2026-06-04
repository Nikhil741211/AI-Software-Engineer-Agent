def is_safe_to_edit(path):
    protected_items = [
        "agent.py",
        "worker.py",
        "main.py",
        "database.py",
        "github_tools.py",
        "repo_manager.py",
        "tools.py",
        "rag_tools.py",
        "safe_file_filter.py",
        "patch_parser.py",
        "monitoring.py",
        "docker-compose.yml",
        "Dockerfile",
        ".env",
        "requirements",
        "__pycache__",
        ".git",
        "venv",
        ".venv",
        "node_modules",

        # prevent AI from destroying tests
        "test_",
        "tests/"
    ]

    for item in protected_items:
        if item in path:
            return False

    return True


def filter_safe_files(files):
    safe_files = []

    for file in files:
        if is_safe_to_edit(file):
            safe_files.append(file)

    return safe_files