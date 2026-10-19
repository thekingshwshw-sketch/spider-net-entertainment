#!/usr/bin/env python3
"""Dependency-light static checks for the Spider Net Entertainment site."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "admin.html", "connect.html")
MAX_HTML_BYTES = 90_000
SCRIPT_RE = re.compile(r"<script\b[^>]*>([\s\S]*?)</script\s*>", re.I)
SCRIPT_OPEN_RE = re.compile(r"<script\b", re.I)
SCRIPT_CLOSE_RE = re.compile(r"</script\s*>", re.I)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_attrs: dict[str, str] = {}
        self.viewports = 0
        self.titles = 0
        self.links: list[tuple[str, str]] = []
        self.blank_targets_without_rel: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "html":
            self.html_attrs = attr
        if tag.lower() == "meta" and attr.get("name", "").lower() == "viewport":
            self.viewports += 1
        if tag.lower() == "title":
            self.titles += 1
        for name in ("href", "src"):
            value = attr.get(name, "").strip()
            if value:
                self.links.append((name, value))
        if tag.lower() == "a" and attr.get("target", "").lower() == "_blank":
            rel = set(attr.get("rel", "").lower().split())
            if not {"noopener", "noreferrer"}.intersection(rel):
                self.blank_targets_without_rel.append(attr.get("href", "(unknown)"))


def fail(message: str) -> None:
    print("FAIL:", message)
    raise SystemExit(1)


def check_page(name: str, node: str | None) -> None:
    path = ROOT / name
    if not path.is_file() or path.stat().st_size == 0:
        fail(f"required page missing or empty: {name}")
    raw = path.read_text(encoding="utf-8")
    lower = raw.lower()
    size = path.stat().st_size
    print(f"\n[{name}] {size:,} bytes")
    if size > MAX_HTML_BYTES:
        fail(f"{name} exceeds {MAX_HTML_BYTES:,} bytes; review inline assets.")
    if "<!doctype html>" not in lower:
        fail(f"{name} is missing the HTML doctype.")
    if "</html>" not in lower:
        fail(f"{name} is missing the closing html tag.")
    if re.search(r"data:image/[^;]+;base64,", raw, re.I):
        fail(f"{name} embeds a Base64 image; use a small external optimized asset instead.")

    parser = PageParser()
    parser.feed(raw)
    parser.close()
    if parser.html_attrs.get("lang", "").lower() != "ar":
        fail(f"{name} must declare lang='ar'.")
    if parser.html_attrs.get("dir", "").lower() != "rtl":
        fail(f"{name} must declare dir='rtl'.")
    if parser.viewports != 1:
        fail(f"{name} must contain exactly one viewport meta tag.")
    if parser.titles != 1:
        fail(f"{name} must contain exactly one title element.")
    if parser.blank_targets_without_rel:
        fail(f"{name} has target=_blank links without rel=noopener/noreferrer.")

    opens = len(SCRIPT_OPEN_RE.findall(raw))
    closes = len(SCRIPT_CLOSE_RE.findall(raw))
    scripts = SCRIPT_RE.findall(raw)
    if opens != closes or len(scripts) != opens:
        fail(f"{name} has mismatched script tags (open={opens}, close={closes}, paired={len(scripts)}).")

    for attr, value in parser.links:
        if value.startswith("#") or value.startswith("//"):
            continue
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or value.startswith("data:"):
            continue
        rel_path = unquote(parsed.path)
        if not rel_path:
            continue
        target = (ROOT / rel_path).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            fail(f"{name} reference escapes repository root: {value}")
        if not target.is_file():
            fail(f"{name} has a missing local {attr} target: {value}")

    for index, source in enumerate(scripts, start=1):
        if not source.strip():
            continue
        if node is None:
            fail("Node.js is required by CI to syntax-check inline JavaScript.")
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as temp:
            temp.write(source)
            temp_path = Path(temp.name)
        try:
            result = subprocess.run(
                [node, "--check", str(temp_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode:
                print(result.stdout)
                print(result.stderr)
                fail(f"{name} inline JavaScript block #{index} failed node --check.")
        finally:
            temp_path.unlink(missing_ok=True)
    print("PASS: Arabic RTL, size, tags, local paths, and inline JavaScript syntax.")


def main() -> int:
    node = shutil.which("node")
    if node is None:
        fail("Node.js was not found. CI installs it on the Ubuntu runner.")
    for page in PAGES:
        check_page(page, node)
    readme = ROOT / "README.md"
    if not readme.is_file() or readme.stat().st_size == 0:
        fail("README.md is missing or empty.")
    for required in ("LAN_DEPLOYMENT_AR.md", "scripts/Check-SpiderNetLAN.ps1"):
        if not (ROOT / required).is_file():
            fail(f"required operational document/script missing: {required}")
    print("\nAll static checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
