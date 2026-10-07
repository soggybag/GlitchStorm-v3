"""STEP model of the DAIER TSL-A064 / Tayda A-8796 round tact switch, from the datasheet.
Origin = body centre on the board surface, +Z up. Pins at (+-2.5, +-2.5)."""
import sys
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString, TCollection_AsciiString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.Interface import Interface_Static
from OCP.TDataStd import TDataStd_Name

FOOT = 1.4      # standoff bumps under the body (4.7 - 3.3)
BODY = 5.9      # body height, D 12
CAP = 7.0       # cap above the body, D 9
PIN = 3.3       # pin length below the bumps

def cyl(d, z0, h):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, z0), gp_Dir(0, 0, 1)), d / 2, h).Shape()
def box(cx, cy, z0, sx, sy, sz):
    return BRepPrimAPI_MakeBox(gp_Pnt(cx - sx / 2, cy - sy / 2, z0), sx, sy, sz).Shape()
def fuse(shapes):
    s = shapes[0]
    for t in shapes[1:]:
        s = BRepAlgoAPI_Fuse(s, t).Shape()
    return s

body = fuse([cyl(12.0, FOOT, BODY), box(0, 0, 0, 3.5, 3.5, FOOT),
             box(4.2, 0, 0, 2, 2, FOOT), box(-4.2, 0, 0, 2, 2, FOOT),
             box(0, 4.2, 0, 2, 2, FOOT), box(0, -4.2, 0, 2, 2, FOOT)])
cap = cyl(9.0, FOOT + BODY, CAP)
pins = fuse([box(x, y, -PIN, 0.8, 0.3, PIN + FOOT + 0.5) for x in (-2.5, 2.5) for y in (-2.5, 2.5)])

doc = TDocStd_Document(TCollection_ExtendedString('step'))
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
asm = st.NewShape()
TDataStd_Name.Set_s(asm, TCollection_ExtendedString('SW_Push_Round_D12mm_DAIER_TSL-A064'))
for name, shp, rgb in (('body', body, (0.12, 0.12, 0.12)), ('cap', cap, (0.95, 0.95, 0.93)), ('pins', pins, (0.8, 0.8, 0.78))):
    lab = st.AddComponent(asm, shp, False)
    ref = st.AddShape(shp, False)
    TDataStd_Name.Set_s(ref, TCollection_ExtendedString(name))
    ct.SetColor(ref, Quantity_Color(*rgb, Quantity_TOC_RGB), XCAFDoc_ColorType.XCAFDoc_ColorSurf)
    ct.SetColor(lab, Quantity_Color(*rgb, Quantity_TOC_RGB), XCAFDoc_ColorType.XCAFDoc_ColorSurf)
st.UpdateAssemblies()
Interface_Static.SetCVal_s('write.step.schema', 'AP214')
w = STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True)
w.Transfer(doc, STEPControl_AsIs)
print(w.Write(sys.argv[1]))
