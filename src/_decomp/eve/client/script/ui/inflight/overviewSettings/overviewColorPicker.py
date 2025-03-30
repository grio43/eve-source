#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\overviewColorPicker.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.dropdownColorPicker import DropdownColorPicker

class OverviewColorPickerCont(DropdownColorPicker):
    __guid__ = 'overviewColorPicker'
    default_numColumns = 8
    NUM_COLORS = 24

    def GetColors(self):
        return [ Color().SetHSB(h / float(self.NUM_COLORS), 0.75, 1.0).GetRGB() for h in xrange(self.NUM_COLORS) ]
