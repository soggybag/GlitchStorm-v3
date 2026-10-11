# GlitchStorm v3: build notes

## Panel parts: heights

The board hangs from the 9 mm pots (Alpha RD901F, back side). The pot body is about 6.3 mm tall and **stands on its metal tabs about 4 mm above the board**. So the board sits **about 10.3 mm below the inside of the face**, plus the face thickness (1590BB: measure, about 3 mm). That puts the outside of the face about 13.3 mm above the board. (Corrected 2026-10-04: the earlier 6.5 mm figure ignored the tabs.)

**Measure your own:** fit one pot, mount it in the lid with no nut under the panel, and measure from the board to the **outside** of the lid. Buttons should be that height + 2–3 mm.

### Buttons (SW1, SW2, SW3 MODE): Tayda A-8796 (DAIER TSL-A064)

**Chosen 2026-10-03:** round 12 mm body, white 9 mm cap, momentary.
- **Height (re-read from the datasheet 2026-10-04):** the body sits on **1.4 mm standoff bumps** (pins 4.7 mm from the body, 3.3 mm below the bumps), then 5.9 mm body + 7.0 mm cap = **14.3 mm overall** above the board. The outside of the face is ~13.3 mm up (10.3 mm gap + ~3 mm face), so the cap should stick out **about 1 mm**: usable but shallow. Check on the real build; a taller cap would help.
- **Footprint:** `SuperFreq:SW_Push_Round_D12mm_P5.00mm_DAIER_TSL-A064` (project library `SuperFreq.pretty`). 4 pins on a 5.00 × 5.00 mm square, 1.1 mm holes, origin at the body centre (same layout as E-Switch KS01Q01).
- **Orientation doesn't matter.** Inside the switch, pins 1–2 and 3–4 are joined. The board wires only two **diagonal** pads (always on opposite sides of the switch); the other two are soldered for strength only.
- **Panel hole:** **~9.5–10 mm** for the 9 mm cap, centred on the button (outside view: MODE · BTN 1 · BTN 2, 15 mm apart).
- Rated 10 mA: fine for a Nano input with `INPUT_PULLUP`.
- **3D model:** `3dmodels/SW_Push_Round_D12mm_DAIER_TSL-A064.step`, drawn from the datasheet (bumps, body, cap, pins), attached in the footprint with offset/rotation 0. Rebuild with `scripts/make_button_step.py` (needs the `cadquery-ocp` Python package).

**Alternative** (needs the old `SW_PUSH_6mm` 6.5 × 4.5 mm footprint): any 6 × 6 mm 4-pin tact switch. Tayda A-5156 (13 mm) or A-5147 (11 mm); A-5145 (9.5 mm) is too short.

### LEDs (D1–D4, 3 mm)

They're on the back. A 3 mm LED is ~5.3 mm tall and the gap is ~10.3 mm, so mount it **on its legs** about 5 mm off the board, with the top at the panel (a strip of card cut to the gap height makes a quick spacer while soldering). Drill 3.2 mm, or use 3 mm LED bezels.

### Pots

Alpha RD901F 9 mm, T18 knurled shaft (the 3D model on the board). Panel hole **7.5 mm** (M7 bushing). The DC jack, MODE pin and volume notes are in `GlitchStorm Roadmap.md`.

## 3D model

`3dmodels/pot_RD901F_T18_shaft_alpha_9mm_vertical.step` (from jolin-components) is attached to RV1–RV5. Settings for the KiCad `Potentiometer_Alpha_RD901F-40-00D_Single_Vertical` footprint: **rotate X −90, offset (6.6, −2.5, 4) mm** (z 4 = the body sits on its 4 mm tabs; corrected 2026-10-04 on this board). The same model and settings are on the Hyper Fuzz, Rat Energizer and Trem boards.

## Jacks (all Tayda)

- **J1 PHONES and J2 LINE OUT: PJ-320A 3.5 mm (Tayda A-4863)**, footprint `SuperFreq:Jack_3.5mm_PJ-320A_Horizontal`, made from Tayda's drawing (`320.pdf`).
  - Pins 2/3/4 in one row (3.2 / 6.2 / 10.2 mm behind the body front), pin 5 in the opposite row (11.3 mm), rows 4.6 mm apart; flat 1.2 × 0.6 mm pins in slots; two 1.5 mm locating pegs.
  - Wiring: **pin 4 = tip (signal)**, pin 3 = ring (PHONES: second channel; LINE OUT: unused), **pins 2 + 5 = GND**. It's a 4-pole jack; a normal 3-pole plug's sleeve touches both pins 2 and 5.
  - **Before soldering, check one with a meter:** plug tip → pin 4, plug sleeve → pins 2 and 5. The pin functions come from reading the datasheet diagram, and match KiCad's PJ320E. If yours differs, don't solder it; the footprint needs two pad names swapped.
  - The 2 mm collar sits at the board's back edge. The barrel centre is ~2.8 mm above the board (on the inside face). Drill positions are in `enclosure/` (estimates). **Plug-reach problem:** the jack front is ~6 mm inside the outside of the wall; see `enclosure/README.md`.
- **J3 DC 9V: Tayda A-4118** (2.1 mm PCB DC jack, flat blade pins; slotted footprint). Centre negative. Check the sleeve blade with a meter (see the Roadmap).

## Measured on the v3.0 build (2026-10-10)

- PCB to the pot body top (inside of the lid): **9.91 mm** (predicted 10.3).
- A-8796 button: shoulder **8.68 mm**, cap top **14.7 mm**. With a ~2.5–3 mm lid, the cap is ~2 mm proud and the shoulder clears the inside by ~1.2 mm. **The button height is fine;** the earlier "only ~1 mm proud" worry is resolved.
- PJ-320A: a loose jack's pins may read badly for continuity (oxidised). After soldering, the pinout matched the footprint (tip pin 4, sleeve pins 2 + 5).

## v3.1 change list (from the v3.0 bench test)

- **Buttons: DONE 2026-10-11.** Silkscreen left → right (outside): **BTN 1 · BTN 3 · BTN 2**.
  - BTN 1 = SW3 → D2; **BTN 3 = SW1 → D3 (centre)**; BTN 2 = SW2 → D4.
  - **The current firmware uses the centre button (BTN 3, D3) as MODE.** The label stays generic so the button can do other things later. D3 is INT1, so it can still use an interrupt like D2 (INT0).
  - No wiring change. The test sketch was updated (`BTN_MODE = 3`, `BTN1 = 2`).
  - Labels sit under each button; DRC 0 errors.
- Still to decide after drilling: jack plug reach (jacks ~6 mm inside the wall's outer surface) and Nano USB access.
- Not needed: taller buttons (cap measured ~2 mm proud).
