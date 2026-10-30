#!/usr/bin/env python3
"""Check that every source_url and url in the packs answers over HTTPS (run in CI monthly)."""
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_packs import PACKS, load_yaml  # noqa: E402


def urls():
    for f in sorted(PACKS.glob("*/*.yaml")):
        if f.parent.name.startswith("_"):
            continue
        data = load_yaml(f) or {}
        stack = [data]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in ("url", "source_url") and isinstance(v, str):
                        yield f"{f.parent.name}/{f.name}", v
                    else:
                        stack.append(v)
            elif isinstance(x, list):
                stack.extend(x)


def main():
    bad = 0
    seen = {}
    for where, url in urls():
        if url not in seen:
            try:
                req = urllib.request.Request(url, method="GET", headers={"User-Agent": "open-jx-link-check"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    seen[url] = r.status
            except Exception as e:  # noqa: BLE001
                seen[url] = str(e)[:80]
        status = seen[url]
        if status != 200:
            bad += 1
            print(f"BROKEN {where}: {url} -> {status}")
    print(f"{len(seen)} unique URLs, {bad} broken reference(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
