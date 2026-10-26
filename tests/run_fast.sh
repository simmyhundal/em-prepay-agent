#!/bin/sh
# The checks to run before every merge (under a minute, no model calls, no paid run).
# Usage: sh tests/run_fast.sh
cd "$(dirname "$0")/.." || exit 1
fail=0
for t in tests/test_*.py; do
  if python3 "$t" >/dev/null 2>&1; then echo "ok   $t"; else echo "FAIL $t"; fail=1; fi
done
exit $fail
