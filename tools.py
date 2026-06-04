import os
import subprocess


# READ FILE
def read_file(path):
    with open(path, "r") as f:
        return f.read()


# WRITE FILE
def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)


# SEARCH CODE
def search_code(keyword):
    results = []

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)

                try:
                    with open(path, "r") as f:
                        content = f.read()

                    if keyword.lower() in content.lower():
                        results.append(path)

                except Exception:
                    pass

    return results


# RUN TESTS
def run_tests(repo_path="workspace/test_repo"):
    result = subprocess.run(
        [
            "pytest",
            "--ignore=workspace",
            "--ignore=.git",
            "--ignore=__pycache__"
        ],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    return result.stdout + result.stderr


# FILE TREE TRAVERSAL
def get_file_tree(root="."):
    files = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if d not in [
                "__pycache__",
                ".git",
                "venv",
                "node_modules"
            ]
        ]

        for file in filenames:
            if file.endswith(".py"):
                files.append(os.path.join(dirpath, file))

    return files


# SAVE REASONING LOG
def save_reasoning_log(reasoning, filename="reasoning_log.txt"):
    with open(filename, "w") as f:
        for step in reasoning:
            f.write(str(step) + "\n\n")