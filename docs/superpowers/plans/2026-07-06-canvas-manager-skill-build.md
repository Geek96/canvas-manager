# CanvasManager Skill Build — Implementation Plan

> **Note for external readers:** this is the original build plan kept for
> historical reference — it's how this skill was built, not something you
> need to read to use it (start from the top-level `README.md` instead).
> The "PlanVault repo" and `docs/superpowers/specs/...` design spec it
> references below live in a separate, private repo and aren't published
> alongside this one.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the standalone `CanvasManager` Claude Code plugin/skill: a reusable rule set that lets any student sync Canvas LMS course content into a semester/course-organized Obsidian vault, with a deterministic Python sync engine underneath and agent-authored SKILL.md/references/templates on top.

**Architecture:** A small, dependency-free Python module (`skills/canvas-manager/scripts/`) owns the mechanical, must-be-correct part of the pipeline — hashing content, diffing against a manifest, writing append-only raw snapshots, writing sync logs. `SKILL.md` and `references/*.md` own everything that requires judgment (calling the user's Canvas MCP, normalizing its output into the script's input schema, and digesting raw snapshots into `wiki/` notes). This split keeps the risky, hard-to-eyeball logic (idempotency, never-overwrite) in tested code, and keeps the parts that genuinely need an agent's judgment in instructions.

**Tech Stack:** Python 3 standard library only (`argparse`, `json`, `hashlib`, `pathlib`, `datetime`, `unittest`) — no external dependencies, no virtualenv required. Markdown + YAML frontmatter for all skill content and data files.

Design reference: see `docs/superpowers/specs/2026-07-06-canvas-manager-design.md` in the PlanVault repo for the full brainstormed spec this plan implements.

---

### Task 1: Repo scaffold

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.gitignore`
- Create: `README.md`
- Create: `skills/canvas-manager/scripts/__init__.py` (empty, makes the dir importable if ever packaged)

- [ ] **Step 1: Create the directory skeleton**

```bash
mkdir -p .claude-plugin
mkdir -p skills/canvas-manager/scripts
mkdir -p skills/canvas-manager/references
mkdir -p skills/canvas-manager/templates
mkdir -p tests/fixtures
```

- [ ] **Step 2: Write `.claude-plugin/plugin.json`**

```json
{
  "name": "canvas-manager",
  "version": "0.1.0",
  "description": "Sync Canvas LMS courses into a semester/course-organized Obsidian vault, with structured hand-off to daily planning tools",
  "author": {
    "name": "Geek96",
    "url": "https://github.com/Geek96"
  },
  "license": "MIT",
  "keywords": ["canvas", "lms", "obsidian", "students", "planning"],
  "skills": [
    "./skills/canvas-manager"
  ]
}
```

- [ ] **Step 3: Write `.gitignore`**

```gitignore
__pycache__/
*.pyc
.DS_Store
```

- [ ] **Step 4: Write a stub `README.md`**

```markdown
# CanvasManager

A Claude Code skill that syncs Canvas LMS courses into a semester → course
organized Obsidian vault (`raw/` = Canvas evidence, `wiki/` = your learning
notes), on a schedule you control.

Standalone usage: install this repo as a Claude Code plugin and follow
`skills/canvas-manager/SKILL.md`.

Optional PlanVault integration: PlanVault can pull this repo in as a git
submodule for users who want Canvas course management alongside their daily
planning. See PlanVault's own docs for that wiring.
```

- [ ] **Step 5: Create empty `scripts/__init__.py`**

```bash
touch skills/canvas-manager/scripts/__init__.py
```

- [ ] **Step 6: Commit**

```bash
git add .claude-plugin .gitignore README.md skills tests
git commit -m "chore: scaffold CanvasManager repo"
```

---

### Task 2: `manifest.py` — manifest load/save/hash/diff

**Files:**
- Create: `skills/canvas-manager/scripts/manifest.py`
- Test: `tests/test_manifest.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_manifest.py
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager" / "scripts"))

import manifest as manifest_mod  # noqa: E402


class TestManifest(unittest.TestCase):
    def test_load_manifest_missing_file_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = manifest_mod.load_manifest(Path(tmp) / "canvas-objects.json")
            self.assertEqual(result, {})

    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest" / "canvas-objects.json"
            data = {"assignments/1": {"title": "Homework 1", "content_hash": "abc"}}
            manifest_mod.save_manifest(path, data)
            self.assertEqual(manifest_mod.load_manifest(path), data)

    def test_compute_content_hash_deterministic(self):
        h1 = manifest_mod.compute_content_hash("hello")
        h2 = manifest_mod.compute_content_hash("hello")
        self.assertEqual(h1, h2)

    def test_compute_content_hash_changes_with_content(self):
        h1 = manifest_mod.compute_content_hash("hello")
        h2 = manifest_mod.compute_content_hash("hello world")
        self.assertNotEqual(h1, h2)

    def test_diff_object_new_when_key_absent(self):
        self.assertEqual(manifest_mod.diff_object({}, "assignments/1", "abc"), "new")

    def test_diff_object_changed_when_hash_differs(self):
        state = {"assignments/1": {"content_hash": "old"}}
        self.assertEqual(manifest_mod.diff_object(state, "assignments/1", "new"), "changed")

    def test_diff_object_unchanged_when_hash_matches(self):
        state = {"assignments/1": {"content_hash": "same"}}
        self.assertEqual(manifest_mod.diff_object(state, "assignments/1", "same"), "unchanged")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s tests -v`
Expected: `ModuleNotFoundError: No module named 'manifest'` (module doesn't exist yet).

- [ ] **Step 3: Write the minimal implementation**

```python
# skills/canvas-manager/scripts/manifest.py
"""Manifest read/write/diff helpers for CanvasManager raw snapshots."""
import hashlib
import json
from pathlib import Path


def load_manifest(manifest_path: Path) -> dict:
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def save_manifest(manifest_path: Path, manifest: dict) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def compute_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def diff_object(manifest: dict, key: str, content_hash: str) -> str:
    entry = manifest.get(key)
    if entry is None:
        return "new"
    if entry.get("content_hash") != content_hash:
        return "changed"
    return "unchanged"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: `Ran 7 tests in ...s` / `OK`

- [ ] **Step 5: Commit**

```bash
git add skills/canvas-manager/scripts/manifest.py tests/test_manifest.py
git commit -m "feat: add manifest load/save/hash/diff helpers"
```

---

### Task 3: `snapshot.py` — snapshot + sync-log writers

**Files:**
- Create: `skills/canvas-manager/scripts/snapshot.py`
- Test: `tests/test_snapshot.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_snapshot.py
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager" / "scripts"))

import snapshot as snapshot_mod  # noqa: E402


SAMPLE_OBJ = {
    "canvas_type": "assignment",
    "canvas_id": 12345,
    "course_id": 67890,
    "title": "Homework 4",
    "updated_at_canvas": "2026-07-09T07:55:00",
    "source_url": "https://school.instructure.com/courses/67890/assignments/12345",
    "content": "Due Friday.",
}


class TestSnapshot(unittest.TestCase):
    def test_format_snapshot_includes_frontmatter_fields(self):
        text = snapshot_mod.format_snapshot(SAMPLE_OBJ, "2026-07-06T10:30:00")
        self.assertIn("canvas_type: assignment", text)
        self.assertIn("canvas_id: 12345", text)
        self.assertIn("source_url: https://school.instructure.com/courses/67890/assignments/12345", text)
        self.assertIn("Due Friday.", text)

    def test_write_snapshot_creates_file_at_expected_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            path = snapshot_mod.write_snapshot(course_dir, "assignments", SAMPLE_OBJ, "2026-07-06-103000", "2026-07-06T10:30:00")
            self.assertEqual(path, course_dir / "raw" / "assignments" / "12345" / "2026-07-06-103000.md")
            self.assertTrue(path.exists())

    def test_write_snapshot_never_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            first = snapshot_mod.write_snapshot(course_dir, "assignments", SAMPLE_OBJ, "2026-07-06-103000", "2026-07-06T10:30:00")
            changed = dict(SAMPLE_OBJ, content="Due Monday now.")
            second = snapshot_mod.write_snapshot(course_dir, "assignments", changed, "2026-07-06-103000", "2026-07-06T10:30:00")
            self.assertNotEqual(first, second)
            self.assertTrue(first.exists())
            self.assertTrue(second.exists())
            self.assertIn("Due Friday.", first.read_text())
            self.assertIn("Due Monday now.", second.read_text())

    def test_write_sync_log_lists_new_updated_unchanged_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            path = snapshot_mod.write_sync_log(
                course_dir, "2026-07-06-103000", "assignments",
                new_ids=["assignments/1"], updated_ids=["assignments/2"],
                unchanged_count=3, missing_ids=["assignments/4"],
            )
            text = path.read_text()
            self.assertIn("assignments/1", text)
            self.assertIn("assignments/2", text)
            self.assertIn("未变化: 3", text)
            self.assertIn("assignments/4", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s tests -v`
Expected: `ModuleNotFoundError: No module named 'snapshot'`

- [ ] **Step 3: Write the minimal implementation**

```python
# skills/canvas-manager/scripts/snapshot.py
"""Snapshot + sync-log writers for CanvasManager raw storage."""
from pathlib import Path


def format_snapshot(obj: dict, fetched_at: str) -> str:
    lines = ["---"]
    lines.append(f"canvas_type: {obj['canvas_type']}")
    lines.append(f"canvas_id: {obj['canvas_id']}")
    lines.append(f"course_id: {obj['course_id']}")
    lines.append(f"title: {obj['title']}")
    lines.append(f"fetched_at: {fetched_at}")
    lines.append(f"updated_at_canvas: {obj['updated_at_canvas']}")
    lines.append(f"source_url: {obj['source_url']}")
    lines.append("---")
    lines.append("")
    lines.append(obj["content"])
    return "\n".join(lines)


def _unique_path(candidate: Path) -> Path:
    """Never overwrite an existing raw file: append -2, -3, ... on collision."""
    if not candidate.exists():
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    n = 2
    while True:
        alt = candidate.with_name(f"{stem}-{n}{suffix}")
        if not alt.exists():
            return alt
        n += 1


def write_snapshot(course_dir: Path, object_type: str, obj: dict, fetched_at_slug: str, fetched_at: str) -> Path:
    snapshot_dir = course_dir / "raw" / object_type / str(obj["canvas_id"])
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = _unique_path(snapshot_dir / f"{fetched_at_slug}.md")
    snapshot_path.write_text(format_snapshot(obj, fetched_at), encoding="utf-8")
    return snapshot_path


def write_sync_log(course_dir: Path, fetched_at_slug: str, object_type: str, new_ids, updated_ids, unchanged_count, missing_ids) -> Path:
    log_dir = course_dir / "raw" / "sync"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = _unique_path(log_dir / f"{fetched_at_slug}-{object_type}.md")
    lines = [f"# Sync {fetched_at_slug} ({object_type})", ""]
    lines.append("新增:")
    lines += [f"- {i}" for i in new_ids] or ["- (none)"]
    lines.append("")
    lines.append("更新:")
    lines += [f"- {i}" for i in updated_ids] or ["- (none)"]
    lines.append("")
    lines.append(f"未变化: {unchanged_count}")
    lines.append("")
    lines.append("缺失/隐藏:")
    lines += [f"- {i}" for i in missing_ids] or ["- (none)"]
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path
```

Note the `_unique_path` guard: two syncs of *different* object types (or the same one) can land in the same wall-clock second — without this guard the second write would silently overwrite the first snapshot/log, breaking the append-only guarantee that the whole design depends on.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: `Ran 11 tests in ...s` / `OK`

- [ ] **Step 5: Commit**

```bash
git add skills/canvas-manager/scripts/snapshot.py tests/test_snapshot.py
git commit -m "feat: add snapshot and sync-log writers with collision-safe filenames"
```

---

### Task 4: `sync.py` — CLI orchestrator

**Files:**
- Create: `skills/canvas-manager/scripts/sync.py`
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_sync.py
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager" / "scripts"))

import sync as sync_mod  # noqa: E402


def make_obj(canvas_id, content, updated_at="2026-07-09T07:55:00"):
    return {
        "canvas_type": "assignment",
        "canvas_id": canvas_id,
        "course_id": 67890,
        "title": f"Homework {canvas_id}",
        "updated_at_canvas": updated_at,
        "source_url": f"https://school.instructure.com/courses/67890/assignments/{canvas_id}",
        "content": content,
    }


class TestSync(unittest.TestCase):
    def test_first_sync_writes_new_snapshots_for_all_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            objects = [make_obj(1, "Due Friday."), make_obj(2, "Due next Friday.")]
            result = sync_mod.run_sync(course_dir, "assignments", objects, datetime(2026, 7, 6, 10, 30, 0))
            self.assertEqual(sorted(result["new"]), ["assignments/1", "assignments/2"])
            self.assertEqual(result["updated"], [])
            self.assertEqual(result["unchanged"], 0)
            self.assertEqual(result["missing"], [])

    def test_second_sync_with_no_changes_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            objects = [make_obj(1, "Due Friday.")]
            sync_mod.run_sync(course_dir, "assignments", objects, datetime(2026, 7, 6, 10, 30, 0))
            result = sync_mod.run_sync(course_dir, "assignments", objects, datetime(2026, 7, 6, 18, 0, 0))
            self.assertEqual(result["new"], [])
            self.assertEqual(result["updated"], [])
            self.assertEqual(result["unchanged"], 1)
            snapshots = list((course_dir / "raw" / "assignments" / "1").glob("*.md"))
            self.assertEqual(len(snapshots), 1)

    def test_changed_object_appends_new_snapshot_and_keeps_old(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            sync_mod.run_sync(course_dir, "assignments", [make_obj(1, "Due Friday.")], datetime(2026, 7, 6, 10, 30, 0))
            result = sync_mod.run_sync(
                course_dir, "assignments",
                [make_obj(1, "Due Friday, extended to Monday.", updated_at="2026-07-11T07:55:00")],
                datetime(2026, 7, 6, 18, 0, 0),
            )
            self.assertEqual(result["updated"], ["assignments/1"])
            snapshots = sorted((course_dir / "raw" / "assignments" / "1").glob("*.md"))
            self.assertEqual(len(snapshots), 2)
            self.assertIn("Due Friday.", snapshots[0].read_text())
            self.assertIn("extended to Monday", snapshots[1].read_text())

    def test_object_missing_from_run_is_marked_missing_not_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            sync_mod.run_sync(course_dir, "assignments", [make_obj(1, "A"), make_obj(2, "B")], datetime(2026, 7, 6, 10, 30, 0))
            result = sync_mod.run_sync(course_dir, "assignments", [make_obj(1, "A")], datetime(2026, 7, 6, 18, 0, 0))
            self.assertEqual(result["missing"], ["assignments/2"])
            self.assertTrue((course_dir / "raw" / "assignments" / "2").exists())
            manifest = json.loads((course_dir / "raw" / "_manifest" / "canvas-objects.json").read_text())
            self.assertEqual(manifest["assignments/2"]["status"], "missing")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s tests -v`
Expected: `ModuleNotFoundError: No module named 'sync'`

- [ ] **Step 3: Write the minimal implementation**

```python
# skills/canvas-manager/scripts/sync.py
#!/usr/bin/env python3
"""CanvasManager sync engine: diffs incoming Canvas objects against the manifest
and writes new/changed raw snapshots without duplicating unchanged ones."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manifest as manifest_mod  # noqa: E402
import snapshot as snapshot_mod  # noqa: E402


def run_sync(course_dir: Path, object_type: str, objects: list, now: datetime) -> dict:
    manifest_path = course_dir / "raw" / "_manifest" / "canvas-objects.json"
    state = manifest_mod.load_manifest(manifest_path)

    fetched_at = now.isoformat(timespec="seconds")
    fetched_at_slug = now.strftime("%Y-%m-%d-%H%M%S")

    new_ids, updated_ids, missing_ids = [], [], []
    unchanged_count = 0
    seen_keys = set()

    for obj in objects:
        key = f"{object_type}/{obj['canvas_id']}"
        seen_keys.add(key)
        content_hash = manifest_mod.compute_content_hash(obj["content"])
        status = manifest_mod.diff_object(state, key, content_hash)

        if status == "unchanged":
            unchanged_count += 1
            continue

        snapshot_path = snapshot_mod.write_snapshot(
            course_dir, object_type, obj, fetched_at_slug, fetched_at
        )
        state[key] = {
            "canvas_type": obj["canvas_type"],
            "canvas_id": obj["canvas_id"],
            "course_id": obj["course_id"],
            "title": obj["title"],
            "latest_snapshot": str(snapshot_path.relative_to(course_dir)),
            "last_canvas_updated_at": obj["updated_at_canvas"],
            "content_hash": content_hash,
            "status": "active",
        }
        (new_ids if status == "new" else updated_ids).append(key)

    for key, entry in state.items():
        if key.startswith(f"{object_type}/") and key not in seen_keys and entry.get("status") == "active":
            entry["status"] = "missing"
            missing_ids.append(key)

    manifest_mod.save_manifest(manifest_path, state)
    snapshot_mod.write_sync_log(course_dir, fetched_at_slug, object_type, new_ids, updated_ids, unchanged_count, missing_ids)

    return {
        "new": new_ids,
        "updated": updated_ids,
        "unchanged": unchanged_count,
        "missing": missing_ids,
    }


def main():
    parser = argparse.ArgumentParser(description="Sync one Canvas object type into a course's raw/ store.")
    parser.add_argument("--course-dir", required=True, type=Path)
    parser.add_argument("--object-type", required=True, help="e.g. assignments, announcements, pages, modules")
    parser.add_argument("--input", required=True, type=Path, help="JSON file: list of normalized Canvas objects")
    args = parser.parse_args()

    objects = json.loads(args.input.read_text(encoding="utf-8"))
    result = run_sync(args.course_dir, args.object_type, objects, datetime.now())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s tests -v`
Expected: `Ran 15 tests in ...s` / `OK`

- [ ] **Step 5: Manually verify the CLI end-to-end**

```bash
mkdir -p /tmp/cm-smoke
cat > /tmp/cm-objs.json <<'EOF'
[{"canvas_type": "assignment", "canvas_id": 1, "course_id": 1, "title": "HW1", "updated_at_canvas": "2026-07-06T10:00:00", "source_url": "https://x/1", "content": "Do problems 1-5."}]
EOF
python3 skills/canvas-manager/scripts/sync.py --course-dir /tmp/cm-smoke --object-type assignments --input /tmp/cm-objs.json
```

Expected stdout: a JSON object with `"new": ["assignments/1"]`, `"unchanged": 0`, `"missing": []`. Confirm `/tmp/cm-smoke/raw/assignments/1/*.md` and `/tmp/cm-smoke/raw/_manifest/canvas-objects.json` were created, then `rm -rf /tmp/cm-smoke /tmp/cm-objs.json`.

- [ ] **Step 6: Commit**

```bash
git add skills/canvas-manager/scripts/sync.py tests/test_sync.py
git commit -m "feat: add sync.py CLI wiring manifest+snapshot into one command"
```

---

### Task 5: `references/canvas-object-model.md` — the normalized input schema

**Files:**
- Create: `skills/canvas-manager/references/canvas-object-model.md`

- [ ] **Step 1: Write the reference doc**

```markdown
# Canvas Object Model

`sync.py` never talks to Canvas or an MCP server directly — it only accepts a
JSON list of objects already normalized to this shape:

​```json
{
  "canvas_type": "assignment",
  "canvas_id": 12345,
  "course_id": 67890,
  "title": "Homework 4",
  "updated_at_canvas": "2026-07-09T07:55:00",
  "source_url": "https://school.instructure.com/courses/67890/assignments/12345",
  "content": "Markdown/plain-text body of the object"
}
​```

Required fields: `canvas_type`, `canvas_id`, `course_id`, `title`,
`updated_at_canvas`, `source_url`, `content`. All are strings except
`canvas_id`/`course_id`, which are integers.

`canvas_type` is always singular (`assignment`, `announcement`, `page`,
`module`, `discussion`, `syllabus`). The `--object-type` flag passed to
`sync.py` is the plural form used for the `raw/` subdirectory
(`assignments`, `announcements`, `pages`, `modules`, `discussions`).

## Turning Canvas MCP output into this shape

Whatever Canvas MCP server the user has connected (e.g. a community
`canvas-mcp` server), its tool responses will have their own field names.
Before calling `sync.py`, the agent must map that output into the schema
above and write it to a temp JSON file, one file per object type per course,
per sync run. This mapping step is the only part of the pipeline that
depends on which MCP server the user has installed — everything downstream
(`sync.py`, the raw/manifest/wiki rules) is server-agnostic.

If a Canvas field doesn't map cleanly (e.g. an MCP server that doesn't
expose `updated_at`), fall back to the fetch time and note the gap in that
run's sync log — never invent a value.
```

- [ ] **Step 2: Commit**

```bash
git add skills/canvas-manager/references/canvas-object-model.md
git commit -m "docs: define the normalized Canvas object schema"
```

---

### Task 6: `references/vault-structure.md`

**Files:**
- Create: `skills/canvas-manager/references/vault-structure.md`

- [ ] **Step 1: Write the reference doc**

```markdown
# Vault Structure

​```text
{user-chosen root}/
└── {Semester}/                          # e.g. 2026Spring
    ├── 学期总览.md
    └── {Course}/                        # default "CourseCode - Course Name"
        ├── raw/
        │   ├── _manifest/canvas-objects.json
        │   ├── sync/
        │   ├── assignments/{id}/{timestamp}.md
        │   ├── announcements/{id}/{timestamp}.md
        │   ├── pages/{id}/{timestamp}.md
        │   ├── modules/{id}/{timestamp}.md
        │   └── files/{id}/...
        ├── wiki/
        │   ├── 资料摘要/
        │   ├── 概念/
        │   ├── 主题/
        │   ├── 综合/
        │   └── assets/
        ├── templates/
        └── 课程总览.md
​```

Rules:

- `raw/` is append-only evidence. Nothing already written to `raw/` is ever
  edited or deleted, including by this skill.
- `wiki/` is the learning surface. It can be updated, merged, rewritten, or
  deleted — but only the regions this skill generated (see
  `obsidian-rules.md` for the ownership boundary with user-written content).
- Course directory names default to `CourseCode - Course Name`
  (e.g. `CS101 - Intro to CS`); the user can rename at initialization.
- This skill's own protocol (this file, `sync-rules.md`, etc.) lives only in
  the skill package. Never generate a per-course `AGENTS.md` — that causes
  rule drift between courses and between users.
```

- [ ] **Step 2: Commit**

```bash
git add skills/canvas-manager/references/vault-structure.md
git commit -m "docs: define the semester/course/raw/wiki vault structure"
```

---

### Task 7: `references/sync-rules.md`

**Files:**
- Create: `skills/canvas-manager/references/sync-rules.md`

- [ ] **Step 1: Write the reference doc**

```markdown
# Sync Rules

## When to sync

- Light sync: daily, twice a day (defaults: 06:00 and 18:00).
- Deep sync: weekly (default: Sunday 18:00) — produces the Weekly Digest
  (see below).

This skill does not assume any particular automation is running. At the end
of initialization, tell the user to set these three runs up themselves via
Claude Code's `/schedule` skill, pointed at this skill's sync procedure.

## Sync procedure (per course, per object type)

1. Call the user's Canvas MCP tools to fetch the current objects of one type
   (e.g. all assignments) for the course.
2. Normalize each object into the schema in `canvas-object-model.md`, and
   write the list to a temp JSON file.
3. Run:
   ​```bash
   python3 skills/canvas-manager/scripts/sync.py \
     --course-dir "{Root}/{Semester}/{Course}" \
     --object-type assignments \
     --input /tmp/canvas-assignments.json
   ​```
4. Read the JSON result (`new`, `updated`, `unchanged`, `missing` object
   keys). For every `new` or `updated` key, read its `latest_snapshot` path
   from `raw/_manifest/canvas-objects.json` and update the relevant `wiki/`
   note (see `obsidian-rules.md`).
5. Repeat for each object type (`assignments`, `announcements`, `pages`,
   `modules`, `discussions`).

Never write to `raw/` directly — always go through `sync.py`, which is the
only thing that knows how to avoid duplicating unchanged snapshots and how
to avoid overwriting same-second writes.

## Weekly Digest (deep sync)

After the normal per-object-type sync above, additionally:

- Update `学期总览.md` and each course's `课程总览.md`.
- Summarize the week's new/updated objects (from that week's
  `raw/sync/*.md` logs).
- Draft next week's plan candidates into
  `{Root}/{Semester}/_exports/planvault-tasks.md`, prioritized by **course
  time structure** (due dates, exam dates) — not by which objects were
  recently touched. A teacher uploading a file is not itself a signal of
  urgency.

## Attachments

Default sync reads metadata and text content only. Large file attachments
(PDF/PPT/etc.) are not downloaded automatically — that is a separate,
on-demand action the user can trigger per file.

## Failure handling

- If a Canvas MCP call fails or is rate-limited for an object type, skip
  that type for this run — do not partially write its manifest entries.
  Note the failure in that run's sync log. The next scheduled run retries
  automatically.
- `sync.py` itself only ever updates the manifest entries it successfully
  wrote a snapshot for, so a script-level failure mid-run cannot corrupt
  entries it didn't touch.
```

- [ ] **Step 2: Commit**

```bash
git add skills/canvas-manager/references/sync-rules.md
git commit -m "docs: define the sync/digest/attachment/failure rules"
```

---

### Task 8: `references/obsidian-rules.md` — wiki authoring & ownership boundary

**Files:**
- Create: `skills/canvas-manager/references/obsidian-rules.md`

- [ ] **Step 1: Write the reference doc**

```markdown
# Obsidian / Wiki Authoring Rules

`wiki/` is organized like this inside each course:

​```text
wiki/
├── 资料摘要/   # one summary per raw object (a lecture page, a module, a syllabus)
├── 概念/       # concept cards extracted from course material
├── 主题/       # cross-week, cross-module topic write-ups
├── 综合/       # 作业总览.md, 公告时间线.md, 考试与截止日期.md, 课程复习计划.md
└── assets/
​```

## Ownership boundary (read this before editing any wiki file)

A wiki file can contain both agent-generated content and the student's own
handwritten notes in the same file. This skill must never destroy the
student's own writing.

Rule: every agent-generated section starts with an HTML comment marker and
ends with a matching close marker:

​```markdown
<!-- agent-managed:start id="资料摘要-page-991" -->
... content this skill generated/updated ...
<!-- agent-managed:end -->
```

When updating a wiki file:

1. Read the whole file.
2. Only replace text between a matching `agent-managed:start`/`:end` pair
   with the same `id`.
3. If no marker with that `id` exists yet, append a new marked section —
   never assume the whole file is safe to overwrite.
4. Anything outside marker pairs (the student's own prose) is left
   byte-for-byte untouched.

## What goes in wiki vs. what stays in raw

- `raw/` keeps the Canvas object as received — never summarized, never
  rewritten.
- `wiki/资料摘要/` holds one digested summary per raw object, referencing its
  `source_snapshot` path so it's traceable back to the evidence it was
  written from.
- `wiki/概念/` and `wiki/主题/` are synthesis the agent builds up over time
  across multiple raw objects — these are the parts most likely to also
  contain the student's own notes, so the marker discipline above matters
  most here.
```

- [ ] **Step 2: Commit**

```bash
git add skills/canvas-manager/references/obsidian-rules.md
git commit -m "docs: define wiki authoring rules and the agent/user content boundary"
```

---

### Task 9: Templates

**Files:**
- Create: `skills/canvas-manager/templates/semester-dashboard.md`
- Create: `skills/canvas-manager/templates/course-dashboard.md`
- Create: `skills/canvas-manager/templates/source-summary.md`
- Create: `skills/canvas-manager/templates/concept.md`
- Create: `skills/canvas-manager/templates/topic.md`
- Create: `skills/canvas-manager/templates/synthesis.md`

- [ ] **Step 1: `semester-dashboard.md`**

```markdown
# {{semester}} 学期总览

## 本学期课程
- [ ] {{course_1}}
- [ ] {{course_2}}

## 本周关注
<!-- agent-managed:start id="weekly-focus" -->
(下次 Weekly Digest 时填充)
<!-- agent-managed:end -->
```

- [ ] **Step 2: `course-dashboard.md`**

```markdown
# {{course_name}} 课程总览

- Canvas: {{course_url}}
- 学期: {{semester}}

## 近期 due
<!-- agent-managed:start id="upcoming-due" -->
(下次 sync 时填充)
<!-- agent-managed:end -->

## 资源索引
- [作业总览](../wiki/综合/作业总览.md)
- [公告时间线](../wiki/综合/公告时间线.md)
- [考试与截止日期](../wiki/综合/考试与截止日期.md)
```

- [ ] **Step 3: `source-summary.md`**

```markdown
---
source_type: {{canvas_type}}
source_snapshot: {{raw_snapshot_path}}
---

# {{title}}

<!-- agent-managed:start id="summary" -->
(摘要内容)
<!-- agent-managed:end -->

## 我的笔记
(学生手写区域，agent 不会碰这里)
```

- [ ] **Step 4: `concept.md`**

```markdown
# {{concept_name}}

来源课程: {{course_name}}

<!-- agent-managed:start id="definition" -->
(定义/解释)
<!-- agent-managed:end -->

## 我的理解
(学生手写区域)
```

- [ ] **Step 5: `topic.md`**

```markdown
# {{topic_name}}

跨越: {{module_range}}

<!-- agent-managed:start id="topic-synthesis" -->
(跨周/跨 module 的整理)
<!-- agent-managed:end -->
```

- [ ] **Step 6: `synthesis.md`**

```markdown
# {{synthesis_title}}

<!-- agent-managed:start id="synthesis-body" -->
(综合内容，如作业总览 / 公告时间线 / 考试与截止日期 / 课程复习计划)
<!-- agent-managed:end -->
```

- [ ] **Step 7: Commit**

```bash
git add skills/canvas-manager/templates
git commit -m "feat: add wiki/dashboard templates with agent-managed markers"
```

---

### Task 10: `SKILL.md` — the entry point

**Files:**
- Create: `skills/canvas-manager/SKILL.md`

- [ ] **Step 1: Write `SKILL.md`**

```markdown
---
name: canvas-manager
description: Use when a student wants to sync Canvas LMS course content (assignments, announcements, pages, modules) into an organized Obsidian vault, or asks to initialize/sync/review a semester or course tracked by CanvasManager.
---

# CanvasManager

Turns a Canvas LMS course into a semester → course organized Obsidian vault.
Canvas is the source of truth; Obsidian is the learning surface.
`raw/` holds unedited Canvas evidence; `wiki/` holds what you've digested
from it. See `references/vault-structure.md` for the full layout.

## First-time initialization

Ask the user:

1. Where should the vault root live? (a folder path)
2. What's the current semester name? (e.g. `2026Spring`)
3. Which Canvas courses to track this semester, and does the default
   `CourseCode - Course Name` directory naming work, or do they want to
   rename any course directory?

Then create the directory skeleton from `references/vault-structure.md` and
the templates in `templates/` for each course, plus the semester dashboard.
If two courses would resolve to the same default directory name (e.g. two
courses both named "Intro Seminar"), stop and ask the user to pick distinct
names for the colliding ones — never silently overwrite an existing course
directory.

## Every sync

Follow `references/sync-rules.md` step by step — it covers calling the
user's Canvas MCP, normalizing objects per
`references/canvas-object-model.md`, invoking `scripts/sync.py`, and
updating `wiki/` per `references/obsidian-rules.md`.

At the end of initialization, tell the user to set up three recurring runs
via Claude Code's `/schedule` skill (daily 06:00 light sync, daily 18:00
light sync, Sunday 18:00 deep sync/Weekly Digest) — this skill does not
assume any automation is already running.

## Hand-off to planning tools

This skill does not do calendars, daily planning, or reminders. Each deep
sync writes plan candidates to
`{Root}/{Semester}/_exports/planvault-tasks.md` — task title, course, type
(`assignment`/`quiz`/`exam`/`reading`/`project`), `due_at`,
`estimated_workload`, `source_url`, `source_snapshot`, `priority_hint`.
A planning tool (e.g. PlanVault) is expected to read that file; this skill
never schedules or reminds on its own.
```

- [ ] **Step 2: Commit**

```bash
git add skills/canvas-manager/SKILL.md
git commit -m "feat: add canvas-manager SKILL.md entry point"
```

---

### Task 11: End-to-end smoke test with realistic fixture data

**Files:**
- Create: `tests/fixtures/sample_course_objects.json`
- Test: `tests/test_smoke.py`

- [ ] **Step 1: Write a realistic multi-object-type fixture**

```json
[
  {"canvas_type": "assignment", "canvas_id": 501, "course_id": 42, "title": "Problem Set 3", "updated_at_canvas": "2026-07-01T09:00:00", "source_url": "https://school.instructure.com/courses/42/assignments/501", "content": "Solve problems 1-8, due next Friday."},
  {"canvas_type": "announcement", "canvas_id": 900, "course_id": 42, "title": "Midterm date confirmed", "updated_at_canvas": "2026-07-02T14:00:00", "source_url": "https://school.instructure.com/courses/42/discussion_topics/900", "content": "Midterm is on July 20th, in-class."},
  {"canvas_type": "page", "canvas_id": 77, "course_id": 42, "title": "Week 3 Reading Guide", "updated_at_canvas": "2026-07-01T08:00:00", "source_url": "https://school.instructure.com/courses/42/pages/77", "content": "Read chapters 4-5 before Wednesday's lecture."}
]
```

- [ ] **Step 2: Write the failing smoke test**

```python
# tests/test_smoke.py
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "canvas-manager" / "scripts"))

import sync as sync_mod  # noqa: E402

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "sample_course_objects.json"


class TestSmoke(unittest.TestCase):
    def test_full_course_sync_by_object_type_then_reruns_idempotently(self):
        objects = json.loads(FIXTURE_PATH.read_text())
        by_type = {}
        for obj in objects:
            by_type.setdefault(obj["canvas_type"] + "s", []).append(obj)

        with tempfile.TemporaryDirectory() as tmp:
            course_dir = Path(tmp)
            first_pass = {}
            for object_type, objs in by_type.items():
                first_pass[object_type] = sync_mod.run_sync(course_dir, object_type, objs, datetime(2026, 7, 6, 6, 0, 0))

            for object_type, result in first_pass.items():
                self.assertEqual(result["unchanged"], 0)
                self.assertGreater(len(result["new"]), 0)

            second_pass = {}
            for object_type, objs in by_type.items():
                second_pass[object_type] = sync_mod.run_sync(course_dir, object_type, objs, datetime(2026, 7, 6, 18, 0, 0))

            for object_type, result in second_pass.items():
                self.assertEqual(result["new"], [])
                self.assertEqual(result["updated"], [])
                self.assertGreater(result["unchanged"], 0)

            manifest_path = course_dir / "raw" / "_manifest" / "canvas-objects.json"
            manifest = json.loads(manifest_path.read_text())
            self.assertEqual(len(manifest), len(objects))
            for entry in manifest.values():
                self.assertEqual(entry["status"], "active")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run to verify it fails first, then passes**

Run: `python3 -m unittest discover -s tests -v`
Expected first run (before fixture exists): `FileNotFoundError` for the fixture path — create the fixture file from Step 1 if not already present, then re-run.
Expected after fixture + existing `sync.py` from Task 4: `Ran 16 tests in ...s` / `OK` (15 prior tests + this one).

- [ ] **Step 4: Commit**

```bash
git add tests/fixtures/sample_course_objects.json tests/test_smoke.py
git commit -m "test: add end-to-end multi-object-type smoke test"
```

---

### Task 12: Finalize README and tag v0.1.0

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Expand `README.md` with real usage instructions**

```markdown
# CanvasManager

A Claude Code skill that syncs Canvas LMS courses into a semester → course
organized Obsidian vault (`raw/` = Canvas evidence, `wiki/` = your learning
notes), on a schedule you control.

## Standalone usage

1. Install this repo as a Claude Code plugin (or point Claude Code at
   `skills/canvas-manager/SKILL.md` directly).
2. Connect a Canvas MCP server for your school's Canvas instance.
3. Ask the agent to initialize CanvasManager — it will ask for your vault
   root, current semester, and courses.
4. After initialization, set up the three recurring sync runs via
   Claude Code's `/schedule` skill (see `skills/canvas-manager/SKILL.md`).

## Optional PlanVault integration

PlanVault users who also use Canvas can pull this repo in as a git
submodule (opt-in, not required for PlanVault's core daily-planning
features). CanvasManager writes plan candidates to
`{Root}/{Semester}/_exports/planvault-tasks.md` for PlanVault to consume —
it does not do calendars, reminders, or daily planning itself.

## Development

​```bash
python3 -m unittest discover -s tests -v
​```

No external dependencies — Python 3 standard library only.
```

- [ ] **Step 2: Run the full test suite one last time**

Run: `python3 -m unittest discover -s tests -v`
Expected: `Ran 16 tests in ...s` / `OK`

- [ ] **Step 3: Commit and tag**

```bash
git add README.md
git commit -m "docs: finalize README with usage instructions (v0.1.0)"
git tag v0.1.0
```
