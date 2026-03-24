import json
import os
import uuid
import logging

from ingestion.rss_fetcher import fetch_rss_articles
from ingestion.article_extractor import extract_article
from ingestion.deduplicator import filter_new_articles

# Agentic chunking
from chunking.agentic_chunker import agentic_chunking
from storage.chunk_storage import (
    save_chunks,
    is_article_processed,
    mark_article_processed
)

# Semantic chunking
from chunking.semantic_chunking import semantic_chunking
from storage.semantic_chunk_storage import (
    save_semantic_chunks,
    is_processed as is_semantic_processed,
    mark_processed as mark_semantic_processed
)

# CONFIG
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

ARTICLES_FILE = "storage/articles.json"

RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/politics/rss.xml",
    "http://rss.cnn.com/rss/cnn_allpolitics.rss",
    "https://www.theguardian.com/world/rss",
    "https://www.euronews.com/rss?format=xml",
    "https://mexiconewsdaily.com/feed/",
    "https://japantoday.com/feed/atom"
]

# STORAGE FUNCTIONS
def ensure_articles_file():
    os.makedirs("storage", exist_ok=True)

    if not os.path.exists(ARTICLES_FILE):
        with open(ARTICLES_FILE, "w") as f:
            json.dump([], f)


def load_articles():
    ensure_articles_file()

    try:
        with open(ARTICLES_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.warning(" Corrupted articles.json, resetting...")
        return []
    except Exception as e:
        logging.error(f" Error loading articles: {e}")
        return []


def save_articles(new_articles):
    existing = load_articles()
    existing.extend(new_articles)

    with open(ARTICLES_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    logging.info(f" Saved {len(new_articles)} articles")

# MAIN PIPELINE
def main():
    logging.info(" Fetching RSS feeds...")

    all_articles = []

    for feed in RSS_FEEDS:
        logging.info(f" Fetching from: {feed}")
        articles = fetch_rss_articles(feed, limit=10)
        all_articles.extend(articles)

    logging.info(f" Total fetched: {len(all_articles)}")

    # DEDUPLICATION
    logging.info("Removing duplicates...")
    new_articles = filter_new_articles(all_articles)

    logging.info(f"New articles: {len(new_articles)}")

    # ARTICLE EXTRACTION
    processed_articles = []

    logging.info("Extracting full content...")

    for article in new_articles:
        data = extract_article(article["url"])

        if data and data["text"]:
            processed_articles.append({
                "id": str(uuid.uuid4()),
                "title": data["title"] or article["title"],
                "text": data["text"],
                "url": article["url"],
                "source": article["source"],
                "published": data["published"]
            })

    save_articles(processed_articles)

    # LOAD ALL ARTICLES
    articles = load_articles()

    # AGENTIC CHUNKING
    logging.info("Starting agentic chunking...")

    agentic_total = []

    for article in articles:
        article_id = article["id"]

        if is_article_processed(article_id):
            logging.info(f" Skipping agentic: {article['title']}")
            continue

        logging.info(f"Agentic chunking: {article['title']}")

        chunks = agentic_chunking(article["text"])

        formatted_chunks = [
            {
                "article_id": article_id,
                "topic": chunk["topic"],
                "chunk": chunk["chunk"]
            }
            for chunk in chunks
        ]

        agentic_total.extend(formatted_chunks)

        mark_article_processed(article_id)

    if agentic_total:
        save_chunks(agentic_total)

    logging.info(f"Agentic chunking complete: {len(agentic_total)} chunks saved")

    #SEMANTIC CHUNKING
    logging.info("Starting semantic chunking...")

    semantic_total = []

    for article in articles:
        article_id = article["id"]

        if is_semantic_processed(article_id):
            logging.info(f"⏭Skipping semantic: {article['title']}")
            continue

        logging.info(f"Semantic chunking: {article['title']}")

        chunks = semantic_chunking(article["text"])

        formatted_chunks = [
            {
                "article_id": article_id,
                "chunk": chunk
            }
            for chunk in chunks
        ]

        semantic_total.extend(formatted_chunks)

        mark_semantic_processed(article_id)

    if semantic_total:
        save_semantic_chunks(semantic_total)

    logging.info(f"✅ Semantic chunking complete: {len(semantic_total)} chunks saved")

# ENTRY POINT
if __name__ == "__main__":
    main()