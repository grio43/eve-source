#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\undockQuestions.py
from ballparkCommon.docking import CanDock
import structures
from carbonui import const as uiconst
from eve.client.script.ui.station.askForUndock import IsOkToBoardWithModulesLackingSkills
from eve.common.script.sys.idCheckers import IsStation
from eve.common.lib import appConst
from eve.common.script.util.facwarCommon import IsOccupierEnemyFaction
from factionwarfare.dockableChecks import IsDockableStructureUsageRestrictedByOccupationState, IsShipExemptFromDockingRestrictions
from operations.client.operationscontroller import GetOperationsController
from operations.client.util import are_operations_active
from carbonui.uicore import uicore
from evestations.standingsrestriction import get_station_standings_restriction

def IsOkToUndock():
    if not IsOkToUndockInUnfriendlySpace():
        return False
    if not IsOkToUndockInHighSecWhileAtWar():
        return False
    if not IsOkToBoardWithModulesLackingSkills(sm.GetService('clientDogmaIM').GetDogmaLocation(), uicore.Message):
        return False
    if not IsOkToUndockWithCrimewatchTimers():
        return False
    if not IsOkToUndockInInceptionNPE():
        return False
    if not IsOkToUndockFromStructureInShipThatCannotRedock():
        return False
    if not IsOkToUndockInHighSecIfMilitiaMember():
        return False
    if not IsOkToUndockStandingsRestriction():
        return False
    return True


def IsOkToUndockFromStructureInShipThatCannotRedock():
    if session.structureid:
        invCache = sm.GetService('invCache')
        shipTypeID = invCache.GetInventoryFromId(session.shipid).typeID
        stationTypeID = invCache.GetInventoryFromId(session.structureid).typeID
        if not CanDock(stationTypeID, shipTypeID):
            msgResult = eve.Message('AskUndockWithShipThatCannotDock', {'item': shipTypeID}, uiconst.YESNO)
            return msgResult == uiconst.ID_YES
    return True


def IsOkToUndockInUnfriendlySpace():
    if settings.user.suppress.Get('suppress.AskUndockInEnemySystem', None):
        return True
    if session.structureid:
        if sm.RemoteSvc('structureSettings').CharacterHasSetting(session.structureid, structures.SETTING_HOUSING_CAN_DOCK):
            return True
        from eve.client.script.ui.shared.dockedUI.controllers.structureController import StructureController
        structureController = StructureController(itemID=session.structureid)
        ownerName = cfg.eveowners.Get(structureController.GetOwnerID()).ownerName
        if not _ConfirmDoUndockInEnemySystem(ownerName):
            return False
    elif session.warfactionid:
        fwOccupationState = sm.GetService('fwWarzoneSvc').GetLocalOccupationState()
        if fwOccupationState and not fwOccupationState.isFrontline:
            if IsOccupierEnemyFaction(session.warfactionid, fwOccupationState.occupierID):
                occupierName = cfg.eveowners.Get(fwOccupationState.occupierID).ownerName
                if not _ConfirmDoUndockInEnemySystem(occupierName):
                    return False
    return True


def _ConfirmDoUndockInEnemySystem(ownerName):
    if uicore.Message('AskUndockInEnemySystem', {'sovHolderName': ownerName}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
        return False
    return True


def IsOkToUndockInHighSecWhileAtWar():
    if not sm.GetService('securitySvc').is_effective_high_sec_system(session.solarsystemid2):
        return True
    if not sm.GetService('war').IsPlayerCurrentlyAtWarOrInFW():
        return True
    if uicore.Message('AskUndockInHighSecWhileAtWar', {}, uiconst.YESNO) != uiconst.ID_YES:
        return False
    return True


def IsOkToUndockWithCrimewatchTimers():
    systemSecStatus = sm.GetService('securitySvc').get_modified_security_class(eve.session.solarsystemid2)
    crimewatchSvc = sm.GetService('crimewatchSvc')
    if crimewatchSvc.IsCriminal(session.charid):
        if systemSecStatus == const.securityClassHighSec:
            if eve.Message('UndockCriminalConfirm', {}, uiconst.YESNO) == uiconst.ID_YES:
                return True
            else:
                return False
    if systemSecStatus > const.securityClassZeroSec:
        engagements = crimewatchSvc.GetMyEngagements()
        if len(engagements):
            if eve.Message('UndockAggressionConfirm', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return False
    return True


def IsOkToUndockWithMissingCargo():
    if settings.user.suppress.Get('suppress.CourierUndockMissingCargo', None):
        return True
    if sm.GetService('journal').CheckUndock(session.stationid):
        return True
    return False


def IsOkToUndockInInceptionNPE():
    if not are_operations_active():
        return True
    return GetOperationsController().can_undock()


def IsOkToUndockInHighSecIfMilitiaMember():
    if not session.warfactionid:
        return True
    systemCheckSupressed = settings.user.suppress.Get('suppress.FacWarWarningUndock', None) == uiconst.ID_OK
    if systemCheckSupressed:
        return True
    dockableItem = None
    if sm.GetService('station').stationItem:
        dockableItem = sm.GetService('station').stationItem
    elif session.structureid:
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(session.structureid)
        if structureInfo:
            dockableItem = structureInfo
    if not dockableItem:
        return True
    isSafe = sm.GetService('facwar').CheckForSafeSystem(dockableItem, eve.session.warfactionid)
    if isSafe:
        return True
    if not eve.Message('FacWarWarningUndock', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
        settings.user.suppress.Set('suppress.FacWarWarningUndock', None)
        return False
    return True


def IsOkToUndockStandingsRestriction():
    if not IsStation(session.locationid):
        return True
    standingsRestriction = get_station_standings_restriction(appConst.stationServiceDocking, session.locationid, session.charid)
    if not standingsRestriction:
        return True
    userInput = eve.Message('AskUndockStandingsRestriction', params=standingsRestriction, buttons=uiconst.YESNO)
    return userInput == uiconst.ID_YES


def CheckOkToUndockWhileAttackerInFW():
    if not session.warfactionid:
        return
    if not sm.GetService('fwWarzoneSvc').IsWarzoneSolarSystem(session.solarsystemid2):
        return
    invCache = sm.GetService('invCache')
    shipTypeID = invCache.GetInventoryFromId(session.shipid).typeID
    if IsShipExemptFromDockingRestrictions(shipTypeID):
        return
    occupationState = sm.GetService('fwWarzoneSvc').GetLocalOccupationState()
    restricted = IsDockableStructureUsageRestrictedByOccupationState(occupationState, session.warfactionid)
    if restricted:
        raise UserError('CantUndockWhenAttackerInFw')
