"""
PDF retrieval from open-access sources.

Priority order (per pdf_retriever_agent/SOUL.md):
  1. OpenAlex OA URL
  2. arXiv
  3. Elsevier FullText API  (requires ELSEVIER_API_KEY + ELSEVIER_INST_TOKEN)
  4. Unpaywall              (requires UNPAYWALL_EMAIL)
  5. Semantic Scholar

Main entry point: retrieve_pdf(row, pdfs_dir) -> (pdf_path, source) or (None, None)
"""

import os
import re
import time
import requests
from pathlib import Path

_RATE_LIMIT_DELAY = 0.5  # seconds between requests to same API


# ── helpers ──────────────────────────────────────────────────────────────────

def _download_pdf(url: str, dest: Path, session: requests.Session) -> bool:
    """Download URL to dest. Returns True if file is a valid PDF."""
    try:
        resp = session.get(url, timeout=30, stream=True)
        if resp.status_code != 200:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        # validate magic bytes
        with open(dest, "rb") as f:
            magic = f.read(5)
        if magic != b"%PDF-":
            dest.unlink(missing_ok=True)
            return False
        return True
    except Exception:
        dest.unlink(missing_ok=True)
        return False


def _arxiv_id_from_doi(doi: str) -> str | None:
    """Extract arXiv ID from DOI pattern 10.48550/arXiv.XXXX.XXXXX."""
    if not doi:
        return None
    m = re.search(r"arXiv[.\-_](\d{4}\.\d{4,5})", doi, re.IGNORECASE)
    return m.group(1) if m else None


# ── source 1 : OpenAlex ──────────────────────────────────────────────────────

def _openalex_oa_url(openalex_id: str, session: requests.Session) -> str | None:
    if not openalex_id:
        return None
    work_id = openalex_id.replace("https://openalex.org/", "")
    url = f"https://api.openalex.org/works/{work_id}"
    try:
        resp = session.get(url, timeout=15)
        time.sleep(_RATE_LIMIT_DELAY)
        if resp.status_code == 200:
            data = resp.json()
            return (data.get("open_access") or {}).get("oa_url")
    except Exception:
        pass
    return None


# ── source 2 : arXiv ─────────────────────────────────────────────────────────

def _arxiv_pdf_url(arxiv_id: str) -> str | None:
    if not arxiv_id:
        return None
    clean = arxiv_id.strip().removeprefix("arXiv:").removeprefix("arxiv:")
    return f"https://arxiv.org/pdf/{clean}.pdf"


# ── source 3 : Elsevier FullText API ─────────────────────────────────────────

def _elsevier_pdf(doi: str, dest: Path, session: requests.Session) -> bool:
    api_key = os.environ.get("ELSEVIER_API_KEY")
    inst_token = os.environ.get("ELSEVIER_INST_TOKEN")
    if not (doi and api_key and inst_token):
        return False
    url = f"https://api.elsevier.com/content/article/doi/{doi}"
    headers = {
        "X-ELS-APIKey": api_key,
        "X-ELS-Insttoken": inst_token,
        "Accept": "application/pdf",
    }
    try:
        resp = session.get(url, headers=headers, timeout=30, stream=True)
        time.sleep(_RATE_LIMIT_DELAY)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("X-RateLimit-Reset", 60))
            raise RuntimeError(f"Elsevier rate limit — retry after {retry_after}s")
        if resp.status_code != 200:
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        with open(dest, "rb") as f:
            magic = f.read(5)
        if magic != b"%PDF-":
            dest.unlink(missing_ok=True)
            return False
        return True
    except RuntimeError:
        raise
    except Exception:
        dest.unlink(missing_ok=True)
        return False


# ── source 4 : Unpaywall ─────────────────────────────────────────────────────

def _unpaywall_pdf_url(doi: str, session: requests.Session) -> str | None:
    email = os.environ.get("UNPAYWALL_EMAIL")
    if not (doi and email):
        return None
    url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    try:
        resp = session.get(url, timeout=15)
        time.sleep(_RATE_LIMIT_DELAY)
        if resp.status_code == 200:
            data = resp.json()
            best = data.get("best_oa_location") or {}
            return best.get("url_for_pdf")
    except Exception:
        pass
    return None


# ── source 5 : Semantic Scholar ──────────────────────────────────────────────

def _semantic_scholar_pdf_url(s2_id: str, session: requests.Session) -> str | None:
    if not s2_id:
        return None
    url = f"https://api.semanticscholar.org/graph/v1/paper/{s2_id}?fields=openAccessPdf"
    try:
        resp = session.get(url, timeout=15)
        time.sleep(_RATE_LIMIT_DELAY)
        if resp.status_code == 200:
            data = resp.json()
            oa = data.get("openAccessPdf") or {}
            return oa.get("url")
    except Exception:
        pass
    return None


# ── main entry point ──────────────────────────────────────────────────────────

def retrieve_pdf(
    row: dict,
    pdfs_dir: Path,
    session: requests.Session | None = None,
) -> tuple[Path | None, str | None]:
    """
    Attempt to download a PDF for a paper row from master_research_data.csv.

    Returns (pdf_path, source_name) on success, (None, None) on failure.
    source_name is one of: openalex_oa | arxiv | elsevier | unpaywall | semantic_scholar
    """
    if session is None:
        session = requests.Session()
        session.headers["User-Agent"] = "sota-agent/0.3 (research; contact via GitHub)"

    paper_id = str(row.get("id", "unknown"))
    dest = pdfs_dir / f"{paper_id}.pdf"

    if dest.exists():
        return dest, row.get("pdf_source", "cached")

    doi = (row.get("doi") or "").strip()
    openalex_id = (row.get("openalex_id") or "").strip()
    arxiv_id = (row.get("arxiv_url") or "").strip()
    if not arxiv_id:
        arxiv_id = _arxiv_id_from_doi(doi) or ""

    # Source 1 — OpenAlex OA
    oa_url = _openalex_oa_url(openalex_id, session)
    if oa_url and _download_pdf(oa_url, dest, session):
        return dest, "openalex_oa"

    # Source 2 — arXiv
    arxiv_url = _arxiv_pdf_url(arxiv_id)
    if arxiv_url and _download_pdf(arxiv_url, dest, session):
        return dest, "arxiv"

    # Source 3 — Elsevier
    try:
        if _elsevier_pdf(doi, dest, session):
            return dest, "elsevier"
    except RuntimeError as e:
        print(f"[elsevier] {paper_id}: {e}")

    # Source 4 — Unpaywall
    uw_url = _unpaywall_pdf_url(doi, session)
    if uw_url and _download_pdf(uw_url, dest, session):
        return dest, "unpaywall"

    # Source 5 — Semantic Scholar (using DOI as identifier)
    s2_url = _semantic_scholar_pdf_url(doi, session)
    if s2_url and _download_pdf(s2_url, dest, session):
        return dest, "semantic_scholar"

    return None, None
