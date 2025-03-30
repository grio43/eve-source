#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\itemShip.py
from __future__ import absolute_import
import blue
import eveicon
import evetypes
import localization
import uthread2
from collections import OrderedDict, defaultdict
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from carbonui import TextColor, uiconst, TextBody, Align, TextDetail, PickState
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from characterdata.factions import get_faction_logo_flat
from dogma import data as dogma_data
import dogma.const as dogmaConst
from eve.client.script.ui.shared.neocom.neocom.highlightState import HighlightState, GetIndicatorColor
from eve.common.script.sys import idCheckers
from menucheckers.itemCheckers import ItemChecker
from inventoryutil.client.inventory import get_fitting_flags_for_ship_type
from inventorycommon.util import IsModularShip
from fsdBuiltData.common.iconIDs import GetIconFile
from eve.common.lib import appConst
from eve.common.script.sys import eveCfg
from eve.client.script.ui import eveThemeColor, eveColor
from shipgroup import get_ship_group_name
from eve.client.script.ui.shared.traits import TraitAttributeIcon
from eve.client.script.ui.util import uix
from eve.client.script.ui.shared.cloneGrade import ORIGIN_INVENTORY
from eve.client.script.ui.shared.cloneGrade.omegaCloneOverlayIcon import OmegaCloneOverlayIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.shared.item import InvItem, ItemSelectionFrame
import launchdarkly
CARD_STATE_NORMAL = 1
CARD_STATE_ACTIVE = 2
CARD_STATE_PACKAGED = 3
SHIP_CARD_FITTING_ICON_ENABLED = 'ship-card-fitting-icon-enabled'
SHIP_CARD_FITTING_ICON_ENABLED_DEFAULT = True
_should_display_fitting_icon = SHIP_CARD_FITTING_ICON_ENABLED_DEFAULT

def _refresh_fitting_flag(ld_client, flag_key, flag_fallback, flag_deleted):
    global _should_display_fitting_icon
    _should_display_fitting_icon = ld_client.get_bool_variation(feature_key=flag_key, fallback=flag_fallback)


launchdarkly.get_client().notify_flag(SHIP_CARD_FITTING_ICON_ENABLED, SHIP_CARD_FITTING_ICON_ENABLED_DEFAULT, _refresh_fitting_flag)

class ShipItemIcon(InvItem):

    def AddIconContainer(self):
        self.groupIcon = Sprite(parent=self.mainContainer, pickState=PickState.OFF, align=Align.TOPRIGHT, width=16, height=16, left=1, top=1, opacity=1, shadowOffset=(1, 1), shadowColor=(0, 0, 0))
        super(ShipItemIcon, self).AddIconContainer()

    def Load(self, node):
        super(ShipItemIcon, self).Load(node)
        self.groupIcon.texturePath = sm.GetService('bracket').GetBracketIcon(self.typeID)


class ShipItemCard(InvItem):
    FACTION_LOGO_ANIMATION_DURATION = 0.25
    FACTION_LOGO_MIN_SIZE = 96
    FACTION_LOGO_MAX_SIZE = 108
    OPACITY_IDLE = 0.2
    OPACITY_HOVER = 0.3
    OPACITY_MOUSEDOWN = 0.5
    MAIN_PADDING = 3
    fittedItems = []

    @classmethod
    def GetEntryHeight(cls):
        return 106

    @classmethod
    def GetEntryWidth(cls):
        return 235

    @classmethod
    def GetEntryColMargin(cls):
        return 6

    @classmethod
    def IsFixedWidth(cls):
        return False

    def ConstructLayout(self):
        self.card_state = CARD_STATE_NORMAL
        self.mainContainer = Container(name='MainContainer', parent=self, clipChildren=True, padding=self.MAIN_PADDING)
        self.ConstructBottom()
        self.ConstructContent()
        self.ConstructBackground()
        self.ConstructIndicator()

    def ConstructContent(self):
        iconWrapper = Container(name='iconWrapper', parent=self.mainContainer, align=Align.TOLEFT, width=self.ICON_SIZE, padding=2)
        self.iconCont = Container(name='iconCont', parent=iconWrapper, align=Align.CENTER, width=self.ICON_SIZE, height=self.ICON_SIZE)
        self._processing_click = False
        self.hoverIcon = ButtonIcon(name='hoverIcon', parent=self.iconCont, width=self.ICON_SIZE, height=self.ICON_SIZE, iconSize=32, texturePath=eveicon.soldier_of_fortune, opacity=0, func=self.OnDblClick)
        self.hoverBg = Sprite(name='hoverBg', parent=self.iconCont, width=self.ICON_SIZE, height=self.ICON_SIZE, texturePath='res:/UI/Texture/Classes/ShipTree/groups/bgWhite.png', color=(0, 0, 0, 0), opacity=0)
        content = Container(name='content', parent=self.mainContainer, align=Align.TOALL, padding=(6, 6, 6, 2), clipChildren=True)
        groupCont = Container(name='groupCont', parent=content, align=Align.TOTOP, height=16)
        self.groupIcon = Sprite(parent=groupCont, pickState=PickState.OFF, align=Align.CENTERLEFT, width=16, height=16, color=TextColor.NORMAL)
        self.groupLabel = TextDetail(parent=groupCont, align=Align.CENTERLEFT, text='', color=TextColor.SECONDARY, left=20)
        self.fittingIcon = FittedItemsIcon(parent=groupCont, align=Align.CENTERRIGHT, width=16, height=16, display=False)
        nameCont = ContainerAutoSize(name='nameCont', parent=content, align=Align.VERTICALLY_CENTERED)
        self.sr.label = TextBody(parent=nameCont, align=Align.TOTOP, color=TextColor.HIGHLIGHT, bold=True, maxLines=1, autoFadeSides=16)
        self.typeNameLabel = TextDetail(parent=nameCont, align=Align.TOTOP, text='', color=TextColor.SECONDARY, maxLines=1, autoFadeSides=16)

    def ConstructOmegaIcon(self):
        if self.omegaIcon:
            return
        self.omegaIcon = OmegaCloneOverlayIcon(parent=self.iconCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=self.ICON_SIZE, height=self.ICON_SIZE, opacity=self.OMEGAICON_OPACITY, origin=ORIGIN_INVENTORY, reason=self.typeID, idx=0)

    def ConstructBottom(self):
        bottomCont = Container(name='bottom', parent=self.mainContainer, align=Align.TOBOTTOM, height=30, padding=(2, 0, 2, 2))
        self.ConstructActiveState(bottomCont)
        self.ConstructPackagedState(bottomCont)
        self.traitCont = Container(name='traits', parent=bottomCont, align=uiconst.TOALL, padLeft=8, padRight=8, clipChildren=True)
        self.bottomBG = StretchSpriteHorizontal(name='bottomBG', parent=bottomCont, align=Align.TOALL, texturePath='res:/UI/Texture/classes/Button/background_cut_bottom_left_right.png', leftEdgeSize=9, rightEdgeSize=9, color=eveColor.WHITE, opacity=0.05)
        self.AddTag(bottomCont, Align.TOTOP_NOPUSH)

    def ConstructActiveState(self, parent):
        self.activeStateContainer = ContainerAutoSize(name='activeState', parent=parent, align=Align.TORIGHT, padLeft=2)
        TextBody(parent=self.activeStateContainer, name='label', align=Align.CENTER, color=TextColor.SUCCESS, text=localization.GetByLabel('UI/Ship/Active'), padLeft=12, padRight=12)
        Frame(bgParent=self.activeStateContainer, name='bg', align=Align.TOALL, texturePath='res:/UI/Texture/classes/Button/background_cut_bottom_right.png', cornerSize=9, color=(0, 0, 0, 0.6))

    def ConstructPackagedState(self, parent):
        self.packagedStateContainer = ContainerAutoSize(name='packagedState', parent=parent, align=Align.TORIGHT, alignMode=Align.TORIGHT)
        labelCont = ContainerAutoSize(parent=self.packagedStateContainer, align=Align.TORIGHT, padRight=9)
        self.packagedLabelCont = ContainerAutoSize(parent=labelCont, align=Align.TORIGHT)
        self.packagedLabelCont.DisableAutoSize()
        self.packagedLabel = TextBody(parent=self.packagedLabelCont, align=Align.CENTERLEFT, color=TextColor.WARNING, text=localization.GetByLabel('UI/Ship/Packaged'), opacity=0, padLeft=4)
        qtyContainer = ContainerAutoSize(parent=labelCont, align=Align.TORIGHT)
        self.packagedQtyLabel = TextBody(parent=qtyContainer, align=Align.CENTERLEFT, text='')
        Frame(bgParent=self.packagedStateContainer, name='bg', align=Align.TOALL, texturePath='res:/UI/Texture/classes/Button/background_cut_bottom_right.png', cornerSize=9, color=(0, 0, 0, 0.6))
        Sprite(parent=self.packagedStateContainer, texturePath='res:/UI/Texture/classes/Hangar/card_footer_triangle.png', color=(0, 0, 0, 0.6), align=Align.CENTERLEFT, height=30, width=30, left=-30)

    def ConstructBackground(self):
        self.factionIconCont = Transform(parent=self.mainContainer, align=Align.CENTERRIGHT, height=75, width=90, padRight=45)
        self.factionIcon = Sprite(name='factionIcon', parent=self.factionIconCont, align=Align.CENTER, width=self.FACTION_LOGO_MIN_SIZE, height=self.FACTION_LOGO_MIN_SIZE, pickState=PickState.OFF, color=(1, 1, 1, 0.05), top=0)
        Frame(name='card_mask_frame', bgParent=self, align=Align.TOALL, texturePath='res:/UI/Texture/classes/Hangar/card_fill.png', cornerSize=16, color=(0, 0, 0, 0.9), padding=self.MAIN_PADDING)
        self.backgroundFrame = Frame(parent=self, name='background_frame', align=Align.TOALL, texturePath='res:/UI/Texture/classes/Hangar/card_fill.png', cornerSize=9, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.1, color=eveThemeColor.THEME_FOCUS, padding=self.MAIN_PADDING, opacity=self.OPACITY_IDLE)

    def ConstructIndicator(self):
        self.cardIndicator = Frame(parent=self, name='indicator', align=Align.TOALL, texturePath='res:/UI/Texture/classes/Hangar/card_indicator.png', cornerSize=9, opacity=0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.8, padding=self.MAIN_PADDING)
        self.tagContainer = Frame(parent=self, name='tag', align=Align.TOALL, texturePath='res:/UI/Texture/classes/Hangar/card_indicator.png', cornerSize=9, padding=self.MAIN_PADDING, state=uiconst.UI_HIDDEN, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.6, color=GetIndicatorColor(HighlightState.important))

    def ConstructSelectionFrame(self):
        self._selection_frame = CardSelectionFrame(parent=self, align=uiconst.TOALL, idx=0, active=self._isSelected and self._showHilite)

    def UpdateTag(self):
        super(ShipItemCard, self).UpdateTag()
        if self.shouldShowTag:
            animations.MorphScalar(self.tagContainer, 'glowBrightness', 0.6, 1, duration=1.5, loops=10, curveType=uiconst.ANIM_WAVE)
        else:
            animations.StopAllAnimations(self.tagContainer)

    def UpdateCardState(self):
        item = ItemChecker(self.rec)
        if item.IsActiveShip():
            self.SetCardState(CARD_STATE_ACTIVE)
        elif item.IsAssembledShip():
            self.SetCardState(CARD_STATE_NORMAL)
        else:
            self.SetCardState(CARD_STATE_PACKAGED)

    def SetCardState(self, state):
        self.card_state = state
        if state == CARD_STATE_NORMAL:
            self.bottomBG.texturePath = 'res:/UI/Texture/classes/Button/background_cut_bottom_left_right.png'
            self.bottomBG.rightEdgeSize = 9
            self.activeStateContainer.Hide()
            self.packagedStateContainer.Hide()
            self.cardIndicator.color = eveThemeColor.THEME_FOCUS
            self.cardIndicator.opacity = 0
        elif state == CARD_STATE_ACTIVE:
            self.bottomBG.texturePath = 'res:/UI/Texture/classes/Button/background_cut_bottom_left.png'
            self.bottomBG.rightEdgeSize = 9
            self.activeStateContainer.Show()
            self.packagedStateContainer.Hide()
            self.cardIndicator.color = TextColor.SUCCESS
        else:
            self.bottomBG.texturePath = 'res:/UI/Texture/classes/Hangar/card_footer_stripes.png'
            self.bottomBG.rightEdgeSize = 110
            self.activeStateContainer.Hide()
            self.packagedStateContainer.Show()
            self.cardIndicator.color = eveThemeColor.THEME_FOCUS
            self.cardIndicator.opacity = 0

    def Load(self, node):
        self._processing_click = False
        super(ShipItemCard, self).Load(node)
        self.UpdateCardState()
        self.UpdateFittingIcon()
        if self.card_state == CARD_STATE_PACKAGED:
            quantity = uix.GetItemQty(self.sr.node, 'ss')
            self.packagedQtyLabel.text = u'x{qty}'.format(qty=quantity)
        self.groupLabel.text = get_ship_group_name(self.typeID)
        self.groupIcon.texturePath = sm.GetService('bracket').GetBracketIcon(self.typeID)
        factionID = evetypes.GetFactionID(self.typeID)
        factionLogo = get_faction_logo_flat(factionID)
        if factionLogo:
            self.factionIcon.texturePath = factionLogo.resolve(64)
        else:
            self.factionIconCont.Hide()
        if self.typeID not in cfg.infoBubbleTypeElements:
            return
        self.traitCont.Flush()
        data = cfg.infoBubbleTypeElements[self.typeID]
        attributeIDs = [ x[1] for x in sorted(data.items(), key=lambda d: int(d[0])) ]
        for index, attributeID in enumerate(attributeIDs):
            icon = TraitAttributeIcon(parent=self.traitCont, align=uiconst.CENTERLEFT, attributeID=attributeID, width=16, height=16, left=24 * index)
            icon.OnClick = self.OnClick
            icon.GetMenu = self.GetMenu
            icon.isDragObject = True
            icon.GetDragData = self.GetDragData
            icon.OnDropData = self.OnDropData

    def UpdateFittingIcon(self):
        self.fittingIcon.display = False
        if self.card_state == CARD_STATE_PACKAGED:
            return
        self.fittingIcon.Update(self.id, self.typeID)

    def UpdateLabel(self, new = 0):
        super(ShipItemCard, self).UpdateLabel(new)
        item = ItemChecker(self.rec)
        if item.IsAssembledShip():
            self.typeNameLabel.text = evetypes.GetName(self.typeID)

    def OnMouseEnter(self, *args):
        super(ShipItemCard, self).OnMouseEnter(*args)
        animations.StopAllAnimations(self.factionIcon)
        animations.MorphScalar(self.factionIcon, 'width', startVal=self.factionIcon.width, endVal=self.FACTION_LOGO_MAX_SIZE, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        animations.MorphScalar(self.factionIcon, 'height', startVal=self.factionIcon.height, endVal=self.FACTION_LOGO_MAX_SIZE, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        animations.FadeTo(self.factionIcon, self.factionIcon.opacity, endVal=0.025, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        animations.FadeTo(self.backgroundFrame, self.backgroundFrame.opacity, endVal=self.OPACITY_HOVER, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        animations.StopAllAnimations(self.packagedLabel)
        self.packagedLabelCont.ExpandWidth()
        animations.FadeIn(self.packagedLabel, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        if self.card_state != CARD_STATE_ACTIVE:
            animations.FadeIn(self.cardIndicator, duration=0.1)
            self.hoverIcon.SetTexturePath(eveicon.board)
        else:
            self.hoverIcon.SetTexturePath('res:/UI/Texture/WindowIcons/fitting.png')
        if not sm.GetService('cloneGradeSvc').IsRestricted(self.typeID):
            animations.FadeIn(self.hoverIcon, duration=self.FACTION_LOGO_ANIMATION_DURATION)
            animations.FadeIn(self.hoverBg, endVal=0.5, duration=self.FACTION_LOGO_ANIMATION_DURATION / 2)

    def OnDblClick(self, *args):
        if self._processing_click:
            return
        self._processing_click = True
        super(ShipItemCard, self).OnDblClick(*args)
        uthread2.start_tasklet(self._reset_click)

    def _reset_click(self):
        uthread2.sleep(2)
        self._processing_click = False

    def OnMouseExit(self, *args):
        super(ShipItemCard, self).OnMouseExit(*args)
        animations.StopAllAnimations(self.factionIcon)
        animations.MorphScalar(self.factionIcon, 'width', startVal=self.factionIcon.width, endVal=self.FACTION_LOGO_MIN_SIZE, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        animations.MorphScalar(self.factionIcon, 'height', startVal=self.factionIcon.height, endVal=self.FACTION_LOGO_MIN_SIZE, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        animations.FadeTo(self.factionIcon, self.factionIcon.opacity, endVal=0.05, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        animations.FadeTo(self.backgroundFrame, self.backgroundFrame.opacity, endVal=self.OPACITY_IDLE, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        animations.StopAllAnimations(self.packagedLabel)
        self.packagedLabelCont.CollapseWidth()
        animations.FadeOut(self.packagedLabel, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        if self.card_state != CARD_STATE_ACTIVE:
            animations.FadeOut(self.cardIndicator, duration=0.1)
        animations.FadeOut(self.hoverIcon, duration=self.FACTION_LOGO_ANIMATION_DURATION)
        animations.FadeOut(self.hoverBg, duration=self.FACTION_LOGO_ANIMATION_DURATION / 2)

    def OnColorThemeChanged(self):
        super(ShipItemCard, self).OnColorThemeChanged()
        self.backgroundFrame.rgb = eveThemeColor.THEME_FOCUSDARK[:3]
        if self.card_state != CARD_STATE_ACTIVE:
            self.cardIndicator.rgb = eveThemeColor.THEME_FOCUS[:3]


class CardSelectionFrame(ItemSelectionFrame):

    def _create_frames_if_missing(self):
        if self._outer_frame is None:
            self._outer_frame = Frame(parent=self, texturePath='res:/UI/Texture/classes/Hangar/card_outline.png', cornerSize=9, color=eveThemeColor.THEME_FOCUS, opacity=0.6, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.6)

    def OnColorThemeChanged(self):
        super(CardSelectionFrame, self).OnColorThemeChanged()
        if self._outer_frame:
            self._outer_frame.rgb = eveThemeColor.THEME_FOCUS[:3]


class FittedItemsIcon(Sprite):
    default_width = 16
    default_height = 16
    default_texturePath = eveicon.fitting
    default_color = TextColor.NORMAL
    __notifyevents__ = ['OnDogmaItemChange', 'OnFittingStripped']

    def __init__(self, *args, **kwargs):
        self._tasklet = None
        self._itemID = None
        self._typeID = None
        self._fittedItems = []
        self._charges = []
        self._dronesInBay = []
        super(FittedItemsIcon, self).__init__(*args, **kwargs)

    def ApplyAttributes(self, attributes):
        super(FittedItemsIcon, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def Close(self):
        super(FittedItemsIcon, self).Close()
        sm.UnregisterNotify(self)

    def Update(self, itemID, typeID):
        self._itemID = itemID
        self._typeID = typeID
        if self._tasklet:
            self._tasklet.Kill()
        self._tasklet = uthread2.start_tasklet(self._Update)

    def _Update(self, delay = None):
        if not self._should_display():
            self.display = False
            return
        if delay:
            uthread2.sleep(delay)
        self._update_items()
        self.opacity = TextColor.HIGHLIGHT.opacity if self._fittedItems or self._dronesInBay else TextColor.SECONDARY.opacity
        self.display = True

    def _update_items(self):
        self._fittedItems = []
        self._charges = []
        self._dronesInBay = []
        flags = get_fitting_flags_for_ship_type(self._typeID)
        if not flags:
            return
        if dogma_data.get_type_attribute(self._typeID, dogmaConst.attributeDroneCapacity) or IsModularShip(self._typeID):
            flags.append(appConst.flagDroneBay)
        inventory = sm.GetService('invCache').GetInventoryFromId(self._itemID)
        items = inventory.ListByFlags(flags)
        for item in items:
            if item.flagID in appConst.fittingFlags:
                if idCheckers.IsModule(item.categoryID) or item.flagID in appConst.subsystemSlotFlags:
                    self._fittedItems.append(item)
                elif idCheckers.IsCharge(item.categoryID):
                    self._charges.append(item)
            elif item.flagID == appConst.flagDroneBay:
                self._dronesInBay.append(item)

    def _should_display(self):
        if self._itemID == session.shipid:
            return True
        if not _should_display_fitting_icon:
            return False
        return blue.os.desiredSimDilation > 0.9

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self._itemID == session.shipid:
            self._update_items()
        tooltipPanel.LoadGeneric1ColumnTemplate()
        groupedEntries = OrderedDict()
        for attributeID, flagID in ((dogmaConst.attributeHiSlots, appConst.flagHiSlot0),
         (dogmaConst.attributeMedSlots, appConst.flagMedSlot0),
         (dogmaConst.attributeLowSlots, appConst.flagLoSlot0),
         (dogmaConst.attributeSubSystemSlot, appConst.flagSubSystemSlot0),
         (dogmaConst.attributeRigSlots, appConst.flagRigSlot0)):
            totalNum = int(dogma_data.get_type_attribute(self._typeID, attributeID, 0))
            groupedEntries[eveCfg.GetShipFlagLocationName(flagID)] = {'icon': GetIconFile(dogma_data.get_attribute_icon_id(attributeID)),
             'totalNum': totalNum,
             'fitted': defaultdict(int),
             'fittedAmount': 0,
             'charges': dict()}

        for fittedItem in self._fittedItems:
            slotName = eveCfg.GetShipFlagLocationName(fittedItem.flagID)
            if slotName in groupedEntries:
                groupedEntries[slotName]['fitted'][fittedItem.typeID] += 1
                groupedEntries[slotName]['fittedAmount'] += 1

        if self._charges:
            moduleTypesBySlot = {item.flagID:item.typeID for item in self._fittedItems}
            for charge in self._charges:
                moduleTypeID = moduleTypesBySlot.get(charge.flagID, None)
                if moduleTypeID:
                    slotName = eveCfg.GetShipFlagLocationName(charge.flagID)
                    if slotName in groupedEntries:
                        charges = groupedEntries[slotName]['charges']
                        if moduleTypeID not in charges:
                            charges[moduleTypeID] = defaultdict(int)
                        charges[moduleTypeID][charge.typeID] += charge.stacksize

        for slotName, groupInfo in groupedEntries.iteritems():
            if groupInfo['totalNum'] == 0 and groupInfo['fittedAmount'] == 0:
                continue
            if groupInfo['totalNum'] > 0:
                text = u'{} [{}/{}]'.format(slotName, groupInfo['fittedAmount'], groupInfo['totalNum'])
            else:
                text = u'{} [{}]'.format(slotName, groupInfo['fittedAmount'])
            tooltipPanel.AddCell(self._ConstructGroupEntry(groupInfo['icon'], text))
            for typeID, amount in sorted(groupInfo['fitted'].iteritems(), key=lambda entry: evetypes.GetName(entry[0])):
                tooltipPanel.AddCell(self._ConstructTypeEntry(typeID, amount))
                charges = groupInfo['charges'].get(typeID, {})
                for chargeTypeID, amount in sorted(charges.iteritems(), key=lambda entry: evetypes.GetName(entry[0])):
                    tooltipPanel.AddCell(self._ConstructTypeEntry(chargeTypeID, amount, padLeft=16))

            tooltipPanel.AddSpacer()

        if self._dronesInBay:
            dronesDict = defaultdict(int)
            for item in self._dronesInBay:
                dronesDict[item.typeID] += item.stacksize

            usedVolume = sum([ evetypes.GetVolume(typeID) * amount for typeID, amount in dronesDict.iteritems() ])
            totalVolume = dogma_data.get_type_attribute(self._typeID, dogmaConst.attributeDroneCapacity)
            tooltipPanel.AddCell(self._ConstructGroupEntry(eveicon.drones, u'{} [{}]'.format(localization.GetByLabel('UI/Drones/Drones'), localization.GetByLabel('UI/Inventory/ContainerQuantityAndCapacity', quantity=usedVolume, capacity=totalVolume))))
            for typeID, amount in dronesDict.iteritems():
                tooltipPanel.AddCell(self._ConstructTypeEntry(typeID, amount))

        self.tooltipPanelMenu = tooltipPanel

    def _ConstructGroupEntry(self, icon, text):
        entryHeight = 24
        container = ContainerAutoSize(align=Align.CENTERLEFT, height=entryHeight, bgColor=(1, 1, 1, 0.1))
        Sprite(parent=container, align=Align.TOLEFT, width=entryHeight, height=entryHeight, texturePath=icon, color=TextColor.NORMAL)
        labelCont = ContainerAutoSize(parent=container, align=Align.TOLEFT)
        TextBody(parent=labelCont, text=text, align=Align.CENTERLEFT, left=8, width=tooltipConst.LABEL_WRAP_WIDTH)
        return container

    def _ConstructTypeEntry(self, typeID, amount, padLeft = 0):
        entryHeight = 24
        container = ContainerAutoSize(align=Align.CENTERLEFT, height=entryHeight, padLeft=padLeft)
        ItemIcon(parent=container, align=Align.TOLEFT, width=entryHeight, height=entryHeight, showOmegaOverlay=False, typeID=typeID)
        labelCont = ContainerAutoSize(parent=container, align=Align.TOLEFT)
        text = evetypes.GetName(typeID)
        if amount > 1:
            text = localization.GetByLabel('UI/InfoWindow/FittingItemLabelWithQuantity', quantity=amount, itemName=text)
        TextBody(parent=labelCont, text=text, align=Align.CENTERLEFT, left=8, width=tooltipConst.LABEL_WRAP_WIDTH - padLeft)
        return container

    def OnDogmaItemChange(self, item, change):
        if self._itemID != session.shipid:
            return
        self._Update()

    def OnFittingStripped(self, shipID):
        if self._itemID != shipID:
            return
        if self._tasklet:
            self._tasklet.Kill()
        self._tasklet = uthread2.start_tasklet(self._Update, delay=0.5)
