PROTECTED_FILES = {
    "agent.py",
    "main.py",
    "worker.py",
    "database.py",
    "github_tools.py",
    "graph_agent.py",
    "rag_tools.py",
    "tools.py",
    "guardrails.py",
    "loop_detector.py",
    "diff_tools.py",
    "safe_file_filter.py",
    "issue_classifier.py",
}


def is_safe_to_edit(file_path):
    normalized = file_path.replace("\\", "/")
    filename = normalized.split("/")[-1]

    if filename in PROTECTED_FILES:
        return False

    if "__pycache__" in normalized:
        return False

    if normalized.endswith(".db"):
        return False

    if normalized.endswith(".txt"):
        return False

    return normalized.endswith(".py")


def filter_safe_files(files):
    return [file for file in files if is_safe_to_edit(file)]
