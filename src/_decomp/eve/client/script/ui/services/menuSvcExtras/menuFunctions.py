#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menuSvcExtras\menuFunctions.py
import sys
import types
import evetypes
import blue
import destiny
import localization
import log
import structures
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from cosmetics.client.shipSkinApplicationSvc import get_ship_skin_application_svc
from crates.crateutil import is_fixed_crate
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.crate.fixedcratewindow import FixedCrateWindow
from eve.client.script.ui.crate.window import CrateWindow
from eve.client.script.ui.services.encodedItemsWindow import EncodedItemsWindow
from eve.client.script.ui.shared.shipNameDialog import prompt_rename_ship
from eve.client.script.ui.shared.skillRequirementDialog import prompt_missing_skill_requirements
from eve.client.script.ui.skilltrading.skillInjectorWindow import SkillInjectorWindow
from eve.client.script.ui.util import searchOld
from eve.client.script.ui.util import uix, utilWindows
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg, idCheckers
from eveexceptions import UserError
from eveprefs import prefs
from inventorycommon.typeHelpers import GetAveragePrice
from menu import MenuLabel
from neocom2 import btnIDs
from structures.deployment import GetStructureNamePrefix
from utillib import KeyVal
import logging
logger = logging.getLogger(__name__)

def AddHint(hint, where):
    hintobj = Container(parent=where, name='hint', align=uiconst.TOPLEFT, width=200, height=16, idx=0, state=uiconst.UI_DISABLED)
    hintobj.hinttext = eveLabel.EveHeaderSmall(text=hint, parent=hintobj, top=4, state=uiconst.UI_DISABLED)
    border = Frame(parent=hintobj, frameConst=uiconst.FRAME_BORDER1_CORNER5, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25))
    frame = Frame(parent=hintobj, color=(0.0, 0.0, 0.0, 0.75), frameConst=uiconst.FRAME_FILLED_CORNER4, state=uiconst.UI_DISABLED)
    if hintobj.hinttext.textwidth > 200:
        hintobj.hinttext.width = 200
        hintobj.hinttext.text = '<center>' + hint + '</center>'
    hintobj.width = max(56, hintobj.hinttext.textwidth + 16)
    hintobj.height = max(16, hintobj.hinttext.textheight + hintobj.hinttext.top * 2)
    hintobj.left = (where.width - hintobj.width) / 2
    hintobj.top = -hintobj.height - 4
    hintobj.hinttext.left = (hintobj.width - hintobj.hinttext.textwidth) / 2


def AwardDecoration(charIDs):
    if not charIDs:
        return
    if not type(charIDs) == list:
        charIDs = [charIDs]
    info, graphics = sm.GetService('medals').GetAllCorpMedals(session.corpid)
    options = [ (medal.title, medal.medalID) for medal in info ]
    if len(options) <= 0:
        raise UserError('MedalCreateToAward')
    cfg.eveowners.Prime(charIDs)
    hintLen = 5
    hint = ', '.join([ cfg.eveowners.Get(charID).name for charID in charIDs[:hintLen] ])
    if len(charIDs) > hintLen:
        hint += ', ...'
    ret = uix.ListWnd(options, 'generic', localization.GetByLabel('UI/Corporations/Common/AwardCorpMemberDecoration'), isModal=1, ordered=1, scrollHeaders=[localization.GetByLabel('UI/Inventory/InvItemNameShort')], hint=hint)
    if ret:
        medalID = ret[1]
        sm.StartService('medals').GiveMedalToCharacters(medalID, charIDs)


def GetOwnerLabel(ownerID):
    name = ''
    if ownerID is not None:
        try:
            name = ' (' + cfg.eveowners.Get(ownerID).name + ')    '
        except:
            sys.exc_clear()

    return str(ownerID) + name


def CopyItemIDAndMaybeQuantityToClipboard(invItem):
    txt = str(invItem.itemID)
    if invItem.stacksize > 1:
        txt = MenuLabel('UI/Menusvc/ItemAndQuantityForClipboard', {'itemID': str(invItem.itemID),
         'quantity': invItem.stacksize})
    blue.pyos.SetClipboardData(txt)


def AddToQuickBar(typeID, parent = 0):
    sm.GetService('marketutils').AddTypeToQuickBar(typeID, parent)


def RemoveFromQuickBar(node):
    current = settings.user.ui.Get('quickbar', {})
    parent = node.parent
    typeID = node.typeID
    toDelete = None
    for dataID, data in current.items():
        if parent == data.parent and type(data.label) == types.IntType:
            if data.label == typeID:
                toDelete = dataID
                break

    if toDelete:
        del current[toDelete]
    settings.user.ui.Set('quickbar', current)
    sm.ScatterEvent('OnMarketQuickbarChange')


def TryLookAt(itemID, radius = None):
    slimItem = uix.GetBallparkRecord(itemID)
    isSiteBall = sm.GetService('sensorSuite').IsSiteBall(itemID)
    if not slimItem and not isSiteBall:
        return
    camera = sm.GetService('sceneManager').GetActivePrimaryCamera()
    camera.LookAt(itemID, objRadius=radius)


def ToggleLookAt(itemID, radius = None):
    bp = sm.GetService('michelle').GetBallpark()
    if bp:
        ball = bp.GetBall(session.shipid)
        if ball and ball.mode == destiny.DSTBALL_WARP:
            return
    TryLookAt(itemID, radius)


def AbandonLoot(wreckID):
    twit = sm.GetService('michelle')
    localPark = twit.GetBallpark()
    allowedGroup = None
    if wreckID in localPark.slimItems:
        allowedGroup = localPark.slimItems[wreckID].groupID
    if eve.Message('ConfirmAbandonLoot', {'type': (const.UE_GROUPID, allowedGroup)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
        return
    remotePark = sm.GetService('michelle').GetRemotePark()
    if remotePark is not None:
        remotePark.CmdAbandonLoot([wreckID])


def AbandonAllLoot(wreckID):
    twit = sm.GetService('michelle')
    localPark = twit.GetBallpark()
    remotePark = twit.GetRemotePark()
    if remotePark is None:
        return
    wrecks = []
    allowedGroup = None
    if wreckID in localPark.slimItems:
        allowedGroup = localPark.slimItems[wreckID].groupID
    if eve.Message('ConfirmAbandonLootAll', {'type': (const.UE_GROUPID, allowedGroup)}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
        return
    bp = sm.GetService('michelle').GetBallpark()
    for itemID, slimItem in localPark.slimItems.iteritems():
        if slimItem.groupID == allowedGroup:
            if bp.HaveLootRight(itemID) and not bp.IsAbandoned(itemID):
                wrecks.append(itemID)

    if remotePark is not None:
        remotePark.CmdAbandonLoot(wrecks)


def Eject(suppressConfirmation = False):
    if suppressConfirmation or eve.Message('ConfirmEject', {}, uiconst.YESNO) == uiconst.ID_YES:
        ship = sm.StartService('gameui').GetShipAccess()
        if ship:
            if session.stationid:
                eve.Message('NoEjectingToSpaceInStation')
            else:
                log.LogNotice('Ejecting from ship', session.shipid)
                sm.ScatterEvent('OnBeforeActiveShipChanged', None, eveCfg.GetActiveShip())
                sm.StartService('sessionMgr').PerformSessionChange('eject', ship.Eject)


def Board(itemID):
    ship = sm.StartService('gameui').GetShipAccess()
    if ship:
        typeID = None
        if not session.stationid:
            ballparkRecord = uix.GetBallparkRecord(itemID)
            if ballparkRecord:
                typeID = ballparkRecord.typeID
        else:
            item = sm.GetService('godma').GetItem(itemID)
            if item:
                typeID = item.typeID
        if typeID:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if len(dogmaLocation.GetMissingSkills(typeID)) > 0:
                prompt_missing_skill_requirements(typeID)
                return
        log.LogNotice('Boarding ship', itemID)
        sm.ScatterEvent('OnBeforeActiveShipChanged', itemID, eveCfg.GetActiveShip())
        sm.StartService('sessionMgr').PerformSessionChange('board', ship.Board, itemID, session.shipid or session.stationid)


def BoardSMAShip(structureID, shipID):
    ship = sm.StartService('gameui').GetShipAccess()
    if ship:
        log.LogNotice('Boarding SMA ship', structureID, shipID)
        sm.ScatterEvent('OnBeforeActiveShipChanged', shipID, eveCfg.GetActiveShip())
        sm.StartService('sessionMgr').PerformSessionChange('board', ship.BoardStoredShip, structureID, shipID)


def SafeLogoff():
    shipAccess = sm.GetService('gameui').GetShipAccess()
    failedConditions = shipAccess.SafeLogoff()
    if failedConditions:
        eve.Message('CustomNotify', {'notify': '<br>'.join([localization.GetByLabel('UI/Inflight/SafeLogoff/ConditionsFailedHeader')] + [ localization.GetByLabel(error) for error in failedConditions ])})


def AskNewContainerPassword(invCacheSvc, id_, desc, which = 1, setnew = '', setold = ''):
    container = invCacheSvc.GetInventoryFromId(id_)
    wndFormat = []
    if container.HasExistingPasswordSet(which):
        wndFormat.append({'type': 'edit',
         'setvalue': setold or '',
         'label': localization.GetByLabel('UI/Menusvc/OldPassword'),
         'key': 'oldpassword',
         'maxlength': 16,
         'setfocus': 1,
         'passwordChar': '*'})
    wndFormat.append({'type': 'edit',
     'setvalue': setnew or '',
     'label': localization.GetByLabel('UI/Menusvc/NewPassword'),
     'key': 'newpassword',
     'maxlength': 16,
     'passwordChar': '*'})
    wndFormat.append({'type': 'edit',
     'setvalue': '',
     'label': localization.GetByLabel('UI/Menusvc/ConfirmPassword'),
     'key': 'conpassword',
     'maxlength': 16,
     'passwordChar': '*'})
    retval = uix.HybridWnd(wndFormat, desc, windowID='askNewContainerPassword', icon=uiconst.QUESTION, minW=420, minH=75)
    if retval:
        old = retval['oldpassword'] or None if 'oldpassword' in retval else None
        new = retval['newpassword'] or None
        con = retval['conpassword'] or None
        if new is None or len(new) < 3:
            eve.Message('MinThreeLetters')
            return AskNewContainerPassword(invCacheSvc, id_, desc, which, new, old)
        if new != con:
            eve.Message('NewPasswordMismatch')
            return AskNewContainerPassword(invCacheSvc, id_, desc, which, new, old)
        container.SetPassword(which, old, new)


def ConfigureALSC(itemID, invCacheSvc):
    container = invCacheSvc.GetInventoryFromId(itemID)
    config = container.ALSCConfigGet()
    defaultLock = bool(config & const.ALSCLockAddedItems)
    containerOwnerID = container.GetItem().ownerID
    if idCheckers.IsCorporation(containerOwnerID):
        if charsession.corprole & const.corpRoleEquipmentConfig == 0:
            raise UserError('PermissionDeniedNeedEquipRole', {'corp': (const.UE_OWNERID, containerOwnerID)})
    else:
        userDefaultLock = settings.user.ui.Get('defaultContainerLock_%s' % itemID, None)
        if userDefaultLock:
            defaultLock = True if userDefaultLock == const.flagLocked else False
    configSettings = [(const.ALSCPasswordNeededToOpen, localization.GetByLabel('UI/Menusvc/ContainerPasswordForOpening')),
     (const.ALSCPasswordNeededToLock, localization.GetByLabel('UI/Menusvc/ContainerPasswordForLocking')),
     (const.ALSCPasswordNeededToUnlock, localization.GetByLabel('UI/Menusvc/ContainerPasswordForUnlocking')),
     (const.ALSCPasswordNeededToViewAuditLog, localization.GetByLabel('UI/Menusvc/ContainerPasswordForViewingLog'))]
    formFormat = []
    formFormat.append({'type': 'header',
     'text': localization.GetByLabel('UI/Menusvc/ContainerDefaultLocked')})
    formFormat.append({'type': 'checkbox',
     'setvalue': defaultLock,
     'key': const.ALSCLockAddedItems,
     'label': '',
     'text': localization.GetByLabel('UI/Menusvc/ALSCLocked')})
    formFormat.append({'type': 'btline'})
    formFormat.append({'type': 'push'})
    formFormat.append({'type': 'header',
     'text': localization.GetByLabel('UI/Menusvc/ContainerPasswordRequiredFor')})
    for value, settingName in configSettings:
        formFormat.append({'type': 'checkbox',
         'setvalue': value & config == value,
         'key': value,
         'label': '',
         'text': settingName})

    formFormat.append({'type': 'btline'})
    formFormat.append({'type': 'push'})
    retval = uix.HybridWnd(formFormat, caption=localization.GetByLabel('UI/Menusvc/ContainerConfigurationHeader'), windowID='configureContainer', modal=1, buttons=uiconst.OKCANCEL, unresizeAble=1, minW=300)
    if retval is None:
        return
    settings.user.ui.Delete('defaultContainerLock_%s' % itemID)
    newconfig = 0
    for k, v in retval.iteritems():
        newconfig |= k * v

    if config != newconfig:
        container.ALSCConfigSet(newconfig)


def RetrievePasswordALSC(itemID, invCacheSvc):
    container = invCacheSvc.GetInventoryFromId(itemID)
    formFormat = []
    formFormat.append({'type': 'header',
     'text': localization.GetByLabel('UI/Menusvc/RetrieveWhichPassword')})
    formFormat.append({'type': 'push'})
    formFormat.append({'type': 'btline'})
    configSettings = [[const.SCCPasswordTypeGeneral, localization.GetByLabel('UI/Menusvc/GeneralPassword')], [const.SCCPasswordTypeConfig, localization.GetByLabel('UI/Menusvc/RetrievePasswordConfiguration')]]
    for value, settingName in configSettings:
        formFormat.append({'type': 'checkbox',
         'setvalue': value & const.SCCPasswordTypeGeneral == value,
         'key': value,
         'label': '',
         'text': settingName,
         'group': 'which_password'})

    formFormat.append({'type': 'btline'})
    retval = uix.HybridWnd(formFormat, caption=localization.GetByLabel('UI/Commands/RetrievePassword'), windowID='retrieveContainerPassword', modal=1, buttons=uiconst.OKCANCEL)
    if retval is None:
        return
    container.RetrievePassword(retval['which_password'])


def SetName(invOrSlimItem, invCacheSvc):
    itemID = invOrSlimItem.itemID
    invCacheSvc.TryLockItem(itemID, 'lockItemRenaming', {'itemType': invOrSlimItem.typeID}, 1)
    try:
        cfg.evelocations.Prime([itemID])
        categoryID = evetypes.GetCategoryID(invOrSlimItem.typeID)
        if categoryID == const.categoryStructure:
            return _SetStructureName(itemID)
        try:
            setval = cfg.evelocations.Get(itemID).name
        except StandardError:
            setval = ''
            sys.exc_clear()

        maxLength = 100
        if categoryID == const.categoryStarbase:
            maxLength = 32
        if categoryID == const.categoryShip:
            nameRet = prompt_rename_ship(ship_type_id=invOrSlimItem.typeID, name=setval)
        else:
            nameRet = utilWindows.NamePopup(localization.GetByLabel('UI/Menusvc/SetName'), localization.GetByLabel('UI/Menusvc/TypeInNewName'), setvalue=setval, maxLength=maxLength)
        if nameRet:
            invCacheSvc.GetInventoryMgr().SetLabel(itemID, nameRet.replace('\n', ' '))
            sm.ScatterEvent('OnItemNameChange', itemID)
    finally:
        invCacheSvc.UnlockItem(itemID)


def _SetStructureName(structureID):
    structureInfo = sm.GetService('structureDirectory').GetStructureInfo(structureID)
    if structureInfo is None:
        log.LogError('Trying to set a name on a non-existent structure', structureID)
        return
    if not idCheckers.IsSolarSystem(structureInfo.solarSystemID) or not structureInfo.inSpace:
        log.LogError("Can't rename a structure that's not in space.  What is", structureID, 'doing inside', structureInfo.solarSystemID, 'anyways?')
        return
    extraConfig = KeyVal()
    if evetypes.IsUpwellStargate(structureInfo.typeID):
        destinationSolarsystemID = sm.GetService('structureDirectory').GetJbStructureDestination(structureID)
        if not destinationSolarsystemID:
            raise UserError('JumpGateHasNoDestination')
        extraConfig.destinationSolarsystemID = destinationSolarsystemID
    namePrefix = GetStructureNamePrefix(structureInfo.typeID, structureInfo.solarSystemID, extraConfig)
    currentName = cfg.evelocations.Get(structureID).locationName
    if not currentName.startswith(namePrefix):
        currentName = namePrefix + currentName

    def _CheckLen(name, *args):
        if len(name) - len(namePrefix) < structures.MIN_STRUCTURE_NAME_LEN:
            raise UserError('CharNameTooShort')

    newName = utilWindows.NamePopup(localization.GetByLabel('UI/Menusvc/SetName'), localization.GetByLabel('UI/Menusvc/TypeInNewName'), setvalue=currentName, maxLength=32 + len(namePrefix), fixedPrefix=namePrefix, validator=_CheckLen)
    if newName:
        sm.RemoteSvc('structureDeployment').RenameStructure(structureID, newName)
        sm.GetService('structureDirectory').OnCorporationStructuresUpdated()


def RedeemCurrency(item, qty):
    sm.GetService('invCache').GetInventoryMgr().DepositPlexToVault(session.stationid or session.structureid, item.itemID, qty)


def ActivateCharacterReSculpt(itemID):
    dialogParams = {'charName': cfg.eveowners.Get(session.charid).name}
    if eve.Message('ActivateCharacterReSculpt', dialogParams, uiconst.YESNO) == uiconst.ID_YES:
        sm.RemoteSvc('userSvc').ActivateCharacterReSculpt(itemID)


def _activate_ship_skin_license(itemID, typeID):
    license = sm.GetService('cosmeticsSvc').GetStaticLicenseByID(typeID)
    duration = None
    if license.is_single_use:
        key = 'ActivateSkinLicenseSingleUse'
    elif license.is_permanent:
        key = 'ActivateSkinLicensePermanent'
    else:
        key = 'ActivateSkinLicenseLimited'
        duration = license.duration
    parameters = _GetParametersForMsg(license, session.charid, duration)
    if eve.Message(key, parameters, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
        sm.GetService('cosmeticsSvc').ActivateShipSkinLicense([itemID])
        return True
    else:
        return False


def ActivateShipSkinLicense(itemAndTypeIDs):
    if len(itemAndTypeIDs) > 1:
        key = 'ActivateMultipleShipSkinLicense'
        parameters = {'ownerID': session.charid,
         'numSkins': len(itemAndTypeIDs)}
        if eve.Message(key, parameters, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        itemIDs = [ x[0] for x in itemAndTypeIDs ]
        sm.GetService('cosmeticsSvc').ActivateShipSkinLicense(itemIDs)
        return
    itemID, typeID = itemAndTypeIDs[0]
    _activate_ship_skin_license(itemID, typeID)


def ActivateShipSkinLicenseAndApply(itemID, typeID):
    if not _activate_ship_skin_license(itemID, typeID):
        return
    if not session.shipid:
        return
    licenceType = sm.GetService('cosmeticsSvc').GetSkinByLicenseType(typeID)
    if not licenceType:
        logger.error('licenceType not found for typeID=%r', typeID)
        return
    shipItem = sm.GetService('invCache').GetInventoryFromId(session.shipid).GetItem()
    if not shipItem:
        logger.error('shipItem not found for session.shipid=%r', session.shipid)
        return
    get_ship_skin_application_svc().apply_first_party_skin(shipItem.itemID, shipItem.typeID, licenceType)


def ConsumeSkinDesignComponent(items):
    if len(items) == 0:
        return
    quantity = 0
    for item in items:
        _, _, stacksize = item
        quantity += stacksize

    if quantity > 1:
        key = 'ConsumeMultipleSkinDesignComponents'
        parameters = {'ownerID': session.charid,
         'quantity': quantity}
        if eve.Message(key, parameters, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
    else:
        key = 'ConsumeSkinDesignComponent'
        _, typeID, _ = items[0]
        parameters = {'ownerID': session.charid,
         'typeID': typeID}
        if eve.Message(key, parameters, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
    from cosmetics.client.shipSkinComponentSvc import get_ship_skin_component_svc
    error_msg = get_ship_skin_component_svc().consume_component_items(items)
    if error_msg:
        ShowQuickMessage(error_msg)
    else:
        sm.GetService('neocom').Blink(btnIDs.SHIP_SKINR, localization.GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/NewDesignElementAddedToCollection'))


def DecryptItem(itemID, typeID):
    url = sm.RemoteSvc('encodedItems').DecodeItem(itemID)
    if url is not None:
        EncodedItemsWindow.Open(windowInstanceID=typeID, url=url, caption=evetypes.GetName(typeID), typeID=typeID)


def _GetParametersForMsg(license, ownerID, duration):
    parameters = {'type': license.typeID,
     'ownerID': ownerID,
     'materialName': license.material.name,
     'hullNames': ', '.join((evetypes.GetName(ship) for ship in license.skin.types)),
     'days': duration}
    return parameters


def ActivateSkillExtractor(item):
    sm.GetService('skills').ActivateSkillExtractor(item)


def ActivateSkillInjector(item, quantity):
    SkillInjectorWindow.OpenOrReload(injectorItem=item, quantity=quantity)


def SplitSkillInjector(itemID, quantity):
    sm.GetService('skills').SplitSkillInjector(itemID, quantity)


def CombineSkillInjector(itemID, quantity):
    sm.GetService('skills').CombineSkillInjector(itemID, quantity)


def OpenCrate(typeID, itemID, stacksize):
    if is_fixed_crate(typeID):
        FixedCrateWindow.Open(crate_stack_list=[(typeID, itemID, stacksize)])
    else:
        CrateWindow.Open(typeID=typeID, itemID=itemID, stacksize=stacksize)


def CraftDynamicItem(item):
    sm.GetService('dynamicItemSvc').OpenCraftWindow(item)


def ActivateAbyssalKey(item):
    sm.GetService('abyss').open_key_activation_window(item)


def ActivateWarpVector(item):
    sm.RemoteSvc('warpVectorMgr').UseVector(item.itemID)


def ActivateVoidSpaceKey(item):
    sm.GetService('voidSpaceSvc').open_void_space_activation_window(item)


def ActivateRandomJumpKey(item):
    sm.GetService('randomJumpSvc').open_random_jump_key_activation_window(item)


def ActivatePVPfilamentKey(item):
    sm.GetService('pvpFilamentSvc').OpenPVPfilamentWindow(item)


def AbortSelfDestructShip(pickid):
    if eve.Message('ConfirmAbortSelfDestruct', {}, uiconst.YESNO) == uiconst.ID_YES:
        ship = sm.StartService('gameui').GetShipAccess()
        if ship and not session.stationid:
            log.LogNotice('Aborting self Destruct for', session.shipid)
            sm.StartService('sessionMgr').PerformSessionChange('abortselfdestruct', ship.AbortSelfDestruct, pickid)


def SelfDestructShip(pickid):
    slimItem = uix.GetBallparkRecord(pickid)
    groupID = None
    if slimItem:
        groupID = slimItem.groupID
    msg = 'ConfirmSelfDestruct'
    msgArgs = {}
    if groupID == const.groupCapsule:
        msg = 'ConfirmSelfDestructCapsule'
        implantCost = uix.GetImplantsCostForCharacter()
        if implantCost:
            implantsText = localization.GetByLabel('UI/Inflight/ImplantsLostOnSelfDestruct', iskValue=implantCost)
        else:
            implantsText = ''
        msgArgs = {'implantsText': implantsText}
    if eve.Message(msg, msgArgs, uiconst.YESNO) == uiconst.ID_YES:
        ship = sm.StartService('gameui').GetShipAccess()
        if ship and not session.stationid:
            log.LogNotice('Self Destruct for', session.shipid)
            sm.StartService('sessionMgr').PerformSessionChange('selfdestruct', ship.SelfDestruct, pickid)


def DeclareWar():
    from eve.client.script.ui.shared.neocom.corporation.war.warDeclare import WarDeclareWnd
    wnd = WarDeclareWnd.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.Maximize()
    else:
        WarDeclareWnd()


def DeclareWarAgainst(againstID):
    from eve.client.script.ui.shared.neocom.corporation.war.warDeclare import WarDeclareWnd
    wnd = WarDeclareWnd.GetIfOpen()
    if wnd and not wnd.destroyed and wnd.warDeclareController.GetDefenderID() == againstID:
        wnd.Maximize()
    else:
        WarDeclareWnd(defenderOwnerID=againstID)


def TransferOwnership(itemID):
    members = sm.GetService('alliance').GetMembers()
    twit = sm.GetService('michelle')
    remotePark = twit.GetRemotePark()
    localPark = twit.GetBallpark()
    if itemID not in localPark.slimItems:
        return
    oldOwnerID = localPark.slimItems[itemID].ownerID
    owners = {member.corporationID for member in members.itervalues()}
    if len(owners):
        cfg.eveowners.Prime(owners)
    tmplist = []
    for member in members.itervalues():
        if oldOwnerID != member.corporationID:
            tmplist.append((cfg.eveowners.Get(member.corporationID).ownerName, member.corporationID))

    ret = uix.ListWnd(tmplist, 'generic', localization.GetByLabel('UI/Corporations/Common/SelectCorporation'), None, 1)
    if ret is not None and len(ret):
        newOwnerID = ret[1]
        if remotePark is not None:
            remotePark.CmdTransferCorpAssetOwnership(itemID, oldOwnerID, newOwnerID)


def AbortSelfDestructStructure(itemID):
    if eve.Message('ConfirmAbortSelfDestruct', {}, uiconst.YESNO) == uiconst.ID_YES:
        michelle = sm.GetService('michelle')
        localPark = michelle.GetBallpark()
        if itemID not in localPark.slimItems:
            return
        remotePark = michelle.GetRemotePark()
        if remotePark is not None:
            remotePark.CmdAbortSelfDestructStructure(itemID)


def SelfDestructStructure(itemID):
    timeDelayInMinutes = prefs.GetValue('secondsUntilStructureSelfDestruct', 1200) / 60
    corpName = cfg.eveowners.Get(session.corpid).ownerName
    if eve.Message('ConfirmSelfDestructStructure', {'durationInMin': timeDelayInMinutes,
     'corpName': corpName}, uiconst.YESNO) == uiconst.ID_YES:
        michelle = sm.GetService('michelle')
        localPark = michelle.GetBallpark()
        if itemID not in localPark.slimItems:
            return
        remotePark = michelle.GetRemotePark()
        if remotePark is not None:
            remotePark.CmdSelfDestructStructure(itemID)


def TransferCorporationOwnership(itemID):
    michelle = sm.GetService('michelle')
    remotePark = michelle.GetRemotePark()
    localPark = michelle.GetBallpark()
    if itemID not in localPark.slimItems or remotePark is None:
        return
    oldOwnerID = localPark.slimItems[itemID].ownerID
    name = utilWindows.NamePopup(localization.GetByLabel('UI/Corporations/Common/TransferOwnership'), localization.GetByLabel('UI/Corporations/Common/TransferOwnershipLabel'))
    if name is None:
        return
    owner = searchOld.SearchOwners(searchStr=name, groupIDs=[const.groupCorporation], hideNPC=True, notifyOneMatch=True, searchWndName='AddToBlockSearch')
    if owner is None or owner == oldOwnerID:
        return
    remotePark.CmdTransferCorpAssetOwnership(itemID, oldOwnerID, owner)
