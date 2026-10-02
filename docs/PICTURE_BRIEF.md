# Drawing a creature or trainer picture from a brief (clean room)

Goal: every Pokemon (front and back) and every trainer is **our own drawing**, recognisable at a
glance as that creature at 4 shades, never a blurred or traced copy of the retail picture.

## How a picture is made

The only facts kept from the retail picture are its size, a deliberately coarse silhouette (gaps
closed, thin lines dropped) and a 4x4 grid of mean shade. Everything inside comes from a **brief**
that you write: a short list of drawing operations (see the header of
`games/pokered/art/pics.py` for the exact format: `base`, `bevel`, `poly`, `ell`, `line`, `dots`,
`eye`, `stripes`, `dither`, `shade`, `art`, `cut`, `add`). Coordinates are picture pixels, x right,
y down. Shades: 0 white, 1 light, 2 dark, 3 black. On the Super Game Boy / Game Boy Color each
creature gets a palette where 1 is its main body colour and 2 its darker colour, so: body mostly
1, shadows and darker parts 2, white only for eyes, teeth, bellies and highlights, black for lines.

## Rules (non-negotiable)

- You may **look** at the retail picture (left side of the viewer, with a pixel ruler) to learn the
  pose and where things are: "eye near (12, 14)", "the wing covers the top right", "belly patch
  lower left", "three claws on each foot". You also know these creatures: draw what the creature
  **is** (its face, its markings, its limbs), in your own simplified style.
- Do **not** reproduce the retail pixels: no copying its dither, its exact line work or its shading
  pixel by pixel. Bold shapes, clear face, clean flat shading with a few lines. An `art` stamp is
  for a face or small detail of your own design (at most about 12x12), not for transcribing.
- The taint scan compares the inside of every picture with retail and fails at 90% equal pixels;
  typical good briefs land around 40-65%.
- Write only your own brief file. Do not edit modules, do not run make or git, no background jobs,
  one python command at a time (the PC is short of RAM). Sheets go to `D:/n64work/pokered/sheets/`.

## Workflow (from `D:/n64work/pokered-cleanroom`, Git Bash, `export OPENBLAS_NUM_THREADS=1`)

```
# look: retail with ruler on the left, ours (from the current briefs) on the right
python -m games.pokered.briefview D:/n64work/pokered/sheets/<you>_a.png pokemon/front/abra.png pokemon/front/aerodactyl.png ... --scale 6 --cols 2
```

Open the sheet with the Read tool. Work in batches of 4 to 6 pictures per sheet: look, write or fix
their briefs, render again, compare, fix once or twice, move on. Use `--scale 8` for a single hard one,
`--clean-only` when you only need ours.

Brief file: `games/pokered/briefs/<your file>.json`, one JSON object:

```json
{
 "pokemon/front/abra.png": {"base": 1, "bevel": 0.6, "ops": [
   {"cut": [[20, 30], [26, 30], [23, 38]]},
   {"poly": [[10, 20], [22, 20], [20, 34], [12, 34]], "s": 2},
   {"eye": [14, 12], "r": [2.5, 1.5], "kind": "slit"},
   {"line": [[12, 17], [16, 18], [20, 17]], "s": 3},
   {"art": ["#..#", ".##."], "at": [12, 15]}
 ]},
 "pokemon/back/abrab.png": {"base": 1, "ops": []}
}
```

Keep the file valid JSON at all times (a broken file drops all your briefs from the render).

## What makes it recognisable (in this order)

1. **Shape**: the kept silhouette is a coarse blob. Use `cut` to open the gaps that define the
   creature (between legs, under wings, between ears, around a tail) and `add` for thin parts that
   were dropped (tails, antennae, whiskers, horns, stems, flames, leeks, spoons).
2. **Face**: eyes in the right place and style (round with pupil, dot, angry brow, closed arc),
   mouth, beak, nostrils. One good face does more than any shading.
3. **Signature parts**: Bulbasaur's bulb, Charmander's tail flame, Squirtle's shell plates,
   Pikachu's cheek spots, ear tips and tail, Magnemite's screws and magnets, stripes, spots, belly
   patches, wings with a few ribs, claws, fins.
4. **Limb and body lines**: a few black lines where an arm crosses the body, where the head meets
   the body, where a leg overlaps.
5. **Shading**: a darker (2) region on the lower right or on darker body parts; white (0) bellies.
   Keep it flat and bold.

Back pictures (32x32, shown doubled in battle, seen from behind and cropped at the bottom) are
simpler: head and back shape, ears/horns/wings/tail, the back markings, at most a sliver of face.

## Report

One line per batch of pictures done, plus a list of the ones you are least happy with.
