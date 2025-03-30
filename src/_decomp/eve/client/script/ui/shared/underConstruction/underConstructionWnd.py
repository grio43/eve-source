#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\underConstruction\underConstructionWnd.py
import logging
from collections import defaultdict
from carbonui.button.const import ButtonVariant
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from eve.client.script.ui.shared.underConstruction.util import GetBgTextureInfo, GetFactionBgTexturePath, FACTION_BG_HEIGHT, FACTION_BG_WIDTH
from localization import GetByLabel
from carbonui.window.settings import WindowMarginMode
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
import evetypes
import uthread2
from eve.client.script.ui.shared.underConstruction.underConstructionInputItem import InputItemController, UnderConstructionInputScrollEntry
from eve.client.script.ui.shared.underConstruction.underConstructionOutputCont import UnderConstructionOutputCont
from threadutils import throttled
from eve.client.script.environment.invControllers import ShipCargo
import locks
from spacecomponents.common.componentConst import UNDER_CONSTRUCTION
from spacecomponents.common.data import get_space_component_for_type
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.window import Window
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.control.scrollContainer import ScrollContainer
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.button import Button
from eve.common.script.util.eveFormat import FmtISK, FmtLP
from spacecomponents.common.helper import HasUnderConstructionComponent
from eve.common.lib import appConst
logger = logging.getLogger(__name__)
from eve.client.script.environment.invControllers import SpaceComponentInventory

class UnderConstructionWnd(Window):
    __guid__ = 'UnderConstructionWnd'
    __notifyevents__ = ['OnSessionChanged']
    default_minSize = (930, 520)
    default_windowID = 'underConstructionWnd'

    def DebugReload(self, *args):
        self.Reload(self)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        if session.role & ROLE_PROGRAMMER:
            reloadBtn = Button(parent=self.content, label='Reload', align=uiconst.TOPRIGHT, func=self.DebugReload, top=0, idx=0)
        self._itemID = attributes.itemID
        self._typeID = None
        self._depositingItems = False
        self._depositBtnDelay = False
        self._constructedTypeID = None
        self._inputRequiredByTypeID = {}
        self._qtyRequiredByTypeID = {}
        self.inputEntriesByTypeID = {}
        self.invCookie = sm.GetService('inv').Register(self)
        self.invController = SpaceComponentInventory(itemID=self._itemID)
        self._typeID = self.invController.GetTypeID()
        if not HasUnderConstructionComponent(self._typeID):
            self.Close()
            logger.exception('trying to open a under construction window for something without the component')
            return
        self.SetCaption(evetypes.GetName(self._typeID))
        underConstructionComp = get_space_component_for_type(self._typeID, UNDER_CONSTRUCTION)
        self._inputRequiredByTypeID = underConstructionComp.inputItems
        self._qtyRequiredByTypeID = {typeID:inputInfo.qtyRequired for typeID, inputInfo in self._inputRequiredByTypeID.iteritems()}
        self._constructedTypeID = underConstructionComp.constructedItem
        self.ConstructUI()
        self.LoadInputItems()
        self.Refresh()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        self.bottomCont = ContainerAutoSize(parent=self.content, name='bottomCont', align=uiconst.TOBOTTOM, alignMode=uiconst.TOTOP)
        self.centerCont = Container(parent=self.content, name='centerCont', clipChildren=True)
        self.centerBgCont = Container(parent=self.content, name='centerBgCont', clipChildren=True)
        self.righSide = Container(parent=self.centerCont, name='righSide', align=uiconst.TORIGHT, width=400)
        self.leftSide = Container(parent=self.centerCont, name='leftSide')
        bgTexturePathInfo = GetBgTextureInfo(self._constructedTypeID)
        if bgTexturePathInfo:
            texturePath, tw, th = bgTexturePathInfo
            Sprite(parent=self.centerBgCont, pos=(0,
             0,
             tw,
             th), align=uiconst.CENTERRIGHT, texturePath=texturePath, state=uiconst.UI_DISABLED)
            showIcon = False
        else:
            showIcon = True
        factionBgTexturePath = GetFactionBgTexturePath(self._constructedTypeID)
        Sprite(parent=self.centerBgCont, pos=(0,
         0,
         FACTION_BG_WIDTH,
         FACTION_BG_HEIGHT), align=uiconst.CENTERRIGHT, texturePath=factionBgTexturePath, state=uiconst.UI_DISABLED)
        self.ConstructLeftSide()
        self.ConstructRightSide(showIcon=showIcon)
        self.ConstructBottom()

    def ConstructLeftSide(self):
        self.inputScroll = ScrollContainer(name='inputScroll', parent=self.leftSide, padRight=20)

    def ConstructBottom(self):
        padding = self._GetPaddingValue()
        depositBtnCont = ContainerAutoSize(parent=self.bottomCont, name='depositBtnCont', align=uiconst.TORIGHT)
        text = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/DepositItems')
        self.depositItemsBtn = Button(parent=depositBtnCont, label=text, func=self.DepositItems, align=uiconst.CENTER)
        selectionBtnCont = ContainerAutoSize(parent=self.bottomCont, name='selectionBtnCont', align=uiconst.TORIGHT, left=padding)
        text = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/DeselectAllItems')
        self.changeSelectionBtn = Button(parent=selectionBtnCont, label=text, func=self.ChangeSelection, align=uiconst.CENTER, variant=ButtonVariant.GHOST)
        self.bottomCont.minHeight = self.depositItemsBtn.height + 2 * padding
        gridParent = ContainerAutoSize(parent=self.bottomCont, name='gridParent', align=uiconst.CENTERLEFT)
        grid = LayoutGrid(parent=gridParent, align=uiconst.TOPLEFT, columns=2, cellSpacing=(24, 0))
        hasLpRewards = bool(any((x.lpRewards for x in self._inputRequiredByTypeID.itervalues())))
        lpRewardsText = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/TotalLpPayout') if hasLpRewards else ''
        EveLabelMedium(parent=grid, text=lpRewardsText)
        hasIskRewards = bool(any((x.iskRewards for x in self._inputRequiredByTypeID.itervalues())))
        iskRewardsText = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/TotalIskPayout') if hasIskRewards else ''
        EveLabelMedium(parent=grid, text=iskRewardsText)
        self.lpLabel = EveLabelMedium(parent=grid, state=uiconst.UI_NORMAL)
        self.iskLabel = EveLabelMedium(parent=grid)
        self.lpLabel.display = hasLpRewards
        self.iskLabel.display = hasIskRewards

    def _GetPaddingValue(self):
        padding = 8 if self.margin_mode == WindowMarginMode.COMPACT else 16
        return padding

    def ConstructRightSide(self, showIcon):
        self.outputCont = UnderConstructionOutputCont(parent=self.righSide, align=uiconst.CENTERRIGHT, constructedTypeID=self._constructedTypeID, showIcon=showIcon)

    def LoadInputItems(self):
        self.inputScroll.Flush()
        inputItemsList = self._inputRequiredByTypeID.items()
        inputItemsList.sort()
        cargoQtyByTypeID = self.GetQtyByTypeID_Cargo()
        paddingValue = self._GetPaddingValue()
        for input in inputItemsList:
            typeID, inputInfo = input
            qtyInCargo = cargoQtyByTypeID.get(typeID, 0)
            itemController = InputItemController(typeID, inputInfo.qtyRequired, inputInfo.iskRewards, inputInfo.lpRewards, isSelected=bool(qtyInCargo))
            inputEntry = UnderConstructionInputScrollEntry(parent=self.inputScroll, align=uiconst.TOTOP, itemController=itemController, inputChangedCallback=self.OnInputChanged, qtyInCargo=qtyInCargo, paddingValue=paddingValue, padBottom=1)
            self.inputEntriesByTypeID[typeID] = inputEntry

    def DepositItems(self, *args):
        with locks.TempLock('UnderConstructionWnd_DepositItems_%s' % self._itemID):
            sucessfulDeposit = False
            try:
                self._depositingItems = True
                self._depositBtnDelay = True
                self.depositItemsBtn.Disable()
                qtyByTypeID = self.GetTypeIDsAndQtyFromInputEntries()
                if self.DepositConfirmed(qtyByTypeID):
                    failedToMove = self._DoDepositItems(qtyByTypeID)
                    sucessfulDeposit = not failedToMove
            finally:
                self._depositingItems = False
                if sucessfulDeposit:
                    self.Close()
                else:
                    uthread2.call_after_wallclocktime_delay(self.EnableBtnAfterDeposit, 1.0)
                self.Refresh()

    def ChangeSelection(self, *args):
        numItemsSelected = sum((qty for qty in self.GetTypeIDsAndQtyFromInputEntries().itervalues()))
        deselectAll = bool(numItemsSelected)
        if deselectAll:
            for typeID, inputEntry in self.inputEntriesByTypeID.iteritems():
                inputEntry.SetEntryDeselected()

        else:
            for typeID, inputEntry in self.inputEntriesByTypeID.iteritems():
                inputEntry.SelectNonSelectedEntry()
                maxValue = inputEntry.inputItemController.maxToAdd
                inputEntry.inputCont.inputEdit.SetValue(maxValue, False)

        self.Refresh()

    def EnableBtnAfterDeposit(self):
        self._depositBtnDelay = False
        self.UpdateBtn()

    def DepositConfirmed(self, qtyByTypeID):
        depositTextList = [ u'\u2022 %s' % GetByLabel('UI/Common/QuantityAndItem', quantity=qty, item=typeID) for typeID, qty in qtyByTypeID.iteritems() if qty ]
        depositText = '<br>'.join(depositTextList)
        rewardTextList = []
        totalIsk, totalLP, _ = self.GetRewardsFromTypeIDAndQty()
        if totalIsk or totalLP:
            if totalIsk:
                rewardTextList += [FmtISK(totalIsk)]
            if totalLP:
                rewardTextList += [FmtLP(totalLP)]
        rewardText = ''
        if rewardTextList:
            rewardText += '<br><br>%s<br>' % GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/RewardsTextInConfirmation')
            rewardText += '<br>'.join(rewardTextList)
        if eve.Message('ConfirmUnderConstructionDeposit', {'itemList': depositText,
         'rewardText': rewardText}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            return True
        return False

    def GetTypeIDsAndQtyFromInputEntries(self):
        qtyByTypeID = {}
        for typeID, inputEntry in self.inputEntriesByTypeID.iteritems():
            inputQty = inputEntry.GetInputQty()
            qtyByTypeID[typeID] = inputQty

        return qtyByTypeID

    def _DoDepositItems(self, qtyByTypeID):
        ballpark = sm.GetService('michelle').GetBallpark()
        underConstructionComp = ballpark.componentRegistry.GetComponentForItem(self._itemID, UNDER_CONSTRUCTION)
        failedToMove = underConstructionComp.DepositItemsFromShip(qtyByTypeID)
        if failedToMove:
            failedTextList = [ u'\u2022 %s' % GetByLabel('UI/Common/QuantityAndItem', quantity=qty, item=typeID) for typeID, qty in failedToMove.iteritems() if qty > 0 ]
            failedText = '<br>'.join(failedTextList)
            eve.Message('FailedUnderConstructionDeposit', {'itemList': failedText})
        return failedToMove

    def OnInputChanged(self, *args):
        self.Refresh()

    def Refresh(self):
        self._RefreshThrottled()

    @throttled(0.5)
    def _RefreshThrottled(self):
        if self._depositingItems:
            return
        self.UpdateInputEntries()
        self.UpdateRewards()
        self.UpdateBtn()

    def UpdateInputEntries(self):
        underConstructionQtyByTypeID = self.GetQtyByTypeID_UnderConstruction()
        cargoQtyByTypeID = self.GetQtyByTypeID_Cargo()
        qtyByTypeIdInWnd = {}
        qtyByTypeIdInContainer = {}
        for typeID, inputEntry in self.inputEntriesByTypeID.iteritems():
            unitsInContainer = underConstructionQtyByTypeID.get(typeID, 0)
            qtyInCargo = cargoQtyByTypeID.get(typeID, 0)
            inputEntry.UpdateEntry(unitsInContainer, qtyInCargo)
            if unitsInContainer:
                qtyByTypeIdInContainer[typeID] = unitsInContainer
            if inputEntry.GetInputQty():
                qtyByTypeIdInWnd[typeID] = inputEntry.GetInputQty()

        self.outputCont.UpdateProgress(qtyByTypeIdInContainer, qtyByTypeIdInWnd, self._qtyRequiredByTypeID)

    def GetQtyByTypeID_UnderConstruction(self):
        underConstructionQtyByTypeID = defaultdict(int)
        for item in self.invController.GetItems():
            underConstructionQtyByTypeID[item.typeID] += item.stacksize

        return underConstructionQtyByTypeID

    def GetQtyByTypeID_Cargo(self):
        cargoInvController = ShipCargo()
        cargoQtyByTypeID = defaultdict(int)
        for item in cargoInvController.GetItems():
            cargoQtyByTypeID[item.typeID] += item.stacksize

        return cargoQtyByTypeID

    def UpdateRewards(self):
        totalIsk, totalLP, lpByCorp = self.GetRewardsFromTypeIDAndQty()
        self.iskLabel.SetText(FmtISK(totalIsk))
        self.lpLabel.SetText(FmtLP(totalLP))
        if lpByCorp:
            corpsAndLp = sorted(lpByCorp.items())
            textList = []
            for corpID, lp in corpsAndLp:
                t = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/NumLpFromCorp', numLP=lp, corpName=cfg.eveowners.Get(corpID).name)
                textList.append(t)

            self.lpLabel.hint = '<br>'.join(textList)
        else:
            self.lpLabel.hint = ''

    def GetRewardsFromTypeIDAndQty(self):
        totalIsk = 0
        totalLP = 0
        qtyByTypeID = self.GetTypeIDsAndQtyFromInputEntries()
        lpByCorp = defaultdict(int)
        for typeID, inputQty in qtyByTypeID.iteritems():
            inputInfo = self._inputRequiredByTypeID.get(typeID, None)
            if inputInfo:
                totalIsk += inputQty * inputInfo.iskRewards
                lpForType = 0
                for corpID, lp in inputInfo.lpRewards.iteritems():
                    numLpFromCorp = inputQty * lp
                    lpForType += numLpFromCorp
                    lpByCorp[corpID] += numLpFromCorp

                totalLP += lpForType

        return (totalIsk, totalLP, lpByCorp)

    def UpdateBtn(self):
        if self._depositBtnDelay:
            return
        numItems = sum((qty for qty in self.GetTypeIDsAndQtyFromInputEntries().itervalues()))
        totalMaxValue = sum((inputEntry.inputItemController.maxToAdd for inputEntry in self.inputEntriesByTypeID.itervalues()))
        if numItems > 0:
            self.depositItemsBtn.Enable()
            self.changeSelectionBtn.SetLabel(GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/DeselectAllItems'))
            self.changeSelectionBtn.hint = ''
        else:
            self.depositItemsBtn.Disable()
            self.changeSelectionBtn.SetLabel(GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/AutoSelect'))
            self.changeSelectionBtn.hint = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/AutoSelectHint')
        if totalMaxValue:
            self.changeSelectionBtn.Enable()
        else:
            self.changeSelectionBtn.Disable()

    def OnInvChangeAny(self, item, change):
        if self._AreWeInterestedInChange(item, change):
            self.Refresh()

    def _AreWeInterestedInChange(self, itemID, change):
        if itemID.locationID in (session.shipid, self._itemID):
            return True
        if appConst.ixLocationID in change and change[appConst.ixLocationID] == session.shipid:
            return True
        return False

    def OnSessionChanged(self, isRemote, sess, change):
        if 'shipid' in change:
            self.Refresh()

    def Close(self, *args, **kwargs):
        super(UnderConstructionWnd, self).Close(*args, **kwargs)
        sm.GetService('inv').Unregister(self.invCookie)
