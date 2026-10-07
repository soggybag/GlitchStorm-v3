"""GlitchStorm v3 - fixed version of the Eagle GlitchStorm-v2 (same Nano pin map, firmware unchanged).
Fixes: series-R 2nd-order PWM filter on D11, MCP6002 rail-to-rail buffers, separate line out, LM386 headphone amp at gain 20
with Zobel + decoupling, tip/ring fed through 10R each (mono plugs safe), filtered 5V_A for audio, 9 V input to VIN.
usage: build_gs3.py <out.kicad_sch>"""
from sch import *
import sys
OUT = sys.argv[1]
g = lambda n: round(n * 2.54, 3)
s = Sheet('GlitchStorm3', 'A3')
FR = 'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
FC = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
FC12 = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
FPOT = 'UglyFace:Potentiometer_Alpha_16mm_Vertical'
FPAD = 'Connector_Wire:SolderWire-0.5sqmm_1x01_D0.9mm_OD2.1mm'
RL = {'1k': 'C17513', '10k': 'C17414', '100k': 'C17407', '470': 'C17710', '47k': 'C17713', '2k2': 'C17520', '10': 'C17415', '4R7': 'C17675'}
CL = {'100n': 'C49678', '10n': 'C1710', '1n': 'C46653', '47n': 'C53134', '1u': 'C28323', '10u': 'C15850', '22u': 'C12891'}
W = lambda *p: s.wire(*p)
P = s.P
def GND(p): s.power('GND', p)
def V5(p): s.power('+5V', p)
def lab(n, p, side='r'): s.label(n, p, side)
def Rh(ref, v, cx, y, desc=None): s.part(ref, 'Device', 'R', v, cx, y, 90, fp=FR, lcsc=RL[v], desc=desc or f'Resistor {v} 1% 0805', text='t')
def Rv(ref, v, x, cy, side='r', desc=None): s.part(ref, 'Device', 'R', v, x, cy, 0, fp=FR, lcsc=RL[v], desc=desc or f'Resistor {v} 1% 0805', text=side)
def fpc(v): return FC12 if v == '22u' else FC
def Ch(ref, v, cx, y, desc=None): s.part(ref, 'Device', 'C', v, cx, y, 90, fp=fpc(v), lcsc=CL[v], desc=desc or f'Ceramic {v}', text='t')
def Cv(ref, v, x, cy, side='r', desc=None): s.part(ref, 'Device', 'C', v, x, cy, 0, fp=fpc(v), lcsc=CL[v], desc=desc or f'Ceramic {v}', text=side)
def POT(ref, v, name, x, y, rot=0, mirror=None, text='r'):
    if text == 'r': text = ((x + 4.445, y - 1.27), (x + 4.445, y + 1.27), 'left')
    s.part(ref, 'Device', 'R_Potentiometer', v, x, y, rot, mirror=mirror, fp=FPOT, desc=f'{name} pot, Alpha 16 mm, hand-soldered (face side)', text=text, extra={'Panel': name}, bom=False)
def PAD(ref, name, x, y):
    s.part(ref, 'Connector_Generic', 'Conn_01x01', name, x, y, 180, fp=FPAD, desc=f'Wire pad: {name}', bom=False,
           text=((x - 2.54, y - 1.27), (x - 2.54, y + 1.27), 'right'))
    return P(ref, '1')
def OPA(unit, x, y):
    s.part('U2', 'Amplifier_Operational', 'MCP6002-xSN', 'MCP6002', x, y, 0, unit=unit, fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', lcsc='C7377',
           desc='Dual rail-to-rail op-amp on 5 V (MCP6002T-I/SN)', text='ic')

# ================================================================ ARDUINO NANO + CONTROLS (pin map unchanged)
s.box('ARDUINO NANO (A1) + CONTROLS - pin map unchanged: pots A0-A3, buttons D3/D4, LEDs D7-D10, audio D11', g(3), g(5), g(88), g(76))
s.part('A1', 'MCU_Module', 'Arduino_Nano_v3.x', 'Arduino Nano', g(45), g(45), 0, fp='Module:Arduino_Nano',
       desc='Arduino Nano on female headers (socketed), hand-soldered', text=((g(51), g(33)), (g(51), g(34.5)), 'left'), bom=False)
V5(P('A1', '27')); GND(P('A1', '4')); GND(P('A1', '29'))
q = P('A1', '30'); W(q, (q[0], q[1] - g(3))); lab('VIN', (q[0], q[1] - g(3)), 'l')
for pin in ('1', '2', '3', '5', '8', '9', '15', '16', '17', '18', '23', '24', '25', '26', '28'):
    s.noconnect(P('A1', pin))
for i, (ref, name, apin, cref) in enumerate((('RV1', 'POT1', '19', 'C1'), ('RV2', 'POT2', '20', 'C2'), ('RV3', 'POT3', '21', 'C3'), ('RV4', 'RATE', '22', 'C4'))):
    xi = g(56 + 7 * i)
    POT(ref, 'B10k', name, xi, g(22), rot=270, text=((xi - g(2), g(17)), (xi - g(2), g(18.5)), 'left'))
    V5(P(ref, '3')); GND(P(ref, '1'))
    q = P('A1', apin)
    W(P(ref, '2'), (xi, g(27)), (xi, q[1]), q)
    Cv(cref, '100n', xi + g(2), g(28.5), side='r', desc=f'ADC filter on {name}'); W((xi, g(27)), (xi + g(2), g(27))); GND(P(cref, '2'))
for ref, dpin, y in (('SW1', '6', g(42)), ('SW2', '7', g(45))):
    s.part(ref, 'Switch', 'SW_Push', 'B3F-10XX', g(27), y, 180, fp='Button_Switch_THT:SW_PUSH_6mm', desc='Tactile button (INPUT_PULLUP in firmware), hand-soldered', text='t', bom=False)
    q = P('A1', dpin)
    W(q, (g(32), q[1]), (g(32), y), P(ref, '1')); W(P(ref, '2'), (g(23), y)); GND((g(23), y))
for i, (dpin, led, res) in enumerate((('10', 'D4', 'R4'), ('11', 'D3', 'R3'), ('12', 'D2', 'R2'), ('13', 'D1', 'R1'))):
    xi = g(12 + 5 * i)
    s.part(led, 'Device', 'LED', 'LED', xi, g(62), 90, fp='LED_THT:LED_D3.0mm', desc='3mm LED, hand-soldered', text='r', bom=False)
    Rv(res, '1k', xi, g(66.5), side='r', desc='LED current (~3 mA)')
    q = P('A1', dpin)
    W(q, (xi, q[1]), P(led, '2')); W(P(led, '1'), P(res, '1')); GND(P(res, '2'))
q = P('A1', '14'); W(q, (g(37), q[1])); lab('D11_PWM', (g(37), q[1]), 'l')
s.text('Pots B10k (ADC wants <10k source) with 100n at each ADC pin. LED resistors 1k.', g(5), g(74))

# ================================================================ PWM FILTER + BUFFERS + VOLUME + LINE OUT
s.box('PWM FILTER (2 x RC, ~16 kHz) + BUFFER (U2A) + VOLUME + BUFFER (U2B) + LINE OUT', g(92), g(5), g(162), g(40))
y1 = g(18)
lab('D11_PWM', (g(95), y1), 'l')
Rh('R5', '1k', g(99.5), y1, desc='PWM filter 1 (limits D11 current to 5 mA)'); W((g(95), y1), P('R5', '1'))
W(P('R5', '2'), (g(103), y1)); Cv('C5', '10n', g(103), y1 + 3.81, side='l', desc='PWM filter 1 (1k/10n = 16 kHz)'); GND(P('C5', '2'))
Rh('R6', '10k', g(106.5), y1, desc='PWM filter 2'); W((g(103), y1), P('R6', '1'))
W(P('R6', '2'), (g(110), y1)); Cv('C6', '1n', g(110), y1 + 3.81, side='l', desc='PWM filter 2 (10k/1n = 16 kHz)'); GND(P('C6', '2'))
OPA(1, g(117), y1 + g(1))
W((g(110), y1), P('U2', '3'))
W(P('U2', '2'), (g(113), y1 + g(2)), (g(113), y1 + g(5)), (g(121), y1 + g(5)), (g(121), y1 + g(1)))
W(P('U2', '1'), (g(121), y1 + g(1)), (g(122), y1 + g(1)))
Ch('C7', '10u', g(124.5), y1 + g(1), desc='DC block into VOLUME')
W((g(122), y1 + g(1)), P('C7', '1'))
POT('RV5', 'A10k', 'VOLUME', g(128), y1 + g(1) + 3.81, mirror='x', text=((g(126), y1 + g(5)), (g(126), y1 + g(6.5)), 'left'))
W(P('C7', '2'), P('RV5', '3')); GND(P('RV5', '1'))
yw = P('RV5', '2')[1]
Ch('C8', '1u', g(132.5), yw, desc='Coupling into U2B'); W(P('RV5', '2'), P('C8', '1'))
W(P('C8', '2'), (g(136), yw))
Rv('R7', '100k', g(136), yw + 3.81, side='l', desc='U2B bias to VBIAS (2.5 V)'); W(P('R7', '2'), (g(136), yw + g(3.5))); lab('VBIAS', (g(136), yw + g(3.5)), 'l')
OPA(2, g(142), yw + g(1))
W((g(136), yw), P('U2', '5'))
W(P('U2', '6'), (g(138), yw + g(2)), (g(138), yw + g(5)), (g(146), yw + g(5)), (g(146), yw + g(1)))
yl = g(32)
W(P('U2', '7'), (g(146), yw + g(1)), (g(148), yw + g(1)), (g(148), yl), (g(148), g(36)))
lab('BUF_OUT', (g(148), g(36)), 'l')
Ch('C9', '10u', g(150.5), yl, desc='Line out DC block'); W((g(148), yl), P('C9', '1'))
W(P('C9', '2'), (g(153), yl))
Rv('R9', '100k', g(153), yl + 3.81, side='l', desc='Line out DC reference (no pop)'); GND(P('R9', '2'))
Rh('R8', '470', g(155.5), yl, desc='Line out isolation (cable capacitance / short)'); W((g(153), yl), P('R8', '1'))
s.part('J2', 'Connector_Audio', 'AudioJack2', 'LINE OUT', g(160), yl, 0, mirror='y', fp='Connector_Audio:Jack_3.5mm_CUI_SJ1-3513N_Horizontal',
       desc='LINE OUT, 3.5 mm (CUI SJ1-3513N), inside side of the board, opening at the back edge, hand-soldered', text=((g(158), yl - g(4)), (g(158), yl - g(3)), None), bom=False)
W(P('R8', '2'), P('J2', 'T'))
q = P('J2', 'S'); W(q, (q[0] - g(1), q[1]), (q[0] - g(1), q[1] - g(2))); GND((q[0] - g(1), q[1] - g(2)))
s.text('Line out ~1.7 Vrms max; VOLUME sets both outputs.', g(94), g(38))

# ================================================================ HEADPHONE AMP (LM386, gain 20)
s.box('HEADPHONE AMP: LM386 (U3) gain 20, Zobel, 10R on tip AND ring (mono plugs safe)', g(92), g(43), g(162), g(76))
ya = g(58)
lab('BUF_OUT', (g(95), ya - g(1)), 'l')
Ch('C11', '1u', g(99.5), ya - g(1), desc='Headphone amp input coupling'); W((g(95), ya - g(1)), P('C11', '1'))
Rh('R12', '47k', g(105.5), ya - g(1), desc='Input pad (47k/2k2 = /22)'); W(P('C11', '2'), P('R12', '1'))
W(P('R12', '2'), (g(109), ya - g(1)))
Rv('R13', '2k2', g(109), ya - g(1) + 3.81, side='l', desc='Input pad / DC path for the LM386 input'); GND(P('R13', '2'))
s.part('U3', 'Amplifier_Audio', 'LM386', 'LM386', g(118), ya, 0, fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', lcsc='C23573',
       desc='LM386MX-1, gain 20 (pins 1/8 open), headphones', text=((g(120), ya - g(6)), (g(120), ya - g(5)), 'left'))
W((g(109), ya - g(1)), P('U3', '3'))
W(P('U3', '2'), (g(114), P('U3', '2')[1]), (g(114), ya + g(3))); GND((g(114), ya + g(3)))
GND(P('U3', '4')); s.noconnect(P('U3', '1')); s.noconnect(P('U3', '8'))
q6 = P('U3', '6'); W(q6, (q6[0], q6[1] - g(1)), (g(112), q6[1] - g(1)), (g(112), q6[1] - g(3))); lab('5V_A', (g(112), q6[1] - g(3)), 'l')
q7 = P('U3', '7'); W(q7, (q7[0], ya - g(7)), (g(126), ya - g(7)))
Cv('C14', '10u', g(126), ya - g(5.5), side='r', desc='LM386 bypass (pin 7): supply ripple rejection'); GND(P('C14', '2'))
yo = ya
W(P('U3', '5'), (g(124), yo), (g(127), yo))
Rv('R14', '10', g(124), yo + g(1.5), side='l', desc='Zobel (stops LM386 oscillation)')
Cv('C15', '47n', g(124), yo + g(4.5), side='l', desc='Zobel'); GND(P('C15', '2'))
s.part('C16', 'Device', 'C_Polarized', '220u', g(129.5), yo, 90, fp='Capacitor_THT:CP_Radial_D6.3mm_P2.50mm',
       desc='Headphone output coupling (220u into 32 ohm = 23 Hz), 10 V electrolytic, hand-soldered', text='t', bom=False)
W((g(127), yo), P('C16', '1'))
W(P('C16', '2'), (g(133), yo), (g(133), yo - g(2)), (g(133), yo + g(3)))
Rh('R16', '10', g(137.5), yo - g(2), desc='Ring feed (a mono plug shorts only this 10R)'); W((g(133), yo - g(2)), P('R16', '1'))
Rh('R15', '10', g(137.5), yo + g(3), desc='Tip feed'); W((g(133), yo + g(3)), P('R15', '1'))
s.part('J1', 'Connector_Audio', 'AudioJack3', 'PHONES', g(146), yo + g(1), 0, mirror='y', fp='Connector_Audio:Jack_3.5mm_CUI_SJ1-3523N_Horizontal',
       desc='HEADPHONES, 3.5 mm TRS (CUI SJ1-3523N), inside side of the board, opening at the back edge, hand-soldered', text=((g(146), yo - g(4)), (g(146), yo - g(3)), None), bom=False)
W(P('R16', '2'), (g(141), yo - g(2)), (g(141), P('J1', 'R')[1]), P('J1', 'R'))
W(P('R15', '2'), (g(142), yo + g(3)), (g(142), P('J1', 'T')[1]), P('J1', 'T'))
q = P('J1', 'S'); W(q, (q[0] - g(1), q[1]), (q[0] - g(1), q[1] - g(2))); GND((q[0] - g(1), q[1] - g(2)))
s.text('Pad sized so full VOLUME just reaches LM386 clipping on 5 V (~3.5 Vpp) into 32 ohm phones.', g(94), g(72))

# ================================================================ POWER
s.box('POWER: 9 V DC jack (centre negative) -> SS14 -> Nano VIN (USB also works). 5V_A = filtered +5V for audio', g(3), g(80), g(162), g(112))
ry = g(88)
s.part('J3', 'Connector', 'Barrel_Jack_Switch', 'DC 9V', g(6), ry - g(1), 0, fp='Connector_BarrelJack:BarrelJack_CUI_PJ-102AH_Horizontal',
       desc='2.1 mm DC jack, CENTRE NEGATIVE (pedal standard): pin 1 centre = GND, pin 2 sleeve = +9V; hand-soldered', text=((g(3), ry - g(5)), (g(3), ry - g(4)), 'left'), bom=False)
s.part('D5', 'Diode', 'SS14', 'SS14', g(15), ry, 180, fp='Diode_SMD:D_SMA_Handsoldering', lcsc='C2480', desc='Series polarity protection', text='t')
W(P('J3', '2'), P('D5', '2'))
q = P('J3', '1'); W(q, (g(11), q[1]), (g(11), q[1] - g(2))); GND((g(11), q[1] - g(2)));
s.noconnect(P('J3', '3'))
W(P('D5', '1'), (g(20), ry), (g(24), ry), (g(28), ry), (g(32), ry)); lab('VIN', (g(32), ry))
s.power('PWR_FLAG', (g(20), ry))
Cv('C17', '22u', g(24), ry + 3.81, desc='VIN bulk'); GND(P('C17', '2'))
s.power('PWR_FLAG', (g(11), P('J3', '1')[1]))
V5((g(44), ry)); W((g(44), ry), (g(46), ry))
Rh('R17', '4R7', g(49.5), ry, desc='Isolates audio 5V from the Nano digital 5V'); W((g(46), ry), P('R17', '1'))
W(P('R17', '2'), (g(54), ry), (g(58), ry), (g(62), ry), (g(66), ry)); lab('5V_A', (g(66), ry))
s.power('PWR_FLAG', (g(54), ry))
Cv('C18', '22u', g(58), ry + 3.81, desc='5V_A reservoir'); GND(P('C18', '2'))
Cv('C12', '22u', g(62), ry + 3.81, desc='LM386 supply - place at U3 pin 6'); GND(P('C12', '2'))
Cv('C13', '100n', g(66), ry + 3.81, desc='LM386 supply - place at U3 pin 6'); GND(P('C13', '2'))
lab('5V_A', (g(80), ry), 'l'); W((g(80), ry), (g(84), ry))
Rv('R10', '100k', g(84), ry + 3.81, desc='VBIAS divider')
Rv('R11', '100k', g(84), ry + g(6) + 3.81, desc='VBIAS divider'); GND(P('R11', '2'))
W(P('R10', '2'), P('R11', '1'))
Cv('C10', '10u', g(88), ry + g(6) + 3.81, desc='VBIAS filter'); GND(P('C10', '2'))
W((g(84), ry + g(6)), (g(88), ry + g(6)), (g(92), ry + g(6))); lab('VBIAS', (g(92), ry + g(6)))
s.part('U2', 'Amplifier_Operational', 'MCP6002-xSN', 'MCP6002', g(110), g(96), 0, unit=3, fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', lcsc='C7377', text='ic')
q = P('U2', '8'); W(q, (q[0], q[1] - g(2))); lab('5V_A', (q[0], q[1] - g(2)), 'l'); GND(P('U2', '4'))
Cv('C19', '100n', g(114), g(96), desc='U2 decoupling - place at the chip'); W(P('C19', '1'), (g(114), g(93))); lab('5V_A', (g(114), g(93)), 'r'); GND(P('C19', '2'))
s.text('Ground: audio returns (U3, jacks, filter caps) to one point at the LM386; Nano digital ground joins there.', g(5), g(108))

s.write(OUT, {'title': 'GlitchStorm v3', 'date': '2026-09-29', 'rev': '3.0 draft',
              'company': 'Super-Freq',
              'comments': ['Fixed GlitchStorm v2: same Nano pin map (firmware unchanged)',
                           'PWM filter + MCP6002 buffers, line out + LM386 headphone amp (gain 20, Zobel, 10R tip/ring)',
                           '9 V -> VIN, filtered 5V_A for audio. DRAFT']})
print('ok', len(s.syms), 'symbols')
