#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\item.py
import eveicon
import telemetry
import dogma.data
import eve.client.script.environment.invControllers as invCtrl
import inventorycommon.typeHelpers
import localization
import log
import weakref
from carbon.common.script.util.format import FmtAmt
from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataFromRawTuples
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import GetAttrs, GetWindowAbove
from carbonui import fontconst, TextColor, uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from dogma import units
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label, EveLabelSmall
from eve.client.script.ui.control.themeColored import FrameThemeColored
from eve.client.script.ui.shared.neocom.neocom.highlightState import GetIndicatorGlowBrightness, HighlightState, GetIndicatorColor
from eve.client.script.ui.util import uix
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.services.menuSvcExtras.invItemFunctions import GetContainerContents
from eve.client.script.ui.services.menuSvcExtras.menuFunctions import ActivateCharacterReSculpt, ActivateSkillExtractor, ActivateSkillInjector, OpenCrate, ActivateAbyssalKey, CraftDynamicItem, ActivateRandomJumpKey, ActivatePVPfilamentKey, ActivateVoidSpaceKey, ActivateWarpVector, DecryptItem
from eve.client.script.ui.shared.cloneGrade import ORIGIN_INVENTORY
from eve.client.script.ui.shared.cloneGrade.omegaCloneOverlayIcon import OmegaCloneOverlayIcon
from eve.client.script.ui.shared.fitting.ghostFittingHelpers import TryPreviewFitItemOnMouseAction
from eve.client.script.ui.shared.market.sellMulti import SellItems
from eve.client.script.ui.shared.tooltip.item import InventoryItemTooltip
from eve.client.script.ui.shared.activateMultiTraining import ActivateMultiTraining
from eve.client.script.ui.skilltrading.banner import AlphaInjectorBanner, SkillInjectorBanner, NonDiminishingInjectionBoosterBanner
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg
from eve.common.script.util import industryCommon
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from evetypes import TypeNotFoundException
from fighters.client import GetSquadronClassResPath, GetSquadronClassTooltip
from inventorycommon.const import VIEWMODE_LIST, VIEWMODE_DETAILS, VIEWMODE_ICONS, VIEWMODE_ASSETS, VIEWMODE_CARDS
from inventorycommon.util import GetItemVolume, IsShipFittingFlag
from menucheckers.itemCheckers import ItemChecker
from uthread2 import StartTasklet
_CONTAINER_GROUPS = {const.groupWreck,
 const.groupCargoContainer,
 const.groupSecureCargoContainer,
 const.groupAuditLogSecureContainer,
 const.groupFreightContainer}
OPACITY_BG = 0.9
COLOR_ACTIVESHIP = (0.0,
 0.6,
 0.0,
 1.0)
SLOT_TEXTURES = {const.effectRigSlot: 'res:/UI/Texture/classes/InvItem/slotSizeIIII.png',
 const.effectHiPower: 'res:/UI/Texture/classes/InvItem/slotSizeIII.png',
 const.effectMedPower: 'res:/UI/Texture/classes/InvItem/slotSizeII.png',
 const.effectLoPower: 'res:/UI/Texture/classes/InvItem/slotSizeI.png'}
AMMOSIZE_TEXTURES = {0: None,
 1: 'res:/UI/Texture/classes/InvItem/ammoSizeS.png',
 2: 'res:/UI/Texture/classes/InvItem/ammoSizeM.png',
 3: 'res:/UI/Texture/classes/InvItem/ammoSizeL.png',
 4: 'res:/UI/Texture/classes/InvItem/ammoSizeXL.png'}
TAG_SIZE = 8
TAG_COLOR = (0.97, 0.09, 0.13)
TAG_TEXTURE_PATH = 'res:/UI/Texture/Shared/smallDot.png'
TAG_PADDING = 2

class InvItemIconContainer(Container):
    default_state = uiconst.UI_NORMAL
    isDragObject = True

    def __init__(self, parent, height, entry):
        self._entry_ref = weakref.ref(entry)
        super(InvItemIconContainer, self).__init__(name='IconContainer', parent=parent, align=uiconst.TOTOP, height=height)

    @property
    def typeID(self):
        entry = self._entry_ref()
        if entry is not None:
            return getattr(entry, 'typeID', None)

    def GetMenu(self):
        entry = self._entry_ref()
        if entry is not None:
            return entry.GetMenu()

    def GetDragData(self, *args):
        entry = self._entry_ref()
        if entry is not None:
            return entry.GetDragData()

    def OnEndDrag(self, dragSource, dropLocation, dragData):
        entry = self._entry_ref()
        if entry is not None:
            return entry.OnEndDrag(dragSource, dropLocation, dragData)

    def OnClick(self, *args):
        entry = self._entry_ref()
        if entry is not None:
            return entry.OnClick(*args)

    def OnDblClick(self, *args):
        entry = self._entry_ref()
        if entry is not None:
            return entry.OnDblClick(*args)

    def OnMouseDown(self, *args):
        entry = self._entry_ref()
        if entry is not None:
            return entry.OnMouseDown(*args)

    def OnMouseUp(self, *args):
        entry = self._entry_ref()
        if entry is not None:
            return entry.OnMouseUp(*args)

    def OnDragEnter(self, dragObj, nodes):
        entry = self._entry_ref()
        if entry is not None:
            return entry.OnDragEnter(dragObj, nodes)

    def OnDragExit(self, dragObj, nodes):
        entry = self._entry_ref()
        if entry is not None:
            return entry.OnDragExit(dragObj, nodes)

    def OnDropData(self, dragObj, nodes):
        entry = self._entry_ref()
        if entry is not None:
            return entry.OnDropData(dragObj, nodes)

    def LoadTooltipPanel(self, panel, owner):
        entry = self._entry_ref()
        if entry is not None:
            return entry.LoadTooltipPanel(panel, owner)


class InvItem(SE_BaseClassCore):
    __guid__ = 'xtriui.InvItem'
    __groups__ = []
    __categories__ = []
    __notifyevents__ = ['ProcessActiveShipChanged',
     'OnLockedItemChangeUI',
     'OnInvClipboardChanged',
     'OnInventoryBadgingCreated',
     'OnInventoryBadgingDestroyed',
     'OnInventoryItemUnseen',
     'OnInventoryItemSeen']
    default_name = 'InvItem'
    default_width = 64
    default_height = 64
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_PICKCHILDREN
    isDragObject = True
    highlightable = True
    OMEGAICON_OPACITY = 0.8
    ICON_SIZE = 64
    _selection_frame = None
    _icon_frame = None

    def __init__(self, **kwargs):
        self.typeID = None
        self.subTypeID = None
        self.id = None
        self.powerType = None
        self.sr.node = None
        self.sr.tlicon = None
        self.rec = None
        self.activeShipHighlite = None
        self.blinkBG = None
        self.lockedIcon = None
        self.omegaIcon = None
        self.mainContainer = None
        self.iconCont = None
        self.tagContainer = None
        self.opacity = None
        self.viewOnly = None
        self.shouldShowTag = False
        self.isHovered = None
        super(InvItem, self).__init__(**kwargs)

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        super(InvItem, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.ConstructLayout()

    @classmethod
    def GetEntryHeight(cls):
        return cls.ICON_SIZE + fontconst.fontSizeFactor * 30 + 6

    @classmethod
    def GetEntryWidth(cls):
        return 64

    @classmethod
    def GetEntryColMargin(cls):
        return 16

    @classmethod
    def IsFixedWidth(cls):
        return True

    def ConstructLayout(self):
        self.mainContainer = Container(name='MainContainer', parent=self)
        self.AddIconContainer()
        self.AddTextContainer()

    def AddIconContainer(self):
        self.iconCont = InvItemIconContainer(parent=self.mainContainer, height=self.ICON_SIZE, entry=self)
        self.AddTag(parent=self.iconCont, tagAlign=uiconst.TOBOTTOM)

    def AddTextContainer(self):
        self.sr.label = Label(name='itemNameLabel', parent=self.mainContainer, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padding=(-3, 2, -3, 0), maxLines=2)

    def AddTag(self, parent, tagAlign):
        if not self.tagContainer:
            self.tagContainer = Line(name='newItemTagLine', parent=parent, weight=2, state=uiconst.UI_HIDDEN, align=uiconst.TOTOP_NOPUSH, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=GetIndicatorGlowBrightness(HighlightState.important), color=GetIndicatorColor(HighlightState.important))

    def MarkAsSeen(self):
        if self.shouldShowTag and self.rec:
            sm.GetService('neocom').MarkInventoryItemSeen(itemID=self.id, typeID=self.rec.typeID, flagID=self.rec.flagID, locationID=self.rec.locationID)
            self.HideTag()

    def IsTagged(self):
        return self.shouldShowTag

    def HideTag(self):
        if self.shouldShowTag:
            self.shouldShowTag = False
            self.UpdateTag()

    def UpdateShouldShowTag(self):
        if self.rec:
            self.shouldShowTag = sm.GetService('neocom').IsInventoryItemUnseen(itemID=self.id, typeID=self.rec.typeID, flagID=self.rec.flagID, locationID=self.rec.locationID)

    def UpdateTag(self):
        if not self.tagContainer:
            return
        self.tagContainer.state = uiconst.UI_DISABLED if self.shouldShowTag else uiconst.UI_HIDDEN

    def Select(self, animate = True):
        super(InvItem, self).Select(animate)
        if self._selection_frame:
            self._selection_frame.set_active(True, animate)
        self._update_icon_frame_padding()
        self._update_icon_opacity()
        self.MarkAsSeen()

    def Deselect(self, animate = True):
        super(InvItem, self).Deselect(animate)
        if self._selection_frame:
            self._selection_frame.set_active(False, animate)
        self._update_icon_frame_padding()
        self._update_icon_opacity()

    def OnInventoryBadgingCreated(self):
        self.UpdateShouldShowTag()
        self.UpdateTag()

    def OnInventoryBadgingDestroyed(self):
        self.shouldShowTag = False
        self.UpdateTag()

    def OnInventoryItemUnseen(self, item_ids):
        if self.id in item_ids:
            self.shouldShowTag = True
            self.UpdateTag()

    def OnInventoryItemSeen(self, item_ids):
        if self.id in item_ids:
            self.shouldShowTag = False
            self.UpdateTag()

    def OnInvClipboardChanged(self):
        if self.sr.node and sm.GetService('inv').IsOnClipboard(self.sr.node.item.itemID):
            self.opacity = 0.2
        else:
            self.opacity = 1.0

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if self.destroyed or not self.sr.node:
            return
        if self.id is not None and self.id in (shipID, oldShipID):
            self.Load(self.sr.node)

    def OnLockedItemChangeUI(self, itemID, ownerID, locationID):
        if not self.destroyed and self.sr.node:
            if itemID == self.id:
                item = None
                if self.rec:
                    item = self.rec
                elif self.sr.node.item:
                    item = self.sr.node.item
                if item is None:
                    log.LogInfo('Lock issue item is None')
                else:
                    locked = item.flagID == const.flagLocked or sm.GetService('lockedItems').IsItemLocked(item)
                    log.LogInfo('Locked:', locked, 'item:', item)
                    self.SetLockState(locked)

    def SetViewOnly(self, isViewOnly):
        self.viewOnly = isViewOnly
        if self.sr.node:
            self.sr.node.viewOnly = isViewOnly

    def SetLockState(self, locked):
        self.SetViewOnly(min(1, locked))
        if not self.sr.icon:
            return
        if self.viewOnly:
            self.ConstructLockedIcon()
            self.lockedIcon.Show()
        elif self.lockedIcon:
            self.lockedIcon.Hide()
        self._update_icon_opacity()

    def ConstructLockedIcon(self):
        if not self.lockedIcon:
            self.lockedIcon = Sprite(name='lockedIcon', parent=self.iconCont, align=uiconst.CENTER, width=16, height=16, texturePath=eveicon.locked, hint=localization.GetByLabel('UI/Inventory/ItemLocked'), color=TextColor.SECONDARY, idx=0)

    def Reset(self):
        self.viewOnly = 0
        self.subTypeID = None

    def PreLoad(node):
        if node.viewMode in (VIEWMODE_LIST, VIEWMODE_DETAILS):
            labelFunc = node.labelFunc or uix.GetItemLabel
            label = labelFunc(node.item, node)

    def LoadMainIcon(self):
        if self.GetViewMode() == VIEWMODE_LIST:
            return
        if not self.sr.icon:
            Fill(name='background', bgParent=self.iconCont, color=(1.0, 1.0, 1.0, 0.05))
            self._icon_frame = Container(parent=self.iconCont, align=uiconst.TOALL, padding=self._get_icon_frame_padding(), clipChildren=True)
            self.sr.icon = eveIcon.Icon(name='icon', parent=self._icon_frame, align=uiconst.CENTER, width=self.ICON_SIZE, height=self.ICON_SIZE, state=uiconst.UI_DISABLED, opacity=self._get_icon_opacity())
        try:
            self.sr.icon.LoadIconByTypeID(typeID=self.rec.typeID, ignoreSize=True, isCopy=self.sr.node.isBlueprint and self.sr.node.isCopy)
        except TypeNotFoundException:
            log.LogWarn('Failed to load icon for type', self.rec.typeID, '. Type does not exist.')

    def _SetItemContainerInternalName(self, name, isList):
        self.name = name
        if isList:
            self.sr.node.panelName = name

    def Load(self, node):
        self.sr.node = node
        self.sr.node.__guid__ = self.__guid__
        self.sr.node.itemID = node.item.itemID
        self.id = node.item.itemID
        self.rec = node.item
        self.typeID = node.item.typeID
        if not self.rec:
            return
        item = ItemChecker(self.rec)
        self.isContainer = self.rec.groupID in _CONTAINER_GROUPS and item.IsSingleton()
        self.isUnassembledContainer = self.rec.groupID in _CONTAINER_GROUPS and not item.IsSingleton()
        if item.IsBlueprint():
            self.sr.node.isBlueprint = True
            self.sr.node.isCopy = item.IsBlueprintCopy()
        if self.sr.node is None:
            return
        self.Reset()
        self.quantity = self.rec.stacksize
        viewMode = self.GetViewMode()
        listFlag = viewMode in (VIEWMODE_LIST, VIEWMODE_DETAILS)
        self._SetItemContainerInternalName(name='ItemEntry_%d' % self.typeID, isList=listFlag)
        if viewMode != VIEWMODE_CARDS:
            if eveCfg.GetActiveShip() == self.sr.node.item.itemID:
                if self.activeShipHighlite is None:
                    if listFlag:
                        padding = (0, 0, 0, 1)
                    else:
                        padding = (-5, -3, -5, -3)
                    self.activeShipHighlite = Container(name='activeShipHighlite', parent=self, idx=-1)
                    Frame(texturePath='res:/UI/Texture/Classes/InvItem/bgSelected.png', color=COLOR_ACTIVESHIP, parent=self.activeShipHighlite, padding=padding)
                    Frame(parent=self.activeShipHighlite, color=COLOR_ACTIVESHIP, padding=padding, opacity=0.4)
            elif self.activeShipHighlite:
                self.activeShipHighlite.Close()
                self.activeShipHighlite = None
        attribs = node.Get('godmaattribs', {})
        self.powerType = None
        for icon in (self.sr.ammosize_icon, self.sr.slotsize_icon, self.sr.contraband_icon):
            if icon:
                icon.Hide()

        if item.IsHardware():
            if viewMode != VIEWMODE_LIST:
                texturePath = None
                if attribs.has_key(const.attributeChargeSize):
                    texturePath = AMMOSIZE_TEXTURES[attribs[const.attributeChargeSize]]
                elif attribs.has_key(const.attributeRigSize):
                    texturePath = AMMOSIZE_TEXTURES[attribs[const.attributeRigSize]]
                if texturePath:
                    self.ConstructAmmoSizeIcon()
                    self.sr.ammosize_icon.texturePath = texturePath
            for effect in dogma.data.get_type_effects(self.rec.typeID):
                if effect.effectID in (const.effectRigSlot,
                 const.effectHiPower,
                 const.effectMedPower,
                 const.effectLoPower):
                    if viewMode != VIEWMODE_LIST:
                        self.ConstructSlotSizeIcon()
                        self.sr.slotsize_icon.LoadIcon(SLOT_TEXTURES[effect.effectID], ignoreSize=True)
                    self.powerType = effect.effectID
                    continue
                if viewMode != VIEWMODE_LIST and effect.effectID == const.effectSubSystem and const.attributeSubSystemSlot in attribs:
                    self.ConstructSlotSizeIcon()
                    self.sr.slotsize_icon.LoadIcon('res:/UI/Texture/classes/InvItem/slotSubsystem.png', ignoreSize=True)

        elif self.rec.groupID == const.groupVoucher and self.sr.node.voucher is not None:
            if self.rec.typeID != const.typeBookmark:
                self.subTypeID = self.sr.node.voucher.GetTypeInfo()[1]
        elif self.rec.categoryID == const.categoryCharge and attribs.has_key(const.attributeChargeSize):
            self.ConstructAmmoSizeIcon()
            self.sr.ammosize_icon.texturePath = AMMOSIZE_TEXTURES[attribs[const.attributeChargeSize]]
        factionID = sm.GetService('map').GetItem(eve.session.solarsystemid2).factionID
        if inventorycommon.typeHelpers.GetIllegalityInFaction(self.sr.node.invtype, factionID) is not None:
            self.ConstructContrabandIcon()
        if listFlag:
            self.sr.label.width = uicore.desktop.width
        if viewMode == VIEWMODE_ICONS or viewMode == VIEWMODE_CARDS:
            self.LoadMainIcon()
        if self.sr.node.Get('selected', 0):
            self.Select(animate=False)
        else:
            self.Deselect(animate=False)
        self.UpdateShouldShowTag()
        self.UpdateTag()
        self.UpdateLabel()
        self.CheckLoadOmegaIcon()
        self.LoadTechLevelIcon(node.item.typeID)
        locked = node.Get('locked', 0)
        viewOnly = node.Get('viewOnly', 0)
        if viewMode != VIEWMODE_LIST:
            if item.IsFighter():
                self.ConstructFighterClassIcon()
            elif self.sr.fighterClass:
                self.sr.fighterClass.display = False
        self.SetLockState(locked)
        if not locked:
            self.SetViewOnly(viewOnly)
        if item.IsStation():
            self.DisableDrag()
        self.OnInvClipboardChanged()

    def GetViewMode(self):
        if self.sr.node:
            return self.sr.node.viewMode

    def CheckLoadOmegaIcon(self):
        if self.GetViewMode() not in (VIEWMODE_ICONS, VIEWMODE_DETAILS, VIEWMODE_CARDS):
            return
        if sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(self.typeID):
            self.ConstructOmegaIcon()
            self.omegaIcon.Show()
        elif self.omegaIcon:
            self.omegaIcon.Hide()

    def ConstructOmegaIcon(self):
        if not self.omegaIcon:
            if self._selection_frame is not None:
                index = self._selection_frame.GetOrder() + 1
            elif self.sr.icon is not None:
                index = self.sr.icon.GetOrder()
            else:
                index = 0
            self.omegaIcon = OmegaCloneOverlayIcon(parent=self.iconCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=self.ICON_SIZE, height=self.ICON_SIZE, opacity=self.OMEGAICON_OPACITY, origin=ORIGIN_INVENTORY, reason=self.typeID, idx=index)

    def ConstructFlagsCont(self):
        if self.sr.flags is None:
            if self.GetViewMode() == VIEWMODE_DETAILS:
                self.sr.flags = Container(parent=self, idx=0, name='flags', pos=(4, 21, 32, 15), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, opacity=OPACITY_BG)
            elif self.GetViewMode() == VIEWMODE_ICONS:
                self.sr.flags = Container(parent=self, idx=0, name='flags', pos=(2, 33, 32, 15), align=uiconst.TOPRIGHT, state=uiconst.UI_PICKCHILDREN, opacity=OPACITY_BG)

    def ConstructFighterClassCont(self):
        if self.sr.fighterClass is None:
            if self.sr.node.viewMode == VIEWMODE_DETAILS:
                self.sr.fighterClass = Container(parent=self, idx=0, name='fighterClass', pos=(26, 0, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, bgColor=(0,
                 0,
                 0,
                 OPACITY_BG))
            elif self.sr.node.viewMode == VIEWMODE_ICONS:
                self.sr.fighterClass = Container(parent=self, idx=0, name='fighterClass', pos=(2, 2, 15, 15), align=uiconst.TOPRIGHT, state=uiconst.UI_PICKCHILDREN, bgColor=(0,
                 0,
                 0,
                 OPACITY_BG))
        self.sr.fighterClass.display = False

    def ConstructSlotSizeIcon(self):
        self.ConstructFlagsCont()
        if not self.sr.slotsize_icon:
            self.sr.slotsize_icon = eveIcon.Icon(parent=self.sr.flags, name='slotSize', pos=(0, 0, 15, 0), align=uiconst.TORIGHT, hint=localization.GetByLabel('UI/Inventory/FittingConstraint'))
        self.sr.slotsize_icon.state = uiconst.UI_DISABLED

    def ConstructFighterClassIcon(self):
        self.ConstructFighterClassCont()
        if not self.sr.fighterClassIcon:
            self.sr.fighterClassIcon = Sprite(parent=self.sr.fighterClass, name='fighterClass', pos=(0, 0, 16, 16))
        texturePath = GetSquadronClassResPath(self.typeID)
        self.sr.fighterClassIcon.LoadTexture(texturePath)
        self.sr.fighterClassIcon.hint = localization.GetByLabel(GetSquadronClassTooltip(self.typeID))
        self.sr.fighterClass.display = True

    def ConstructAmmoSizeIcon(self):
        self.ConstructFlagsCont()
        if not self.sr.ammosize_icon:
            self.sr.ammosize_icon = Sprite(parent=self.sr.flags, name='ammoSize', pos=(0, 0, 15, 0), align=uiconst.TORIGHT, hint=localization.GetByLabel('UI/Inventory/AmmoSizeConstraint'))
        self.sr.ammosize_icon.state = uiconst.UI_DISABLED

    def ConstructContrabandIcon(self):
        self.ConstructFlagsCont()
        if not self.sr.contraband_icon:
            self.sr.contraband_icon = Sprite(parent=self.sr.flags, name='contrabandIcon', pos=(0, 0, 15, 0), align=uiconst.TORIGHT, texturePath='res:/UI/Texture/classes/InvItem/contrabandIcon.png', hint=localization.GetByLabel('UI/Inventory/ItemIsContraband'))
        self.sr.contraband_icon.state = uiconst.UI_DISABLED

    def LoadTechLevelIcon(self, typeID = None):
        tlicon = uix.GetTechLevelIcon(self.sr.tlicon, 0, typeID)
        if tlicon is not None and GetAttrs(tlicon, 'parent') is None:
            self.sr.tlicon = tlicon
            if self.sr.node.viewMode == VIEWMODE_CARDS:
                tlicon.SetParent(self.iconCont, 0)
            else:
                tlicon.SetParent(self, 0)

    def UpdateLabel(self, new = 0):
        labelFunc = self.sr.node.labelFunc or uix.GetItemLabel
        label = labelFunc(self.rec, self.sr.node, new)
        if self.sr.node.viewMode != VIEWMODE_CARDS:
            self.ExpandContainerIfFirstWordExceedsWidth(label)
        self.sr.label.SetText(label)
        if self.sr.node.viewMode in (VIEWMODE_LIST, VIEWMODE_DETAILS, VIEWMODE_CARDS):
            return
        quantity = uix.GetItemQty(self.sr.node, 'ss')
        if self.rec.singleton or self.rec.typeID in (const.typeBookmark,):
            if self.sr.qtypar:
                self.sr.qtypar.Close()
                self.sr.qtypar = None
            return
        if not self.sr.qtypar:
            self.sr.qtypar = ContainerAutoSize(name='qtypar', parent=self.iconCont, align=uiconst.BOTTOMRIGHT, pos=(2, 2, 0, 0), state=uiconst.UI_DISABLED, bgColor=(0,
             0,
             0,
             OPACITY_BG), idx=0)
            self.sr.quantity_label = EveLabelSmall(parent=self.sr.qtypar, maxLines=1, opacity=1.0, padding=(4, 1, 4, 0))
        self.sr.quantity_label.text = quantity

    def _isUnlockedWithExpertSystems(self):
        return sm.GetService('skills').IsUnlockedWithExpertSystem(self.typeID)

    def ExpandContainerIfFirstWordExceedsWidth(self, label):
        if self.sr.node.viewMode != VIEWMODE_ICONS:
            return
        words = label[8:].split(' ')
        if len(words[0]) > 11:
            self.sr.label.padLeft = -3
            self.sr.label.left = 2

    def GetMenu(self):
        if self.sr.node:
            containerMenu = []
            if hasattr(self.sr.node.scroll.sr.content, 'GetMenu'):
                containerMenu = self.sr.node.scroll.sr.content.GetMenu()
            selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
            items = []
            for node in selected:
                if node.item:
                    items.append((node.item, node.Get('viewOnly', 0), None))

            menu = CreateMenuDataFromRawTuples(GetMenuService().InvItemMenu(items))
            menu.AddSeparator()
            menu += containerMenu
            return menu
        else:
            return GetMenuService().InvItemMenu(self.rec, self.viewOnly)

    def GetHeight(self, *args):
        node, width = args
        if node.viewMode in (VIEWMODE_DETAILS, VIEWMODE_ASSETS):
            node.height = 42
        else:
            node.height = 21
        return node.height

    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)
            else:
                self.sr.node.scroll.SelectNode(self.sr.node)
                eve.Message('ListEntryClick')

    def OnMouseEnter(self, *args):
        if uicore.uilib.leftbtn:
            return
        SE_BaseClassCore.OnMouseEnter(self, *args)
        self.sr.hint = ''
        if self._hiliteFill:
            self._hiliteFill.hovered = True
        if getattr(self, 'rec', None):
            TryPreviewFitItemOnMouseAction(self.rec)
        if self.sr.node and self.sr.node.viewMode == VIEWMODE_ICONS:
            StartTasklet(self.SetIconHint)
        if self.omegaIcon and not self._isUnlockedWithExpertSystems():
            self.omegaIcon.OnMouseEnter()
        if self.rec:
            typeID = self.rec.typeID
            if typeID:
                if ItemChecker(self.rec).IsSkillInjector():
                    sm.ScatterEvent('OnSkillInjectorMouseEnter', typeID)
                if not self.isHovered:
                    self.isHovered = True
                    sm.ScatterEvent('OnInventoryItemMouseEntered', typeID, self.rec.itemID)
        self._update_icon_frame_padding()
        self.MarkAsSeen()

    def SetIconHint(self):
        if self.sr.node:
            quantity = uix.GetItemQty(self.sr.node, 'ln')
            isSingleton = bool(self.rec.singleton)
            itemName = uix.GetItemName(self.sr.node.item, self.sr.node)
            self.sr.hint = itemName if isSingleton else '%s - %s' % (quantity, itemName)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.IsDragging():
            return
        if self.rec is None:
            return
        itemChecker = ItemChecker(self.rec)
        if itemChecker.IsAlphaSkillInjector():
            tooltipPanel.LoadGeneric1ColumnTemplate()
            tooltipPanel.state = uiconst.UI_NORMAL
            injectorBanner = AlphaInjectorBanner(align=uiconst.TOPLEFT, width=280, typeID=self.rec.typeID)
            tooltipPanel.AddCell(injectorBanner)
        elif itemChecker.IsSkillInjector():
            tooltipPanel.LoadGeneric1ColumnTemplate()
            tooltipPanel.state = uiconst.UI_NORMAL
            injectorBanner = SkillInjectorBanner(align=uiconst.TOPLEFT, width=280, typeID=self.rec.typeID)
            tooltipPanel.AddCell(injectorBanner)
        elif itemChecker.IsNonDiminishingInjectionBooster():
            tooltipPanel.margin = (12, 8, 12, 8)
            banner = NonDiminishingInjectionBoosterBanner(align=uiconst.TOPLEFT, typeID=self.rec.typeID, quantity=self.rec.stacksize)
            tooltipPanel.AddCell(banner)
        else:
            InventoryItemTooltip(tooltipPanel=tooltipPanel, item=self.rec)

    def GetTooltipPointer(self):
        return uiconst.POINT_BOTTOM_2

    def ConstructHiliteFill(self):
        if not self._hiliteFill:
            self._hiliteFill = ListEntryUnderlay(bgParent=self.iconCont)
        if self._selection_frame is None:
            self.ConstructSelectionFrame()

    def ConstructSelectionFrame(self):
        self._selection_frame = ItemSelectionFrame(parent=self.iconCont, align=uiconst.TOALL, idx=0, active=self._isSelected and self._showHilite)

    def ShowHilite(self, animate = True):
        super(InvItem, self).ShowHilite(animate)
        if self._isSelected or not self._showHilite:
            return
        if self._selection_frame:
            self._selection_frame.set_active(True, animate)
        self._update_icon_frame_padding()

    def HideHilite(self, animate = True):
        super(InvItem, self).HideHilite(animate)
        if self._isSelected or not self._showHilite:
            return
        if self._selection_frame:
            self._selection_frame.set_active(False, animate)
        self._update_icon_frame_padding()

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        if self._hiliteFill:
            self._hiliteFill.hovered = False
        if getattr(self, 'Draggable_dragging', 0):
            return
        TryPreviewFitItemOnMouseAction(None)
        if self.omegaIcon:
            self.omegaIcon.OnMouseExit()
        if self.rec and ItemChecker(self.rec).IsSkillInjector():
            sm.ScatterEvent('OnSkillInjectorMouseExit')
        if self.isHovered:
            self.isHovered = False
            sm.ScatterEvent('OnInventoryItemMouseExited', self.rec.typeID, self.rec.itemID)
        self._update_icon_frame_padding()

    def OnDblClick(self, *args):
        if self.rec is None:
            return
        itemChecker = ItemChecker(self.rec)
        if self.sr.node and self.sr.node.Get('OnDblClick', None):
            self.sr.node.OnDblClick(self)
        elif self.isContainer and not self.rec.flagID == const.flagCorpDeliveries:
            self.OpenContainer()
        elif not self.viewOnly:
            if industryCommon.IsBlueprintCategory(self.rec.categoryID):
                from eve.client.script.ui.shared.industry.industryWnd import Industry
                Industry.OpenOrShowBlueprint(blueprintID=self.sr.node.itemID)
            elif itemChecker.OfferActivateCharacterReSculptToken():
                ActivateCharacterReSculpt(self.rec.itemID)
            elif itemChecker.OfferActivateMultiTraining():
                ActivateMultiTraining(self.rec.itemID)
            elif itemChecker.OfferActivateSkillInjector():
                if self.typeID == const.typeAlphaTrainingInjector:
                    quantity = 1
                else:
                    quantity = self.rec.stacksize
                ActivateSkillInjector(self.rec, quantity)
            else:
                if not itemChecker.IsInPilotLocation():
                    return
                if itemChecker.IsAssembledShip():
                    if itemChecker.IsActiveShip():
                        uicore.cmd.OpenFitting()
                    elif session.stationid:
                        sm.StartService('station').TryActivateShip(self.rec)
                    elif session.structureid:
                        sm.StartService('structureDocking').ActivateShip(self.rec.itemID)
                elif itemChecker.IsShip():
                    GetMenuService().AssembleAndBoardShip(self.rec)
                elif self.isUnassembledContainer:
                    GetMenuService().AssembleContainer([self.rec])
                elif itemChecker.OfferActivateSkillExtractor():
                    ActivateSkillExtractor(self.rec)
                elif itemChecker.IsStructure():
                    sm.GetService('structureDeployment').Deploy(self.rec)
                elif itemChecker.OfferOpenCrate():
                    OpenCrate(self.typeID, self.rec.itemID, self.rec.stacksize)
                elif itemChecker.OfferRandomJumpKey():
                    ActivateRandomJumpKey(self.rec)
                elif itemChecker.OfferPVPFilamentKey():
                    ActivatePVPfilamentKey(self.rec)
                elif itemChecker.OfferActivateAbyssalKey():
                    ActivateAbyssalKey(self.rec)
                elif itemChecker.OfferActivateVoidSpaceKey():
                    ActivateVoidSpaceKey(self.rec)
                elif itemChecker.OfferWarpVector():
                    ActivateWarpVector(self.rec)
                elif itemChecker.OfferCraftDynamicItem():
                    CraftDynamicItem(self.rec)
                elif itemChecker.IsDecodable():
                    DecryptItem(self.rec.itemID, self.rec.typeID)
                else:
                    sm.GetService('info').ShowInfo(self.rec.typeID, self.rec.itemID)

    def OnMouseDown(self, *args):
        if getattr(self, 'powerType', None):
            TryPreviewFitItemOnMouseAction(self.rec)
        uicore.uilib.tooltipHandler.CloseTooltip()
        SE_BaseClassCore.OnMouseDown(self, *args)

    def GetDragData(self, *args):
        if not self.sr.node:
            return None
        nodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        for node in nodes:
            if not getattr(node, 'viewOnly', False):
                return nodes

    def OnEndDrag(self, dragSource, dropLocation, dragData):
        if dragSource.IsUnder(self):
            wnd = SellItems.GetIfOpen()
            if dropLocation.IsUnder(wnd) or dropLocation is wnd:
                wnd.DropItems(None, dragData)
        sm.ScatterEvent('OnInvItemDropEnded', self.name)

    def OnMouseUp(self, btn, *args):
        if uicore.uilib.mouseOver != self:
            if getattr(self, 'powerType', None):
                main = sm.GetService('station').GetSvc('fitting')
                if main is not None:
                    main.Hilite(None)
        SE_BaseClassCore.OnMouseUp(self, btn, *args)

    def OpenContainer(self):
        from eve.client.script.ui.shared.inventory.invWindow import Inventory as InventoryWindow
        if self.rec.ownerID not in (eve.session.charid, eve.session.corpid):
            eve.Message('CantDoThatWithSomeoneElsesStuff')
            return
        wnd = GetWindowAbove(self)
        item = ItemChecker(self.rec)
        if item.IsInPilotLocation():
            invID = ('StationContainer', self.rec.itemID)
            if self.sr.node.openContainerFunc is not None:
                return self.sr.node.openContainerFunc(invID)
            InventoryWindow.OpenOrShow(invID=invID, openFromWnd=wnd)
        elif item.OfferViewContents():
            if item.IsOwnedByMyCorp():
                return GetContainerContents(self.rec, sm.GetService('invCache'), item.GetLocationIDOfItemInCorpOffice())
            if item.IsOwnedByMe():
                if item.IsDirectlyInPersonalHangar():
                    return GetContainerContents(self.rec, sm.GetService('invCache'), self.rec.locationID)
                inventory = sm.GetService('invCache').GetInventoryFromId(self.rec.locationID)
                item = inventory.GetItem() if inventory else None
                if not item:
                    return
                category = getattr(item, 'categoryID', None)
                if category == const.categoryShip and item.locationID == session.stationid:
                    return InventoryWindow.OpenOrShow(invID=('StationContainer', self.rec.itemID), openFromWnd=wnd)

    def OnDragEnter(self, dragObj, nodes):
        if self.sr.node.container:
            self.sr.node.container.OnDragEnter(dragObj, nodes)
        if not nodes or not getattr(nodes[0], 'rec', None):
            return

        def isStackable():
            for node in nodes:
                if not getattr(node.rec, 'singleton', False) and node.rec.typeID == self.rec.typeID and node.rec.itemID != self.rec.itemID:
                    return True

            return False

        if not self.rec:
            return
        item = ItemChecker(self.rec)
        if self.isContainer or item.IsAssembledShip() or isStackable():
            self.ConstructBlinkBG()
            animations.FadeIn(self.blinkBG, 0.3, duration=0.2)

    def OnDragExit(self, dragObj, nodes):
        if self.sr.node.container:
            self.sr.node.container.OnDragExit(dragObj, nodes)
        if self.blinkBG:
            animations.FadeOut(self.blinkBG, duration=0.2)
        TryPreviewFitItemOnMouseAction(None)

    def OnDropData(self, dragObj, nodes):
        if self.blinkBG:
            animations.FadeOut(self.blinkBG, duration=0.2)
        if len(nodes) and getattr(nodes[0], 'scroll', None):
            nodes[0].scroll.ClearSelection()
            if not nodes[0].rec:
                return
            if not hasattr(nodes[0].rec, 'locationID'):
                return
            locationID = nodes[0].rec.locationID
            if locationID != self.rec.locationID:
                if not sm.GetService('crimewatchSvc').CheckCanTakeItems(locationID):
                    sm.GetService('crimewatchSvc').SafetyActivated(const.shipSafetyLevelPartial)
                    return
        item = ItemChecker(self.rec)
        if item.IsAssembledShip():
            if invCtrl.ShipCargo(self.rec.itemID).OnDropData(nodes):
                self.Blink()
            return
        if self.isContainer:
            if invCtrl.StationContainer(self.rec.itemID).OnDropData(nodes):
                self.Blink()
            return
        mergeToMe = []
        notUsed = []
        fighters = []
        sourceID = None
        for node in nodes:
            if hasattr(node, 'WithdrawPlex') and callable(node.WithdrawPlex):
                node.WithdrawPlex(self.sr.node.container.invController)
                continue
            if getattr(node, '__guid__', None) == 'uicls.FightersHealthGauge':
                fighters.append(node)
                continue
            if getattr(node, '__guid__', None) not in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem'):
                notUsed.append(node)
                continue
            if node.item.itemID == self.sr.node.item.itemID:
                notUsed.append(node)
                continue
            if node.item.typeID == self.sr.node.item.typeID and not isinstance(self.sr.node.item.itemID, tuple) and not getattr(node.item, 'singleton', False) and not self.sr.node.item.singleton:
                mergeToMe.append(node.item)
            else:
                notUsed.append(node)
            if sourceID is None:
                sourceID = node.rec.locationID

        if fighters:
            invCtrl.ShipFighterBay(self.rec.itemID).AddFightersFromTube(fighters)
            return
        if sourceID is None:
            log.LogInfo('OnDropData: Moot operation with ', nodes)
            return
        if mergeToMe:
            mergeAllowed = self._IsMergeAllowed(mergeToMe)
            if not mergeAllowed:
                return
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        mergeData = []
        stateMgr = sm.StartService('godma').GetStateManager()
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        singletons = []
        if len(mergeToMe) > 1 and shift:
            raise UserError('CannotPerformOnMultipleItems')
        for invItem in mergeToMe:
            if invItem.stacksize == 1:
                quantity = 1
            elif shift:
                ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, localization.GetByLabel('UI/Inventory/ItemActions/StackItems'))
                if ret is not None:
                    quantity = ret['qty']
                else:
                    quantity = None
            else:
                quantity = invItem.stacksize
            if not quantity:
                continue
            if invItem.categoryID == const.categoryCharge and IsShipFittingFlag(invItem.flagID):
                if type(invItem.itemID) is tuple:
                    flag = invItem.itemID[1]
                    chargeIDs = dogmaLocation.GetSubLocationsInBank(invItem.locationID, invItem.itemID)
                    if chargeIDs:
                        for chargeID in chargeIDs:
                            charge = dogmaLocation.dogmaItems[chargeID]
                            mergeData.append((charge.itemID,
                             self.rec.itemID,
                             dogmaLocation.GetAttributeValue(chargeID, const.attributeQuantity),
                             charge))

                    else:
                        mergeData.append((invItem.itemID,
                         self.rec.itemID,
                         quantity,
                         invItem))
                else:
                    crystalIDs = dogmaLocation.GetCrystalsInBank(invItem.locationID, invItem.itemID)
                    if crystalIDs:
                        for crystalID in crystalIDs:
                            crystal = dogmaLocation.GetItem(crystalID)
                            if crystal.singleton:
                                singletons.append(crystalID)
                            else:
                                mergeData.append((crystal.itemID,
                                 self.rec.itemID,
                                 crystal.stacksize,
                                 crystal))

                    else:
                        mergeData.append((invItem.itemID,
                         self.rec.itemID,
                         quantity,
                         invItem))
            else:
                mergeData.append((invItem.itemID,
                 self.rec.itemID,
                 quantity,
                 invItem))

        if singletons and GetAttrs(self, 'sr', 'node', 'rec', 'flagID'):
            flag = self.sr.node.rec.flagID
            inv = sm.GetService('invCache').GetInventoryFromId(self.rec.locationID)
            if inv:
                inv.MultiAdd(singletons, sourceID, flag=flag, fromManyFlags=True)
        if mergeData and GetAttrs(self, 'sr', 'node', 'container', 'invController', 'MultiMerge'):
            invController = self.sr.node.container.invController
            sm.ScatterEvent('OnInvContDragExit', invController.GetInvID(), [])
            if invController.MultiMerge(mergeData, sourceID):
                sm.GetService('audio').SendUIEvent('ui_state_stack')
                self.Blink()
        if notUsed and GetAttrs(self, 'sr', 'node', 'container', 'OnDropData'):
            self.sr.node.container.OnDropData(dragObj, notUsed)

    def _IsMergeAllowed(self, mergeToMe):
        if session.stationid or session.structureid:
            return True
        containerItem = sm.GetService('invCache').GetInventoryFromId(self.rec.locationID).GetItem()
        mergeNotAllowed = containerItem.itemID == mergeToMe[0].locationID and containerItem.ownerID not in (session.charid, session.corpid, session.allianceid)
        return not mergeNotAllowed

    def Blink(self):
        self.ConstructBlinkBG()
        animations.FadeTo(self.blinkBG, 0.0, 1.0, duration=0.25, curveType=uiconst.ANIM_WAVE, loops=2)

    def ConstructBlinkBG(self):
        if self.blinkBG is None:
            self.blinkBG = Sprite(name='blinkBg', parent=self.iconCont, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/bgSelected.png', opacity=0.0, idx=0)

    @classmethod
    def GetCopyData(cls, node):
        if node.__guid__ == 'xtriui.InvItem':
            sortName = 'sort_%s' % localization.GetByLabel('UI/Common/Quantity')
            qty = node.get(sortName) or ''
            return '%s<t>%s' % (node.name, qty)
        return node.label

    def _get_icon_opacity(self):
        if not self.sr.node:
            return 0.0
        else:
            view_mode = self.GetViewMode()
            if self.viewOnly and view_mode == VIEWMODE_ICONS:
                return 0.25
            return 1.0

    def _update_icon_opacity(self):
        if self.sr.icon:
            self.sr.icon.opacity = self._get_icon_opacity()

    def _get_icon_frame_padding(self):
        view_mode = self.GetViewMode()
        if view_mode == VIEWMODE_ICONS and (self._isSelected or self.isHovered) and self._showHilite:
            return (4, 4, 4, 4)
        else:
            return (0, 0, 0, 0)

    def _update_icon_frame_padding(self):
        if self._icon_frame:
            self._icon_frame.padding = self._get_icon_frame_padding()


class Item(InvItem):
    __guid__ = 'listentry.InvItem'
    OMEGAICON_OPACITY = 1.0
    ICON_SIZE = 32

    def ConstructLayout(self):
        self.sr.label = EveLabelMedium(name='InventoryItemLOL', parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT, idx=3, lineSpacing=-0.2, maxLines=1, autoFadeSides=16)
        self.iconCont = Container(parent=self, align=uiconst.CENTERLEFT, pos=(5,
         0,
         self.ICON_SIZE,
         self.ICON_SIZE))
        self.tagContainer = None

    def Load(self, node):
        InvItem.Load(self, node)
        viewMode = self.GetViewMode()
        if viewMode in [VIEWMODE_ICONS, VIEWMODE_DETAILS]:
            self.AddTag(parent=self.iconCont, tagAlign=uiconst.TOBOTTOM)
        elif viewMode == VIEWMODE_LIST:
            self.AddTag(parent=self, tagAlign=uiconst.CENTER)
        if viewMode == VIEWMODE_DETAILS:
            self.sr.label.left = 46
            self.LoadMainIcon()
        else:
            self.sr.label.left = 12
        self.UpdateShouldShowTag()
        self.UpdateTag()

    def CheckLoadOmegaIcon(self):
        if self.GetViewMode() not in (VIEWMODE_ICONS, VIEWMODE_DETAILS) and not self._isUnlockedWithExpertSystems():
            return
        if sm.GetService('cloneGradeSvc').IsRestrictedForAlpha(self.typeID):
            self.ConstructOmegaIcon()
            self.omegaIcon.Show()
        elif self.omegaIcon:
            self.omegaIcon.Hide()

    def ConstructOmegaIcon(self):
        if not self.omegaIcon:
            self.omegaIcon = OmegaCloneOverlayIcon(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(5,
             0,
             self.ICON_SIZE,
             self.ICON_SIZE), iconSize=20, opacity=self.OMEGAICON_OPACITY, idx=0, origin=ORIGIN_INVENTORY, reason=self.typeID)

    def ConstructHiliteFill(self):
        SE_BaseClassCore.ConstructHiliteFill(self)

    def SetLockState(self, locked):
        self.SetViewOnly(min(1, locked))
        if self.viewOnly:
            self.sr.label.SetRGBA(0.5, 0.5, 0.5, 1.0)
            self.iconCont.opacity = 0.25
            if self.sr.node.viewMode == VIEWMODE_DETAILS:
                self.ConstructLockedIcon()
                self.lockedIcon.Show()
        else:
            self.sr.label.SetRGBA(*TextColor.NORMAL)
            self.iconCont.opacity = 1.0
            if self.lockedIcon:
                self.lockedIcon.Hide()

    def ConstructLockedIcon(self):
        if not self.lockedIcon:
            self.lockedIcon = Sprite(name='lockedIcon', parent=self.iconCont, align=uiconst.CENTER, width=16, height=16, texturePath=eveicon.locked, hint=localization.GetByLabel('UI/Inventory/ItemLocked'), idx=0)


class ItemWithVolume(Item):
    __guid__ = 'listentry.InvItemWithVolume'

    def UpdateLabel(self, new = 0):
        InvItem.UpdateLabel(self, new)
        if GetAttrs(self, 'sr', 'node', 'remote'):
            return
        volume = GetItemVolume(self.rec)
        self.sr.node.Set('sort_%s' % localization.GetByLabel('UI/Inventory/ItemVolume'), volume)
        unit = units.get_display_name(const.unitVolume)
        label = '<t>%s %s' % (FmtAmt(volume), unit)
        if self.sr.node.viewMode in (VIEWMODE_LIST, VIEWMODE_DETAILS):
            self.sr.label.text += label
            label = self.sr.label.text
        else:
            self.sr.label.text += label
            label = self.sr.label.text
        self.sr.node.label = label


class InvAssetItem(Item):
    __guid__ = 'listentry.InvAssetItem'

    def Load(self, node):
        Item.Load(self, node)
        if node.Get('sublevel', 0):
            padding = 16 * node.Get('sublevel', 0)
            iconPadding = 5 + padding
            self.sr.label.left = 46 + padding
            self.iconCont.left = iconPadding
            if self.omegaIcon:
                self.omegaIcon.left = iconPadding
            if self.sr.flags:
                self.sr.flags.left = iconPadding
            if self.sr.tlicon:
                self.sr.tlicon.left = iconPadding

    def OnDropData(self, dragObj, nodes):
        pass


class InvAssetItemBySelection(InvAssetItem):
    __guid__ = 'listentry.InvAssetItemBySelection'

    def OnMouseEnter(self, *args):
        pass

    def LoadTooltipPanel(self, tooltipPanel, *args):
        pass

    def Load(self, node):
        node.selected = 0
        InvAssetItem.Load(self, node)
        if node.isSelected:
            self.SelectHighlight()
        else:
            self.UnSelectHighlight()

    def SelectHighlight(self):
        self.sr.node.isSelected = True
        self.background_color = (150, 0, 0, 0.5)

    def UnSelectHighlight(self):
        self.sr.node.isSelected = False
        self.background_color = (0, 0, 0, 0.0)


class ItemSelectionFrame(Container):
    _outer_frame = None

    def __init__(self, active = False, **kwargs):
        self._active = active
        super(ItemSelectionFrame, self).__init__(**kwargs)
        self._update_active(animate=False)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self.set_active(value)

    def set_active(self, value, animate = True):
        if self._active != value:
            self._active = value
            self._update_active(animate)

    def _get_frame_opacity(self):
        if self._active:
            return 1.0
        else:
            return 0.0

    def _get_outer_frame_glow_brightness(self):
        if self._active:
            return 0.5
        else:
            return 0.0

    def _update_active(self, animate = True):
        if self._active:
            self._create_frames_if_missing()
        if not self._outer_frame:
            return
        opacity = self._get_frame_opacity()
        if animate:
            duration = uiconst.TIME_ENTRY if self._active else uiconst.TIME_EXIT
            animations.MorphScalar(self._outer_frame, 'glowBrightness', startVal=self._outer_frame.glowBrightness, endVal=self._get_outer_frame_glow_brightness(), duration=duration)
            animations.FadeTo(self._outer_frame, startVal=self._outer_frame.opacity, endVal=opacity, duration=duration)
        else:
            animations.StopAnimation(self._outer_frame, 'glowBrightness')
            self._outer_frame.glowBrightness = self._get_outer_frame_glow_brightness()
            animations.StopAnimation(self._outer_frame, 'opacity')
            self._outer_frame.opacity = opacity

    def _create_frames_if_missing(self):
        if self._outer_frame is None:
            self._outer_frame = FrameThemeColored(parent=self, align=uiconst.TOALL, frameConst=uiconst.FRAME_BORDER2_CORNER0, colorType=uiconst.COLORTYPE_UIHILIGHT, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=self._get_outer_frame_glow_brightness(), opacity=self._get_frame_opacity())
