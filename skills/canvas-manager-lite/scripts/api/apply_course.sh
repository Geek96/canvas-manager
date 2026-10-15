#!/bin/bash
# Write the prepared objects into the raw store with sync_lite.py
# (latest-only, content-hash skip). Run after reviewing prepare_course.sh.
#
# usage: apply_course.sh <data-dir> <outdir-for-course>
set -euo pipefail
L="$(cd "$(dirname "$0")/.."; pwd)/sync_lite.py"
for f in "$2"/*.json; do
  t=$(basename "$f" .json); echo "-- $t"
  python3 "$L" --data-dir "$1" --object-type "$t" --input "$f" \
    | python3 -c "import json,sys;print({k:v for k,v in json.load(sys.stdin).items() if v})"
done
