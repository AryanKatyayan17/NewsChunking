from streamlit_app.utils.llm import call_llm
import json
import logging
import re


def extract_json(text):
    """Extract JSON from LLM response"""
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return match.group(0)
    except Exception as e:
        logging.error(f"JSON extraction failed: {e}")
    return None


def agentic_chunking(article_text):
    if not article_text.strip():
        return []

    prompt = f"""
    You are an intelligent news analyst.

    Split the following news article into meaningful sections such as:
    - Headline
    - Background
    - Key Events
    - Quotes
    - Impact

    Return ONLY a valid JSON array in the format:
    [
    {{"topic": "Headline", "chunk": "..."}},
    {{"topic": "Background", "chunk": "..."}},
    {{"topic": "Key Events", "chunk": "..."}},
    {{"topic": "Quotes", "chunk": "..."}},
    {{"topic": "Impact", "chunk": "..."}}
    ]

    RULES:
    - Output MUST be valid JSON
    - Do NOT include explanations
    - Do NOT include markdown
    - Do NOT include text outside JSON
    - Keep chunks concise but meaningful

    ARTICLE:
    {article_text}
    """

    try:
        response = call_llm(prompt)

        json_text = extract_json(response)

        if not json_text:
            logging.warning("No valid JSON found in response")
            return [{"topic": "Full Article", "chunk": article_text[:1000]}]

        data = json.loads(json_text)

        chunks = []
        for item in data:
            if "chunk" in item:
                chunks.append({
                    "topic": item.get("topic", "Unknown"),
                    "chunk": item["chunk"]
                })

        logging.info(f"Generated {len(chunks)} chunks")
        return chunks

    except json.JSONDecodeError:
        logging.error("JSON parsing failed")
        return [{"topic": "Fallback", "chunk": article_text[:1000]}]

    except Exception as e:
        logging.error(f"Chunking error: {e}")
        return [{"topic": "Error", "chunk": article_text[:1000]}]