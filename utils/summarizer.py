import re
import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_summarizer():
    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn"
    )

def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    # Remove phone numbers
    text = re.sub(r'\b\d[\d\s\-().]{7,}\d\b', '', text)
    # Remove extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

def summarize(text):
    summarizer = load_summarizer()

    cleaned = clean_text(text)

    result = summarizer(
        cleaned[:3000],
        max_new_tokens=200,
        min_length=60,
        do_sample=False,
        repetition_penalty=3.0,
        no_repeat_ngram_size=4,
    )

    return result[0]["summary_text"]