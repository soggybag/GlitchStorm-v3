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
| 0.1 | **Jack pin check (PJ-320A), meter on a loose jack:** plug in a 3.5 mm plug; tip → pin 4, sleeve → pins 2 and 5 | as listed (from the datasheet reading). **If not, stop:** the footprint needs two pads swapped | ✅ |
| 0.2 | **DC jack (A-4118):** with your adapter plugged in, which blade is +? The board expects **+ on the sleeve blade (pin 2), centre negative** | sleeve = + | 🤯 |
| 0.3 | Fit one RD901F pot (tabs soldered) and measure the real board-to-panel gap: board → **outside** of the 1590BB lid | ~13.3 mm (10.3 mm gap + ~3 mm face) | 9.91mm |
| 0.4 | Button height (A-8796) on the board | 14.3 mm: the cap clears the face by ~1 mm? | 8.68mm to lip |
| 0.5 | Nano on its headers: USB connector vs the wall / rim | does a cable fit? (known issue) | ?? |

**Section 0 notes (2026-10-10):**
- **Jacks:** continuity was unreliable on the loose jacks (oxidised pins); after soldering, the pins read as expected ✓.
- **Heights** (calipers from the PCB surface):
  - **Pot body top** (where the thread starts) = **9.91 mm**. That's where the lid's inside face sits (predicted 10.3 mm), so the outside of the face ≈ 9.9 + lid thickness (~2.5–3 mm) ≈ **12.4–12.9 mm**.
  - **Button:** the wide lip (body shoulder) is at **8.68 mm**, so it stays **~1.2 mm below the inside of the lid** ✓. The cap top is at **14.7 mm** (datasheet estimate 14.3), so the cap stands **~1.8–2.3 mm proud of the face** ✓. Usable: **no taller button needed for v3.1.**
  - Panel hole for the button: big enough for the 9 mm cap (9.5–10 mm), smaller than the 12 mm body, so the body can't push through.
- 0.5 (USB reach): to check once the box is drilled.

## 1. Before power (board assembled, Nano fitted)

| # | Check | Expected | Measured |
|---|---|---|---|
| 1.1 | Visual: U2/U3 pin 1, D5 band, C16 polarity (THT 220µ), Nano orientation, LEDs | as silkscreen | ✅ |
| 1.2 | Ohms VIN (D5 cathode) → GND | climbs; **fail: a few Ω** | Mega Ohms |
| 1.3 | Ohms 5V_A (U3 pin 6) → GND | climbs; not a short | Mega ohms |

## 2. First power (DC jack, 9 V)

The Nano draws ~20–40 mA, so the 100 Ω trick would starve its regulator. **Use the meter on its mA range in series**, or a 10 Ω resistor (each 0.01 V = 1 mA).

| # | Check | Expected | Measured |
|---|---|---|---|
| 2.1 | Supply current, HW test sketch running | **~30–45 mA** (Nano ~20, LEDs ~3 mA each when lit, LM386 ~4) | 28.4mA with all knobs in the center and LEDs cycling, nothing plugged into the outputs. |

## 3. DC voltages (HW test sketch, MODE 2 = silent)

| # | Node | Where | Expected | Measured |
|---|---|---|---|---|
| 3.1 | VIN | D5 cathode / Nano VIN | supply − ~0.3 V | supply 9.37V / Nano VIN 9.07V |
| 3.2 | +5V | Nano 5V pin | 5.0 V | 5V |
| 3.3 | 5V_A | U2 pin 8 / U3 pin 6 | ~4.95 V | 4.98V |
| 3.4 | VBIAS | R10/R11 junction | ~2.5 V | 2.48V |
| 3.5 | U2 pin 7 (BUF_OUT) | | ~2.5 V | 2.49V |
| 3.6 | U3 pin 5 (LM386 out) | | ~2.5 V | 2.5V |
| 3.7 | **MODE 1 (DC):** U2 pin 1 while turning POT2 | **0 → ~5 V**, smooth (the filtered PWM) | |

**Sections 2–3 notes (2026-10-10):**
- **Power path:** 9.37 V in → **9.07 V at VIN**. D5 drops 0.30 V, as expected, which also confirms the **DC jack polarity is right**.
- **Rails:** +5V 5.00 V, **5V_A 4.98 V** (20 mV across R17 4.7 Ω ≈ 4 mA, the LM386 + MCP6002) ✓.
- **Bias:** VBIAS 2.48 V, BUF_OUT 2.49 V, LM386 out 2.50 V. Everything sits at mid-supply ✓.
- **Still to do:**
  - 2.1 (supply current);
  - 3.7 and section 4: these need the pots (the analog inputs float without them);
  - sections 5–6, after the enclosure is drilled and the pots/LEDs/buttons are mounted.

## 4. Controls (Serial Monitor at 115200 baud)

| # | Check | Expected | Seen |
|---|---|---|---|
| 4.1 | A0–A3 readings, each pot end to end | 0 ↔ 1023, smooth; note which direction is up | CW is up, A0 - A3 range 0 - 1023 |
| 4.2 | MODE button cycles 0 → 1 → 2 | LED shows the mode in 1/2; chase in 0 | SW1/BTN3 (center) Lights LED D4, SW2/BTN2 (right) lights D3, SW3/BTN1 (left) lights toggles light D3/Cycles LEDs |
| 4.3 | BTN1 / BTN2 | light LED 1 / LED 2; Serial shows the button bits | |
| 4.4 | RATE changes the chase speed (MODE 0) | | RATE changes the speed CCW is fast, CW is slow |
| 4.5 | All four LEDs light | | Yes |

## 5. Audio (MODE 0 = tone)

| # | Point | Expected | Seen |
|---|---|---|---|
| 5.1 | U2 pin 1 | the square from D11, edges rounded by the ~16 kHz filter, 0–5 V | From phones I see about 4V max vol, 0.32mS Square at max freq, 5mS at min freq |
| 5.2 | U2 pin 7 (BUF_OUT), VOLUME max | the same, AC-coupled around 2.5 V | looks 5V |
| 5.3 | LINE OUT jack | tone; VOLUME controls it | outputs mono, working |
| 5.4 | PHONES (low volume first!), both ears | tone in both ears; no hiss or whine in MODE 2 | outputs stereo, working |
| 5.5 | POT1 sweeps the pitch 100 Hz → 2 kHz | | From phones I see about 4V max vol, 0.32mS Square at max freq, 5mS at min freq |
| 5.6 | Any digital noise (Nano clock whine) at the outputs in MODE 2, VOLUME max | note the level | I detect a small about of what sounds like a digital clicking at high frequencies. |

Then load your synth firmware: **`firmware/GlitchStorm_v3/`** (ported 2026-10-11: BTN 1 up, BTN 3 MODE = restart, BTN 2 down). Buttons (all `INPUT_PULLUP`): **BTN 1 = D2 (left), BTN 3 = D3 (centre, MODE), BTN 2 = D4 (right)**. The v2 firmware used D3/D4 as its two buttons, so map MODE to D3 and give D2 the old D3 job.

**Sections 4–5 notes (2026-10-11):**
- 4.1 pots: 0–1023, **CW = up** ✓. 4.4 RATE: CW = slower chase. That's just the test sketch's mapping (a bigger reading gives a longer delay), not a wiring fault ✓. 4.5 all LEDs ✓.
- **4.2/4.3 button → LED mapping: to confirm.**
  - The test sketch expects: **MODE = SW3 (D2), left from outside** → cycles modes ✓ (seen).
  - **SW1 (D3), centre** → lights LED 1 (board **D1**, the left-most LED from outside).
  - **SW2 (D4), right** → lights LED 2 (board **D2**).
  - Seen: centre → "D4", right → "D3".
  - In MODE 1 / MODE 2 the sketch also keeps D3 / D4 lit as the mode indicator, so check in **MODE 0** (chase) or by the Serial `btn` bits (MODE, BTN1, BTN2), and note LED positions left → right from outside.
- **5.1/5.5 pitch:** 5 ms at min and 0.32 ms at max. The sketch sets 100 Hz–2 kHz (10 ms–0.5 ms full cycle). 5 ms at the low end looks like **half a cycle** (= 100 Hz). Re-measure full cycles; this is the sketch's tone, not the hardware.
- 5.1 ~4 Vpp at the phones (LM386 on 5 V) ✓; 5.2 BUF_OUT ~5 Vpp at full volume (MCP6002 rail-to-rail) ✓; 5.3 line mono ✓; 5.4 phones both ears ✓.
- **5.6 faint digital clicking in MODE 2:** the test sketch prints to Serial every 250 ms, and USB traffic draws 5 V current in bursts. Test: close the Serial Monitor and power from the DC jack with USB unplugged. If the clicks stop, it's USB/serial activity (not present in normal use). If they stay, note the level for v3.1 (more 5V_A filtering).

**Follow-up (2026-10-11):**
- **Buttons/LEDs:** correct. Centre (SW1) → D1, right (SW2) → D2; the LEDs run D1–D4 left → right from outside. (The first reading was mirrored by looking at the back of the board.) ✓
- **Pitch:** the earlier readings were half cycles ✓.
- **Clicking:** gone with USB unplugged: it's USB/serial traffic, not a v3.1 issue ✓.
- **Unstable low notes** (bottom ~5 % of POT1, worse with RATE CW; also near the bottom with RATE at max): **a test-sketch artifact, not hardware.**
  1. The sketch called `tone()` on every loop pass (~0.5 ms), and each call restarts the waveform. Notes with a period longer than a loop (100 Hz = 10 ms) got chopped.
  2. **ADC crosstalk:** the first `analogRead` after switching channels is pulled toward the previous channel's voltage. RATE (A3) is read just before POT1 (A0) on the next pass, so RATE's position nudges the POT1 reading. That's why RATE changed the effect.
  - **Fixed in `GS3_HWTest.ino`:** a double read per channel, and `tone()` only re-set when POT1 moves by more than 3 counts. Re-flash and re-check; the low end should be steady.
  - **For the synth firmware:** the same ADC crosstalk applies. Discard the first read after switching channels (or average), and avoid re-starting the audio timer every loop.

- **2.1 supply current: 28.4 mA** (knobs centred, LEDs cycling, outputs unplugged). Just under the 30–45 mA estimate ✓.
- **Low end with the fixed sketch:** stable ✓.
- **Silkscreen labels don't match the circuit (v3.1 fix):** left to right on the back,
  - the left button (SW3, D2 = **MODE**) is labelled "BTN 1" (left over from v2, before MODE was added);
  - the centre button (SW1, D3 = **BTN 1**) has no label;
  - the right button (SW2, D4 = BTN 2) is labelled correctly.
  - **Decided 2026-10-11:** silkscreen **BTN 1 · BTN 3 · BTN 2** (left → right). The **centre button (BTN 3, D3) is MODE** in the current firmware and the test sketch (re-flash `GS3_HWTest.ino`). BTN 1 (left, D2) lights LED 1; BTN 2 (right, D4) lights LED 2.

**Synth firmware (2026-10-11):** `firmware/GlitchStorm_v3/` runs on the board.
- Two firmware bugs were found and fixed on the bench:
  1. Buttons missed at high RATE (polling while the audio ISR was busy) → pin-change interrupt.
  2. Programs 2–9 froze the controls at mid/high RATE (ISR overrun) → per-equation CPU guard in the ISR.
- Now all 16 programs step at any RATE ✓.

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
