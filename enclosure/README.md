# Enclosure: Hammond/Tayda 1590BB (landscape)

- **`GlitchStorm3_1590BB_drill.csv`:** face holes for the Tayda Box Tool, plus the side-wall holes as estimates.
- **`GlitchStorm3_1590BB_drill_template.svg`:** a 1:1 printable template, outside view, with the jack wall and the USB end unfolded.

Generated 2026-10-04 from the KiCad board (v3, PJ-320A jacks, pots raised 4 mm on their tabs).

## Mill marking file (Bantam Tools Othermill)

**`GlitchStorm3_1590BB_mill_marks.svg`:** for engraving hole marks on the face, then drilling on the drill press.
- **Page:** 119.5 × 94 mm = the 1590BB face (landscape), **outside view**.
- **Contents:** one circle per hole at its finished diameter (outline to inscribe), plus a **1 mm circle at each centre** (the drill point). Stroke only, no fill, no text, no box outline, so nothing else gets engraved.
- **Checked 2026-10-10** against the v3.0 board (the ordered boards; the working copy is identical): every pot shaft, button centre and LED centre matches the drill CSV.

**Orientation:** the **top edge of the SVG = the jack wall** (the long side with PHONES / LINE / DC), and the **right edge = the USB end**.

**Alignment:**
- If Bantam places the file by its page, line the page's lower-left corner up with the face's lower-left corner.
- If it places by the geometry instead, the marks' bounding box starts **26.0 mm from the left edge and 20.0 mm from the bottom edge** of the face (it spans x 26.0–93.5, y 20.0–58.75).
- Either way, the layout is symmetric about the face centre (POT 2 / BTN 1 are on the centre line). The most reliable zero is **the centre of the face**: X 59.75, Y 47 from the lower-left.
- The box walls have a slight draft, so the top face measures a little under 119.5 × 94. **Measure your box** and centre on it rather than trusting the corners.

**Check before you start:**
- The 1590BB is ~34–35 mm tall. The original Othermill's Z clearance is about that much, so **check the box fits under the spindle with the engraving bit** (with the spoilboard / bed setup you use) before running.
- If it doesn't fit, print the SVG at 100 % instead, tape it on, and centre-punch.

## Face (side A): taken from the board, ready to order

| Hole | Ø mm | Part |
|---|---|---|
| POT 1–3, RATE, VOLUME | 7.5 | Alpha RD901F 9 mm (M7 bushing) |
| MODE, BTN 1, BTN 2 | 10.0 | Tayda A-8796 (Ø9 cap) |
| LEDs D1–D4 | 3.2 | 3 mm LED, no bezel (~5–6 mm with a bezel) |

### Coordinates

- **Origin and units:** the origin is the centre of the face; units are mm, **+X right, +Y up**, viewed from outside.
- **Landscape view:** the jacks are on the top long wall and the Nano USB is on the right end.
- **Board-to-face mapping:** the box centre sits at board (150, 100). The controls are on the back of the board (facing the panel), so the outside view is mirrored: **X = 150 − x_board, Y = 100 − y_board**.
- **Tayda columns:** Tayda's 1590BB side A is portrait (90 × 115.5). The "Tayda portrait" columns are the landscape layout turned 90° clockwise (X = Y_land, Y = −X_land). In that view the jack wall is on the right long side and the USB end is at the bottom.
  - The Box Tool shows which letter (C or E) is the right wall. I couldn't confirm Tayda's side letters, so this README doesn't name them.
- **Hole sizes:** the diameters are for raw aluminium. For powder-coated boxes, add Tayda's allowance (users report +0.2 to +0.4 mm).
- **Mounting holes:** M3 holes H1–H4 are not drilled, because the board hangs from the pot nuts.

## Side walls: estimates only; drill by hand after a test fit

The heights below are calculated, not measured. Each depth is measured from the **outside surface of the face** and adds up:

- face ≈ 3.0 mm (measure yours);
- board-to-face gap ≈ 10.3 mm (pot body 6.3 + 4 mm tabs);
- board 1.6 mm;
- the part's own centre height above the board.

| Wall | Hole | Along (X) | Depth | Ø |
|---|---|---|---|---|
| Jack wall | PHONES | −7.0 | 17.7 | 6.0 |
| Jack wall | LINE OUT | −21.0 | 17.7 | 6.0 |
| Jack wall | DC 9V | −35.25 | 21.4 | 8.0 |
| USB end | Nano USB | Y +26.0 | 27.0 | slot ~12 × 8 |

### Problems found while making these

1. **Plug reach.**
   - The jack fronts sit at the board edge. That is **~6 mm inside the outside of the wall** (a ~1.6–3 mm gap to the inner wall, plus the wall itself).
   - A 3.5 mm plug needs ~14 mm of insertion, and a DC plug ~9 mm. Most plugs won't seat fully through a 6 mm or 8 mm hole unless the plug body can enter the hole.
   - **Fix options:**
     - (a) move J1/J2/J3 outward on the board so their fronts overhang the edge and touch the inner wall (board change);
     - (b) use panel-mount jacks wired to the pads;
     - (c) use bigger holes that let the plug bodies in.
2. **USB height.**
   - With the Nano on female headers, the USB centre is ~27 mm deep, and the slot runs into the rim (the side wall is ~29 mm).
   - Expect to file a notch at the rim's edge, or mount the Nano on low-profile headers.
3. **Button height.** The A-8796 is 14.3 mm overall (it stands on 1.4 mm bumps), so the cap should stick out only ~1 mm past a 3 mm face. See `docs/Build Notes.md`.

**Before ordering:** print the SVG at 100% (check the 50 × 10 mm box), and test-fit the pots, the board and one of each jack.
