import json
import os
import logging

CHUNKS_FILE = "storage/chunks.json"
PROCESSED_FILE = "storage/processed_chunks.json"


def ensure_storage():
    """Ensure storage files exist"""
    os.makedirs("storage", exist_ok=True)

    for file in [CHUNKS_FILE, PROCESSED_FILE]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump([], f)
            logging.info(f"Created file: {file}")


def load_json(file):
    """Safe JSON loader"""
    ensure_storage()

    try:
        with open(file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.warning(f"Corrupted JSON in {file}, resetting...")
        return []
    except Exception as e:
        logging.error(f"Error loading {file}: {e}")
        return []


def save_json(file, data):
    """Safe JSON saver"""
    ensure_storage()

    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving {file}: {e}")


# CHUNK STORAGE
def load_chunks():
    return load_json(CHUNKS_FILE)


def save_chunks(new_chunks):
    existing = load_chunks()
    existing.extend(new_chunks)
    save_json(CHUNKS_FILE, existing)

    logging.info(f"Saved {len(new_chunks)} chunks")

# PROCESSED ARTICLES TRACKING
def load_processed_articles():
    return set(load_json(PROCESSED_FILE))


def mark_article_processed(article_id):
    processed = load_processed_articles()
    processed.add(article_id)
    save_json(PROCESSED_FILE, list(processed))


def is_article_processed(article_id):
    processed = load_processed_articles()
    return article_id in processed