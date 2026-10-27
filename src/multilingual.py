"""Multilingual query translation and legal lexicon mapping for Indian languages.

Supports:
- Devanagari (Hindi, Marathi)
- Malayalam
- Tamil
- Telugu
- Bengali
- Gujarati
- Kannada
- Punjabi (Gurmukhi)

Provides instant deterministic legal term mapping and optional neural translation fallback.
"""

from __future__ import annotations

import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger("multilingual")

# Unicode ranges for Indic scripts
INDIC_RANGES = [
    (r"[\u0900-\u097F]", "Hindi/Devanagari"),
    (r"[\u0D00-\u0D7F]", "Malayalam"),
    (r"[\u0B80-\u0BFF]", "Tamil"),
    (r"[\u0C00-\u0C7F]", "Telugu"),
    (r"[\u0980-\u09FF]", "Bengali"),
    (r"[\u0A80-\u0AFF]", "Gujarati"),
    (r"[\u0C80-\u0CFF]", "Kannada"),
    (r"[\u0A00-\u0A7F]", "Punjabi"),
]

# High-fidelity domain-specific legal translation mapping for matrimonial law
LEGAL_GLOSSARY = {
    # Hindi / Devanagari
    r"विवाह\s*विच्छेद": "divorce dissolution of marriage",
    r"विवाह\s*शून्यता": "nullity of marriage section 19",
    r"अकृतता": "nullity of marriage",
    r"तलाक": "divorce",
    r"क्रूरता": "cruelty",
    r"मानसिक\s*क्रूरता": "mental cruelty",
    r"शारीरिक\s*क्रूरता": "physical cruelty",
    r"परित्याग": "desertion",
    r"व्यभिचार": "adultery",
    r"जारकर्म": "adultery",
    r"पारस्परिक\s*सहमति": "mutual consent section 10A",
    r"आपसी\s*सहमति": "mutual consent section 10A",
    r"दांपत्य\s*अधिकार": "conjugal rights",
    r"प्रत्यास्थापन": "restitution of conjugal rights section 32",
    r"न्यायिक\s*पृथक्करण": "judicial separation section 22",
    r"गुजारा\s*भत्ता": "maintenance permanent alimony section 37",
    r"भरण[- ]पोषण": "maintenance alimony",
    r"सह[- ]प्रत्यर्थी": "co-respondent section 11",
    r"पति": "husband",
    r"पत्नी": "wife",
    r"ईसाई": "Christian Indian Divorce Act",
    r"धारा\s*10": "Section 10",
    r"धारा\s*10ए": "Section 10A",
    r"धारा\s*19": "Section 19",
    r"धारा\s*22": "Section 22",
    r"धारा\s*32": "Section 32",
    r"धारा\s*37": "Section 37",

    # Marathi
    r"घटस्फोट": "divorce dissolution of marriage",
    r"परस्पर\s*संमती": "mutual consent section 10A",

    # Malayalam
    r"വിവാഹമോചനം": "divorce dissolution of marriage",
    r"ക്രൂരത": "cruelty",
    r"മാനസിക\s*ക്രൂരത": "mental cruelty",
    r"ഉപേക്ഷിക്കൽ": "desertion",
    r"വ്യഭിചാരം": "adultery",
    r"പരസ്പര\s*സമ്മതം": "mutual consent section 10A",
    r"ദാമ്പത്യ\s*അവകാശം": "restitution of conjugal rights",
    r"ഭർത്താവ്": "husband",
    r"ഭാര്യ": "wife",
    r"ക്രിസ്ത്യൻ": "Christian Indian Divorce Act",

    # Tamil
    r"விவாகரத்து": "divorce dissolution of marriage",
    r"கொடுமை": "cruelty",
    r"கைவிடுதல்": "desertion",
    r"விபச்சாரம்": "adultery",
    r"பரஸ்பர\s*சம்மதம்": "mutual consent section 10A",
    r"கணவன்": "husband",
    r"மனைவி": "wife",
    r"கிறிஸ்தவ": "Christian Indian Divorce Act",

    # Telugu
    r"వివాహ\s*రద్దు": "divorce dissolution of marriage",
    r"క్రూరత్వం": "cruelty",
    r"పరిత్యాగం": "desertion",
    r"వ్యభిచారం": "adultery",
    r"పరస్పర\s*అంగీకారం": "mutual consent section 10A",
    r"భర్త": "husband",
    r"భార్య": "wife",

    # Bengali
    r"বিবাহ\s*বিচ্ছেদ": "divorce dissolution of marriage",
    r"নিষ্ঠুরতা": "cruelty",
    r"পরিত্যাগ": "desertion",
    r"ব্যভিচার": "adultery",
    r"পারস্পরিক\s*সম্মতি": "mutual consent section 10A",
    r"স্বামী": "husband",
    r"স্ত্রী": "wife",
}


def detect_language(text: str) -> Optional[str]:
    """Detects if text contains characters from any Indic script."""
    if not text:
        return None
    for pattern, lang in INDIC_RANGES:
        if re.search(pattern, text):
            return lang
    return None


def is_vernacular(text: str) -> bool:
    """Returns True if text contains non-ASCII Indic script characters."""
    return detect_language(text) is not None


def translate_query(query: str) -> Tuple[str, Optional[str]]:
    """Translates a regional or vernacular query into English legal terms.

    Returns:
        (translated_query, detected_language_name)
    """
    clean_q = query.strip()
    lang = detect_language(clean_q)
    if not lang:
        return clean_q, None

    # Step 1: Lexicon-based replacement of statutory terms
    replaced = clean_q
    mapped_terms = []
    for pattern, eng_term in LEGAL_GLOSSARY.items():
        if re.search(pattern, replaced, re.IGNORECASE):
            replaced = re.sub(pattern, f" {eng_term} ", replaced, flags=re.IGNORECASE)
            mapped_terms.append(eng_term)

    # Step 2: Attempt neural translation for any remaining vernacular context
    # if deep-translator is installed and network is accessible
    try:
        from deep_translator import GoogleTranslator
        neural = GoogleTranslator(source="auto", target="en").translate(clean_q)
        if neural and len(neural.strip()) > 3:
            # Combine neural translation with mapped statutory terms for high recall
            combined = f"{neural} {' '.join(mapped_terms)}".strip()
            # Collapse duplicate spaces
            combined = re.sub(r"\s+", " ", combined)
            return combined, lang
    except Exception as e:
        logger.debug(f"Neural translation fallback not reachable ({e}); using glossary translation.")

    # Step 3: Clean up lexicon-mapped query
    # Strip any remaining unmapped Indic characters
    clean_terms = []
    for token in replaced.split():
        # Keep ASCII words and digits
        ascii_token = re.sub(r"[^\x00-\x7F]+", "", token).strip()
        if ascii_token:
            clean_terms.append(ascii_token)

    final_query = " ".join(clean_terms).strip()
    if not final_query:
        # Default fallback if only unrecognized non-ASCII characters were present
        final_query = f"Indian Divorce Act matrimonial relief {clean_q}"

    return final_query, lang
