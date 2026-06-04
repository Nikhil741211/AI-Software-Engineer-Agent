import os


def search_relevant_files(query, top_k=3, repo_path="workspace/test_repo"):
    results = []

    keywords = query.lower().split()

    skip_dirs = [
        "__pycache__",
        ".git",
        "venv",
        ".venv",
        "node_modules",
        ".pytest_cache",
        "workspace"
    ]

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [
            d for d in dirs
            if d not in skip_dirs
        ]

        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)

                try:
                    with open(path, "r") as f:
                        content = f.read().lower()

                    score = 0

                    for word in keywords:
                        if word in content:
                            score += 2

                        if word in file.lower():
                            score += 1

                    if score > 0:
                        results.append((score, path))

                except Exception:
                    pass

    results.sort(reverse=True)

    matched_files = [path for score, path in results[:top_k]]

    if not matched_files:
        fallback = os.path.join(repo_path, "sample_code.py")
        if os.path.exists(fallback):
            matched_files = [fallback]

    return matched_files