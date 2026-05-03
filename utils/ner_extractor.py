import re

def extract_entities(text):
    text_sample = text[:5000]

    entities = {
        "👤 People / Parties":  [],
        "🏢 Organizations":     [],
        "📅 Dates & Deadlines": [],
        "💰 Money & Amounts":   [],
        "📍 Locations":         [],
        "⚖️ Legal References":  [],
    }

    # Dates
    dates = re.findall(
        r'\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|'
        r'\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}|'
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
        r'\s+\d{1,2},?\s+\d{4}|'
        r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)'
        r'\s+\d{4})\b', text_sample, re.IGNORECASE
    )
    entities["📅 Dates & Deadlines"] = list(set(dates))

    # Money
    money = re.findall(
        r'\b(?:USD|GBP|EUR|PKR)?\s?[\$\£\€\₨]?\s?\d+(?:,\d{3})*(?:\.\d{2})?\s?'
        r'(?:USD|GBP|EUR|PKR|dollars?|pounds?|euros?)?\b',
        text_sample, re.IGNORECASE
    )
    entities["💰 Money & Amounts"] = list(set([m.strip() for m in money if m.strip() and any(c.isdigit() for c in m)]))

    # Legal references
    legal = re.findall(
        r'\b(?:Section|Clause|Article|Schedule|Exhibit|Appendix|Amendment)\s+\d+[A-Za-z]?\b|'
        r'\b(?:GDPR|CCPA|HIPAA|SOX|DMCA|NDA)\b',
        text_sample, re.IGNORECASE
    )
    entities["⚖️ Legal References"] = list(set(legal))

    # Organizations (Company, Ltd, Inc, Corp patterns)
    orgs = re.findall(
        r'\b[A-Z][a-zA-Z\s]+(?:Ltd|Limited|Inc|Corp|Corporation|LLC|LLP|Group|Services|Solutions|Technologies)\b',
        text_sample
    )
    entities["🏢 Organizations"] = list(set(orgs))[:10]

    # People (Mr/Mrs/Dr titles or capitalized full names)
    people = re.findall(
        r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b|'
        r'\b(?:Client|Company|Party|Vendor|Provider|Contractor)\s+[A-Z]\b',
        text_sample
    )
    entities["👤 People / Parties"] = list(set(people))[:10]

    # Locations
    locations = re.findall(
        r'\b(?:New York|London|California|Texas|United States|United Kingdom|'
        r'Pakistan|India|Dubai|Canada|Australia|Germany|France)\b',
        text_sample, re.IGNORECASE
    )
    entities["📍 Locations"] = list(set(locations))

    return entities