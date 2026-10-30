#!/usr/bin/env python3
"""Static checks on the built Copilot Cowork package (no tenant needed).

    python evals/check_package.py dist/open-jx-0.1.0.zip

Mirrors the published Copilot Cowork plugin rules (manifest v1.28 root keys,
ASKILL-M001–M003, ASKILL-P001–P008, companion-file limits and path rules) and
adds open-jx checks: every pack in packs/ is compiled, every companion file is
referenced from its SKILL.md, router routing table names only known skills.
Exit code 1 on any error.
"""
from __future__ import annotations

import io
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_KEYS = {"$schema", "manifestVersion", "version", "id", "developer", "name", "description", "icons",
                 "accentColor", "agentSkills", "agentConnectors", "localizationInfo"}
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
SAFE = re.compile(r"^[A-Za-z0-9\-_. !]+$")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
GUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
LEGAL_SKILLS = {"analyze-related-contracts", "build-case-chronology", "check-cross-references", "check-defined-terms",
                "check-execution-readiness", "compare-across-jurisdictions", "compare-key-terms", "create-playbook",
                "draft-legal-memo", "draft-minutes-and-resolutions", "draft-new-contract", "edit-contract",
                "explain-legal-concepts", "extract-obligations-and-deadlines", "identify-regulatory-gaps",
                "improve-legal-prompt", "legal-reasoning", "review-contract", "summarize-legal-matters",
                "summarize-redlines"}

errors: list[str] = []
notes: list[str] = []


def err(code, msg):
    errors.append(f"ERROR {code}: {msg}")


def ok(msg):
    notes.append(f"ok    {msg}")


def frontmatter(text: str):
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    try:
        return yaml.safe_load(parts[1]), parts[2]
    except yaml.YAMLError:
        return None, parts[2]


def main(zip_path: Path) -> int:
    z = zipfile.ZipFile(zip_path)
    names = [n for n in z.namelist() if not n.endswith("/")]
    for n in names:
        for part in PurePosixPath(n).parts:
            if part.startswith("."):
                err("PATH", f"hidden file or folder not allowed: {n}")
            if not SAFE.match(part):
                err("PATH", f"unsafe characters in path: {n}")
            if part.split(".")[0].upper() in RESERVED:
                err("PATH", f"reserved name: {n}")
        if "\\" in n or ".." in n:
            err("PATH", f"backslash or '..' in path: {n}")
    ok(f"{len(names)} files, path rules checked")

    # manifest
    if "manifest.json" not in names:
        err("MANIFEST", "manifest.json missing at zip root")
        return report()
    m = json.loads(z.read("manifest.json"))
    extra = set(m) - MANIFEST_KEYS
    if extra:
        err("MANIFEST", f"root keys not allowed by the v1.28 schema: {sorted(extra)}")
    if m.get("manifestVersion") not in ("1.28", "1.29"):
        err("MANIFEST", f"manifestVersion {m.get('manifestVersion')} (expected 1.28 or 1.29)")
    if not GUID.match(str(m.get("id", ""))):
        err("MANIFEST", "id must be a GUID")
    dev = m.get("developer", {})
    for k in ("name", "websiteUrl", "privacyUrl", "termsOfUseUrl"):
        if not dev.get(k):
            err("MANIFEST", f"developer.{k} missing")
        elif k != "name" and not str(dev[k]).startswith("https://"):
            err("MANIFEST", f"developer.{k} must be https")
    if "YOUR-GITHUB-HANDLE" in json.dumps(dev):
        notes.append("WARN  developer URLs still use the YOUR-GITHUB-HANDLE placeholder; set repo_url in build.config.json")
    if len(m.get("name", {}).get("short", "")) > 30:
        err("MANIFEST", "name.short over 30 characters")
    if len(m.get("description", {}).get("short", "")) > 80:
        err("MANIFEST", "description.short over 80 characters")
    if len(m.get("description", {}).get("full", "")) > 4000:
        err("MANIFEST", "description.full over 4000 characters")
    for key, size in (("color", (192, 192)), ("outline", (32, 32))):
        f = m.get("icons", {}).get(key)
        if f not in names:
            err("ICON", f"{key} icon {f} missing")
            continue
        im = Image.open(io.BytesIO(z.read(f)))
        if im.size != size:
            err("ICON", f"{f} is {im.size}, expected {size}")
        if key == "outline" and im.mode == "RGBA":
            px = im.load()
            colours = {px[x, y][:3] for x in range(im.width) for y in range(im.height) if px[x, y][3] > 0}
            if colours - {(255, 255, 255)}:
                err("ICON", "outline icon must be white on transparent")
    ok("manifest and icons")

    skills = m.get("agentSkills", [])
    if not skills:
        err("ASKILL-M001", "no agentSkills")
    if len(skills) > 20:
        err("ASKILL-M002", f"{len(skills)} skills (max 20)")
    seen = set()
    skill_names = set()
    for s in skills:
        folder = s.get("folder", "")
        if not folder:
            err("ASKILL-M001", "agentSkills entry without folder")
            continue
        if len(folder) > 256:
            err("ASKILL-M003", f"folder path over 256 chars: {folder}")
        rel = folder[2:] if folder.startswith("./") else folder
        if rel in seen:
            err("ASKILL-P008", f"duplicate folder {rel}")
        seen.add(rel)
        skill_md = f"{rel}/SKILL.md"
        if not any(n.startswith(rel + "/") for n in names):
            err("ASKILL-P001", f"folder {rel} not in zip")
            continue
        if skill_md not in names:
            err("ASKILL-P002", f"{skill_md} missing")
            continue
        text = z.read(skill_md).decode("utf-8")
        fm, body = frontmatter(text)
        if fm is None:
            err("ASKILL-P003", f"{skill_md}: invalid YAML frontmatter")
            continue
        name, desc = fm.get("name"), fm.get("description")
        if not name or not desc:
            err("ASKILL-P004", f"{skill_md}: name and description required")
            continue
        folder_name = PurePosixPath(rel).name
        if name != folder_name or not KEBAB.match(name) or len(name) > 64:
            err("ASKILL-P005", f"{skill_md}: name '{name}' must be kebab-case, ≤64 chars and equal the folder '{folder_name}'")
        if not 1 <= len(desc) <= 1024:
            err("DESC", f"{name}: description is {len(desc)} chars (1–1024)")
        skill_names.add(name)
        words = len(body.split())
        if words * 1.35 > 5000:
            err("BODY", f"{name}: body ≈{int(words * 1.35)} tokens (target under 5,000)")
        companions = [n for n in names if n.startswith(rel + "/") and n != skill_md]
        if len(companions) > 20:
            err("COMPANION", f"{name}: {len(companions)} companion files (max 20)")
        total = 0
        for c in companions:
            size = z.getinfo(c).file_size
            total += size
            if size > 5 * 1024 * 1024:
                err("COMPANION", f"{c} over 5 MB")
            rel_c = c[len(rel) + 1:]
            parent_ref = str(PurePosixPath(rel_c).parent) + "/"
            if rel_c not in text and parent_ref not in text:
                notes.append(f"WARN  {c} is not referenced from {name}/SKILL.md")
        if total > 10 * 1024 * 1024:
            err("COMPANION", f"{name}: companion files total over 10 MB")
        ok(f"{name}: {len(desc)}-char description, ≈{int(words * 1.35)} body tokens, {len(companions)} companion files")

    # open-jx specific
    packs = sorted(p.name for p in (ROOT / "packs").iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))
    index = z.read("skills/jx-router/references/jurisdictions.md").decode() if "skills/jx-router/references/jurisdictions.md" in names else ""
    for p in packs:
        if f"| {p} |" not in index:
            err("PACKS", f"pack {p} is not in the compiled jurisdiction index")
    ok(f"{len(packs)} packs compiled: {', '.join(packs)}")
    router = z.read("skills/jx-router/SKILL.md").decode() if "skills/jx-router/SKILL.md" in names else ""
    if "<!-- BEGIN GENERATED PACK LIST -->\n<!-- END" in router:
        err("ROUTER", "generated pack list is empty")
    referenced = set(re.findall(r"\b(jx-[a-z-]+)\b", router))
    unknown = referenced - skill_names
    if unknown:
        err("ROUTER", f"router names skills not in the package: {sorted(unknown)}")
    table = router.split("## Routing table", 1)[-1].split("##", 1)[0]
    legal_named = set(re.findall(r"\b([a-z]+(?:-[a-z]+)+)\b", table)) - referenced - {"open-jx"}
    unknown_legal = legal_named - LEGAL_SKILLS
    if unknown_legal:
        err("ROUTER", f"routing table names unknown Legal for Cowork skills: {sorted(unknown_legal)}")
    missing_legal = LEGAL_SKILLS - legal_named
    if missing_legal:
        notes.append(f"WARN  routing table does not mention: {sorted(missing_legal)}")
    ok("router routing table checked against the 20 Legal for Cowork skills")
    return report()


def report() -> int:
    for n in notes:
        print(n)
    for e in errors:
        print(e)
    print(f"\n{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(Path(sys.argv[1])))
