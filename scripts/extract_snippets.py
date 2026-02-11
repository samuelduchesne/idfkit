"""Extract Python code blocks from docs markdown into standalone snippet files.

This script:
1. Parses each markdown file under docs/
2. Finds all ```python code blocks
3. Creates snippet files under docs/snippets/ mirroring the docs structure
4. Replaces inline code blocks with --8<-- snippet includes
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
SNIPPETS_DIR = DOCS_DIR / "snippets"

# Markdown files to process (relative to docs/)
# Excludes api/ (auto-generated) and .ipynb notebooks
EXCLUDE_DIRS = {"api", "overrides", "snippets", "troubleshooting", "stylesheets"}


def slugify(text: str) -> str:
    """Convert a heading to a snake_case filename stem."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "_", text)
    text = text.strip("_")
    return text


def extract_code_blocks(md_path: Path) -> list[dict[str, str | int]]:
    """Extract all python fenced code blocks from a markdown file.

    Returns a list of dicts with keys:
      - code: the code content
      - start_line: line number of opening ```python
      - end_line: line number of closing ```
      - heading: nearest preceding heading text
    """
    content = md_path.read_text()
    lines = content.split("\n")

    blocks: list[dict[str, str | int]] = []
    current_heading = "example"
    in_code_block = False
    code_lines: list[str] = []
    block_start = 0
    fence_lang = ""

    for i, line in enumerate(lines):
        # Track headings
        heading_match = re.match(r"^#{1,6}\s+(.+?)(?:\s*\{.*\})?\s*$", line)
        if heading_match and not in_code_block:
            current_heading = heading_match.group(1)
            continue

        # Start of fenced code block
        if not in_code_block and re.match(r"^```python\s*$", line):
            in_code_block = True
            fence_lang = "python"
            code_lines = []
            block_start = i
            continue

        # End of fenced code block
        if in_code_block and re.match(r"^```\s*$", line):
            if fence_lang == "python":
                blocks.append({
                    "code": "\n".join(code_lines),
                    "start_line": block_start,
                    "end_line": i,
                    "heading": current_heading,
                })
            in_code_block = False
            fence_lang = ""
            continue

        # Inside code block
        if in_code_block:
            code_lines.append(line)

    return blocks


def generate_snippet_name(heading: str, index: int, seen: dict[str, int]) -> str:
    """Generate a unique snippet filename from a heading."""
    base = slugify(heading)
    if not base:
        base = "example"

    # Truncate very long names
    if len(base) > 50:
        base = base[:50].rstrip("_")

    key = base
    if key in seen:
        seen[key] += 1
        return f"{base}_{seen[key]}"
    else:
        seen[key] = 1
        return base


def process_file(md_path: Path) -> int:
    """Process a single markdown file, extracting code blocks to snippets.

    Returns the number of code blocks extracted.
    """
    blocks = extract_code_blocks(md_path)
    if not blocks:
        return 0

    # Determine snippet directory
    rel = md_path.relative_to(DOCS_DIR)
    snippet_dir = SNIPPETS_DIR / rel.with_suffix("")
    snippet_dir.mkdir(parents=True, exist_ok=True)

    # Read the original content
    content = md_path.read_text()
    lines = content.split("\n")

    # Pre-compute names in forward order so numbering is correct
    seen_names: dict[str, int] = {}
    snippet_names: list[str] = []
    for block in blocks:
        heading = str(block["heading"])
        name = generate_snippet_name(heading, 0, seen_names)
        snippet_names.append(name)

    # Apply replacements in reverse order so line numbers stay valid
    for i in range(len(blocks) - 1, -1, -1):
        block = blocks[i]
        name = snippet_names[i]
        start = int(block["start_line"])
        end = int(block["end_line"])
        code = str(block["code"])

        snippet_file = snippet_dir / f"{name}.py"

        # Write snippet file
        snippet_file.write_text(code + "\n")

        # Compute the include path relative to project root
        include_path = snippet_file.relative_to(PROJECT_ROOT)

        # Replace the code block content (keep the fences)
        # Original: ```python\n<code>\n```
        # New:      ```python\n--8<-- "<path>"\n```
        lines[start] = "```python"
        lines[start + 1 : end] = [f'--8<-- "{include_path}"']

    # Write modified markdown
    md_path.write_text("\n".join(lines))

    return len(blocks)


def find_markdown_files() -> list[Path]:
    """Find all non-excluded markdown files under docs/."""
    files = []
    for md_path in sorted(DOCS_DIR.rglob("*.md")):
        rel = md_path.relative_to(DOCS_DIR)
        parts = rel.parts
        if any(part in EXCLUDE_DIRS for part in parts):
            continue
        files.append(md_path)
    return files


def main() -> None:
    total = 0
    files = find_markdown_files()
    print(f"Found {len(files)} markdown files to process")

    for md_path in files:
        count = process_file(md_path)
        if count > 0:
            rel = md_path.relative_to(DOCS_DIR)
            print(f"  {rel}: {count} code blocks extracted")
            total += count

    print(f"\nTotal: {total} code blocks extracted to {SNIPPETS_DIR.relative_to(PROJECT_ROOT)}/")


if __name__ == "__main__":
    main()
