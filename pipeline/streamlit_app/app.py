import streamlit as st
import subprocess

from services.article_service import load_articles
from services.chunk_service import get_chunks_by_article
from services.rag_service import answer_question
from services.vector_service import VectorStore

from services.global_vector_store import GlobalVectorStore
from services.chat_service import chat_with_news

# PAGE CONFIG
st.set_page_config(page_title="News Intelligence System", layout="wide")

st.title("News Intelligence System")

# SIDEBAR CONTROLS
st.sidebar.title("Controls")

if st.sidebar.button("Refresh News"):
    with st.spinner("Fetching latest news..."):
        subprocess.run(["python", "main.py"])
    st.success("News updated!")
    st.rerun()

# MODE TOGGLE
mode = st.radio(
    "Select Mode",
    ["Article Mode", "Chat Mode"]
)

# CHAT MODE
if mode == "Chat Mode":

    st.header("News Chat Assistant")

    # Initialize Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    # Load Global Vector Store
    if "global_store" not in st.session_state:
        with st.spinner("Building knowledge base..."):
            store = GlobalVectorStore()
            store.load_chunks()
            store.build_index()
            st.session_state.global_store = store

    vector_store = st.session_state.global_store

    # Display Chat History
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # User Input
    user_input = st.chat_input("Ask about the news...")

    if user_input:

        # Add user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        st.chat_message("user").write(user_input)

        # Generate response
        with st.spinner("Thinking..."):
            response, sources = chat_with_news(
                vector_store,
                user_input,
                st.session_state.chat_history
            )

        # Add bot response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

        st.chat_message("assistant").write(response)

        # Show Sources
        with st.expander("📚 Sources"):
            for s in sources:
                st.write(f"**{s.get('topic', 'Unknown')}**")
                st.write(s.get("chunk", "")[:200] + "...")
                st.write("---")

# ARTICLE MODE
if mode == "Article Mode":

    # LOAD ARTICLES
    articles = load_articles()

    if not articles:
        st.warning("No articles found. Run the pipeline first.")
        st.stop()

    # SIDEBAR - ARTICLE SELECTION
    st.sidebar.title("Articles")

    selected_title = st.sidebar.selectbox(
        "Select an article",
        [article["title"] for article in articles]
    )

    selected_article = next(
        a for a in articles if a["title"] == selected_title
    )

    # MAIN PANEL: ARTICLE VIEW
    st.header(selected_article["title"])

    st.subheader("Article Content")
    st.write(selected_article["text"])

    # LOAD CHUNKS
    chunks = get_chunks_by_article(selected_article["id"])

    # DISPLAY CHUNKS
    st.subheader("Extracted Chunks")

    if chunks:
        for chunk in chunks:
            st.markdown(f"### {chunk['topic']}")
            st.write(chunk["chunk"])
    else:
        st.warning("No chunks available for this article.")

    # VECTOR STORE (ARTICLE LEVEL)
    vector_store = None

    if chunks:
        vector_store = VectorStore()
        vector_store.build_index(chunks)

    # Q&A SECTION
    st.subheader( "Ask Questions")

    question = st.text_input("Enter your question")

    if st.button("Ask"):
        if not chunks:
            st.warning("No chunks available for this article.")
        elif not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                answer = answer_question(chunks, question, vector_store)

            st.success("Answer:")
            st.write(answer)