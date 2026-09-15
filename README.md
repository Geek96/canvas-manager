<p align="center">
  <img src="https://img.shields.io/badge/AI_Agent-Skill-7C3AED?style=for-the-badge" alt="AI Agent Skill"/>
  <img src="https://img.shields.io/badge/version-0.2.1-10B981?style=for-the-badge" alt="Version 0.2.1"/>
  <img src="https://img.shields.io/github/license/Geek96/canvas-manager?style=for-the-badge&color=6B7280" alt="MIT License"/>
</p>

<h1 align="center">🎓 canvas-manager</h1>

<p align="center">
  <strong>A Claude Code skill that syncs Canvas LMS courses into a semester → course organized Obsidian vault</strong>
  <br/>
  <code>Canvas → raw evidence → digested wiki notes → PlanVault hand-off</code>
  <br/><br/>
  Defaults to <strong>CanvasManager Lite</strong> — no Canvas API token required
</p>

<p align="center">
  <strong>English</strong>
</p>

---

## ✨ Features

- **Two ways to read Canvas** — `canvas-manager-lite` drives your own logged-in
  browser via `opencli` (default, no API token needed); `canvas-manager`
  talks to a Canvas MCP server if your institution allows student API tokens
- **Evidence-first vault** — `raw/` keeps unedited Canvas snapshots per
  object; `wiki/` holds the digested notes built from them, never the other
  way around
- **Idempotent, content-hashed sync** — re-running a sync with nothing
  changed on Canvas is a no-op; a Python engine (stdlib only, unit-tested)
  owns diffing/manifest state so that part isn't left to agent judgment
- **Never silently overwrites** — a file that might be a new version of one
  you already have is flagged `needs_confirmation`, not auto-replaced
- **Agent-managed-region marker discipline** — the skill only ever touches
  the sections of a wiki file it generated; your own handwritten notes in
  the same file are never touched
- **Obsidian-native output** — YAML frontmatter, `> [!callouts]`,
  `[[wiki-links]]` — no Obsidian plugin required, the skill writes plain
  files directly to your vault folder
- **Structured PlanVault hand-off** — optional plan-candidate export for a
  separate daily-planning tool to consume; this skill itself never
  schedules or reminds

---

## 📦 Installation

This is a Claude Code plugin/skill. Clone it or install it, then point
Claude Code at whichever variant matches your Canvas access (see
[Dependencies](#-dependencies--prerequisites) below for what each variant
needs before it'll actually work).

```bash
npx skills add Geek96/canvas-manager
```

or clone directly:

```bash
git clone https://github.com/Geek96/canvas-manager.git
```

Both skills are auto-registered via `.claude-plugin/plugin.json` once
installed. The plugin ships both variants — you only need to set up the
dependencies for the one you're actually going to use.

---

## 🔧 Dependencies & Prerequisites

> **Required by both variants** — Python 3 (standard library only, nothing
> to `pip install`) and an Obsidian vault folder (the app itself is
> optional — the skill writes plain Markdown files directly to disk, no
> Obsidian plugin or API needed to consume them).

### CanvasManager Lite (default — use this if your school blocks student API tokens)

```
☐ opencli            ← browser bridge, reuses your logged-in Canvas session
☐ Logged into Canvas  ← in the same browser profile opencli is bridged to
```

**1. Install `opencli`**

> Provides: drives a real, already-logged-in browser tab so the skill can
> read Canvas pages the same way you would, without any API access.

```bash
npm install -g @jackwener/opencli
```

See [github.com/jackwener/OpenCLI](https://github.com/jackwener/OpenCLI)
for the full install guide (the browser extension it needs, supported
browsers, etc.) if the npm package alone isn't enough on your platform.

**2. Verify the bridge is connected**

```bash
opencli doctor
```

Should report the daemon running and the browser extension connected. If
not, (re)install/reconnect the extension per the `opencli` docs above
before asking the agent to sync anything.

**3. Confirm you're logged into Canvas**

Open your institution's Canvas dashboard
(`https://{your-school}.instructure.com/`) in the same browser profile and
confirm it shows real personalized content (a to-do list, grades link) —
not a login page. `opencli` reuses this session; it does not log in for
you.

No Canvas API token, no MCP server, no Obsidian plugin — this is the
minimum-dependency path and the one to use by default.

### Full CanvasManager (only if your school allows self-service API tokens)

```
☐ Canvas API token   ← generated from your institution's Canvas account settings
☐ Canvas MCP server   ← connected to Claude Code, configured with that token
```

**1. Get a Canvas API token** — Canvas → Account → Settings → **New Access
Token**. Many institutions (Georgia Tech included) disable this for
students; if yours does, use CanvasManager Lite above instead.

**2. Connect a Canvas MCP server** — any MCP server that exposes Canvas's
course/assignment/announcement/module/page endpoints to Claude Code, e.g.
[vishalsachdev/canvas-mcp](https://github.com/vishalsachdev/canvas-mcp).
Configure it with your token per that server's own setup instructions.

The trade-off for the extra setup: full timestamped history per object
under `raw/`, instead of Lite's latest-version-only storage.

---

## 🧩 Skills Overview

```
┌───────────────────────────────────────────────────────────────┐
│                       canvas-manager (plugin)                  │
│                                                                 │
│   canvas-manager-lite (default)      canvas-manager (full)     │
│   opencli browser bridge             Canvas MCP server         │
│   no API token needed                needs a student API token │
│           │                                   │                │
│           └───────────────┬───────────────────┘                │
│                            ▼                                   │
│                 shared vault structure                         │
│         raw/ (evidence) → wiki/ (digested notes)               │
│                            │                                   │
│                            ▼                                   │
│         optional: {Semester}/_exports/planvault-tasks.md       │
│                     → PlanVault (separate skill)                │
└───────────────────────────────────────────────────────────────┘
```

| Skill | What it does | Needs |
|-------|-------------|-------|
| **`canvas-manager-lite`** | Sync via browser bridge — start here | `opencli`, a logged-in browser |
| `canvas-manager` | Sync via Canvas API/MCP — full history | Canvas API token, a Canvas MCP server |

---

## 📖 Example Workflows

### First-time setup

```
> Set up CanvasManager for my Fall 2026 semester
```

The agent will ask for your vault root, semester name, and which courses
to track (default `CourseCode - Course Name` directory naming, editable).

### Ongoing sync

```
> Sync my Canvas courses
```

Reads each tracked course's assignments/announcements/pages/modules,
diffs against what's already in `raw/`, and updates `wiki/` notes only for
what actually changed.

### Recurring sync (optional)

After first-time setup, ask the agent to set up light (twice-daily) and
deep (weekly) sync runs via Claude Code's `/schedule` skill — CanvasManager
doesn't schedule itself.

---

## 📁 Project Structure

```text
canvas-manager/
├── skills/
│   ├── canvas-manager-lite/          # default: opencli browser bridge
│   │   ├── SKILL.md
│   │   ├── references/
│   │   └── scripts/sync_lite.py, files.py
│   └── canvas-manager/                # full: Canvas API/MCP
│       ├── SKILL.md
│       ├── references/                # vault structure, object model,
│       │                              # wiki authoring rules (shared by both)
│       ├── templates/                 # shared wiki templates
│       └── scripts/sync.py, manifest.py, snapshot.py
├── tests/                             # 29 unit tests, stdlib unittest
├── .claude-plugin/plugin.json
└── README.md
```

---

## Optional PlanVault integration

PlanVault users who also use Canvas can pull this repo in as a git
submodule (opt-in, not required for PlanVault's core daily-planning
features). CanvasManager writes plan candidates to
`{Root}/{Semester}/_exports/planvault-tasks.md` for PlanVault to consume —
it does not do calendars, reminders, or daily planning itself.

## Optional textbook-cracking integration

If a course has a real textbook/reader placed in its `textbooks/` folder,
[`textbook-cracking`](https://github.com/Geek96/textbook-cracking) (a
separate skill, install it the same way as this one) builds out
`wiki/textbook_breakdown/` — chapter summaries, concept pages, and
content-model-specific detail pages (proofs for math, worked case studies
for CS, document entries for a primary-source reader) — with real fidelity
rules instead of ad hoc summarization. It already knows to nest its output
under this repo's `wiki/textbook_breakdown/` folder when it detects a
CanvasManager-managed course, so the two compose without collisions. Not
required — CanvasManager works fine without it, just with a lighter-touch
textbook treatment.

---

## Development

```bash
python3 -m unittest discover -s tests -v
```

No external dependencies — Python 3 standard library only.

---

## 📄 License

MIT © [Geek96](https://github.com/Geek96)
