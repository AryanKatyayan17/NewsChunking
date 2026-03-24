from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

class VectorStore:
    def __init__(self):
        self.index = None
        self.texts = []

    def build_index(self, chunks):
        self.texts = [c["chunk"] for c in chunks]

        embeddings = model.encode(self.texts)
        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

    def search(self, query, k=3):
        query_vec = model.encode([query]).astype("float32")

        distances, indices = self.index.search(query_vec, k)

        return [self.texts[i] for i in indices[0]]