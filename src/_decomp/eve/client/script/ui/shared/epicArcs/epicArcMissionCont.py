#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\epicArcs\epicArcMissionCont.py
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.shared.epicArcs import epicArcConst
import blue

class EpicArcMissionCont(Container):
    default_name = 'EpicArcMissionCont'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.missionNode = attributes.missionNode
        iconSize = attributes.iconSize
        self.icon = Sprite(name='icon', parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTER, pos=(0,
         0,
         iconSize,
         iconSize))
        self.glowSprite = GlowSprite(name='glowSprite', parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTER, pos=(0,
         0,
         iconSize,
         iconSize), glowAmount=0.0)
        self.UpdateIcon()

    def UpdateIcon(self):
        missionState = self.missionNode.GetState()
        texturePath = self._GetTexturePath(missionState)
        color = self._GetIconColor(missionState)
        self.icon.texturePath = texturePath
        self.icon.SetRGBA(*color)
        self.glowSprite.texturePath = texturePath
        self.glowSprite.SetRGBA(*color)

    def OnMouseEnter(self, *args):
        if self.missionNode.GetState() != epicArcConst.MISSION_UNAVAILABLE:
            self.glowSprite.OnMouseEnter()

    def OnMouseExit(self, *args):
        self.glowSprite.OnMouseExit()

    def _GetIconColor(self, missionState):
        if missionState in (epicArcConst.MISSION_ACCEPTED, epicArcConst.MISSION_OFFERED):
            return epicArcConst.COLOR_ACTIVE
        if missionState == epicArcConst.MISSION_UNAVAILABLE:
            return Color.GRAY6
        if missionState == epicArcConst.MISSION_COMPLETED:
            if self.missionNode.IsLastInChapter():
                return epicArcConst.COLOR_CHAPTER_COMPLETE
            else:
                return epicArcConst.COLOR_COMPLETE

    def _GetTexturePath(self, missionState):
        if self.missionNode.IsLastInArc():
            texturePath = self._GetTexturePathLastInArc(missionState)
        elif self.missionNode.IsLastInChapter():
            texturePath = self._GetTexturePathLastInChapter(missionState)
        else:
            texturePath = self._GetTexturePathNormal(missionState)
        return texturePath

    def _GetTexturePathLastInChapter(self, missionState):
        if missionState == epicArcConst.MISSION_UNAVAILABLE:
            return 'res:/UI/Texture/Classes/EpicArcBar/chapter_inactiveMission.png'
        if missionState == epicArcConst.MISSION_OFFERED:
            return 'res:/UI/Texture/Classes/EpicArcBar/mission_Pending.png'
        if missionState == epicArcConst.MISSION_ACCEPTED:
            return 'res:/UI/Texture/Classes/EpicArcBar/chapter_activeMission.png'
        if missionState == epicArcConst.MISSION_COMPLETED:
            return 'res:/UI/Texture/Classes/EpicArcBar/chapter_completedMission.png'

    def _GetTexturePathLastInArc(self, missionState):
        if missionState == epicArcConst.MISSION_UNAVAILABLE:
            return 'res:/UI/Texture/Classes/EpicArcBar/epicArc_inactive.png'
        if missionState == epicArcConst.MISSION_OFFERED:
            return 'res:/UI/Texture/Classes/EpicArcBar/mission_Pending.png'
        if missionState == epicArcConst.MISSION_ACCEPTED:
            return 'res:/UI/Texture/Classes/EpicArcBar/epicArc_active.png'
        if missionState == epicArcConst.MISSION_COMPLETED:
            return 'res:/UI/Texture/Classes/EpicArcBar/epicArc_complete.png'

    def _GetTexturePathNormal(self, missionState):
        if missionState == epicArcConst.MISSION_UNAVAILABLE:
            return 'res:/UI/Texture/Classes/EpicArcBar/mission_Inactive.png'
        if missionState == epicArcConst.MISSION_OFFERED:
            return 'res:/UI/Texture/Classes/EpicArcBar/mission_Pending.png'
        if missionState == epicArcConst.MISSION_ACCEPTED:
            return 'res:/UI/Texture/Classes/EpicArcBar/mission_Active.png'
        if missionState == epicArcConst.MISSION_COMPLETED:
            return 'res:/UI/Texture/Classes/EpicArcBar/mission_Complete.png'

    def GetHint(self):
        self.missionNode.GetHint()

    def GetMenu(self):
        if session.role & ROLE_PROGRAMMER:
            return [('missionID: %s' % self.missionNode.missionID, blue.pyos.SetClipboardData, (str(self.missionNode.missionID),)), (self.missionNode.GetInProgressText(), lambda : None, [])]
