import json
import os
import logging

URLS_FILE = "storage/processed_urls.json"


def ensure_storage():
    """Ensure storage folder and file exist"""
    folder = os.path.dirname(URLS_FILE)

    # Create folder if missing
    if not os.path.exists(folder):
        os.makedirs(folder)
        logging.info(f"Created folder: {folder}")

    # Create file if missing
    if not os.path.exists(URLS_FILE):
        with open(URLS_FILE, "w") as f:
            json.dump([], f)
        logging.info(f"Created file: {URLS_FILE}")


def load_processed_urls():
    """Load processed URLs safely"""
    ensure_storage()

    try:
        with open(URLS_FILE, "r") as f:
            data = json.load(f)
            return set(data)

    except json.JSONDecodeError:
        logging.warning("Corrupted JSON detected. Resetting file...")
        return set()

    except Exception as e:
        logging.error(f"Error loading URLs: {e}")
        return set()


def save_processed_urls(urls):
    """Save URLs safely"""
    ensure_storage()

    try:
        with open(URLS_FILE, "w") as f:
            json.dump(list(urls), f, indent=2)

    except Exception as e:
        logging.error(f"Error saving URLs: {e}")


def filter_new_articles(articles):
    """Filter out already processed articles"""
    processed = load_processed_urls()

    new_articles = []

    for article in articles:
        url = article.get("url")

        if not url:
            continue

        if url not in processed:
            new_articles.append(article)
            processed.add(url)

    save_processed_urls(processed)

    logging.info(f"Deduplication complete: {len(new_articles)} new articles")

    return new_articles