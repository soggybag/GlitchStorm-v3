/*
  Arduino FM synth (super-freq.com/arduino-fm-synth), ported to the GlitchStorm v3 hardware (2026-10-11).
  Simple ring mod mozzi synth
  Adapted from Mozzi Example: Knob_lightLevel_FMsynth
  Originally modded by: https://www.instructables.com/Using-Mozzi-Library-with-5-potentiometers/
  This creates an FM synth with 5 knobs. It makes alien spaceship noises!

  v3 hardware port (Mozzi 2.x):
  - Audio: the breadboard version used Mozzi's default PWM on D9 (Timer 1). On v3 the audio filter is on D11 and
    D9/D10 drive LEDs, so Mozzi runs in MOZZI_OUTPUT_EXTERNAL_TIMED mode (it keeps the sample timing on Timer 1)
    and audioOutput() writes each sample to Timer 2's PWM on D11 (62.5 kHz, above the v3 ~16 kHz filter).
  - Controls: v3 has four pots on A0-A3 (the fifth knob is the analog VOLUME) plus three buttons:
      POT 1 (A0) = carrier frequency          (was KNOB_0)
      POT 2 (A1) = modulation intensity       (was KNOB_1)
      POT 3 (A2) = modulation speed (LFO)     (was KNOB_2)
      RATE  (A3) = modulator frequency 2      (was KNOB_3)
      BTN 1 (D2, left) / BTN 2 (D4, right) = intensity 2 down / up, 1-10 (was KNOB_4); shown on the LEDs in binary
      BTN 3 (D3, centre, MODE) = modulation ratio 1-8 (was fixed at 5); the LEDs show it for ~1 s, then go back
  - Serial removed (USB traffic is audible on v3).
  The synth maths (maps, intensity, LFO, smoothing, phase mod) is unchanged from the breadboard sketch.
*/

#include "MozziConfigValues.h"
#define MOZZI_AUDIO_MODE MOZZI_OUTPUT_EXTERNAL_TIMED // sample timing by Mozzi, output written by audioOutput()
#define MOZZI_AUDIO_BITS 8
#define MOZZI_CONTROL_RATE 128

// Import libraries
#include <Mozzi.h>                // Required for a Mozzi Sketch
#include <Oscil.h>                // Oscillator
#include <tables/cos2048_int8.h>  // Table for Oscils to play
#include <Smooth.h>               // Low pass filter
#include <AutoMap.h>              // Maps unpredictable inputs to a range

// v3 pins
#define AUDIO_PIN   11 // OC2A: Timer 2 PWM into the v3 output filter
#define BTN1_PIN    2  // left:   intensity 2 down
#define BTN3_PIN    3  // centre: MODE (modulation ratio)
#define BTN2_PIN    4  // right:  intensity 2 up
const uint8_t LED_PINS[4] = {7, 8, 9, 10}; // bit 0..3 (D10 = bit 3 = the left-most LED from outside)

// Define carrier frequency max and min, for AutoMap
const int MIN_CARRIER_FREQ = 22;
const int MAX_CARRIER_FREQ = 440;

// Define intensity max and min, for AutoMap, note they're inverted for reverse dynamics
const int MIN_INTENSITY = 700;
const int MAX_INTENSITY = 10;

// Define mod speed max and min, for AutoMap, note they're inverted for reverse dynamics
const int MIN_MOD_SPEED = 10000;
const int MAX_MOD_SPEED = 1;

// Define some auto maps. These scale values read from analog input to values used for audio operations
AutoMap kMapCarrierFreq(0, 1023, MIN_CARRIER_FREQ, MAX_CARRIER_FREQ);
AutoMap kMapIntensity(0, 1023, MIN_INTENSITY, MAX_INTENSITY);
AutoMap kMapModSpeed(0, 1023, MIN_MOD_SPEED, MAX_MOD_SPEED);

const int KNOB_0 = 0; // Analog pin A0 Carrier frequency
const int KNOB_1 = 1; // Analog pin A1 Modulator Frequency
const int KNOB_2 = 2; // Analog pin A2 Modulation speed
const int KNOB_3 = 3; // Analog pin A3 Mod Frequency 2 (the RATE knob on v3)

Oscil<COS2048_NUM_CELLS, MOZZI_AUDIO_RATE> aCarrier(COS2048_DATA);     // Carrier Frequency Oscil
Oscil<COS2048_NUM_CELLS, MOZZI_AUDIO_RATE> aModulator(COS2048_DATA);   // Modulator Frequency Oscil
Oscil<COS2048_NUM_CELLS, MOZZI_CONTROL_RATE> kIntensityMod(COS2048_DATA); // Modulator intensity Oscil

int mod_ratio = 5;       // brightness (harmonics): now set with MODE, 1-8
int intensity_2_mul = 5; // was KNOB_4 (1-10): now set with BTN 1 / BTN 2
long fm_intensity;       // carries control info from updateControl to updateAudio

// smoothing for intensity to remove clicks on transitions
float smoothness = 0.95f;
Smooth <long> aSmoothIntensity(smoothness);

// Button state (defined before any function so Arduino's auto-prototypes can see the type)
struct Btn { uint8_t pin; uint8_t hist; };
Btn btn1 = {BTN1_PIN, 0xFF}, btn2 = {BTN2_PIN, 0xFF}, btn3 = {BTN3_PIN, 0xFF};

// LEDs: show intensity 2; after MODE, show the ratio for ~1 s
uint8_t showRatioTicks = 0;

void showLeds(uint8_t v) {
  for (uint8_t i = 0; i < 4; i++) digitalWrite(LED_PINS[i], bitRead(v, i));
}

// Buttons, polled at the control rate (128 Hz = every 7.8 ms; Mozzi's scheduling keeps this steady).
// A press counts when the pin has read LOW twice in a row after being HIGH (debounce ~8-16 ms).

bool btnPressed(Btn &b) {
  b.hist = (b.hist << 1) | digitalRead(b.pin);
  return (b.hist & 0b111) == 0b100; // HIGH, then LOW, LOW
}

void audioOutput(const AudioOutput f) {
  int out = f.l() + MOZZI_AUDIO_BIAS; // centre on 128
  OCR2A = constrain(out, 0, 255);
}

void setup() {
  for (uint8_t i = 0; i < 4; i++) pinMode(LED_PINS[i], OUTPUT);
  pinMode(BTN1_PIN, INPUT_PULLUP);
  pinMode(BTN2_PIN, INPUT_PULLUP);
  pinMode(BTN3_PIN, INPUT_PULLUP);
  showLeds(intensity_2_mul);

  startMozzi(); // :))

  // Timer 2: fast PWM on OC2A (D11), no prescaler = 16 MHz / 256 = 62.5 kHz
  pinMode(AUDIO_PIN, OUTPUT);
  TCCR2A = _BV(COM2A1) | _BV(WGM21) | _BV(WGM20);
  TCCR2B = _BV(CS20);
  OCR2A = 128;
}

void updateControl() {

  // Read Knobs with mozziAnalogRead()

  int knob_0_value = mozziAnalogRead(KNOB_0); // value is 0 - 1023
  int knob_1_value = mozziAnalogRead(KNOB_1); // value is 0 - 1023
  int knob_2_value = mozziAnalogRead(KNOB_2); // value is 0 - 1023
  int knob_3_value = mozziAnalogRead(KNOB_3); // value is 0 - 1023
  // These numbers need to converted (mapped) to values that makes sense for use with Mozzi

  // Buttons: BTN 1 / BTN 2 = intensity 2 (was knob 4), MODE = modulation ratio
  if (btnPressed(btn1) && intensity_2_mul > 1)  { intensity_2_mul--; showRatioTicks = 0; }
  if (btnPressed(btn2) && intensity_2_mul < 10) { intensity_2_mul++; showRatioTicks = 0; }
  if (btnPressed(btn3)) { mod_ratio = mod_ratio % 8 + 1; showRatioTicks = MOZZI_CONTROL_RATE; }
  if (showRatioTicks) { showRatioTicks--; showLeds(mod_ratio); } else showLeds(intensity_2_mul);

  // Map values from analog read to values used by synth

  int carrier_freq = kMapCarrierFreq(knob_0_value);           // map knob 0 to carrier frequency
  int intensity = kMapIntensity(knob_1_value);                // map knob 1 intenisty
  float mod_speed = (float)kMapModSpeed(knob_2_value) / 1000; // map knob 2 to mod speed use a float here for low frequencies
  int intensity_2 = kMapIntensity(knob_3_value);              // map knob 3 to frequency 1 intensity
  int knob_4_calibrated = intensity_2_mul;                    // was kMapIntensity2(knob 4): now from the buttons

  // Calculate the modulation Frequency
  // (kept as in the breadboard sketch: this int product can overflow and wrap, which is part of its sound)
  int mod_freq = carrier_freq * mod_ratio * intensity_2;

  // set the FM oscillator frequencies
  aCarrier.setFreq(carrier_freq);
  aModulator.setFreq(mod_freq);

  // calculate the fm_intensity
  fm_intensity = ((long)intensity * knob_4_calibrated * (kIntensityMod.next() + 128)) >> 8; // shift back to range after 8 bit multiply

  kIntensityMod.setFreq(mod_speed);
}

AudioOutput updateAudio() {
  // Ring mod the FM'd carrier with the modulator
  long modulation = aSmoothIntensity.next(fm_intensity) * aModulator.next();
  // Phase mod the carrier
  return MonoOutput::from8Bit(aCarrier.phMod(modulation));
}

void loop() {
  audioHook();
}
