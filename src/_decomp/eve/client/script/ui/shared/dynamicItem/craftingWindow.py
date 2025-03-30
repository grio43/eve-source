#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dynamicItem\craftingWindow.py
from __future__ import absolute_import
import __builtin__
import math
import dogma.data as dogma_data
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.services.setting import CharSettingBool
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.util.various_unsorted import IsUnder
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.entries import item as item_entry
from eve.client.script.ui.control.entries.space import Space
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.themeColored import FillThemeColored, SpriteThemeColored
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.dynamicItem.const import COLOR_DECAYED, COLOR_GRAVID, COLOR_NEGATIVE, COLOR_POSITIVE, COLOR_UNSTABLE, GetAbnormalTypes, GetDecayedTypes, GetGravidTypes, GetUnstableTypes
from eve.client.script.ui.shared.dynamicItem.info import FormatAttributeBonusRange
from eve.client.script.ui.shared.industry.submitButton import PrimaryButton
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.info.attribute import Attribute, MutatedAttribute
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
import blue
import dynamicitemattributes as dynamicitems
import eveexceptions
import evetypes
import localization
import log
import menucheckers
import signals
import trinity
import uthread
import utillib
from localization import GetByLabel
MUTATOR_FAST_ANIMATIONS_SETTING = CharSettingBool('MutatorFastAnimations', False)
RES_BAR_FILL = 'res:/UI/Texture/Classes/DynamicItem/arrows.png'
RES_ERROR_ICON = 'res:/UI/Texture/Icons/icons111_07.png'
RES_INPUT_BACKGROUND = 'res:/UI/Texture/classes/DynamicItem/inputBackground.png'
RES_INPUT_FRAME = 'res:/UI/Texture/classes/DynamicItem/inputFrame.png'
RES_INPUT_RING = 'res:/UI/Texture/classes/DynamicItem/bgCircle.png'
RES_RING_GLOW_MASK = 'res:/UI/Texture/classes/DynamicItem/bgGlowRing.png'
RES_SWIRL = 'res:/UI/Texture/classes/DynamicItem/swirl.png'
RES_WINDOW_ICON = 'res:/ui/Texture/WindowIcons/mutation.png'

def Item(typeID, itemID = None, locationID = None, flagID = None, ownerID = None):
    return utillib.KeyVal(typeID=typeID, itemID=itemID, locationID=locationID, flagID=flagID, ownerID=ownerID)


class CraftingController(object):
    __notifyevents__ = ['OnItemChange', 'OnSessionChanged']

    def __init__(self, mutator, source = None):
        self.onChange = signals.Signal(signalName='onChange')
        self.onDragEnter = signals.Signal(signalName='onDragEnter')
        self.onDragExit = signals.Signal(signalName='onDragExit')
        self.onError = signals.Signal(signalName='onError')
        self._craftingResult = None
        self._isCrafting = False
        self._isResultPresented = False
        self._mutator = mutator
        self._mutatorTypes = None
        self._resultItemID = None
        self._settings = __builtin__.settings
        self._source = source
        sm.RegisterNotify(self)

    @property
    def isFastAnimations(self):
        return MUTATOR_FAST_ANIMATIONS_SETTING.is_enabled()

    @isFastAnimations.setter
    def isFastAnimations(self, isFastAnimations):
        MUTATOR_FAST_ANIMATIONS_SETTING.set(isFastAnimations)

    @property
    def isResultPresented(self):
        return self._isResultPresented

    @property
    def mutatorItemID(self):
        return self._mutator.itemID

    @property
    def mutatorTypeID(self):
        return self._mutator.typeID

    @property
    def resultItemID(self):
        return self._resultItemID

    @property
    def sourceTypeID(self):
        if self._source is None:
            return
        return self._source.typeID

    @property
    def sourceItemID(self):
        if self._source is None:
            return
        return self._source.itemID

    @property
    def resultTypeID(self):
        if self._source is None:
            return
        return dynamicitems.GetResultType(self._mutator.typeID, self._source.typeID)

    def GetAttribute(self, attributeID):
        if not self.IsSourceItemSelected():
            return Attribute(attributeID, None)
        value = None
        if self.IsCraftingResultAvailable():
            value = self._craftingResult[attributeID]
        static = sm.GetService('clientDogmaStaticSvc')
        base = static.GetTypeAttribute(self._source.typeID, attributeID)
        bonusLow, bonusHigh = self.GetAttributeBonusRange(attributeID)
        return MutatedAttribute(attribute=Attribute(attributeID, value), sourceValue=base, minValue=base * bonusLow, maxValue=base * bonusHigh, highIsGood=self._GetHighIsGood(attributeID))

    def _GetHighIsGood(self, attributeID):
        attributes = dynamicitems.GetMutatorAttributes(self.mutatorTypeID)
        attribute = attributes[attributeID]
        return getattr(attribute, 'highIsGood', None)

    def GetApplicableTypes(self):
        return dynamicitems.GetApplicableTypes(self.mutatorTypeID)

    def GetRelatedMutatorTypes(self):
        if self._mutatorTypes is None:
            resultTypes = dynamicitems.GetResultTypes(self.mutatorTypeID)
            mutatorTypes = dynamicitems.GetMutatorTypesByResultTypes(resultTypes)
            self._mutatorTypes = mutatorTypes
        return self._mutatorTypes

    def GetModifiedAttributeIDs(self):
        return dynamicitems.GetMutatorAttributes(self.mutatorTypeID).keys()

    def GetAttributeBonusRange(self, attributeID):
        attributes = dynamicitems.GetMutatorAttributes(self.mutatorTypeID)
        attribute = attributes[attributeID]
        return (attribute.min, attribute.max)

    def SelectSourceItem(self, item):
        if self._isCrafting or self.IsCraftingResultAvailable():
            return
        if item is None and self._source is not None:
            self._source = None
            self.onChange()
            return
        if item.typeID not in self.GetApplicableTypes():
            raise RuntimeError('Invalid source item type')
        if item.itemID is None:
            item = self._FindItem(item.typeID)
        if self.sourceItemID is not None and self.sourceItemID == item.itemID:
            return
        self._source = item
        self.onChange()

    def SelectMutator(self, item):
        if self._isCrafting or self.IsCraftingResultAvailable():
            return
        if item is None:
            return
        if item.typeID not in dynamicitems.GetAllMutatorTypes():
            raise RuntimeError('Invalid mutator item type')
        if item.itemID is None:
            item = self._FindItem(item.typeID)
        if item.itemID is not None and self._mutator.itemID == item.itemID:
            return
        if self.mutatorTypeID == item.typeID and self.mutatorItemID == item.itemID:
            return
        if item.typeID not in self.GetRelatedMutatorTypes():
            self._source = None
            self._mutatorTypes = None
        self._mutator = item
        if self.IsSourceItemSelected() and not self.IsSourceItemAvailable():
            self._source = self._FindItem(self._source.typeID)
        self.onChange()

    def IsItemAvailable(self, typeID):
        item = self._FindItem(typeID)
        return item.itemID is not None

    def _FindItem(self, typeID):
        checker = menucheckers.ItemChecker(self._mutator)
        if not checker.IsInPilotLocation():
            return Item(typeID=typeID, locationID=self._mutator.locationID, flagID=self._mutator.flagID)
        invCache = sm.GetService('invCache')
        if self._mutator.locationID == session.stationid:
            inventory = invCache.GetInventory(const.containerHangar)
        else:
            inventory = invCache.GetInventoryFromId(self._mutator.locationID)
        items = inventory.List(self._mutator.flagID)
        for item in items:
            if item.typeID == typeID:
                return Item(typeID=typeID, itemID=item.itemID, locationID=self._mutator.locationID, flagID=self._mutator.flagID, ownerID=item.ownerID)

        return Item(typeID=typeID, locationID=self._mutator.locationID, flagID=self._mutator.flagID)

    def IsSourceItemSelected(self):
        return self._source is not None

    def IsSourceItemAvailable(self):
        if not self.IsSourceItemSelected():
            return False
        checker = menucheckers.ItemChecker(self._source)
        return self._source.itemID is not None and checker.IsInPilotLocation()

    def IsMutatorAvailable(self):
        checker = menucheckers.ItemChecker(self._mutator)
        return self._mutator.itemID is not None and checker.IsInPilotLocation()

    def ExecuteCrafting(self):
        self._isCrafting = True
        try:
            if not self.IsMutatorAvailable():
                raise RuntimeError('The selected mutator is not available')
            if not self.IsSourceItemAvailable():
                raise RuntimeError('Invalid source item selected')
            dynamicItemSvc = sm.GetService('dynamicItemSvc')
            try:
                itemID = dynamicItemSvc.CreateDynamicItem(self.mutatorItemID, self._source.itemID)
            except eveexceptions.UserError:
                raise
            except Exception:
                log.LogException()
                message = localization.GetByLabel('UI/DynamicItem/UnknownErrorBody')
                self.onError(message)
            else:
                self._craftingResult = dynamicItemSvc.GetMutatedAttributes(itemID)
                self._resultItemID = itemID
                self.onChange()

        finally:
            self._isCrafting = False

    def SetResultPresented(self):
        self._isResultPresented = True
        self.onChange()

    def IsCraftingResultAvailable(self):
        return self._craftingResult is not None

    def Close(self):
        sm.UnregisterNotify(self)
        self.onChange.clear()
        self.onDragEnter.clear()
        self.onDragExit.clear()
        self.onError.clear()

    def AcceptItemDropData(self, dropData):
        for entry in dropData:
            item = getattr(entry, 'item', None)
            if item is None:
                continue
            if self.IsAcceptedSourceItem(item):
                self.SelectSourceItem(item)
                break
            if self.IsAcceptedMutatorItem(item):
                self.SelectMutator(item)
                break

    def IsAcceptedSourceItem(self, item):
        if self._isCrafting or self.IsCraftingResultAvailable():
            return False
        if not self._IsItemReachable(item):
            return False
        if item.typeID not in self.GetApplicableTypes():
            return False
        if self._source is None:
            return True
        if self._source.itemID is None and item.itemID is not None:
            return True
        if self._source.itemID != item.itemID:
            return True
        if self._source.typeID != item.typeID:
            return True
        return False

    def IsAcceptedMutatorItem(self, item):
        if self._isCrafting or self.IsCraftingResultAvailable():
            return False
        if not self._IsItemReachable(item):
            return False
        if item.typeID not in dynamicitems.GetAllMutatorTypes():
            return False
        if self._mutator.itemID is None and item.itemID is not None:
            return True
        if self._mutator.itemID != item.itemID:
            return True
        if self._mutator.typeID != item.typeID:
            return True
        return False

    def _IsItemReachable(self, item):
        if item.ownerID != session.charid:
            return False
        if item.flagID in const.fittingFlags:
            return False
        return True

    def GetResultDragData(self):
        item = utillib.KeyVal(typeID=self.resultTypeID, itemID=self._resultItemID, locationID=self._mutator.locationID, flagID=self._mutator.flagID, ownerID=self._mutator.ownerID, stacksize=1, categoryID=evetypes.GetCategoryID(self.resultTypeID), groupID=evetypes.GetGroupID(self.resultTypeID), singleton=True)
        return utillib.KeyVal(__guid__='listentry.InvItem', typeID=self.resultTypeID, item=item, rec=item, label=evetypes.GetName(self.resultTypeID), name=evetypes.GetName(self.resultTypeID))

    def Reset(self):
        self._resultItemID = None
        self._craftingResult = None
        self._isResultPresented = False
        self._mutator = self._FindItem(self._mutator.typeID)
        if self.IsSourceItemSelected():
            self._source = self._FindItem(self._source.typeID)
        self.onChange()

    def OnItemChange(self, item, change, location):
        itemMovedKeys = (const.ixLocationID, const.ixOwnerID, const.ixFlag)
        if not any((key in change for key in itemMovedKeys)):
            return
        if item.itemID is None:
            return
        if item.itemID == self.resultItemID:
            self.Reset()
        elif item.itemID == self.mutatorItemID:
            self.SelectMutator(Item(typeID=item.typeID))
        elif item.typeID == self.mutatorTypeID and not self.IsMutatorAvailable():
            self.SelectMutator(Item(typeID=item.typeID))
        elif item.itemID == self.sourceItemID or item.typeID == self.sourceTypeID and not self.IsSourceItemAvailable():
            self.SelectSourceItem(Item(typeID=item.typeID))

    def OnSessionChanged(self, isRemote, session, changes):
        monitoredChanges = ('locationid', 'stationid', 'structureid', 'shipid')
        if any((key in changes for key in monitoredChanges)):
            self.Reset()

    def OnDragEnter(self, item):
        self.onDragEnter(item)

    def OnDragExit(self):
        self.onDragExit()


class CraftingWindow(Window):
    default_fixedWidth = 750
    default_fixedHeight = 478
    default_windowID = 'CraftingWindow'
    default_caption = GetByLabel('UI/DynamicItem/MutateItem')
    default_isCollapseable = False
    default_isLightBackgroundConfigurable = False
    default_isLockable = False
    default_isOverlayable = False
    default_isStackable = False
    default_iconNum = RES_WINDOW_ICON

    @classmethod
    def Open(cls, **attributes):
        window = cls.GetIfOpen()
        if not window:
            return super(CraftingWindow, cls).Open(**attributes)
        mutator = attributes.get('mutator', None)
        if mutator and mutator.itemID == window.controller.mutatorItemID:
            window.Maximize()
            return window
        window.CloseByUser()
        return super(CraftingWindow, cls).Open(**attributes)

    def ApplyAttributes(self, attributes):
        super(CraftingWindow, self).ApplyAttributes(attributes)
        self.controller = CraftingController(attributes.mutator)
        self._dragCookie = None
        self._isDragHintActive = False
        self.Layout()
        self.controller.onDragEnter.connect(self.OnItemDragEnter)
        self.controller.onDragExit.connect(self.OnItemDragExit)
        self.controller.onError.connect(self.OnError)

    def Layout(self):
        buildCont = Container(name='buildCont', parent=self.GetMainArea(), align=uiconst.TOLEFT, width=400)
        buttonCont = ContainerAutoSize(name='buttonCont', parent=buildCont, align=uiconst.TOBOTTOM)
        BuildButton(parent=buttonCont, align=uiconst.CENTERTOP, controller=self.controller)
        inputCont = Container(name='inputCont', parent=buildCont, align=uiconst.TOALL)
        self.sourceItemSlot = SourceItemSlot(parent=inputCont, align=uiconst.CENTER, top=-10, controller=self.controller)
        self.sourceItemSlot.OnDropData = self.OnDropData
        attributeCont = Container(name='attributeCont', parent=self.GetMainArea(), align=uiconst.TOALL)
        mutatorItemSlot = MutatorItemSlot(parent=attributeCont, align=uiconst.TOTOP, controller=self.controller)
        mutatorItemSlot.OnDropData = self.OnDropData
        attributeScroll = ScrollContainer(parent=attributeCont, align=uiconst.TOALL, padTop=5, padBottom=5)
        attributeListCont = ContainerAutoSize(parent=attributeScroll, align=uiconst.TOPLEFT)
        AttributeList(parent=attributeListCont, align=uiconst.TOPLEFT, controller=self.controller, width=300)

    def UpdateState(self):
        name = evetypes.GetName(self.controller.mutatorTypeID)
        self.SetCaption(name)

    def Close(self, *args, **kwargs):
        self.controller.Close()
        if self._dragCookie is not None:
            uicore.uilib.UnregisterForTriuiEvents(self._dragCookie)
            self._dragCookie = None
        super(CraftingWindow, self).Close(*args, **kwargs)

    def GetUtilMenu(self, menu):
        menu.AddCheckBox(text=localization.GetByLabel('UI/DynamicItem/OptionFastAnimations'), checked=MUTATOR_FAST_ANIMATIONS_SETTING.is_enabled(), callback=MUTATOR_FAST_ANIMATIONS_SETTING.toggle)

    def GetMenuMoreOptions(self):
        m = MenuData()
        m.AddCheckbox(localization.GetByLabel('UI/DynamicItem/OptionFastAnimations'), setting=MUTATOR_FAST_ANIMATIONS_SETTING)
        return m

    def OnItemDragEnter(self, item):
        if self.controller.IsAcceptedSourceItem(item):
            self._isDragHintActive = True
            uthread.new(self.AnimDragEnter)

    def OnItemDragExit(self):
        if self._isDragHintActive:
            uthread.new(self.AnimDragExit)

    def AnimDragEnter(self):
        self.sourceItemSlot.AnimShowDragHint()

    def AnimDragExit(self):
        self.sourceItemSlot.AnimHideDragHint()

    def OnError(self, message):
        error = ErrorMessage(parent=self.GetMainArea(), align=uiconst.CENTER, width=750, height=450, idx=0)
        error.DelegateEvents(self)
        error.SetMessage(message)
        uthread.new(error.AnimShow)
        self.controller.Close()

    def OnDropData(self, source, data):
        self.controller.AcceptItemDropData(data)
        if self._dragCookie is not None:
            uicore.uilib.UnregisterForTriuiEvents(self._dragCookie)
            self._dragCookie = None
            uthread.new(self.AnimDragExit)

    def OnGlobalDrag(self, *args):
        target = uicore.uilib.mouseOver
        if uicore.IsDragging() and (IsUnder(target, self) or target == self):
            return True
        else:
            self.controller.OnDragExit()
            self._dragCookie = None
            return False

    def OnDragEnter(self, source, data):
        if self._dragCookie is not None:
            return
        for entry in data:
            item = getattr(entry, 'item', None)
            if item is None:
                continue
            self._dragCookie = uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVEDRAG, self.OnGlobalDrag)
            self.controller.OnDragEnter(item)
            break


class ErrorMessage(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(ErrorMessage, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        Fill(bgParent=self, color=Color.BLACK, opacity=0.75)
        dialogCont = ContainerAutoSize(parent=self, align=uiconst.CENTER, alignMode=uiconst.TOPLEFT, width=440)
        Sprite(parent=dialogCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, pos=(0, 0, 64, 64), texturePath=RES_ERROR_ICON)
        messageCont = ContainerAutoSize(parent=dialogCont, align=uiconst.TOPLEFT, left=80, width=360)
        FillThemeColored(bgParent=messageCont, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.9)
        eveLabel.EveCaptionLarge(parent=messageCont, align=uiconst.TOTOP, padding=(16, 16, 16, 8), text=localization.GetByLabel('UI/DynamicItem/UnknownErrorHeader'))
        self.label = eveLabel.EveLabelLarge(parent=messageCont, align=uiconst.TOTOP, padding=(16, 0, 16, 16))

    def SetMessage(self, message):
        self.label.SetText(message)

    def AnimShow(self):
        animations.FadeTo(self, duration=0.8, curveType=uiconst.ANIM_OVERSHOT)


class AttributeList(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(AttributeList, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self._mutatorTypes = self.controller.GetRelatedMutatorTypes()
        uthread.new(self.Load)
        self.controller.onChange.connect(self.OnChange)

    def Load(self):
        entries = []
        for attributeID in self.controller.GetModifiedAttributeIDs():
            entry = AttributeEntry(align=uiconst.TOTOP, top=8, controller=self.controller, attributeID=attributeID)
            entries.append(entry)

        sortedEntries = sorted(entries, key=lambda e: e.label)
        for i, entry in enumerate(sortedEntries):
            entry.SetParent(self)
            entry.SetAnimationIndex(i)

    def Reload(self):
        self.Flush()
        self.Load()
        for child in self.children:
            uthread.new(child.AnimEnter)

    def OnChange(self):
        if self.controller.mutatorTypeID not in self._mutatorTypes:
            self._mutatorTypes = self.controller.GetRelatedMutatorTypes()
            uthread.new(self.Reload)
        else:
            for child in self.children:
                child.OnChange()


class MutatorItemSlot(Container):
    default_height = 80
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(MutatorItemSlot, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self._selectedTypeID = self.controller.mutatorTypeID
        self._isAvailable = self.controller.IsMutatorAvailable()
        self.Layout()
        self.UpdateState()
        self.controller.onChange.connect(self.OnChange)
        self.controller.onDragEnter.connect(self.OnItemDragEnter)
        self.controller.onDragExit.connect(self.OnItemDragExit)

    def Layout(self):
        self.bgFill = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.errorFrame = ErrorFrame(bgParent=self, opacity=0.0, opacityHigh=0.2, opacityLow=0.1, color=COLOR_NEGATIVE)
        mutatorIconCont = Container(parent=self, align=uiconst.TOLEFT, width=80)
        self.mutatorIcon = ItemIcon(parent=mutatorIconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, showOmegaOverlay=False)
        mutatorLabelCont = Container(parent=self, align=uiconst.TOALL)
        floatLabelCont = ContainerAutoSize(parent=mutatorLabelCont, align=uiconst.CENTERLEFT, width=206)
        self.mutatorLabel = eveLabel.EveLabelLargeBold(parent=floatLabelCont, align=uiconst.TOTOP)
        eveLabel.EveLabelMedium(parent=floatLabelCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/DynamicItem/MutationEffects'), opacity=0.6)

    def UpdateState(self):
        self._selectedTypeID = self.controller.mutatorTypeID
        self._isAvailable = self.controller.IsMutatorAvailable()
        name = evetypes.GetName(self._selectedTypeID)
        self.mutatorLabel.SetText(name)
        self.mutatorIcon.SetTypeID(self._selectedTypeID)
        if self._isAvailable:
            self.errorFrame.Hide()
            self.mutatorIcon.opacity = 1.0
            self.mutatorLabel.opacity = 1.0
        else:
            self.errorFrame.Show()
            self.mutatorIcon.opacity = 0.5
            self.mutatorLabel.opacity = 0.5

    def AnimUpdateItemIcon(self):
        animations.FadeTo(self.mutatorIcon, endVal=self.mutatorIcon.opacity, duration=0.3, curveType=uiconst.ANIM_OVERSHOT, timeOffset=0.1)
        animations.Tr2DScaleIn(self.mutatorIcon.icon, scaleCenter=(0.5, 0.5), duration=0.2)
        animations.FadeIn(self.mutatorLabel, endVal=self.mutatorLabel.opacity, duration=0.3)
        if uicore.uilib.mouseOver != self:
            self.AnimDeactivate()

    def LoadTooltipPanel(self, panel, owner):
        if not self.controller.IsCraftingResultAvailable():
            panel.SetState(uiconst.UI_NORMAL)
            panel.margin = (8, 8, 8, 8)
            MutatorItemScrollList(parent=panel, align=uiconst.TOPLEFT, width=284, height=110, controller=self.controller)

    def GetTooltipPositionFallbacks(self):
        return [uiconst.POINT_BOTTOM_2,
         uiconst.POINT_TOP_2,
         uiconst.POINT_LEFT_2,
         uiconst.POINT_RIGHT_2]

    def AnimActivate(self):
        animations.FadeTo(self.bgFill, startVal=self.bgFill.opacity, endVal=0.35, duration=0.1)

    def AnimDeactivate(self):
        animations.FadeTo(self.bgFill, startVal=self.bgFill.opacity, endVal=0.25, duration=0.3)

    def OnMouseEnter(self, *args):
        if self.controller.IsCraftingResultAvailable():
            return
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        uthread.new(self.AnimActivate)

    def OnMouseExit(self, *args):
        uthread.new(self.AnimDeactivate)

    def OnItemDragEnter(self, item):
        if self.controller.IsAcceptedMutatorItem(item):
            uthread.new(self.AnimActivate)

    def OnItemDragExit(self):
        uthread.new(self.AnimDeactivate)

    def OnChange(self):
        if self._selectedTypeID != self.controller.mutatorTypeID or self._isAvailable != self.controller.IsMutatorAvailable():
            self.UpdateState()
            uthread.new(self.AnimUpdateItemIcon)


class MutatorItemScrollList(Scroll):
    default_multiSelect = False

    def ApplyAttributes(self, attributes):
        super(MutatorItemScrollList, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        uthread.new(self.LoadMutatorItemList)

    def LoadMutatorItemList(self):
        self.ShowLoading()
        try:
            entries = {}
            for typeID in self.controller.GetRelatedMutatorTypes():
                key = evetypes.GetName(typeID)
                entry = GetFromClass(SourceItemEntry, {'typeID': typeID,
                 'label': evetypes.GetName(typeID),
                 'getIcon': True,
                 'isSelected': typeID == self.controller.sourceTypeID,
                 'isItemOwned': self.controller.IsItemAvailable(typeID)})
                entries[key] = entry

        finally:
            self.HideLoading()

        sortedEntries = []
        if entries:
            text = localization.GetByLabel('UI/DynamicItem/MutaplasmidListHeader')
            entry = GetFromClass(HeaderEntry, {'text': text})
            sortedEntries.append(entry)
            sortedEntries.extend(sortedValuesByKey(entries))
        self.Load(contentList=sortedEntries)

    def OnSelectionChange(self, nodes):
        if not nodes:
            return
        item = Item(typeID=nodes[0].typeID, itemID=None)
        self.controller.SelectMutator(item)

    def Prepare_Underlay_(self):
        pass


class SourceItemSlot(Container):
    default_width = 70
    default_height = 70
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    isDragObject = True

    def ApplyAttributes(self, attributes):
        super(SourceItemSlot, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self._selectedMutatorID = self.controller.mutatorTypeID
        self._selectedTypeID = self.controller.sourceTypeID
        self._isAvailable = self.controller.IsSourceItemAvailable()
        self.Layout()
        self.Load()
        self.controller.onChange.connect(self.OnChange)

    def Layout(self):
        swirlCont = Container(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 64, 64), clipChildren=False)
        self.swirlPrimary = Sprite(parent=swirlCont, align=uiconst.CENTER, pos=(0, 0, 500, 500), texturePath=RES_SWIRL, color=self.GetSwirlColor())
        self.swirlSecondary = Sprite(parent=swirlCont, align=uiconst.CENTER, pos=(0, 0, 500, 500), texturePath=RES_SWIRL, textureSecondaryPath=RES_SWIRL, spriteEffect=trinity.TR2_SFX_MODULATE, blendMode=trinity.TR2_SBM_ADDX2, color=self.GetSwirlColor(), rotation=math.pi)
        self.swirlTiny = Sprite(parent=swirlCont, align=uiconst.CENTER, pos=(0, 0, 200, 200), texturePath=RES_SWIRL, textureSecondaryPath=RES_SWIRL, spriteEffect=trinity.TR2_SFX_MODULATE, blendMode=trinity.TR2_SBM_ADDX2, color=self.GetSwirlColor(), opacity=0.0)
        animations.MorphScalar(self.swirlPrimary, 'rotation', startVal=0.0, endVal=-2.0 * math.pi, duration=80.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        animations.SpSecondaryTextureRotate(self.swirlSecondary, endVal=-2.0 * math.pi, duration=40.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        animations.SpSecondaryTextureScale(self.swirlSecondary, startVal=(0.8, 0.8), endVal=(1.2, 1.2), duration=35.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        self.itemIcon = ItemIcon(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=64, height=64, showOmegaOverlay=False)
        self.box = SpriteThemeColored(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 70, 70), texturePath=RES_INPUT_FRAME, opacity=0.5, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.errorFrame = ErrorFrame(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 64, 64), opacity=0.0, opacityHigh=0.2, opacityLow=0.1, color=COLOR_NEGATIVE)
        self.bgGrid = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 64, 64), texturePath=RES_INPUT_BACKGROUND, opacity=0.0)
        Fill(parent=self, align=uiconst.CENTER, pos=(0, 0, 64, 64), color=Color.BLACK, opacity=0.2)
        self.bgCircle = SpriteThemeColored(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=400, height=400, texturePath=RES_INPUT_RING, textureSecondaryPath=RES_RING_GLOW_MASK, spriteEffect=trinity.TR2_SFX_MODULATE, opacity=0.0, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.bgCircleUnderlay = SpriteThemeColored(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=400, height=400, texturePath=RES_INPUT_RING, opacity=0.6, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)

    def Load(self):
        if self._selectedTypeID is not None:
            self.itemIcon.SetTypeID(self._selectedTypeID)
            if self._isAvailable:
                self.itemIcon.opacity = 1.0
                self.errorFrame.Hide()
            else:
                self.itemIcon.opacity = 0.5
                self.errorFrame.Show()

    def AnimUpdateItemIcon(self):
        animations.FadeOut(self.bgCircle, duration=0.3, callback=self.bgCircle.StopAnimations)
        if self._selectedTypeID is None:
            self.itemIcon.opacity = 0.0
            self.errorFrame.Hide()
            animations.FadeOut(self.bgGrid, duration=0.3)
        else:
            self.itemIcon.SetTypeID(self._selectedTypeID)
            if self._isAvailable:
                opacity = 1.0
                self.errorFrame.Hide()
            else:
                opacity = 0.5
                self.errorFrame.Show()
            animations.FadeTo(self.itemIcon, endVal=opacity, duration=0.3, curveType=uiconst.ANIM_OVERSHOT5, timeOffset=0.1)
            animations.Tr2DScaleIn(self.itemIcon.icon, scaleCenter=(0.5, 0.5), duration=0.2)
            animations.FadeTo(self.bgGrid, startVal=self.bgGrid.opacity, endVal=0.8, duration=0.2)

    def AnimShowDragHint(self):
        animations.FadeTo(self.box, startVal=self.box.opacity, endVal=1.0, duration=0.3)
        animations.FadeTo(self.bgCircle, startVal=0.0, endVal=10.0, duration=1.6, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        animations.MorphVector2(self.bgCircle, 'scaleSecondary', startVal=(1.1, 1.1), endVal=(2.5, 2.5), duration=1.6, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)

    def AnimHideDragHint(self):
        self.bgCircle.StopAnimations()
        self.box.StopAnimations()
        animations.FadeTo(self.bgCircle, startVal=self.bgCircle.opacity, endVal=0.0, duration=0.6)
        animations.FadeTo(self.box, startVal=self.box.opacity, endVal=0.5, duration=0.3)

    def AnimCraft(self):
        self.Disable()
        animations.FadeOut(self.itemIcon, duration=0.3)
        animations.MorphScalar(self.itemIcon, 'width', startVal=64, endVal=55, duration=0.5)
        animations.MorphScalar(self.itemIcon, 'height', startVal=64, endVal=55, duration=0.5)
        animations.FadeTo(self.swirlPrimary, startVal=self.swirlPrimary.opacity, endVal=1.6, duration=2.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        animations.FadeTo(self.swirlSecondary, startVal=self.swirlSecondary.opacity, endVal=4.0, duration=1.0)
        animations.SpSecondaryTextureRotate(self.swirlSecondary, startVal=self.swirlSecondary.rotationSecondary, endVal=self.swirlSecondary.rotationSecondary - 2.0 * math.pi, duration=22.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        animations.FadeIn(self.swirlTiny, duration=0.8, curveType=uiconst.ANIM_OVERSHOT5)
        animations.SpSecondaryTextureRotate(self.swirlTiny, endVal=-2.0 * math.pi, duration=7.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        attributeCount = len(self.controller.GetModifiedAttributeIDs())
        animationFactor = 1.0 if not MUTATOR_FAST_ANIMATIONS_SETTING.is_enabled() else 10.0
        duration = 1.5 + (attributeCount - 1) * 1.2 / animationFactor
        blue.pyos.synchro.SleepWallclock(duration * 1000)
        if self.destroyed:
            return
        self.itemIcon.SetTypeID(self.controller.resultTypeID)
        self.Enable()
        animations.FadeTo(self.bgCircle, startVal=0.0, endVal=10.0, duration=1.6, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        animations.MorphVector2(self.bgCircle, 'scaleSecondary', startVal=(2.5, 2.5), endVal=(1.1, 1.1), duration=1.6, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        animations.FadeTo(self.itemIcon, duration=0.3, curveType=uiconst.ANIM_OVERSHOT5, timeOffset=0.1)
        animations.MorphScalar(self.itemIcon, 'width', startVal=55, endVal=64, duration=0.4)
        animations.MorphScalar(self.itemIcon, 'height', startVal=55, endVal=64, duration=0.4, callback=self.controller.SetResultPresented)
        animations.FadeOut(self.swirlTiny, duration=0.5)
        animations.FadeTo(self.swirlPrimary, startVal=self.swirlPrimary.opacity, endVal=1.0, duration=3.0)
        animations.FadeTo(self.swirlSecondary, startVal=self.swirlSecondary.opacity, endVal=0.0, duration=3.0, sleep=True)
        if self.destroyed:
            return
        animations.SpSecondaryTextureRotate(self.swirlSecondary, startVal=self.swirlSecondary.rotationSecondary, endVal=self.swirlSecondary.rotationSecondary - 2.0 * math.pi, duration=40.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        animations.FadeIn(self.swirlSecondary, duration=3.0)

    def AnimUpdateSwirl(self):
        newColor = self.GetSwirlColor()
        animations.SpColorMorphTo(self.swirlPrimary, endColor=newColor, duration=0.5)
        animations.SpColorMorphTo(self.swirlSecondary, endColor=newColor, duration=0.5)
        animations.SpColorMorphTo(self.swirlTiny, endColor=newColor, duration=0.5)

    def LoadTooltipPanel(self, panel, owner):
        panel.SetState(uiconst.UI_NORMAL)
        panel.margin = (8, 8, 8, 8)
        if self.controller.IsCraftingResultAvailable():
            name = evetypes.GetName(self.controller.resultTypeID)
            panel.AddLabelMedium(text=name)
        else:
            SourceItemScrollList(parent=panel, align=uiconst.TOPLEFT, width=250, height=200, controller=self.controller)

    def OnChange(self):
        if self.controller.isResultPresented:
            return
        if self.controller.IsCraftingResultAvailable():
            self._selectedTypeID = self.controller.resultTypeID
            self._isAvailable = True
            uthread.new(self.AnimCraft)
        elif self._selectedTypeID != self.controller.sourceTypeID or self._isAvailable != self.controller.IsSourceItemAvailable():
            self._selectedTypeID = self.controller.sourceTypeID
            self._isAvailable = self.controller.IsSourceItemAvailable()
            uthread.new(self.AnimUpdateItemIcon)
        if self._selectedMutatorID != self.controller.mutatorTypeID:
            self._selectedMutatorID = self.controller.mutatorTypeID
            uthread.new(self.AnimUpdateSwirl)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        animations.FadeTo(self.box, startVal=self.box.opacity, endVal=1.0, duration=0.2)

    def OnMouseExit(self, *args):
        animations.FadeTo(self.box, startVal=self.box.opacity, endVal=0.5, duration=0.3)

    def GetDragData(self, *args):
        if self.controller.IsCraftingResultAvailable():
            return [self.controller.GetResultDragData()]
        else:
            return []

    def GetSwirlColor(self):
        typeID = self.controller.mutatorTypeID
        if typeID in GetDecayedTypes():
            return COLOR_DECAYED
        elif typeID in GetGravidTypes():
            return COLOR_GRAVID
        elif typeID in GetUnstableTypes() or typeID in GetAbnormalTypes():
            return COLOR_UNSTABLE
        else:
            return Color.WHITE


class SourceItemScrollList(Scroll):
    default_multiSelect = False

    def ApplyAttributes(self, attributes):
        super(SourceItemScrollList, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        uthread.new(self.LoadSourceItemList)

    def LoadSourceItemList(self):
        self.ShowLoading()
        try:
            owned = {}
            unowned = {}
            for typeID in self.controller.GetApplicableTypes():
                if typeID == self.controller.sourceTypeID:
                    isOwned = self.controller.IsSourceItemAvailable()
                    itemID = self.controller.sourceItemID
                else:
                    isOwned = self.controller.IsItemAvailable(typeID)
                    itemID = None
                key = (evetypes.GetMetaLevel(typeID), evetypes.GetName(typeID))
                entry = GetFromClass(SourceItemEntry, {'typeID': typeID,
                 'itemID': itemID,
                 'label': evetypes.GetName(typeID),
                 'getIcon': True,
                 'isSelected': typeID == self.controller.sourceTypeID,
                 'isItemOwned': isOwned})
                if isOwned:
                    owned[key] = entry
                else:
                    unowned[key] = entry

        finally:
            self.HideLoading()

        entries = []
        if owned or unowned:
            text = localization.GetByLabel('UI/DynamicItem/SourceItemListHeader')
            entry = GetFromClass(HeaderEntry, {'text': text})
            entries.append(entry)
        if owned:
            entries.extend(sortedValuesByKey(owned))
        if unowned:
            if owned:
                entries.append(GetFromClass(Space, {'height': 8}))
            entries.extend(sortedValuesByKey(unowned))
        self.Load(contentList=entries)
        self.ScrollToSelectedNode()

    def OnSelectionChange(self, nodes):
        if not nodes:
            return
        data = nodes[0]
        item = Item(typeID=data.typeID, itemID=data.itemID)
        self.controller.SelectSourceItem(item)

    def Prepare_Underlay_(self):
        pass


def sortedValuesByKey(dictionary):
    for _, entry in sorted(dictionary.items(), key=lambda x: x[0]):
        yield entry


class HeaderEntry(Text):

    def Startup(self, *args):
        super(HeaderEntry, self).Startup(*args)
        self.sr.text.align = uiconst.TOPLEFT
        self.sr.text.padLeft = -8
        self.sr.text.state = uiconst.UI_DISABLED

    def GetHeight(self, *args):
        node, width = args
        textHeight = uix.GetTextHeight(node.text, maxLines=1)
        node.height = 4 + textHeight
        return node.height

    def GetMenu(self):
        return []


class SourceItemEntry(item_entry.Item):

    def Load(self, node):
        super(SourceItemEntry, self).Load(node)
        if not node.isItemOwned:
            self.sr.icon.opacity = self.sr.label.opacity = 0.25

    def UpdateAlignment(self, *args):
        budget = super(SourceItemEntry, self).UpdateAlignment(*args)
        budgetLeft, budgetTop, budgetWidth, budgetHeight, sizeChange = budget
        self.sr.label.SetRightAlphaFade(budgetWidth - 54, 16)
        return budget


class AttributeEntry(Container):
    default_clipChildren = False
    default_height = 48

    def ApplyAttributes(self, attributes):
        super(AttributeEntry, self).ApplyAttributes(attributes)
        self.attributeID = attributes.attributeID
        self.controller = attributes.controller
        self._animIndex = attributes.get('animationIndex', 0)
        self._lastSourceTypeID = self.controller.sourceTypeID
        self._lastMutatorTypeID = self.controller.mutatorTypeID
        self.Layout()
        uthread.new(self.Load)

    @property
    def label(self):
        return dogma_data.get_attribute_display_name(self.attributeID)

    def Layout(self):
        self.valueLabel = None
        self.bgFill = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT)
        iconCont = Container(parent=self, align=uiconst.TOLEFT, width=46)
        self.icon = Icon(parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, size=32)
        self.nameLabel = eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, top=6, singleline=True, opacity=self.GetNameLabelOpacity())
        self.nameLabel.SetRightAlphaFade(fadeEnd=200, maxFadeWidth=10)
        self.mutationBar = MutationBar(parent=self, align=uiconst.TOBOTTOM, idx=0, controller=self.controller, attributeID=self.attributeID, animationIndex=self._animIndex)

    def Load(self):
        self.icon.LoadIcon(dogma_data.get_attribute_icon_id(self.attributeID))
        self.nameLabel.SetText(dogma_data.get_attribute_display_name(self.attributeID))
        self.nameLabel.SetHint(dogma_data.get_attribute_display_name(self.attributeID))
        self.UpdateAttributeValue()

    def SetAnimationIndex(self, index):
        self._animIndex = index
        self.mutationBar.SetAnimationIndex(index)

    def ConstructValueLabel(self):
        attribute = self.controller.GetAttribute(self.attributeID)
        if self.controller.IsCraftingResultAvailable():
            return FinalAttributeValueLabel(parent=self, align=uiconst.TOTOP_NOPUSH, height=16, controller=self.controller, attributeID=self.attributeID, value=attribute.value)
        if self.controller.IsSourceItemSelected():
            text = self._FormatAttributeRange(attribute)
        else:
            low, high = self.controller.GetAttributeBonusRange(self.attributeID)
            text = FormatAttributeBonusRange(self.attributeID, low, high)
        return eveLabel.EveLabelMedium(parent=self, align=uiconst.TOTOP_NOPUSH, text=text)

    def GetNameLabelOpacity(self):
        if self.controller.IsCraftingResultAvailable():
            return 0.6
        else:
            return 1.0

    def UpdateAttributeValue(self):
        if self.valueLabel:
            self.valueLabel.Close()
        self.valueLabel = self.ConstructValueLabel()

    def AnimEnter(self):
        animations.FadeTo(self, duration=0.3, timeOffset=self._animIndex * 0.05)

    def AnimUpdateAttributeValue(self):
        if self.valueLabel:
            animations.FadeOut(self.valueLabel, duration=0.1, sleep=True)
        if self.destroyed:
            return
        self.UpdateAttributeValue()
        animations.FadeTo(self.valueLabel, duration=0.25, curveType=uiconst.ANIM_OVERSHOT2, timeOffset=self._animIndex * 0.05)
        animations.FadeTo(self.nameLabel, startVal=self.nameLabel.opacity, endVal=self.GetNameLabelOpacity(), duration=0.3)

    def AnimShowFinalValue(self):
        animations.FadeOut(self.valueLabel, duration=0.05, sleep=True)
        if self.destroyed:
            return
        self.UpdateAttributeValue()
        attribute = self.controller.GetAttribute(self.attributeID)
        self.valueLabel.value = attribute.sourceValue
        animationFactor = 1.0 if not MUTATOR_FAST_ANIMATIONS_SETTING.is_enabled() else 10.0
        uthread.new(self.valueLabel.AnimSetValue, attribute.value, duration=1.5, timeOffset=self._animIndex * 1.2 / animationFactor)
        animations.FadeTo(self.nameLabel, startVal=self.nameLabel.opacity, endVal=self.GetNameLabelOpacity(), duration=0.3, timeOffset=self._animIndex * 1.2 / animationFactor)
        animations.FadeTo(self.valueLabel, startVal=0.0, endVal=1.0, duration=1.5, curveType=uiconst.ANIM_OVERSHOT2, timeOffset=self._animIndex * 1.2 / animationFactor)
        animations.MorphScalar(self.valueLabel, 'left', startVal=-10, endVal=0, duration=0.2, timeOffset=self._animIndex * 1.2 / animationFactor)
        animations.FadeTo(self.bgFill, startVal=self.bgFill.opacity, endVal=self.bgFill.opacity + 0.2, duration=0.25, curveType=uiconst.ANIM_WAVE, timeOffset=1.5 + self._animIndex * 1.2 / animationFactor)

    def _FormatAttributeRange(self, attribute):
        negativeColor = Color(*COLOR_NEGATIVE).GetHex()
        positiveColor = Color(*COLOR_POSITIVE).GetHex()
        if not attribute.highIsGood:
            negativeColor, positiveColor = positiveColor, negativeColor
        if attribute.mutationLow < attribute.sourceValue:
            lowColor = negativeColor
        else:
            lowColor = positiveColor
        if attribute.mutationHigh < attribute.sourceValue:
            highColor = negativeColor
        else:
            highColor = positiveColor
        template = u'<color={colorLow}>{low}</color> - <color={colorHigh}>{high}</color>'
        return template.format(low=attribute.displayMutationLow, high=attribute.displayMutationHigh, colorLow=lowColor, colorHigh=highColor)

    def OnChange(self):
        if self.controller.isResultPresented:
            return
        if self.controller.IsCraftingResultAvailable():
            self._lastSourceTypeID = None
            self._lastMutatorTypeID = None
            uthread.new(self.AnimShowFinalValue)
        elif self._lastSourceTypeID != self.controller.sourceTypeID or self._lastMutatorTypeID != self.controller.mutatorTypeID:
            uthread.new(self.AnimUpdateAttributeValue)
            self._lastSourceTypeID = self.controller.sourceTypeID
            self._lastMutatorTypeID = self.controller.mutatorTypeID


class FinalAttributeValueLabel(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(FinalAttributeValueLabel, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.attributeID = attributes.attributeID
        self._value = attributes.value
        self.Layout()
        self.UpdateValueLabel()

    def Layout(self):
        self.valueLabel = eveLabel.EveLabelLargeBold(parent=self, align=uiconst.BOTTOMLEFT, autoFitToText=True)
        self.diffLabel = eveLabel.EveLabelSmall(parent=self, align=uiconst.BOTTOMLEFT, top=1, opacity=0.0)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.UpdateValueLabel()

    def AnimSetValue(self, value, duration = 0.5, timeOffset = 0.0):
        base = self.value or 0.0
        animations.FadeOut(self.diffLabel, duration=0.05)
        animations.MorphScalar(self, 'value', startVal=base, endVal=value, duration=duration, timeOffset=timeOffset, sleep=True)
        if self.destroyed:
            return
        self.value = value
        self.SetDiff(value - base)
        animations.FadeIn(self.diffLabel, duration=0.2)

    def SetDiff(self, diff):
        attribute = self.controller.GetAttribute(self.attributeID)
        diffStr = attribute.FormatDiff(diff)
        if attribute.isMutationPositive:
            color = Color(*COLOR_POSITIVE).GetHex()
        else:
            color = Color(*COLOR_NEGATIVE).GetHex()
        text = u'<color={color}>({diff})</color>'.format(color=color, diff=diffStr)
        self.diffLabel.SetText(text)
        self.diffLabel.left = self.valueLabel.textwidth + 8

    def UpdateValueLabel(self):
        attribute = self.controller.GetAttribute(self.attributeID)
        self.valueLabel.SetText(attribute.Format(self.value))


class MutationBar(Container):
    default_height = 4
    default_clipChildren = False

    def ApplyAttributes(self, attributes):
        super(MutationBar, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.attributeID = attributes.attributeID
        self._lastAttribute = self.controller.GetAttribute(self.attributeID)
        self._animationIndex = attributes.get('animationIndex', 0)
        self.Layout()
        self.controller.onChange.connect(self.OnChange)

    def Layout(self):
        FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.barPin = Container(parent=self, align=uiconst.TOPLEFT_PROP, left=0.5, height=1.0, width=1.0, opacity=0.0)
        self.barPip = Fill(parent=self.barPin, align=uiconst.TOPLEFT, height=self.height, width=1, color=(0.7, 0.7, 0.7, 1.0))
        self.barFill = Sprite(parent=self, align=uiconst.TOLEFT_PROP, left=0.5, width=0.0, texturePath=RES_BAR_FILL, tileX=True)

    def SetAnimationIndex(self, index):
        self._animationIndex = index

    def AnimUpdateBar(self):
        attribute = self.controller.GetAttribute(self.attributeID)
        attributeValuesDiffer = self._lastAttribute is not None and self._lastAttribute.value is not None and self._lastAttribute.value != attribute.value
        if attributeValuesDiffer:
            self.AnimHideBar()
        if self.destroyed:
            return
        if attribute is not None and attribute.value is not None:
            self.AnimShowBar()
        self._lastAttribute = attribute

    def AnimHideBar(self):
        animations.MorphScalar(self.barFill, 'width', startVal=self.barFill.width, endVal=0.0, duration=0.1)
        animations.MorphScalar(self.barPin, 'left', startVal=self.barPin.left, endVal=0.5, duration=0.1)
        animations.FadeOut(self.barPin, duration=0.05, sleep=True, timeOffset=0.1)

    def AnimShowBar(self):
        attribute = self.controller.GetAttribute(self.attributeID)
        trueSource = max(attribute.sourceValue, attribute.mutationMin)
        if attribute.isMutationPositive:
            self.barFill.align = uiconst.TOLEFT_PROP
            self.barFill.SetRGB(*COLOR_POSITIVE)
            self.barFill.rotation = 0.0
            rangeWidth = abs(attribute.mutationHigh - trueSource)
        else:
            self.barFill.align = uiconst.TORIGHT_PROP
            self.barFill.SetRGB(*COLOR_NEGATIVE)
            self.barFill.rotation = math.pi
            rangeWidth = abs(attribute.mutationLow - trueSource)
        animationFactor = 1.0 if not MUTATOR_FAST_ANIMATIONS_SETTING.is_enabled() else 10.0
        animations.FadeTo(self.barPin, startVal=0.0, endVal=1.0, duration=0.05, timeOffset=self._animationIndex * 1.2 / animationFactor)
        animations.FadeTo(self.barPip, startVal=self.barPip.opacity, endVal=2.0, duration=0.2, curveType=uiconst.ANIM_WAVE, timeOffset=1.5 + self._animationIndex * 1.2 / animationFactor)
        if rangeWidth > 0.0:
            width = abs(attribute.value - trueSource) / rangeWidth
        else:
            width = 0.0
        sign = 1.0 if attribute.isMutationPositive else -1.0
        animations.MorphScalar(self.barPin, 'left', startVal=0.5, endVal=0.5 + sign * (width / 2.0), duration=1.5, timeOffset=self._animationIndex * 1.2 / animationFactor)
        animations.MorphScalar(self.barFill, 'width', startVal=0.0, endVal=width / 2.0, duration=1.5, timeOffset=self._animationIndex * 1.2 / animationFactor)

    def OnChange(self):
        if self.controller.isResultPresented:
            return
        uthread.new(self.AnimUpdateBar)


class BuildButton(PrimaryButton):

    def ApplyAttributes(self, attributes):
        super(BuildButton, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.UpdateState()
        self.controller.onChange.connect(self.UpdateState)

    def ClickFunc(self, *args):
        if self.controller.isResultPresented:
            self.controller.Reset()
        else:
            self.controller.ExecuteCrafting()

    def GetColor(self):
        return sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)

    def GetText(self):
        if self.controller.isResultPresented:
            return localization.GetByLabel('UI/DynamicItem/Continue')
        else:
            return localization.GetByLabel('UI/DynamicItem/Mutate')

    def IsActive(self):
        if self.controller.isResultPresented:
            return True
        elif self.controller.IsCraftingResultAvailable():
            return False
        elif not self.controller.IsMutatorAvailable():
            return False
        elif self.controller.IsSourceItemAvailable():
            return True
        else:
            return False

    def IsBlinking(self):
        return False

    def IsErrorPresent(self):
        if not self.controller.IsMutatorAvailable():
            return True
        if not self.controller.IsSourceItemSelected():
            return False
        if not self.controller.IsSourceItemAvailable():
            return True
        return False

    def UpdateIsEnabledByState(self):
        if self.IsActive():
            self.Enable()
        else:
            self.Disable()

    def UpdateBlinkByState(self):
        pass

    def OnColorThemeChanged(self):
        self.UpdateState()

    def LoadTooltipPanel(self, panel, owner):
        panel.margin = (8, 8, 8, 0)
        if not self.controller.IsMutatorAvailable():
            panel.AddLabelMedium(text=localization.GetByLabel('UI/DynamicItem/ErrorMutatorNotAvailable'), width=200, padBottom=8)
        if not self.controller.IsSourceItemSelected():
            panel.AddLabelMedium(text=localization.GetByLabel('UI/DynamicItem/ErrorSourceItemNotSelected'), width=200, padBottom=8)
        elif not self.controller.IsSourceItemAvailable():
            panel.AddLabelMedium(text=localization.GetByLabel('UI/DynamicItem/ErrorSourceItemNotAvailable'), width=200, padBottom=8)


def __SakeReloadHook():
    try:
        instance = CraftingWindow.GetIfOpen()
        if instance:
            CraftingWindow.Reload(instance)
    except Exception:
        import log
        log.LogException()
