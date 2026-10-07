"""Silkscreen for GlitchStorm v3.  finish_gs3.py <pcb>
Face side (B) = control labels (read when the bare board is used face-up).  Inside (F) = name/version + jack labels."""
import pcbnew, sys
mm = pcbnew.FromMM; tm = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
FPS = list(b.GetFootprints()); DRW = list(b.GetDrawings())
FP = {f.GetReference(): f for f in FPS}
for d in DRW:
    if d.GetClass() == 'PCB_TEXT': b.Remove(d)
for f in FPS:
    if f.GetReference() in ('ENC1',): continue
    f.Reference().SetVisible(False)
def pos(ref): p = FP[ref].GetPosition(); return tm(p.x), tm(p.y)
def padxy(ref, n):
    for p in FP[ref].Pads():
        if p.GetNumber() == n: q = p.GetPosition(); return tm(q.x), tm(q.y)
def text(s, x, y, size=1.0, bold=False, layer=pcbnew.F_SilkS, angle=0):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(layer); t.SetMirrored(layer == pcbnew.B_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(max(0.15, size * 0.15))); t.SetBold(bold)
    t.SetTextAngleDegrees(angle); t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); b.Add(t); return t
B = pcbnew.B_SilkS
for ref, name in (('RV1', 'POT 1'), ('RV2', 'POT 2'), ('RV3', 'POT 3'), ('RV4', 'RATE'), ('RV5', 'VOLUME')):
    x, y = padxy(ref, '2'); text(name, x, y + (2.4 if ref in ('RV1', 'RV2', 'RV3') else -2.4), 1.2, True, B)
for ref, name in (('SW1', 'BTN 1'), ('SW2', 'BTN 2')):
    x, y = pos(ref); c = [p.GetPosition() for p in FP[ref].Pads()]; cx = sum(tm(p.x) for p in c) / 4; cy = sum(tm(p.y) for p in c) / 4
    text(name, cx, cy + 5.2, 1.0, True, B)
for ref, name in (('J1', 'PHONES'), ('J2', 'LINE'), ('J3', '9V DC -')):
    x, y = pos(ref); c = FP[ref].GetBoundingBox(False)
    for L in (pcbnew.F_SilkS, B): text(name, (tm(c.GetLeft()) + tm(c.GetRight())) / 2, tm(c.GetBottom()) + 1.4, 1.0, True, L)
text('USB', 99.5, 74.0, 1.0, True, B, 90); text('USB', 99.5, 74.0, 1.0, True, pcbnew.F_SilkS, 90)
text('GLITCHSTORM v3', 150.0, 133.8, 1.5, True); text('SUPER-FREQ', 150.0, 136.1, 1.0)
text('GLITCHSTORM v3', 150.0, 133.8, 1.3, True, B); text('SUPER-FREQ', 150.0, 136.0, 0.9, False, B)
pcbnew.SaveBoard(sys.argv[1], b); print('ok')
