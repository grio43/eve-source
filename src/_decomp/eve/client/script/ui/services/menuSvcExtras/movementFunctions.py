#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menuSvcExtras\movementFunctions.py
from ballparkCommon.parkhelpers.warpSubjects import WarpSubjects
from eve.client.script.ui.control.message import ShowQuickMessage
from randomJump import get_error_label
from spacecomponents.common.componentConst import SHIPCASTER_LAUNCHER, FILAMENT_SPOOLUP
from spacecomponents.common.helper import HasShipcasterComponent
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.format import FmtAmt, FmtDist
from carbonui.uicore import uicore
import destiny
from eve.client.script.parklife import states
import eve.client.script.ui.util.defaultRangeUtils as defaultRangeUtils
from eve.common.lib import appConst as const
from eve.common.script.sys.eveCfg import CheckShipHasFighterBay, IsControllingStructure
from evefleet import FORMATION_SKILL, FORMATION_DISTANCE_SKILL
from evefleet.client.util import GetFormationSelected, GetFormationSpacingSelected, GetFormationSizeSelected
from eveexceptions import UserError, ExceptionEater
from eveservices.menu import GetMenuService
from evetypes import IsUpwellStargate
from evedungeons.client.ship_restrictions_window import ShipRestrictionsWindow
import carbonui.const as uiconst
import localization
import log
from eve.client.script.ui.util import uix
from menu import MenuLabel
ORBIT_RANGES = (500, 1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000, 30000)
KEEP_AT_RANGE_RANGES = (500, 1000, 2500, 5000, 7500, 10000, 15000, 20000, 25000, 30000)

def SetDefaultDist(key):
    if not key:
        return
    minDist, maxDist = {'Orbit': (500, 1000000),
     'KeepAtRange': (50, 1000000),
     'WarpTo': (const.minWarpEndDistance, const.maxWarpEndDistance)}.get(key, (500, 1000000))
    current = GetMenuService().GetDefaultActionDistance(key)
    current = current or ''
    fromDist = FmtAmt(minDist)
    toDist = FmtAmt(maxDist)
    if key == 'KeepAtRange':
        hint = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistanceHint', fromDist=fromDist, toDist=toDist)
        caption = localization.GetByLabel('UI/Inflight/Submenus/KeepAtRange')
    elif key == 'Orbit':
        hint = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistanceHint', fromDist=fromDist, toDist=toDist)
        caption = localization.GetByLabel('UI/Inflight/OrbitObject')
    elif key == 'WarpTo':
        hint = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistanceHint', fromDist=fromDist, toDist=toDist)
        caption = localization.GetByLabel('UI/Inflight/Submenus/WarpToWithin')
    else:
        hint = ''
        caption = ''
    r = uix.QtyPopup(maxvalue=maxDist, minvalue=minDist, setvalue=current, hint=hint, caption=caption, label=None, digits=0)
    if r:
        newRange = max(minDist, min(maxDist, r['qty']))
        defaultRangeUtils.UpdateRangeSetting(key, newRange)


def GetKeepAtRangeMenu(itemID, typeID, dist, currentDistance):
    keepRangeMenu = _GetRangeMenu(itemID=itemID, typeID=typeID, dist=dist, currentDistance=currentDistance, rangesList=KEEP_AT_RANGE_RANGES, mainFunc=KeepAtRange, setDefaultFunc=defaultRangeUtils.SetDefaultKeepAtRangeDist, atCurrentRangeLabel='UI/Inflight/KeepAtCurrentRange', setDefaultLabel='UI/Inflight/Submenus/SetDefaultWarpRange', referenceString='KeepAtRange')
    return keepRangeMenu


def GetOrbitMenu(itemID, typeID, dist, currentDistance):
    orbitMenu = _GetRangeMenu(itemID=itemID, typeID=typeID, dist=dist, currentDistance=currentDistance, rangesList=ORBIT_RANGES, mainFunc=Orbit, setDefaultFunc=defaultRangeUtils.SetDefaultOrbitDist, atCurrentRangeLabel='UI/Inflight/OrbitAtCurrentRange', setDefaultLabel='UI/Inflight/Submenus/SetDefaultWarpRange', referenceString='Orbit')
    return orbitMenu


def _GetRangeMenu(itemID, typeID, dist, currentDistance, rangesList, mainFunc, setDefaultFunc, atCurrentRangeLabel, setDefaultLabel, referenceString):
    rangeMenu = []
    rangeSubMenu = []
    for eachRange in rangesList:
        fmtRange = FmtDist(eachRange)
        fmtRangeNoWhiteSpace = ''.join(fmtRange.split())
        optionReferenceString = referenceString + fmtRangeNoWhiteSpace
        rangeMenu.append((fmtRange,
         mainFunc,
         (itemID, eachRange),
         None,
         None,
         optionReferenceString,
         typeID))
        rangeSubMenu.append((fmtRange, setDefaultFunc, (eachRange,)))

    rangeMenu += [(MenuLabel(atCurrentRangeLabel, {'currentDistance': currentDistance}), mainFunc, (itemID, dist)), None, (MenuLabel(setDefaultLabel), rangeSubMenu)]
    return rangeMenu


def GetDefaultDist(key, itemID = None, minDist = 500, maxDist = 1000000):
    drange = GetMenuService().GetDefaultActionDistance(key)
    if drange is None:
        dist = ''
        if itemID:
            bp = sm.StartService('michelle').GetBallpark()
            if not bp:
                return
            ball = bp.GetBall(itemID)
            if not ball:
                return
            dist = long(max(minDist, min(maxDist, ball.surfaceDist)))
        fromDist = FmtAmt(minDist)
        toDist = FmtAmt(maxDist)
        if key == 'KeepAtRange':
            hint = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistanceHint', fromDist=fromDist, toDist=toDist)
            caption = localization.GetByLabel('UI/Inflight/SetDefaultKeepAtRangeDistance')
        elif key == 'Orbit':
            hint = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistanceHint', fromDist=fromDist, toDist=toDist)
            caption = localization.GetByLabel('UI/Inflight/SetDefaultOrbitDistance')
        elif key == 'WarpTo':
            hint = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistanceHint', fromDist=fromDist, toDist=toDist)
            caption = localization.GetByLabel('UI/Inflight/SetDefaultWarpWithinDistance')
        else:
            hint = ''
            caption = ''
        r = uix.QtyPopup(maxvalue=maxDist, minvalue=minDist, setvalue=dist, hint=hint, caption=caption, label=None, digits=0)
        if r:
            newRange = max(minDist, min(maxDist, r['qty']))
            defaultRangeUtils.UpdateRangeSetting(key, newRange)
        else:
            return
    return drange


def GetSelectedShipAndFighters():
    selectedFighterIDs = GetFightersSelectedForNavigation()
    shipIsSelected = len(selectedFighterIDs) == 0 or IsSelectedForNavigation(session.shipid)
    return (shipIsSelected, selectedFighterIDs)


def GetFightersSelectedForNavigation():
    if not CheckShipHasFighterBay(session.shipid):
        return []
    selectedItemIDs = sm.GetService('stateSvc').GetStatesForFlag(states.selectedForNavigation)
    fighterIDsInSpace = sm.GetService('fighters').shipFighterState.GetAllFighterIDsInSpace()
    return [ fighterItemID for fighterItemID in fighterIDsInSpace if fighterItemID in selectedItemIDs ]


def IsSelectedForNavigation(itemID):
    return sm.GetService('stateSvc').GetState(itemID, states.selectedForNavigation)


def SelectForNavigation(itemID):
    if not CheckShipHasFighterBay(session.shipid):
        return
    sm.GetService('stateSvc').SetState(itemID, states.selectedForNavigation, True)


def DeselectForNavigation(itemID):
    sm.GetService('stateSvc').SetState(itemID, states.selectedForNavigation, False)


def ToggleSelectForNavigation(itemID):
    if IsSelectedForNavigation(itemID):
        DeselectForNavigation(itemID)
    else:
        SelectForNavigation(itemID)


def DeselectAllForNavigation():
    sm.GetService('stateSvc').ResetByFlag(states.selectedForNavigation)


def GetSelectedFightersByTubeIDs():
    selectedItemIDs = sm.GetService('stateSvc').GetStatesForFlag(states.selectedForNavigation)
    if not selectedItemIDs:
        return {}
    shipFighterState = sm.GetService('fighters').shipFighterState
    fighterIDsByTubeID = {}
    allFighters = shipFighterState.GetAllFighters()
    for eachFighter in allFighters:
        if eachFighter and eachFighter.itemID in selectedItemIDs:
            fighterIDsByTubeID[eachFighter.tubeFlagID] = eachFighter.itemID

    return fighterIDsByTubeID


def IsApproachingBall(targetBallID):
    ball = sm.GetService('michelle').GetBall(session.shipid)
    if ball is None:
        return False
    return ball.mode == destiny.DSTBALL_FOLLOW and ball.followId == targetBallID


def _IsAlreadyFollowingBallAtRange(ballID, targetID, targetRange, moveMode = destiny.DSTBALL_FOLLOW):
    ball = sm.GetService('michelle').GetBall(ballID)
    if ball is None:
        return
    return ball.mode == moveMode and ball.followId == targetID and ball.followRange == targetRange


def _GetMovementDistanceOrDefault(targetID, targetRange, action, **kwargs):
    if targetRange is None:
        return GetDefaultDist(action, targetID, **kwargs)
    return targetRange


def KeepAtRange(targetID, followRange = None):
    if _IsInvalidMovementTarget(targetID):
        return
    followRange = _GetMovementDistanceOrDefault(targetID, followRange, 'KeepAtRange', minDist=const.approachRange)
    if followRange is None:
        return
    shipIsSelected, selectedFighterIDs = GetSelectedShipAndFighters()
    if shipIsSelected:
        _Ship_KeepAtRange(targetID, followRange)
    if selectedFighterIDs:
        sm.GetService('fighters').CmdMovementFollow(selectedFighterIDs, targetID, followRange)


def _Ship_KeepAtRange(targetID, followRange):
    if IsControllingStructure():
        return
    if _IsAlreadyFollowingBallAtRange(session.shipid, targetID, followRange):
        return
    sm.GetService('space').SetIndicationTextForcefully(ballMode=destiny.DSTBALL_FOLLOW, followId=targetID, followRange=int(followRange))
    bp = sm.GetService('michelle').GetRemotePark()
    bp.CmdFollowBall(targetID, followRange)
    sm.GetService('autoPilot').CancelSystemNavigation()
    sm.GetService('flightPredictionSvc').OptionActivated('KeepAtRange', targetID, followRange)
    sm.GetService('tacticalNavigation').NotifyOfKeepAtRangeCommand(targetID, followRange)


def Orbit(targetID, followRange = None):
    if _IsInvalidMovementTarget(targetID):
        return
    followRange = _GetMovementDistanceOrDefault(targetID, followRange, 'Orbit')
    if followRange is None:
        return
    followRange = float(followRange) if followRange < 10.0 else int(followRange)
    shipIsSelected, selectedFighterIDs = GetSelectedShipAndFighters()
    if shipIsSelected:
        _Ship_Orbit(targetID, followRange)
    if selectedFighterIDs:
        sm.GetService('fighters').CmdMovementOrbit(selectedFighterIDs, targetID, followRange)


def _Ship_Orbit(targetID, followRange):
    if IsControllingStructure():
        return
    _ScatterOrbitAchievementEvent(targetID, followRange)
    if _IsAlreadyFollowingBallAtRange(session.shipid, targetID, followRange, moveMode=destiny.DSTBALL_ORBIT):
        return
    sm.GetService('space').SetIndicationTextForcefully(ballMode=destiny.DSTBALL_ORBIT, followId=targetID, followRange=followRange)
    bp = sm.GetService('michelle').GetRemotePark()
    bp.CmdOrbit(targetID, followRange)
    sm.GetService('autoPilot').CancelSystemNavigation()
    sm.GetService('flightPredictionSvc').OptionActivated('Orbit', targetID, followRange)


def _ScatterOrbitAchievementEvent(targetID, distance):
    try:
        slimItem = sm.GetService('michelle').GetItem(targetID)
        if slimItem:
            sm.GetService('tacticalNavigation').NotifyOfOrbitCommand(targetID, distance, slimItem)
        else:
            log.LogTraceback('Failed at scattering orbit event')
    except Exception as e:
        log.LogTraceback('Failed at scattering orbit event')


def Approach(targetID, cancelAutoNavigation = True):
    if _IsInvalidMovementTarget(targetID):
        return
    shipIsSelected, selectedFighterIDs = GetSelectedShipAndFighters()
    if shipIsSelected:
        ShipApproach(targetID, cancelAutoNavigation)
    if selectedFighterIDs:
        sm.GetService('fighters').CmdMovementFollow(selectedFighterIDs, targetID, const.approachRange)


def ShipApproach(targetID, cancelAutoNavigation = True):
    if IsControllingStructure():
        return
    autoPilot = sm.GetService('autoPilot')
    if cancelAutoNavigation:
        autoPilot.CancelSystemNavigation()
    approachRange = const.approachRange
    if _IsAlreadyFollowingBallAtRange(session.shipid, targetID, approachRange):
        return
    sm.GetService('space').SetIndicationTextForcefully(ballMode=destiny.DSTBALL_FOLLOW, followId=targetID, followRange=approachRange)
    bp = sm.GetService('michelle').GetRemotePark()
    sm.GetService('menu').StoreAlignTarget(alignTargetID=targetID, aligningToBookmark=False)
    bp.CmdFollowBall(targetID, approachRange)
    sm.GetService('flightPredictionSvc').OptionActivated('Approach', targetID, approachRange)
    slimItem = sm.GetService('michelle').GetItem(targetID)
    sm.GetService('tacticalNavigation').NotifyOfApproachCommand(slimItem)


def GoToPoint(position):
    bp = sm.GetService('michelle').GetRemotePark()
    if bp is not None:
        shipIsSelected, selectedFighterIDs = GetSelectedShipAndFighters()
        if selectedFighterIDs:
            _Fighters_GoToPoint(selectedFighterIDs, position)
        if shipIsSelected:
            _Ship_GoToPoint(bp, position)


def _Ship_GoToPoint(bp, position):
    if IsControllingStructure():
        return
    sm.GetService('autoPilot').CancelSystemNavigation()
    bp.CmdGotoPoint(*position)


def _Fighters_GoToPoint(fighterIDs, position):
    fighterSvc = sm.GetService('fighters')
    fighterSvc.CmdGotoPoint(fighterIDs, position)


def GetWarpToRanges():
    ranges = [const.minWarpEndDistance,
     (const.minWarpEndDistance / 10000 + 1) * 10000,
     (const.minWarpEndDistance / 10000 + 2) * 10000,
     (const.minWarpEndDistance / 10000 + 3) * 10000,
     (const.minWarpEndDistance / 10000 + 5) * 10000,
     (const.minWarpEndDistance / 10000 + 7) * 10000,
     const.maxWarpEndDistance]
    return ranges


def DockOrJumpOrActivateGate(itemID):
    if _IsInvalidMovementTarget(itemID):
        return
    bp = sm.StartService('michelle').GetBallpark()
    menuSvc = GetMenuService()
    if bp:
        item = bp.GetInvItem(itemID)
        if item.groupID == const.groupStation:
            menuSvc.DockStation(itemID)
        elif item.categoryID == const.categoryStructure:
            if IsUpwellStargate(item.typeID):
                menuSvc.JumpThroughStructureJumpBridge(itemID)
            else:
                sm.GetService('structureDocking').Dock(itemID)
        elif item.groupID == const.groupStargate:
            slimItem = bp.slimItems.get(itemID)
            if slimItem:
                jump = slimItem.jumps[0]
                if not jump:
                    return
                menuSvc.StargateJump(itemID, item.typeID, jump.toCelestialID, jump.locationID)
        elif item.typeID in [const.typeNeedlejackTrace, const.typeYoiulTrace, const.typeTriglavianSpaceTrace]:
            menuSvc.ActivateRandomJumpTraceGate(itemID)
        elif item.typeID == const.typeAbyssEncounterGate:
            menuSvc.ActivateAbyssalAccelerationGate(itemID)
        elif item.typeID == const.typeAbyssEntranceGate:
            menuSvc.ActivateAbyssalEntranceAccelerationGate(itemID)
        elif item.typeID == const.typeAbyssExitGate:
            menuSvc.ActivateAbyssalEndGate(itemID)
        elif item.typeID == const.typeAbyssPvPGate:
            menuSvc.ActivatePVPAbyssalEndGate(itemID)
        elif item.typeID == const.typeVoidSpaceExitGate:
            menuSvc.ActivateVoidSpaceExitGate(itemID)
        elif item.groupID == const.groupWarpGate:
            menuSvc.ActivateAccelerationGate(itemID)
        elif item.groupID == const.groupWormhole:
            menuSvc.EnterWormhole(itemID)
        elif HasShipcasterComponent(item.typeID):
            menuSvc.JumpThroughShipcaster(itemID)


def _IsInvalidMovementTarget(itemID):
    if sm.GetService('michelle').GetRemotePark() is None:
        return False
    return itemID == session.shipid or sm.GetService('sensorSuite').IsSiteBall(itemID)


def ApproachLocation(bookmark):
    bp = sm.StartService('michelle').GetRemotePark()
    if bp:
        if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
            referringAgentID = getattr(bookmark, 'referringAgentID', None)
            sm.StartService('agents').GetAgentMoniker(bookmark.agentID).GotoLocation(bookmark.locationType, bookmark.locationNumber, referringAgentID)
        else:
            sm.GetService('menu').StoreAlignTarget(alignTargetID=None, aligningToBookmark=False)
            bp.CmdGotoBookmark(bookmark.bookmarkID)
            sm.GetService('tacticalNavigation').NotifyOfApproachCommand()


def WarpToBookmark(bookmark, warpRange = 20000.0, fleet = False):
    michelle = sm.GetService('michelle')
    bp = michelle.GetRemotePark()
    if bp:
        if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
            referringAgentID = getattr(bookmark, 'referringAgentID', None)
            sm.StartService('agents').GetAgentMoniker(bookmark.agentID).WarpToLocation(bookmark.locationType, bookmark.locationNumber, warpRange, fleet, referringAgentID, GetFormationSettings())
        else:
            sm.GetService('autoPilot').CancelSystemNavigation()
            michelle.CmdWarpToStuff('bookmark', bookmark.bookmarkID, minRange=warpRange, fleet=fleet)
            sm.StartService('space').WarpDestination(bookmarkID=bookmark.bookmarkID)


def WarpFleetToBookmark(bookmark, warpRange = 20000.0, fleet = True):
    michelle = sm.GetService('michelle')
    bp = michelle.GetRemotePark()
    if bp:
        if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
            referringAgentID = getattr(bookmark, 'referringAgentID', None)
            sm.StartService('agents').GetAgentMoniker(bookmark.agentID).WarpToLocation(bookmark.locationType, bookmark.locationNumber, warpRange, fleet, referringAgentID, GetFormationSettings())
        else:
            sm.GetService('autoPilot').CancelSystemNavigation()
            michelle.CmdWarpToStuff('bookmark', bookmark.bookmarkID, minRange=warpRange, fleet=fleet)


def WarpToItem(itemID, warpRange = None, cancelAutoNavigation = True, warpSubject = WarpSubjects.ITEM):
    if itemID == session.shipid:
        return
    if warpRange is None:
        warpRange = GetMenuService().GetDefaultActionDistance('WarpTo')
    siteBracket = sm.GetService('sensorSuite').GetBracketByBallID(itemID)
    if siteBracket:
        siteBracket.data.WarpToAction(None, warpRange)
        return
    michelle = sm.GetService('michelle')
    bp = michelle.GetRemotePark()
    if bp is not None:
        if cancelAutoNavigation:
            sm.GetService('autoPilot').CancelSystemNavigation()
        michelle.CmdWarpToStuff(warpSubject, itemID, minRange=warpRange)
        sm.StartService('space').WarpDestination(celestialID=itemID)
        sm.GetService('flightPredictionSvc').OptionActivated('AlignTo', itemID)
        item = michelle.GetItem(itemID)
        if item and item.typeID == const.typeAsteroidBelt:
            sm.ScatterEvent('OnWarpToAsteroidBelt')


def WarpToOperationSite(siteID):
    sm.ScatterEvent('OnOperationSiteWarpToExecuted', siteID)
    sm.GetService('michelle').CmdWarpToStuff(WarpSubjects.OPERATION_DUNGEON, siteID)


def CanWarpToOperationSite(siteID):
    sm.GetService('michelle').CanWarpToOperationSite(siteID)


def WarpToMiningPointPoint(moonID, warpRange = None):
    _WarpToMoonMiningPoint(moonID, warpRange)


def WarpFleetToMiningPointPoint(moonID, warpRange = None):
    _WarpToMoonMiningPoint(moonID, warpRange, fleet=True)


def _WarpToMoonMiningPoint(moonID, warpRange = None, fleet = False):
    if warpRange is None:
        warpRange = GetMenuService().GetDefaultActionDistance('WarpTo')
    michelle = sm.GetService('michelle')
    bp = michelle.GetRemotePark()
    if bp is not None:
        sm.GetService('autoPilot').CancelSystemNavigation()
        michelle.CmdWarpToStuff(WarpSubjects.MOON_MINING_POINT, moonID, minRange=warpRange, fleet=fleet)
        sm.StartService('space').WarpDestination(celestialID=moonID)
        sm.GetService('flightPredictionSvc').OptionActivated('AlignTo', moonID)


def GetFormationSettings():
    skillSvc = sm.GetService('skills')
    formationSettings = {'formationType': GetFormationSelected(skillSvc.MySkillLevel(FORMATION_SKILL)),
     'formationSpacing': GetFormationSpacingSelected(skillSvc.MySkillLevel(FORMATION_DISTANCE_SKILL)),
     'formationSize': GetFormationSizeSelected(skillSvc.MySkillLevel(FORMATION_DISTANCE_SKILL))}
    return formationSettings


def RealDock(itemID):
    bp = sm.StartService('michelle').GetBallpark()
    if not bp:
        return
    if sm.GetService('viewState').HasActiveTransition():
        return
    eve.Message('OnDockingRequest')
    bp = sm.GetService('michelle').GetRemotePark()
    if bp is not None:
        log.LogNotice('Docking', itemID)
        if uicore.uilib.Key(uiconst.VK_CONTROL) and uicore.uilib.Key(uiconst.VK_SHIFT) and uicore.uilib.Key(uiconst.VK_MENU) and session.role & ROLE_GML:
            sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdTurboDock, itemID)
        else:
            sm.GetService('sessionMgr').PerformSessionChange('dock', bp.CmdDock, itemID, session.shipid)


def RealActivateRandomFilamentGate(itemID):
    remoteBallpark = sm.GetService('michelle').GetRemotePark()
    try:
        remoteBallpark.CallComponentFromClient(itemID, FILAMENT_SPOOLUP, 'JumpThroughRandomFilamentGate')
    except UserError as e:
        if e.msg == 'RandomJumpError':
            textList = []
            for errorLine in e.dict['errors']:
                errorCode, errorArgs = errorLine
                text = get_error_label(localization.GetByLabel, errorCode, *errorArgs)
                textList.append(text)

            if textList:
                text = '<br>'.join(textList)
                ShowQuickMessage(text)
                return
        raise


def RealActivateAccelerationGate(itemID):
    crimewatchSvc = sm.GetService('crimewatchSvc')
    requiredSafetyLevel, errorMessage, confirmationMessage = crimewatchSvc.GetRequiredSafetyLevelForActivatingAccelerationGate(itemID)
    considerSvc = sm.GetService('consider')
    if not considerSvc.SafetyCheckPasses(requiredSafetyLevel):
        raise UserError(errorMessage)
    if confirmationMessage:
        userPromptResult = eve.Message(confirmationMessage, buttons=uiconst.YESNO)
        if userPromptResult != uiconst.ID_YES:
            return
    try:
        sm.StartService('sessionMgr').PerformSessionChange(localization.GetByLabel('UI/Inflight/ActivateGate'), sm.RemoteSvc('keeper').ActivateAccelerationGate, itemID, violateSafetyTimer=1)
    except UserError as e:
        if e.msg in ('DunShipCannotWarp', 'DunBlacklistCannotWarp'):
            dungeonID = sm.GetService('dungeonTracking').GetCurrentDungeonID()
            if dungeonID:
                slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(itemID)
                gateID = slimItem.dunObjectID if slimItem else None
                ShipRestrictionsWindow.Open(dungeon_id=dungeonID, gate_id=gateID)
                return
        raise

    log.LogNotice('Acceleration Gate activated to ', itemID)


def RealActivateAbyssalGate(itemID):
    sm.GetService('sessionMgr').PerformSessionChange('abyssToAbyssJump', sm.RemoteSvc('abyssalMgr').AbyssalGateActivation, itemID, violateSafetyTimer=True)


def RealActivateEntranceToAbyssalGate(itemID):
    sm.GetService('abyss').open_abyss_jump_window(itemID)


def RealActivateAbyssalEndGate(itemID):
    sm.GetService('sessionMgr').PerformSessionChange('abyssToKnownJump', sm.RemoteSvc('abyssalMgr').AbyssalEndGateActivation, itemID)


def RealActivatePVPAbyssalEndGate(itemID):
    sm.GetService('sessionMgr').PerformSessionChange('abyssToKnownJump', sm.RemoteSvc('pvpFilamentMgr').AbyssalPVPEndGateActivation, itemID)


def RealActivateVoidSpaceExitGate(itemID):
    sm.GetService('sessionMgr').PerformSessionChange('voidToKnownJump', sm.RemoteSvc('voidSpaceMgr').VoidSpaceEndGateActivation, itemID)


def RealEnterWormhole(itemID):
    isHighSec = sm.GetService('securitySvc').is_effective_high_sec_system(session.solarsystemid)
    if isHighSec and eve.Message('WormholeJumpingFromHiSec', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
        return
    log.LogNotice('Wormhole Jump from', session.solarsystemid2, 'to', itemID)
    sm.StartService('sessionMgr').PerformSessionChange(localization.GetByLabel('UI/Inflight/EnterWormhole'), sm.RemoteSvc('wormholeMgr').WormholeJump, itemID)


def RealJumpThroughShipcaster(itemID, targetSolarsystemID, targetLandingPadID):
    (sm.GetService('shipcaster').JumpThroughShipcaster(itemID, targetSolarsystemID, targetLandingPadID),)


def GetGlobalActiveItemKeyName(labelPath):
    return {'UI/Inflight/OrbitObject': 'Orbit',
     'UI/Inflight/Submenus/KeepAtRange': 'KeepAtRange',
     'UI/Inflight/WarpToWithinDistance': 'WarpTo',
     'UI/Inflight/Submenus/WarpToWithin': 'WarpTo'}.get(labelPath, None)


def GetDefaultWarpToLabel():
    defaultWarpDist = GetMenuService().GetDefaultActionDistance('WarpTo')
    return MenuLabel('UI/Inflight/WarpToWithinDistance', {'distance': FmtDist(float(defaultWarpDist))})


def StopMyShip():
    uicore.cmd.GetCommandAndExecute('CmdStopShip')


def TryStopMyShip():
    with ExceptionEater('Failed attempt to stop ship.'):
        StopMyShip()
