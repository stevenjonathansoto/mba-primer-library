"""Consistency checks for the primer library. Standard library only.

Run from the repo root:
    python scripts/check_site.py

Exits 0 when everything passes, 1 otherwise. Checks:
  - every card's download link points at a file that exists
  - every primer file in the repo is linked from a card (no orphans)
  - card ids are present, shaped like card-<slug>, and unique
  - every data-category token is one of the filter options the page offers
  - every card has the required fields (title, search keywords, read time,
    "Last Updated", download link)

If you change the card markup or move card data out of index.html, update this
script in the same change so the checks keep describing the real site.
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
PRIMER_EXTENSIONS = (".docx", ".pdf")
REQUIRED_ATTRS = {"category": "data-category", "keywords": "data-title", "read_time": "data-read-time"}
LAST_UPDATED_RE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$"
)


class CardParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards = []
        self._card = None
        self._depth = 0
        self._capture = None  # which text field we're inside, if any

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()

        if self._card is None:
            if tag == "div" and "primer-card" in classes:
                self._card = {
                    "id": a.get("id"),
                    "status": a.get("data-status", "legacy"),
                    "category": a.get("data-category"),
                    "keywords": a.get("data-title"),
                    "read_time": a.get("data-read-time"),
                    "title": "",
                    "updated": "",
                    "downloads": [],
                }
                self._depth = 1
            return

        if tag == "div":
            self._depth += 1
            if "card-updated" in classes:
                self._capture = "updated"
        elif tag == "h3" and "card-title" in classes:
            self._capture = "title"
        elif tag == "a" and a.get("href", "").lower().endswith(PRIMER_EXTENSIONS):
            self._card["downloads"].append(a["href"])

    def handle_endtag(self, tag):
        if self._card is None:
            return
        if tag == "h3" and self._capture == "title":
            self._capture = None
        if tag == "div":
            if self._capture == "updated":
                self._capture = None
            self._depth -= 1
            if self._depth == 0:
                self.cards.append(self._card)
                self._card = None

    def handle_data(self, data):
        if self._card is not None and self._capture:
            self._card[self._capture] += data


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    parser = CardParser()
    parser.feed(html)
    cards = parser.cards

    allowed = set(re.findall(r"toggleFilter\('([^']+)'", html)) - {"all"}
    failures = []

    if not cards:
        failures.append("no primer cards found")
    seen_ids = {}
    linked = set()
    for i, c in enumerate(cards, 1):
        label = c["id"] or f"card #{i}"

        if not c["id"]:
            failures.append(f"{label}: missing id")
        elif not re.fullmatch(r"card-[a-z0-9]+(-[a-z0-9]+)*", c["id"]):
            failures.append(f"{label}: id should look like card-<lowercase-slug>")
        elif c["id"] in seen_ids:
            failures.append(f"{label}: duplicate id (also card #{seen_ids[c['id']]})")
        else:
            seen_ids[c["id"]] = i

        for field, attr in REQUIRED_ATTRS.items():
            if not c[field]:
                failures.append(f"{label}: missing {attr}")
        if not c["title"].strip():
            failures.append(f"{label}: missing card-title")

        updated = re.sub(r"\s+", " ", c["updated"]).replace("Last Updated:", "").strip()
        if not LAST_UPDATED_RE.match(updated):
            failures.append(f"{label}: 'Last Updated' should be '<Month> <YYYY>', got {updated!r}")

        for token in (c["category"] or "").split():
            if allowed and token not in allowed:
                failures.append(
                    f"{label}: category '{token}' is not a filter option ({', '.join(sorted(allowed))})"
                )

        if c["status"] not in {"legacy", "validated", "coming-soon"}:
            failures.append(f"{label}: unknown status")
        if c["status"] == "coming-soon" and c["downloads"]:
            failures.append(f"{label}: coming-soon card must not have downloads")
        if not c["downloads"] and c["status"] != "coming-soon":
            failures.append(f"{label}: no download link")
        for href in c["downloads"]:
            linked.add(href)
            if not (ROOT / href).is_file():
                failures.append(f"{label}: download link points at a missing file: {href}")

    present = {
        p.relative_to(ROOT).as_posix()
        for ext in PRIMER_EXTENSIONS
        for p in ROOT.rglob(f"*{ext}")
        if ".git" not in p.parts and "node_modules" not in p.parts
    }
    for orphan in sorted(present - linked):
        failures.append(f"orphan primer (no card links to it): {orphan}")

    print(f"checked {len(cards)} cards, {len(present)} primer files, "
          f"{len(allowed)} filter categories")
    if failures:
        for f in failures:
            print(f"FAIL  {f}")
        print(f"\n{len(failures)} problem(s)")
        return 1
    print("OK    all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
