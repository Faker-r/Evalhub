import re

# Valid benchmark type tags from Lighteval
VALID_BENCHMARK_TAGS = {
    "bias", "biology", "biomedical", "chemistry", "classification", "code-generation",
    "commonsense", "conversational", "dialog", "dialogue", "emotion", "ethics", "factuality",
    "general-knowledge", "generation", "geography", "graduate-level", "health", "history",
    "instruction-following", "justice", "knowledge", "language", "language-modeling",
    "language-understanding", "legal", "long-context", "math", "medical", "morality",
    "multi-turn", "multilingual", "multimodal", "multiple-choice", "narrative", "nli",
    "physical-commonsense", "physics", "qa", "question-answering", "reading-comprehension",
    "reasoning", "safety", "science", "scientific", "summarization", "symbolic", "translation",
    "utilitarianism", "virtue", "coding", "information-retrieval", "retrieval",
    "text-generation", "text-classification", "token-classification", "causal-lm",
}

# Keywords to infer tags from task/dataset names
# Format: "keyword": ["tag1", "tag2"]
INFERRED_TAG_KEYWORDS = {
    "math": ["math", "reasoning"],
    "gsm8k": ["math", "reasoning"],
    "aime": ["math", "reasoning"],
    "algebra": ["math", "reasoning"],
    "arithmetic": ["math", "reasoning"],
    "code": ["coding", "code-generation"],
    "coding": ["coding", "code-generation"],
    "humaneval": ["coding", "code-generation"],
    "mbpp": ["coding", "code-generation"],
    "mmlu": ["general-knowledge", "knowledge"],
    "knowledge": ["knowledge"],
    "common": ["commonsense"],
    "qa": ["qa"],
    "question": ["qa"],
    "nli": ["nli"],
    "chat": ["conversational"],
    "dialog": ["dialogue"],
    "summar": ["summarization"],
    "translat": ["translation"],
    "medic": ["medical"],
    "bio": ["biology"],
    "chem": ["chemistry"],
    "physic": ["physics"],
    "scien": ["science"],
    "legal": ["legal"],
    "histor": ["history"],
    "geograph": ["geography"],
    "logic": ["reasoning"],
    "reason": ["reasoning"],
    "emotion": ["emotion"],
    "factiv": ["factuality"],
    "truth": ["factuality"],
}

# Language code mappings (HuggingFace to ISO 639-1)
# Maps various language codes and names to standardized two-letter codes
LANGUAGE_CODE_MAP = {
    # English
    "en": "en", "eng": "en", "english": "en",
    # Chinese
    "zh": "zh", "zh-cn": "zh", "zh-hans": "zh", "zh-hant": "zh", 
    "zh-tw": "zh", "chi": "zh", "chinese": "zh", "zho": "zh", "cmn": "zh",
    # Arabic
    "ar": "ar", "ara": "ar", "arabic": "ar", "arb": "ar",
    # French
    "fr": "fr", "fra": "fr", "fre": "fr", "french": "fr",
    # Russian
    "ru": "ru", "rus": "ru", "russian": "ru",
    # Spanish
    "es": "es", "spa": "es", "spanish": "es", "esp": "es",
    # German
    "de": "de", "deu": "de", "ger": "de", "german": "de",
    # Hindi
    "hi": "hi", "hin": "hi", "hindi": "hi",
    # Additional common languages
    "ja": "ja", "jpn": "ja", "japanese": "ja",
    "ko": "ko", "kor": "ko", "korean": "ko",
    "pt": "pt", "por": "pt", "portuguese": "pt", "pt-br": "pt",
    "it": "it", "ita": "it", "italian": "it",
    "nl": "nl", "nld": "nl", "dut": "nl", "dutch": "nl",
    "pl": "pl", "pol": "pl", "polish": "pl",
    "tr": "tr", "tur": "tr", "turkish": "tr",
    "vi": "vi", "vie": "vi", "vietnamese": "vi",
    "th": "th", "tha": "th", "thai": "th",
    "id": "id", "ind": "id", "indonesian": "id",
    "uk": "uk", "ukr": "uk", "ukrainian": "uk",
    "he": "he", "heb": "he", "hebrew": "he",
    "fa": "fa", "fas": "fa", "per": "fa", "persian": "fa",
    "bn": "bn", "ben": "bn", "bengali": "bn",
    "te": "te", "tel": "te", "telugu": "te",
    "ta": "ta", "tam": "ta", "tamil": "ta",
    "sw": "sw", "swa": "sw", "swahili": "sw",
}

def normalize_language_code(lang_code: str) -> str | None:
    """
    Normalize language code to standard two-letter ISO 639-1 format.
    
    Args:
        lang_code: Language code from HuggingFace (can be en, eng, english, zh-CN, etc.)
        
    Returns:
        Normalized two-letter language code or None if not recognized
    """
    if not lang_code:
        return None
    
    # Convert to lowercase and strip whitespace
    lang_code = lang_code.lower().strip()
    
    # Look up in mapping
    return LANGUAGE_CODE_MAP.get(lang_code)

def filter_benchmark_tags(tags: list[str]) -> list[str]:
    """
    Filter and normalize tags to include valid benchmark type tags and normalized language tags.
    """
    if not tags:
        return []
    
    filtered = []
    seen_languages = set()
    seen_tags = set()
    
    # Process each tag
    for tag in tags:
        tag_lower = tag.lower()
        
        # Handle language tags - normalize and deduplicate
        if tag_lower.startswith("language:"):
            lang_code = tag_lower.split(":", 1)[1] if ":" in tag_lower else None
            if lang_code:
                normalized = normalize_language_code(lang_code)
                if normalized and normalized not in seen_languages:
                    filtered.append(f"language:{normalized}")
                    seen_languages.add(normalized)
            continue
        
        # Check if this is a plain language code/name that should be converted to language:XX
        normalized_lang = normalize_language_code(tag_lower)
        if normalized_lang and normalized_lang not in seen_languages:
            # This is a language identifier, convert to standard format
            filtered.append(f"language:{normalized_lang}")
            seen_languages.add(normalized_lang)
            continue
            
        # Skip tags with special prefixes that are metadata
        if any(tag_lower.startswith(prefix) for prefix in [
            "task_categories:", "task_ids:", "size_categories:", "license:",
            "doi:", "region:", "source_datasets:", "format:",
            "annotations_creators:", "language_creators:", "multilinguality:",
            "pretty_name:", "config_name:", "data_files:", "dataset_info:",
            "args:", "kwargs:", 
        ]):
            continue
            
        # Skip size indicators
        if any(indicator in tag_lower for indicator in ["<n<", ">", "k", "m", "b"]) and any(
            char.isdigit() for char in tag
        ):
            continue
            
        # Skip common metadata tags
        if tag_lower in [
            "text", "json", "csv", "parquet", "text-file", "jsonl",
            "cc0-1.0", "mit", "apache-2.0", "cc-by-4.0", "cc-by-sa-4.0",
            "other", "unknown", "monolingual", "multilingual", "crowdsourced",
            "found", "automatic", "extended", "other-", "dataset", "datasets",
            "transformers", "nlp", "llm", "large-language-model",
            "audio", "image", "video", "multimodal",
        ]:
            continue

        # Allow arxiv tags through directly
        if tag_lower.startswith("arxiv:"):
            if tag_lower not in seen_tags:
                filtered.append(tag) 
                seen_tags.add(tag_lower)
            continue

        # For remaining tags, try to match against valid benchmark tags
        normalized_str = tag_lower.replace("-", " ").replace("_", " ")
        parts = normalized_str.split()
        
        candidate = tag_lower
        if candidate in VALID_BENCHMARK_TAGS:
             if candidate not in seen_tags:
                filtered.append(candidate)
                seen_tags.add(candidate)
        
        candidate_hyphen = tag_lower.replace("_", "-")
        if candidate_hyphen in VALID_BENCHMARK_TAGS:
             if candidate_hyphen not in seen_tags:
                filtered.append(candidate_hyphen)
                seen_tags.add(candidate_hyphen)

        for part in parts:
            if part in VALID_BENCHMARK_TAGS:
                if part not in seen_tags:
                    filtered.append(part)
                    seen_tags.add(part)
    
    return filtered

def infer_tags_from_task_info(task_name: str, description: str | None = None) -> list[str]:
    """
    Infer tags based on keywords in the task/dataset name and description.
    """
    inferred = set()
    name_lower = task_name.lower()
    for keyword, tags in INFERRED_TAG_KEYWORDS.items():
        if keyword in name_lower:
            for tag in tags:
                inferred.add(tag)
    return list(inferred)

def clean_description(description: str | None) -> str | None:
    """
    Clean and extract a readable summary from HuggingFace dataset description.
    """
    if not description:
        return None

    # Filter out placeholder text from HuggingFace
    placeholder_patterns = [
        "more information needed",
        "add a description",
        "no description",
        "todo",
        "tbd",
        "coming soon",
    ]
    desc_lower = description.lower().strip()
    if any(pattern in desc_lower for pattern in placeholder_patterns) and len(description) < 100:
        return None
    
    # Remove "Dataset Card for X" headers
    text = re.sub(r'^#*\s*Dataset Card for[^\n]*\n*', '', description, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove table of contents sections
    text = re.sub(r'##?\s*Table of Contents.*?(?=##|\Z)', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove all markdown headers but keep the content after them
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove markdown links but keep the text: [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    
    # Remove citation blocks (starting with >)
    text = re.sub(r'^>\s+.*$', '', text, flags=re.MULTILINE)
    
    # Split into paragraphs and get first meaningful ones
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Filter out paragraphs that are too short or look like section headers
    meaningful_paragraphs = [
        p for p in paragraphs 
        if len(p) > 50 and not p.endswith(':') and len(p.split()) > 8
    ]
    
    if not meaningful_paragraphs:
        return '\n\n'.join(paragraphs[:2])[:500] if paragraphs else None
    
    result = '\n\n'.join(meaningful_paragraphs[:2])
    
    if len(result) > 500:
        result = result[:500]
        last_period = max(result.rfind('.'), result.rfind('!'), result.rfind('?'))
        if last_period > 200:
            result = result[:last_period + 1]
    
    return result.strip() if result.strip() else None
