// GlitchStorm v3 hardware test (not the synth firmware).
// Pin map (v3): pots A0-A3 (POT1, POT2, POT3, RATE), buttons to GND (INPUT_PULLUP), left to right from outside:
//   BTN 1 = D2 (SW3), BTN 3 = D3 (SW1, centre, used as MODE), BTN 2 = D4 (SW2),
// LEDs D10 / D9 / D8 / D7 (D1-D4 on the board) via 1k, audio PWM on D11.
// BTN 3 (centre) = MODE, cycles the test:  0 = TONE   : D11 square wave, pitch from POT1 (100 Hz - 2 kHz), LED chase speed from RATE
//                               1 = DC     : D11 analogWrite from POT2 (filtered PWM -> U2 pin 1 reads 0-5 V on a meter)
//                               2 = SILENT : D11 low (check the noise floor at the jacks)
// BTN 1 (left) / BTN 2 (right) light LED 1 / LED 2 while held. Serial (115200): pot readings and mode, every 250 ms.
const uint8_t LEDS[4] = {10, 9, 8, 7};
const uint8_t BTN_MODE = 3, BTN1 = 2, BTN2 = 4, AUDIO = 11;   // MODE = centre button (D3)
uint8_t mode = 0; bool lastMode = HIGH; unsigned long tChase = 0, tPrint = 0; uint8_t chase = 0;
int toneRaw = -100;   // last A0 value the tone was set from (hysteresis)

// Read an analog pin twice and keep the second: the ADC's sample cap still holds the previous channel's
// voltage, so the first read after switching channels is pulled toward it (crosstalk from RATE into POT1).
int readPot(uint8_t ch) { analogRead(ch); return analogRead(ch); }

void setup() {
  for (uint8_t i = 0; i < 4; i++) pinMode(LEDS[i], OUTPUT);
  pinMode(BTN_MODE, INPUT_PULLUP); pinMode(BTN1, INPUT_PULLUP); pinMode(BTN2, INPUT_PULLUP);
  pinMode(AUDIO, OUTPUT);
  Serial.begin(115200);
  Serial.println(F("GlitchStorm v3 HW test. MODE: 0 tone / 1 DC / 2 silent"));
}

void loop() {
  int p[4]; for (uint8_t i = 0; i < 4; i++) p[i] = readPot(A0 + i);
  bool m = digitalRead(BTN_MODE);
  if (lastMode == HIGH && m == LOW) { mode = (mode + 1) % 3; noTone(AUDIO); digitalWrite(AUDIO, LOW); toneRaw = -100; delay(30); }
  lastMode = m;
  // Only re-start the tone when POT1 really moved: calling tone() every loop restarts the waveform each time,
  // which made low notes (periods longer than one loop) sound unstable.
  if (mode == 0) { if (abs(p[0] - toneRaw) > 3) { toneRaw = p[0]; tone(AUDIO, map(p[0], 0, 1023, 100, 2000)); } }
  else if (mode == 1) analogWrite(AUDIO, p[1] >> 2);
  else digitalWrite(AUDIO, LOW);
  // LEDs: chase in TONE mode (speed = RATE), mode number in the others; buttons override LED 1 / 2
  if (mode == 0) {
    if (millis() - tChase > (unsigned long)map(p[3], 0, 1023, 40, 600)) { tChase = millis(); chase = (chase + 1) % 4; }
    for (uint8_t i = 0; i < 4; i++) digitalWrite(LEDS[i], i == chase);
  } else {
    for (uint8_t i = 0; i < 4; i++) digitalWrite(LEDS[i], i == mode + 1);
  }
  if (digitalRead(BTN1) == LOW) digitalWrite(LEDS[0], HIGH);
  if (digitalRead(BTN2) == LOW) digitalWrite(LEDS[1], HIGH);
  if (millis() - tPrint > 250) {
    tPrint = millis();
    Serial.print(F("mode ")); Serial.print(mode);
    for (uint8_t i = 0; i < 4; i++) { Serial.print(F("  A")); Serial.print(i); Serial.print('='); Serial.print(p[i]); }
    Serial.print(F("  btn ")); Serial.print(!digitalRead(BTN_MODE)); Serial.print(!digitalRead(BTN1)); Serial.println(!digitalRead(BTN2));
  }
}
