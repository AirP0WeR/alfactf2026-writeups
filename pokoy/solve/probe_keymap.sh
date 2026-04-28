#!/bin/bash
SOLVE=/Users/cyanogen/Documents/ctf/alfa-ctf-2026/tasks-2026/pokoy/solve
cd "$SOLVE"
for k in 1 2 3 a 4 5 6 b 7 8 9 c '*' 0 '#' d; do
  echo -n "key '$k': "
  for n in 1 2 3 4 5 6 7 8; do
    seq=$(printf "%${n}s" "" | tr ' ' "$k")
    docker run --rm -v "$SOLVE:/work" -w /work \
      -e POKOY_KEYS="$seq" \
      -e POKOY_OUT_FB=/work/fb.bin \
      -e POKOY_OUT_DUMP=/work/dump.txt \
      -e POKOY_OUT_STATE=/work/state.txt \
      peace-app python3 drive.py >/dev/null 2>&1
    b=$(tail -1 "$SOLVE/state.txt" | awk '{print $2}')
    echo -n "$n=$b "
  done
  echo
done
