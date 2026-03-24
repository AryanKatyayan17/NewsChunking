import json

ARTICLES_FILE = "storage/articles.json"

def load_articles():
    try:
        with open(ARTICLES_FILE, "r") as f:
            return json.load(f)
    except:
        return []