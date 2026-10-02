#!/bin/sh
# Clean build: pristine code + data, no retail picture, every picture generated.
#   sh games/pokered/build_clean.sh [fresh]     -> D:/n64work/pokered/clean/pokered.gbc, pokeblue.gbc
set -e
W=${POKERED_WORK:-/d/n64work/pokered}
R="$(cd "$(dirname "$0")/../.." && pwd)"
export PATH="$HOME/bin:$W/rgbds:$PATH" OPENBLAS_NUM_THREADS=1
if [ "$1" = fresh ] || [ ! -d "$W/clean" ]; then
  rm -rf "$W/clean"
  cp -r "$W/pristine" "$W/clean"
  rm -rf "$W/clean/.git"
  find "$W/clean/gfx" -name '*.png' -delete      # no retail picture stays in the clean tree
fi
cd "$W/clean"
find gfx \( -name '*.2bpp' -o -name '*.1bpp' -o -name '*.pic' \) -delete
rm -f gfx/*.o pokered.gbc pokeblue.gbc
(cd "$R" && python -m games.pokered.generate "$W/clean")
make -j2 red blue > "$W/clean_build.log" 2>&1 || { grep -i -m8 "error\|overflow\|too big" "$W/clean_build.log"; tail -3 "$W/clean_build.log"; exit 1; }
sha1sum pokered.gbc pokeblue.gbc | cut -c1-12,41-
ls -l pokered.gbc | awk '{print "size", $5}'
