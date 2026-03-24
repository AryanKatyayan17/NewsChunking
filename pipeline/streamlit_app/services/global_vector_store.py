from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import logging

SEMANTIC_FILE = "storage/semantic_chunks.json"

model = SentenceTransformer("all-MiniLM-L6-v2")


class GlobalVectorStore:
    def __init__(self):
        self.index = None
        self.chunks = []

    def load_chunks(self):
        """Load semantic chunks instead of agentic"""
        try:
            with open(SEMANTIC_FILE, "r") as f:
                self.chunks = json.load(f)

            logging.info(f" Loaded {len(self.chunks)} semantic chunks")

        except Exception as e:
            logging.error(f" Failed to load semantic chunks: {e}")
            self.chunks = []

    def build_index(self):
        if not self.chunks:
            logging.warning(" No semantic chunks available")
            return

        texts = [c["chunk"] for c in self.chunks]

        embeddings = model.encode(texts)
        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        logging.info(" Global semantic vector index built")

    def search(self, query, k=5):
        if self.index is None:
            logging.warning(" Index not built")
            return []

        query_vec = model.encode([query]).astype("float32")

        distances, indices = self.index.search(query_vec, k)

        results = [self.chunks[i] for i in indices[0]]
        return results