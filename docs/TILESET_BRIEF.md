# Redrawing a tileset (clean room brief)

Goal: every tile of a Pokemon Red/Blue tileset is **redrawn by us** so the clean build shows
recognisable rooms and landscapes without one retail pixel.

## Rules (non-negotiable)

- The retail pictures live only in the dirty tree `D:/n64work/pokered/dirty`. You may **look** at them
  (zoomed sheets) to learn **what each tile is** ("left half of a bookshelf top", "floor", "stair
  step", "top-left of a 2x2 potted plant").
- You then **draw your own** version of that thing with the tile kit, at your own pixel design.
  Never transcribe, trace or copy pixels or dither patterns from the retail tile; never read retail
  pixel values in code. Same subject, same footprint and edges that connect — different drawing.
  A near copy fails the taint scan and the purpose.
- Flat single-shade tiles and plain lines are fine (they carry no content).
- Only write the files you were given (`games/pokered/art/ts_<name>.py`). Do not edit shared modules,
  do not run `make`, do not use git, do not start servers or browsers. Sheets go to
  `D:/n64work/pokered/sheets/` (never into the repo).
- This PC is short of RAM: run one python command at a time; set nothing in the background.

## What a tileset is

- `gfx/tilesets/<name>.png`: 16 tiles per row, tile number = row*16+col (hex). Shades 0 white, 1 light,
  2 dark, 3 black.
- `gfx/blocksets/<name>.bst`: blocks of 4x4 tiles; maps are grids of blocks. The block table tells you
  which tiles sit next to each other: this is how you find out that four tiles are one table, or
  that a tile repeats as floor. Objects must connect across tile borders the way the blocks use them.
- Facts you may use from the code (pristine tree `D:/n64work/pokered/pristine`):
  `data/tilesets/collision_tile_ids.asm` (walkable tiles), `door_tile_ids.asm`, `warp_tile_ids.asm`,
  `bookshelf_tile_ids.asm`, `tileset_headers.asm` (counter tiles, grass tile), `ledge_tiles.asm`.
- Water tile `$14` is animated by the game (its pixels are rotated sideways): keep it a seamless
  water texture. Flower tile `$03` is replaced by three frames.

## Tools (run from `D:/n64work/pokered-cleanroom`)

```
S=D:/n64work/pokered/sheets
# learn: big numbered tileset, blocks, block table, a whole map (dirty tree)
python -m games.pokered.tsview D:/n64work/pokered/dirty <name> $S/d_<name>_tiles.png --tiles
python -m games.pokered.tsview D:/n64work/pokered/dirty <name> $S/d_<name>_blocks.png --blocks 0:60 --scale 4
python -m games.pokered.tsview D:/n64work/pokered/dirty <name> x --dump
python -m games.pokered.tsview D:/n64work/pokered/dirty <name> $S/d_map.png --map maps/<Map>.blk --width <blocks>
# draw: write games/pokered/art/ts_<name>.py, then
python -m games.pokered.generate D:/n64work/pokered/clean "tilesets/<name>.png"
# check ours: same viewer on the clean tree (add --plain for no grid)
python -m games.pokered.tsview D:/n64work/pokered/clean <name> $S/c_<name>_blocks.png --blocks 0:60 --scale 3 --plain
python -m games.pokered.tsview D:/n64work/pokered/clean <name> $S/c_map.png --map maps/<Map>.blk --width <blocks>
```

Map widths: `constants/map_constants.asm` (`map_const NAME, width, height` in blocks); which maps use
a tileset: `grep -l "<TILESET>" data/maps/headers/*.asm`. Open images with the Read tool; keep it to
a few images per tileset (numbered tiles, blocks in two or three pages, one or two maps, then ours).

## How to write the module

Copy the pattern of `games/pokered/art/ts_overworld.py` (read it first) and the kit
`games/pokered/art/tilekit.py`:

- `T = {}`; `T[0x12] = T8("""8 rows of text art""")` (`.` white, `-` light, `+` dark, `#` black), or
  `tex(lambda x, y: shade)` for textures, or draw an object on a canvas `C(w, h)` with `rect`, `frame`,
  `hline`, `vline`, `line`, `ellipse`, `poly`, `blob` (outlined solid lit from the top left), `put`
  (text art), `text` (our font), then `put(T, canvas, [[0x40, 0x41], [0x50, 0x51]])` to cut it into
  tiles in the layout the blocks use.
- End with
  ```python
  @drawer("tilesets/<name>.png")
  def <name>(rel, a):
      return build_sheet(build(), a, WALK, "<name>")
  ```
  `WALK` = the walkable tile numbers from `collision_tile_ids.asm`. `build_sheet` prints the tiles
  you have not drawn yet (they get a fallback pattern); tiles that are blank in the original are
  blanked for you. Done = nothing listed as "not drawn yet".
- You may import drawings from `ts_overworld.py` (LAWN, WATER, tree(), ...) or another finished
  module for things that are the same subject, so the game looks consistent.
- Style: black outlines, light from the top left, floors light and quiet (the player and text must
  stand out), walls and furniture darker, clear shapes over texture. Walkable tiles must look
  walkable, solid ones solid. Doors, stairs, mats, counters, PCs, signs must read at a glance.
- Text on tiles (signs, posters) is re-typeset with our font (`c.text`, or 3x5 capitals as in
  `ts_overworld.S3`).

## Report

Five lines: tiles drawn / total per tileset, anything you could not identify, anything in a shared
module you needed and did not have.
