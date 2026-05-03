import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_model():
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-base"
    )

def generate_answer(context, question):
    qa_pipeline = load_model()

    prompt = f"""You are a legal AI assistant.

Context:
{context}

Question:
{question}

Give a simple, clear answer:"""

    result = qa_pipeline(
        prompt,
        max_new_tokens=256,
        do_sample=False,
        repetition_penalty=3.0,
        no_repeat_ngram_size=4,
        early_stopping=True
    )

    return result[0]["generated_text"]