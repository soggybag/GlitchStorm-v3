# GlitchStorm v3 firmware

| Folder | What |
|---|---|
| `GlitchStorm_v3/` | The synth: Mitchell's Glitch Storm (from `~/Documents/Synth/glitch-storm/Glitch_Storm`, Apr 2026) ported to the v3 board. `equations.h` copied unchanged |
| `GS3_HWTest/` | Hardware test sketch for `docs/Test Procedure v3.0.md` |

**Controls (v3), left to right from outside:**

| Button | Pin | Does |
|---|---|---|
| BTN 1 | D2 | program **up** |
| BTN 3 (centre) | D3 | **MODE**: restart the current equation (t = 0). Edit `modeButtonPressed()` to change it |
| BTN 2 | D4 | program **down** |

- POT 1–3 (A0–A2) = a, b, c; RATE (A3) = sample rate 256 Hz–32 kHz.
- LEDs = program number in binary, with the left-most LED as the top bit.

**Changes from the previous firmware:**
- Serial debugging off: USB traffic is audible on v3.
- Up-button wrap off-by-one fixed.
- Buttons caught by a pin-change interrupt, so they respond at any RATE (polling missed short presses when the audio ISR was busy); 20 ms debounce; act on press.
- Double ADC reads (pots no longer pull on each other).
- The sample rate only updates when RATE really moves, which stops pitch wobble and missed-compare dropouts.
- `programNumber` and `t` are `volatile`; `t` is reset with interrupts off.
- **CPU guard:** the audio ISR times itself every sample and never lets the sample period drop below 1.5× its own run time (+200 cycles), so `loop()` (buttons, LEDs, pots) always gets at least a third of the CPU.
  - Without it, the heavier equations (2–9: 32-bit `%`, multiplies, variable shifts) ran back-to-back at mid-to-high RATE and froze the buttons.
  - **Side effect:** each equation has its own top speed. Past that point, turning RATE up does nothing more.

**Status:** flashed and tested on the v3.0 board 2026-10-11. All 16 programs step forward and back at any RATE; buttons respond at full RATE.

**Build:** Arduino IDE or `arduino-cli compile --fqbn arduino:avr:nano GlitchStorm_v3` (compiled OK 2026-10-11: 6160 bytes flash, 353 bytes RAM). Many Nano clones need the old bootloader: board option **Processor: ATmega328P (Old Bootloader)**, or `--fqbn arduino:avr:nano:cpu=atmega328old`.
