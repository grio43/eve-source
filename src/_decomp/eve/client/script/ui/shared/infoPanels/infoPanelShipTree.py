#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelShipTree.py
import carbonui.const as uiconst
import eve.client.script.ui.shared.shipTree.shipTreeConst as shipTreeConst
import localization
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uicore import uicore
from characterdata.factions import get_faction_name
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import LogoIcon
from eve.client.script.ui.control.eveLabel import Label, EveCaptionSmall
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from eve.client.script.ui.shared.shipTree.shipTreeConst import ICON_BY_FACTIONID
from eve.client.script.ui.shared.traits import TraitAttributeIcon
from eveservices.menu import GetMenuService
from inventorycommon.const import typeFaction

class InfoPanelShipTree(InfoPanelBase):
    default_name = 'InfoPanelShipTree'
    panelTypeID = infoPanelConst.PANEL_SHIP_TREE
    label = 'UI/ShipTree/ShipTree'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/ShipTree.png'
    hasSettings = False
    isCollapsable = False
    __notifyevents__ = ('OnBeforeShipTreeFactionSelected', 'OnShipTreeSkillTrained')

    def ApplyAttributes(self, attributes):
        InfoPanelBase.ApplyAttributes(self, attributes)
        self.header = self.headerCls(parent=self.headerCont, align=uiconst.CENTERLEFT, text=localization.GetByLabel(self.label))
        BTNSIZE = 24
        Button(parent=self.headerCont, align=uiconst.CENTERRIGHT, pos=(0,
         0,
         BTNSIZE,
         BTNSIZE), texturePath='res:/UI/Texture/Icons/73_16_45.png', iconSize=16, func=self.ExitShipTreeMode, hint=localization.GetByLabel('UI/ShipTree/ExitShipTree'))
        self.mainIconCont = ContainerAutoSize(name='mainIconCont', parent=self.mainCont, align=uiconst.TOTOP, padTop=2)
        numInRow = 5
        size = 53
        self.factionButtons = []
        selectedFactionID = sm.GetService('shipTreeUI').GetSelectedFaction()
        for i, factionID in enumerate(shipTreeConst.FACTIONS):
            left = i % numInRow * (size + 1)
            top = i / numInRow * (size + 2)
            isActive = factionID == selectedFactionID
            btn = ShipTreeButtonIcon(parent=self.mainIconCont, texturePath=ICON_BY_FACTIONID.get(factionID), align=uiconst.TOPLEFT, pos=(left,
             top,
             size,
             size), iconSize=46, func=sm.GetService('shipTreeUI').SelectFaction, args=(factionID, True), hint=get_faction_name(factionID), factionID=factionID, isActive=isActive)
            self.factionButtons.append(btn)

        factionID = sm.GetService('shipTreeUI').GetSelectedFaction()
        self.factionInfoCont = InfoBubbleRace(parent=self.mainCont, align=uiconst.TOTOP, width=0, padTop=10, factionID=factionID)

    def OnBeforeShipTreeFactionSelected(self, factionID):
        for btn in self.mainIconCont.children:
            btn.SetActive(factionID == btn.factionID)

        self.factionInfoCont.UpdateFaction(factionID)

    def OnShipTreeSkillTrained(self):
        for btn in self.factionButtons:
            btn.CheckBlink()

    def ExitShipTreeMode(self, *args):
        uicore.cmd.GetCommandAndExecute('CmdToggleShipTree')


class InfoBubbleRace(Container):
    default_name = 'InfoBubbleRace'
    default_alignMode = uiconst.TOTOP
    __notifyevents__ = ('OnShipTreeFactionButtonEnter', 'OnShipTreeFactionButtonExit', 'OnShipTreeFactionSelected')

    def ApplyAttributes(self, attributes):
        super(InfoBubbleRace, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.factionID = attributes.factionID
        self.mainCont = Container(name='mainCont', parent=self)
        self.content = ContainerAutoSize(name='content', parent=self.mainCont, align=uiconst.TOTOP, callback=self.OnMainContResize)
        self.bgFrame = Container(name='bgFrame', parent=self, state=uiconst.UI_DISABLED)
        self.frameTop = StretchSpriteHorizontal(name='frameTop', parent=self.bgFrame, align=uiconst.TOTOP, texturePath='res:/UI/Texture/classes/ShipTree/InfoBubble/frameUpper.png', height=36)
        self.frameBottom = StretchSpriteHorizontal(name='frameBottom', parent=self.bgFrame, align=uiconst.TOBOTTOM, texturePath='res:/UI/Texture/classes/ShipTree/InfoBubble/frameLower.png', height=36)
        self.bgFill = Container(name='bgFill', parent=self, state=uiconst.UI_DISABLED)
        StretchSpriteHorizontal(parent=self.bgFill, align=uiconst.TOTOP, texturePath='res:/UI/Texture/classes/ShipTree/InfoBubble/backTopExtender.png', height=1)
        StretchSpriteHorizontal(parent=self.bgFill, align=uiconst.TOBOTTOM, texturePath='res:/UI/Texture/classes/ShipTree/InfoBubble/backBottom.png', height=6)
        Sprite(parent=self.bgFill, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/ShipTree/InfoBubble/backMiddle.png')
        topCont = ContainerAutoSize(name='topContainer', parent=self.content, align=uiconst.TOTOP, padding=(10, 10, 10, 0), height=50)
        topRightCont = ContainerAutoSize(name='topContentContainer', parent=topCont, align=uiconst.TOPLEFT, left=64, width=180)
        self.icon = Sprite(name='icon', parent=topCont, pos=(0, 0, 64, 64), align=uiconst.TOPLEFT)
        self.caption = EveCaptionSmall(parent=topRightCont, align=uiconst.TOTOP)
        self.flowContainerCont = ContainerAutoSize(parent=topRightCont, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT)
        self.attributeCont = FlowContainer(name='attributeCont', parent=self.flowContainerCont, align=uiconst.TOPLEFT, contentSpacing=(1, 1), padTop=5, width=160)
        self.descriptionLabel = Label(name='descriptionLabel', parent=self.content, align=uiconst.TOTOP, padding=(10, 6, 10, 10))
        self.ShowFaction(self.factionID)

    def OnMainContResize(self):
        self.height = self.content.height

    def UpdateFaction(self, factionID):
        self.factionID = factionID
        self.ShowFaction(factionID)

    def ShowFaction(self, factionID, animate = True):
        self.icon.texturePath = ICON_BY_FACTIONID.get(factionID)
        self.caption.text = get_faction_name(factionID)
        factionData = cfg.infoBubbleFactions[factionID]
        self.attributeCont.Flush()
        for _, attributeID in factionData['elements'].iteritems():
            TraitAttributeIcon(name='InfoBubbleAttributeIcon', parent=self.attributeCont, align=uiconst.NOALIGN, attributeID=attributeID, opacity=1.0, width=30)

        self.descriptionLabel.text = localization.GetByMessageID(factionData['descriptionID'])

    def OnShipTreeFactionButtonEnter(self, factionID):
        self.ShowFaction(factionID, animate=False)

    def OnShipTreeFactionButtonExit(self, factionID):
        self.ShowFaction(self.factionID, animate=False)


class ShipTreeButtonIcon(ButtonIcon):
    default_name = 'ShipTreeButtonIcon'
    default_iconColor = eveColor.WHITE

    def ApplyAttributes(self, attributes):
        super(ShipTreeButtonIcon, self).ApplyAttributes(attributes)
        self.factionID = attributes.factionID
        self.CheckBlink()
        self.SetActive(self.isActive)

    def _GetIconColor(self):
        return eveColor.WHITE

    def CheckBlink(self):
        if sm.GetService('shipTree').IsGroupsRecentlyUnlocked(self.factionID):
            self.Blink(duration=1.2, loops=uiconst.ANIM_REPEAT)
        else:
            self.StopBlink()

    def ConstructBackground(self):
        self.mouseEnterBG = Frame(name='mouseEnterBG', bgParent=self.bgContainer, texturePath='res:/UI/Texture/classes/ShipTree/InfoPanel/hover.png', opacity=0.0)
        self.mouseDownBG = Sprite(name='mouseDownBG', bgParent=self.bgContainer, texturePath='res:/UI/Texture/classes/ButtonIcon/mouseDown.png', opacity=0.0)
        self.selectedBG = Frame(name='selectedBG', bgParent=self.bgContainer, texturePath='res:/UI/Texture/classes/ShipTree/InfoPanel/selected.png', opacity=0.0)

    def OnMouseEnter(self, *args):
        super(ShipTreeButtonIcon, self).OnMouseEnter(*args)
        sm.ScatterEvent('OnShipTreeFactionButtonEnter', self.factionID)

    def OnMouseExit(self, *args):
        super(ShipTreeButtonIcon, self).OnMouseExit(*args)
        sm.ScatterEvent('OnShipTreeFactionButtonExit', self.factionID)

    def SetActive(self, isActive, animate = True):
        self.isActive = isActive
        self.UpdateIconState()
        if animate:
            if isActive:
                uicore.animations.FadeTo(self.selectedBG, self.selectedBG.opacity, 1.0, duration=0.15)
            else:
                uicore.animations.FadeTo(self.selectedBG, self.selectedBG.opacity, 0.0, duration=0.15)
        elif self.selectedBG:
            self.selectedBG.StopAnimations()
            self.selectedBG.opacity = 1.0 if isActive else 0.0

    def OnMouseDown(self, *args):
        if not self.enabled:
            return
        self.SetActive(self.isActive)
        if self.isHoverBGUsed:
            uicore.animations.FadeIn(self.mouseDownBG, duration=0.1)
        else:
            uicore.animations.FadeTo(self.icon, self.icon.opacity, self.GLOWAMOUNT_MOUSECLICK, duration=0.1)

    def OnMouseUp(self, *args):
        if self.isHoverBGUsed:
            uicore.animations.FadeOut(self.mouseDownBG, duration=0.1)
        else:
            uicore.animations.FadeTo(self.icon, self.icon.opacity, self.OPACITY_IDLE, duration=0.1)
        if not self.enabled:
            return
        if uicore.uilib.mouseOver == self:
            if not self.isHoverBGUsed:
                uicore.animations.FadeTo(self.icon, self.icon.opacity, self.GLOWAMOUNT_MOUSEHOVER, duration=0.1)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(self.factionID, typeFaction)
