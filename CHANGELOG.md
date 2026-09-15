# Changelog

## 0.3.0

**Breaking**: this skill no longer generates deadline-aware synthesis —
`作业总览.md`, `公告时间线.md`, `考试与截止日期.md`, `课程复习计划.md`, or the
`{Semester}/_exports/planvault-tasks.md` PlanVault hand-off file. That's now
the separate [`course-manager`](https://github.com/Geek96/course-manager)
skill's job, built from this skill's evidence but not written by this skill.
This skill is now scoped to exactly what it's always documented as: raw
Canvas evidence in `raw/`, plus one digested summary per object in
`wiki/course_content/`/`wiki/info/`.

If you were relying on those notes, install `course-manager` alongside
this skill — it reads `raw/`, `wiki/course_content/`, and `wiki/info/`
read-only and rebuilds the same views in `wiki/综合/`.

Also:
- CanvasManager Lite is now the default, recommended path in `README.md`
  and `.claude-plugin/plugin.json`'s skill ordering — most institutions
  don't give students self-service API tokens, and Lite is the variant
  actually validated against a real semester's worth of courses. Full
  `canvas-manager` is framed as the alternative for schools that do allow
  tokens.
- Fixed first-time-setup gaps found by walking through onboarding as a
  cold-start student: `canvas-manager`'s trigger description had no
  precondition on actually having a token/MCP server (so it could
  out-compete Lite for exactly the students who should default to it);
  the `opencli` install command only existed in the README, not in the
  Lite skill's own files; the initialization flow never asked for the
  Canvas institution domain every URL depends on.
- Added `references/interaction-style.md`: which first-run decisions
  should be closed/multiple-choice questions built from live data (which
  courses — fetch the list first, then let the student pick) versus
  genuinely open free-text ones.
- Recommends the separate
  [`textbook-cracking`](https://github.com/Geek96/textbook-cracking) skill
  for building out `wiki/textbook_breakdown/`, instead of doing it ad hoc.

## 0.2.1

Wired in the shared `obsidian-core.md` authoring contract; bumped for the
v0.2.0 template/docs redesign (Obsidian callouts, tags, wiki-links).

## 0.2.0

Added `canvas-manager-lite`: reads Canvas through `opencli`'s browser
bridge instead of the API/MCP, for institutions (Georgia Tech included)
that disable self-service student API tokens.

## 0.1.0

Initial release: `canvas-manager` (full, API/MCP-based) — semester → course
organized Obsidian vault, idempotent content-hashed sync engine, wiki
authoring with agent-managed-region marker discipline.
