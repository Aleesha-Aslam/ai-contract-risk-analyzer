import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_risk_model():
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-base"
    )

RISKY_KEYWORDS = {
    "high": [
        "not liable", "no liability", "not responsible", "waive",
        "waiver", "indemnify", "indemnification", "terminate immediately",
        "unlimited liability", "no warranty", "as is", "at our discretion"
    ],
    "medium": [
        "may terminate", "subject to change", "without notice",
        "at any time", "modify", "amend", "sole discretion",
        "limited liability", "no guarantee"
    ],
    "low": [
        "confidential", "payment terms", "governing law",
        "dispute resolution", "notice period"
    ]
}

CATEGORY_KEYWORDS = {
    "💰 Payment Terms": {
        "high":   ["subject to change", "without notice", "no refund", "non-refundable"],
        "medium": ["payment terms", "late payment", "interest", "penalty"],
        "low":    ["invoice", "billing", "payment schedule"]
    },
    "⚖️ Liability": {
        "high":   ["not liable", "no liability", "not responsible", "unlimited liability", "as is"],
        "medium": ["limited liability", "no guarantee", "indemnify", "indemnification"],
        "low":    ["liability", "responsible", "obligation"]
    },
    "📅 Termination": {
        "high":   ["terminate immediately", "without notice", "at our discretion"],
        "medium": ["may terminate", "at any time", "sole discretion"],
        "low":    ["notice period", "termination", "expiry"]
    },
    "🔒 Confidentiality": {
        "high":   ["no confidentiality", "public disclosure", "share with third parties"],
        "medium": ["limited confidentiality", "may disclose"],
        "low":    ["confidential", "non-disclosure", "proprietary"]
    },
    "📋 Obligations": {
        "high":   ["waive", "waiver", "no warranty"],
        "medium": ["amend", "modify", "change"],
        "low":    ["governing law", "dispute resolution", "jurisdiction"]
    }
}

def calculate_category_scores(text):
    text_lower = text.lower()
    category_scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        high_hits   = sum(1 for k in keywords["high"]   if k in text_lower)
        medium_hits = sum(1 for k in keywords["medium"] if k in text_lower)
        low_hits    = sum(1 for k in keywords["low"]    if k in text_lower)

        score = min(100, (high_hits * 25) + (medium_hits * 12) + (low_hits * 3))

        if score >= 60:
            level = "HIGH"
            color = "#f85149"
            emoji = "🔴"
        elif score >= 25:
            level = "MEDIUM"
            color = "#d29922"
            emoji = "🟡"
        else:
            level = "LOW"
            color = "#3fb950"
            emoji = "🟢"

        category_scores[category] = {
            "score": score,
            "level": level,
            "color": color,
            "emoji": emoji
        }

    return category_scores

def calculate_risk_score(text):
    text_lower = text.lower()

    high_hits   = sum(1 for k in RISKY_KEYWORDS["high"]   if k in text_lower)
    medium_hits = sum(1 for k in RISKY_KEYWORDS["medium"] if k in text_lower)
    low_hits    = sum(1 for k in RISKY_KEYWORDS["low"]    if k in text_lower)

    score = min(100, (high_hits * 20) + (medium_hits * 10) + (low_hits * 3))

    if score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    else:
        level = "LOW"

    found_keywords = {
        "high":   [k for k in RISKY_KEYWORDS["high"]   if k in text_lower],
        "medium": [k for k in RISKY_KEYWORDS["medium"] if k in text_lower],
        "low":    [k for k in RISKY_KEYWORDS["low"]    if k in text_lower],
    }

    return score, level, found_keywords

def analyze_risk(text):
    risk_model = load_risk_model()

    prompt = f"""You are a legal risk analyst. Analyze this contract and identify risks.

Contract:
{text[:2000]}

Provide:
- Risk Level: LOW, MEDIUM, or HIGH
- Key Issues found
- Recommendation

Answer:"""

    result = risk_model(
        prompt,
        max_new_tokens=256,
        do_sample=False,
        repetition_penalty=3.0,
        no_repeat_ngram_size=4,
        early_stopping=True
    )

    return result[0]["generated_text"]