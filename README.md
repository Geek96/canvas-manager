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

### No Canvas API token? Use CanvasManager Lite

Some institutions disable self-service Canvas API token creation for
students. `skills/canvas-manager-lite/SKILL.md` covers the same vault, but
reads Canvas through `opencli`'s browser bridge (your own logged-in
session) instead of the API/MCP. The trade-off: text content
(assignments/pages/announcements/modules) only keeps its latest version,
not a full history, and replacing an existing file with a same-named new
version always requires your explicit confirmation first. See
`skills/canvas-manager-lite/references/opencli-sync-rules.md` for details.

## Optional PlanVault integration

PlanVault users who also use Canvas can pull this repo in as a git
submodule (opt-in, not required for PlanVault's core daily-planning
features). CanvasManager writes plan candidates to
`{Root}/{Semester}/_exports/planvault-tasks.md` for PlanVault to consume —
it does not do calendars, reminders, or daily planning itself.

## Development

```bash
python3 -m unittest discover -s tests -v
```

No external dependencies — Python 3 standard library only.
