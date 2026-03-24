from groq import Groq
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
key = st.secrets.get("key") or os.getenv("key")

client = Groq(api_key=os.getenv(key))

def call_llm(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content
