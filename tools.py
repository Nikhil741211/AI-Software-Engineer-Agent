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

    for file in os.listdir():
        if file.endswith(".py"):
            with open(file, "r") as f:
                content = f.read()

                if keyword in content:
                    results.append(file)

    return results


# RUN TESTS
def run_tests():
    result = subprocess.run(
        ["pytest"],
        cwd="workspace/test_repo",
        capture_output=True,
        text=True
    )

    return result.stdout + result.stderr
# FILE TREE TRAVERSAL
def get_file_tree(root="."):
    files = []

    for dirpath, dirnames, filenames in os.walk(root):
        for file in filenames:
            if file.endswith(".py"):
                files.append(os.path.join(dirpath, file))

    return files


# SAVE REASONING LOG
def save_reasoning_log(reasoning, filename="reasoning_log.txt"):
    with open(filename, "w") as f:
        for step in reasoning:
            f.write(str(step) + "\n\n")
