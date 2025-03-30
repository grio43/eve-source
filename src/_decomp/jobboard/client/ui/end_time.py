#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\end_time.py
import eveicon
import eveui
import carbonui
from eveui import Sprite
from localization import GetByLabel
from localization.formatters import FormatDateTime

class EndTime(eveui.ContainerAutoSize):
    default_align = carbonui.Align.TORIGHT
    default_alignMode = carbonui.Align.TOPLEFT

    def __init__(self, end_time, icon_size = 16, *args, **kwargs):
        super(EndTime, self).__init__(*args, **kwargs)
        Sprite(name='end_time_icon', parent=self, state=eveui.State.disabled, align=carbonui.Align.CENTERLEFT, width=icon_size, height=icon_size, texturePath=eveicon.calendar, opacity=carbonui.TextColor.DISABLED.opacity)
        expiration_label = carbonui.TextBody(parent=self, align=carbonui.Align.TOPLEFT, left=icon_size + 4, color=carbonui.TextColor.SECONDARY, text=GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/EndDate'))
        carbonui.TextBody(parent=self, align=carbonui.Align.TOPLEFT, left=icon_size + 12 + expiration_label.width, color=carbonui.TextColor.NORMAL, text=FormatDateTime(value=end_time, timeFormat='short'))
