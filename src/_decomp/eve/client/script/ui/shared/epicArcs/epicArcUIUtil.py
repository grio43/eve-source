#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\epicArcs\epicArcUIUtil.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.epicArcs import epicArcConst

def GetLineColor(isComplete):
    if isComplete:
        return Color(*epicArcConst.COLOR_COMPLETE).SetAlpha(0.3).GetRGBA()
    else:
        return (0.5, 0.5, 0.5, 0.1)
