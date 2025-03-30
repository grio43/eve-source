#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\dropbox\dropboxWnd.py
import carbonui.const as uiconst
import inventorycommon
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold, EveCaptionMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import GradientThemeColored
from eve.client.script.ui.structure.dropbox.const import TILE_SIZE
from eve.client.script.ui.structure.dropbox.dropboxController import DropBoxController
from eve.client.script.ui.structure.dropbox.dropboxTilePlacer import DropBoxTilePlacer
from eve.client.script.ui.structure.dropbox.transferItem import TransferItem
from eve.common.script.util.eveFormat import FmtISKAndRound
from eveservices.menu import GetMenuService
from eveuniverse.security import securityClassZeroSec
from localization import GetByLabel
from reprocessing.ui.controller import NodesToItems
from signals.signalUtil import ChangeSignalConnect
from carbonui.uicore import uicore

class DropboxWnd(Window):
    __guid__ = 'dropboxWnd'
    __notifyevents__ = ['OnSessionChanged', 'OnClientEvent_WarpStarted']
    default_width = 400
    default_height = 400
    default_minSize = (300, 400)
    default_windowID = 'dropboxWnd'
    default_descriptionLabelPath = 'Tooltips/Neocom/HangarTransfer_description'
    default_captionLabelPath = 'Tooltips/Neocom/HangarTransfer'
    default_iconNum = 'res:/UI/Texture/WindowIcons/items.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        structureID = attributes.structureID
        structureTypeID = attributes.structureTypeID
        self.isTranferInProgress = False
        self.validRange = sm.GetService('godma').GetTypeAttribute(structureTypeID, const.attributeCargoDeliverRange)
        self.dropBoxController = DropBoxController(structureID, session.shipid)
        mainCont = Container(name='mainCont', parent=self.sr.main, padding=const.defaultPadding)
        self.transferToLabel = EveLabelMedium(name='transferToLabel', parent=mainCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padding=(6, 0, 6, 6))
        self.bottomContainer = Container(name='bottomCont', parent=mainCont, align=uiconst.TOBOTTOM, height=36, padTop=8)
        inputCont = Container(name='inputCont', parent=mainCont, align=uiconst.TOALL)
        self.inputInfoCont = TransferInputContainer(name='inputInfo', parent=inputCont, dropBoxController=self.dropBoxController)
        self.AddButtons()
        self.ChangeSignalConnection()
        sm.RegisterNotify(self)
        structureLink = GetShowInfoLink(structureTypeID, cfg.evelocations.Get(structureID).name, itemID=structureID)
        text = GetByLabel('UI/HangarTransfer/TransferTo', structureLink=structureLink)
        self.transferToLabel.text = text
        self.verifyingTimer = AutoTimer(1000, self.VerifyRestrictions)
        if attributes.itemsToTransfer:
            self.dropBoxController.AddManyItems(attributes.itemsToTransfer)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.dropBoxController.on_items_added, self.OnItemsAdded), (self.dropBoxController.on_items_removed, self.OnItemsRemoved), (self.dropBoxController.on_items_updated, self.OnItemsUpdated)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnItemsAdded(self, itemIDs):
        self.UpdateButton()

    def OnItemsRemoved(self, itemIDs):
        updateNoContentHint = not self.isTranferInProgress and self.dropBoxController.GetNumToBeTransferred() < 1
        self.inputInfoCont.RemoveItems(itemIDs, updateNoContentHint)
        self.UpdateButton()

    def OnItemsUpdated(self, itemIDs):
        self.UpdateButton()

    def AddButtons(self):
        btnCont = Container(name='buttonCont', parent=self.bottomContainer, align=uiconst.TOBOTTOM, height=36, idx=0)
        self.transferBtn = Button(name='transferBtn', parent=btnCont, label=GetByLabel('UI/HangarTransfer/TransferBtn'), func=self.TransferItems, align=uiconst.CENTERRIGHT)
        self.cancelButton = Button(parent=btnCont, label=GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel, align=uiconst.CENTERLEFT)
        self.UpdateButton()

    def UpdateButton(self):
        numItems = self.dropBoxController.GetNumToBeTransferred()
        if numItems:
            self.transferBtn.Enable()
            self.transferBtn.hint = ''
        else:
            self.transferBtn.Disable()
            self.transferBtn.hint = GetByLabel('UI/HangarTransfer/NothingToTransfer')

    def Cancel(self, *args):
        self.CloseByUser()

    def TransferItems(self, *args):
        try:
            self.isTranferInProgress = True
            itemRecsMoved = self.dropBoxController.TransferItems()
            self.inputInfoCont.PopulateMovedTiles(itemRecsMoved)
        finally:
            self.isTranferInProgress = False

    def Close(self, *args, **kwds):
        self.verifyingTimer = None
        sm.UnregisterNotify(self.dropBoxController)
        self.ChangeSignalConnection(connect=False)
        self.dropBoxController = None
        Window.Close(self, *args, **kwds)

    def OnClientEvent_WarpStarted(self, *args):
        self.Close()

    def OnSessionChanged(self, isRemote, session, change):
        if 'shipid' in change and session.shipid != self.dropBoxController.forShipID:
            self.Close()
        elif session.structureid or session.stationid:
            self.Close()

    def VerifyRestrictions(self):
        self.VerifyRange()
        self.VerifyNotCloaked()
        self.VerifyCrimewatchFlags()

    def VerifyRange(self):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return self.Close()
        try:
            structureID = self.dropBoxController.GetStructureID()
            dist = bp.GetBall(structureID).surfaceDist
            if dist > self.validRange:
                self.Close()
        except StandardError:
            self.Close()

    def VerifyNotCloaked(self):
        shipBall = sm.GetService('michelle').GetBall(session.shipid)
        if not shipBall:
            return self.Close()
        if shipBall.isCloaked:
            self.Close()

    def VerifyCrimewatchFlags(self):
        crimewatchSvc = sm.GetService('crimewatchSvc')
        if crimewatchSvc.IsCriminal(session.charid):
            if sm.GetService('map').GetSecurityClass(session.solarsystemid2) != securityClassZeroSec:
                eve.Message('CannotDeliverInEmpireWhileCriminal')
                self.Close()
                return
        if sm.GetService('crimewatchSvc').HaveWeaponsTimer():
            eve.Message('CannotDeliverWithWeaponsTimer')
            self.Close()


class TransferInputContainer(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.dropBoxController = attributes.dropBoxController
        infoCont = Container(name='infoCont', parent=self, align=uiconst.TOBOTTOM, height=38, clipChildren=True)
        self.CreateScrollContainer()
        self.numItemsLabel = EveLabelMedium(name='numItemsLabel', parent=infoCont, align=uiconst.TOPRIGHT, left=5, top=4)
        self.totalPriceLabel = EveLabelMedium(name='totalPriceLabel', parent=infoCont, align=uiconst.TOPRIGHT, left=5, top=20)
        inputTileParent = ContainerAutoSize(name='inputTileParent', parent=self.scrollCont, align=uiconst.TOTOP, percentage=0.5, alignMode=uiconst.TOTOP)
        tileContainer = FlowContainer(name='tileContainer', parent=inputTileParent, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, contentSpacing=(8, 8), padding=8)
        self.tilePlacer = DropBoxTilePlacer(tileContainer)
        self.overlayMoveCont = Container(name='overlayMoveCont', parent=inputTileParent, align=uiconst.TOALL)
        movedToText = GetByLabel('UI/HangarTransfer/MovedTo')
        overlayLabel = EveCaptionMedium(name='overlayLabel', parent=self.overlayMoveCont, align=uiconst.CENTERTOP, top=6, text=movedToText)
        self.overlayLabelDest = EveLabelMediumBold(name='overlayLabel2', parent=self.overlayMoveCont, align=uiconst.CENTERTOP, top=26, state=uiconst.UI_NORMAL, text='')
        self.overlayMoveCont.display = False
        self.movedTileContainer = FlowContainer(name='movedTileContainer', parent=inputTileParent, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, contentSpacing=(8, 8), padding=8)
        self.movedTilePlacer = DropBoxTilePlacer(self.movedTileContainer)
        self.ChangeSignalConnection(connect=True)
        self.UpdateItemInfo()

    def CreateScrollContainer(self):
        self.scrollCont = ScrollContainer(name='inputScroll', parent=self, align=uiconst.TOALL, showUnderlay=True)
        self.scrollCont.onDropDataSignal.connect(self.OnDroppingItems)
        self.scrollCont.GetAbsoluteSize()
        self.UpdateNoContentHint()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.dropBoxController.on_items_added, self.OnItemsAdded), (self.dropBoxController.on_items_updated, self.OnItemsUpdated)]
        ChangeSignalConnect(signalAndCallback, connect)

    def UpdateNoContentHint(self):
        if self.dropBoxController.IsDockableStructure():
            self.scrollCont.ShowNoContentHint(GetByLabel('UI/HangarTransfer/DropHereToTransfer'))
        else:
            self.scrollCont.ShowNoContentHint(GetByLabel('UI/HangarTransfer/DropHereToTransfer_NonDockable'))

    def OnItemsAdded(self, itemIDs):
        for eachItemID in itemIDs:
            self.AddItemToTilePlacer(eachItemID)

        if self.dropBoxController.GetNumToBeTransferred() > 0:
            self.scrollCont.HideNoContentHint()
        self.UpdateItemInfo()

    def RemoveItems(self, itemIDs, updateNoContentHint):
        for each in itemIDs:
            self.tilePlacer.RemoveItem(each)

        self.UpdateItemInfo()
        if updateNoContentHint:
            self.UpdateNoContentHint()

    def OnItemsUpdated(self, itemIDs):
        for eachItemID in itemIDs:
            itemContainer = self.MakeInputItem(eachItemID)
            if itemContainer:
                self.tilePlacer.ReplaceItem(eachItemID, itemContainer)

        self.UpdateItemInfo()

    def OnDroppingItems(self, dragObj, nodes):
        items = NodesToItems(nodes)
        self.dropBoxController.AddManyItems(items)

    def AddItemToTilePlacer(self, itemID):
        itemContainer = self.MakeInputItem(itemID)
        if itemContainer:
            self.tilePlacer.AddItem(itemID, itemContainer)
            self.tilePlacer.mainContainer.OnDropData = self.OnDroppingItems

    def MakeInputItem(self, itemID):
        itemRec = self.dropBoxController.GetItem(itemID)
        if not itemRec:
            return None
        return self._MakeInputItem(itemRec)

    def _MakeInputItem(self, itemRec, isRemovable = True):
        itemContainer = CreateInputItem(itemRec, self.dropBoxController, isRemovable=isRemovable)
        itemContainer.removeIcon.OnClick = (self.RemoveItem, itemRec.itemID)
        return itemContainer

    def RemoveItem(self, itemID):
        self.dropBoxController.RemoveItems([itemID])

    def GetItemMenu(self, itemID, typeID):
        menu = []
        menu += GetMenuService().GetMenuFromItemIDTypeID(itemID, typeID, includeMarketDetails=True)
        menu.append((GetByLabel('UI/Generic/RemoveItem'), self.RemoveItem, (itemID,)))
        return menu

    def _GetAveragePrice(self, typeID):
        price = inventorycommon.typeHelpers.GetAveragePrice(typeID)
        if price is None:
            return 0.0
        return price

    def UpdateItemInfo(self):
        allItems = self.dropBoxController.GetItems()
        numItems = self.dropBoxController.GetNumToBeTransferred()
        price = sum((self._GetAveragePrice(x.typeID) * max(1, x.quantity) for x in allItems))
        self.totalPriceLabel.text = GetByLabel('UI/Inventory/EstIskPrice', iskString=FmtISKAndRound(price, False))
        self.numItemsLabel.text = GetByLabel('UI/Inventory/NumItems', numItems=numItems, numFilteredTxt='')

    def PopulateMovedTiles(self, itemRecs):
        if self.dropBoxController.IsDockableStructure():
            destText = GetByLabel('UI/Inventory/ItemHangar')
        else:
            destText = GetByLabel('UI/Ship/FuelBay')
        self.overlayLabelDest.text = destText
        self.overlayMoveCont.display = True
        self.movedTileContainer.display = True
        uicore.animations.FadeTo(self.overlayMoveCont, 0.0, 1.0)
        self.movedTilePlacer.Clear()
        for each in itemRecs:
            itemContainer = self._MakeInputItem(each, isRemovable=False)
            if itemContainer:
                self.movedTilePlacer.AddItem(each.itemID, itemContainer)

        uicore.animations.FadeTo(self.movedTileContainer, 0.25, 0.0, timeOffset=2, callback=self.ResetMoved)

    def ResetMoved(self):
        self.movedTilePlacer.Clear()
        self.movedTileContainer.display = False
        self.overlayMoveCont.display = False
        self.UpdateNoContentHint()

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        self.dropboxController = None
        Container.Close(self)


def CreateInputItem(item, dropboxController, isRemovable):
    return TransferItem(align=uiconst.TOPLEFT, width=TILE_SIZE, height=TILE_SIZE, dropboxController=dropboxController, isRemovable=isRemovable, item=item)
