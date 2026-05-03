from google import genai
from transformers import pipeline
import streamlit as st

@st.cache_resource
def load_local_risk_model():
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-base"
    )

def gemini_answer(context, question, api_key):
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""You are a legal AI assistant. Analyze the contract context and answer the question clearly.

Contract Context:
{context}

Question:
{question}

Give a detailed, clear answer:"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        error = str(e)
        if "503" in error or "UNAVAILABLE" in error:
            return "⚠️ Gemini servers are busy. Please try again in a few seconds."
        elif "429" in error or "QUOTA" in error:
            return "⚠️ Gemini quota exceeded. Please wait a minute and try again."
        elif "400" in error or "API_KEY" in error:
            return "⚠️ Invalid API key. Please check your Gemini API key."
        else:
            return f"⚠️ Gemini error: {error}"


def gemini_summarize(text, api_key):
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""You are a legal document expert. Summarize this contract in clear, simple English.
Cover: parties involved, main obligations, payment terms, termination conditions, and key risks.

Contract:
{text[:4000]}

Summary:"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        error = str(e)
        if "503" in error or "UNAVAILABLE" in error:
            return "⚠️ Gemini servers are busy. Please try again in a few seconds."
        elif "429" in error or "QUOTA" in error:
            return "⚠️ Gemini quota exceeded. Please wait a minute and try again."
        elif "400" in error or "API_KEY" in error:
            return "⚠️ Invalid API key. Please check your Gemini API key."
        else:
            return f"⚠️ Gemini error: {error}"


def gemini_risk(text, api_key):
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""You are a legal risk analyst. Analyze this contract thoroughly.

Contract:
{text[:4000]}

Provide:
1. Risk Level: LOW, MEDIUM, or HIGH
2. Top 3 risky clauses found
3. What each risk means for the parties
4. Your recommendation

Be specific and detailed:"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        error = str(e)
        if "503" in error or "UNAVAILABLE" in error:
            # ✅ Auto fallback to local model
            try:
                risk_model = load_local_risk_model()
                prompt = f"""You are a legal risk analyst. Analyze this contract.

Contract:
{text[:2000]}

Provide Risk Level and Key Issues:"""
                result = risk_model(
                    prompt,
                    max_new_tokens=256,
                    do_sample=False,
                    repetition_penalty=3.0,
                    no_repeat_ngram_size=4,
                    early_stopping=True
                )
                return "⚡ (Gemini busy — using local model)\n\n" + result[0]["generated_text"]
            except:
                return "⚠️ Gemini servers are busy. Please try again in a few seconds."
        elif "429" in error or "QUOTA" in error:
            return "⚠️ Gemini quota exceeded. Please wait a minute and try again."
        elif "400" in error or "API_KEY" in error:
            return "⚠️ Invalid API key. Please get a new key from aistudio.google.com"
        else:
            return f"⚠️ Gemini error: {error}"