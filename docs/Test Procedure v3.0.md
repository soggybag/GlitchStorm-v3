# GlitchStorm v3.0: test procedure

Board: `GlitchStorm3` **v3.0** (git tag `v3.0`; `archive/v3.0/` has the schematic PDF and the interactive BOM). Arduino Nano + MCP6002 + LM386, 1590BB.
General method: `../../_tools/BENCH_TESTING.md`. **Hardware test sketch:** `firmware/GS3_HWTest/GS3_HWTest.ino`. Load it first, then your synth firmware once the hardware checks out.

## What's on the board

| Block | Parts | Notes |
|---|---|---|
| Power | J3 DC (Tayda A-4118, **centre negative**) → **D5 SS14** → Nano VIN; Nano 5 V regulator → **+5V**; **5V_A** = +5V via R17 4.7 Ω + C12/C18 22µ + C13/C19 100n | Audio gets its own filtered 5 V |
| Controls | RV1–RV3 POT1–3 and RV4 RATE (B10k) on A0–A3, 100n each; SW1 BTN1 D3, SW2 BTN2 D4, **SW3 MODE D2** (new), all to GND; LEDs D1–D4 on D10/D9/D8/D7 via 1k | |
| PWM filter | D11 → R5 1k / C5 10n → R6 10k / C6 1n (2nd order, ~16 kHz) → **U2A** follower | |
| Volume + bias | C7 10µ → **RV5 VOLUME A10k** → C8 1µ; **VBIAS** = R10/R11 100k ≈ 2.5 V via R7 100k → **U2B** follower = BUF_OUT | One volume for both outputs |
| Line out | C9 10µ, R9 100k, **R8 470 Ω** → J2 tip | |
| Headphones | C11 1µ, R12 47k / R13 2k2 pad → **U3 LM386** (gain 20, C14 bypass, Zobel R14 10 Ω + C15 47n) → C16 220µ → **R15 / R16 10 Ω** → J1 tip and ring | |

## 0. Before soldering the panel parts

| # | Check | Expected | Measured |
|---|---|---|---|
| 0.1 | **Jack pin check (PJ-320A), meter on a loose jack:** plug in a 3.5 mm plug; tip → pin 4, sleeve → pins 2 and 5 | as listed (from the datasheet reading). **If not, stop:** the footprint needs two pads swapped | |
| 0.2 | **DC jack (A-4118):** with your adapter plugged in, which blade is +? The board expects **+ on the sleeve blade (pin 2), centre negative** | sleeve = + | |
| 0.3 | Fit one RD901F pot (tabs soldered) and measure the real board-to-panel gap: board → **outside** of the 1590BB lid | ~13.3 mm (10.3 mm gap + ~3 mm face) | |
| 0.4 | Button height (A-8796) on the board | 14.3 mm: the cap clears the face by ~1 mm? | |
| 0.5 | Nano on its headers: USB connector vs the wall / rim | does a cable fit? (known issue) | |

## 1. Before power (board assembled, Nano fitted)

| # | Check | Expected | Measured |
|---|---|---|---|
| 1.1 | Visual: U2/U3 pin 1, D5 band, C16 polarity (THT 220µ), Nano orientation, LEDs | as silkscreen | |
| 1.2 | Ohms VIN (D5 cathode) → GND | climbs; **fail: a few Ω** | |
| 1.3 | Ohms 5V_A (U3 pin 6) → GND | climbs; not a short | |

## 2. First power (DC jack, 9 V)

The Nano draws ~20–40 mA, so the 100 Ω trick would starve its regulator. **Use the meter on its mA range in series**, or a 10 Ω resistor (each 0.01 V = 1 mA).

| # | Check | Expected | Measured |
|---|---|---|---|
| 2.1 | Supply current, HW test sketch running | **~30–45 mA** (Nano ~20, LEDs ~3 mA each when lit, LM386 ~4) | |

## 3. DC voltages (HW test sketch, MODE 2 = silent)

| # | Node | Where | Expected | Measured |
|---|---|---|---|---|
| 3.1 | VIN | D5 cathode / Nano VIN | supply − ~0.3 V | |
| 3.2 | +5V | Nano 5V pin | 5.0 V | |
| 3.3 | 5V_A | U2 pin 8 / U3 pin 6 | ~4.95 V | |
| 3.4 | VBIAS | R10/R11 junction | ~2.5 V | |
| 3.5 | U2 pin 7 (BUF_OUT) | | ~2.5 V | |
| 3.6 | U3 pin 5 (LM386 out) | | ~2.5 V | |
| 3.7 | **MODE 1 (DC):** U2 pin 1 while turning POT2 | **0 → ~5 V**, smooth (the filtered PWM) | |

## 4. Controls (Serial Monitor at 115200 baud)

| # | Check | Expected | Seen |
|---|---|---|---|
| 4.1 | A0–A3 readings, each pot end to end | 0 ↔ 1023, smooth; note which direction is up | |
| 4.2 | MODE button cycles 0 → 1 → 2 | LED shows the mode in 1/2; chase in 0 | |
| 4.3 | BTN1 / BTN2 | light LED 1 / LED 2; Serial shows the button bits | |
| 4.4 | RATE changes the chase speed (MODE 0) | | |
| 4.5 | All four LEDs light | | |

## 5. Audio (MODE 0 = tone)

| # | Point | Expected | Seen |
|---|---|---|---|
| 5.1 | U2 pin 1 | the square from D11, edges rounded by the ~16 kHz filter, 0–5 V | |
| 5.2 | U2 pin 7 (BUF_OUT), VOLUME max | the same, AC-coupled around 2.5 V | |
| 5.3 | LINE OUT jack | tone; VOLUME controls it | |
| 5.4 | PHONES (low volume first!), both ears | tone in both ears; no hiss or whine in MODE 2 | |
| 5.5 | POT1 sweeps the pitch 100 Hz → 2 kHz | | |
| 5.6 | Any digital noise (Nano clock whine) at the outputs in MODE 2, VOLUME max | note the level | |

Then load your synth firmware. The pin map is the same as v2 plus **MODE on D2** (`INPUT_PULLUP`).

## 6. Enclosure (the open issues from ordering)

| # | Check | Result |
|---|---|---|
| 6.1 | Plug reach: does a 3.5 mm plug seat fully through the wall? (predicted: jack fronts ~6 mm inside the wall) | |
| 6.2 | Button caps: proud of the face enough to press? | |
| 6.3 | USB: can a cable reach the Nano? | |
| 6.4 | Decisions for v3.1 (overhanging jacks, taller buttons, USB access) | |

## Record

| Item | Result |
|---|---|
| Unit number | |
| Date | |
| Notes | |
