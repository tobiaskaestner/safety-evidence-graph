#!/usr/bin/env bash
# Resolve how to invoke OFT: prefer `oft` on PATH, else a jar in this dir / cwd.
if command -v oft >/dev/null 2>&1; then OFT="oft";
elif ls openfasttrace-*.jar >/dev/null 2>&1; then OFT="java -jar $(ls openfasttrace-*.jar | head -1)";
else echo "OFT not found: put openfasttrace-*.jar here or install the 'oft' launcher"; exit 2; fi
echo "# using: $OFT"
echo "## trace (exit code is the verdict: 0 = all covered)"
$OFT trace -o plain -v failure_details doc/ src/
echo "exit=$?"
