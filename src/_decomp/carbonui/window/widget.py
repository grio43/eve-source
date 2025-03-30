#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\widget.py
from carbonui.control.window import Window
from carbonui.window.header.small import SmallWindowHeader

class WidgetWindow(Window):
    default_isLightBackground = True
    default_isCompactable = True

    def Prepare_Header_(self):
        self._SetHeader(SmallWindowHeader())
