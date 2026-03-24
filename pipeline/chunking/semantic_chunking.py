import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Download once
nltk.download('punkt')

model = SentenceTransformer("all-MiniLM-L6-v2")


def semantic_chunking(text, threshold=0.7):
    if not text.strip():
        return []

    sentences = nltk.sent_tokenize(text)

    if len(sentences) == 0:
        return []

    embeddings = model.encode(sentences)

    chunks = []
    current_chunk = [sentences[0]]

    for i in range(1, len(sentences)):
        similarity = cosine_similarity(
            [embeddings[i]],
            [embeddings[i - 1]]
        )[0][0]

        if similarity >= threshold:
            current_chunk.append(sentences[i])
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentences[i]]

    chunks.append(" ".join(current_chunk))

    logging.info(f"🧩 Semantic chunks created: {len(chunks)}")

    return chunks