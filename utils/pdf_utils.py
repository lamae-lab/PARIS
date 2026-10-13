"""
Full-text extraction from downloaded PDFs using pymupdf (fitz).

Main entry point: analyze_pdf(pdf_path) -> dict
Returned dict keys match the new CSV columns added in v0.3:
  full_text_available, sections_detected, limitations_extracted,
  future_work_extracted, methods_extracted, open_code, open_data
"""

from __future__ import annotations
import re
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:
    fitz = None  # type: ignore[assignment]


# ── section detection ─────────────────────────────────────────────────────────

_SECTION_PATTERNS = [
    "abstract", "introduction", "related work", "background",
    "preliminaries", "methodology", "methods", "approach",
    "experiments", "experimental setup", "results", "evaluation",
    "discussion", "limitations", "conclusion", "future work",
    "acknowledgment", "acknowledgement", "references",
]

_SECTION_RE = re.compile(
    r"^\s*(?:\d+[\.\d]*\s+)?(" + "|".join(_SECTION_PATTERNS) + r")\s*$",
    re.IGNORECASE,
)


def _detect_section(line: str) -> str | None:
    m = _SECTION_RE.match(line.strip())
    if m:
        return m.group(1).lower()
    return None


def _extract_text_by_section(doc) -> dict[str, str]:
    """Return dict {section_name: full text} using font-size heuristic + pattern matching."""
    blocks = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    blocks.append({
                        "text": span["text"],
                        "size": span["size"],
                        "flags": span["flags"],  # bold = flags & 2^4
                    })

    # estimate body font size as the most common size
    from collections import Counter
    sizes = [round(b["size"]) for b in blocks if b["text"].strip()]
    body_size = Counter(sizes).most_common(1)[0][0] if sizes else 11

    sections: dict[str, list[str]] = {"preamble": []}
    current = "preamble"

    for b in blocks:
        text = b["text"].strip()
        if not text:
            continue
        is_heading = (
            round(b["size"]) > body_size + 1
            or bool(b["flags"] & 16)  # bold
        )
        if is_heading:
            sec = _detect_section(text)
            if sec:
                current = sec
                if sec not in sections:
                    sections[sec] = []
                continue
        sections.setdefault(current, []).append(text)

    return {k: " ".join(v) for k, v in sections.items()}


# ── limitation extraction ─────────────────────────────────────────────────────

_LIMIT_KEYWORDS = re.compile(
    r"\b(limit\w*|constrain\w*|restrict\w*|assum\w*|only|cannot|can not|"
    r"does not|unable|fail\w*|challeng\w*|not yet|remains?)\b",
    re.IGNORECASE,
)

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _extract_sentences(text: str, keyword_re: re.Pattern, max_results: int = 5) -> list[str]:
    sentences = _SENTENCE_RE.split(text)
    hits = [s.strip() for s in sentences if keyword_re.search(s) and len(s.split()) > 5]
    # prefer sentences with measurable specificity (numbers, named entities)
    hits.sort(key=lambda s: len(re.findall(r"\d+|\b[A-Z][a-z]+\b", s)), reverse=True)
    return hits[:max_results]


_FUTURE_KEYWORDS = re.compile(
    r"\b(future work|future research|plan to|will investigate|remains? to be|"
    r"promising direction|next step|could be extend\w*|open question)\b",
    re.IGNORECASE,
)


# ── method / tool extraction ──────────────────────────────────────────────────

_FRAMEWORK_RE = re.compile(
    r"\b(PyTorch|TensorFlow|JAX|Keras|Qiskit|Cirq|PennyLane|QuTiP|"
    r"scikit-learn|sklearn|NumPy|SciPy|Pandas|Hugging ?Face|"
    r"GRAPE|CRAB|DRAG|REINFORCE|PPO|SAC|DDPG|DQN|Adam|SGD|BFGS|"
    r"Monte Carlo|Bayesian|Transformer|BERT|GPT|LLaMA)\b",
    re.IGNORECASE,
)



def _extract_methods(sections: dict[str, str]) -> list[str]:
    target_text = " ".join(
        sections.get(s, "")
        for s in ("methodology", "methods", "approach", "experiments", "experimental setup")
    )
    found = set(_FRAMEWORK_RE.findall(target_text))
    return sorted(found)


# ── reproducibility flags ─────────────────────────────────────────────────────

_OPEN_CODE_RE = re.compile(
    r"(github\.com|gitlab\.com|code is available|source code|open[\s-]?source"
    r"|available at https?://|released the code)",
    re.IGNORECASE,
)

_OPEN_DATA_RE = re.compile(
    r"(dataset is (publicly )?available|data available|open[\s-]?dataset"
    r"|zenodo\.org|figshare\.com|huggingface\.co/datasets|kaggle\.com)",
    re.IGNORECASE,
)


# ── key result extraction ─────────────────────────────────────────────────────



# ── main ──────────────────────────────────────────────────────────────────────

_EMPTY_RESULT: dict = {
    "full_text_available": False,
    "sections_detected": "",
    "limitations_extracted": "",
    "future_work_extracted": "",
    "methods_extracted": "",
    "open_code": "Unknown",
    "open_data": "Unknown",
}


def analyze_pdf(pdf_path: str | Path) -> dict:
    """
    Extract structured information from a PDF.
    Returns a dict with keys matching v0.3 CSV columns.
    Never raises — returns _EMPTY_RESULT on any failure.
    """
    if fitz is None:
        return _EMPTY_RESULT.copy()

    try:
        doc = fitz.open(str(pdf_path))  # type: ignore[union-attr]
    except Exception:
        return _EMPTY_RESULT.copy()

    try:
        sections = _extract_text_by_section(doc)
    except Exception:
        doc.close()
        return _EMPTY_RESULT.copy()

    full_text = " ".join(sections.values())

    # limitations — look in discussion + limitations + conclusion
    limit_text = " ".join(
        sections.get(s, "")
        for s in ("limitations", "discussion", "conclusion")
    )
    limitations = _extract_sentences(limit_text, _LIMIT_KEYWORDS, max_results=5)

    # future work — conclusion + future work sections
    fw_text = " ".join(
        sections.get(s, "")
        for s in ("future work", "conclusion", "discussion")
    )
    future_work = _extract_sentences(fw_text, _FUTURE_KEYWORDS, max_results=3)

    methods = _extract_methods(sections)

    open_code = "True" if _OPEN_CODE_RE.search(full_text) else "False"
    open_data = "True" if _OPEN_DATA_RE.search(full_text) else "False"

    doc.close()

    detected_sections = [s for s in sections if s != "preamble" and sections[s].strip()]

    return {
        "full_text_available": True,
        "sections_detected": ",".join(detected_sections),
        "limitations_extracted": " | ".join(limitations),
        "future_work_extracted": " | ".join(future_work),
        "methods_extracted": ",".join(methods),
        "open_code": open_code,
        "open_data": open_data,
    }
