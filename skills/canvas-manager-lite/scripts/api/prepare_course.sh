#!/bin/bash
# Fetch one course through the student's logged-in browser (opencli) via the
# Canvas REST API, build sync_lite.py inputs, and print a dry-run diff.
# Nothing in the raw store changes until apply_course.sh is run.
#
# usage: prepare_course.sh <session> <course_id> <data-dir> <workdir>
#   env CANVAS_BASE=https://{institution}.instructure.com (required)
set -euo pipefail
HERE=$(cd "$(dirname "$0")"; pwd)
S=$1; C=$2; D=$3; W=$4
: "${CANVAS_BASE:?set CANVAS_BASE, e.g. https://gatech.instructure.com}"
mkdir -p "$W/dump" "$W/out"
opencli browser "$S" open "$CANVAS_BASE/courses/$C" >/dev/null 2>&1
opencli browser "$S" eval "$(sed "s/__COURSE__/$C/" "$HERE/fetch_course.js")" 2>/dev/null \
  | grep -v 'Update available\|npm install' | grep -v '^\s*$' > "$W/dump/$C.json"
rm -rf "$W/out/$C"
python3 "$HERE/build_course.py" "$W/dump/$C.json" "$D" "$W/out/$C" --base="$CANVAS_BASE"
python3 "$HERE/dry_run.py" "$D" "$W/out/$C"
