
import os
import re
import json
import time
import math
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

def sha1_text(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def now_utc_iso() -> str:
    import datetime
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def safe_get(d: dict, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def normalize_whitespace(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_gdelt_date(date_str: str):
    # GDELT often returns YYYYMMDDHHMMSS
    if not isinstance(date_str, str):
        return pd.NaT
    if re.fullmatch(r"\d{14}", date_str):
        return pd.to_datetime(date_str, format="%Y%m%d%H%M%S", errors="coerce", utc=True)
    # fallback
    return pd.to_datetime(date_str, errors="coerce", utc=True)

def language_bucket(lang: str) -> str:
    # normalize a few common labels
    if not isinstance(lang, str) or not lang:
        return "unknown"
    lang = lang.lower()
    mapping = {
        "zh-cn": "zh",
        "zh-tw": "zh",
        "zh-hk": "zh",
        "zh": "zh",
        "en": "en",
        "es": "es",
        "ru": "ru",
    }
    return mapping.get(lang, lang)
