#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PUBLICATIONS_DIR = ROOT / "_publications"
MAILTO = "cziyuanyang@gmail.com"


def normalize_title(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title or "").lower()
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return normalized.strip()


def score_candidate(target_title: str, target_year: Optional[str], candidate: dict) -> int:
    candidate_title = candidate.get("display_name") or candidate.get("title") or ""
    normalized_target = normalize_title(target_title)
    normalized_candidate = normalize_title(candidate_title)
    if not normalized_target or not normalized_candidate:
        return 0

    score = 0
    if normalized_target == normalized_candidate:
        score += 100
    elif normalized_candidate in normalized_target or normalized_target in normalized_candidate:
        score += 60

    overlap = sum(1 for token in normalized_target.split() if token and token in normalized_candidate)
    score += overlap

    publication_year = candidate.get("publication_year")
    if target_year and publication_year and str(publication_year) == str(target_year):
        score += 20

    return score


def fetch_openalex_citation(title: str, year: Optional[str]) -> Optional[int]:
    params = urlencode({
        "filter": f"display_name.search:{title}",
        "per-page": "8",
        "mailto": MAILTO,
    })
    request = Request(
        f"https://api.openalex.org/works?{params}",
        headers={"User-Agent": f"ziyuanyang-homepage-bot/1.0 ({MAILTO})"},
    )
    with urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    candidates = data.get("results") or []
    best_candidate = None
    best_score = -1
    for candidate in candidates:
        score = score_candidate(title, year, candidate)
        if score > best_score:
            best_score = score
            best_candidate = candidate

    if best_candidate is None or best_score < 20:
        return None

    return int(best_candidate.get("cited_by_count") or 0)


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


def process_file(path: Path) -> bool:
    text = path.read_text()
    lines, body = parse_front_matter(text)
    title = extract_field(lines, "title")
    date_value = extract_field(lines, "date")
    year = date_value[:4] if date_value else None
    if not title:
        return False

    citation_count = fetch_openalex_citation(title, year)
    time.sleep(0.2)
    if citation_count is None:
        return False

    new_lines = upsert_citation_count(lines, citation_count)
    new_text = "---\n" + "\n".join(new_lines) + "\n---" + body
    if new_text == text:
        return False

    path.write_text(new_text)
    return True


def main() -> int:
    changed = []
    for path in sorted(PUBLICATIONS_DIR.rglob("*.md")):
        try:
            if process_file(path):
                changed.append(path)
                print(f"updated {path.relative_to(ROOT)}")
        except Exception as exc:
            print(f"warning: failed to update {path.relative_to(ROOT)}: {exc}")

    print(f"done, updated {len(changed)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
