from __future__ import annotations

import pathlib
import re
import sys


CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    bad_files: list[str] = []

    for md_file in root.rglob("*.md"):
        if ".git" in md_file.parts:
            continue
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        if CJK_PATTERN.search(text):
            bad_files.append(str(md_file.relative_to(root)))

    if bad_files:
        print("Non-English or non-ASCII content detected in:")
        for file in bad_files:
            print(f"- {file}")
        return 1

    print("Markdown English check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
