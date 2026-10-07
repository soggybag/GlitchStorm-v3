# GlitchStorm v3 v3.0: archived revision

- **Git tag:** `v3.0` (commit `af12740`, 2026-10-06)
- **Tag note:** v3.0: ordered from JLCPCB (October 2026 batch)
- **Archived:** 2026-10-06 with `_tools/archive_version.py`

## Finding a part

1. Open `GlitchStorm3_ibom.html` in a browser. Type a reference (R14) or a value (100k) in the filter box; the part lights up on the board.
   - Hover over a pad to see its net.
   - F / B switch sides.
2. Find the same reference in `GlitchStorm3_schematic.pdf` with Cmd-F.
3. `GlitchStorm3_board_front.pdf` / `_back.pdf` are printable: page 1 has the outlines and references, page 2 the copper. The back is mirrored, as you see it holding the board.

## Files

- `GlitchStorm3_board_back.pdf`
- `GlitchStorm3_board_front.pdf`
- `GlitchStorm3_ibom.html`
- `GlitchStorm3_render_bottom.png`
- `GlitchStorm3_render_top.png`
- `GlitchStorm3_schematic.pdf`
- `docs`/
- `parts.csv`
- `production`/

`production/` holds the files sent to JLCPCB for this revision: GlitchStorm3.zip, GlitchStorm3_hand_solder.csv, bom.csv, designators.csv, netlist.ipc, positions.csv.
