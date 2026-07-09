#!/usr/bin/env python3
from __future__ import annotations

import html
import difflib
import re
import time
import unicodedata
from urllib.parse import quote
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PUBLICATIONS_DIR = ROOT / "_publications"
BADGE_DATA_FILE = ROOT / "assets" / "data" / "gs_data_shieldsio.json"
SCHOLAR_SUMMARY_FILE = ROOT / "assets" / "data" / "google_scholar_summary.json"
JEKYLL_SCHOLAR_SUMMARY_FILE = ROOT / "_data" / "google_scholar_summary.yml"
GOOGLE_SCHOLAR_USER = "2vZsJskAAAAJ"
GOOGLE_SCHOLAR_URL = f"https://scholar.google.com/citations?user={GOOGLE_SCHOLAR_USER}&hl=en&oi=ao"
GOOGLE_SCHOLAR_SEARCH_URL = "https://scholar.google.com/scholar?q="
USER_AGENT = "Mozilla/5.0 (compatible; ziyuanyang-homepage-bot/1.0; +https://github.com/Zi-YuanYang/Zi-YuanYang.github.io)"


def normalize_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title or "").lower()
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return normalized.strip()


def score_candidate(target_title: str, target_year: Optional[str], candidate: dict) -> int:
    candidate_title = candidate.get("title") or ""
    normalized_target = normalize_title(target_title)
    normalized_candidate = normalize_title(candidate_title)
    if not normalized_target or not normalized_candidate:
        return 0

    score = 0
    if normalized_target == normalized_candidate:
        score += 100
    elif normalized_candidate in normalized_target or normalized_target in normalized_candidate:
        score += 60

    overlap = sum(
        1
        for token in normalized_target.split()
        if token and token in normalized_candidate.split()
    )
    score += overlap

    score += int(difflib.SequenceMatcher(None, normalized_target, normalized_candidate).ratio() * 100)

    publication_year = candidate.get("year")
    if target_year and publication_year and str(publication_year) == str(target_year):
        score += 20

    return score


def fetch_url(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def parse_scholar_rows(document: str) -> list[dict]:
    rows = []
    for row_html in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', document, flags=re.S):
        title_match = re.search(r'class="gsc_a_at">(.*?)</a>', row_html, flags=re.S)
        if not title_match:
            continue

        citation_match = re.search(r'<td class="gsc_a_c">(.*?)</td>', row_html, flags=re.S)
        year_match = re.search(r'<td class="gsc_a_y">.*?(\d{4})', row_html, flags=re.S)

        title = html.unescape(re.sub(r"<.*?>", "", title_match.group(1))).strip()
        citation_text = ""
        if citation_match:
            citation_text = html.unescape(re.sub(r"<.*?>", "", citation_match.group(1))).strip()
        citation_number_match = re.search(r"\d+", citation_text)

        rows.append(
            {
                "title": title,
                "year": year_match.group(1) if year_match else None,
                "citation_count": int(citation_number_match.group(0)) if citation_number_match else 0,
            }
        )

    return rows


def parse_profile_totals(document: str) -> dict[str, int]:
    metric_values = re.findall(r'<td class="gsc_rsb_std">(\d+)</td>', document)
    if len(metric_values) < 6:
        raise ValueError("Could not parse Google Scholar profile totals")

    return {
        "citedby": int(metric_values[0]),
        "citedby5y": int(metric_values[1]),
        "hindex": int(metric_values[2]),
        "hindex5y": int(metric_values[3]),
        "i10index": int(metric_values[4]),
        "i10index5y": int(metric_values[5]),
    }


def fetch_scholar_publications() -> list[dict]:
    publications = []
    cstart = 0
    pagesize = 100

    while True:
        page_url = f"{GOOGLE_SCHOLAR_URL}&cstart={cstart}&pagesize={pagesize}"
        page_html = fetch_url(page_url)
        page_rows = parse_scholar_rows(page_html)
        if not page_rows:
            break

        publications.extend(page_rows)
        if len(page_rows) < pagesize:
            break

        cstart += len(page_rows)
        time.sleep(0.5)

    return publications


def fetch_exact_title_citation_count(title: str) -> Optional[int]:
    quoted_title = f'"{title}"'
    search_url = GOOGLE_SCHOLAR_SEARCH_URL + quote(quoted_title)
    document = fetch_url(search_url)

    if "/sorry/" in document or "unusual traffic" in document.lower():
        raise ValueError("Google Scholar search rate-limited this request")

    top_title_match = re.search(r'<h3[^>]*class="gs_rt"[^>]*>(.*?)</h3>', document, flags=re.S)
    if not top_title_match:
        return None

    top_title = html.unescape(re.sub(r"<.*?>", "", top_title_match.group(1))).strip()
    score = score_candidate(title, None, {"title": top_title})
    if score < 140:
        return None

    citation_match = re.search(r'(?:Cited by|被引用次数)\s*(\d+)', document)
    if not citation_match:
        return 0

    return int(citation_match.group(1))


def write_summary_files(profile_totals: dict[str, int]) -> None:
    BADGE_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    BADGE_DATA_FILE.write_text(
        (
            '{'
            f'"schemaVersion": 1, "label": "citations", "message": "{profile_totals["citedby"]}"'
            '}'
        )
        + "\n"
    )
    SCHOLAR_SUMMARY_FILE.write_text(
        (
            "{\n"
            f'  "citedby": {profile_totals["citedby"]},\n'
            f'  "citedby5y": {profile_totals["citedby5y"]},\n'
            f'  "hindex": {profile_totals["hindex"]},\n'
            f'  "hindex5y": {profile_totals["hindex5y"]},\n'
            f'  "i10index": {profile_totals["i10index"]},\n'
            f'  "i10index5y": {profile_totals["i10index5y"]}\n'
            "}\n"
        )
    )
    JEKYLL_SCHOLAR_SUMMARY_FILE.write_text(
        (
            f'citedby: {profile_totals["citedby"]}\n'
            f'citedby5y: {profile_totals["citedby5y"]}\n'
            f'hindex: {profile_totals["hindex"]}\n'
            f'hindex5y: {profile_totals["hindex5y"]}\n'
            f'i10index: {profile_totals["i10index"]}\n'
            f'i10index5y: {profile_totals["i10index5y"]}\n'
        )
    )


def find_best_scholar_match(
    title: str,
    year: Optional[str],
    scholar_publications: list[dict],
) -> Optional[dict]:
    best_candidate = None
    best_score = -1

    for candidate in scholar_publications:
        score = score_candidate(title, year, candidate)
        if score > best_score:
            best_score = score
            best_candidate = candidate

    if best_candidate is None or best_score < 100:
        return None

    return best_candidate


def parse_front_matter(text: str) -> tuple[list[str], str]:
    if not text.startswith("---\n"):
        raise ValueError("Missing front matter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid front matter")
    front_matter = parts[1].strip("\n").splitlines()
    body = parts[2]
    return front_matter, body


def extract_field(lines: list[str], key: str) -> Optional[str]:
    prefix = f"{key}:"
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].strip().strip("'").strip('"')
    return None


def upsert_citation_count(lines: list[str], citation_count: int) -> list[str]:
    new_line = f"citation_count: {citation_count}"
    for idx, line in enumerate(lines):
        if line.startswith("citation_count:"):
            updated = list(lines)
            updated[idx] = new_line
            return updated

    insert_at = 0
    for key in ("priority_author:", "type:", "selected:", "date:"):
        for idx, line in enumerate(lines):
            if line.startswith(key):
                insert_at = idx + 1
    updated = list(lines)
    updated.insert(insert_at, new_line)
    return updated


def process_file(path: Path, scholar_publications: list[dict]) -> bool:
    text = path.read_text()
    lines, body = parse_front_matter(text)
    title = extract_field(lines, "title")
    scholar_title = extract_field(lines, "scholar_title") or title
    scholar_search_title = extract_field(lines, "scholar_search_title") or scholar_title
    date_value = extract_field(lines, "date")
    year = date_value[:4] if date_value else None
    if not title or not scholar_title:
        return False

    scholar_match = find_best_scholar_match(scholar_title, year, scholar_publications)
    citation_count = int(scholar_match.get("citation_count") or 0) if scholar_match else 0
    if citation_count == 0:
        try:
            exact_title_count = fetch_exact_title_citation_count(scholar_search_title)
        except Exception:
            exact_title_count = None
        if exact_title_count is not None:
            citation_count = max(citation_count, exact_title_count)

    if scholar_match is None and citation_count == 0:
        return False

    new_lines = upsert_citation_count(lines, citation_count)
    new_text = "---\n" + "\n".join(new_lines) + "\n---" + body
    if new_text == text:
        return False

    path.write_text(new_text)
    return True


def main() -> int:
    profile_html = fetch_url(GOOGLE_SCHOLAR_URL)
    profile_totals = parse_profile_totals(profile_html)
    write_summary_files(profile_totals)

    scholar_publications = fetch_scholar_publications()
    print(f"loaded {len(scholar_publications)} Google Scholar publication(s)")
    print(f'total citations: {profile_totals["citedby"]}')

    changed = []
    for path in sorted(PUBLICATIONS_DIR.rglob("*.md")):
        try:
            if process_file(path, scholar_publications):
                changed.append(path)
                print(f"updated {path.relative_to(ROOT)}")
        except Exception as exc:
            print(f"warning: failed to update {path.relative_to(ROOT)}: {exc}")

    print(f"done, updated {len(changed)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
