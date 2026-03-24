from utils.llm import call_llm


def format_chat_history(history):
    """Convert chat history into string format"""
    formatted = ""
    for msg in history:
        role = msg["role"]
        content = msg["content"]
        formatted += f"{role.upper()}: {content}\n"
    return formatted


def chat_with_news(vector_store, question, chat_history, k=5):
    retrieved_chunks = vector_store.search(question, k=k)
    context = "\n".join([c["chunk"] for c in retrieved_chunks])
    history_text = format_chat_history(chat_history)

    prompt = f"""
        You are an intelligent news assistant.

        You can:
        - Summarise global news
        - Explain specific events
        - Answer based ONLY on provided context

        Instructions:
        - If question is broad → summarise key events
        - If question is specific → give detailed explanation
        - If not found → say "Not mentioned in the news"

        Context:
        {context}

        Conversation History:
        {history_text}

        Question:
        {question}
        """

    response = call_llm(prompt)

    return response, retrieved_chunks