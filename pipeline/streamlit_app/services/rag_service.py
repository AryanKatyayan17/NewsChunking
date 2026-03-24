from utils.llm import call_llm

def answer_question(context_chunks, question, vector_store):
    relevant_chunks = vector_store.search(question)

    context = "\n".join(relevant_chunks)

    prompt = f"""
    Answer the question using ONLY the context below.

    Context:
    {context}

    Question:
    {question}
    """

    return call_llm(prompt)