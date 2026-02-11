import re

def normalize_indic_text(text: str, lang: str = "hi"):
    """
    Normalize Indic language text
    Remove punctuation, extra spaces, etc.
    """
    text = text.lower()
    
    # Language-specific unicode ranges
    unicode_ranges = {
        "hi": r"[\u0900-\u097F]",  # Devanagari (Hindi, Marathi)
        "bn": r"[\u0980-\u09FF]",  # Bengali
        "ta": r"[\u0B80-\u0BFF]",  # Tamil
        "te": r"[\u0C00-\u0C7F]",  # Telugu
        "gu": r"[\u0A80-\u0AFF]",  # Gujarati
        "kn": r"[\u0C80-\u0CFF]",  # Kannada
        "ml": r"[\u0D00-\u0D7F]",  # Malayalam
        "pa": r"[\u0A00-\u0A7F]",  # Punjabi (Gurmukhi)
        "or": r"[\u0B00-\u0B7F]",  # Odia
        "as": r"[\u0980-\u09FF]",  # Assamese (same as Bengali)
    }
    
    range_pattern = unicode_ranges.get(lang, r"[\u0900-\u097F]")
    
    # Keep only language-specific characters and spaces
    text = re.sub(f"[^{range_pattern[1:-1]}\\s]", "", text)
    
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def calculate_wer(reference: str, hypothesis: str):
    """
    Calculate Word Error Rate
    Simple implementation
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    
    if len(ref_words) == 0:
        return 0.0 if len(hyp_words) == 0 else 1.0
    
    # Simple Levenshtein distance
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j
    
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = min(
                    d[i-1][j] + 1,    # deletion
                    d[i][j-1] + 1,    # insertion
                    d[i-1][j-1] + 1   # substitution
                )
    
    return d[len(ref_words)][len(hyp_words)] / len(ref_words)