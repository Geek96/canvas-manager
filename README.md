# CanvasManager

A Claude Code skill that syncs Canvas LMS courses into a semester → course
organized Obsidian vault (`raw/` = Canvas evidence, `wiki/` = your learning
notes), on a schedule you control.

## Standalone usage (recommended: CanvasManager Lite)

Most institutions don't give students self-service Canvas API tokens, so
**CanvasManager Lite is the default, recommended way to use this repo** —
no Canvas MCP server or API token required.

1. Install this repo as a Claude Code plugin (or point Claude Code at
   `skills/canvas-manager-lite/SKILL.md` directly).
2. Install [`opencli`](https://github.com/jackwener/opencli) and confirm its
   browser bridge is connected (`opencli doctor`), logged into Canvas in the
   same browser profile.
3. Ask the agent to initialize CanvasManager — it will ask for your vault
   root, current semester, and courses.
4. After initialization, set up the three recurring sync runs via
   Claude Code's `/schedule` skill.

Lite reads Canvas the same way you would in a browser, reusing your
logged-in session, instead of the API/MCP. The trade-off: text content
(assignments/pages/announcements/modules) only keeps its latest version,
not a full history, and replacing an existing file with a same-named new
version always requires your explicit confirmation first. See
`skills/canvas-manager-lite/references/opencli-sync-rules.md` for details.

### Have a Canvas API token? Use full CanvasManager instead

If your institution does allow self-service API tokens and you have a
Canvas MCP server connected, `skills/canvas-manager/SKILL.md` covers the
same vault via the API instead of the browser bridge — the main practical
difference is a full timestamped history per object under `raw/`, instead
of Lite's latest-version-only storage. Same first-time-initialization flow,
just point Claude Code at `skills/canvas-manager/SKILL.md` in step 1 above
and connect a Canvas MCP server in step 2 instead of `opencli`.

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
