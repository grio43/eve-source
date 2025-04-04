#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\reprocessing\ui\reprocessingWnd.py
from math import pi
import carbonui.const as uiconst
import evetypes
import trinity
from carbonui.control.combo import Combo
from carbonui.primitives.flowcontainer import FlowContainer
from eve.client.script.ui.util import uix
import uthread
from menu import MenuLabel, MenuList
from carbon.common.script.util.format import FmtAmt
from carbonui.const import CENTER
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from dogma.const import attributeRefiningYieldMutator
from carbonui.control.button import Button
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, EveLabelMedium, EveLabelMediumBold, EveLabelSmallBold, Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import GradientThemeColored
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from eve.common.lib.appConst import singletonBlueprintCopy
from eve.common.script.sys.eveCfg import GetActiveShip
from eve.common.script.util.eveFormat import FmtISKAndRound, FmtISK
from eveservices.menu import GetMenuService
from inventorycommon.const import categoryAsteroid, categoryBlueprint
from inventorycommon.const import flagCorpSAGsExcludingProjects, flagHangar, corpDivisionsByFlag
from localization import GetByLabel
from reprocessing.ui.const import STATE_REPROCESS, STATE_RESTRICTED, STATE_SUSPICIOUS
from reprocessing.ui.containerCreator import ContainerCreator, Containers
from reprocessing.ui.controller import Controller, NodesToItems
from reprocessing.ui.grouper import GetCategoryGrouper, GetGroupGrouper
from reprocessing.ui.inputGroups import InputGroups
from reprocessing.ui.inputItemAdder import InputItemAdder
from reprocessing.ui.itemContainers import InputItemContainerInterface, ItemContainerInterface
from reprocessing.ui.itemReprocessor import ItemReprocessor
from reprocessing.ui.outputItemAdder import OutputItemAdder, MaterialFetcher
from reprocessing.ui.quotes import Quotes
from reprocessing.ui.states import States
from reprocessing.ui.tileplacer import TilePlacer
from reprocessing.ui.util import GetSkillFromTypeID, GetAttributeSkillsFromTypeID, GetSkillFromCategoryID
from uthread2 import start_tasklet
from utillib import KeyVal
TILE_SIZE = 52
ICON_SIZE = 48
COL_YELLOW = (1.0, 0.7, 0.0)
COL_RED = (1.0, 0.0, 0.06)
COL_GREEN = (0.3, 0.9, 0.1)
COL_BLUE = (0.298, 0.549, 0.69, 1.0)
COL_LIGHTBLUE = (0.765, 0.914, 1.0, 1.0)

class ReprocessingWnd(Window):
    __guid__ = 'form.ReprocessingWnd'
    default_width = 600
    default_height = 400
    default_minSize = (default_width, default_height)
    default_windowID = 'reprocessingWindow'
    default_descriptionLabelPath = 'Tooltips/StationServices/ReprocessingPlant_description'
    default_captionLabelPath = 'UI/Station/ReprocessingPlant'
    default_iconNum = 'res:/UI/Texture/WindowIcons/Reprocess.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.preSelectedItems = attributes.selectedItems
        self.outputPrice = 0
        self.outputItemsCount = 0
        mainCont = Container(name='mainCont', parent=self.sr.main, padding=uiconst.defaultPadding)
        self.bottomContainer = bottomCont = Container(name='bottomCont', parent=mainCont, align=uiconst.TOBOTTOM, height=36)
        reprocessingCont = Container(name='reprocessingCont', parent=mainCont, align=uiconst.TOALL)
        inputCont = Container(name='inputCont', parent=reprocessingCont, align=uiconst.TOLEFT_PROP, width=0.48)
        outputCont = Container(name='outputCont', parent=reprocessingCont, align=uiconst.TORIGHT_PROP, width=0.48)
        self.inputInfoCont = ReprocessInputContainer(name='inputInfo', parent=inputCont, dropFunc=self.AddItemByDrag, removeFunc=self.RemoveItem)
        self.outputInfoCont = ReprocessOutputContainer(name='outputInfo', parent=outputCont)
        self.loadingOverlay = Container(parent=self.inputInfoCont, idx=0)
        Fill(bgParent=self.loadingOverlay, color=(0.0, 0.0, 0.0, 0.3))
        LoadingWheel(name='loadingWheel', parent=self.loadingOverlay, align=uiconst.CENTER, width=80, height=80, state=uiconst.UI_DISABLED)
        self.loadingOverlay.opacity = 0.0
        self.controller = CreateReprocessingWindowController(self, self.inputInfoCont, self.outputInfoCont, sm.GetService('invCache'), sm.GetService('reprocessing'), GetActiveShip)
        self.inputInfoCont.captionLabel.text = GetByLabel('UI/Reprocessing/ReprocessingWindow/InputMaterials')
        self.outputInfoCont.captionLabel.text = GetByLabel('UI/Reprocessing/ReprocessingWindow/OutputResults')
        btnCont = Container(name='buttonCont', parent=bottomCont, align=uiconst.TOBOTTOM, height=36, idx=0, padding=(-4, 3, -4, -2))
        GradientThemeColored(bgParent=btnCont)
        self.reprocessButton = Button(parent=btnCont, name='reprocessButton', uniqueUiName=pConst.UNIQUE_NAME_REPROCESS_BUTTON, label=GetByLabel('UI/Reprocessing/ReprocessingWindow/ReprocessButton'), func=self.ReprocessItems, align=uiconst.CENTERRIGHT, fixedheight=28, left=8)
        left = self.reprocessButton.left + self.reprocessButton.width
        self.totalIskCostLabel = EveLabelMedium(parent=btnCont, text='', align=uiconst.CENTERRIGHT, left=left + 8, color=COL_RED)
        self.cancelButton = Button(parent=btnCont, label=GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel, align=uiconst.CENTERLEFT, fixedheight=28, left=8)
        self.DisableReprocessButton(disable=True)
        if self.preSelectedItems:
            start_tasklet(self.AddPreselectedItems, self.preSelectedItems)

    def ShowInputLoading(self):
        self.inputInfoCont.overlayCont.display = False
        uicore.animations.FadeIn(self.loadingOverlay, endVal=1.0, duration=0.2)

    def HideInputLoading(self):
        uicore.animations.FadeOut(self.loadingOverlay, duration=0.2)

    def DisableReprocessButton(self, disable):
        if disable:
            self.reprocessButton.Disable()
            self.reprocessButton.hint = GetByLabel('UI/Reprocessing/ReprocessingWindow/NoReprocessableItems')
        else:
            self.reprocessButton.Enable()
            self.reprocessButton.hint = ''

    def AddPreselectedItems(self, items):
        self.controller.AddItems(items)
        outputItems = self.outputInfoCont.GetItems()
        if self.reprocessButton.disabled and len(outputItems):
            self.DisableReprocessButton(disable=False)

    def RemoveItem(self, itemID):
        self.controller.RemoveItem(itemID)
        outputItems = self.controller.GetOutputItems()
        if len(outputItems) == 0:
            self.DisableReprocessButton(True)

    def AddItemByDrag(self, dragObj, nodes):
        self.controller.AddItems(NodesToItems(nodes))
        outputItems = self.outputInfoCont.GetItems()
        if self.reprocessButton.disabled and len(outputItems):
            self.DisableReprocessButton(disable=False)
        self.cancelButton.SetLabel(GetByLabel('UI/Common/Buttons/Cancel'))

    def Cancel(self, *args):
        self.CloseByUser()

    def GetOutputItems(self):
        return []

    def ReprocessItems(self, *args):
        reprocessed, remaining = self.controller.Reprocess(*self.outputInfoCont.outputCombo.GetValue())
        self.DisableReprocessButton(disable=True)
        self.cancelButton.SetLabel(GetByLabel('UI/Common/Buttons/Cancel'))
        for item in remaining:
            self.RemoveItem(item.itemID)

        self.controller.inputItems.ClearItems()
        self.controller.inputGroups.ClearAllGroups()
        self.outputInfoCont.AnimateOutputItems()
        self.outputInfoCont.FadeOutOutputItems()
        self.outputInfoCont.FadeHeaders()
        if reprocessed:
            self.outputInfoCont.overlayCont.display = True

    def UpdateTotalIskCost(self, iskCost):
        self.totalIskCostLabel.SetText(FmtISK(-iskCost))

    def Close(self, *args, **kwargs):
        super(ReprocessingWnd, self).Close(*args, **kwargs)
        if self.controller:
            self.controller.Close()


class ReprocessingContainer(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        nameCont = Container(name='nameCont', parent=self, align=uiconst.TOTOP, height=18)
        self.infoCont = Container(name='infoCont', parent=self, align=uiconst.TOBOTTOM, height=54, clipChildren=True)
        self.groupContainers = {}
        self.overlayCont = Container(name='overlayCont', parent=self, align=uiconst.TOALL)
        self.CreateScrollContainer()
        self.captionLabel = EveLabelMediumBold(parent=nameCont, left=6)
        self.volumeLabel = EveLabelMedium(name='volumeLabel', parent=self.infoCont, align=uiconst.BOTTOMRIGHT, left=5, top=4)
        self.totalPriceLabel = EveLabelMedium(name='totalPriceLabel', parent=self.infoCont, align=uiconst.BOTTOMRIGHT, left=5, top=20)
        self.numItemsLabel = EveLabelMedium(name='numItemsLabel', parent=self.infoCont, align=uiconst.BOTTOMRIGHT, left=5, top=36)

    def CreateScrollContainer(self):
        self.scrollCont = ScrollContainer(parent=self, align=uiconst.TOALL, showUnderlay=True)

    def UpdateItemInfo(self, outputPrice, numberOfItems, volume = None, iskCost = 0.0):
        self.totalPriceLabel.text = GetByLabel('UI/Inventory/EstIskPrice', iskString=FmtISKAndRound(outputPrice, False))
        self.numItemsLabel.text = GetByLabel('UI/Inventory/NumItems', numItems=numberOfItems, numFilteredTxt='')
        if volume is not None:
            self.volumeLabel.text = GetByLabel('UI/Reprocessing/ReprocessingWindow/TotalVolume', volume=FmtAmt(volume, showFraction=2))

    def RemoveGroup(self, groupID):
        group = self.groupContainers.pop(groupID)
        group.Close()

    def AddItem(self, groupID, (ctrlID, item)):
        self.groupContainers[groupID].tilePlacer.AddItem(ctrlID, item)
        self.overlayCont.display = False

    def ClearAllItems(self):
        for group in self.groupContainers.values():
            group.tilePlacer.Clear()
            group.Close()


class ReprocessInputContainer(ReprocessingContainer):

    def ApplyAttributes(self, attributes):
        ReprocessingContainer.ApplyAttributes(self, attributes)
        self.removeFunc = attributes.removeFunc
        self.scrollCont.name = 'inputScroll'
        self.scrollCont.Copy = self.CopyInput
        self.scrollCont.OnDropData = self.OnDroppingItems
        self.parentDropFunc = attributes.dropFunc
        self.volumeLabel.display = False
        self.UpdateItemInfo(0, 0)
        self.overlayCont.GetAbsoluteSize()
        self.scrollCont.ShowNoContentHint(GetByLabel('UI/Reprocessing/ReprocessingWindow/DropHereToReprocess'))

    def AddGroup(self, groupID, groupName):
        self.groupContainers[groupID] = ReprocessingInputGroupContainer(parent=self.scrollCont, align=uiconst.TOTOP, percentage=0.5, groupID=groupID, groupName=groupName)

    def AddItem(self, groupID, (ctrlID, item)):
        self.scrollCont.HideNoContentHint()
        ReprocessingContainer.AddItem(self, groupID, (ctrlID, item))
        item.OnDropData = self.OnDroppingItems
        item.GetMenu = lambda *args: self.GetItemMenu(ctrlID, item.typeID)
        self.groupContainers[groupID].tilePlacer.mainContainer.OnDropData = self.OnDroppingItems

    def OnDroppingItems(self, dragObj, nodes):
        if self.parentDropFunc:
            self.parentDropFunc(dragObj, nodes)

    def GetItemMenu(self, itemID, typeID):
        menu = MenuList()
        menu += GetMenuService().GetMenuFromItemIDTypeID(itemID, typeID, includeMarketDetails=True)
        menu.append((GetByLabel('UI/Generic/RemoveItem'), self.removeFunc, (itemID,)))
        return menu

    def AnimateItems(self):
        for group in self.groupContainers.itervalues():
            inputItems = group.tilePlacer.GetItems()
            timeOffset = 0.2 / len(inputItems)
            funcs = [ (self.GrayOutItem, (item,)) for item in inputItems ]
            uthread.parallel(funcs)
            for item in inputItems:
                uicore.animations.FadeOut(item, duration=timeOffset, sleep=True)

        for groupID, group in self.groupContainers.items():
            group.Close()

        self.groupContainers = {}

    def GrayOutItem(self, item):
        animateCall = lambda cont: uicore.animations.MorphScalar(cont, attrName='saturation', startVal=1.0, endVal=0.0, duration=0.3, sleep=True)
        uthread.parallel([(animateCall, (item.icon,)), (animateCall, (item.techIcon,))])

    def SetEfficiency(self, group, efficiency, typeIDs):
        self.groupContainers[group].SetEfficiency(efficiency, typeIDs)

    def SetTaxAndStationEfficiency(self, group, efficiency, tax):
        self.groupContainers[group].SetTaxAndStationEfficiency(efficiency, tax)

    def CopyInput(self):
        allItems = []
        groupConts = self.groupContainers.values()
        groupConts.sort(key=lambda x: x.GetOrder())
        for group in groupConts:
            inputItems = group.tilePlacer.GetItems()
            allItems += inputItems

        CopyItemsToClipboard(allItems)


class ReprocessOutputContainer(ReprocessingContainer):

    def ApplyAttributes(self, attributes):
        ReprocessingContainer.ApplyAttributes(self, attributes)
        self.scrollCont.name = 'outputScroll'
        self.scrollCont.Copy = self.CopyOutput
        self.volumeLabel.display = True
        self.UpdateItemInfo(0, 0, 0)
        self.overlayCont.display = False
        w, h = self.overlayCont.GetAbsoluteSize()
        overlayLabel = EveCaptionMedium(name='overlayLabel', parent=self.overlayCont, align=uiconst.CENTER)
        overlayLabel.text = GetByLabel('UI/Reprocessing/ReprocessingWindow/OutputTransferredTo')
        self.overlayLabel2 = EveLabelMediumBold(name='overlayLabel2', parent=self.overlayCont, align=uiconst.CENTER, top=20, state=uiconst.UI_NORMAL)
        self.overlayLabel2.text = GetByLabel('UI/Inventory/ItemHangar')
        self.overlayLabel2.OnClick = uicore.cmd.OpenInventory
        self._CreateOutputCombo()

    def _CreateOutputCombo(self):
        hangarValue = (session.stationid or session.structureid, flagHangar)
        sameLocationValue = (None, None)
        comboOptions = [(GetByLabel('UI/Reprocessing/ReprocessingWindow/InputLocationComboBoxLabel'),
          sameLocationValue,
          None,
          None,
          0), (GetByLabel('UI/Inventory/ItemHangar'),
          hangarValue,
          None,
          'res:/ui/Texture/WindowIcons/itemHangar.png',
          0)]
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        if office:
            officeLabel = GetByLabel('UI/Inventory/CorporationHangars')
            officeIcon = 'res:/UI/Texture/WindowIcons/corporation.png'
            comboOptions.append((officeLabel,
             None,
             None,
             officeIcon,
             0))
            divisions = sm.GetService('corp').GetDivisionNames()
            for flagID in flagCorpSAGsExcludingProjects:
                divID = corpDivisionsByFlag[flagID]
                comboOptions.append((divisions[divID + 1],
                 (office.officeID, flagID),
                 None,
                 officeIcon,
                 1))

        outputLabel = EveLabelSmallBold(name='overlayLabel', parent=self.infoCont, align=uiconst.CENTERLEFT, top=-5)
        outputLabel.text = GetByLabel('UI/Industry/OutputLocation')
        self.outputCombo = Combo(parent=self.infoCont, align=uiconst.BOTTOMLEFT, callback=self.OnCombo, height=22, width=120)
        self.outputCombo.LoadOptions(comboOptions, hangarValue)
        self.outputCombo.last_selected = hangarValue

    def OnCombo(self, comboBox, key, value):
        if value is None:
            comboBox.SelectItemByValue(comboBox.last_selected)
            return
        comboBox.last_selected = value
        flag = value[1]
        if not self.overlayCont.display:
            if flag in corpDivisionsByFlag:
                division = corpDivisionsByFlag[flag] + 1
                self.overlayLabel2.text = '%s - %s' % (GetByLabel('UI/Inventory/CorporationHangars'), sm.GetService('corp').GetDivisionNames()[division])
            else:
                self.overlayLabel2.text = key

    def AddGroup(self, groupID, groupName):
        self.groupContainers[groupID] = ReprocessingOutputGroupContainer(parent=self.scrollCont, align=uiconst.TOTOP, percentage=0.5, groupID=groupID, groupName=groupName)

    def AddItem(self, groupID, (ctrlID, item)):
        ReprocessingContainer.AddItem(self, groupID, (ctrlID, item))
        item.GetMenu = (self.GetItemMenu, ctrlID)

    @staticmethod
    def GetItemMenu(typeID):
        m = [(MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, (typeID,))]
        if evetypes.GetMarketGroupID(typeID) is not None:
            sm.GetService('marketutils').AddMarketDetailsMenuOption(m, typeID)
            m.append((MenuLabel('UI/Inventory/ItemActions/AddTypeToMarketQuickbar'), sm.GetService('marketutils').AddTypeToQuickBar, (typeID,)))
        return m

    def GetItems(self):
        items = []
        for group in self.groupContainers.itervalues():
            items.extend(group.tilePlacer.GetItems())

        return items

    def AnimateOutputItems(self):
        outputItems = self.GetItems()
        for item in outputItems:
            uicore.animations.BlinkOut(item.outputFrame, duration=0.7, loops=1, startVal=5.0)

    def FadeOutOutputItems(self):
        outputItems = self.GetItems()
        for item in outputItems:
            uicore.animations.FadeTo(item, duration=0.7, startVal=1.0, endVal=0.3)

    def FadeHeaders(self):
        for group in self.groupContainers.itervalues():
            group.header.headerText.opacity = 0.3

    def ShowItems(self):
        self.overlayCont.display = False
        for group in self.groupContainers.itervalues():
            group.header.headerText.opacity = 1.0

        for item in self.GetItems():
            item.opacity = 1.0

    def CopyOutput(self):
        CopyItemsToClipboard(self.GetItems())


class ReprocessingItemContainer(Container):
    default_width = 64
    default_height = 64
    default_align = uiconst.TOALL
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isSelected = False
        self.typeID = attributes.typeID
        typeName = evetypes.GetName(self.typeID)
        self.quantity = attributes.quantity
        self.stacksize = attributes.get('stacksize', None)
        self.itemState = attributes.get('itemState', None)
        singleton = attributes.get('singleton', 0)
        isBlueprint = evetypes.GetCategoryID(self.typeID) == categoryBlueprint
        isCopy = isBlueprint and singleton == singletonBlueprintCopy
        self.stateIcon = None
        self.spriteCont = self.spriteCont = Container(name='spriteCont', parent=self, align=CENTER, width=ICON_SIZE, height=ICON_SIZE, state=uiconst.UI_PICKCHILDREN)
        self.icon = Icon(name=typeName, parent=self.spriteCont, width=ICON_SIZE, height=ICON_SIZE, align=CENTER, state=uiconst.UI_DISABLED, saturation=1.0, effectOpacity=0.0, spriteEffect=trinity.TR2_SFX_SOFTLIGHT)
        self.icon.LoadIconByTypeID(typeID=self.typeID, ignoreSize=True, isCopy=isCopy)
        self.hint = typeName
        self.techIcon = Sprite(name='techIcon', parent=self.spriteCont, width=16, height=16, idx=0, saturation=1.0, effectOpacity=0.0, spriteEffect=trinity.TR2_SFX_SOFTLIGHT)
        uix.GetTechLevelIcon(self.techIcon, 0, self.typeID)
        if self.itemState:
            resPath, stateColor = self.GetStateResPathAndColor(self.itemState)
            self.stateIcon = Sprite(name='stateIcon', parent=self.spriteCont, width=32, height=32, idx=0, left=-4, top=-4, align=uiconst.TOPRIGHT, texturePath=resPath, color=stateColor, state=uiconst.UI_DISABLED)
        self.entryHilite = Sprite(name='hilite', align=uiconst.TOALL, parent=self.spriteCont, texturePath='res:/UI/Texture/classes/InvItem/bgHover.png', blendMode=trinity.TR2_SBM_ADD, opacity=0.0, idx=0, state=uiconst.UI_DISABLED)
        self.entryHilite.hint = typeName
        self.quantityParent = Container(parent=self, idx=0, name='qtyCont', pos=(3, 38, 32, 11), align=uiconst.TOPRIGHT, bgColor=(0, 0, 0, 0.95), state=uiconst.UI_HIDDEN)
        self.qtyLabel = Label(parent=self.quantityParent, left=2, maxLines=1, fontsize=9)
        self._SetQtyText()

    def _SetQtyText(self):
        if self.stacksize:
            numberOfItems = self.stacksize
        else:
            numberOfItems = self.quantity
        self.qtyLabel.text = FmtAmt(numberOfItems, 'ss')
        if numberOfItems:
            self.quantityParent.state = uiconst.UI_DISABLED
        else:
            self.quantityParent.state = uiconst.UI_HIDDEN

    def GetStateResPathAndColor(self, state):
        if state == STATE_REPROCESS:
            resPath = 'res:/UI/Texture/Reprocessing/Reprocess.png'
            stateColor = COL_GREEN
        elif state == STATE_RESTRICTED:
            resPath = 'res:/UI/Texture/Reprocessing/Restricted.png'
            stateColor = COL_RED
        elif state == STATE_SUSPICIOUS:
            resPath = 'res:/UI/Texture/Reprocessing/Suspicious.png'
            stateColor = COL_YELLOW
        return (resPath, stateColor)

    def BlinkHilite(self):
        uicore.animations.FadeIn(self.entryHilite, duration=0.5)

    def ShowHilited(self):
        uicore.animations.FadeIn(self.entryHilite, duration=0.2)

    def ShowNotHilited(self):
        uicore.animations.FadeOut(self.entryHilite, duration=0.2)


class ReprocessingInputItemContainer(ReprocessingItemContainer):
    isDragObject = True

    def ApplyAttributes(self, attributes):
        ReprocessingItemContainer.ApplyAttributes(self, attributes)
        self.getTypeAttribute = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute
        self.getSkillLevel = sm.GetService('skills').MySkillLevel
        self.itemID = attributes.itemID
        self.quantity = attributes.quantity
        self.outputMaterials = attributes.outputMaterials
        self.hintInfo = attributes.hintInfo
        self.onMouseEnter = None
        self.onMouseExit = None
        bgSprite = Sprite(bgParent=self.spriteCont, name='background', texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png')

    def AddItem(self):
        pass

    def OnMouseEnter(self, *args):
        if uicore.uilib.leftbtn:
            return
        if self.onMouseEnter is not None:
            self.onMouseEnter()

    def OnMouseExit(self, *args):
        if self.onMouseExit is not None:
            self.onMouseExit()

    def RegisterForHoverEvents(self, itemID, onMouseEnter, onMouseExit):
        self.onMouseEnter = lambda : onMouseEnter(itemID)
        self.onMouseExit = lambda : onMouseExit(itemID)

    def GetDragData(self):
        return [KeyVal(itemID=self.itemID, __guid__='xtriui.TypeIcon', typeID=self.typeID, isReprocessingItem=True)]

    def LoadTooltipPanel(self, tooltipPanel, *args):
        typeID, reprocessingYield, stationTaxHint, itemYieldHint, stationEfficiency = self.hintInfo
        tooltipPanel.LoadGeneric1ColumnTemplate()
        rowSpan = 1
        if self.itemState:
            rowSpan = 2
        subGrid1 = LayoutGrid()
        icon = Icon(width=64, height=64, align=CENTER)
        icon.LoadIconByTypeID(typeID=self.typeID, ignoreSize=True)
        subGrid1.AddCell(icon, rowSpan=rowSpan)
        yieldText = '<color=%s>%s%%</color>' % (Color.RGBtoHex(*COL_LIGHTBLUE), FmtAmt(reprocessingYield * 100.0, showFraction=1))
        topLabel = EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/ItemYieldHint', itemName=evetypes.GetName(self.typeID), itemYield=yieldText), width=170, autoFitToText=True, left=6, top=4, bold=True)
        subGrid1.AddCell(topLabel)
        if self.itemState:
            hintText = ''
            hintColor = None
            if self.itemState == STATE_REPROCESS:
                hintText = GetByLabel('UI/Reprocessing/ReprocessingWindow/ReprocessedFurtherHint')
                hintColor = COL_GREEN
            elif self.itemState == STATE_RESTRICTED:
                portionSize = evetypes.GetPortionSize(typeID)
                if portionSize > self.quantity:
                    noOfItems = FmtAmt(portionSize, showFraction=0)
                    hintText = GetByLabel('UI/Reprocessing/ReprocessingWindow/CannotReprocessHint', noOfItems=noOfItems)
                else:
                    hintText = GetByLabel('UI/Reprocessing/ReprocessingWindow/CannotReprocessNoValueHint')
                hintColor = COL_RED
            elif self.itemState == STATE_SUSPICIOUS:
                hintText = GetByLabel('UI/Reprocessing/ReprocessingWindow/ReprocessingWarningHint')
                hintColor = COL_YELLOW
            stateHint = EveLabelMedium(text=hintText, width=170, autoFitToText=True, left=6, top=4, color=hintColor)
            subGrid1.AddCell(stateHint)
        tooltipPanel.AddCell(subGrid1)
        subGrid = LayoutGrid()
        subGrid.AddCell(cellPadding=6, colSpan=2)
        subGrid.AddCell(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/DetailedYieldHint'), color=COL_BLUE, bold=True), colSpan=2)
        for label in GetReprocessingModifiersAsLabels(typeID, stationEfficiency, self.getTypeAttribute, self.getSkillLevel):
            subGrid.AddCell(label)

        if itemYieldHint:
            subGrid.AddCell(cellPadding=6, colSpan=2)
            subGrid.AddCell(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/YouWillReceiveHint'), color=COL_BLUE, bold=True), colSpan=2)
            for typeID, qty in itemYieldHint:
                subGrid.AddCell(EveLabelMedium(text=FmtAmt(qty, showFraction=False), colSpan=1, align=uiconst.TORIGHT, padRight=3, color=COL_LIGHTBLUE, bold=True))
                subGrid.AddCell(EveLabelMedium(text='%s' % evetypes.GetName(typeID), colSpan=1, padLeft=3))

        tooltipPanel.AddCell(subGrid)


class ReprocessingOutputItemContainer(ReprocessingItemContainer):

    def ApplyAttributes(self, attributes):
        ReprocessingItemContainer.ApplyAttributes(self, attributes)
        self.outputFrame = Frame(name='outputFrame', bgParent=self.spriteCont, texturePath='res:/UI/Texture/Reprocessing/Dash_Frame_48.png')
        self.outputFrame.SetRGB(*COL_YELLOW)
        qtyInfo = attributes.qtyInfo
        typeInfo = attributes.fromTypeInfo
        self._SetInfo(qtyInfo, typeInfo)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        subGrid1 = LayoutGrid()
        icon = Icon(width=64, height=64, align=CENTER)
        icon.LoadIconByTypeID(typeID=self.typeID, ignoreSize=True)
        subGrid1.AddCell(cellObject=icon)
        subGrid1.AddCell(EveLabelMedium(text=evetypes.GetName(self.typeID), width=170, autoFitToText=True, left=6, top=4, bold=True))
        tooltipPanel.AddCell(subGrid1)
        subGrid = LayoutGrid()
        subGrid.columns = 2
        l1 = EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/ReprocessedFrom'), color=COL_BLUE, bold=True)
        subGrid.AddCell(l1, colSpan=2)
        for typeID, quantity in self.typeInfo.iteritems():
            subGrid.AddCell(EveLabelMedium(text=FmtAmt(quantity, showFraction=0), align=uiconst.TORIGHT, padRight=3, color=COL_LIGHTBLUE, bold=True))
            subGrid.AddCell(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/ReprocessedFromType', typeName=evetypes.GetName(typeID)), padLeft=3))

        subGrid.AddCell(EveLabelMedium(text=FmtAmt(self.unrecoverableQty, showFraction=0), colSpan=1, align=uiconst.TORIGHT, padRight=2, color=COL_RED, bold=True))
        subGrid.AddCell(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/NotRecoverableHint'), colSpan=1, padLeft=2))
        subGrid.AddCell(EveLabelMedium(text=FmtAmt(self.quantity, showFraction=0), colSpan=1, align=uiconst.TORIGHT, padRight=2, color=COL_GREEN, bold=True))
        subGrid.AddCell(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/TotalOutputHint'), colSpan=1, padLeft=2))
        if self.iskCost:
            subGrid.AddCell(EveLabelMedium(text=FmtAmt(self.iskCost, showFraction=0), colSpan=1, align=uiconst.TORIGHT, padRight=2, bold=True))
            subGrid.AddCell(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/IskPaidPerItem'), colSpan=1, padLeft=2))
        tooltipPanel.AddCell(subGrid)

    def Update(self, qtyInfo, fromItemIDs, fromTypeInfo):
        self._SetInfo(qtyInfo, fromTypeInfo)

    def _SetInfo(self, qtyInfo, typeInfo):
        self.quantity, self.iskCost, self.unrecoverableQty = qtyInfo
        self.typeInfo = typeInfo
        self._SetQtyText()


def AskToContinue(error):
    buttons = uiconst.YESNO
    default = uiconst.ID_YES
    msg = cfg.GetMessage(error.msg, error.dict, onNotFound='return')
    if msg.type not in ('warning', 'question'):
        buttons = None
        default = None
    ret = eve.Message(error.msg, error.dict, buttons=buttons, default=default)
    return ret == uiconst.ID_YES


def CreateOutputItemContainer(typeID, fromItemIDs, fromTypeInfo, qtyInfo, canBeReprocessed):
    if canBeReprocessed:
        itemState = STATE_REPROCESS
    else:
        itemState = None
    return ReprocessingOutputItemContainer(align=uiconst.TOPLEFT, width=TILE_SIZE, height=TILE_SIZE, typeID=typeID, qtyInfo=qtyInfo, itemID=0, fromTypeInfo=fromTypeInfo, itemState=itemState)


def CreateInputItemContainer(item, hintInfo, itemState):
    return ReprocessingInputItemContainer(align=uiconst.TOPLEFT, width=TILE_SIZE, height=TILE_SIZE, typeID=item.typeID, quantity=item.quantity, itemID=item.itemID, categoryID=item.categoryID, hintInfo=hintInfo, itemState=itemState, singleton=item.singleton, stacksize=item.stacksize)


class ReprocessingInputGroupContainer(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.header = ReprocessingInputHeaderContainer(parent=self, align=uiconst.TOTOP, height=24, percentage=0.0, groupID=attributes.groupID, groupName=attributes.groupName)
        tileContainer = FlowContainer(parent=self, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, contentSpacing=(8, 8), padding=8)
        self.tilePlacer = TilePlacer(tileContainer)

    def SetEfficiency(self, efficiency, typeIDs):
        self.header.UpdateGauge(efficiency)
        self.header.UpdateSkills(typeIDs)

    def SetTaxAndStationEfficiency(self, efficiency, tax):
        self.header.stationEfficiency = efficiency
        self.header.stationTax = tax


class ReprocessingOutputGroupContainer(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.header = ReprocessingHeaderContainer(parent=self, align=uiconst.TOTOP, height=24, percentage=0.0, groupID=attributes.groupID, groupName=attributes.groupName)
        tileContainer = FlowContainer(parent=self, align=uiconst.TOTOP, contentSpacing=(8, 8), padding=8)
        self.tilePlacer = TilePlacer(tileContainer)

    def UpdateInfo(self, typeID, qtyInfo, fromItemIDs, fromTypeInfo):
        tile = self.tilePlacer.GetItem(typeID)
        tile.Update(qtyInfo, fromItemIDs, fromTypeInfo)


class ReprocessingHeaderContainer(Container):
    default_align = uiconst.TOTOP
    default_height = 24

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.groupID = attributes.groupID
        self.groupName = attributes.groupName
        Fill(bgParent=self, color=(0.0, 0.0, 0.0, 0.5))
        leftCont = Container(parent=self, align=uiconst.TOALL)
        self.headerText = EveLabelMedium(text=self.groupName, parent=leftCont, left=2, maxLines=1, align=uiconst.CENTERLEFT, bold=True, padLeft=4)


class ReprocessingInputHeaderContainer(ReprocessingHeaderContainer):

    def ApplyAttributes(self, attributes):
        ReprocessingHeaderContainer.ApplyAttributes(self, attributes)
        self.percentage = attributes.percentage
        self.avgBonus = 0
        self.state = uiconst.UI_NORMAL
        self.groupHilite = Fill(bgParent=self, color=(0.4, 0.4, 0.4, 0.1), opacity=0.0)
        self.getTypeAttribute = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute
        self.getSkillLevel = sm.GetService('skills').MySkillLevel
        self.stationTax = attributes.tax
        self.stationEfficiency = attributes.efficiency
        rightCont = Container(parent=self, align=uiconst.TORIGHT, width=100)
        Sprite(parent=rightCont, width=24, height=24, ignoreSize=True, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/Reprocessing/Reprocess.png')
        self.gaugeParent = Container(name='gaugeParent', parent=rightCont, align=uiconst.TOALL, padding=(0, 5, 2, 4), state=uiconst.UI_NORMAL)
        self.gaugeParent.LoadTooltipPanel = self.LoadGaugeTooltipPanel
        self.gaugeLabel = EveLabelSmallBold(parent=self.gaugeParent, align=uiconst.CENTER)
        Frame(parent=self.gaugeParent, color=(0.5, 0.5, 0.5, 0.05))
        Fill(bgParent=self.gaugeParent, color=(0.0, 0.0, 0.0, 0.8))
        self.reprocessingGauge = GradientSprite(parent=self.gaugeParent, align=uiconst.TOLEFT_PROP, rotation=-pi / 2, rgbData=[(0, COL_YELLOW)], alphaData=[(0, 0.6), (0.5, 0.4), (1.0, 0.6)], state=uiconst.UI_DISABLED)
        self.UpdateGauge(self.percentage)

    def UpdateGauge(self, percentage):
        self.reprocessingGauge.width = percentage
        self.percentage = percentage
        self.gaugeLabel.text = GetByLabel('UI/Common/Formatting/PercentageDecimal', percentage=percentage * 100.0)

    def UpdateSkills(self, typeIDs):
        skillBonuses = []
        for groupID, typeIDs in typeIDs.iteritems():
            for typeID in typeIDs:
                _, bonus = GetAttributeSkillsFromTypeID(typeID, self.getTypeAttribute, self.getSkillLevel)
                skillBonuses.append(bonus)

        bonusAmt = sum(skillBonuses)
        self.avgBonus = bonusAmt / len(typeIDs)

    def LoadGaugeTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        subGrid1 = LayoutGrid()
        icon = Sprite(width=64, height=64, ignoreSize=True, align=CENTER, texturePath='res:/UI/Texture/Reprocessing/Reprocess.png')
        subGrid1.AddCell(icon)
        itemName = self.groupName
        yieldText = '<color=%s>%s%%</color>' % (Color.RGBtoHex(*COL_LIGHTBLUE), FmtAmt(self.percentage * 100.0, showFraction=1))
        topLabel = EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/ItemYieldHint', itemName=itemName, itemYield=yieldText), width=170, autoFitToText=True, left=6, top=4, bold=True)
        subGrid1.AddCell(topLabel)
        tooltipPanel.AddCell(subGrid1)
        subGrid = LayoutGrid()
        l1 = EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/ReprocessingCalculations'), color=COL_BLUE, bold=True)
        subGrid.AddCell(l1, colSpan=2)
        for label in GetReprocessingModifiersAsLabels(self.groupID, self.stationEfficiency, self.getTypeAttribute, self.getSkillLevel, avgBonus=self.avgBonus, category=True):
            subGrid.AddCell(label)

        tooltipPanel.AddCell(subGrid)

    def OnMouseEnter(self, *args):
        uicore.animations.FadeIn(self.groupHilite, duration=0.4, endVal=0.25)

    def OnMouseExit(self, *args):
        uicore.animations.FadeOut(self.groupHilite, duration=0.4)


def CreateReprocessingWindowController(wnd, inputInfoCont, outputInfoCont, invCache, reprocessing, GetActiveShip):
    quotes = Quotes(reprocessing)
    materialFetcher = MaterialFetcher(quotes)
    inputItemContainer = inputInfoCont
    inputItemContainer = InputItemContainerInterface(inputItemContainer)
    outputItemContainer = outputInfoCont
    outputItemContainer = ItemContainerInterface(outputItemContainer)
    inputGrouper = GetCategoryGrouper()
    inputGroups = InputGroups(inputItemContainer, inputGrouper)
    containerCreator = ContainerCreator(Containers(CreateInputItemContainer), Containers(CreateOutputItemContainer), quotes)
    inputItemAdder = InputItemAdder(inputItemContainer, containerCreator, quotes, States(quotes), inputGrouper, GetActiveShip)
    outputItemAdder = OutputItemAdder(materialFetcher, outputItemContainer, containerCreator, GetGroupGrouper())
    reprocessor = ItemReprocessor(reprocessing, invCache, AskToContinue)
    controller = Controller(wnd, inputItemAdder, inputGroups, quotes, outputItemAdder, reprocessor, GetActiveShip)
    sm.RegisterNotify(controller)
    return controller


def GetReprocessingModifiersAsLabels(typeID, stationEfficiency, getTypeAttribute, getSkillLevel, avgBonus = None, category = False):
    labelList = []
    labelList.extend(GetStationEfficiencyAsLabel(stationEfficiency))
    labelList.extend(GetSkillBonusesAsLabels(typeID, getTypeAttribute, getSkillLevel, category=category))
    if category:
        if typeID == categoryAsteroid:
            labelList.extend(GetOreAvgBonusAsLabel(avgBonus))
            labelList.extend(GetImplantModifiersAsLabels(getTypeAttribute))
    elif evetypes.GetCategoryID(typeID) == categoryAsteroid:
        labelList.extend(GetImplantModifiersAsLabels(getTypeAttribute))
    return labelList


def GetStationEfficiencyAsLabel(stationEfficiency):
    stationBonusLabel = EveLabelMedium(text=GetByLabel('UI/Common/Formatting/Percentage', percentage=stationEfficiency * 100), colSpan=1, align=uiconst.TORIGHT, padRight=2, color=COL_LIGHTBLUE, bold=True)
    stationTextLabel = EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/BaseYield'), colSpan=1, padLeft=2)
    return (stationBonusLabel, stationTextLabel)


def GetOreAvgBonusAsLabel(avgBonus):
    labelOpacity = 0.35
    if avgBonus > 0:
        labelOpacity = 1.0
    oreAvgBonusLabel = EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/YieldFormatting', bonusYield=1.0 + avgBonus / 100), colSpan=1, align=uiconst.TORIGHT, padRight=3, color=COL_GREEN, bold=True, opacity=labelOpacity)
    oreAvgTextLabel = EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/OreProcessingHint'), colSpan=1, padLeft=3, opacity=labelOpacity)
    return (oreAvgBonusLabel, oreAvgTextLabel)


def GetSkillBonusesAsLabels(typeID, getTypeAttribute, getSkillLevel, category = False):
    skillLabels = []
    if not category:
        skillBonuses = GetSkillFromTypeID(typeID, getTypeAttribute, getSkillLevel)
    else:
        skillBonuses = GetSkillFromCategoryID(typeID, getTypeAttribute, getSkillLevel)
    for skillType, bonus in skillBonuses:
        skillName = evetypes.GetName(skillType)
        labelOpacity = 0.35
        if bonus > 0:
            labelOpacity = 1.0
        skillLabels.append(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/YieldFormatting', bonusYield=1.0 + bonus / 100), colSpan=1, align=uiconst.TORIGHT, padRight=3, color=COL_GREEN, bold=True, opacity=labelOpacity))
        skillLabels.append(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/BonusFromSkill', skillName=skillName), colSpan=1, padLeft=3, opacity=labelOpacity))

    return skillLabels


def GetImplantModifiersAsLabels(getTypeAttribute):
    implantLabels = []
    implants = sm.GetService('godma').GetItem(session.charid).implants
    for implant in implants:
        implantBonus = getTypeAttribute(implant.typeID, attributeRefiningYieldMutator)
        if implantBonus > 0.0:
            implantLabels.append(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/YieldFormatting', bonusYield=1.0 + implantBonus / 100), colSpan=1, align=uiconst.TORIGHT, padRight=3, color=COL_GREEN, bold=True))
            implantLabels.append(EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/BonusFromSkill', skillName=evetypes.GetName(implant.typeID)), colSpan=1, padLeft=3))

    return implantLabels


def GetStationTaxAsLabel(stationTax):
    taxBonusLabel = EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/YieldFormatting', bonusYield=1.0 - stationTax), colSpan=1, align=uiconst.TORIGHT, padRight=3, color=COL_RED, bold=True)
    taxTextLabel = EveLabelMedium(text=GetByLabel('UI/Reprocessing/ReprocessingWindow/StationTaxHint'), colSpan=1, padLeft=3)
    return (taxBonusLabel, taxTextLabel)


def CopyItemsToClipboard(items):
    textLine = []
    for item in items:
        t = '%s\t%s' % (evetypes.GetName(item.typeID), abs(item.quantity))
        textLine.append(t)

    text = '\n'.join(textLine)
    from carbon.common.script.util.commonutils import StripTags
    strippedText = StripTags(text)
    if strippedText:
        import blue
        blue.pyos.SetClipboardData(strippedText)
