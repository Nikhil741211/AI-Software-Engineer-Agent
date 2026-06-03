import os


def search_relevant_files(query, top_k=3):
    results = []

    keywords = query.lower().split()

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)

                try:
                    with open(path, "r") as f:
                        content = f.read().lower()

                    score = 0
                    for word in keywords:
                        if word in content or word in file.lower():
                            score += 1

                    if score > 0:
                        results.append((score, path))

                except Exception:
                    pass

    results.sort(reverse=True)

    files = [path for score, path in results[:top_k]]

    if not files:
        files = ["./sample_code.py"]

    return files
