#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\volume.py
import eveui
from eve.common.script.util.eveFormat import FmtISK, FmtISKAndRound
from .attribute import AttributeColumn

class VolumeColumn(AttributeColumn):

    def __init__(self, **kwargs):
        super(VolumeColumn, self).__init__(**kwargs)

    def get_text(self, entry):
        value = self.get_value(entry)
