# File: java_chatgpt_clone.py

import os
import re
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment or Streamlit secrets.")

# Streamlit page config
st.set_page_config(page_title="Java GPT Assistant", layout="wide")
st.title("\U0001F916 JavaGPT Assistant")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
# Default model
if "model_name" not in st.session_state:
    st.session_state.model_name = "gemma2-9b-it"

# Sidebar settings
with st.sidebar:
    st.header("Settings")
    st.markdown("This assistant is tailored for Java programmers.")

    valid_models = {
        "Gemma 2 (9B)": "gemma2-9b-it",
        "LLaMA 3.3 (70B)": "llama-3.3-70b-versatile"
    }

    model_choice = st.selectbox(
        "Choose a Groq model",
        list(valid_models.keys()),
        index=0
    )

    selected_model_id = valid_models[model_choice]
    st.session_state.model_name = selected_model_id
    st.sidebar.markdown(f"**Model ID Sent:** `{selected_model_id}`")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Display chat messages
for msg in st.session_state.chat_history:
    role = msg["role"]
    content = msg["content"]
    with st.chat_message(role):
        st.markdown(content)

# Format Java code blocks if present

def format_java_code_blocks(text: str) -> str:
    code_blocks = re.findall(r"```(java)?(.*?)```", text, re.DOTALL)
    for lang, block in code_blocks:
        formatted = f"```java\n{block.strip()}\n```"
        text = text.replace(f"```{lang}{block}```", formatted)
    return text

# Chat input
if prompt := st.chat_input("Ask anything about Java..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        system_prompt = (
            "You are JavaGPT, an expert assistant specialized in Java programming. "
            "You help developers write, debug, optimize, and understand Java code. "
            "You explain concepts clearly and give practical examples. You always use correct, modern Java syntax and best practices.\n\n"
            "When answering:\n"
            "- Prioritize clear and concise explanations.\n"
            "- Format Java code inside markdown triple backticks like ```java ... ```\n"
            "- Provide step-by-step reasoning where helpful.\n"
            "- If a problem can be solved in multiple ways, briefly mention alternatives.\n\n"
            "Do not make up information. If you're unsure, say so.\n"
            "Always tailor your help specifically for Java developers — including topics like OOP, multithreading, Spring Boot, JavaFX, Maven, Gradle, or performance optimization.\n"
            "You do not answer unrelated questions (like personal, philosophical, or non-programming topics). Stay focused on helping with Java development only."
        )

        messages = [
            {"role": "system", "content": system_prompt}
        ] + st.session_state.chat_history

        chat_completion = client.chat.completions.create(
            messages=messages,
            model=st.session_state.model_name
        )

        response = chat_completion.choices[0].message.content
        formatted_response = format_java_code_blocks(response)

        st.session_state.chat_history.append({"role": "assistant", "content": formatted_response})
        with st.chat_message("assistant"):
            st.markdown(formatted_response)

    except Exception as e:
        error_msg = f"\n**Error communicating with Groq API:** {str(e)}"
        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.error(error_msg)

# Optional clear history button
if st.sidebar.button("Clear chat history"):
    st.session_state.chat_history = []
    st.rerun()
