"""GlitchStorm v3 board for a Hammond 1590BB (landscape), pedal-style: pots/buttons/LEDs on the FACE side (B),
Nano + jacks + SMD on the INSIDE (F). Jacks open at the back edge, Nano USB at the side wall. Bare-PCB: 4x M3 standoff holes.
usage: buildpcb_gs3.py <netlist> <out.kicad_pcb> <projdir>"""
import pcbnew, re, sys, os, math
NET, OUT, PROJ = sys.argv[1:4]
FPD = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'
PDLIB = os.path.expanduser('~/Documents/KiCad/10.0/footprints/2025_PedalDivision_Enclosures.pretty')
mm = pcbnew.FromMM; tm = pcbnew.ToMM
CX, CY = 150.0, 100.0                              # enclosure centre
X0, X1, Y0, Y1 = CX - 53, CX + 46.8, CY - 41, CY + 39   # board 99.8 x 80 (JLC 100 x 100 price break)
N = 6.0                                            # corner notch for the screw bosses
OUTLINE = [(X0 + N, Y0), (X1 - N, Y0), (X1 - N, Y0 + N), (X1, Y0 + N), (X1, Y1 - N), (X1 - N, Y1 - N), (X1 - N, Y1),
           (X0 + N, Y1), (X0 + N, Y1 - N), (X0, Y1 - N), (X0, Y0 + N), (X0 + N, Y0 + N)]
def sx(txt):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', txt); st = [[]]
    for t in toks:
        if t == '(': st.append([])
        elif t == ')': x = st.pop(); st[-1].append(x)
        else: st[-1].append(t[1:-1] if t[0] == '"' else t)
    return st[0][0]
def get(l, k):
    for x in l:
        if isinstance(x, list) and x and x[0] == k: return x
def all_(l, k): return [x for x in l if isinstance(x, list) and x and x[0] == k]
T = sx(open(NET).read())
comps = {}
for c in all_(get(T, 'components'), 'comp'):
    f = {fl[1][1]: (fl[2] if len(fl) > 2 else '') for fl in all_(get(c, 'fields') or [], 'field')}
    comps[get(c, 'ref')[1]] = dict(value=get(c, 'value')[1], fp=get(c, 'footprint')[1], fields=f, uuids=get(c, 'tstamps')[1:])
nets = {get(n, 'name')[1]: [(get(x, 'ref')[1], get(x, 'pin')[1]) for x in all_(n, 'node')] for n in all_(get(T, 'nets'), 'net')}
POWER = {'GND', '+5V', '/5V_A', '/VIN', '/VBIAS'}
def libpath(lib): return os.path.join(PROJ, lib + '.pretty') if lib in ('UglyFace', 'SuperFreq') else os.path.join(FPD, lib + '.pretty')
b = pcbnew.NewBoard(OUT)
netobj = {}
for n in nets:
    ni = pcbnew.NETINFO_ITEM(b, n); b.Add(ni); netobj[n] = ni
pad2net = {(r, p): n for n, nodes in nets.items() for r, p in nodes}
HAND = {'A1', 'J1', 'J2', 'J3', 'RV1', 'RV2', 'RV3', 'RV4', 'RV5', 'SW1', 'SW2', 'D1', 'D2', 'D3', 'D4', 'C16'}
FP = {}
for ref, c in comps.items():
    lib, name = c['fp'].split(':')
    fp = pcbnew.FootprintLoad(libpath(lib), name); assert fp is not None, c['fp']
    fp.SetFPID(pcbnew.LIB_ID(lib, name)); fp.SetReference(ref); fp.SetValue(c['value'])
    fp.SetPath(pcbnew.KIID_PATH('/' + c['uuids'][0])); fp.SetSheetname('/'); fp.SetSheetfile('GlitchStorm3.kicad_sch')
    for k, v in c['fields'].items():
        if k not in ('Footprint', 'Datasheet'): fp.SetField(k, v.replace('\\"', '"'))
    if ref in HAND: fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    for f_ in fp.GetFields():
        if f_.GetName() != 'Reference': f_.SetVisible(False)
    for it in list(fp.GraphicalItems()):
        if it.GetLayer() == pcbnew.Edge_Cuts: it.SetLayer(pcbnew.F_Fab)   # e.g. the SJ1-3523N 'PCB edge' marker
    b.Add(fp); FP[ref] = fp
    for pad in fp.Pads():
        n = pad2net.get((ref, pad.GetNumber()))
        if n: pad.SetNet(netobj[n])
def put(ref, x, y, rot=0, back=False):
    fp = FP[ref]
    if back and not fp.IsFlipped(): fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    fp.SetOrientationDegrees(rot); fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
def crt(fp):
    xs, ys = [], []
    for it in fp.GraphicalItems():
        if it.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            bb = it.GetBoundingBox(); xs += [tm(bb.GetLeft()), tm(bb.GetRight())]; ys += [tm(bb.GetTop()), tm(bb.GetBottom())]
    if not xs:
        bb = fp.GetBoundingBox(False); return (tm(bb.GetLeft()), tm(bb.GetTop()), tm(bb.GetRight()), tm(bb.GetBottom()))
    return (min(xs), min(ys), max(xs), max(ys))
def padc(ref):
    ps = [p.GetPosition() for p in FP[ref].Pads()]
    return sum(tm(p.x) for p in ps) / len(ps), sum(tm(p.y) for p in ps) / len(ps)
def put_centre(ref, x, y, rot=0, back=False):
    put(ref, x, y, rot, back); cx, cy = padc(ref); put(ref, 2 * x - cx, 2 * y - cy, rot, back)
def put_edge(ref, x, top, rot):
    """place with rotation rot, courtyard top edge at y = top, courtyard centred on x"""
    put(ref, x, top, rot); c = crt(FP[ref]); p = FP[ref].GetPosition()
    put(ref, tm(p.x) + x - (c[0] + c[2]) / 2, tm(p.y) + top - c[1], rot)
# outline + enclosure reference
for i in range(len(OUTLINE)):
    a, c = OUTLINE[i], OUTLINE[(i + 1) % len(OUTLINE)]
    s_ = pcbnew.PCB_SHAPE(b); s_.SetShape(pcbnew.SHAPE_T_SEGMENT); s_.SetLayer(pcbnew.Edge_Cuts)
    s_.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1]))); s_.SetEnd(pcbnew.VECTOR2I(mm(c[0]), mm(c[1]))); s_.SetWidth(mm(0.1)); b.Add(s_)
enc = pcbnew.FootprintLoad(PDLIB, 'Hammond_1590BB')
if enc:
    enc.SetReference('ENC1'); enc.SetValue('Hammond_1590BB'); enc.SetAttributes(pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    for m in list(enc.Models()): pass
    b.Add(enc); enc.SetOrientationDegrees(90); enc.SetPosition(pcbnew.VECTOR2I(mm(CX), mm(CY)))
# ---- face side (outside view = mirror of this F view). Outside: top row POT1 POT2 POT3, bottom row RATE  SW1 SW2  VOLUME, LEDs between rows
PIN = 14.605
placed = set()
for ref, x, sh in (('RV1', CX + 30, CY - 8), ('RV2', CX, CY - 8), ('RV3', CX - 30, CY - 8), ('RV4', CX + 30, CY + 22), ('RV5', CX - 30, CY + 22)):
    put(ref, x, sh + PIN, 0); placed.add(ref)
put_centre('SW1', CX + 11, CY + 22, 0, back=True); put_centre('SW2', CX - 11, CY + 22, 0, back=True); placed |= {'SW1', 'SW2'}
for ref, x in (('D1', CX + 20), ('D2', CX + 12), ('D3', CX - 12), ('D4', CX - 20)):
    put_centre(ref, x, CY + 8, 0, back=True); placed.add(ref)
# ---- inside: Nano along the back edge, USB at the side wall (F-view left = outside right); jacks at the back edge
for rot in (90, 270):
    put('A1', CX, CY, rot); c = crt(FP['A1']); p1 = [pp for pp in FP['A1'].Pads() if pp.GetNumber() == '1'][0].GetPosition()
    if tm(p1.x) - c[0] > c[2] - tm(p1.x): break          # USB (far from pin 1) points to -x
put('A1', CX, CY, rot); c = crt(FP['A1']); p = FP['A1'].GetPosition()
put('A1', tm(p.x) + (X0 + 0.3) - c[0], tm(p.y) + (CY - 26) - (c[1] + c[3]) / 2, rot); placed.add('A1')
put_edge('J1', CX + 7, Y0 - 0.5, 180)     # PHONES  (SJ1-3523N opens toward +y -> rot 180)
put_edge('J2', CX + 21, Y0 - 0.5, 270)    # LINE    (SJ1-3513N opens toward -x -> rot 270)
put_edge('J3', CX + 34.5, Y0 - 0.5, 180)    # DC      (PJ-102AH opens toward +y -> rot 180)
placed |= {'J1', 'J2', 'J3'}
HOLES = [(CX - 46, CY - 10), (CX + 43, CY - 10), (CX - 46, CY + 32), (CX + 43, CY + 32)]
for i, (x, y) in enumerate(HOLES):
    h = pcbnew.FootprintLoad(FPD + '/MountingHole.pretty', 'MountingHole_3.2mm_M3')
    h.SetReference(f'H{i + 1}'); h.SetAttributes(pcbnew.FP_BOARD_ONLY | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    b.Add(h); h.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
FIX = {'U3': (CX + 9, CY - 6, 0), 'U2': (CX + 26, CY - 6, 0), 'D5': (CX + 34.5, CY - 18, 90), 'C16': (CX, CY + 27, 0)}
for ref, (x, y, r) in FIX.items(): put(ref, x, y, r); placed.add(ref)
# ---- obstacles and greedy placement of the SMD parts (inside)
occ = []
for ref in placed:
    fp = FP[ref]
    if ref.startswith(('RV', 'SW', 'D')) and ref not in ('D5',):
        for pad in fp.Pads():
            bb = pad.GetBoundingBox(); i = 0.5
            occ.append((tm(bb.GetLeft()) - i, tm(bb.GetTop()) - i, tm(bb.GetRight()) + i, tm(bb.GetBottom()) + i))
        continue
    x0, y0, x1, y1 = crt(fp); occ.append((x0 - .2, y0 - .2, x1 + .2, y1 + .2))
for x, y in HOLES: occ.append((x - 3.6, y - 3.6, x + 3.6, y + 3.6))
def inside(bx):
    x0, y0, x1, y1 = bx
    if x0 < X0 + 0.6 or y0 < Y0 + 0.6 or x1 > X1 - 0.6 or y1 > Y1 - 0.6: return False
    for (cxn, cyn) in ((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1)):
        nx0, nx1 = (X0, X0 + N + 0.6) if cxn == X0 else (X1 - N - 0.6, X1)
        ny0, ny1 = (Y0, Y0 + N + 0.6) if cyn == Y0 else (Y1 - N - 0.6, Y1)
        if x0 < nx1 and x1 > nx0 and y0 < ny1 and y1 > ny0: return False
    return True
def free(bx): return inside(bx) and all(not (bx[0] < a[2] and bx[2] > a[0] and bx[1] < a[3] and bx[3] > a[1]) for a in occ)
refnets = {}
for n, nodes in nets.items():
    for r, p in nodes: refnets.setdefault(r, []).append((n, p))
DEC = {'C19': ('U2', '8'), 'C13': ('U3', '6'), 'C12': ('U3', '6'), 'C14': ('U3', '7'), 'C1': ('A1', '19'), 'C2': ('A1', '20'), 'C3': ('A1', '21'), 'C4': ('A1', '22')}
def padxy(ref, num):
    for p in FP[ref].Pads():
        if p.GetNumber() == num: q = p.GetPosition(); return tm(q.x), tm(q.y)
def target(ref):
    if ref in DEC: return padxy(*DEC[ref]), 50
    pts_ = []
    for n, _ in refnets.get(ref, []):
        if n in POWER: continue
        for r, p in nets[n]:
            if r != ref and r in placed: pts_.append(padxy(r, p))
    if not pts_: return None, 0
    return (sum(p[0] for p in pts_) / len(pts_), sum(p[1] for p in pts_) / len(pts_)), len(pts_)
todo = [r for r in comps if r not in placed]
report = []
while todo:
    best = max(todo, key=lambda r: (target(r)[1], r))
    tgt, k = target(best)
    if tgt is None: tgt = (CX, CY + 10)
    fp = FP[best]; done = False
    for rad in [i * 0.25 for i in range(0, 240)]:
        steps = max(1, int(2 * math.pi * rad / 0.4)) if rad else 1
        for sidx in range(steps):
            ang = 2 * math.pi * sidx / steps
            x = round((tgt[0] + rad * math.cos(ang)) * 4) / 4; y = round((tgt[1] + rad * math.sin(ang)) * 4) / 4
            for rot in (0, 90):
                put(best, x, y, rot)
                bx = crt(fp); bx = (bx[0] - 0.2, bx[1] - 0.2, bx[2] + 0.2, bx[3] + 0.2)
                if free(bx): occ.append(bx); done = True; break
            if done: break
        if done: break
    if not done: report.append(best)
    placed.add(best); todo.remove(best)
pcbnew.SaveBoard(OUT, b)
print('saved', len(comps), 'parts; unplaced:', report)
