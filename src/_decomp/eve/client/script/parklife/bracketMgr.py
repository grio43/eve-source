#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\bracketMgr.py
import collections
import math
import sys
import blue
import stackless
import telemetry
import evetypes
import fsd.schemas.binaryLoader as fsdBinaryLoader
import localization
import overviewPresets.overviewSettingsConst as osConst
import uthread
from caching.memoize import Memoize
from carbon.common.script.sys import service
from carbon.common.script.util import logUtil as log
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.util import colorblind
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.parklife import states as state
from eve.client.script.parklife.bracketConst import SHOW_NONE, SHOW_DEFAULT, SHOW_ALL
from eve.client.script.parklife.bracketSettings import bracket_display_override_setting, bracket_showing_specials_setting
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.inflight.bracketsAndTargets import bracketVarious
from eve.client.script.ui.inflight.bracketsAndTargets.bracketNameFormatting import TagWithBold, TagWithColor, TagWithItalic, TagWithSize, TagWithUnderLine
from eve.client.script.ui.inflight.bracketsAndTargets.haulerBracket import HaulerBracket
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracket import InSpaceBracket
from eve.client.script.ui.inflight.bracketsAndTargets.navigationBracket import NavigationBracket
from eve.client.script.ui.inflight.bracketsAndTargets.siphonBracket import SiphonSiloBracket
from eve.client.script.ui.inflight.bracketsAndTargets.skyhookBracket import SkyhookBracket
from eve.client.script.ui.inflight.bracketsAndTargets.structureBracket import StructureBracket
from eve.client.script.ui.inflight.bracketsAndTargets.targetInBar import TargetInBar
from eve.client.script.ui.inflight.bracketsAndTargets.timedBracket import TimedBracket
from eve.client.script.ui.inflight.overview import overviewConst
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.util import uix
from eve.common.lib import appConst
from eve.common.script.sys import idCheckers
from eve.common.script.sys.idCheckers import IsSkyhook
from eveInflight.componentBracketController import ComponentBracketController
from eveprefs import prefs
from spacecomponents.client.messages import MSG_ON_BRACKET_CREATED
from stargate.client.gate_signals import on_lock_removed
from uthread2 import call_after_simtime_delay
RED = (0.8, 0, 0, 1.0)
ORANGE = (0.75, 0.4, 0, 1.0)
YELLOW = (1.0, 1.0, 0, 0.3)
RECORDED_DAMAGE_PERIOD_SECONDS = 120
NUMBER_OF_DAMAGEDEALERS = 5
INF = 1e+32
BRACKET_CATEGORIES_WITH_RANGE_MARKER = (appConst.categoryShip,
 appConst.categoryEntity,
 appConst.categoryDrone,
 appConst.categoryFighter)

class BracketMgr(service.Service):
    __guid__ = 'svc.bracket'
    __update_on_reload__ = 0
    __exportedcalls__ = {'GetBracketName': [],
     'GetBracketName2': [],
     'ResetOverlaps': [],
     'CheckOverlaps': [],
     'CleanUp': [],
     'ClearBracket': [],
     'GetBracketProps': [],
     'Reload': [],
     'GetScanSpeed': [],
     'GetCaptureData': []}
    __notifyevents__ = ['DoBallsAdded',
     'DoBallRemove',
     'DoBallClear',
     'ProcessSessionChange',
     'OnFleetStateChange',
     'OnStateChange',
     'OnDestinationSet',
     'OnPostCfgDataChanged',
     'OnBallparkCall',
     'OnSlimItemChange',
     'OnAttribute',
     'OnAttributes',
     'OnCaptureChanged',
     'ProcessBountyInfoUpdated',
     'OnUIScalingChange',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnDamageMessage',
     'OnDamageMessages',
     'DoBallsRemove',
     'OnStructureVisibilityUpdated',
     'OnHaulerQuantityChangedInClient',
     'OnRefreshWhenDockingRequestDenied',
     'OnStructureAccessUpdated',
     'OnDockingAccessChangedForCurrentSolarSystem_Local',
     'OnStateSetupChange',
     'OnMyFleetInited',
     'OnClientEvent_WarpStarted',
     'OnClientEvent_WarpFinished',
     'OnOverviewOverrideChanged',
     'OnBracketIconUpdated',
     'OnEmanationLockUpdated']
    __startupdependencies__ = ['wreck', 'overviewPresetSvc']
    __dependencies__ = ['michelle',
     'tactical',
     'map',
     'settings',
     'target',
     'fighters',
     'stateSvc']

    def __init__(self):
        super(BracketMgr, self).__init__()
        self.wantedGroupsWhenSelectedOnly = (appConst.groupHarvestableCloud,)
        self.wantedCategoriesWhenSelectedOnly = (appConst.categoryAsteroid,)
        self.specials = (appConst.groupLargeCollidableStructure, appConst.groupMoon)
        self.renewingBracketFlags = False
        self.pendingBracketRenewal = False
        self.filterLCS = ['wall_x',
         'wall_z',
         ' wall',
         ' barricade',
         ' fence',
         ' barrier',
         ' junction',
         ' elevator',
         ' lookout',
         ' neon sign']
        self.showState = SHOW_DEFAULT
        self.showingSpecials = False
        self.componentBracketController = ComponentBracketController()
        bracket_display_override_setting.on_change.connect(self.OnBracketDisplaySettingChanged)
        bracket_showing_specials_setting.on_change.connect(self.OnBracketDisplaySettingChanged)
        on_lock_removed.connect(self.OnEmanationGateLockRemoved)
        colorblind.on_colorblind_mode_changed.connect(self.OnColorBlindModeChanged)

    def OnBracketDisplaySettingChanged(self, *args):
        self.SoftReload()

    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.scenarioMgr = sm.StartService('scenario')
        self.shipFighterState = GetShipFighterState()
        self.shipFighterState.signalOnFighterInSpaceUpdate.connect(self.OnFighterInSpaceUpdate)
        self.Reload()
        self.CreateBracketIndexes()

    def CreateBracketIndexes(self):
        self.bracketDataByCategoryID = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/bracketsByCategory.static', optimize=False)
        self.bracketDataByGroupID = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/bracketsByGroup.static', optimize=False)
        self.bracketDataByTypeID = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/bracketsByType.static', optimize=False)
        self.bracketsData = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/brackets.static', optimize=False)

    def GetBrackeDatatByID(self, bracketID):
        return self.bracketsData.get(bracketID, None)

    def GetBracketDataByTypeID(self, typeID):
        try:
            bracketID = self.bracketDataByTypeID[typeID]
        except KeyError:
            try:
                bracketID = self.bracketDataByGroupID[evetypes.GetGroupID(typeID)]
            except KeyError:
                try:
                    bracketID = self.bracketDataByCategoryID[evetypes.GetCategoryID(typeID)]
                except KeyError:
                    return None

        return self.GetBrackeDatatByID(bracketID)

    def GetBracketDataByGroupID(self, groupID):
        if groupID in self.bracketDataByGroupID:
            bracketID = self.bracketDataByGroupID[groupID]
            return self.GetBrackeDatatByID(bracketID)
        categoryID = evetypes.GetCategoryIDByGroup(groupID)
        if categoryID in self.bracketDataByCategoryID:
            bracketID = self.bracketDataByCategoryID[categoryID]
            return self.GetBrackeDatatByID(bracketID)

    def GetBracketIcon(self, typeID, isEmpty = None, itemID = None):
        bracket = self.GetBracketDataByTypeID(typeID)
        return self._GetBracketIcon(bracket, isEmpty, typeID, itemID)

    def _GetBracketIcon(self, bracket, isEmpty, typeID = None, itemID = None):
        if bracket:
            componentBracketIcon = self.componentBracketController.GetBracketIcon(bracket, self.michelle.GetBallpark(), typeID, itemID)
            if componentBracketIcon:
                return componentBracketIcon
            elif isEmpty and hasattr(bracket, 'texturePathEmpty'):
                return bracket.texturePathEmpty
            else:
                return bracket.texturePath

    def GetBracketIconByGroupID(self, groupID, isEmpty = None):
        bracket = self.GetBracketDataByGroupID(groupID)
        return self._GetBracketIcon(bracket, isEmpty)

    def Stop(self, stream):
        self.CleanUp()

    def CleanUp(self):
        self.brackets = {}
        self.updateBrackets = {}
        self.damageByBracketID = {}
        self.biggestDamageDealers = []
        self.shipLabels = None
        self.overlaps = []
        self.overlapsHidden = []
        self.checkingOverlaps = 0
        self.showHiddenTimer = None
        self.hairlinesTimer = None
        self.inTargetRangeTimer = None
        self.damageDealerTimer = None
        uicore.layer.bracket.Flush()
        self.fleetBracketColor = (0.6, 0.15, 0.9, 0.5)

    def Hide(self):
        l_bracket = uicore.layer.bracket
        if l_bracket:
            l_bracket.state = uiconst.UI_HIDDEN

    def Show(self):
        l_bracket = uicore.layer.bracket
        if l_bracket:
            l_bracket.state = uiconst.UI_PICKCHILDREN

    @telemetry.ZONE_METHOD
    def Reload(self, *args, **kwds):
        self.CleanUp()
        overviewPresetSvc = sm.GetService('overviewPresetSvc')
        showInTargetRange = overviewPresetSvc.GetSettingValueOrDefaultFromName(osConst.SETTING_TARGET_RANGE, True)
        if showInTargetRange:
            self.inTargetRangeTimer = AutoTimer(1000, self.ShowInTargetRange)
        showBiggestDamageDealers = overviewPresetSvc.GetSettingValueOrDefaultFromName(osConst.SETTING_BIGGEST_DMG_DEALER, True)
        if showBiggestDamageDealers:
            self.damageDealerTimer = AutoTimer(1000, self.ShowBiggestDamageDealers_thread)
        uthread.new(self.SoftReload)
        self.UpdateFleetColor()

    @telemetry.ZONE_METHOD
    def SoftReload(self, showSpecials = None, bracketShowState = None):
        if bracketShowState is not None:
            self.showState = bracketShowState
        if showSpecials is not None:
            self.showingSpecials = showSpecials
        ballPark = sm.GetService('michelle').GetBallpark(doWait=True)
        if not ballPark:
            return
        for slimItem in ballPark.slimItems.itervalues():
            self.AddBracketIfWanted(slimItem)

    def ShowOwnShip(self):
        if not self.showHiddenTimer:
            myShipBracket = self.brackets.get(session.shipid, None)
            if myShipBracket:
                myShipBracket.ShowOwnShip()
                self.showHiddenTimer = AutoTimer(100, self.StopShowingHidden)

    def StopShowingHidden(self):
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        if not alt:
            self.showHiddenTimer = None
            bracket = self.brackets.get(session.shipid, None)
            if bracket:
                bracket.SetNormalInvisibleStateForOwnShip()

    def IsShowingAll(self):
        return bracket_display_override_setting.is_equal(SHOW_ALL)

    def IsHidingAll(self):
        return bracket_display_override_setting.is_equal(SHOW_NONE)

    def IsShowingSpecials(self):
        return bracket_showing_specials_setting.is_enabled()

    @telemetry.ZONE_METHOD
    def IsWanted(self, ballID, typeID = None, groupID = None, categoryID = None, slimItem = None, filtered = None):
        if typeID and not self.GetBracketDataByTypeID(typeID):
            return False
        else:
            if typeID is None or groupID is None or categoryID is None:
                slimItem = slimItem or sm.GetService('michelle').GetBallpark().GetInvItem(ballID)
                if slimItem is None:
                    log.LogWarn('IsWanted - ball', ballID, 'not found in park')
                    return False
                typeID = slimItem.typeID
                groupID = slimItem.groupID
                categoryID = slimItem.categoryID
            if groupID == appConst.groupDeadspaceOverseersStructure:
                checkName = evetypes.GetName(typeID).lower()
                if checkName in self.filterLCS:
                    return False
            if categoryID == appConst.categoryStructure:
                if not sm.GetService('structureProximityTracker').IsStructureVisible(ballID):
                    return False
            if groupID in self.wantedGroupsWhenSelectedOnly or categoryID in self.wantedCategoriesWhenSelectedOnly:
                return self.IsSelectedOrTargeted(ballID)
            isSpecial = groupID in self.specials
            if isSpecial:
                if self.IsShowingSpecials():
                    return True
                return self.IsSelectedOrTargeted(ballID)
            if self.IsShowingAll():
                return True
            isSelectedOrTargeted = self.IsSelectedOrTargeted(ballID)
            if self.IsHidingAll():
                return isSelectedOrTargeted
            if isSelectedOrTargeted:
                return True
            slimItem = slimItem or sm.GetService('michelle').GetBallpark().GetInvItem(ballID)
            filtered = filtered or sm.GetService('tactical').GetFilteredStatesFunctionNames(isBracket=True)
            alwaysShown = sm.GetService('tactical').GetAlwaysShownStatesFunctionNames()
            return sm.GetService('tactical').WantIt(slimItem, filtered, alwaysShown, isBracket=True)

    @telemetry.ZONE_METHOD
    def IsSelectedOrTargeted(self, ballID):
        for isWanted in self.stateSvc.GetStates(ballID, [state.selected,
         state.targeted,
         state.targeting,
         state.activeTarget]):
            if isWanted:
                return True

        return sm.GetService('target').IsTarget(ballID)

    def GetBracketName(self, objectID):
        if objectID in self.brackets:
            return self.brackets[objectID].displayName
        return ''

    def GetBracket(self, objectID):
        return self.brackets.get(objectID, None)

    def GetBracketName2(self, objectID):
        if not objectID:
            return ''
        ret = self.GetBracketName(objectID)
        if ret != '':
            ret = ret.replace('<br>', ' ')
            return ret
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return ''
        slimItem = ballpark.slimItems.get(objectID, None)
        if slimItem is None:
            return ''
        ret = self.GetDisplayNameForBracket(slimItem)
        if ret:
            ret = ret.replace('<br>', ' ')
        return ret

    def DisplayName(self, slimItem, displayName):
        shipLabelList = []
        if not getattr(self, 'shipLabels', None):
            self.shipLabels = self.stateSvc.GetShipLabels()
            self.hideCorpTicker = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(osConst.SETTING_HIDE_CORP_TICKER, True)
        for label in self.shipLabels:
            isVisible = label[overviewConst.LABEL_STATE]
            labelType = label[overviewConst.LABEL_TYPE]
            if labelType != overviewConst.LABEL_TYPE_LINEBREAK and not isVisible:
                continue
            pre = label[overviewConst.PRE]
            post = label[overviewConst.POST]
            labelText = None
            if labelType is overviewConst.LABEL_TYPE_NONE:
                if slimItem.corpID and not idCheckers.IsNPC(slimItem.corpID):
                    shipLabelList.append(pre)
            elif labelType == overviewConst.LABEL_TYPE_LINEBREAK:
                if shipLabelList and shipLabelList[-1] != overviewConst.CHAR_BR:
                    shipLabelList.append(overviewConst.CHAR_BR)
            elif labelType == overviewConst.LABEL_TYPE_CORP:
                if slimItem.corpID and not idCheckers.IsNPC(slimItem.corpID) and not (self.hideCorpTicker and slimItem.allianceID):
                    labelText = cfg.corptickernames.Get(slimItem.corpID).tickerName
            elif labelType == overviewConst.LABEL_TYPE_ALLIANCE:
                if slimItem.allianceID:
                    try:
                        labelText = cfg.allianceshortnames.Get(slimItem.allianceID).shortName
                    except:
                        log.LogError('Failed to get allianceName, itemID:', slimItem.itemID, 'allianceID:', slimItem.allianceID)

            elif labelType == overviewConst.LABEL_TYPE_PILOT:
                labelText = displayName
            elif labelType == overviewConst.LABEL_TYPE_SHIP_TYPE:
                labelText = evetypes.GetName(slimItem.typeID)
            elif labelType == overviewConst.LABEL_TYPE_SHIP_NAME:
                labelText = cfg.evelocations.Get(slimItem.itemID).name
            if labelText:
                labelsForType = [labelText]
                isBold = label.get(overviewConst.LABEL_BOLD, False)
                isUnderlined = label.get(overviewConst.LABEL_UNDERLINE, False)
                isItalic = label.get(overviewConst.LABEL_ITALIC, False)
                labelsForType = TagWithBold(labelsForType, isBold)
                labelsForType = TagWithUnderLine(labelsForType, isUnderlined)
                labelsForType = TagWithItalic(labelsForType, isItalic)
                labelsForType.insert(0, pre)
                labelsForType.append(post)
                color = label.get(overviewConst.LABEL_COLOR, None)
                fontsize = label.get(overviewConst.LABEL_SIZE)
                labelsForType = TagWithColor(labelsForType, color)
                labelsForType = TagWithSize(labelsForType, fontsize)
                shipLabelList += labelsForType

        return ''.join(shipLabelList)

    def OnSlimItemChange(self, oldSlim, newSlim):
        bracket = self.GetBracket(newSlim.itemID)
        if not bracket:
            return
        if hasattr(bracket, 'OnSlimItemChange'):
            bracket.OnSlimItemChange(oldSlim, newSlim)
        bracket.slimItem = newSlim
        bracket.displayName = None
        if idCheckers.IsStarbase(newSlim.categoryID):
            if newSlim.posState == oldSlim.posState and newSlim.posTimestamp == oldSlim.posTimestamp and newSlim.incapacitated == oldSlim.incapacitated and newSlim.controllerID == oldSlim.controllerID and newSlim.ownerID == oldSlim.ownerID:
                return
            bracket.UpdateStructureState(newSlim)
        elif idCheckers.IsOrbital(newSlim.categoryID):
            if newSlim.orbitalState == oldSlim.orbitalState and newSlim.orbitalTimestamp == oldSlim.orbitalTimestamp and newSlim.ownerID == oldSlim.ownerID and newSlim.orbitalHackerID == oldSlim.orbitalHackerID and newSlim.orbitalHackerProgress == oldSlim.orbitalHackerProgress:
                return
            bracket.UpdateOrbitalState(newSlim)
        elif newSlim.groupID == appConst.groupPlanet and newSlim.corpID != oldSlim.corpID:
            if newSlim.corpID is not None:
                bracket.displaySubLabel = localization.GetByLabel('UI/DustLink/ControlledBy', corpName=cfg.eveowners.Get(newSlim.corpID).name)
            else:
                bracket.displaySubLabel = None
        if newSlim.corpID != oldSlim.corpID:
            uthread.pool('BracketMgr::OnSlimItemChange --> UpdateStates', bracket.UpdateFlagAndBackground, newSlim)
        if newSlim.groupID in appConst.environmentContainers:
            if newSlim.groupID == appConst.groupWreck and newSlim.isEmpty and not oldSlim.isEmpty:
                self.stateSvc.SetState(newSlim.itemID, state.flagWreckEmpty, True)
            bracket.Load_update(newSlim)
        self.UpdateCaptureFromSlim(newSlim)

    def UpdateCaptureFromSlim(self, slimItem):
        if getattr(slimItem, 'capturePoint', None):
            if not hasattr(self, 'capturePoints'):
                self.capturePoints = {}
            slimItem.capturePoint['lastIncident'] = blue.os.GetSimTime()
            self.capturePoints[slimItem.itemID] = slimItem.capturePoint
            bracket = self.GetBracket(slimItem.itemID)
            if bracket:
                bracket.UpdateCaptureProgress(slimItem.capturePoint)

    def ProcessSessionChange(self, isremote, session, change):
        if not sm.GetService('connection').IsConnected() or session.stationid is not None or session.charid is None:
            self.CleanUp()
        elif not change.has_key('solarsystemid') and change.has_key('shipid') and change['shipid'][0] is not None:
            oldShipID, shipID = change['shipid']
            slimItem = sm.GetService('michelle').GetItem(oldShipID)
            if slimItem is not None:
                self._RecreateBracket(slimItem)
            slimItem = sm.GetService('michelle').GetItem(shipID)
            if slimItem is not None:
                self._RecreateBracket(slimItem)

    def RecreateBracket(self, itemID):
        slimItem = sm.GetService('michelle').GetItem(itemID)
        if slimItem:
            self._RecreateBracket(slimItem)

    def _RecreateBracket(self, slimItem):
        self.RemoveBracket(slimItem.itemID)
        self.AddBracketIfWanted(slimItem)

    def GetBracketProps(self, slimItem, ball = None):
        bracketData = self.GetBracketDataByTypeID(slimItem.typeID)
        texturePath = self._GetBracketIcon(bracketData, getattr(slimItem, 'isEmpty', False), slimItem.typeID, slimItem.itemID)
        minVisibleDistance = getattr(bracketData, 'minVisibleDistance', 0.0)
        maxVisibleDistance = getattr(bracketData, 'maxVisibleDistance', INF)
        iconOffset = getattr(bracketData, 'iconOffset', 0)
        return (texturePath,
         1,
         minVisibleDistance,
         maxVisibleDistance,
         iconOffset,
         0)

    def PrimeLocations(self, slimItem):
        locations = []
        for each in slimItem.jumps:
            if each.locationID not in locations:
                locations.append(each.locationID)
            if each.toCelestialID not in locations:
                locations.append(each.toCelestialID)

        if len(locations):
            cfg.evelocations.Prime(locations)

    def DoBallsAdded(self, balls_slimItems, *args, **kw):
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::BracketMgr')
        try:
            uthread.new(self._AddBrackets, balls_slimItems).context = blue.pyos.taskletTimer.GetCurrent() + '::_AddBrackets'
        finally:
            t.PopTimer(timer)

    @telemetry.ZONE_METHOD
    def _AddBrackets(self, balls_slimItems):
        for ball, slimItem in balls_slimItems:
            self.AddBracketIfWanted(slimItem, ball)

    @telemetry.ZONE_METHOD
    def RemoveBracket(self, itemID):
        if itemID in self.brackets:
            self.LogInfo('DoBallRemove::bracketMgr removing item', itemID)
            bracket = self.brackets[itemID]
            if bracket is not None and not bracket.destroyed:
                bracket.Close()
            del self.brackets[itemID]
        if itemID in self.updateBrackets:
            del self.updateBrackets[itemID]

    @telemetry.ZONE_METHOD
    def AddBracketIfWanted(self, slimItem, ball = None):
        try:
            itemID = slimItem.itemID
            groupID = slimItem.groupID
            categoryID = slimItem.categoryID
            typeID = slimItem.typeID
            if not self.IsWanted(itemID, typeID=typeID, groupID=groupID, categoryID=categoryID, slimItem=slimItem):
                bracket = self.brackets.get(itemID, None)
                if bracket:
                    bracket.Hide()
                return
            bracket = self.brackets.get(itemID, None)
            if bracket:
                if not bracket.display:
                    bracket.Show()
                return
            ball = ball or sm.GetService('michelle').GetBall(itemID)
            if not ball:
                return
            panel = self.GetNewBracket(itemID=itemID, categoryID=categoryID, groupID=groupID, typeID=slimItem.typeID)
            self.brackets[itemID] = panel
            if typeID == appConst.typeAsteroidBelt:
                panel.name = 'bracketAsteroidBelt'
            elif categoryID == appConst.categoryAsteroid:
                panel.name = 'bracketAsteroid'
            elif categoryID == appConst.categoryStation:
                panel.name = 'bracketStation'
            elif hasattr(slimItem, 'ownerID'):
                if slimItem.ownerID == appConst.factionUnknown and groupID == appConst.groupPirateDrone:
                    panel.name = 'bracketNPCPirateDrone1'
            if categoryID == appConst.categoryFighter and slimItem.ownerID == session.charid:
                self.UpdateSquadronNumber(itemID, panel)
            panel.displayName = None
            if groupID == appConst.groupPlanet and slimItem.corpID:
                panel.displaySubLabel = localization.GetByLabel('UI/DustLink/ControlledBy', corpName=cfg.eveowners.Get(slimItem.corpID).name)
            else:
                panel.displaySubLabel = None
            self.SetupBracketProperties(panel, ball, slimItem)
            panel.updateItem = self.stateSvc.CheckIfUpdateItem(slimItem) and itemID != session.shipid
            panel.Startup(slimItem, ball)
            if panel.updateItem:
                self.updateBrackets[itemID] = panel
            if hasattr(self, 'capturePoints') and itemID in self.capturePoints.keys():
                panel.UpdateCaptureProgress(self.capturePoints[itemID])
            else:
                self.UpdateCaptureFromSlim(slimItem)
            if idCheckers.IsOrbital(categoryID):
                panel.UpdateOrbitalState(slimItem)
            self.michelle.GetBallpark().componentRegistry.SendMessageToItem(itemID, MSG_ON_BRACKET_CREATED, panel, slimItem)
        except AttributeError as e:
            log.LogException(e)
            sys.exc_clear()

    def OnFighterInSpaceUpdate(self, fighterID, tubeFlagID):
        try:
            fighterBracket = self.brackets[fighterID]
        except KeyError:
            pass
        else:
            fighterInSpace = self.shipFighterState.GetFighterInSpaceByID(fighterID)
            if fighterInSpace:
                fighterBracket.UpdateSquadronNumber(fighterInSpace.tubeFlagID)
            else:
                self.RecreateBracket(fighterID)

    def UpdateSquadronNumber(self, fighterID, fighterBracket):
        fighterInSpace = self.shipFighterState.GetFighterInSpaceByID(fighterID)
        if fighterInSpace is None:
            tubeFlagID = None
        else:
            tubeFlagID = fighterInSpace.tubeFlagID
        fighterBracket.UpdateSquadronNumber(tubeFlagID)

    def GetBracketClass(self, categoryID, groupID, typeID, itemID):
        if categoryID == appConst.categoryStructure:
            return StructureBracket
        elif typeID == appConst.typeMobileShippingUnit:
            return TimedBracket
        elif groupID == appConst.groupSiphonPseudoSilo:
            return SiphonSiloBracket
        elif groupID == appConst.groupNpcIndustrialCommand:
            return HaulerBracket
        elif self.IsMyFighterInSpace(categoryID, itemID) or itemID == session.shipid:
            return NavigationBracket
        elif IsSkyhook(typeID):
            return SkyhookBracket
        else:
            return InSpaceBracket

    def IsMyFighterInSpace(self, categoryID, itemID):
        return categoryID == appConst.categoryFighter and sm.GetService('fighters').shipFighterState.IsMyFighterInSpace(itemID)

    @telemetry.ZONE_METHOD
    def GetNewBracket(self, itemID = '', categoryID = None, groupID = None, typeID = None):
        bracketCls = self.GetBracketClass(categoryID, groupID, typeID, itemID)
        bracket = bracketCls(parent=uicore.layer.bracket, name='__inflightbracket_%s' % itemID, align=uiconst.NOALIGN, state=uiconst.UI_NORMAL)
        return bracket

    @telemetry.ZONE_METHOD
    def GetDisplayNameForBracket(self, slimItem):
        try:
            displayName = uix.GetSlimItemName(slimItem)
        except Exception as e:
            if slimItem:
                self.LogException('Couldnt generate name for bracket, slimItem is not None')
            else:
                self.LogException('Couldnt generate name for bracket, slimItem is None')
            return

        groupID = slimItem.groupID
        categoryID = slimItem.categoryID
        if groupID == appConst.groupStation:
            displayName = uix.EditStationName(displayName, usename=1)
        elif groupID == appConst.groupStargate:
            uthread.new(self.PrimeLocations, slimItem)
        elif groupID == appConst.groupHarvestableCloud:
            displayName = localization.GetByLabel('UI/Generic/HarvestableCloud', item=slimItem.typeID)
        if not idCheckers.IsOrbital(categoryID) and getattr(slimItem, 'corpID', None):
            displayName = self.DisplayName(slimItem, displayName)
        return displayName

    @telemetry.ZONE_METHOD
    def SetupBracketProperties(self, bracket, ball, slimItem, props = None):
        if props is None:
            props = self.GetBracketProps(slimItem, ball)
        _iconNo, _dockType, _minDist, _maxDist, _iconOffset, _logflag = props
        tracker = bracket.projectBracket
        tracker.trackBall = ball
        tracker.name = unicode(cfg.evelocations.Get(ball.id).locationName)
        tracker.parent = uicore.layer.inflight.GetRenderObject()
        tracker.dock = _dockType
        tracker.marginRight = tracker.marginLeft + bracket.width
        tracker.marginBottom = tracker.marginTop + bracket.height
        bracket.data = props
        bracket.dock = _dockType
        bracket.minDispRange = _minDist
        bracket.maxDispRange = _maxDist
        bracket.inflight = True
        bracket.ball = ball
        bracket.invisible = False

    @telemetry.ZONE_METHOD
    def UpdateLabels(self):
        self.shipLabels = self.stateSvc.GetShipLabels()
        self.hideCorpTicker = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(osConst.SETTING_HIDE_CORP_TICKER, True)
        for bracket in self.brackets:
            slimItem = self.brackets[bracket].slimItem
            if not slimItem:
                continue
            if slimItem.corpID:
                self.brackets[slimItem.itemID].displayName = self.GetDisplayNameForBracket(slimItem)
                if slimItem.groupID == appConst.groupPlanet:
                    self.brackets[slimItem.itemID].displaySubLabel = localization.GetByLabel('UI/DustLink/ControlledBy', corpName=cfg.eveowners.Get(slimItem.corpID).name)

    @telemetry.ZONE_METHOD
    def RenewFlags(self):
        if self.renewingBracketFlags:
            self.pendingBracketRenewal = True
            return
        self.renewingBracketFlags = True
        self.pendingBracketRenewal = False
        uthread.pool('BracketMgr::RenewFlags', self._RenewAllFlags)

    def _RenewAllFlags(self):
        try:
            self._DoRenewAllFlags()
        finally:
            self.renewingBracketFlags = False

        if self.pendingBracketRenewal:
            self.RenewFlags()

    def _DoRenewAllFlags(self):
        for bracket in self.brackets.values():
            if not self._ShouldRenewBracket(bracket):
                continue
            bracket.Load_update(bracket.slimItem)
            blue.pyos.BeNice()

    def _ShouldRenewBracket(self, bracket):
        if bracket.destroyed:
            return False
        if bracket.itemID not in self.updateBrackets:
            if bracket.slimItem is None or bracket.slimItem.groupID not in appConst.containerGroupIDs:
                return False
        return True

    def RenewFlagForItemIDs(self, itemIDs):
        uthread.new(self._RenewFlagForItemIDs, itemIDs)

    def _RenewFlagForItemIDs(self, itemIDs):
        for eachItemID in itemIDs:
            bracket = self.GetBracket(eachItemID)
            if bracket is None:
                continue
            if not self._ShouldRenewBracket(bracket):
                continue
            bracket.Load_update(bracket.slimItem)
            blue.pyos.BeNice()

    def RenewSingleFlagForCharID(self, charID):
        uthread.new(self._RenewSingleFlag, charID)

    def _RenewSingleFlag(self, charID):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        for bracket in self.brackets.itervalues():
            slimItem = bracket.slimItem
            if slimItem is None:
                continue
            if bracket.itemID not in self.updateBrackets:
                if slimItem.groupID not in appConst.containerGroupIDs:
                    continue
            if getattr(slimItem, 'ownerID', None) == charID:
                bracket.Load_update(slimItem)
            elif getattr(slimItem, 'charID', None) == charID:
                bracket.Load_update(slimItem)
            blue.pyos.BeNice()

    def OnBallparkCall(self, funcName, args):
        if funcName == 'SetBallFree':
            itemID, isFree = args
            bracket = self.GetBracket(itemID)
            if bracket and bracket.slimItem:
                bracket.SetBracketAnchoredState(bracket.slimItem)

    def OnClientEvent_WarpStarted(self, *args):
        for itemID, bracket in self.brackets.iteritems():
            if isinstance(bracket, StructureBracket) and bracket.slimItem.timer is not None:
                bracket.Update()
                call_after_simtime_delay(bracket.Update, 10)

    def OnClientEvent_WarpFinished(self, *args):
        for itemID, bracket in self.brackets.iteritems():
            if isinstance(bracket, StructureBracket) and bracket.slimItem.timer is not None:
                bracket.Update()

    def OnOverviewOverrideChanged(self):
        self.SoftReload()

    def OnBracketIconUpdated(self, itemID):
        bracket = self.brackets.get(itemID, None)
        if bracket and hasattr(bracket, 'UpdateIcon'):
            bracket.UpdateIcon()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        if isRelease:
            for itemID, bracket in self.brackets.iteritems():
                if bracket is not None and not bracket.destroyed:
                    bracket.Close()

            self.capturePoints = {}
            self.brackets = {}
            self.updateBrackets = {}
            return
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        self.RemoveBracket(ball.id)
        if ball.id in getattr(self, 'capturePoints', {}):
            del self.capturePoints[ball.id]

    def DoBallClear(self, solitem):
        self.brackets = {}
        self.updateBrackets = {}
        for bracket in uicore.layer.bracket.children:
            bracket.Close()

    def OnUIScalingChange(self, *args):
        self.Reload()

    def OnColorBlindModeChanged(self):
        self.Reload()

    def OnDestinationSet(self, destinationID = None):
        focusOn = []
        updateGroups = (appConst.groupStation, appConst.groupStargate)
        updateCategories = (appConst.categoryStructure,)
        for each in uicore.layer.bracket.children:
            if not getattr(each, 'IsBracket', 0) or each.destroyed:
                continue
            if not each.slimItem or each.slimItem.groupID not in updateGroups and each.slimItem.categoryID not in updateCategories:
                continue
            each.UpdateIconColor(each.slimItem)
            if each.sr.icon and each.sr.icon.GetRGB() != appConst.OVERVIEW_NORMAL_COLOR:
                focusOn.append(each)

        for each in focusOn:
            each.SetOrder(0)

    def OnFleetStateChange(self, fleetState):
        if fleetState:
            for itemID, tag in fleetState.targetTags.iteritems():
                bracket = self.GetBracket(itemID)
                if not bracket:
                    continue
                if bracket.slimItem:
                    bracket.Load_update(bracket.slimItem)

    def OnFleetJoin_Local(self, member, *args):
        self.UpdateWrecksAndContainers(member)

    def OnFleetLeave_Local(self, member, *args):
        self.UpdateWrecksAndContainers(member)

    def UpdateWrecksAndContainers(self, member):
        if member.charID == session.charid:
            for bracket in self.brackets.values():
                if bracket.slimItem and bracket.slimItem.groupID in (appConst.groupWreck, appConst.groupCargoContainer):
                    bracket.Load_update(bracket.slimItem)

    def OnStateChange(self, itemID, flag, flagState, *args):
        if flag in (state.selected, state.targeted, state.targeting):
            slimItem = uix.GetBallparkRecord(itemID)
            if not slimItem:
                return
            IsWanted = self.IsWanted(slimItem.itemID, slimItem=slimItem)
            if flagState:
                self.AddBracketIfWanted(slimItem)
            elif not IsWanted:
                self.RemoveBracket(slimItem.itemID)
                return
        bracket = self.GetBracket(itemID)
        if bracket:
            try:
                bracket.OnStateChange(itemID, flag, flagState, *args)
            except AttributeError:
                pass

    def OnStructureVisibilityUpdated(self, structureID):
        self.RecreateBracket(structureID)

    def OnHaulerQuantityChangedInClient(self, haulerID, qty, totalQty, ownerID, typeID):
        if haulerID in self.brackets:
            self.brackets[haulerID].UpdateQuantity(totalQty)

    def OnRefreshWhenDockingRequestDenied(self, structureID):
        bracket = self.GetBracket(structureID)
        if bracket and getattr(bracket, 'slimItem', None):
            bracket.UpdateFlagAndBackground(bracket.slimItem)

    def OnStructureAccessUpdated(self):
        self._RefreshStructureBracketIcons()

    def OnDockingAccessChangedForCurrentSolarSystem_Local(self):
        self._RefreshStructureBracketIcons()

    def _RefreshStructureBracketIcons(self):
        for eachBracket in self.brackets.itervalues():
            if getattr(eachBracket, 'slimItem', None) and eachBracket.slimItem.categoryID == appConst.categoryStructure:
                eachBracket.UpdateFlagAndBackground(eachBracket.slimItem)

    def OnAttribute(self, attributeName, item, newValue):
        if item.itemID == session.shipid and attributeName == 'scanResolution':
            for targetID in sm.GetService('target').GetTargeting():
                bracket = self.GetBracket(targetID)
                if bracket and hasattr(bracket, 'OnAttribute'):
                    bracket.OnAttribute(attributeName, item, newValue)

    def OnAttributes(self, changeList):
        for t in changeList:
            self.OnAttribute(*t)

    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            bracket = self.GetBracket(data[0])
            if bracket is not None:
                bracket.displayName = None

    def OnCaptureChanged(self, ballID, captureID, lastIncident, points, captureTime, lastCapturing):
        bracket = self.GetBracket(ballID)
        if not hasattr(self, 'capturePoints'):
            self.capturePoints = {}
        self.capturePoints[ballID] = {'captureID': captureID,
         'lastIncident': blue.os.GetSimTime(),
         'points': points,
         'captureTime': captureTime,
         'lastCapturing': lastCapturing}
        if bracket:
            bracket.UpdateCaptureProgress(self.capturePoints[ballID])

    def ResetOverlaps(self):
        for each in self.overlaps:
            if not getattr(each, 'IsBracket', 0):
                continue
            projectBracket = each.projectBracket
            if projectBracket:
                projectBracket.bracket = each.GetRenderObject()
                each.KillLabel()
                each.opacity = getattr(each, '_pervious_opacity', 1.0)
                each.SetAlign(uiconst.NOALIGN)

        for each in self.overlapsHidden:
            bubble = each.sr.bubble
            if bubble:
                bubble.state = uiconst.UI_PICKCHILDREN

        self.overlaps = []
        self.overlapsHidden = []

    def GetOverlapOverlap(self, sameX, minY, maxY):
        overlaps = []
        stillLeft = []
        for bracket in sameX:
            if bracket.absoluteTop > minY - 16 and bracket.absoluteBottom < maxY + 16:
                if bracket.displayName:
                    overlaps.append((bracket.displayName.lower(), bracket))
                else:
                    overlaps.append(('', bracket))
            else:
                stillLeft.append(bracket)

        return (overlaps, stillLeft)

    def CheckingOverlaps(self):
        return self.checkingOverlaps

    @telemetry.ZONE_METHOD
    def CheckOverlaps(self, sender, hideRest = 0):
        self.checkingOverlaps = sender.itemID
        self.ResetOverlaps()
        overlaps = []
        excludedC = (appConst.categoryAsteroid,)
        excludedG = (appConst.groupHarvestableCloud,)
        sameX = []
        LEFT = 0
        TOP = 1
        BOTTOM = 2
        RIGHT = 3
        BRACKETSIZE = 16
        MAXEXPANDED = 15

        @Memoize
        def GetAbsolute(bracket):
            ro = bracket.GetRenderObject()
            x, y = uicore.ReverseScaleDpi(ro.displayX), uicore.ReverseScaleDpi(ro.displayY)
            centerX = x + bracket.width / 2
            centerY = y + bracket.height / 2
            return (centerX - 8,
             centerY - 8,
             centerY + 8,
             centerX + 8)

        s = GetAbsolute(sender)
        topMargin, bottomMargin = sender.GetLockedPositionTopBottomMargin()
        sender._topMargin = topMargin
        sender._bottomMargin = bottomMargin
        totalHeight = BRACKETSIZE + topMargin
        for bracket in sender.parent.children:
            if not getattr(bracket, 'IsBracket', 0) or not bracket.display or bracket.invisible or bracket.categoryID in excludedC or bracket.groupID in excludedG or bracket == sender:
                continue
            b = GetAbsolute(bracket)
            overlapx = not (b[RIGHT] <= s[LEFT] or b[LEFT] >= s[RIGHT])
            overlapy = not (b[BOTTOM] <= s[TOP] or b[TOP] >= s[BOTTOM])
            if overlapx and overlapy and bracket.displayName:
                topMargin, bottomMargin = bracket.GetLockedPositionTopBottomMargin()
                bracket._topMargin = topMargin
                bracket._bottomMargin = bottomMargin
                totalHeight += topMargin + BRACKETSIZE + bottomMargin
                overlaps.append((bracket.displayName.lower(), bracket))
            elif overlapx and not overlapy:
                sameX.append(bracket)
            if len(overlaps) == MAXEXPANDED:
                break

        if not overlaps:
            self.checkingOverlaps = None
            sender.parent.state = uiconst.UI_PICKCHILDREN
            return
        if sameX:
            while len(overlaps) < MAXEXPANDED:
                minY = s[TOP] - totalHeight
                maxY = s[BOTTOM]
                oo, sameX = self.GetOverlapOverlap(sameX, minY, maxY)
                if not oo or not sameX:
                    break
                for overlap in oo:
                    overlaps.append(overlap)
                    topMargin, bottomMargin = overlap[1].GetLockedPositionTopBottomMargin()
                    overlap[1]._topMargin = topMargin
                    overlap[1]._bottomMargin = bottomMargin
                    totalHeight += topMargin + BRACKETSIZE + bottomMargin
                    if len(overlaps) == MAXEXPANDED:
                        break

        overlaps = SortListOfTuples(overlaps, reverse=True)

        def LockBracketPosition(bracket, left, top):
            projectBracket = bracket.projectBracket
            if projectBracket:
                projectBracket.bracket = None
            bracket.SetAlign(uiconst.TOPLEFT)
            bracket.left = left - bracket.width / 2
            lockedTopPos = top - (bracket.height - 16) / 2
            bracket.top = lockedTopPos
            bracket._lockedTopPos = lockedTopPos
            bracket.displayX = left
            bracket._pervious_opacity = bracket.opacity
            bracket.opacity = 1.0
            bracket.SetOrder(0)
            if hasattr(bracket, 'UpdateSubItems'):
                bracket.UpdateSubItems()

        top = s[TOP]
        left = s[LEFT] + BRACKETSIZE / 2
        sender._lockedTopPos = top
        self.overlaps = [sender] + overlaps
        for overlapBracket in self.overlaps:
            hasBubble = bool(overlapBracket.sr.bubble)
            if not hasBubble:
                overlapBracket.ShowLabel()
            if overlapBracket is not sender:
                top -= overlapBracket._bottomMargin
            LockBracketPosition(overlapBracket, left, top)
            top -= overlapBracket._topMargin + BRACKETSIZE

        self.overlapsHidden = []
        if hideRest:
            for bracket in sender.parent.children:
                if bracket is sender or bracket in overlaps or not getattr(bracket, 'IsBracket', 0) or bracket.state != uiconst.UI_PICKCHILDREN or bracket.invisible:
                    continue
                bubble = bracket.sr.bubble
                if bubble:
                    bubble.state = uiconst.UI_HIDDEN
                    self.overlapsHidden.append(bracket)

        if top < 0:
            for overlapBracket in self.overlaps:
                overlapBracket.top = -top + overlapBracket._lockedTopPos - BRACKETSIZE

        sender.parent.state = uiconst.UI_PICKCHILDREN
        self.checkingOverlaps = None
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)

    def OnGlobalMouseDown(self, *args):
        mo = uicore.uilib.mouseOver
        for bracket in self.overlaps:
            if mo in (bracket, bracket.label):
                return True

        self.ResetOverlaps()

    def GetBracket(self, bracketID):
        if getattr(self, 'brackets', None) is not None:
            return self.brackets.get(bracketID, None)

    def ClearBracket(self, id, *args, **kwds):
        self.RemoveBracket(id)

    def GetScanSpeed(self, source = None, target = None):
        if source is None:
            source = session.shipid
        if not source:
            return
        myitem = sm.GetService('godma').GetItem(source)
        scanSpeed = None
        if myitem.scanResolution and target:
            slimItem = target
            targetitem = sm.GetService('godma').GetType(slimItem.typeID)
            if targetitem.AttributeExists('signatureRadius'):
                radius = targetitem.signatureRadius
            else:
                radius = 0
            if radius <= 0.0:
                bp = sm.GetService('michelle').GetBallpark()
                radius = bp.GetBall(slimItem.itemID).radius
                if radius <= 0.0:
                    radius = evetypes.GetRadius(targetitem.typeID)
                    if radius <= 0.0:
                        radius = 1.0
            scanSpeed = 40000000.0 / myitem.scanResolution / math.log(radius + math.sqrt(radius * radius + 1)) ** 2.0
        if scanSpeed is None:
            scanSpeed = 2000
            log.LogWarn('GetScanSpeed returned the defauly scanspeed of %s ms ... missing scanResolution?' % scanSpeed)
        return min(scanSpeed, 180000)

    def GetCaptureData(self, ballID):
        if hasattr(self, 'capturePoints'):
            return self.capturePoints.get(ballID, None)

    def ProcessBountyInfoUpdated(self, itemIDs):
        for itemID in itemIDs:
            try:
                self.brackets[itemID].RefreshBounty()
            except KeyError:
                pass

    @telemetry.ZONE_METHOD
    def OnDamageMessages(self, dmgmsgs):
        for msg in dmgmsgs:
            self.OnDamageMessage(*msg[1:])

    @telemetry.ZONE_METHOD
    def OnDamageMessage(self, damageMessagesArgs):
        attackerID = damageMessagesArgs.get('attackerID', None)
        if attackerID is None:
            attackType = damageMessagesArgs.get('attackType', 'me')
            if attackType != 'me':
                self.LogWarn('No attacker found! - damageMessagesArgs = ', damageMessagesArgs)
            return
        damage = damageMessagesArgs['damage']
        s = blue.os.GetSimTime() / appConst.SEC
        if attackerID not in self.damageByBracketID:
            self.damageByBracketID[attackerID] = collections.defaultdict(long)
        self.damageByBracketID[attackerID][s] += int(damage)
        if damage:
            self.TryBlinkAttacker(attackerID)

    def DisableShowingDamageDealers(self, *args):
        if self.damageDealerTimer is None:
            return
        self.damageDealerTimer = None
        if not session.shipid:
            return
        oldDamageDealers = self.biggestDamageDealers[:]
        self.RemoveDamageIndicatorFromBrackets(oldDamageDealers, [])

    def EnableShowingDamageDealers(self, *args):
        if self.damageDealerTimer is None:
            self.ShowBiggestDamageDealers_thread()
            self.damageDealerTimer = AutoTimer(1000, self.ShowBiggestDamageDealers_thread)

    def TryBlinkAttacker(self, attackerID, *args):
        if attackerID not in self.biggestDamageDealers:
            return
        bracket = self.GetBracket(attackerID)
        if not bracket:
            return
        sprite = bracket.GetHitSprite(create=False)
        if sprite:
            uicore.animations.FadeTo(sprite, startVal=sprite.baseOpacity + 0.05, endVal=sprite.baseOpacity, duration=0.75, loops=1, curveType=uiconst.ANIM_OVERSHOT)

    def ShowBiggestDamageDealers_thread(self, *args):
        oldDamageDealers = self.biggestDamageDealers[:]
        newDamageDealers = self.FindBiggestDamageDealers()
        alphas = [0.25,
         0.2,
         0.15,
         0.12,
         0.08]
        size = [100,
         90,
         80,
         75,
         70]
        counter = 0
        self.biggestDamageDealers = []
        for damage, bracketID in newDamageDealers:
            bracket = self.GetBracket(bracketID)
            if bracket:
                sprite = bracket.GetHitSprite()
                currentPlace = getattr(sprite, 'currentPlace', None)
                duration = 0.2
                newOpacity = alphas[counter]
                sprite.baseOpacity = newOpacity
                newSize = size[counter]
                if currentPlace is None:
                    sprite.width = sprite.height = newSize
                    uicore.animations.FadeTo(sprite, startVal=0, endVal=newOpacity, duration=duration)
                else:
                    uicore.animations.FadeTo(sprite, startVal=sprite.opacity, endVal=newOpacity, duration=duration)
                    uicore.animations.MorphScalar(sprite, 'width', startVal=sprite.width, endVal=newSize, duration=duration)
                    uicore.animations.MorphScalar(sprite, 'height', startVal=sprite.height, endVal=newSize, duration=duration)
                sprite.currentPlace = counter
                self.biggestDamageDealers.append(bracketID)
                if getattr(prefs, 'showDamageOnTarget', False):
                    label = getattr(bracket, 'debugLabel', None)
                    if not label:
                        label = bracket.debugLabel = EveLabelSmall(text='', parent=bracket, top=42, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)
                    label.text = damage
            counter += 1

        self.RemoveDamageIndicatorFromBrackets(oldDamageDealers, self.biggestDamageDealers)

    def RemoveDamageIndicatorFromBrackets(self, oldDamageDealers, newDamageDealers, *args):
        for bracketID in oldDamageDealers:
            if bracketID in newDamageDealers:
                continue
            bracket = self.GetBracket(bracketID)
            if bracket is None:
                continue
            sprite = bracket.GetHitSprite(create=False)
            if sprite:
                sprite.Close()
            label = getattr(bracket, 'debugLabel', None)
            if label:
                label.Close()

    def FindBiggestDamageDealers(self, *args):
        numDamageDealers = NUMBER_OF_DAMAGEDEALERS
        now = blue.os.GetSimTime() / appConst.SEC
        timeline = now - RECORDED_DAMAGE_PERIOD_SECONDS
        attackersToRemove = []
        damageSumAndAttackerID = []
        for attackerID in self.damageByBracketID:
            latestAttacks = collections.defaultdict(long)
            for timestamp, value in self.damageByBracketID[attackerID].iteritems():
                if timestamp > timeline:
                    latestAttacks[timestamp] = value

            if len(latestAttacks) == 0:
                attackersToRemove.append(attackerID)
                continue
            self.damageByBracketID[attackerID] = latestAttacks
            if attackerID in self.brackets:
                totalDamage = sum(latestAttacks.itervalues())
                if totalDamage == 0:
                    continue
                attackersDamageTuple = (totalDamage, attackerID)
                damageSumAndAttackerID.append(attackersDamageTuple)

        for attackerID in attackersToRemove:
            del self.damageByBracketID[attackerID]

        damageSumAndAttackerID.sort(reverse=True)
        results = damageSumAndAttackerID[:numDamageDealers]
        return results

    def DisableInTargetRange(self, *args):
        if self.inTargetRangeTimer is None:
            return
        self.inTargetRangeTimer = None
        if not session.shipid:
            return
        for key, bracket in self.brackets.items():
            canTargetSprite = bracket.GetCanTargetSprite(create=False)
            if canTargetSprite:
                canTargetSprite.Close()

    def EnableInTargetRange(self, *args):
        if self.inTargetRangeTimer is None:
            self.ShowInTargetRange()
            self.inTargetRangeTimer = AutoTimer(1000, self.ShowInTargetRange)

    def ShowInTargetRange(self, *args):
        if not session.shipid:
            return
        bp = sm.GetService('michelle').GetBallpark()
        ship = sm.GetService('godma').GetItem(session.shipid)
        if ship is None:
            return
        maxTargetRange = ship.maxTargetRange
        for key, bracket in self.brackets.items():
            if not bracket or bracket.destroyed or key == session.shipid:
                continue
            if bracket.categoryID not in BRACKET_CATEGORIES_WITH_RANGE_MARKER:
                continue
            settingConfigName = 'showCategoryInTargetRange_%s' % bracket.categoryID
            showCategory = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(settingConfigName, True)
            distance = self.GetBallDistanceFromBracketKey(bp, key)
            if distance is None:
                continue
            canTargetSprite = bracket.GetCanTargetSprite()
            if canTargetSprite is not None:
                if distance > maxTargetRange or not showCategory:
                    newOpacity = 0.0
                    canTargetSprite.display = False
                    continue
                elif getattr(bracket, 'brighterForRange', False):
                    newOpacity = 1.0
                else:
                    newOpacity = 0.15
                canTargetSprite.display = True
                if canTargetSprite.opacity != newOpacity:
                    canTargetSprite.opacity = newOpacity or 0

    def ShowModuleRange(self, moduleID, rangeDistance, *args):
        showInTargetRange = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(osConst.SETTING_TARGET_RANGE, True)
        if not showInTargetRange:
            return
        bp = sm.GetService('michelle').GetBallpark()
        maxTargetRange = sm.GetService('godma').GetItem(session.shipid).maxTargetRange
        for key, bracket in self.brackets.items():
            if not bracket or bracket.destroyed or key == session.shipid:
                continue
            if bracket.categoryID not in BRACKET_CATEGORIES_WITH_RANGE_MARKER:
                continue
            distance = self.GetBallDistanceFromBracketKey(bp, key)
            if distance is None:
                continue
            if distance <= rangeDistance and distance <= maxTargetRange:
                bracket.brighterForRange = True
                canTargetSprite = bracket.GetCanTargetSprite()
                if canTargetSprite is not None:
                    canTargetSprite.opacity = 1.0

    def ShowHairlinesForModule(self, moduleID, reverse = False):
        showHairlines = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(osConst.SETTING_MODULE_HAIRLINES, True)
        if not showHairlines:
            if self.hairlinesTimer:
                self.hairlinesTimer = None
                self.StopShowingHairlines()
                ship = sm.GetService('michelle').GetBall(session.shipid)
                for moduleID in ship.modules:
                    self.ResetModuleIcon(moduleID)

            return
        for target in sm.GetService('target').targetsByID.itervalues():
            if not isinstance(target, TargetInBar):
                continue
            if target is None or target.destroyed:
                continue
            if moduleID in target.activeModules:
                weapon = target.GetWeapon(moduleID)
                icon = weapon.icon
                icon.SetAlpha(1.5)
                bracket = self.brackets.get(target.itemID)
                if bracket is None:
                    return
                self.ShowHairlines(moduleID, bracket, target, reverse)
                return

    def ShowHairlines(self, moduleID, bracket, target, reverse, *args):
        if getattr(self, 'vectorLines', None) is None:
            self.vectorLines = bracketVarious.TargetingHairlines()
            self.vectorLines.CreateHairlines(moduleID, bracket, target)
        self.vectorLines.UpdateHairlinePoints(moduleID, bracket, target)
        self.vectorLines.StartAnimation(reverse=reverse)
        self.hairlinesTimer = AutoTimer(50, self.AnimateVectorLine, moduleID, bracket, target)

    def AnimateVectorLine(self, moduleID, bracket, target, *args):
        if getattr(self, 'vectorLines', None) is None:
            return
        if bracket.destroyed:
            self.vectorLines.StopAnimations()
            self.vectorLines.HideLines()
            self.hairlinesTimer = None
            return
        self.vectorLines.UpdateHairlinePoints(moduleID, bracket, target)

    def StopShowingModuleRange(self, moduleID, *args):
        for key, bracket in self.brackets.items():
            if not bracket or bracket.destroyed:
                continue
            if getattr(bracket, 'brighterForRange', False):
                canTargetSprite = bracket.GetCanTargetSprite()
                if canTargetSprite is not None:
                    canTargetSprite.opacity = 0.3
                bracket.brighterForRange = False

        self.StopShowingHairlines()
        self.ResetModuleIcon(moduleID)

    def ResetModuleIcon(self, moduleID, *args):
        for target in sm.GetService('target').GetTargets().itervalues():
            if not isinstance(target, TargetInBar):
                continue
            target.ResetModuleIcon(moduleID)

    def StopShowingHairlines(self, *args):
        self.hairlinesTimer = None
        if getattr(self, 'vectorLines', None) is not None:
            self.vectorLines.HideLines()
            self.vectorLines.StopAnimations()

    def GetBallDistanceFromBracketKey(self, bp, bracketKey, *args):
        ball = bp.GetBall(bracketKey)
        if ball is None:
            return
        try:
            distance = int(ball.surfaceDist)
        except ValueError:
            return

        return distance

    def OnMyFleetInited(self):
        self.UpdateFleetColor()

    def OnStateSetupChange(self, *args):
        self.UpdateFleetColor()

    def UpdateFleetColor(self):
        flagInfo = self.stateSvc.GetStatePropsColorAndBlink(state.flagSameFleet)
        self.fleetBracketColor = flagInfo.flagColor[:3] + (0.5,)

    def GetFleetBracketColor(self):
        return self.fleetBracketColor

    def OnEmanationLockUpdated(self, lockDetails):
        if not lockDetails or lockDetails.solar_system_id != session.solarsystemid2:
            return
        self._UpdateEmanationLock()

    def OnEmanationGateLockRemoved(self, *args):
        if not session.solarsystemid:
            return
        self._UpdateEmanationLock()

    def _UpdateEmanationLock(self):
        systemInfo = cfg.mapSolarSystemContentCache.get(session.solarsystemid2, None)
        if not systemInfo:
            return
        self.RenewFlagForItemIDs(systemInfo.stargates.keys())
