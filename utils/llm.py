import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

@st.cache_resource
def load_model():
    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    # Task ka naam mita diya gaya hai taake error na aaye
    return pipeline(
        model=model,
        tokenizer=tokenizer
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

    # Dictionary reading fix
    return result[0]["generated_text"]
