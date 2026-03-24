import json
import os
import logging

SEMANTIC_FILE = "storage/semantic_chunks.json"
PROCESSED_FILE = "storage/processed_semantic.json"

def ensure_storage():
    os.makedirs("storage", exist_ok=True)

    for file in [SEMANTIC_FILE, PROCESSED_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump([], f)
            logging.info(f" Created file: {file}")


def load_json(file):
    ensure_storage()
    try:
        with open(file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.warning(f" Corrupted JSON in {file}, resetting...")
        return []
    except Exception as e:
        logging.error(f" Error loading {file}: {e}")
        return []


def save_json(file, data):
    ensure_storage()
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f" Error saving {file}: {e}")


# SEMANTIC CHUNKS
def load_semantic_chunks():
    return load_json(SEMANTIC_FILE)


def save_semantic_chunks(new_chunks):
    existing = load_semantic_chunks()
    existing.extend(new_chunks)
    save_json(SEMANTIC_FILE, existing)

    logging.info(f" Saved {len(new_chunks)} semantic chunks")

# TRACK PROCESSED ARTICLES
def load_processed_articles():
    return set(load_json(PROCESSED_FILE))


def is_processed(article_id):
    processed = load_processed_articles()
    return article_id in processed


def mark_processed(article_id):
    processed = load_processed_articles()
    processed.add(article_id)
    save_json(PROCESSED_FILE, list(processed))