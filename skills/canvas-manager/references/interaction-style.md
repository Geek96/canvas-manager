# Interaction Style: Ask Closed Questions, Not Open Ones

Shared by both variants. Whenever a step in this skill needs the student to
choose among a small, known set of options, present it as an explicit
numbered/lettered choice the student can answer in one word — never as a
vague open-ended question that makes them guess what a valid answer looks
like. If the runtime provides a structured multiple-choice question tool,
use it; otherwise render the same options as a plain numbered list in chat.

"Vault root path" and "semester name" are genuinely open (there's no fixed
set of valid answers), so those stay free-text — but suggest a sensible
default when one exists (e.g. infer the semester name from today's date)
and let the student just confirm it rather than typing it from scratch.

## The known decision points

**1. Which variant to use (token or no token?)** — before initialization
starts, this is effectively a binary choice: *"Does your institution give
you a Canvas API token? [1] Yes, I have one / I can get one → use full
`canvas-manager` [2] No / not sure → use `canvas-manager-lite` (default)"*.
Most students should get routed to Lite without needing to ask this
explicitly at all — see each `SKILL.md`'s own initialization section for
when a check is still worth asking outright (e.g. the student explicitly
asked for version history, which only the full variant provides).

**2. Which courses to track** — never ask this cold. Fetch the student's
actual current-term course list first (via the Canvas MCP's course-listing
tool, or `opencli browser <session> open .../courses` + `extract` for
Lite), then present it as a numbered pick-list: *"Found these Fall 2026
courses on Canvas: [1] CS-1331 ... [2] MATH-3406 ... [3] HIST-2112 ... —
which should I track? (all / comma-separated numbers)"*. This also
surfaces courses the student didn't think to mention, and unpublished
courses that should be excluded or handled as a placeholder (see
`vault-structure.md`).

**3. Sync pacing on a large first-time sync** — when it's not obvious
ahead of time how much content a course (or a batch of newly-added
courses) will turn out to have, ask: *"Process all N courses in one pass
and report at the end, or one course at a time with a pause to look before
continuing? [1] All at once [2] One at a time"* — don't just pick one
silently, effort here can vary by an order of magnitude per course.

**4. Recurring sync setup** — after first-time initialization, a plain
*"Set up recurring sync now via `/schedule`? [1] Yes [2] Later"* rather
than assuming either answer.

**5. File replacement confirmation (Lite only)** — already effectively
binary per `opencli-sync-rules.md`'s `needs_confirmation` flow: name the
specific file, ask *"replace it? [1] Yes [2] No, keep the version I have"*,
never proceed on an assumption either way.

**What this is not**: don't turn genuinely free-text input (a vault path,
a semester label, a custom course directory name) into a forced multiple
choice — that just adds friction. The point is closed questions where the
valid answer set is actually small and known, not closed questions
everywhere.
