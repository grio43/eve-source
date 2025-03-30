#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\isk.py
import eveui
from eve.common.script.util.eveFormat import FmtISK, FmtISKAndRound
from .attribute import AttributeColumn

class ISKColumn(AttributeColumn):

    def __init__(self, round = False, show_fractions = False, **kwargs):
        kwargs.setdefault('align', eveui.Align.center_right)
        super(ISKColumn, self).__init__(**kwargs)
        self.round = round
        self.show_fractions = show_fractions

    def get_text(self, entry):
        value = self.get_value(entry)
        if self.round:
            return FmtISKAndRound(value, self.show_fractions)
        else:
            return FmtISK(value, self.show_fractions)
