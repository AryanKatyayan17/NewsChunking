import requests
import feedparser
import time
import logging

# Configure logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

MAX_RETRIES = 3
TIMEOUT = 5  # seconds
RETRY_DELAY = 2  # seconds


def fetch_rss_articles(rss_url, limit=10):
    logging.info(f"📡 Fetching RSS feed: {rss_url}")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                rss_url,
                headers=HEADERS,
                timeout=TIMEOUT
            )

            response.raise_for_status()

            # Parse RSS content
            feed = feedparser.parse(response.content)

            articles = []

            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": rss_url
                })

            logging.info(f"✅ Success: {len(articles)} articles fetched")
            return articles

        except requests.exceptions.Timeout:
            logging.warning(f"Timeout on attempt {attempt}/{MAX_RETRIES}")

        except requests.exceptions.RequestException as e:
            logging.warning(f"Request failed on attempt {attempt}: {e}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            break

        # Retry delay
        if attempt < MAX_RETRIES:
            logging.info(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

    logging.error(f"Failed to fetch RSS feed after {MAX_RETRIES} attempts: {rss_url}")
    return []