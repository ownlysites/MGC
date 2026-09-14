#!/bin/sh
# Run every harness. Exit non-zero if any of them fails.
#
#   sh dev/all.sh
#
# Fixtures first, if they are not there yet:
#   cd dev && npm install && node extract.cjs
cd "$(dirname "$0")/.." || exit 1

fail=0
for h in dev/compliance.js dev/consistent.js dev/parsers.js dev/mailable.js; do
  printf '%-24s' "$(basename "$h")"
  out=$(node "$h" 2>&1)
  code=$?
  pass=$(printf '%s' "$out" | grep -c 'PASS')
  bad=$(printf '%s' "$out" | grep -c '  FAIL')
  if [ "$code" -eq 2 ]; then
    echo "SKIPPED — no fixtures (cd dev && node extract.cjs)"
  elif [ "$code" -ne 0 ]; then
    echo "FAILED   $pass pass / $bad fail"
    printf '%s\n' "$out" | grep '  FAIL' | head -8 | sed 's/^/    /'
    fail=1
  else
    echo "ok       $pass checks"
  fi
done

# Syntax-check the shipped file itself. A harness that cannot even parse
# index.html reports zero failures, which looks like success.
printf '%-24s' "index.html syntax"
node -e '
const fs=require("fs");const src=fs.readFileSync("index.html","utf8");
const re=/<script(?![^>]*\ssrc=)[^>]*>([\s\S]*?)<\/script>/gi;let m,i=0,bad=0;
while((m=re.exec(src))!==null){i++;try{new Function(m[1]);}catch(e){console.log("\nSYNTAX ERROR block "+i+": "+e.message);bad++;}}
if(bad)process.exit(1); else console.log("ok       "+i+" script blocks");
' || fail=1

[ "$fail" -eq 0 ] && echo "\nALL HARNESSES PASS" || echo "\nSOMETHING FAILED"
exit $fail
