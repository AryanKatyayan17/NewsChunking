from newspaper import Article

def extract_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        return {
            "title": article.title,
            "text": article.text,
            "published": str(article.publish_date)
        }

    except Exception as e:
        print(f"Failed to extract {url}: {e}")
        return None