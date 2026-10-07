
## v3 board update (2026-10-03)

- **DC jack:** footprint → KiCad generic `BarrelJack_Horizontal` (slotted pads for DC-005-style flat blade pins). Same position and pins: 1 centre = GND, 2 sleeve = +9V. Check your jack with a meter: the sleeve blade should be the one in line with the centre pin.
- **Pots:** all five are now Alpha RD901F 9 mm (back side), at the same shaft positions. Drill 7 mm.
- **New MODE button (SW3) → Nano D2** (INT0), wired like the others: to GND, use `INPUT_PULLUP`. Pin map: pots A0–A3 · buttons D2 MODE, D3, D4 · LEDs D7–D10 · audio PWM D11.
- **Panel:** three buttons evenly spaced (MODE on the outside-left), four LEDs in an evenly spaced row (read as one binary number).
- **Volume:** one VOLUME pot sets both headphone and line levels (it sits before the output buffer that feeds both).
