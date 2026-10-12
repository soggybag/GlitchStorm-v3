# GlitchStorm v3 firmware

| Folder | What |
|---|---|
| `GlitchStorm_v3/` | The synth: Mitchell's Glitch Storm (from `~/Documents/Synth/glitch-storm/Glitch_Storm`, Apr 2026) ported to the v3 board. `equations.h` copied unchanged |
| `FM_Synth_v3/` | The Mozzi FM synth from super-freq.com/arduino-fm-synth, ported to v3 (2026-10-11): needs the **Mozzi 2.x** library |
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

## FM_Synth_v3 (Mozzi FM synth)

- **Audio:** the breadboard version used Mozzi's default PWM on D9. On v3, D9/D10 are LEDs and the audio filter is on D11, so Mozzi runs in `MOZZI_OUTPUT_EXTERNAL_TIMED`: Mozzi times the samples (Timer 1, 16384 Hz) and `audioOutput()` writes each one to Timer 2's 62.5 kHz PWM on D11.
- **Controls:**

| Control | Does | Breadboard |
|---|---|---|
| POT 1 (A0) | carrier frequency | KNOB_0 |
| POT 2 (A1) | modulation intensity | KNOB_1 |
| POT 3 (A2) | modulation speed (LFO) | KNOB_2 |
| RATE (A3) | modulator frequency 2 | KNOB_3 |
| BTN 1 / BTN 2 | intensity 2 down / up (1–10, shown on the LEDs) | KNOB_4 |
| BTN 3 (MODE) | modulation ratio 1–8 (the LEDs show it for ~1 s) | fixed at 5 |
| VOLUME | output level (analog) | none |

- The synth maths is unchanged, including the `int` modulator-frequency product that can overflow (part of the sound). Serial is removed.
- Compiled OK 2026-10-11 (Mozzi 2.0.4): 7162 bytes flash, 827 bytes RAM. **Tested on the v3.0 board 2026-10-11: working.**
