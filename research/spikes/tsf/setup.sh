#!/bin/sh
# Build the WP-7 fixture graph in the current directory (must be a git repo —
# see README "Run" step 1). TRUDAG env var overrides the binary.
set -e
TRUDAG="${TRUDAG:-trudag}"

"$TRUDAG" init
for f in EXP-SCHED ASSERT-LOCK ASSERT-COOP PREM-IMPL PREM-TEST; do
    "$TRUDAG" add-item "$f.md"
done
"$TRUDAG" create-link EXP-SCHED ASSERT-LOCK
"$TRUDAG" create-link ASSERT-LOCK ASSERT-COOP
"$TRUDAG" create-link ASSERT-LOCK PREM-IMPL
"$TRUDAG" create-link ASSERT-LOCK PREM-TEST
"$TRUDAG" create-link ASSERT-COOP PREM-IMPL

echo "--- .dotstop.dot ---"
cat .dotstop.dot
