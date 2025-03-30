#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillQueuePanel\skillQueueLastDropEntry.py
from carbonui import const as uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.line import Line

class SkillQueueLastDropEntry(SE_BaseClassCore):
    __guid__ = 'SkillQueueLastDropEntry'
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.posIndicator = Line(parent=self, state=uiconst.UI_HIDDEN, align=uiconst.TOTOP, weight=2)

    def Load(self, node):
        pass

    def ShowIndicator(self, color):
        self.posIndicator.SetRGBA(*color)
        self.posIndicator.state = uiconst.UI_DISABLED

    def HideIndicator(self):
        self.posIndicator.Hide()

    def GetDynamicHeight(self, width):
        return 2
