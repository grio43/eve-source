#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structuremenu.py
import structures
from carbonui.control.contextMenu.menuConst import DISABLED_ENTRY0
from eve.client.script.ui.services.menuSvcExtras import menuFunctions, openFunctions
from localization import GetByLabel
from menu import MenuList, MenuLabel
from eve.common.lib import appConst as const
from moonmining.autoMoonMining.client.auto_moon_miner_window import open_auto_moon_miner

def GetStructureMenu(checker):
    entries = MenuList()
    if not checker.IsStructure():
        return entries
    if checker.OfferBoardStructure():
        entries.append([MenuLabel('UI/Inflight/BoardStructure'), sm.GetService('structureControl').BoardStructure, [checker.item.itemID]])
    elif checker.failure_label:
        entries.reasonsWhyNotAvailable['UI/Inflight/BoardStructure'] = GetByLabel(checker.failure_label)
    if checker.OfferTransferStructureOwnership():
        entries.append([MenuLabel('UI/Inflight/POS/TransferSovStructureOwnership'), menuFunctions.TransferCorporationOwnership, [checker.item.itemID]])
    if checker.OfferReleaseControl():
        label = MenuLabel('UI/Inflight/HUDOptions/ReleaseControl') if checker.IsDockableStructure() else MenuLabel('UI/Inflight/EjectFromShip')
        entries.append([label, sm.GetService('structureControl').ReleaseControl])
    if checker.OfferBoardPreviousShip():
        label = MenuLabel('UI/Inflight/HUDOptions/BoardPreviousShipFromFlex')
        entries.append([label, sm.GetService('structureControl').BoardPreviousShip])
    if checker.OfferUndock():
        entries.append([MenuLabel('UI/Neocom/UndockBtn'), sm.GetService('structureDocking').Undock, [checker.item.itemID]])
    if checker.OfferTakeControl():
        entries.append([MenuLabel('UI/Commands/TakeStructureControl'), sm.GetService('structureControl').TakeControl, [checker.item.itemID]])
    if checker.OfferAccessHangarTransfer():
        if not checker.isMultiSelection:
            entries.append([MenuLabel('UI/Inflight/AccessHangarTransfer'), openFunctions.OpenDropbox, (checker.item.itemID, checker.item.typeID)])
    elif checker.failure_label:
        entries.reasonsWhyNotAvailable['UI/Inflight/AccessHangarTransfer'] = GetByLabel(checker.failure_label)
    if not checker.isMultiSelection and checker.OfferAccessAutoMoonMinerDetails():
        entries.append([MenuLabel('UI/Moonmining/AutoMoonMiner/OfferDetailsWindow'), open_auto_moon_miner, (checker.item.itemID, checker.item.typeID)])
    if checker.OfferActivateJumpBridge():
        entries.append([MenuLabel('UI/Inflight/JumpUsingBridge'), sm.GetService('menu').JumpThroughStructureJumpBridge, (checker.item.itemID,)])
    else:
        if checker.failure_label:
            entries.reasonsWhyNotAvailable['UI/Inflight/JumpUsingBridge'] = GetByLabel(checker.failure_label)
        if checker.OfferActivateJumpBridgeDisabled():
            entries.append([MenuLabel('UI/Inflight/JumpUsingBridge'), DISABLED_ENTRY0])
    if checker.session.HasGMHRole() and checker.IsStructureInSpace():
        states = [ [name, GMSetStructureState, [checker.item.itemID, value]] for value, name in structures.STATES.iteritems() ]
        entries.append(['GM: Set State', states])
        times = [ ['{} seconds'.format(time), GMSetStructureTimer, [checker.item.itemID, time]] for time in [5,
         15,
         60,
         600,
         6000] ]
        entries.append(['GM: Set Timer', times])
        if checker.IsStructureInState(structures.STATE_DEPLOY_VULNERABLE):
            deployTimes = [ ['{} seconds'.format(time), GMSetDeployTimer, [checker.item.itemID, time]] for time in [5,
             15,
             60,
             600,
             6000] ]
            entries.append(['GM: Set Deploy Timer', deployTimes])
        unanchoring = [['Start Unanchoring', GMSetStructureUnanchoring, [checker.item.itemID]], ['Cancel Unanchoring', GMSetStructureUnanchoring, [checker.item.itemID, 'cancel']]]
        unanchoring += [ ['{} seconds'.format(time), GMSetStructureUnanchoring, [checker.item.itemID, time]] for time in [5,
         15,
         60,
         600,
         6000] ]
        entries.append(['GM: Set Unanchoring', unanchoring])
        if checker.CanEditAbandonTimer():
            abandonTimes = [ ['{} seconds'.format(time), GMSetStructureAbandonTimer, [checker.item.itemID, time]] for time in [5,
             60,
             600,
             3600,
             68400,
             604800] ]
            entries.append(['GM: Set Abandon Timer', abandonTimes])
    return entries


def CheckStructureIsNotOffline(slimItem):
    if slimItem.categoryID == const.categoryStructure:
        return getattr(slimItem, 'state', structures.STATE_UNKNOWN) not in structures.OFFLINE_STATES
    return False


def GMSetStructureState(structureID, state):
    sm.RemoteSvc('slash').SlashCmd('/structure state %d %d' % (structureID, state))


def GMSetStructureTimer(structureID, seconds):
    sm.RemoteSvc('slash').SlashCmd('/structure timer %d %d' % (structureID, seconds))


def GMSetStructureUnanchoring(structureID, action = ''):
    sm.RemoteSvc('slash').SlashCmd('/structure unanchor %d %s' % (structureID, action))


def GMSetDeployTimer(structureID, seconds):
    sm.RemoteSvc('slash').SlashCmd('/structure deploytimer %d %d' % (structureID, seconds))


def GMSetStructureAbandonTimer(structureID, seconds):
    sm.RemoteSvc('slash').SlashCmd('/structure abandontimer %d %d' % (structureID, seconds))
