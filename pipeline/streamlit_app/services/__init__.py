import json

CHUNKS_FILE = "storage/chunks.json"

def load_chunks():
    try:
        with open(CHUNKS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def get_chunks_by_article(article_id):
    chunks = load_chunks()
    return [c for c in chunks if c["article_id"] == article_id]