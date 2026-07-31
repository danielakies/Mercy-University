"""Parse every inline <script> in the dashboard so syntax errors surface before a browser does."""
import pathlib
import re
import sys

import esprima

HTML = pathlib.Path(__file__).resolve().parents[2] / "mercy-main-hall-dashboard.html"
src = HTML.read_text(encoding="utf-8")

blocks = list(re.finditer(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", src, re.S))
print(f"{len(blocks)} inline script block(s)")
bad = 0
for i, m in enumerate(blocks):
    code = m.group(1)
    line0 = src.count("\n", 0, m.start(1)) + 1
    # esprima predates ES2020, so neutralise the two bits of it the dashboard uses
    probe = code.replace("??", "||").replace("?.[", "[").replace("?.(", "(").replace("?.", ".")
    try:
        esprima.parseScript(probe)
        print(f"  block {i} (html line {line0}, {len(code.splitlines())} lines): OK")
    except Exception as e:  # noqa: BLE001
        bad += 1
        ln = getattr(e, "lineNumber", None)
        print(f"  block {i} (html line {line0}): FAIL {e}")
        if ln:
            rows = probe.splitlines()
            for j in range(max(1, ln - 2), min(len(rows), ln + 2) + 1):
                print(f"    html {line0 + j - 1:>5}: {rows[j - 1][:160]}")
sys.exit(1 if bad else 0)
