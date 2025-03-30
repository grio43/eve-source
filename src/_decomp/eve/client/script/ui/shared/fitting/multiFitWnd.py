#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\multiFitWnd.py
from collections import defaultdict
import evetypes
import uthread
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.combo import Combo
from carbonui.control.comboEntryData import ComboEntryData
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge, EveCaptionSmall, EveCaptionMedium, EveLabelSmall
from carbonui.control.window import Window
import carbonui.const as uiconst
from eve.client.script.ui.util import uix
from eve.client.script.ui.control.infoIcon import MoreExtraInfoInTooltip
from carbonui.control.progressBar import ProgressBar
from eve.client.script.ui.shared.dockedUI.controllers.stationController import StationController
from eve.client.script.ui.shared.dockedUI.controllers.structureController import StructureController
from eve.client.script.ui.shared.dockedUI.lobbyWnd import CheckCanAccessService
from eve.common.script.sys.eveCfg import IsDocked, InStructure
from globalConfig.getFunctions import GetMaxShipsToFit
from inventorycommon.util import IsModularShip
from localization import GetByLabel
from shipfitting import Fitting
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty
from threadutils import throttled
from utillib import KeyVal
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.uicore import uicore
NORMAL_COLOR = (1,
 1,
 1,
 0.75)
WARNING_COLOR = (1,
 0,
 0,
 0.75)
MAX_TOOLTIP_ENTRIES = 10
REFRESH_TEXTUREPATH = 'res:/UI/Texture/Icons/105_32_22.png'
MAX_TEXT_WIDTH = 300
LEFT_EDGE = 10

class MultiFitWnd(Window):
    __notifyevents__ = ['OnSessionChanged', 'OnMultipleItemChange']
    default_windowID = 'multiFitWnd'
    default_captionLabelPath = 'UI/Fitting/FittingWindow/FittingManagement/MultiFitHeader'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fittingManagement.png'
    layoutColumns = 3

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.fitting = None
        self.isFitting = False
        self.MakeUnstackable()
        self.canFitNum = 0
        self.tryingToFitNum = 1
        self.currentProgress = 0
        self.ConstructUI()
        fitting = attributes.fitting
        self.tryingToFitNum = attributes.get('qty', 1)
        self.LoadWindow(fitting, self.tryingToFitNum)
        self.SetInventoryStatus()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        self.BuildTopParentUI()
        self.AddButtons()
        numColumns = 2
        self.sr.main.clipChildren = True
        self.layoutGrid = layoutGrid = LayoutGrid(parent=ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP), align=uiconst.TOPLEFT, columns=numColumns, cellSpacing=(4, 10))
        spacer = Container(pos=(0, 0, 50, 0), align=uiconst.TOPLEFT)
        layoutGrid.AddCell(cellObject=spacer, colSpan=1)
        layoutGrid.FillRow()
        self.BuildNumToFitUI()
        self.BuildWarningUI()
        self.BuildRefreshInventory()
        self.missingLayoutGrid = LayoutGrid(parent=self.layoutGrid, columns=2, cellSpacing=(4, 10))
        self.BuildAvailableShipsUI()
        self.BuildEquipmentUI()
        self.BuildProgressUI()
        self.MakeRigCbUI()

    def BuildTopParentUI(self):
        self.topParent = Container(parent=self.GetMainArea(), name='topParent', align=uiconst.TOTOP, height=100, clipChildren=True)
        self.shipIcon = Icon(name='shipIcon', parent=self.topParent, state=uiconst.UI_NORMAL, size=64, ignoreSize=True)
        self.shipIcon.GetDragData = self.GetFittingDragData
        self.shipIcon.OnClick = self.OpenFitting
        self.shipIcon.hint = GetByLabel('UI/Fitting/ShowFitting')
        self.techSprite = Sprite(name='techIcon', parent=self.topParent, align=uiconst.RELATIVE, width=16, height=16, idx=0)
        self.fitNameEdit = SingleLineEditText(name='fitNameEdit', parent=self.topParent, left=72, width=150, maxLength=20, hint=GetByLabel('UI/Common/ShipName'))
        top = self.fitNameEdit.top + self.fitNameEdit.height + 5
        self.shipNameLabel = EveLabelMedium(name='shipNameLabel', parent=self.topParent, left=77, top=top, state=uiconst.UI_NORMAL)
        top = self.shipNameLabel.top + 20
        equipmentText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/EquipmentLocation')
        equipCont = Container(name='equipCont', parent=self.topParent, align=uiconst.TOTOP, top=top, padLeft=77)
        equipLabel = EveLabelSmall(text=equipmentText, parent=equipCont, name='equipLabel', align=uiconst.CENTERLEFT)
        self.equipmentLocationCombo = Combo(parent=equipCont, options=[], name='equipmentLocationCombo', pos=(equipLabel.left + equipLabel.textwidth + 6,
         0,
         0,
         0), callback=self.OnEquipLocationChanged, hint=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/EquipmentLocationHint'))
        equipCont.height = max(equipLabel.height, self.equipmentLocationCombo.height)

    def LoadEquipCombo(self):
        fittingSvc = sm.GetService('fittingSvc')
        personalContainers = fittingSvc.FindPersonalContainers()
        options = []
        if personalContainers:
            cfg.evelocations.Prime({x.itemID for x in personalContainers})
            for eachContainer in personalContainers:
                itemID = eachContainer.itemID
                containerName = cfg.evelocations.Get(itemID).name or evetypes.GetName(eachContainer.typeID)
                options.append((containerName.lower(), ComboEntryData(containerName, itemID)))

            options = SortListOfTuples(options)
        options.insert(0, ComboEntryData(GetByLabel('UI/Inventory/ItemHangar'), None))
        if [ (x.label, x.returnValue) for x in self.equipmentLocationCombo.entries ] != [ (x.label, x.returnValue) for x in options ]:
            self.equipmentLocationCombo.LoadOptions(options)

    def AddButtons(self):
        btnCont = FlowContainer(name='buttonParent', parent=self.sr.main, align=uiconst.TOBOTTOM, padding=6, autoHeight=True, centerContent=True, contentSpacing=uiconst.BUTTONGROUPMARGIN, idx=0)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FitShips', numToFit=1)
        self.fitBtn = Button(parent=btnCont, label=text, func=self.DoFitShips, align=uiconst.NOALIGN)
        self.cancelBtn = Button(parent=btnCont, label=GetByLabel('UI/Common/Close'), func=self.Cancel, align=uiconst.NOALIGN)
        if sm.GetService('publicQaToolsClient').CanGiveItemForMultifit():
            self.spawnFitBtn = Button(parent=btnCont, label='Create Missing', func=self.GiveAllPlayer, align=uiconst.NOALIGN)

    def BuildNumToFitUI(self):
        maxShipsAllowed = GetMaxShipsToFit(sm.GetService('machoNet'))
        numCont = Container(name='numCont', align=uiconst.TOTOP, height=30, padLeft=LEFT_EDGE)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/NumShipsToFit')
        self.numToFitLabel = EveLabelLarge(name='numToFitLabel', parent=numCont, text=text, width=250, autoFitToText=True)
        left = self.numToFitLabel.left + self.numToFitLabel.textwidth + 10
        self.numToFitEdit = SingleLineEditInteger(name='numToFitEdit', parent=numCont, minValue=1, maxValue=maxShipsAllowed, OnChange=self.OnNumChanged, left=left, align=uiconst.CENTERLEFT)
        numCont.height = max(self.numToFitLabel.textheight, self.numToFitEdit.height)
        self.layoutGrid.AddCell(cellObject=numCont, colSpan=self.layoutGrid.columns)

    def BuildWarningUI(self):
        self.numWarningLabel = EveCaptionSmall(name='numWarningLabel', state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP, width=MAX_TEXT_WIDTH, autoFitToText=True, text=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MissingShipEquipment'))
        self.numWarningLabel.SetRGBA(*WARNING_COLOR)
        self.PulseLabel(self.numWarningLabel)
        self.numWarningLabel.LoadTooltipPanel = self.LoadMissingTooltip
        self.layoutGrid.AddCell(cellObject=self.numWarningLabel, colSpan=self.layoutGrid.columns)
        self.moreInfoIcon = MoreExtraInfoInTooltip(parent=self.numWarningLabel.parent, align=uiconst.CENTER)
        self.t3Warning = EveCaptionSmall(name='t3Warning', state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP, width=MAX_TEXT_WIDTH, autoFitToText=True, text=GetByLabel('UI/Fitting/FittingWindow/FittingManagement/InvalidT3Fit'))
        self.t3Warning.SetRGBA(*WARNING_COLOR)
        self.layoutGrid.AddCell(cellObject=self.t3Warning, colSpan=self.layoutGrid.columns)
        self.HideT3Warning()
        self.moreInfoIcon.display = False
        self.moreInfoIcon.LoadTooltipPanel = self.LoadMissingTooltip
        self.layoutGrid.FillRow()

    def BuildRefreshInventory(self):
        self.refreshCont = Transform(parent=self.layoutGrid, pos=(0, 0, 32, 32), align=uiconst.CENTER)
        self.refreshIcon = ButtonIcon(name='refreshSprite', parent=self.refreshCont, width=32, height=32, align=uiconst.CENTER, texturePath=REFRESH_TEXTUREPATH, iconSize=32, func=self.OnRefreshClicked)
        self.refreshIcon.hint = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/RefreshInventoryStatusHint')

    def OnRefreshClicked(self, *args):
        uthread.new(self.refreshCont.StartRotationCycle, cycles=1)
        self.RefreshInventory()

    def RefreshInventory(self):
        self.LoadEquipCombo()
        self.SetEquipmentText()
        self.SetInventoryStatus()

    def OnEquipLocationChanged(self, combo, key, val):
        self.RefreshInventory()

    def BuildAvailableShipsUI(self):
        self.shipCounter = EveCaptionMedium(name='shipCounter', parent=self.missingLayoutGrid, state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT, left=4, text='000')
        self.shipCounter.LoadTooltipPanel = self.LoadShipCounterTooltipPanel
        self.shipCounter.missingDict = {}
        shipText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/PackagedShipsInHangar')
        self.availableShipsLabel = EveLabelLarge(name='availableShipsLabel', parent=self.missingLayoutGrid, state=uiconst.UI_NORMAL, text=shipText, align=uiconst.CENTERLEFT, width=MAX_TEXT_WIDTH, autoFitToText=True)
        self.availableShipsLabel.hint = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/PackagedShipsInHangarHint')
        self.layoutGrid.FillRow()

    def BuildEquipmentUI(self):
        self.equipmentCounter = EveCaptionMedium(name='equipmentCounter', parent=self.missingLayoutGrid, state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT, left=4, text='000')
        self.equipmentCounter.LoadTooltipPanel = self.LoadEqCounterTooltipPanel
        self.equipmentCounter.missingDict = {}
        self.availableEquipmentLabel = EveLabelLarge(name='availableEquipmentLabel', parent=self.missingLayoutGrid, state=uiconst.UI_NORMAL, text='', align=uiconst.CENTERLEFT, width=MAX_TEXT_WIDTH, autoFitToText=True)
        self.SetEquipmentText()
        self.layoutGrid.FillRow()

    def SetEquipmentText(self):
        locationID = self.equipmentLocationCombo.GetValue()
        if locationID is None:
            locationName = GetByLabel('UI/Inventory/ItemHangar')
        else:
            locationName = cfg.evelocations.Get(locationID).name or self.equipmentLocationCombo.GetKey()
        eqText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/RoundsOfFittingsInLocation', locationName=locationName)
        self.availableEquipmentLabel.text = eqText

    def BuildProgressUI(self):
        self.progressCont = Container(parent=self.sr.main, height=36, align=uiconst.TOBOTTOM, padding=(10, 0, 10, 10))
        self.progressCounter = EveCaptionMedium(name='progressCounter', parent=self.progressCont, state=uiconst.UI_NORMAL, align=uiconst.CENTERTOP)
        self.progressBar = ProgressBar(parent=self.progressCont, height=10, align=uiconst.TOBOTTOM)
        self.progressCont.display = False

    def MakeRigCbUI(self):
        checked = settings.user.ui.Get('fitting_rigCB', True)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FitRigs')
        self.rigCB = Checkbox(name='rigCB', text=text, OnChange=self.OnCbChanged, left=LEFT_EDGE, checked=checked, settingsPath=('user', 'ui'), settingsKey='fitting_rigCB')
        self.rigCB.hint = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FitRigsHint')
        self.layoutGrid.AddCell(cellObject=self.rigCB, colSpan=self.layoutGrid.columns)

    def OnNumChanged(self, *args):
        self.onNumChangedTimer = AutoTimer(100, self.SetInventoryStatus)

    def OnCbChanged(self, *args):
        self.SetInventoryStatus()

    def OpenFitting(self, *args):
        sm.GetService('fittingSvc').DisplayFitting(self.fitting)

    def LoadWindow(self, fitting, qty = 1):
        self.fitting = fitting
        self.shipCounter.missingDict = {}
        self.equipmentCounter.missingDict = {}
        shipTypeID = fitting.shipTypeID
        self.shipIcon.LoadIconByTypeID(shipTypeID)
        uix.GetTechLevelIcon(self.techSprite, typeID=shipTypeID)
        self.numToFitEdit.SetValue(qty)
        self.fitNameEdit.SetValue(fitting.name)
        self.shipNameLabel.text = GetShowInfoLink(shipTypeID, evetypes.GetName(shipTypeID))
        self.VerifyT3Fit()
        self.RefreshInventory()
        self._ApplyFixedWindowSize()
        self.RegisterPositionAndSize()
        self.Maximize()

    def _ApplyFixedWindowSize(self):
        self.missingLayoutGrid.RefreshGridLayout()
        self.layoutGrid.RefreshGridLayout()
        layoutWidth, layoutHeight = self.layoutGrid.GetSize()
        newHeight = layoutHeight + self.fitBtn.height + self.progressCont.height + self.topParent.height
        height = max(newHeight, self.default_height)
        width = max(layoutWidth, self.default_width)
        width, height = self.GetWindowSizeForContentSize(width, height)
        self.SetFixedWidth(width)
        self.SetFixedHeight(height)

    def SetInventoryStatus(self):
        self.onNumChangedTimer = None
        fitting = self.fitting
        shipTypeID = fitting.shipTypeID
        fittingSvc = sm.GetService('fittingSvc')
        fittingObj = Fitting(fitting.fitData, None)
        itemTypes = fittingObj.GetQuantityByType()
        modulesByFlag = fittingObj.GetModulesByFlag()
        rigsByFlags = fittingObj.GetRigsByFlag()
        rigsToFit = bool(rigsByFlags)
        if rigsToFit:
            self.rigCB.display = True
        else:
            self.rigCB.display = False
        numToFit = self.numToFitEdit.GetValue()
        self.tryingToFitNum = numToFit
        maxAvailableFitting, missingForFullFit = self._GetMaxAvailabeAndMissingForFullFit(itemTypes, modulesByFlag, numToFit)
        nonSingletonShipsNumDict = fittingSvc.GetQtyInLocationByTypeIDs([shipTypeID], onlyGetNonSingletons=True)
        packagedShipsNum = nonSingletonShipsNumDict.get(shipTypeID, 0)
        canFitNum = min(packagedShipsNum, numToFit)
        if maxAvailableFitting is not None:
            canFitNum = min(canFitNum, maxAvailableFitting)
        self.canFitNum = canFitNum
        btnText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/FitShips', numToFit=self.canFitNum)
        self.fitBtn.SetLabel(btnText)
        self.UpdateFitBtnState()
        missingNumShips = max(0, numToFit - packagedShipsNum)
        if missingNumShips:
            missingDict = {shipTypeID: missingNumShips}
        else:
            missingDict = {}
        self.shipCounter.missingDict = missingDict
        if missingForFullFit:
            missingDict = missingForFullFit
        else:
            missingDict = {}
        self.equipmentCounter.missingDict = missingDict
        if missingForFullFit or missingNumShips:
            missingText = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MissingShipEquipment')
            self.numWarningLabel.text = missingText
            self.moreInfoIcon.display = True
            self.moreInfoIcon.left = self.numWarningLabel.textwidth / 2 + 10
            if sm.GetService('publicQaToolsClient').CanGiveItemForMultifit():
                self.spawnFitBtn.Enable()
        else:
            self.numWarningLabel.text = ''
            self.numWarningLabel.height = 0
            self.moreInfoIcon.display = False
            if sm.GetService('publicQaToolsClient').CanGiveItemForMultifit():
                self.spawnFitBtn.Disable()
        self.SetAvailabilityShipOrEq(self.shipCounter, packagedShipsNum, numToFit)
        self.SetAvailabilityShipOrEq(self.equipmentCounter, maxAvailableFitting, numToFit)

    def UpdateFitBtnState(self):
        if self.canFitNum < 1 or self.IsInvalidT3Fit():
            self.fitBtn.Disable()
        else:
            self.fitBtn.Enable()

    def _GetMaxAvailabeAndMissingForFullFit(self, itemTypes, modulesByFlag, numToFit):
        locationID = self.equipmentLocationCombo.GetValue()
        fittingSvc = sm.GetService('fittingSvc')
        qtyByTypeID = fittingSvc.GetQtyInLocationByTypeIDs(itemTypes, locationID=locationID)
        rigTypeIDs = {t for f, t in modulesByFlag.iteritems() if f in const.rigSlotFlags}
        maxAvailableFitting, missingForFullFit = fittingSvc.GetMaxAvailabeAndMissingForFullFit(True, itemTypes, numToFit, qtyByTypeID, rigTypeIDs)
        return (maxAvailableFitting, missingForFullFit)

    def SetAvailabilityShipOrEq(self, label, available, numToFit):
        if available is None:
            label.text = '-'
            label.SetRGBA(*NORMAL_COLOR)
            return
        label.text = available
        if available < numToFit:
            label.SetRGBA(*WARNING_COLOR)
        else:
            label.SetRGBA(*NORMAL_COLOR)

    def DoFitShips(self, *args):
        fitting = self.fitting
        fitRigs = self.rigCB.GetValue()
        numToActuallyFit = self.canFitNum
        fittingName = self.fitNameEdit.GetValue()
        if fittingName is None or fittingName.strip() == '':
            fittingName = fitting.name or evetypes.GetName(fitting.shipTypeID)
            fittingName = StripTags(fittingName)
        fittingSvc = sm.GetService('fittingSvc')
        fittingObj = Fitting(fitting.fitData, None)
        rigsToFit = fittingObj.GetRigsByFlag()
        rigsToFit = bool(rigsToFit)
        if fitRigs or not rigsToFit:
            cargoItemsByType = {}
        else:
            cargoItemsByType = defaultdict(int)
            for flagID, typeID in fittingObj.GetModulesByFlag().iteritems():
                if flagID in const.rigSlotFlags:
                    cargoItemsByType[typeID] += 1

            cargoItemsByType = dict(cargoItemsByType)
        if session.stationid:
            stationController = StationController(itemID=session.stationid)
        elif InStructure():
            stationController = StructureController(itemID=session.structureid)
        else:
            return
        CheckCanAccessService('fitting', stationController)
        equipmentLocationID = self.equipmentLocationCombo.GetValue()
        _, missingForFullFit = self._GetMaxAvailabeAndMissingForFullFit(fittingObj.GetQuantityByType(), fittingObj.GetModulesByFlag(), numToActuallyFit)
        if missingForFullFit:
            self.SetInventoryStatus()
            eve.Message('uiwarning03')
            return
        try:
            fitInfo = fittingObj.GetKeyValForApplyingFit()
            self.PrepareForMultiFitCall()
            fittingSvc.DoFitManyShips(fitting.shipTypeID, fitInfo, cargoItemsByType, fitRigs, fittingName, numToActuallyFit, itemContainerID=equipmentLocationID)
        finally:
            uthread.new(self.ResetUIAfterFitting)

    def PrepareForMultiFitCall(self):
        self.fitBtn.Disable()
        self.cancelBtn.Disable()
        self.isFitting = True
        self.currentProgress = 0
        self.progressCounter.text = self.currentProgress
        self.progressCont.display = True
        self.layoutGrid.Disable()
        self.layoutGrid.opacity = 0.2
        sm.RegisterForNotifyEvent(self, 'OnItemChange')

    def ResetUIAfterFitting(self):
        sm.UnregisterForNotifyEvent(self, 'OnItemChange')
        self.isFitting = False
        self.currentProgress = 0
        uicore.animations.BlinkOut(self.progressCont, startVal=0.0, endVal=1.0, duration=0.5, loops=3, sleep=True)
        self.progressCont.display = False
        self.progressCounter.text = self.currentProgress
        self.cancelBtn.Enable()
        self.layoutGrid.Enable()
        self.layoutGrid.opacity = 1.0
        self.SetInventoryStatus()

    def Cancel(self, *args):
        self.CloseByUser()

    def GetFittingDragData(self):
        entry = KeyVal()
        entry.fitting = self.fitting
        entry.label = self.fitting.name
        entry.displayText = self.fitting.name
        entry.__guid__ = 'listentry.FittingEntry'
        return [entry]

    def LoadMissingTooltip(self, tooltipPanel, *args):
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MissingItems', numToFit=self.tryingToFitNum, fittingName=self.fitting.name)
        tooltipPanel.AddLabelLarge(text=text, padBottom=8)
        self.LoadShipCounterTooltipPanel(tooltipPanel, singleGroupShowing=False)
        self.LoadEqCounterTooltipPanel(tooltipPanel, singleGroupShowing=False)
        missingDict = {}
        missingDict.update(self.shipCounter.missingDict)
        missingDict.update(self.equipmentCounter.missingDict)
        self.AddBuyAllBtn(tooltipPanel, missingDict)

    def LoadShipCounterTooltipPanel(self, tooltipPanel, *args, **kwargs):
        missingDict = self.shipCounter.missingDict
        if not missingDict:
            return
        singleGroupShowing = kwargs.get('singleGroupShowing', True)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MissingShips', numToFit=self.tryingToFitNum, fittingName=self.fitting.name)
        return self.LoadCounterTooltip(tooltipPanel, missingDict, text, singleGroupShowing)

    def LoadEqCounterTooltipPanel(self, tooltipPanel, *args, **kwargs):
        missingDict = self.equipmentCounter.missingDict
        if not missingDict:
            return
        singleGroupShowing = kwargs.get('singleGroupShowing', True)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MissingEquipment', numToFit=self.tryingToFitNum, fittingName=self.fitting.name)
        self.LoadCounterTooltip(tooltipPanel, missingDict, text, singleGroupShowing)

    def LoadCounterTooltip(self, tooltipPanel, missingDict, text, singleGroupShowing = True):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.state = uiconst.UI_NORMAL
        if singleGroupShowing:
            tooltipPanel.AddLabelLarge(text=text, padBottom=8)
        typeList = []
        for eachTypeID, eachQty in missingDict.iteritems():
            typeName = evetypes.GetName(eachTypeID)
            typeList.append((typeName.lower(), (eachTypeID, eachQty)))

        typeList = SortListOfTuples(typeList)
        for eachTypeID, eachQty in typeList[:MAX_TOOLTIP_ENTRIES]:
            typeCont = TooltipEntry(parent=tooltipPanel, typeID=eachTypeID, qty=eachQty)

        if len(typeList) > MAX_TOOLTIP_ENTRIES:
            numItemsNotDisplayed = len(typeList) - MAX_TOOLTIP_ENTRIES
            text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/MoreItemTypesMissing', numMoreItems=numItemsNotDisplayed)
            tooltipPanel.AddLabelMedium(text=text, align=uiconst.CENTERLEFT)
        if singleGroupShowing:
            self.AddBuyAllBtn(tooltipPanel, missingDict)

    def AddBuyAllBtn(self, tooltipPanel, missingDict):

        def BuyAll(*args):
            BuyMultipleTypesWithQty(missingDict)

        Button(parent=tooltipPanel, label=GetByLabel('UI/Market/MarketQuote/BuyAll'), func=BuyAll, align=uiconst.CENTER)
        if session.role & ROLE_WORLDMOD == ROLE_WORLDMOD:
            Button(parent=tooltipPanel, label='GM: Give all', func=self.GiveAllGM, align=uiconst.CENTERRIGHT, args=(missingDict,))
        if session.role & ROLE_GML == ROLE_GML:
            Button(parent=tooltipPanel, label='GM: Load me all', func=self.LoadAllGM, align=uiconst.CENTERRIGHT, args=(missingDict,))

    def GiveAllGM(self, missingDict):
        from eve.client.script.ui.shared.fittingScreen.missingItemsPopup import GiveAllGM
        GiveAllGM(missingDict)

    def LoadAllGM(self, missingDict):
        from eve.client.script.ui.shared.fittingScreen.missingItemsPopup import LoadAllGM
        LoadAllGM(missingDict)

    def GiveAllPlayer(self, *args):
        self.SetInventoryStatus()
        missingDict = {}
        missingDict.update(self.shipCounter.missingDict)
        missingDict.update(self.equipmentCounter.missingDict)
        commandString = ''
        for typeID, qty in missingDict.iteritems():
            commandString += '{typeID}|{qty},'.format(typeID=typeID, qty=qty)

        commandString = commandString[:-1]
        sm.GetService('publicQaToolsClient').SlashCmd('/giveitem {}'.format(commandString))

    def OnItemChange(self, item, change, location):
        if item.typeID != self.fitting.shipTypeID:
            return
        if const.ixSingleton in change:
            self.currentProgress += 1
            self.progressCounter.text = '%s / %s' % (self.currentProgress, self.canFitNum)

    def OnSessionChanged(self, isRemote, sess, change):
        if not IsDocked():
            self.CloseByUser()

    def PulseLabel(self, label):
        uicore.animations.FadeTo(label, startVal=0.65, endVal=0.9, duration=1.0, loops=uiconst.ANIM_REPEAT, curveType=uiconst.ANIM_WAVE)

    def OnMultipleItemChange(self, *args):
        if self.isFitting:
            return
        self.RefreshOnItemChanged_throttled()

    @throttled(0.5)
    def RefreshOnItemChanged_throttled(self):
        self.RefreshInventory()

    def VerifyT3Fit(self):
        isInvalidT3Fit = self.IsInvalidT3Fit()
        if isInvalidT3Fit:
            self.t3Warning.text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/InvalidT3Fit')
        else:
            self.HideT3Warning()

    def IsInvalidT3Fit(self):
        fitting = self.fitting
        if not fitting:
            self.HideT3Warning()
            return False
        shipTypeID = fitting.shipTypeID
        if not IsModularShip(shipTypeID):
            return False
        clientDogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
        subsystemSlotFlagsMissing = const.subsystemSlotFlags[:]
        for typeID, flagID, qty in fitting.fitData:
            if flagID in subsystemSlotFlagsMissing:
                isObsolete = bool(clientDogmaStaticSvc.GetTypeAttribute(typeID, const.attributeModuleIsObsolete))
                if not isObsolete:
                    subsystemSlotFlagsMissing.remove(flagID)
                if clientDogmaStaticSvc.GetTypeAttribute2(typeID, const.attributeFitsToShipType) != shipTypeID:
                    return True

        return bool(subsystemSlotFlagsMissing)

    def HideT3Warning(self):
        self.t3Warning.text = ''
        self.t3Warning.height = 0


class TooltipEntry(Container):
    default_height = 32
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        typeID = attributes.typeID
        qty = attributes.qty
        iconPadding = 1 * const.defaultPadding
        typeIcon = Icon(name='typeIcon', parent=self, state=uiconst.UI_NORMAL, size=32, left=iconPadding, ignoreSize=True, typeID=typeID)
        techIcon = uix.GetTechLevelIcon(typeID=typeID)
        if techIcon:
            techIcon.left = iconPadding
            techIcon.SetParent(self, idx=0)
        typeName = evetypes.GetName(typeID)
        link = '<url="showinfo:%s">%s</url>' % (typeID, typeName)
        text = '%sx %s' % (qty, link)
        left = iconPadding * 2 + typeIcon.width + 10
        label = EveLabelMedium(parent=self, left=left, text=text, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
        self.width = label.left + label.textwidth + 10
