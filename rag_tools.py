from sentence_transformers import SentenceTransformer
import faiss
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = []
file_paths = []


def build_index():
    global documents, file_paths

    documents = []
    file_paths = []

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)

                try:
                    with open(path, "r") as f:
                        content = f.read()

                    documents.append(content)
                    file_paths.append(path)

                except Exception:
                    pass

    embeddings = model.encode(documents)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index


def search_relevant_files(query, top_k=3):
    index = build_index()

    query_embedding = model.encode([query])

    distances, indices = index.search(query_embedding, top_k)

    results = []

    for idx in indices[0]:
        results.append(file_paths[idx])

    return results
