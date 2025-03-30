#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipTree\shipTreeShipGroup.py
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.containerAutoSize import ContainerAutoSize
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveHeaderMedium
import shipTreeConst
from eve.client.script.ui.shared.shipTree.skillLevelsCont import SkillLevelsCont
from expertSystems.client import ExpertSystemService
from shipTreeShipIcon import ShipTreeShipIcon
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.primitives.frame import Frame
from eve.client.script.ui.shared.shipTree.shipTreeConst import ZOOMED_OUT, COLOR_SHIPGROUP_UNLOCKED, COLOR_FRAME, COLOR_BG, COLOR_HOVER_LOCKED, COLOR_HOVER_UNLOCKED
import blue
from carbon.common.script.sys.service import ROLE_PROGRAMMER
from carbonui.const import ANIM_REPEAT, ANIM_WAVE
from localization import GetByMessageID
from carbonui.uicore import uicore
import expertSystems.client
OPACITY_LOCKED = 0.6

class ShipTreeShipGroup(ContainerAutoSize):
    default_name = 'ShipTreeShipGroup'
    default_iconsPerRow = 3
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_PICKCHILDREN
    default_alignMode = uiconst.TOPLEFT
    __notifyevents__ = ('OnShipTreeZoomChanged', 'OnShipTreeSkillTrained')

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.node = attributes.node
        self.factionID = self.node.factionID
        self.shipGroupID = self.node.shipGroupID
        self.name = self.GetNameForShipGroup(self.shipGroupID)
        self.iconsPerRow = self.node.GetIconsPerRow()
        self.typeIDs = sm.GetService('shipTree').GetShipTypeIDs(self.factionID, self.shipGroupID)
        self.zoomLevel = sm.GetService('shipTreeUI').GetZoomLevel()
        self.iconSize = self.node.GetIconSize()
        nodeNum = attributes.nodeNum
        self.groupNameLabel = EveHeaderMedium(name='groupNameLabel', parent=self, align=uiconst.TOPLEFT, text=GetByMessageID(cfg.infoBubbleGroups[self.shipGroupID]['nameID']), left=43, top=0)
        self.iconAndBar = ShipGroupIconAndSkillBar(parent=self, top=20, node=self.node)
        self.shipContainer = ContainerAutoSize(name='shipContainer', parent=self, align=uiconst.TOPLEFT, height=self.iconSize, left=46, top=24)
        self.LoadShips()
        self.lineTop = StretchSpriteHorizontal(name='lineTop', parent=self, align=uiconst.TOTOP, texturePath='res:/UI/Texture/Classes/ShipTree/Groups/frameUpper.png', leftEdgeSize=4, rightEdgeSize=4, height=3, padTop=16)
        width = len(self.typeIDs) % self.iconsPerRow or self.iconsPerRow
        width = self.iconSize * width + 4
        self.lineBottom = StretchSpriteHorizontal(name='lineBottom', parent=self, align=uiconst.BOTTOMLEFT, texturePath='res:/UI/Texture/Classes/ShipTree/Groups/frameLower.png', leftEdgeSize=4, rightEdgeSize=4, height=1, width=width, left=43, top=-7)
        self.UpdateState(nodeNum, animate=False)
        zoomLevel = sm.GetService('shipTreeUI').GetZoomLevel()
        if zoomLevel == ZOOMED_OUT:
            self.groupNameLabel.opacity = 0.0
            self.lineTop.opacity = 0.0
            self.lineBottom.opacity = 0.0

    def UpdateState(self, i = 0, animate = True):
        if self.zoomLevel == ZOOMED_OUT:
            opacity = 0.0
        elif self.node.IsLocked():
            opacity = OPACITY_LOCKED
        else:
            opacity = 1.0
        for uiObj in (self.groupNameLabel, self.lineTop, self.lineBottom):
            if animate:
                uicore.animations.FadeTo(uiObj, uiObj.opacity, opacity, timeOffset=0.05 * i, duration=0.6)
            else:
                uiObj.opacity = opacity

        self.iconAndBar.UpdateState(i, animate)
        for shipIcon in self.shipContainer.children:
            shipIcon.UpdateState(animate)

    def LoadShips(self):
        for i, typeID in enumerate(self.typeIDs):
            beneficialExpertSystems = []
            activeRelatedExpertSystem = False
            if not sm.GetService('skills').IsSkillRequirementMet(typeID) and expertSystems.is_expert_systems_enabled():
                associatedExpertSystems = expertSystems.get_associated_expert_systems(typeID)
                beneficialExpertSystems = [ expertSystem.type_id for expertSystem in associatedExpertSystems if expertSystems.expert_system_benefits_player(expertSystem.type_id) ]
                activeExpertSystems = ExpertSystemService.instance().GetMyExpertSystems()
                associatedExpertSystemsIds = [ expertSystem.type_id for expertSystem in associatedExpertSystems ]
                for es in activeExpertSystems:
                    if es in associatedExpertSystemsIds:
                        activeRelatedExpertSystem = True

            x = i % self.iconsPerRow
            y = (i - x) / self.iconsPerRow
            ShipTreeShipIcon(name=str(typeID), parent=self.shipContainer, typeID=typeID, factionID=self.factionID, groupNode=self.node, pos=(x * (self.iconSize + 1),
             y * (self.iconSize + 1),
             self.iconSize,
             self.iconSize), expertSystemTypeIDs=beneficialExpertSystems, activeRelatedExpertSystem=activeRelatedExpertSystem)

    def OnShipTreeZoomChanged(self, zoomLevel):
        self.zoomLevel = zoomLevel
        self.UpdateState(0, True)

    def OnShipTreeSkillTrained(self):
        self.UpdateState(0, animate=True)
        self.iconAndBar.UpdateState(0, animate=True)

    def FlashGroupIcon(self, duration = 0.8, delay = 0):
        self.iconAndBar.shipGroupIcon.Flash(duration, delay)

    def PlayFanfare(self):
        thump_duration = 0.45
        thump_delay = 0.4
        for i, child in enumerate(self.shipContainer.children):
            child.Thump(thump_duration, thump_delay * i)

        return len(self.shipContainer.children) * thump_delay

    @classmethod
    def GetNameForShipGroup(cls, shipGroupID):
        return 'ship_tree_group_{shipGroupID}'.format(shipGroupID=shipGroupID)


class ShipGroupIconAndSkillBar(ContainerAutoSize):
    default_name = 'ShipGroupIconAndSkillBar'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    __notifyevents__ = ('OnSkillQueueRefreshed', 'OnSkillsChanged', 'OnHighlightExpertSystemShipTreeShips', 'OnUnHighlightExpertSystemShipTreeShips')
    default_bgColor = COLOR_BG

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.node = attributes.node
        self.shipGroupIcon = ShipGroupIcon(parent=self, node=self.node)
        self.skillBarCont = ContainerAutoSize(parent=self, align=uiconst.TOPLEFT, width=42, top=43, state=uiconst.UI_DISABLED)
        for typeID, _ in self.node.GetBonusSkillsSorted():
            SkillLevelsCont(parent=self.skillBarCont, typeID=typeID, align=uiconst.TOTOP, padTop=1, padBottom=1, frameColor=COLOR_FRAME, barColor=shipTreeConst.COLOR_HILIGHT)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        sm.GetService('shipTreeUI').ShowInfoBubble(self, node=self.node)
        self.shipGroupIcon.OnMouseEnter()

    def OnMouseExit(self, *args):
        self.shipGroupIcon.OnMouseExit()

    def GetMenu(self):
        m = []
        if session.role & ROLE_PROGRAMMER:
            text = 'shipGroupID: %s' % self.node.shipGroupID
            m.append((text, blue.pyos.SetClipboardData, (str(self.node.shipGroupID),)))
        return m

    def UpdateState(self, i, animate = True):
        self.shipGroupIcon.UpdateState(i, animate)
        self.UpdateBars(i, animate)

    def OnSkillQueueRefreshed(self):
        self.UpdateBars()

    def OnSkillsChanged(self, *args):
        self.UpdateBars()

    def UpdateBars(self, i = 0, animate = True):
        if self.node.IsLocked():
            self.skillBarCont.Hide()
        else:
            self.skillBarCont.Show()
        isZoomedOut = sm.GetService('shipTreeUI').GetZoomLevel() == ZOOMED_OUT
        barPadding = 2 if isZoomedOut else 1
        for bar in self.skillBarCont.children:
            bar.SetBarPadding(barPadding)
            bar.Update()

    def OnHighlightExpertSystemShipTreeShips(self, *args):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=0.2)

    def OnUnHighlightExpertSystemShipTreeShips(self):
        uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.0)


class ShipGroupIcon(Container):
    default_name = 'ShipGroupIcon'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_DISABLED
    default_width = 42
    default_height = 42
    __notifyevents__ = ('OnShipTreeZoomChanged', 'OnShipTreeShipGroupFocused')

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.node = attributes.node
        self.bgFrame = Frame(name='bgFrame', bgParent=self, texturePath='res:/UI/Texture/Classes/ShipTree/Groups/groupIconFrame.png')
        self.bgFill = Fill(name='bgFill', bgParent=self, color=shipTreeConst.COLOR_BG)
        self.bgBlinkFill = None
        self.icon = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=cfg.infoBubbleGroups[self.node.shipGroupID]['icon'], color=shipTreeConst.COLOR_HILIGHT, width=32, height=32)
        self.bgFlash = Sprite(name='bgFillBlink', bgParent=self, texturePath='res:/UI/Texture/Classes/ShipTree/groups/groupIconFlash.png', idx=0, color=(1, 1, 1, 1), opacity=0.0)

    def OnShipTreeZoomChanged(self, zoom):
        self.UpdateState(0, True)

    def OnShipTreeShipGroupFocused(self, factionID, shipGroupID):
        if (factionID, shipGroupID) == (self.node.factionID, self.node.shipGroupID):
            self.Blink()
        elif self.bgBlinkFill and not self.node.IsBeingTrained():
            uicore.animations.FadeOut(self.bgBlinkFill)

    def Blink(self):
        self.ConstructBgBlinkFill()
        uicore.animations.FadeTo(self.bgBlinkFill, 0.0, 0.5, loops=ANIM_REPEAT, duration=1.2, curveType=ANIM_WAVE)

    def Flash(self, duration = 0.3, delay = 0.0):
        PlaySound('ship_goals_reveal_ship_group_play')
        uicore.animations.FadeTo(self.bgFlash, 0.0, 3, duration=duration, curveType=ANIM_WAVE, timeOffset=delay)
        uicore.animations.SpColorMorphTo(self.icon, endColor=(0, 0, 0, 1), duration=duration, curveType=uiconst.ANIM_WAVE, timeOffset=delay)

    def ConstructBgBlinkFill(self):
        if self.node.IsLocked():
            color = COLOR_HOVER_LOCKED
        else:
            color = COLOR_HOVER_UNLOCKED
        if not self.bgBlinkFill:
            self.bgBlinkFill = Sprite(name='bgFillBlink', bgParent=self, texturePath='res:/UI/Texture/Classes/ShipTree/groups/bgVignette.png', idx=0, color=color, opacity=0.0)
        else:
            self.bgBlinkFill.SetRGBA(color[0], color[1], color[2], self.bgBlinkFill.opacity)

    def OnMouseEnter(self, *args):
        self.ConstructBgBlinkFill()
        uicore.animations.FadeTo(self.bgBlinkFill, self.bgBlinkFill.opacity, 0.4, duration=0.3)

    def OnMouseExit(self, *args):
        if self.bgBlinkFill:
            uicore.animations.FadeTo(self.bgBlinkFill, self.bgBlinkFill.opacity, 0.0, duration=0.3)

    def UpdateState(self, i, animate = True):
        zoomLevel = sm.GetService('shipTreeUI').GetZoomLevel()
        isLocked = self.node.IsLocked()
        opacity = OPACITY_LOCKED if isLocked else 1.0
        if animate:
            uicore.animations.FadeTo(self.icon, self.icon.opacity, opacity, timeOffset=0.05 * i, duration=0.3)
        else:
            self.icon.opacity = opacity
        if zoomLevel == ZOOMED_OUT:
            opacity = 0.0
        elif isLocked:
            opacity = OPACITY_LOCKED
        else:
            opacity = 1.0
        if animate:
            uicore.animations.FadeTo(self.bgFrame, self.bgFrame.opacity, opacity, timeOffset=0.05 * i, duration=0.3)
        else:
            self.bgFrame.opacity = opacity
        color = COLOR_BG if isLocked else COLOR_SHIPGROUP_UNLOCKED
        if animate:
            uicore.animations.SpColorMorphTo(self.bgFill, self.bgFill.GetRGBA(), color)
        else:
            self.bgFill.SetRGBA(*color)
        if self.node.IsBeingTrained():
            self.Blink()
        elif self.bgBlinkFill:
            uicore.animations.FadeOut(self.bgBlinkFill)
