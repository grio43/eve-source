#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\marqueeCont.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.themeColored import FrameThemeColored, FillThemeColored
import carbonui.const as uiconst
import uthread
import blue
from carbonui.uicore import uicore

class MarqueeCont(Container):
    default_name = 'MarqueeCont'
    default_align = uiconst.TOPLEFT
    default_callback = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.parentScale = attributes.parentScale or 1.0
        parLeft, parTop = self.parent.GetAbsolutePosition()
        self.x0 = uicore.uilib.x - parLeft
        self.y0 = uicore.uilib.y - parTop
        FrameThemeColored(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER3, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.5)
        FillThemeColored(parent=self, frameConst=uiconst.FRAME_FILLED_CORNER3, opacity=0.15)
        uthread.new(self.UpdateThread)

    def UpdateThread(self):
        while not self.destroyed:
            x = uicore.uilib.x
            y = uicore.uilib.y
            parLeft, parTop = self.parent.GetAbsolutePosition()
            if x > self.x0 + parLeft:
                self.left = self.x0
                self.width = x - self.left - parLeft
            else:
                self.left = x - parLeft
                self.width = self.x0 - x + parLeft
            self.left = self.left / self.parentScale
            self.width = self.width / self.parentScale
            if y > self.y0 + parTop:
                self.top = self.y0
                self.height = y - self.top - parTop
            else:
                self.top = y - parTop
                self.height = self.y0 - y + parTop
            self.top = self.top / self.parentScale
            self.height = self.height / self.parentScale
            blue.synchro.Yield()

    def GetCenterPoint(self):
        left, top = self.GetAbsolutePosition()
        x = left + self.width / 2
        y = top + self.height / 2
        return (x, y)
