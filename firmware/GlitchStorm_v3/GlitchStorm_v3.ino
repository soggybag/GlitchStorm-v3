// Glitch Storm
// CC By Sa Spherical Sound Society 2020
// Heavy inspiration in Bytebeat (Viznut)
// Some equations are empty. You can collaborate sending your new finding cool sounding ones to the repository
// https://github.com/spherical-sound-society/glitch-storm

// This is my take on Glitch Storm. I revised the original files and made a few changes to suit
// my software design style.

// GlitchStorm v3 hardware port (2026-10-11), from ~/Documents/Synth/glitch-storm/Glitch_Storm (Apr 2026).
// v3 board, buttons left to right from outside (all to GND, INPUT_PULLUP):
//   BTN 1 = D2 (SW3) -> program UP      (same pin as before)
//   BTN 3 = D3 (SW1) -> MODE: restart the current equation (t = 0). Change modeButtonPressed() to give it another job.
//   BTN 2 = D4 (SW2) -> program DOWN    (the v2 PCB used D3 here; v3 is back on D4)
// LEDs D7-D10 show the program number in binary (D10 = bit 3 = the left-most LED from outside).
// Pots A0-A2 = a, b, c; A3 = RATE. Audio PWM on D11 into the v3 2nd-order filter + buffer + LM386.
// Changes from the previous firmware:
//   - debugging (Serial) off by default: USB traffic is audible as clicks on v3
//   - up-button wrap fixed (could reach programNumber == totalPrograms)
//   - buttons caught by a pin-change interrupt (responsive at any RATE), debounced (20 ms), act on press
//   - each pot read twice, first read discarded (the ADC holds the previous channel's voltage)
//   - sample rate only updated when RATE really moves (stops ADC-noise pitch wobble and OCR1A glitches)
//   - programNumber volatile (it's read in the ISR)
//   - CPU guard: the ISR caps the sample rate per equation so loop() always gets time (heavy equations froze
//     the buttons/LEDs at high RATE)

#include <stdint.h>
#include <avr/interrupt.h>
#include <avr/io.h>
#include <avr/pgmspace.h>
#include "equations.h"

#define isDebugging   false // Set to true to enable serial output for debugging (USB traffic is audible on v3)

#define ledPin        13 // On-board LED
#define speakerPin    11 // PWM pin for audio output
#define upButtonPin   2  // BTN 1 (left): program up
#define modeButtonPin 3  // BTN 3 (centre): MODE
#define downButtonPin 4  // BTN 2 (right): program down

// Pins for the 4 LEDs showing the current program number in binary
#define progBit0Pin   7  // Pin for the "program bit 0"
#define progBit1Pin   8  // Pin for the "program bit 1"
#define progBit2Pin   9  // Pin for the "program bit 2"
#define progBit3Pin   10 // Pin for the "program bit 3"

#define debounceMs    20 // button debounce time

volatile long t = 0;                  // time variable for equations
volatile uint8_t a = 0, b = 0, c = 0; // parameters for equations
volatile int value;                   // current output value

volatile byte programNumber = 0; // current program number (read in the ISR)

static unsigned long time_now = 0; // For debugging

uint32_t SAMPLE_RATE = 16384; // Initial sample rate
int rateRaw = -100;           // last RATE reading used (hysteresis)

// CPU guard: the audio ISR measures how many CPU cycles each sample takes and never lets the sample period
// get shorter than 1.5x that (+200 cycles). Heavy equations (32-bit %, multiplies, variable shifts) can
// otherwise take longer than one sample at high RATE settings; the ISR then runs back-to-back and loop()
// (buttons, LEDs, pots) never runs. The guard caps the effective RATE per equation instead.
volatile uint16_t isrCycles = 0; // worst-case ISR time since the last reset (Timer 1 counts at F_CPU)

// Buttons are caught by a pin-change interrupt (PCINT2: D2, D3, D4 are all on port D), so a press is
// latched the moment it happens even when the audio ISR is using most of the CPU at high RATE settings.
#define BTN_UP   _BV(2) // D2 = PD2
#define BTN_MODE _BV(3) // D3 = PD3
#define BTN_DOWN _BV(4) // D4 = PD4
#define BTN_MASK (BTN_UP | BTN_MODE | BTN_DOWN)
volatile uint8_t btnPressed = 0;       // latched presses, read and cleared in loop()
volatile uint8_t btnLastPins = BTN_MASK; // last seen pin states (HIGH = released)
volatile unsigned long btnLastEdge[5]; // per-pin time of the last edge (index = PD bit)



///////////////////////////////////////////////////////////////
// SETUP AUDIO OUTPUT /////////////////////////////////////////

// Initialize sound output
// Note: this function sets up timer 1 and 2 and nothing here should be modified.
// Read about timers here: https://docs.arduino.cc/tutorials/generic/secrets-of-arduino-pwm/
void initSound() {
  pinMode(speakerPin, OUTPUT);       // Set speaker pin as output

  // Timer 2 generates audio on PWM pin OC2A (Arduino pin 11)
  // ASSR -> Async Shift Register, TCCR2A / TCCR2B: Timer/Counter Control Registers A and B
  // WGMn -> Waveform Generation Mode n
  ASSR &= ~(_BV(EXCLK) | _BV(AS2));  // Use internal clock for Timer 2 (p.154) _BV() bit value
  TCCR2A |= _BV(WGM21) | _BV(WGM20); // Set Fast PWM mode (p.155)
  TCCR2B &= ~_BV(WGM22);             // (part of WGM22 is in TCCR2B)

  // Do non-inverting PWM on pin OC2A (p.155)
  // On the Arduino this is pin 11.
  // TCCRnA -> Timer/Counter Control Register nA
  // COMnA -> Compare Output Mode nA
  TCCR2A = (TCCR2A | _BV(COM2A1)) & ~_BV(COM2A0); // Clear OC2A on Compare Match, set at BOTTOM (non-inverting mode)
  TCCR2A &= ~(_BV(COM2B1) | _BV(COM2B0)); // Disconnect OC2B
  // No prescaler (p.158): PWM at 16 MHz / 256 = 62.5 kHz, well above the v3 filter (~16 kHz)
  TCCR2B = (TCCR2B & ~(_BV(CS12) | _BV(CS11))) | _BV(CS10); // Set CS22, CS21, CS20 bits for no prescaling

  // Set initial pulse width to the first sample.
  // OCRnA -> Output Compare Register nA
  OCR2A = 0; // Output Compare Register 2A (8-bit, p.156)

  // Set up Timer 1 to send a sample every interrupt.
  cli(); // Disable interrupts while we set up

  // Timer 1 is a 16-bit timer (p.132)
  // Set CTC mode (Clear Timer on Compare Match) (p.133)
  // Have to set OCR1A *after*, otherwise it gets reset to 0!
  TCCR1B = (TCCR1B & ~_BV(WGM13)) | _BV(WGM12); // Set WGM13:0 to 0100
  TCCR1A = TCCR1A & ~(_BV(WGM11) | _BV(WGM10)); // (part of WGM13:0 is in TCCR1A)

  // No prescaler (p.134)
  TCCR1B = (TCCR1B & ~(_BV(CS12) | _BV(CS11))) | _BV(CS10); // Set CS12, CS11, CS10 bits for no prescaling

  // Set the compare register (OCR1A).
  // OCR1A is a 16-bit register, we have to do this with
  // interrupts disabled to be safe.
  OCR1A = F_CPU / SAMPLE_RATE; // 16e6 / 8000 = 2000
  // Timer 1 calls Interrupt Service Routine ISR(TIMER1_COMPA_vect) at SAMPLE_RATE

  // Enable interrupt when TCNT1 == OCR1A (p.136)
  TIMSK1 |= _BV(OCIE1A); // Enable Timer1 Compare A Match interrupt

  sei(); // Re-enable interrupts

  // Timer 2 handles audio output via PWM on pin 11
  // Timer 1 runs bytebeat calculations with an interrupt at the sample rate
}

///////////////////////////////////////////////////////////////
// SETUP! /////////////////////////////////////////////////////

// Initialize pins and serial, and initialize audio output
void setup() {
  pinMode(ledPin, OUTPUT);      // On-board LED
  pinMode(progBit0Pin, OUTPUT); // Program bit 0
  pinMode(progBit1Pin, OUTPUT); // Program bit 1
  pinMode(progBit2Pin, OUTPUT); // Program bit 2
  pinMode(progBit3Pin, OUTPUT); // Program bit 3

  pinMode(upButtonPin, INPUT_PULLUP);   // Use internal pull-up resistor
  pinMode(modeButtonPin, INPUT_PULLUP); // Use internal pull-up resistor
  pinMode(downButtonPin, INPUT_PULLUP); // Use internal pull-up resistor

  // Pin-change interrupt on D2, D3, D4 (PCINT18-20, group PCINT2)
  btnLastPins = PIND & BTN_MASK;
  PCMSK2 |= _BV(PCINT18) | _BV(PCINT19) | _BV(PCINT20);
  PCIFR  |= _BV(PCIF2);  // clear any pending flag
  PCICR  |= _BV(PCIE2);  // enable the group

  initSound();  // Initialize audio output
  ledCounter(); // Update LEDs to show initial program number

  // Initialize serial for debugging
  if (isDebugging) {
    Serial.begin(9600);
  }
}

///////////////////////////////////////////////////////////////
// LOOP! //////////////////////////////////////////////////////

// Main loop
// Note: audio is handled in the interrupt service routine (ISR(TIMER1_COMPA_vect) below)
void loop() {
  buttonsManager(); // Check buttons and update program number
  potsManager();    // Read pots and update a, b, c, and sample rate

  // slow loop show serial once every second
  if (isDebugging) {
    if (millis() > time_now + 1000) {
      time_now = millis();
      printValues();
    }
  }
}

///////////////////////////////////////////////////////////////
// Handle Pots ////////////////////////////////////////////////

// Helper function to scale parameters
// Scale analog input (0-1023) to a value between minVal and maxVal
// returns a uint 8 (0-255)
uint8_t scaleParam(int analogValue, uint8_t minVal, uint8_t maxVal) {
  return map(analogValue, 0, 1023, minVal, maxVal);
}

// Read a pot twice and keep the second reading: right after switching channels the ADC's
// sample capacitor still holds the previous pot's voltage, which pulls the first reading toward it.
int readPot(uint8_t pin) {
  analogRead(pin);
  return analogRead(pin);
}

// Read pots and update a, b, c, and sample rate
void potsManager() {
  // Get Pots for vars a, b, and c
  int analogA = readPot(A0); // A0 pin 19
  int analogB = readPot(A1); // A1 pin 20
  int analogC = readPot(A2); // A2 pin 21

  // Scale vars a, b, and c, by the ranges for each equation
  a = scaleParam(analogA, equations[programNumber].aMin, equations[programNumber].aMax);
  b = scaleParam(analogB, equations[programNumber].bMin, equations[programNumber].bMax);
  c = scaleParam(analogC, equations[programNumber].cMin, equations[programNumber].cMax);

  // Sample rate uses a unit 16, can't use scaleParam here!
  // Only update when RATE moves by more than 2 counts: ADC noise otherwise wobbles the pitch, and
  // rewriting OCR1A below the running counter makes Timer 1 miss a compare (a short dropout).
  int r = readPot(A3);
  if (abs(r - rateRaw) > 2) {
    rateRaw = r;
    SAMPLE_RATE = map(r, 0, 1023, 256, 32000);
    uint16_t top = F_CPU / SAMPLE_RATE;
    cli();
    OCR1A = top;                    // Update Timer1 compare register (the ISR raises it again if it's too fast)
    isrCycles = 0;                  // re-measure from here
    if (TCNT1 >= top) TCNT1 = 0;     // don't let the counter run past the new compare value
    sei();
  }
}

///////////////////////////////////////////////////////////////
// Update LEDs ////////////////////////////////////////////////

// Helper function to update the 4 LEDs
// Update the 4 LEDs to show the current program number in binary
void ledCounter() {
  digitalWrite(progBit0Pin, bitRead(programNumber, 0));
  digitalWrite(progBit1Pin, bitRead(programNumber, 1));
  digitalWrite(progBit2Pin, bitRead(programNumber, 2));
  digitalWrite(progBit3Pin, bitRead(programNumber, 3));
}

///////////////////////////////////////////////////////////////
// For Debugging //////////////////////////////////////////////

// Helper function for debugging.
// Print current program number and parameters a, b, c to serial
void printValues() {
  Serial.print("program: ");
  Serial.print(programNumber);
  Serial.print("  a: ");
  Serial.print(a);
  Serial.print("  b: ");
  Serial.print(b);
  Serial.print("  c: ");
  Serial.println(c);

  Serial.print(" Rate: ");
  Serial.println(SAMPLE_RATE, DEC);
}

///////////////////////////////////////////////////////////////
// Interrupt Timer generates audio ////////////////////////////

// Get the Number of equations
const uint8_t NUM_EQUATIONS = sizeof(equations) / sizeof(equations[0]);
#define totalPrograms NUM_EQUATIONS

// Timer1 Compare A interrupt service routine
// This generates audio samples from bytebeat equations
ISR(TIMER1_COMPA_vect) {
  if (programNumber >= NUM_EQUATIONS) programNumber = 0; // Reset to first equation if out of bounds
  value = equations[programNumber].func(t, a, b, c); // Compute next sample value
  OCR2A = value; // Update PWM duty cycle for audio output
  t++; // Increment time variable

  // CPU guard (see isrCycles). In CTC mode TCNT1 restarted at this compare match, so it now holds the cycles used
  // (plus entry latency). If the next match already happened (overrun), OCF1A is set again and TCNT1 has wrapped.
  uint16_t used = TCNT1;
  if (TIFR1 & _BV(OCF1A)) used += OCR1A;
  if (used > isrCycles) isrCycles = used;
  uint16_t minTop = isrCycles + (isrCycles >> 1) + 200; // leave >= 1/3 of the CPU for loop()
  if (OCR1A < minTop) OCR1A = minTop;
}

///////////////////////////////////////////////////////////////
// Button Manager /////////////////////////////////////////////

// MODE (BTN 3, centre): restart the current equation from t = 0.
// Give it another job here (e.g. a second page of parameters, freeze, or a random program).
void modeButtonPressed() {
  cli();
  t = 0; // t is a long shared with the ISR: change it with interrupts off
  sei();
}

// Pin-change ISR: a press (HIGH -> LOW) counts only if that pin had been quiet for debounceMs,
// so contact bounce on press or release is ignored. It has priority over the audio timer interrupt.
ISR(PCINT2_vect) {
  uint8_t pins = PIND & BTN_MASK;
  uint8_t changed = pins ^ btnLastPins;
  unsigned long now = millis();
  for (uint8_t bit = 2; bit <= 4; bit++) {
    uint8_t m = _BV(bit);
    if (changed & m) {
      if (!(pins & m) && now - btnLastEdge[bit] > debounceMs) btnPressed |= m; // pressed (active LOW)
      btnLastEdge[bit] = now;
    }
  }
  btnLastPins = pins;
}

// Act on the presses latched by the ISR (on press, not release: more responsive)
void buttonsManager() {
  cli();
  uint8_t p = btnPressed;
  btnPressed = 0;
  sei();

  // Up button (BTN 1, D2)
  if (p & BTN_UP) {
    programNumber++;                                       // Increment program number
    if (programNumber >= totalPrograms) programNumber = 0; // Wrap around (was '>', which allowed one too many)
    ledCounter();                                          // Update LEDs to show new program number
    rateRaw = -100;                                        // re-apply RATE: the new equation has its own CPU cost
  }

  // Down button (BTN 2, D4)
  if (p & BTN_DOWN) {
    // Decrement program number with wrap-around
    if (programNumber > 0) {
      programNumber--;
    } else {
      programNumber = totalPrograms - 1; // Wrap around to last program
    }
    ledCounter(); // Update LEDs to show new program number
    rateRaw = -100; // re-apply RATE: the new equation has its own CPU cost
  }

  // MODE button (BTN 3, D3)
  if (p & BTN_MODE) {
    modeButtonPressed();
  }
}
