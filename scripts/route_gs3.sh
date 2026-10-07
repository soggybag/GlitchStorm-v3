# Freeroute the GlitchStorm v3 board (outline inset 0.3 mm), add GND pours both sides, DRC.  Work dir: $1 (no spaces)
N="$HOME/Documents/KiCad/projects/GlitchStorm v3"; D=${1:?work dir}
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3; K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
J=~/Documents/KiCad/8.0/3rdparty/plugins/app_freerouting_kicad-plugin/jar/freerouting-1.9.0.jar
mkdir -p $D/rt; cp "$N/GlitchStorm3.kicad_pcb" $D/rt/tmp.kicad_pcb; cp $D/golden.kicad_pro $D/rt/tmp.kicad_pro; cp "$N/GlitchStorm3.kicad_dru" $D/rt/tmp.kicad_dru; cd $D/rt
$PY - 2>/dev/null <<'P'
import pcbnew
mm = pcbnew.FromMM
b = pcbnew.LoadBoard('tmp.kicad_pcb')
ds = list(b.GetDrawings()); tr = list(b.GetTracks()); zs = list(b.Zones()); fps = list(b.GetFootprints())
for d in ds:
    if d.GetLayerName() == 'Edge.Cuts': b.Remove(d)
for t in tr: b.Remove(t)
for z in zs: b.Remove(z)
for f in fps:
    if f.GetReference() == 'ENC1': b.Remove(f)
CX, CY = 150.0, 100.0; X0, X1, Y0, Y1 = CX - 53 + .3, CX + 46.8 - .3, CY - 41 + .3, CY + 39 - .3; N = 6.0
pts = [(X0 + N, Y0), (X1 - N, Y0), (X1 - N, Y0 + N), (X1, Y0 + N), (X1, Y1 - N), (X1 - N, Y1 - N), (X1 - N, Y1), (X0 + N, Y1), (X0 + N, Y1 - N), (X0, Y1 - N), (X0, Y0 + N), (X0 + N, Y0 + N)]
for i in range(len(pts)):
    a, c = pts[i], pts[(i + 1) % len(pts)]
    s_ = pcbnew.PCB_SHAPE(b); s_.SetShape(pcbnew.SHAPE_T_SEGMENT); s_.SetLayer(pcbnew.Edge_Cuts)
    s_.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1]))); s_.SetEnd(pcbnew.VECTOR2I(mm(c[0]), mm(c[1]))); s_.SetWidth(mm(0.05)); b.Add(s_)
pcbnew.SaveBoard('tmp.kicad_pcb', b)
b = pcbnew.LoadBoard('tmp.kicad_pcb'); print('dsn', pcbnew.ExportSpecctraDSN(b, 'gs3.dsn'))
P
rm -f gs3.ses; java -jar $J -de gs3.dsn -do gs3.ses -mp 400 -mt 1 > fr.log 2>&1
cd "$N"; $PY - $D 2>/dev/null <<'P'
import pcbnew, sys
D = sys.argv[1]; mm = pcbnew.FromMM
s = pcbnew.LoadBoard(D + '/rt/tmp.kicad_pcb'); print('ses', pcbnew.ImportSpecctraSES(s, D + '/rt/gs3.ses'))
b = pcbnew.LoadBoard('GlitchStorm3.kicad_pcb'); nets = b.GetNetsByName(); n = 0
for t in list(b.GetTracks()): b.Remove(t)
for z in list(b.Zones()): b.Remove(z)
for t in list(s.GetTracks()):
    if t.GetClass() == 'PCB_VIA':
        v = pcbnew.PCB_VIA(b); v.SetPosition(t.GetPosition()); v.SetWidth(t.GetWidth(pcbnew.F_Cu)); v.SetDrill(t.GetDrill()); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); nt = v
    else:
        nt = pcbnew.PCB_TRACK(b); nt.SetStart(t.GetStart()); nt.SetEnd(t.GetEnd()); nt.SetWidth(t.GetWidth()); nt.SetLayer(t.GetLayer())
    nt.SetNet(nets[t.GetNetname()]); b.Add(nt); n += 1
CX, CY = 150.0, 100.0; X0, X1, Y0, Y1 = CX - 53, CX + 46.8, CY - 41, CY + 39
for L, nm in ((pcbnew.F_Cu, 'F'), (pcbnew.B_Cu, 'B')):
    z = pcbnew.ZONE(b); z.SetLayer(L); z.SetNet(nets['GND']); ol = z.Outline(); ol.NewOutline()
    for x, y in ((X0 - .5, Y0 - .5), (X1 + .5, Y0 - .5), (X1 + .5, Y1 + .5), (X0 - .5, Y1 + .5)): ol.Append(mm(x), mm(y))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25)); z.SetThermalReliefGap(mm(0.4)); z.SetThermalReliefSpokeWidth(mm(0.4))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS); z.SetZoneName('GND_' + nm); b.Add(z)
pcbnew.SaveBoard('GlitchStorm3.kicad_pcb', b); print('tracks', n)
P
cp $D/golden.kicad_pro "$N/GlitchStorm3.kicad_pro"
$K pcb drc --schematic-parity --refill-zones --save-board -o $D/r.rpt "$N/GlitchStorm3.kicad_pcb" 2>&1 | grep -i "parity\|unconn"
cp $D/golden.kicad_pro "$N/GlitchStorm3.kicad_pro"
grep -E "^\[" $D/r.rpt | sed 's/:.*//' | sort | uniq -c
