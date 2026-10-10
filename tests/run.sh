#!/usr/bin/env bash
# The suite split by test class and run in parallel.
#
# Every test starts a fresh interpreter, often several, and run one after
# another 153 tests took 127-157 s on four cores. The classes share nothing:
# each test builds its own mkdtemp, HOME and registry. So they run side by side
# here: about 54 s on the same machine.
#
# `python3 tests/test_kb.py` stays the serial fallback, and the one to use when
# a failure needs a single readable log.
#
#   tests/run.sh               # all classes, $(nproc) at a time
#   KB_TEST_JOBS=2 tests/run.sh
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

jobs=${KB_TEST_JOBS:-$(nproc 2>/dev/null || echo 4)}
logs=$(mktemp -d)

# `Base` is the fixture every class inherits from and holds no tests.
mapfile -t classes < <(grep -oE '^class [A-Za-z0-9_]+\((Base|unittest\.TestCase)\)' tests/test_kb.py \
	| sed -E 's/^class ([A-Za-z0-9_]+).*/\1/' | grep -vx Base)

printf '%s\n' "${classes[@]}" | xargs -P "$jobs" -I{} sh -c \
	'python3 -m unittest tests.test_kb.{} >"$0/{}.log" 2>&1; echo $? >"$0/{}.rc"' "$logs"

ran=0 failed=()
for c in "${classes[@]}"; do
	n=$(grep -oE '^Ran [0-9]+' "$logs/$c.log" | awk '{print $2}')
	ran=$((ran + ${n:-0}))
	[ "$(cat "$logs/$c.rc" 2>/dev/null)" = "0" ] || failed+=("$c")
done

# A class the pattern above missed would pass silently by not running at all.
# Counting the test methods is what makes a missed class a failure.
want=$(grep -cE '^    def test_' tests/test_kb.py)

for c in "${failed[@]}"; do
	echo "── $c ──────────────────────────────"
	cat "$logs/$c.log"
done
echo "Ran $ran of $want tests in ${#classes[@]} classes, $jobs at a time; logs in $logs"
if [ "${#failed[@]}" -gt 0 ]; then
	echo "FAILED: ${failed[*]}"
	exit 1
fi
if [ "$ran" -ne "$want" ]; then
	echo "FAILED: $((want - ran)) test(s) never ran — a class is missing from the split"
	exit 1
fi
echo "OK"
