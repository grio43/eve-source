#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\epicArcs\chapterLockCont.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from eve.client.script.ui.shared.epicArcs import epicArcConst
from eve.client.script.ui.shared.epicArcs.epicArcUIUtil import GetLineColor
from localization import GetByLabel

class ChapterLockCont(Container):
    default_name = 'ChapterLockCont'
    default_width = 40
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.missionNode = None
        self.icon = Sprite(parent=self, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(0, -4, 21, 18))
        self.line = StretchSpriteHorizontal(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Classes/EpicArcBar/line.png', padding=(0, 17, 0, 18), leftEdgeSize=4, rightEdgeSize=4)

    def SetNode(self, node):
        self.missionNode = node
        if node.IsLastInArc():
            self.Hide()
        else:
            self.Show()
            self.UpdateLineColor()
            self.UpdateLockIcon(node)

    def UpdateLockIcon(self, node):
        isComplete = node.IsComplete()
        if isComplete:
            texturePath = 'res:/UI/Texture/Classes/EpicArcBar/chapter_Unlocked.png'
            color = epicArcConst.COLOR_COMPLETE
        else:
            texturePath = 'res:/UI/Texture/Classes/EpicArcBar/chapter_Locked.png'
            color = (0.5, 0.5, 0.5, 0.5)
        self.icon.SetTexturePath(texturePath)
        self.icon.SetRGBA(*color)

    def UpdateLineColor(self):
        isComplete = self.missionNode.IsComplete()
        color = GetLineColor(isComplete)
        self.line.SetRGBA(*color)

    def GetHint(self):
        if not self.missionNode.IsComplete():
            return GetByLabel('UI/Agency/FinishChapterToUnlockNext')
