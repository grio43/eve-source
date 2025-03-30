#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menuSvcExtras\invItemFunctions.py
import collections
from collections import defaultdict
import blue
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.net.moniker import Moniker
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import uiconst
from carbonui.uicore import uicore
import uthread2
import destiny
from eve.client.script.ui.shared.neocom.corporation.corp_ui_votes import VoteWizardDialog
from eve.client.script.ui.shared.neocom.ownerSearch import OwnerSearchWindow
from eve.client.script.ui.shared.shipNameDialog import prompt_rename_ship
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.eveCfg import IsControllingStructure
from eve.common.script.util import notificationconst
from eveexceptions import UserError
from eveexceptions.const import UE_TYPEIDL
import evetypes
from inventorycommon.util import IsModularShip
from inventoryrestrictions import is_trashable, CANNOT_TRASH_ERROR
from inventoryutil.client.inventory import get_hangar_inventory
import localization
from eve.client.script.ui.util import uix
from corporation import voting
from shipprogression.boarding_moment.boardingMomentSvc import GetBoardingMomentService

def LaunchSMAContents(invItem):
    _CheckIfValidStateToLaunchFromContainer()
    sm.GetService('gameui').GetShipAccess().LaunchFromContainer(invItem.locationID, invItem.itemID)


def LaunchShipOrContainerFromWreckOrContainer(invItem):
    _CheckIfValidStateToLaunchFromContainer()
    sm.RemoteSvc('eject').LaunchShipOrContainerFromWreckOrContainer(invItem.locationID, invItem.itemID)


def _CheckIfValidStateToLaunchFromContainer():
    bp = sm.GetService('michelle').GetBallpark()
    myShipBall = bp.GetBall(session.shipid)
    if myShipBall and myShipBall.mode == destiny.DSTBALL_WARP:
        raise UserError('ShipInWarp')


def Jettison(invItems, showPrompt = True):
    if showPrompt and eve.Message('ConfirmJettison', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
        return
    itemsByID = {invItem.itemID:invItem for invItem in invItems}
    ship = sm.StartService('gameui').GetShipAccess()
    if ship:
        itemIDs = itemsByID.keys()
        jettisonedToCanIDs, jettisonItemList = ship.Jettison(itemIDs)
        notJettisonedIDs = set(itemIDs) - set(jettisonedToCanIDs) - set(jettisonItemList)
        notJettisonedTypeIDs = set()
        for itemID in notJettisonedIDs:
            if itemID in itemsByID:
                item = itemsByID[itemID]
                notJettisonedTypeIDs.add(item.typeID)

        if notJettisonedTypeIDs:
            raise UserError('NotAllItemsWereJettisoned', {'itemList': (UE_TYPEIDL, notJettisonedTypeIDs)})


def JettisonStructureFuel(invItems):
    if eve.Message('ConfirmJettison', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
        return
    Moniker('structure', session.structureid).JettisonStructureFuel([ i.itemID for i in invItems ])


def Reprocess(invItems):
    if not session.stationid and not session.structureid:
        return
    sm.StartService('reprocessing').ReprocessDlg(invItems)


def TrainNow(invItems):
    if len(invItems) > 1:
        eve.Message('TrainMoreTheOne')
        return
    InjectSkillIntoBrain(invItems)
    blue.pyos.synchro.SleepWallclock(500)
    sm.GetService('skillqueue').TrainSkillNow(invItems[0].typeID, 1)


def InjectSkillIntoBrain(invItems):
    sm.StartService('skills').InjectSkillIntoBrain(invItems)


def PlugInImplant(invItems):
    if eve.Message('ConfirmPlugInImplant', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
        return
    PlaySound(uiconst.SOUND_ADD_OR_USE)
    for invItem in invItems:
        sm.StartService('godma').GetDogmaLM().InjectImplant(invItem.itemID)
        sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeImplantPluggedIn, {'typeID': invItem.typeID})


def ConsumeBooster(invItems):
    if type(invItems) is not list:
        invItems = [invItems]
    for invItem in invItems:
        sm.StartService('godma').GetDogmaLM().UseBooster(invItem.itemID, invItem.locationID)
        sm.GetService('notificationSvc').MakeAndScatterNotification(notificationconst.notificationTypeBoosterConsumed, {'typeID': invItem.typeID})


def DeliverToStructure(items, invCacheSvc):
    if not session.structureid:
        return
    if not isinstance(items, collections.Iterable):
        items = [items]
    items = [ item for item in items if invCacheSvc.GetStationIDOfItem(item) == session.structureid ]
    if not items:
        return

    def Confirm(characterID):
        formatted = [ '<t>- %sx %s<br>' % (item.stacksize, GetShowInfoLink(item.typeID, evetypes.GetName(item.typeID), item.itemID)) for item in items ]
        data = {'items': ''.join(formatted),
         'character': characterID}
        if eve.Message('ConfirmDeliverItems', data, uiconst.YESNO) == uiconst.ID_YES:
            sm.RemoteSvc('structureDeliveries').Deliver(session.structureid, characterID, [ item.itemID for item in items ])

    def Deliver(results):
        for row in results():
            OwnerSearchWindow.CloseIfOpen(windowID='DeliverToStructure')
            return Confirm(row.charID)

    OwnerSearchWindow.CloseIfOpen(windowID='DeliverToStructure')
    OwnerSearchWindow.Open(windowID='DeliverToStructure', actionBtns=[(localization.GetByLabel('UI/Inventory/ItemActions/DeliverItems'), Deliver, True)], caption=localization.GetByLabel('UI/Inventory/ItemActions/DeliverItemsHeader'), input='', showContactList=True, multiSelect=False, ownerGroups=[const.groupCharacter])


def AssembleShip(invItems):
    import stackless
    from eve.client.script.ui.station.assembleModularShip import prompt_assemble_modular_ship
    itemIDs = []
    subSystems = None
    invCache = sm.GetService('invCache')
    for item in invItems:
        lockInfo = invCache.IsItemLocked_NoLock(item.itemID)
        cfg.evelocations.RemoveFromKnowLuzers(item.itemID)
        if lockInfo[0] and lockInfo[7] != stackless.getcurrent():
            continue
        if IsModularShip(item.typeID):
            if not (eveCfg.IsDocked() or IsControllingStructure()):
                eve.Message('CantAssembleModularShipInSpace')
                return
            subSystems = prompt_assemble_modular_ship(item)
            if subSystems:
                itemIDs = item.itemID
                break
            else:
                continue
        itemIDs.append(item.itemID)

    if itemIDs:
        singleItem = not isinstance(itemIDs, list) or len(itemIDs) == 1
        if singleItem and not settings.user.suppress.Get('suppress.ShipNameChangeOnAssemble', False):
            name = prompt_rename_ship(ship_type_id=item.typeID, show_suppress=True)
        else:
            name = None
        PlaySound('ship_goals_assemble_ship_play')
        bmSvc = GetBoardingMomentService()
        if not bmSvc.HasSeen(item.typeID):
            bmSvc.SetUnseen(item.typeID)
        return sm.StartService('gameui').GetShipAccess().AssembleShip(itemIDs, name=name, subSystems=subSystems)


def AssembleAndBoardShip(invItem):
    shipID = AssembleShip([invItem])
    if not shipID:
        return
    if isinstance(shipID, list):
        shipID = shipID[0]
    if session.stationid:
        ship = None
        if shipID != invItem.itemID:
            uthread2.Yield()
            inventory = get_hangar_inventory()
            for item in inventory.List():
                if item.itemID == shipID:
                    ship = item
                    break

        else:
            ship = invItem
        if bool(ship):
            sm.GetService('station').TryActivateShip(ship)
    elif session.structureid:
        sm.GetService('structureDocking').ActivateShip(shipID)
    PlaySound('ship_goals_assemble_board_ship_play')


def CheckItemsInSamePlace(invItems):
    if len(invItems) == 0:
        return
    locationID = invItems[0].locationID
    flag = invItems[0].flagID
    ownerID = invItems[0].ownerID
    for item in invItems:
        if item.locationID != locationID or item.flagID != flag or item.ownerID != ownerID:
            raise UserError('ItemsMustBeInSameHangar')
        locationID = item.locationID
        ownerID = item.ownerID
        flag = item.flagID


def InSameStructureWithCorrectFlag(invItem, allowedFlags):
    currentStructureID = session.structureid
    if not currentStructureID:
        return False
    if invItem.locationID != currentStructureID:
        return False
    if invItem.flagID in allowedFlags:
        return True
    return False


def CheckIfInPrimedOffice(invItem):
    office = sm.StartService('officeManager').GetCorpOfficeAtLocation()
    return office is not None and invItem.locationID == office.officeID


def CheckSameStation(invItem):
    if session.stationid:
        if invItem.locationID == session.stationid:
            return 1
        if isinstance(invItem, blue.DBRow) and 'stationID' in invItem.__columns__ and invItem.stationID == session.stationid:
            return 1
        if CheckIfInPrimedOffice(invItem):
            return 1
        if idCheckers.IsPlayerItem(invItem.locationID) and sm.GetService('invCache').IsInventoryPrimedAndListed(invItem.locationID):
            return 1
    return 0


def InvalidateItemLocation(ownerID, stationID, flag, invCacheSvc):
    if ownerID == session.corpid:
        which = 'offices'
        if flag == const.flagCorpDeliveries:
            which = 'deliveries'
        sm.services['objectCaching'].InvalidateCachedMethodCall('corpmgr', 'GetAssetInventoryForLocation', session.corpid, stationID, which)
    else:
        sm.services['objectCaching'].InvalidateCachedMethodCall('stationSvc', 'GetStation', stationID)
        invCacheSvc.GetInventory(const.containerGlobal).InvalidateStationItemsCache(stationID)


def DeliverToCorpHangarFolder(invItemAndFlagList, invCacheSvc):
    if len(invItemAndFlagList) == 0:
        return
    invItems = []
    itemIDs = []
    for item, flagID in invItemAndFlagList:
        invItems.append(item)
        itemIDs.append(item.itemID)

    CheckItemsInSamePlace(invItems)
    fromID = invItems[0].locationID
    doSplit = bool(uicore.uilib.Key(uiconst.VK_SHIFT) and len(invItemAndFlagList) == 1 and invItemAndFlagList[0][0].stacksize > 1)
    stationID = invCacheSvc.GetStationIDOfItem(invItems[0])
    if stationID is None:
        raise UserError('CanOnlyDoInStations')
    ownerID = invItems[0].ownerID
    flag = invItems[0].flagID
    deliverToFlag = invItemAndFlagList[0][1]
    qty = None
    if doSplit:
        invItem = invItems[0]
        ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, localization.GetByLabel('UI/Inventory/ItemActions/DivideItemStack'))
        if ret is not None:
            qty = ret['qty']
    invCacheSvc.GetInventoryMgr().DeliverToCorpHangar(fromID, stationID, itemIDs, qty, ownerID, deliverToFlag)
    InvalidateItemLocation(ownerID, stationID, flag, invCacheSvc)
    if ownerID == session.corpid:
        sm.ScatterEvent('OnCorpAssetChange', invItems, stationID)


def DeliverToCorpMember(invItems, invCacheSvc):
    if len(invItems) == 0:
        return
    CheckItemsInSamePlace(invItems)
    corpMemberIDs = sm.GetService('corp').GetMemberIDs()
    cfg.eveowners.Prime(corpMemberIDs)
    memberslist = []
    for memberID in corpMemberIDs:
        who = cfg.eveowners.Get(memberID)
        memberslist.append([who.ownerName, memberID, who.typeID])

    stationID = invCacheSvc.GetStationIDOfItem(invItems[0])
    if stationID is None:
        raise UserError('CanOnlyDoInStations')
    res = uix.ListWnd(memberslist, 'character', localization.GetByLabel('UI/Corporations/Common/SelectCorpMember'), localization.GetByLabel('UI/Corporations/Common/SelectCorpMemberToDeliverTo'), 1)
    if res:
        corporationMemberID = res[1]
        return _DeliverToCorpMemberID(corporationMemberID, invItems, invCacheSvc)


def _DeliverToCorpMemberID(corporationMemberID, invItems, invCacheSvc):
    doSplit = uicore.uilib.Key(uiconst.VK_SHIFT) and len(invItems) == 1 and invItems[0].stacksize > 1
    stationID = invCacheSvc.GetStationIDOfItem(invItems[0])
    if stationID is None:
        raise UserError('CanOnlyDoInStations')
    ownerID = invItems[0].ownerID
    flagID = invItems[0].flagID
    itemIDs = [ item.itemID for item in invItems ]
    qty = None
    if doSplit:
        invItem = invItems[0]
        ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, localization.GetByLabel('UI/Inventory/ItemActions/DivideItemStack'))
        if ret is not None:
            qty = ret['qty']
    invCacheSvc.GetInventoryMgr().DeliverToCorpMember(corporationMemberID, stationID, itemIDs, qty, ownerID, flagID)
    InvalidateItemLocation(ownerID, stationID, flagID, invCacheSvc)
    if ownerID == session.corpid:
        sm.ScatterEvent('OnCorpAssetChange', invItems, stationID)


def DeliverToMyself(invItems, invCacheSvc):
    if len(invItems) == 0:
        return
    CheckItemsInSamePlace(invItems)
    _DeliverToCorpMemberID(session.charid, invItems, invCacheSvc)


def SplitStack(invItems, invCacheSvc):
    if len(invItems) != 1:
        raise UserError('CannotPerformOnMultipleItems')
    invItem = invItems[0]
    ret = uix.QtyPopup(invItem.stacksize, 1, 1, None, localization.GetByLabel('UI/Inventory/ItemActions/DivideItemStack'))
    if ret is not None:
        qty = ret['qty']
        stationID = invCacheSvc.GetStationIDOfItem(invItem)
        if stationID is None:
            raise UserError('CanOnlyDoInStations')
        flag = invItem.flagID
        invCacheSvc.GetInventoryMgr().SplitStack(stationID, invItem.itemID, qty, invItem.ownerID)
        InvalidateItemLocation(invItem.ownerID, stationID, flag, invCacheSvc)
        if invItem.ownerID == session.corpid:
            invItem.quantity = invItem.quantity - qty
            sm.ScatterEvent('OnCorpAssetChange', [invItem], stationID)


def LockDownBlueprint(invItem):
    try:
        stationID = {o.stationID for o in sm.StartService('officeManager').GetMyCorporationsOffices() if o.officeID == invItem.locationID}.pop()
    except KeyError:
        return

    blueprint = sm.GetService('blueprintSvc').GetBlueprintItem(invItem.itemID)
    description = localization.GetByLabel('UI/Corporations/Votes/ProposeLockdownDescription', blueprintLocation=stationID, efficiencyLevel=blueprint.materialEfficiency, productivityLevel=blueprint.timeEfficiency)
    formData = {'voteType': voting.voteItemLockdown,
     'voteTitle': localization.GetByLabel('UI/Corporations/Votes/LockdownItem', blueprint=invItem.typeID),
     'voteDescription': description,
     'voteDays': 1,
     'itemID': invItem.itemID,
     'typeID': invItem.typeID,
     'flagInput': invItem.flagID,
     'locationID': stationID}
    dlg = VoteWizardDialog.Open(**formData)
    dlg.GoToStep(len(dlg.steps))
    dlg.ShowModal()


def UnlockBlueprint(invItem):
    dlg = VoteWizardDialog.Open()
    stationID = dlg.locationID
    blueprint = sm.GetService('blueprintSvc').GetBlueprintItem(invItem.itemID)
    description = localization.GetByLabel('UI/Corporations/Votes/ProposeLockdownDescription', blueprintLocation=stationID, efficiencyLevel=blueprint.materialEfficiency, productivityLevel=blueprint.timeEfficiency)
    dlg.voteType = voting.voteItemUnlock
    dlg.voteTitle = localization.GetByLabel('UI/Corporations/Votes/UnlockItem', blueprint=invItem.typeID)
    dlg.voteDescription = description or dlg.voteTitle
    dlg.voteDays = 1
    dlg.itemID = invItem.itemID
    dlg.typeID = invItem.typeID
    dlg.flagInput = invItem.flagID
    dlg.locationID = stationID
    dlg.GoToStep(len(dlg.steps))
    dlg.ShowModal()


def ALSCLock(invItems, invCacheSvc):
    if len(invItems) < 1:
        return
    container = invCacheSvc.GetInventoryFromId(invItems[0].locationID)
    container.ALSCLockItems([ i.itemID for i in invItems ])


def ALSCUnlock(invItems, invCacheSvc):
    if len(invItems) < 1:
        return
    container = invCacheSvc.GetInventoryFromId(invItems[0].locationID)
    container.ALSCUnlockItems([ i.itemID for i in invItems ])


def GetContainerContents(containerItem, invCacheSvc, dockableID):
    dockableID = containerItem.locationID if dockableID is None else dockableID
    if not (idCheckers.IsStation(dockableID) or sm.GetService('structureDirectory').GetStructureInfo(dockableID)):
        raise RuntimeError('GetContainerContents: dockableID is neither structure nor station.')
    DoGetContainerContents(containerItem.itemID, dockableID, containerItem.typeID, invCacheSvc)


def DoGetContainerContents(itemID, stationID, containerTypeID, invCacheSvc):
    from eve.client.script.ui.shared.inventory.containerContentWindow import ContainerContentWindow
    wnd = ContainerContentWindow.GetIfOpen()
    if not wnd or wnd.destroyed:
        wnd = ContainerContentWindow()
    wnd.LoadContent(itemID=itemID, stationID=stationID, containerTypeID=containerTypeID, invCacheSvc=invCacheSvc)
    wnd.Maximize()


def CheckLocked(func, invItemsOrIDs, invCacheSvc):
    if not len(invItemsOrIDs):
        return
    if type(invItemsOrIDs[0]) == int or not hasattr(invItemsOrIDs[0], 'itemID'):
        ret = func(invItemsOrIDs)
    else:
        lockedItems = []
        try:
            for item in invItemsOrIDs:
                if invCacheSvc.IsItemLocked(item.itemID):
                    continue
                if invCacheSvc.TryLockItem(item.itemID):
                    lockedItems.append(item)

            if not len(lockedItems):
                eve.Message('BusyItems')
                return
            ret = func(lockedItems)
        finally:
            for invItem in lockedItems:
                invCacheSvc.UnlockItem(invItem.itemID)

    return ret


def CheckRepackageItems(invItems, warnAboutContainers):
    repackage = []
    if not invItems:
        return repackage
    insuranceQ_OK = 0
    containerQ_OK = -1
    insuranceContracts = None
    godma = sm.GetService('godma')
    for item in invItems:
        if item.typeID == const.typePlasticWrap:
            continue
        itemState = godma.GetItem(item.itemID)
        if itemState and (itemState.damage or item.categoryID in (const.categoryShip, const.categoryDrone) and itemState.armorDamage):
            eve.Message('CantRepackageDamagedItem')
            continue
        if item.categoryID == const.categoryShip:
            if insuranceContracts is None:
                insuranceContracts = sm.StartService('insurance').GetContracts()
            if not insuranceQ_OK and item.itemID in insuranceContracts:
                if eve.Message('RepairUnassembleVoidsContract', {}, uiconst.YESNO) != uiconst.ID_YES:
                    continue
                insuranceQ_OK = 1
        containerGroups = (const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer)
        if warnAboutContainers and item.singleton and item.groupID in containerGroups:
            if not containerQ_OK:
                continue
            if containerQ_OK == -1:
                if sm.GetService('invCache').GetInventoryFromId(item.itemID).List():
                    if eve.Message('RepackageContainers', {}, uiconst.YESNO) != uiconst.ID_YES:
                        containerQ_OK = 0
                        continue
                    containerQ_OK = 1
        repackage.append(item)

    return repackage


def RepackageItems(invItems):
    if any([ i.singleton for i in invItems ]):
        if eve.Message('ConfirmRepackageItem', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
    invItems = CheckRepackageItems(invItems, len(invItems) > 1)
    if not invItems:
        return
    invCache = sm.GetService('invCache')
    itemsByStation = collections.defaultdict(list)
    for item in invItems:
        itemsByStation[invCache.GetStationIDOfItem(item) or item.locationID].append((item.itemID, item.locationID))

    itemsByStation = dict(itemsByStation)
    try:
        sm.RemoteSvc('repackagingSvc').RepackageItems(itemsByStation)
    except UserError as exception:
        if exception.msg == 'ConfirmRepackageSomethingWithUpgrades':
            if eve.Message(exception.msg, exception.dict, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                sm.RemoteSvc('repackagingSvc').RepackageItems(dict(itemsByStation), destroyable=True)
        elif exception.msg == 'ConfirmRepackageMultipleItemsWithUpgrades':
            failedItemIDs = exception.dict.get('itemIDs')
            itemStationTupleByItemID = {}
            for stationID, itemList in itemsByStation.iteritems():
                for itemTuple in itemList:
                    itemStationTupleByItemID[itemTuple[0]] = (stationID, itemTuple)

            newItemsByStation = defaultdict(list)
            for eachItemID in failedItemIDs:
                itemStationTuple = itemStationTupleByItemID.get(eachItemID, None)
                if itemStationTuple:
                    stationID, itemTuple = itemStationTuple
                    newItemsByStation[stationID].append(itemTuple)

            if eve.Message(exception.msg, exception.dict, uiconst.YESNO) == uiconst.ID_YES:
                sm.RemoteSvc('repackagingSvc').RepackageItems(dict(newItemsByStation), destroyable=True)
        else:
            raise

    PlaySound('ship_goals_repackage_ship_play')


def Break(invItems, invCacheSvc):
    ok = 0
    validIDs = []
    for invItem in invItems:
        if ok or eve.Message('ConfirmBreakCourierPackage', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            validIDs.append(invItem.itemID)
            ok = 1

    for itemID in validIDs:
        invCacheSvc.GetInventoryFromId(itemID).BreakPlasticWrap()


def TrashInvItems(invItems, invCacheSvc, showPrompt = True):
    if len(invItems) == 0:
        return
    CheckItemsInSamePlace(invItems)
    if showPrompt and not _IsTrashingAcceptedByUser(invItems[:]):
        return
    stationID = invCacheSvc.GetStationIDOfItem(invItems[0])
    itemsToTrash = []
    for item in invItems:
        if is_trashable(item.typeID):
            itemsToTrash.append(item.itemID)
        else:
            eve.Message(CANNOT_TRASH_ERROR)
            return

    locationID = stationID if stationID else invItems[0].locationID
    errors = invCacheSvc.GetInventoryMgr().TrashItems(itemsToTrash, locationID)
    if errors:
        for e in errors:
            eve.Message(e)

        return
    isCorp = invItems[0].ownerID == session.corpid
    InvalidateItemLocation(session.corpid if isCorp else session.charid, stationID, invItems[0].flagID, invCacheSvc)
    if isCorp:
        sm.ScatterEvent('OnCorpAssetChange', invItems, stationID)


def _IsTrashingAcceptedByUser(invItems):
    if len(invItems) == 1:
        question = 'ConfirmTrashingSin'
        itemWithQuantity = cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, invItems[0].typeID, invItems[0].stacksize)
        args = {'itemWithQuantity': itemWithQuantity}
    else:
        question = 'ConfirmTrashingPlu'
        report = ''
        overflow_item_count = max(len(invItems) - 10, 0)
        if overflow_item_count > 0:
            invItems = invItems[:10]
        for item in invItems:
            report += '<t>- %s<br>' % cfg.FormatConvert(const.UE_TYPEIDANDQUANTITY, item.typeID, item.stacksize)

        if overflow_item_count > 0:
            report += u'<t>{}<br>'.format(localization.GetByLabel('UI/Inventory/TrashItemsOverflowCount', count=overflow_item_count))
        args = {'items': report}
    response = eve.Message(question, args, uiconst.YESNO)
    return response == uiconst.ID_YES


def FindInPersonalAssets(typeID):
    from eve.client.script.ui.shared.assetsWindow import AssetsWindow
    wnd = AssetsWindow.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.Maximize()
        wnd.SearchTypeID(typeID)
    else:
        wnd = AssetsWindow.Open(exactTypeID=typeID)
        wnd.tabGroup.SelectByID('search')
