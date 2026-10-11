#!/usr/bin/env python3
"""Copy teacher-uploaded readable files from the vault-outside raw store
into {Course}/readings/ with human-readable names.

Copies, never symlinks (Syncthing/mobile safe). Deduplicates with -2/-3
suffixes; skips files whose content already exists in readings/.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

READABLE_EXTS = {".pdf", ".docx", ".pptx"}


def sanitize(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', "_", name).strip()
    return name[:120] or "untitled"


def file_hash(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Extract readable documents from the raw store into readings/."
    )
    ap.add_argument("--data-dir", required=True, type=Path,
                    help="e.g. {Root}/{Semester}.data/{Course}")
    ap.add_argument("--course-dir", required=True, type=Path,
                    help="e.g. {Root}/{Semester}/{Course}")
    args = ap.parse_args()

    src_root = args.data_dir / "raw" / "files"
    dest_root = args.course_dir / "readings"
    dest_root.mkdir(parents=True, exist_ok=True)

    copied, skipped, errors = [], [], []
    if not src_root.is_dir():
        print(json.dumps({"copied": copied, "skipped": skipped,
                           "errors": errors, "note": "no raw/files yet"}))
        return

    for src in sorted(src_root.rglob("*")):
        if not src.is_file() or src.suffix.lower() not in READABLE_EXTS:
            continue
        stem = sanitize(src.stem)
        ext = src.suffix.lower()
        dest = dest_root / f"{stem}{ext}"
        n = 2
        while dest.exists() and file_hash(dest) != file_hash(src):
            dest = dest_root / f"{stem}-{n}{ext}"
            n += 1
        if dest.exists():
            skipped.append(dest.name)
            continue
        try:
            shutil.copy2(src, dest)
            copied.append(dest.name)
        except OSError as e:
            errors.append(f"{src}: {e}")

    print(json.dumps({"copied": copied, "skipped": skipped,
                      "errors": errors}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
