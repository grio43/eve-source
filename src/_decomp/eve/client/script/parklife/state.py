#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\state.py
from collections import namedtuple
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.util import timerstuff
from carbonui.util import colorblind
from carbonui.util.color import Color
from eve.client.script.parklife.stateSetting import GetOrderConfigName, GetStateConfigName
from eve.common.lib import appConst
import overviewPresets.overviewSettingsConst as osConst
import eve.client.script.ui.inflight.overview.overviewConst as oConst
from eve.client.script.ui.inflight.overviewShipLabelObject import ShipLabel
from eve.common.script.mgt import buffBarConst
import inventorycommon.const as invConst
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.idCheckers import IsNPCCorporation
from fwwarzone.client.facwarUtil import IsMyFwFaction, IsMyCombatEnemyFaction
from localization import GetByLabel
from eve.client.script.parklife import states as state
import log
import telemetry
from eve.common.script.util import facwarCommon
from eve.client.script.ui.crimewatch import crimewatchConst
from evewar import warConst
CRIMINAL_RED = crimewatchConst.Colors.Criminal.GetRGBA()
SUSPECT_YELLOW = crimewatchConst.Colors.Suspect.GetRGBA()
DISAPPROVAL_COLOR = crimewatchConst.Colors.Disapproval.GetRGBA()
TURQUOISE = (0.0,
 0.63,
 0.57,
 1.0)
DRONES_AND_FIGHTERS = (invConst.categoryDrone, invConst.categoryFighter)
CATEGORIES_WITH_WARFACTIONID = DRONES_AND_FIGHTERS + (appConst.categoryStructure,)
NORELATIONSHIP_SENTINEL = "Just a string which will be used as a sentinel value.  We use 'is' to compare it so it doesn't matter that it's hella long."

def GetStateColors():
    STATE_COLORS = {'purple': ((0.6, 0.15, 0.9, 1.0), 'UI/Common/Colors/Purple'),
     'green': ((0.1, 0.6, 0.1, 1.0), 'UI/Common/Colors/Green'),
     'red': ((0.75, 0.0, 0.0, 1.0), 'UI/Common/Colors/Red'),
     'darkBlue': ((0.0, 0.15, 0.6, 1.0), 'UI/Common/Colors/DarkBlue'),
     'blue': ((0.2, 0.5, 1.0, 1.0), 'UI/Common/Colors/Blue'),
     'darkTurquoise': ((0.0, 0.34, 0.33, 1.0), 'UI/Common/Colors/DarkTurquoise'),
     'turquoise': (TURQUOISE, 'UI/Common/Colors/Turquoise'),
     'orange': ((1.0, 0.35, 0.0, 1.0), 'UI/Common/Colors/Orange'),
     'yellow': ((1.0, 0.7, 0.0, 1.0), 'UI/Common/Colors/Yellow'),
     'indigo': ((0.3, 0.0, 0.5, 1.0), 'UI/Common/Colors/Indigo')}
    if colorblind.IsReplacementEnabled():
        numColors = len(STATE_COLORS)
        STATE_COLORS = {name:(colorblind.GetEvenlyDistributedColor(color, i, numColors), label) for i, (name, (color, label)) in enumerate(STATE_COLORS.iteritems())}
    STATE_COLORS.update({'black': ((0.0, 0.0, 0.0, 1.0), 'UI/Common/Colors/Black'),
     'white': ((0.7, 0.7, 0.7, 1.0), 'UI/Common/Colors/White')})
    return STATE_COLORS


StateProperty = namedtuple('StateProperty', 'text label defaultColor hint iconIndex iconColor defaultBackgroundColor ownerText')
colorToNameMap = {color[0]:colorKey for colorKey, color in GetStateColors().iteritems()}

def FindColorName(colorValue):
    return colorToNameMap.get(colorValue, None)


def IsHighStanding(relationship):
    return relationship > appConst.contactGoodStanding


def IsGoodStanding(relationship):
    return appConst.contactGoodStanding >= relationship > appConst.contactNeutralStanding


def IsNeutralStanding(relationship):
    return relationship == appConst.contactNeutralStanding


def IsBadStanding(relationship):
    return appConst.contactBadStanding <= relationship < appConst.contactNeutralStanding


def IsHorribleStanding(relationship):
    return relationship < appConst.contactBadStanding


class StateSvc(Service):
    __guid__ = 'svc.stateSvc'
    __exportedcalls__ = {'GetExclState': [],
     'GetStates': [],
     'SetState': [],
     'RemoveWarOwners': []}
    __notifyevents__ = ['DoBallClear',
     'DoBallRemove',
     'OnSessionChanged',
     'DoBallsRemove']
    __update_on_reload__ = 0
    __startupdependencies__ = ['settings']
    __dependencies__ = ['bountySvc']

    def Run(self, *etc):
        Service.Run(self, *etc)
        self.logme = 0
        self.exclusive = [state.mouseOver,
         state.selected,
         state.activeTarget,
         state.lookingAt]
        self.exclusives = {}
        self.states = {}
        self.stateColors = {}
        self.stateBlinks = {}
        self.atWar = {}
        self.alliesAtWar = {}
        self.cachedStateSettings = {}
        self.stateColorsInited = 0
        self.props = None
        self.smartFilterProps = None
        self.defaultBackgroundOrder = [state.flagAtWarCanFight,
         state.flagAtWarMilitia,
         state.flagLimitedEngagement,
         state.flagSameFleet,
         state.flagSamePlayerCorp,
         state.flagSameAlliance,
         state.flagStandingHigh,
         state.flagStandingGood,
         state.flagSameMilitia,
         state.flagOutlaw,
         state.flagCriminal,
         state.flagSuspect,
         state.flagDisapproval,
         state.flagStandingHorrible,
         state.flagStandingBad,
         state.flagAlliesAtWar,
         state.flagDangerous,
         state.flagHasKillRight,
         state.flagSameNpcCorp,
         state.flagStandingNeutral,
         state.flagNoStanding,
         state.flagAgentInteractable,
         state.flagIsWanted]
        self.defaultBackgroundStates = [state.flagCriminal,
         state.flagSuspect,
         state.flagOutlaw,
         state.flagSameFleet,
         state.flagSamePlayerCorp,
         state.flagSameNpcCorp,
         state.flagSameAlliance,
         state.flagAtWarCanFight,
         state.flagAtWarMilitia,
         state.flagSameMilitia,
         state.flagLimitedEngagement]
        self.defaultFlagOrder = [state.flagAtWarCanFight,
         state.flagAtWarMilitia,
         state.flagLimitedEngagement,
         state.flagSameFleet,
         state.flagSamePlayerCorp,
         state.flagSameAlliance,
         state.flagStandingHigh,
         state.flagStandingGood,
         state.flagSameMilitia,
         state.flagOutlaw,
         state.flagCriminal,
         state.flagSuspect,
         state.flagDisapproval,
         state.flagStandingHorrible,
         state.flagStandingBad,
         state.flagAlliesAtWar,
         state.flagDangerous,
         state.flagHasKillRight,
         state.flagSameNpcCorp,
         state.flagStandingNeutral,
         state.flagNoStanding,
         state.flagAgentInteractable,
         state.flagIsWanted]
        self.defaultFlagStates = [state.flagSameFleet,
         state.flagSamePlayerCorp,
         state.flagSameNpcCorp,
         state.flagSameAlliance,
         state.flagAtWarCanFight,
         state.flagSameMilitia,
         state.flagAtWarMilitia,
         state.flagStandingHigh,
         state.flagStandingGood,
         state.flagStandingBad,
         state.flagStandingHorrible,
         state.flagCriminal,
         state.flagSuspect,
         state.flagDisapproval,
         state.flagOutlaw,
         state.flagAgentInteractable,
         state.flagStandingNeutral,
         state.flagAlliesAtWar,
         state.flagLimitedEngagement,
         state.flagDangerous,
         state.flagHasKillRight]
        self.defaultBlinkStates = {('flag', state.flagSuspect): True,
         ('flag', state.flagCriminal): True,
         ('flag', state.flagLimitedEngagement): True,
         ('flag', state.flagDisapproval): True,
         ('background', state.flagAtWarCanFight): True,
         ('background', state.flagAtWarMilitia): True}
        self.ewarStates = {buffBarConst.Slot_WarpScramblerMWD: (state.flagWarpScrambledMWD, appConst.iconModuleWarpScramblerMWD),
         buffBarConst.Slot_WarpScrambler: (state.flagWarpScrambled, appConst.iconModuleWarpScrambler),
         buffBarConst.Slot_FighterTackle: (state.flagWarpScrambled, appConst.iconModuleFighterTackle),
         buffBarConst.Slot_FocusedWarpScrambler: (state.flagWarpScrambledMWD, appConst.iconModuleFocusedWarpScrambler),
         buffBarConst.Slot_Webify: (state.flagWebified, appConst.iconModuleStasisWeb),
         buffBarConst.Slot_Electronic: (state.flagECMd, appConst.iconModuleECM),
         buffBarConst.Slot_EwRemoteSensorDamp: (state.flagSensorDampened, appConst.iconModuleSensorDamper),
         buffBarConst.Slot_EwTrackingDisrupt: (state.flagTrackingDisrupted, appConst.iconModuleTrackingDisruptor),
         buffBarConst.Slot_EwGuidanceDisrupt: (state.flagGuidanceDisrupted, appConst.iconModuleGuidanceDisruptor),
         buffBarConst.Slot_EwTargetPaint: (state.flagTargetPainted, appConst.iconModuleTargetPainter),
         buffBarConst.Slot_EwEnergyVampire: (state.flagEnergyLeeched, appConst.iconModuleNosferatu),
         buffBarConst.Slot_EwEnergyNeut: (state.flagEnergyNeut, appConst.iconModuleEnergyNeutralizer),
         buffBarConst.Slot_RemoteTracking: (state.flagRemoteTracking, appConst.iconModuleRemoteTracking),
         buffBarConst.Slot_EnergyTransfer: (state.flagEnergyTransfer, appConst.iconModuleEnergyTransfer),
         buffBarConst.Slot_SensorBooster: (state.flagSensorBooster, appConst.iconModuleSensorBooster),
         buffBarConst.Slot_EccmProjector: (state.flagECCMProjector, appConst.iconModuleECCMProjector),
         buffBarConst.Slot_RemoteHullRepair: (state.flagRemoteHullRepair, appConst.iconModuleHullRepairer),
         buffBarConst.Slot_RemoteArmorRepair: (state.flagRemoteArmorRepair, appConst.iconModuleArmorRepairer),
         buffBarConst.Slot_RemoteArmorMutadaptiveRepairer: (state.flagRemoteArmorRepair, appConst.iconModuleMutadaptiveArmorRepairer),
         buffBarConst.Slot_ShieldTransfer: (state.flagShieldTransfer, appConst.iconModuleShieldBooster)}
        self.ewarStateItems = self.ewarStates.items()
        self.shouldLogError = True
        self.InitFilter()

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change or 'allianceid' in change:
            self.atWar = {}
            self.alliesAtWar = {}

    def RemoveWarOwners(self, ownerIDs):
        if not self.atWar:
            return
        for ownerID in ownerIDs:
            if ownerID in self.atWar:
                del self.atWar[ownerID]
            if ownerID in self.alliesAtWar:
                del self.alliesAtWar[ownerID]

    def GetProps(self):
        if self.props is None:
            criminalLabelAndHint = (GetByLabel('UI/Services/State/Standing/Criminal'), GetByLabel('UI/Services/State/Standing/CriminalHint'))
            suspectLabelAndHint = (GetByLabel('UI/Services/State/Standing/Suspect'), GetByLabel('UI/Services/State/Standing/SuspectHint'))
            outlawLabelAndHint = (GetByLabel('UI/Services/State/Standing/Outlaw'), GetByLabel('UI/Services/State/Standing/OutlawHint'))
            dangerousLabelAndHint = (GetByLabel('UI/Services/State/Standing/Dangerous'), GetByLabel('UI/Services/State/Standing/DangerousHint'))
            sameFleetLabelAndHint = (GetByLabel('UI/Services/State/Standing/SameFleet'), GetByLabel('UI/Services/State/Standing/SameFleetHint'))
            sameCorpLabelAndHint = (GetByLabel('UI/Services/State/Standing/SameCorporation'), GetByLabel('UI/Services/State/Standing/SameCorporationHint'), GetByLabel('UI/Services/State/Standing/SameCorporationOwner'))
            sameNpcCorpLabelAndHint = (GetByLabel('UI/Services/State/Standing/SameNpcCorporation'), GetByLabel('UI/Services/State/Standing/SameNpcCorporationHint'), GetByLabel('UI/Services/State/Standing/SameNpcCorporationOwner'))
            sameAllianceLabelAndHint = (GetByLabel('UI/Services/State/Standing/SameAlliance'), GetByLabel('UI/Services/State/Standing/SameAllianceHint'), GetByLabel('UI/Services/State/Standing/SameAllianceOwner'))
            sameMilitiaLabelAndHint = (GetByLabel('UI/Services/State/Standing/SameMilitia'), GetByLabel('UI/Services/State/Standing/SameMilitiaHint'), GetByLabel('UI/Services/State/Standing/SameMilitiaOwner'))
            atWarWithCorpLabelAndHint = (GetByLabel('UI/Services/State/Standing/AtWarWithCorporationOrAlliance'), GetByLabel('UI/Services/State/Standing/AtWarWithCorporationOrAllianceHint'), GetByLabel('UI/Services/State/Standing/AtWarWithCorporationOrAllianceOwner'))
            atWarWithMilitiaLabelAndHint = (GetByLabel('UI/Services/State/Standing/AtWarWithMilitia'), GetByLabel('UI/Services/State/Standing/AtWarWithMilitiaHint'), GetByLabel('UI/Services/State/Standing/AtWarWithMilitiaOwner'))
            excellentLabelAndHint = (GetByLabel('UI/Services/State/Standing/Excellent'), GetByLabel('UI/Services/State/Standing/ExcellentHint'), GetByLabel('UI/Services/State/Standing/ExcellentOwner'))
            goodLabelAndHint = (GetByLabel('UI/Services/State/Standing/Good'), GetByLabel('UI/Services/State/Standing/GoodHint'), GetByLabel('UI/Services/State/Standing/GoodOwner'))
            neutralLabelAndHint = (GetByLabel('UI/Services/State/Standing/Neutral'), GetByLabel('UI/Services/State/Standing/NeutralHint'), GetByLabel('UI/Services/State/Standing/NeutralOwner'))
            badLabelAndHint = (GetByLabel('UI/Services/State/Standing/Bad'), GetByLabel('UI/Services/State/Standing/BadHint'), GetByLabel('UI/Services/State/Standing/BadOwner'))
            terribleLabelAndHint = (GetByLabel('UI/Services/State/Standing/Terrible'), GetByLabel('UI/Services/State/Standing/TerribleHint'), GetByLabel('UI/Services/State/Standing/TerribleOwner'))
            isWantedLabelAndHint = (GetByLabel('UI/Services/State/Standing/IsWanted'), GetByLabel('UI/Services/State/Standing/IsWantedHint'))
            hasKillRightLabelAndHint = (GetByLabel('UI/Services/State/Standing/HasKillRight'), GetByLabel('UI/Services/State/Standing/HasKillRightHint'))
            agentInteractableLabelAndHint = (GetByLabel('UI/Services/State/Standing/AgentIsInteractable'), GetByLabel('UI/Services/State/Standing/AgentIsInteractableHint'))
            wreckIsViewedLabelAndHint = (GetByLabel('UI/Services/State/Standing/WreckIsViewed'), GetByLabel('UI/Services/State/Standing/WreckIsViewedHint'))
            wreckIsEmptyLabelAndHint = (GetByLabel('UI/Services/State/Standing/WreckIsEmpty'), GetByLabel('UI/Services/State/Standing/WreckIsEmptyHint'))
            noStandingLabelAndHint = (GetByLabel('UI/Services/State/Standing/NoStanding'), GetByLabel('UI/Services/State/Standing/NoStandingHint'), GetByLabel('UI/Services/State/Standing/NoStandingOwner'))
            alliesAtWar = (GetByLabel('UI/Services/State/Standing/AlliesAtWar'), GetByLabel('UI/Services/State/Standing/AlliesAtWarHint'), GetByLabel('UI/Services/State/Standing/AlliesAtWarOwner'))
            limitedEngagementLabelAndHint = (GetByLabel('UI/Services/State/Standing/LimitedEngagement'), GetByLabel('UI/Services/State/Standing/LimitedEngagementHint'))
            disapprovalLabelAndHint = (GetByLabel('UI/Services/State/Standing/Disapproval'), GetByLabel('UI/Services/State/Standing/DisapprovalHint'))
            self.props = {state.flagCriminal: StateProperty(criminalLabelAndHint[0], 'Criminal', 'black', criminalLabelAndHint[1], 5, CRIMINAL_RED, 'red', None),
             state.flagSuspect: StateProperty(suspectLabelAndHint[0], 'Suspect', 'black', suspectLabelAndHint[1], 5, SUSPECT_YELLOW, 'yellow', None),
             state.flagOutlaw: StateProperty(outlawLabelAndHint[0], 'Outlaw', 'red', outlawLabelAndHint[1], 5, Color.WHITE, None, None),
             state.flagDangerous: StateProperty(dangerousLabelAndHint[0], 'Dangerous', 'yellow', dangerousLabelAndHint[1], 5, Color.WHITE, None, None),
             state.flagSameFleet: StateProperty(sameFleetLabelAndHint[0], 'SameFleet', 'purple', sameFleetLabelAndHint[1], 0, Color.WHITE, None, None),
             state.flagSamePlayerCorp: StateProperty(sameCorpLabelAndHint[0], 'SamePlayerCorp', 'green', sameCorpLabelAndHint[1], 1, Color.WHITE, None, sameCorpLabelAndHint[2]),
             state.flagSameNpcCorp: StateProperty(sameNpcCorpLabelAndHint[0], 'SameNpcCorp', 'green', sameNpcCorpLabelAndHint[1], 1, Color.WHITE, None, sameNpcCorpLabelAndHint[2]),
             state.flagSameAlliance: StateProperty(sameAllianceLabelAndHint[0], 'SameAlliance', 'darkBlue', sameAllianceLabelAndHint[1], 1, Color.WHITE, None, sameAllianceLabelAndHint[2]),
             state.flagSameMilitia: StateProperty(sameMilitiaLabelAndHint[0], 'SameMilitia', 'indigo', sameMilitiaLabelAndHint[1], 1, Color.WHITE, None, sameMilitiaLabelAndHint[2]),
             state.flagAtWarCanFight: StateProperty(atWarWithCorpLabelAndHint[0], 'AtWarCanFight', 'red', atWarWithCorpLabelAndHint[1], 1, Color.WHITE, None, atWarWithCorpLabelAndHint[2]),
             state.flagAtWarMilitia: StateProperty(atWarWithMilitiaLabelAndHint[0], 'AtWarMilitia', 'orange', atWarWithMilitiaLabelAndHint[1], 1, Color.WHITE, None, atWarWithMilitiaLabelAndHint[2]),
             state.flagStandingHigh: StateProperty(excellentLabelAndHint[0], 'StandingHigh', 'darkBlue', excellentLabelAndHint[1], 2, Color.WHITE, None, excellentLabelAndHint[2]),
             state.flagStandingGood: StateProperty(goodLabelAndHint[0], 'StandingGood', 'blue', goodLabelAndHint[1], 2, Color.WHITE, None, goodLabelAndHint[2]),
             state.flagStandingNeutral: StateProperty(neutralLabelAndHint[0], 'StandingNeutral', 'white', neutralLabelAndHint[1], 4, Color.WHITE, None, neutralLabelAndHint[2]),
             state.flagStandingBad: StateProperty(badLabelAndHint[0], 'StandingBad', 'orange', badLabelAndHint[1], 3, Color.WHITE, None, badLabelAndHint[2]),
             state.flagStandingHorrible: StateProperty(terribleLabelAndHint[0], 'StandingHorrible', 'red', terribleLabelAndHint[1], 3, Color.WHITE, None, terribleLabelAndHint[2]),
             state.flagIsWanted: StateProperty(isWantedLabelAndHint[0], 'IsWanted', 'black', isWantedLabelAndHint[1], 5, Color.WHITE, None, None),
             state.flagHasKillRight: StateProperty(hasKillRightLabelAndHint[0], 'HasKillRight', 'orange', hasKillRightLabelAndHint[1], 7, Color.WHITE, None, None),
             state.flagAgentInteractable: StateProperty(agentInteractableLabelAndHint[0], 'AgentInteractable', 'blue', agentInteractableLabelAndHint[1], 6, Color.WHITE, None, None),
             state.flagWreckAlreadyOpened: StateProperty(wreckIsViewedLabelAndHint[0], 'WreckViewed', 'white', wreckIsViewedLabelAndHint[1], 1, Color.WHITE, None, None),
             state.flagWreckEmpty: StateProperty(wreckIsEmptyLabelAndHint[0], 'WreckEmpty', 'white', wreckIsEmptyLabelAndHint[1], 1, Color.WHITE, None, None),
             state.flagNoStanding: StateProperty(noStandingLabelAndHint[0], 'NoStanding', 'white', noStandingLabelAndHint[1], 4, Color.WHITE, None, noStandingLabelAndHint[0]),
             state.flagAlliesAtWar: StateProperty(alliesAtWar[0], 'AlliesAtWar', 'darkBlue', alliesAtWar[1], 1, Color.WHITE, None, alliesAtWar[0]),
             state.flagLimitedEngagement: StateProperty(limitedEngagementLabelAndHint[0], 'LimitedEngagement', 'black', limitedEngagementLabelAndHint[1], 5, TURQUOISE, 'turquoise', None),
             state.flagDisapproval: StateProperty(disapprovalLabelAndHint[0], 'Disapproval', 'black', disapprovalLabelAndHint[1], 5, DISAPPROVAL_COLOR, None, None),
             state.flagForcedOn: StateProperty('', 'ForcedOn', 'white', '', 4, Color.WHITE, None, None)}
            self.defaultProp = StateProperty('', '', 'white', '', 6, Color.WHITE, None, '')
        return self.props

    def GetSmartFilterProps(self):
        if self.smartFilterProps is None:
            self.smartFilterProps = {state.flagWarpScrambledMWD: GetByLabel('UI/Services/State/InflightState/WarpScramblingMWD'),
             state.flagWarpScrambled: GetByLabel('UI/Services/State/InflightState/WarpScrambling'),
             state.flagWebified: GetByLabel('UI/Services/State/InflightState/Webified'),
             state.flagECMd: GetByLabel('UI/Services/State/InflightState/Jamming'),
             state.flagSensorDampened: GetByLabel('UI/Services/State/InflightState/SensorDamping'),
             state.flagTrackingDisrupted: GetByLabel('UI/Services/State/InflightState/TrackingDisrupting'),
             state.flagGuidanceDisrupted: GetByLabel('UI/Services/State/InflightState/GuidanceDisrupting'),
             state.flagTargetPainted: GetByLabel('UI/Services/State/InflightState/Painting'),
             state.flagEnergyLeeched: GetByLabel('UI/Services/State/InflightState/EnergyLeeched'),
             state.flagEnergyNeut: GetByLabel('UI/Services/State/InflightState/EnergyNeutralizing'),
             state.flagRemoteTracking: GetByLabel('UI/Services/State/InflightState/RemoteTracking'),
             state.flagEnergyTransfer: GetByLabel('UI/Services/State/InflightState/EnergyTransfer'),
             state.flagSensorBooster: GetByLabel('UI/Services/State/InflightState/SensorBooster'),
             state.flagECCMProjector: GetByLabel('UI/Services/State/InflightState/ECCMProjector'),
             state.flagRemoteHullRepair: GetByLabel('UI/Services/State/InflightState/RemoteHullRepair'),
             state.flagRemoteArmorRepair: GetByLabel('UI/Services/State/InflightState/RemoteArmorRepair'),
             state.flagShieldTransfer: GetByLabel('UI/Services/State/InflightState/ShieldTransfer')}
        return self.smartFilterProps

    @telemetry.ZONE_METHOD
    def GetStateProps(self, st = None):
        props = self.GetProps()
        if st is not None:
            if st in props:
                return props[st]
            else:
                if self.shouldLogError:
                    log.LogTraceback('Bad state flag: %s' % st)
                    self.shouldLogError = False
                return self.defaultProp
        else:
            return props

    @telemetry.ZONE_METHOD
    def GetActiveStateOrder(self, where):
        cacheKey = 'ActiveStateOrder_' + where
        if cacheKey in self.cachedStateSettings:
            return self.cachedStateSettings[cacheKey]
        return self.cachedStateSettings.setdefault(cacheKey, [ flag for flag in self.GetStateOrder(where) if self.GetStateState(where, flag) ])

    @telemetry.ZONE_METHOD
    def GetActiveStateOrderFunctionNames(self, where):
        cacheKey = 'ActiveStateOrderFunctionNames_' + where
        if cacheKey in self.cachedStateSettings:
            return self.cachedStateSettings[cacheKey]
        return self.cachedStateSettings.setdefault(cacheKey, [ self.GetStateProps(flag).label for flag in self.GetActiveStateOrder(where) ])

    @telemetry.ZONE_METHOD
    def GetStateOrder(self, where):
        where = where.lower()
        if where == 'background':
            default = self.defaultBackgroundOrder
        else:
            default = self.defaultFlagOrder
        configName = GetOrderConfigName(where)
        ret = settings.user.overview.Get(configName, default)
        if ret is None:
            return default
        ret.extend([ flag for flag in default if flag not in ret ])
        return ret

    @telemetry.ZONE_METHOD
    def GetStateState(self, where, flag):
        return flag in self.GetStateStates(where)

    @telemetry.ZONE_METHOD
    def GetStateStates(self, where):
        where = where.lower()
        configName = GetStateConfigName(where)
        ret = settings.user.overview.Get(configName)
        if ret is None:
            if where == 'background':
                ret = self.defaultBackgroundStates
            else:
                ret = self.defaultFlagStates
        return ret

    @telemetry.ZONE_METHOD
    def GetStateColors(self):
        return GetStateColors()

    @telemetry.ZONE_METHOD
    def GetStateColor(self, flag, where = 'flag'):
        self.InitColors()
        color = self.stateColors.get((where, flag))
        if color:
            return color
        else:
            color = self._GetDefaultColor(flag, where)
            return color

    def _GetDefaultColor(self, flag, where):
        colors = self.GetStateColors()
        defColor = None
        if where == 'background':
            defColor = self.GetStateProps(flag).defaultBackgroundColor
        if defColor is None:
            defColor = self.GetStateProps(flag).defaultColor
        color = colors[defColor][0]
        return color

    def GetStateFlagColor(self, flagCode):
        return self.GetStateColor(flagCode, 'flag')

    def GetStateBackgroundColor(self, flagCode):
        return self.GetStateColor(flagCode, 'background')

    def GetStatePropsColorAndBlink(self, flagCode):
        if not flagCode:
            return None
        return utillib.KeyVal(flagCode=flagCode, flagProperties=self.GetStateProps(flagCode), flagColor=self.GetStateFlagColor(flagCode), flagBlink=self.GetStateFlagBlink(flagCode))

    @telemetry.ZONE_METHOD
    def GetStateBlink(self, where, flag):
        defBlink = self.defaultBlinkStates.get((where, flag), 0)
        return settings.user.overview.Get(osConst.SETTING_STATE_BLINKS, {}).get((where, flag), defBlink)

    def GetStateFlagBlink(self, flagCode):
        return self.GetStateBlink('flag', flagCode)

    def GetStateBackgroundBlink(self, flagCode):
        return self.GetStateBlink('background', flagCode)

    @telemetry.ZONE_METHOD
    def GetEwarGraphicID(self, ewarType):
        flag, gid = self.ewarStates[ewarType]
        return gid

    def GetEwarTypes(self):
        return self.ewarStateItems

    def GetEwarFlag(self, ewarType):
        flag, gid = self.ewarStates[ewarType]
        return flag

    def GetEwarTypeByEwarState(self, flag = None):
        if not getattr(self, 'ewartypebystate', {}):
            ret = {}
            for ewarType, (f, gid) in self.ewarStateItems:
                ret[f] = ewarType

            self.ewartypebystate = ret
        if flag:
            return self.ewartypebystate[flag]
        return self.ewartypebystate

    def GetEwarHint(self, ewarType):
        flag, gid = self.ewarStates[ewarType]
        return self.GetSmartFilterProps()[flag]

    def GetFixedColorSettings(self):
        stateColors = settings.user.overview.Get(osConst.SETTING_STATE_COLORS, {})
        newStatesColors = {}
        for flag, color in stateColors.iteritems():
            if isinstance(flag, tuple):
                newStatesColors[flag] = color
            else:
                newStatesColors['flag', flag] = color
                newStatesColors['background', flag] = color

        settings.user.overview.Set(osConst.SETTING_STATE_COLORS, newStatesColors)
        return newStatesColors

    def SetStateColor(self, where, flag, color):
        self.InitColors()
        self.stateColors[where, flag] = color
        settings.user.overview.Set(osConst.SETTING_STATE_COLORS, self.stateColors.copy())
        self.cachedStateSettings = {}
        self.NotifyOnStateSetupChange('stateColor')

    def SetStateBlink(self, where, flag, blink):
        stateBlinks = settings.user.overview.Get(osConst.SETTING_STATE_BLINKS, {})
        stateBlinks[where, flag] = blink
        settings.user.overview.Set(osConst.SETTING_STATE_BLINKS, stateBlinks)
        self.cachedStateSettings = {}
        self.NotifyOnStateSetupChange('stateBlink')

    def InitColors(self, reset = 0):
        if reset:
            self.cachedStateSettings = {}
        if not self.stateColorsInited or reset:
            self.stateColors = self.GetFixedColorSettings()
            self.stateColorsInited = 1

    def ResetColors(self):
        settings.user.overview.Set(osConst.SETTING_STATE_COLORS, {})
        self.cachedStateSettings = {}
        self.InitColors(reset=True)
        self.NotifyOnStateSetupChange('stateColor')

    def InitFilter(self):
        self.filterCategs = {invConst.categoryShip,
         invConst.categoryEntity,
         invConst.categoryDrone,
         invConst.categoryFighter}
        self.updateCategs = self.filterCategs.copy()
        self.filterGroups = {invConst.groupCargoContainer,
         invConst.groupSecureCargoContainer,
         invConst.groupStargate,
         invConst.groupWarpGate,
         invConst.groupAbyssalTraces,
         invConst.groupAgentsinSpace,
         invConst.groupCosmicSignature,
         invConst.groupHarvestableCloud,
         invConst.groupForceField,
         invConst.groupWreck}
        applyToStructures = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_APPLY_STRUCTURE, True)
        applyToOtherObjects = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(osConst.SETTING_NAME_APPLY_OTHER_OBJ, False)
        if applyToOtherObjects:
            self.updateGroups = self.filterGroups.copy()
        else:
            self.updateGroups = set()
        if applyToStructures:
            self.updateCategs.add(invConst.categoryStarbase)
            self.updateCategs.add(invConst.categorySovereigntyStructure)
            self.updateCategs.add(invConst.categoryStructure)
        self.updateCategs.add(invConst.categoryStation)
        self.updateGroups.add(invConst.groupStargate)
        settings.user.ui.Set('linkedWeapons_groupsDict', {})

    def ChangeStateOrder(self, where, flag, idx):
        current = self.GetStateOrder(where)[:]
        while flag in current:
            current.remove(flag)

        if idx == -1:
            idx = len(current)
        current.insert(idx, flag)
        configName = GetOrderConfigName(where.lower())
        settings.user.overview.Set(configName, current)
        self.cachedStateSettings = {}
        self.NotifyOnStateSetupChange('flagOrder')

    def ChangeStateState(self, where, flag, true):
        current = self.GetStateStates(where)[:]
        while flag in current:
            current.remove(flag)

        if true:
            current.append(flag)
        configName = GetStateConfigName(where.lower())
        settings.user.overview.Set(configName, current)
        self.cachedStateSettings = {}
        self.NotifyOnStateSetupChange('flagState')

    def ChangeLabelOrder(self, oldidx, idx):
        labels = self.GetShipLabels()
        label = labels.pop(oldidx)
        if idx == -1:
            idx = len(labels)
        labels.insert(idx, label)
        settings.user.overview.Set(osConst.SETTINGS_SHIP_LABELS, labels)
        self.cachedStateSettings = {}
        sm.GetService('bracket').UpdateLabels()
        sm.ScatterEvent('OnOverviewLabelOrderChanged')

    def ChangeShipLabels(self, flag, isSelected):
        labels = self.GetShipLabels()
        flagType = flag[oConst.LABEL_TYPE]
        flag[oConst.LABEL_STATE] = isSelected
        for i in xrange(len(labels)):
            if labels[i][oConst.LABEL_TYPE] == flagType:
                labels[i] = flag
                break

        settings.user.overview.Set(osConst.SETTINGS_SHIP_LABELS, labels)
        self.cachedStateSettings = {}
        sm.GetService('bracket').UpdateLabels()
        sm.ScatterEvent('OnShipLabelsUpdated')

    def SetDefaultShipLabel(self, setting):
        hideCorpTickerDefault = sm.GetService('overviewPresetSvc').GetDefaultSettingValueFromName(osConst.SETTING_HIDE_CORP_TICKER, False)
        allLabels = self.GetAllShipLabels()
        defaults = {'default': (hideCorpTickerDefault, allLabels),
         'ally': (hideCorpTickerDefault, [ShipLabel(onState=1, preText=oConst.CHAR_NONE, labelType=oConst.LABEL_TYPE_PILOT, postText=oConst.CHAR_NONE).GetDict(),
                   ShipLabel(onState=1, preText=oConst.CHAR_SPACE + oConst.L_SQ_BRACKET, labelType=oConst.LABEL_TYPE_CORP, postText=oConst.CHAR_NONE).GetDict(),
                   ShipLabel(onState=1, preText=oConst.CHAR_COMMA, labelType=oConst.LABEL_TYPE_ALLIANCE, postText=oConst.CHAR_NONE).GetDict(),
                   ShipLabel(onState=1, preText=oConst.R_SQ_BRACKET, labelType=oConst.LABEL_TYPE_NONE, postText=oConst.CHAR_NONE).GetDict(),
                   ShipLabel(onState=0, preText=oConst.APOSTROPHE, labelType=oConst.LABEL_TYPE_SHIP_NAME, postText=oConst.APOSTROPHE).GetDict(),
                   ShipLabel(onState=0, preText=oConst.L_BRACKET, labelType=oConst.LABEL_TYPE_SHIP_TYPE, postText=oConst.R_BRACKET).GetDict()]),
         'corpally': (hideCorpTickerDefault, [ShipLabel(onState=1, preText=oConst.CHAR_SPACE + oConst.L_SQ_BRACKET, labelType=oConst.LABEL_TYPE_CORP, postText=oConst.R_SQ_BRACKET).GetDict(),
                       ShipLabel(onState=1, preText=oConst.CHAR_NONE, labelType=oConst.LABEL_TYPE_PILOT, postText=oConst.CHAR_NONE).GetDict(),
                       ShipLabel(onState=1, preText=oConst.CODE_LT, labelType=oConst.LABEL_TYPE_ALLIANCE, postText=oConst.CODE_GT).GetDict(),
                       ShipLabel(onState=0, preText=oConst.APOSTROPHE, labelType=oConst.LABEL_TYPE_SHIP_NAME, postText=oConst.APOSTROPHE).GetDict(),
                       ShipLabel(onState=0, preText=oConst.L_BRACKET, labelType=oConst.LABEL_TYPE_SHIP_TYPE, postText=oConst.R_BRACKET).GetDict(),
                       ShipLabel(onState=0, preText=oConst.L_SQ_BRACKET, labelType=oConst.LABEL_TYPE_NONE, postText=oConst.R_SQ_BRACKET).GetDict()])}
        settings.user.overview.Set(osConst.SETTING_HIDE_CORP_TICKER, defaults.get(setting, 'default')[0])
        self.shipLabels = defaults.get(setting, 'default')[1]
        settings.user.overview.Set(osConst.SETTINGS_SHIP_LABELS, self.shipLabels)
        self.cachedStateSettings = {}
        sm.GetService('bracket').UpdateLabels()

    def NotifyOnStateSetupChange(self, reason):
        self.notifyStateChangeTimer = timerstuff.AutoTimer(1000, self._NotifyOnStateSetupChange, reason)

    def _NotifyOnStateSetupChange(self, reason):
        self.notifyStateChangeTimer = None
        sm.ScatterEvent('OnStateSetupChange', reason)

    @telemetry.ZONE_METHOD
    def CheckIfUpdateItem(self, slimItem):
        return getattr(slimItem, 'categoryID', None) in self.updateCategs or getattr(slimItem, 'groupID', None) in self.updateGroups

    @telemetry.ZONE_METHOD
    def CheckIfFilterItem(self, slimItem):
        return getattr(slimItem, 'categoryID', None) in self.filterCategs or getattr(slimItem, 'groupID', None) in self.filterGroups

    @telemetry.ZONE_METHOD
    def GetStates(self, itemID, flags):
        ret = []
        for flag in flags:
            if flag in self.exclusive:
                ret.append(itemID == self.exclusives.get(flag, 0))
                continue
            ret.append(self.states.get(flag, {}).get(itemID, 0))

        return ret

    def GetState(self, itemID, flag):
        if flag not in self.states:
            return False
        else:
            return itemID in self.states[flag]

    def GetStatesForFlag(self, flag):
        return self.states.get(flag, {}).keys()

    @telemetry.ZONE_METHOD
    def GetExclState(self, flag):
        return self.exclusives.get(flag, None)

    @telemetry.ZONE_METHOD
    def DoExclusive(self, itemID, flag, true, *args):
        excl = self.exclusives.get(flag, None)
        if true:
            if excl and excl != itemID:
                sm.ScatterEvent('OnStateChange', excl, flag, 0, *args)
            sm.ScatterEvent('OnStateChange', itemID, flag, 1, *args)
            self.exclusives[flag] = itemID
        else:
            sm.ScatterEvent('OnStateChange', itemID, flag, 0, *args)
            self.exclusives[flag] = None

    @telemetry.ZONE_METHOD
    def SetState(self, itemID, flag, value, *args):
        self.LogInfo('SetState', itemID, flag, value, *args)
        if flag in self.exclusive:
            self.DoExclusive(itemID, flag, value, *args)
            return
        states = self.states.get(flag, {})
        if value:
            states[itemID] = value
        elif itemID in states:
            del states[itemID]
        if states:
            self.states[flag] = states
        elif flag in self.states:
            del self.states[flag]
        self.LogInfo('Before OnStateChange', itemID, flag, value, *args)
        sm.ScatterEvent('OnStateChange', itemID, flag, value, *args)

    def ResetByFlag(self, flag):
        if flag not in self.states:
            return
        for itemID in self.states[flag].keys():
            sm.ScatterEvent('OnStateChange', itemID, flag, False)

        del self.states[flag]

    def DoBallClear(self, *etc):
        self.states = {}

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        if ball.id in self.exclusives.itervalues():
            for state in self.exclusive:
                if self.GetExclState(state) == ball.id:
                    self.SetState(ball.id, state, 0)

        if ball.id == session.shipid:
            return
        for stateDict in self.states.values():
            if ball.id in stateDict:
                del stateDict[ball.id]

    def GetAllShipLabels(self):
        return [ShipLabel(onState=1, preText=oConst.CHAR_NONE, labelType=oConst.LABEL_TYPE_SHIP_TYPE, postText=oConst.CHAR_SPACE).GetDict(),
         ShipLabel(onState=1, preText=oConst.CODE_LT, labelType=oConst.LABEL_TYPE_ALLIANCE, postText=oConst.CODE_GT).GetDict(),
         ShipLabel(onState=1, preText=oConst.L_SQ_BRACKET, labelType=oConst.LABEL_TYPE_CORP, postText=oConst.R_SQ_BRACKET).GetDict(),
         ShipLabel(onState=1, preText=oConst.CHAR_SPACE, labelType=oConst.LABEL_TYPE_PILOT, postText=oConst.CHAR_SPACE).GetDict(),
         ShipLabel(onState=0, preText=oConst.APOSTROPHE, labelType=oConst.LABEL_TYPE_SHIP_NAME, postText=oConst.APOSTROPHE).GetDict(),
         ShipLabel(onState=0, preText=oConst.L_SQ_BRACKET, labelType=None, postText=oConst.CHAR_NONE).GetDict()]

    def GetShipLabels(self):
        if not getattr(self, 'shipLabels', None):
            self.shipLabels = settings.user.overview.Get(osConst.SETTINGS_SHIP_LABELS, None) or self.GetAllShipLabels()
        return self.shipLabels

    @telemetry.ZONE_METHOD
    def GetIconAndBackgroundFlags(self, slimItem):
        if slimItem is None:
            return (0, 0)
        flag = self.CheckStates(slimItem, 'flag')
        background = self.CheckStates(slimItem, 'background')
        return (flag or 0, background or 0)

    @telemetry.ZONE_METHOD
    def CheckStates(self, slimItem, what):
        if slimItem is None:
            return
        if not (slimItem.ownerID in [None, invConst.ownerSystem] or idCheckers.IsNPC(slimItem.ownerID)):
            relationships = self._GetRelationship(slimItem)
        else:
            relationships = None
        for functionName in self.GetActiveStateOrderFunctionNames(what):
            fullFunctionName = 'Check' + functionName
            checkFunction = getattr(self, fullFunctionName, None)
            if checkFunction:
                if checkFunction(slimItem, relationships):
                    return getattr(state, 'flag' + functionName, None)

    @telemetry.ZONE_METHOD
    def CheckFilteredFlagState(self, slimItem, excludedFlags = ()):
        if slimItem is None:
            return 0
        if not (slimItem.ownerID in [None, invConst.ownerSystem] or idCheckers.IsNPC(slimItem.ownerID)):
            relationships = self._GetRelationship(slimItem)
        else:
            relationships = None
        for flag in self.GetActiveStateOrder('flag'):
            if flag in excludedFlags:
                continue
            flagName = self.GetStateProps(flag).label
            fullFunctionName = 'Check' + flagName
            checkFunction = getattr(self, fullFunctionName, None)
            if checkFunction:
                if checkFunction(slimItem, relationships):
                    return getattr(state, 'flag' + flagName, 0)

        return 0

    @telemetry.ZONE_METHOD
    def _GetRelationship(self, item):
        allianceID = getattr(item, 'allianceID', None)
        ownerID = getattr(item, 'ownerID', None)
        corpID = getattr(item, 'corpID', None)
        return sm.GetService('addressbook').GetRelationship(ownerID, corpID, allianceID)

    @telemetry.ZONE_METHOD
    def IsStandingRelevant(self, slimItem):
        ownerID = slimItem.ownerID
        if ownerID is None or ownerID == invConst.ownerSystem or idCheckers.IsNPC(ownerID):
            return False
        return True

    @telemetry.ZONE_METHOD
    def CheckStandingHigh(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if not self.IsStandingRelevant(slimItem):
            return False
        if relationships is NORELATIONSHIP_SENTINEL:
            relationships = self._GetRelationship(slimItem)
        if not relationships:
            return False
        if getattr(slimItem, 'categoryID', None) not in invConst.stateFilteredCategories:
            return False
        if self.IfAnyRelations(IsHighStanding, self.GetAllRelationshipGroups(relationships)):
            return True
        return False

    @telemetry.ZONE_METHOD
    def CheckStandingGood(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if not self.IsStandingRelevant(slimItem):
            return False
        if relationships is NORELATIONSHIP_SENTINEL:
            relationships = self._GetRelationship(slimItem)
        if not relationships:
            return False
        if getattr(slimItem, 'categoryID', None) not in invConst.stateFilteredCategories:
            return False
        if self.IfAnyRelations(IsGoodStanding, self.GetAllRelationshipGroups(relationships)):
            return True
        return False

    @telemetry.ZONE_METHOD
    def CheckStandingNeutral(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if not self.IsStandingRelevant(slimItem):
            return False
        if relationships is NORELATIONSHIP_SENTINEL:
            relationships = self._GetRelationship(slimItem)
        if not relationships:
            return False
        if getattr(slimItem, 'categoryID', None) not in invConst.stateFilteredCategories:
            return False
        if relationships.hasRelationship:
            if not self.IfAllRelations(IsNeutralStanding, self.GetAllRelationshipGroups(relationships)):
                return False
            if not self.CheckSamePlayerCorp(slimItem) and not self.CheckSameNpcCorp(slimItem) and not self.CheckSameAlliance(slimItem):
                return True
        return False

    @telemetry.ZONE_METHOD
    def CheckStandingBad(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if not self.IsStandingRelevant(slimItem):
            return False
        if relationships is NORELATIONSHIP_SENTINEL:
            relationships = self._GetRelationship(slimItem)
        if not relationships:
            return False
        if getattr(slimItem, 'categoryID', None) not in invConst.stateFilteredCategories:
            return False
        if self.IfAnyRelations(IsBadStanding, self.GetAllRelationshipGroups(relationships)):
            return True
        return False

    @telemetry.ZONE_METHOD
    def CheckStandingHorrible(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if not self.IsStandingRelevant(slimItem):
            return False
        if relationships is NORELATIONSHIP_SENTINEL:
            relationships = self._GetRelationship(slimItem)
        if not relationships:
            return False
        if getattr(slimItem, 'categoryID', None) not in invConst.stateFilteredCategories:
            return False
        if self.IfAnyRelations(IsHorribleStanding, self.GetAllRelationshipGroups(relationships)):
            return True
        return False

    def GetAllRelationshipGroups(self, relationships):
        ret = []
        ret.extend(self.GetAllianceRelationshipGroups(relationships))
        ret.extend(self.GetCorpRelationshipGroups(relationships))
        ret.extend(self.GetPersonalRelationshipGroups(relationships))
        return ret

    def GetAllianceRelationshipGroups(self, relationships):
        return (relationships.allianceToPers, relationships.allianceToCorp, relationships.allianceToAlliance)

    def GetCorpRelationshipGroups(self, relationships):
        return (relationships.corpToPers, relationships.corpToCorp, relationships.corpToAlliance)

    def GetPersonalRelationshipGroups(self, relationships):
        return (relationships.persToPers, relationships.persToCorp, relationships.persToAlliance)

    def IfAnyRelations(self, standingCheck, relationshipGroup):
        return any((standingCheck(relationship) for relationship in relationshipGroup))

    def IfAllRelations(self, standingCheck, relationshipGroup):
        return all((standingCheck(relationship) for relationship in relationshipGroup))

    @telemetry.ZONE_METHOD
    def CheckSamePlayerCorp(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckSamePlayerCorp', slimItem)
        return not IsNPCCorporation(session.corpid) and self._CheckInSameCorp(slimItem)

    @telemetry.ZONE_METHOD
    def CheckSameNpcCorp(self, slimItem, *args):
        if self.logme:
            self.LogInfo('Tactical::CheckSameNpcCorp', slimItem)
        return IsNPCCorporation(session.corpid) and self._CheckInSameCorp(slimItem)

    def _CheckInSameCorp(self, slimItem):
        return getattr(slimItem, 'corpID', None) == session.corpid and getattr(slimItem, 'categoryID', None) in invConst.stateFilteredCategories

    @telemetry.ZONE_METHOD
    def CheckSameAlliance(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckSameAlliance', slimItem)
        return session.allianceid and getattr(slimItem, 'allianceID', None) == session.allianceid and getattr(slimItem, 'categoryID', None) in invConst.stateFilteredCategories

    @telemetry.ZONE_METHOD
    def CheckSameFleet(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckSameFleet', slimItem)
        if session.fleetid:
            charID = self.GetCharIDForSlimItem(slimItem)
            if charID or getattr(slimItem, 'categoryID', None) in DRONES_AND_FIGHTERS:
                if charID is None:
                    charID = slimItem.ownerID
                return sm.GetService('fleet').IsMember(charID)
        return 0

    @telemetry.ZONE_METHOD
    def CheckSameMilitia(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckSameMilitia', slimItem)
        if session.warfactionid:
            if (getattr(slimItem, 'charID', None) or getattr(slimItem, 'categoryID', None) in CATEGORIES_WITH_WARFACTIONID) and getattr(slimItem, 'corpID', None):
                slimItemWarFactionID = getattr(slimItem, 'warFactionID', None)
                if slimItemWarFactionID is not None:
                    return IsMyFwFaction(slimItemWarFactionID)
        return 0

    @telemetry.ZONE_METHOD
    def CheckAgentInteractable(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckAgentInteractable', slimItem)
        return getattr(slimItem, 'groupID', None) == invConst.groupAgentsinSpace

    @telemetry.ZONE_METHOD
    def CheckIsWanted(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckIsWanted', slimItem)
        return self.bountySvc.QuickHasBounty(slimItem)

    @telemetry.ZONE_METHOD
    def CheckHasKillRight(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckIsWanted', slimItem)
        charID = self.GetCharIDForSlimItem(slimItem)
        if not charID:
            return False
        return self.bountySvc.QuickHasKillRight(slimItem)

    @telemetry.ZONE_METHOD
    def CheckAtWarCanFight(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckAtWarCanFight', slimItem)
        ownerId = getattr(slimItem, 'allianceID', None) or getattr(slimItem, 'corpID', None)
        if ownerId:
            if ownerId not in self.atWar:
                self.atWar[ownerId] = sm.StartService('war').GetRelationship(ownerId)
            return self.atWar[ownerId] == warConst.warRelationshipAtWarCanFight
        else:
            return 0

    @telemetry.ZONE_METHOD
    def CheckAlliesAtWar(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckAlliesAtWar', slimItem)
        ownerID = getattr(slimItem, 'allianceID', None) or getattr(slimItem, 'corpID', None)
        if ownerID is not None:
            if ownerID not in self.alliesAtWar:
                self.alliesAtWar[ownerID] = sm.GetService('war').GetRelationship(ownerID)
            return self.alliesAtWar[ownerID] == warConst.warRelationshipAlliesAtWar
        return 0

    @telemetry.ZONE_METHOD
    def CheckAtWarMilitia(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckAtWarMilitia', slimItem)
        if session.warfactionid and getattr(slimItem, 'warFactionID', None):
            warKey = (slimItem.warFactionID, session.warfactionid)
            if warKey not in self.atWar:
                self.atWar[warKey] = IsMyCombatEnemyFaction(slimItem.warFactionID)
            return self.atWar[warKey] == True
        return 0

    @telemetry.ZONE_METHOD
    def CheckDangerous(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckDangerous', slimItem)
        if self.GetCharIDForSlimItem(slimItem) and -0.1 > (getattr(slimItem, 'securityStatus', None) or 0) >= appConst.outlawSecurityStatus:
            return 1
        return 0

    @telemetry.ZONE_METHOD
    def CheckOutlaw(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if self.logme:
            self.LogInfo('Tactical::CheckOutlaw', slimItem)
        if self.GetCharIDForSlimItem(slimItem) and eveCfg.IsOutlawStatus(getattr(slimItem, 'securityStatus', None) or 0):
            return 1
        return 0

    @telemetry.ZONE_METHOD
    def CheckWreckEmpty(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        return getattr(slimItem, 'groupID', None) == invConst.groupWreck and slimItem.isEmpty

    @telemetry.ZONE_METHOD
    def CheckNoStanding(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        if relationships is NORELATIONSHIP_SENTINEL:
            relationships = self._GetRelationship(slimItem)
        return (not relationships or not relationships.hasRelationship) and idCheckers.IsCharacter(getattr(slimItem, 'ownerID', None)) and getattr(slimItem, 'categoryID', None) in invConst.stateFilteredCategories

    @telemetry.ZONE_METHOD
    def CheckWreckViewed(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        return sm.GetService('wreck').IsViewedWreck(slimItem.itemID)

    @telemetry.ZONE_METHOD
    def CheckCriminal(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        charID = self.GetCharIDForSlimItem(slimItem)
        if charID is not None:
            return sm.GetService('crimewatchSvc').IsCriminal(charID)
        return False

    @telemetry.ZONE_METHOD
    def CheckSuspect(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        charID = self.GetCharIDForSlimItem(slimItem)
        if charID is not None:
            return sm.GetService('crimewatchSvc').IsSuspect(charID)
        return False

    @telemetry.ZONE_METHOD
    def CheckDisapproval(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        charID = self.GetCharIDForSlimItem(slimItem)
        if charID is not None:
            return sm.GetService('crimewatchSvc').IsDisapproved(charID)
        return False

    def CheckLimitedEngagement(self, slimItem, relationships = NORELATIONSHIP_SENTINEL):
        charID = self.GetCharIDForSlimItem(slimItem)
        if charID is not None:
            return sm.GetService('crimewatchSvc').HasLimitedEngagmentWith(charID)
        return False

    def CheckMultiSelected(self, slimItem):
        return slimItem.itemID in self.states[state.multiSelected]

    def GetCharIDForSlimItem(self, slimItem):
        charID = getattr(slimItem, 'charID', None)
        if charID and self.IsSlimItemStructure(slimItem):
            return
        return charID

    def IsSlimItemStructure(self, slimItem):
        return getattr(slimItem, 'categoryID', None) == appConst.categoryStructure


def GetNPCGroups():
    npcGroups = {GetByLabel('UI/Services/State/NonPlayerCharacter/Generic'): {GetByLabel('UI/Services/State/NonPlayerCharacter/Pirate'): [invConst.groupAsteroidAngelCartelBattleCruiser,
                                                                                                                              invConst.groupAsteroidAngelCartelBattleship,
                                                                                                                              invConst.groupAsteroidAngelCartelCruiser,
                                                                                                                              invConst.groupAsteroidAngelCartelDestroyer,
                                                                                                                              invConst.groupAsteroidAngelCartelFrigate,
                                                                                                                              invConst.groupAsteroidAngelCartelHauler,
                                                                                                                              invConst.groupAsteroidAngelCartelOfficer,
                                                                                                                              invConst.groupAsteroidBloodRaidersBattleCruiser,
                                                                                                                              invConst.groupAsteroidBloodRaidersBattleship,
                                                                                                                              invConst.groupAsteroidBloodRaidersCruiser,
                                                                                                                              invConst.groupAsteroidBloodRaidersDestroyer,
                                                                                                                              invConst.groupAsteroidBloodRaidersFrigate,
                                                                                                                              invConst.groupAsteroidBloodRaidersHauler,
                                                                                                                              invConst.groupAsteroidBloodRaidersOfficer,
                                                                                                                              invConst.groupAsteroidGuristasBattleCruiser,
                                                                                                                              invConst.groupAsteroidGuristasBattleship,
                                                                                                                              invConst.groupAsteroidGuristasCruiser,
                                                                                                                              invConst.groupAsteroidGuristasDestroyer,
                                                                                                                              invConst.groupAsteroidGuristasFrigate,
                                                                                                                              invConst.groupAsteroidGuristasHauler,
                                                                                                                              invConst.groupAsteroidGuristasOfficer,
                                                                                                                              invConst.groupAsteroidSanshasNationBattleCruiser,
                                                                                                                              invConst.groupAsteroidSanshasNationBattleship,
                                                                                                                              invConst.groupAsteroidSanshasNationCruiser,
                                                                                                                              invConst.groupAsteroidSanshasNationDestroyer,
                                                                                                                              invConst.groupAsteroidSanshasNationFrigate,
                                                                                                                              invConst.groupAsteroidSanshasNationHauler,
                                                                                                                              invConst.groupAsteroidSanshasNationOfficer,
                                                                                                                              invConst.groupAsteroidSerpentisBattleCruiser,
                                                                                                                              invConst.groupAsteroidSerpentisBattleship,
                                                                                                                              invConst.groupAsteroidSerpentisCruiser,
                                                                                                                              invConst.groupAsteroidSerpentisDestroyer,
                                                                                                                              invConst.groupAsteroidSerpentisFrigate,
                                                                                                                              invConst.groupAsteroidSerpentisHauler,
                                                                                                                              invConst.groupAsteroidSerpentisOfficer,
                                                                                                                              invConst.groupDeadspaceAngelCartelBattleCruiser,
                                                                                                                              invConst.groupDeadspaceAngelCartelBattleship,
                                                                                                                              invConst.groupDeadspaceAngelCartelCruiser,
                                                                                                                              invConst.groupDeadspaceAngelCartelDestroyer,
                                                                                                                              invConst.groupDeadspaceAngelCartelFrigate,
                                                                                                                              invConst.groupDeadspaceBloodRaidersBattleCruiser,
                                                                                                                              invConst.groupDeadspaceBloodRaidersBattleship,
                                                                                                                              invConst.groupDeadspaceBloodRaidersCruiser,
                                                                                                                              invConst.groupDeadspaceBloodRaidersDestroyer,
                                                                                                                              invConst.groupDeadspaceBloodRaidersFrigate,
                                                                                                                              invConst.groupDeadspaceGuristasBattleCruiser,
                                                                                                                              invConst.groupDeadspaceGuristasBattleship,
                                                                                                                              invConst.groupDeadspaceGuristasCruiser,
                                                                                                                              invConst.groupDeadspaceGuristasDestroyer,
                                                                                                                              invConst.groupDeadspaceGuristasFrigate,
                                                                                                                              invConst.groupDeadspaceSanshasNationBattleCruiser,
                                                                                                                              invConst.groupDeadspaceSanshasNationBattleship,
                                                                                                                              invConst.groupDeadspaceSanshasNationCruiser,
                                                                                                                              invConst.groupDeadspaceSanshasNationDestroyer,
                                                                                                                              invConst.groupDeadspaceSanshasNationFrigate,
                                                                                                                              invConst.groupDeadspaceSerpentisBattleCruiser,
                                                                                                                              invConst.groupDeadspaceSerpentisBattleship,
                                                                                                                              invConst.groupDeadspaceSerpentisCruiser,
                                                                                                                              invConst.groupDeadspaceSerpentisDestroyer,
                                                                                                                              invConst.groupDeadspaceSerpentisFrigate,
                                                                                                                              invConst.groupDeadspaceSleeperSleeplessPatroller,
                                                                                                                              invConst.groupDeadspaceSleeperSleeplessSentinel,
                                                                                                                              invConst.groupDeadspaceSleeperSleeplessDefender,
                                                                                                                              invConst.groupDeadspaceSleeperAwakenedPatroller,
                                                                                                                              invConst.groupDeadspaceSleeperAwakenedSentinel,
                                                                                                                              invConst.groupDeadspaceSleeperAwakenedDefender,
                                                                                                                              invConst.groupDeadspaceSleeperEmergentPatroller,
                                                                                                                              invConst.groupDeadspaceSleeperEmergentSentinel,
                                                                                                                              invConst.groupDeadspaceSleeperEmergentDefender,
                                                                                                                              invConst.groupAsteroidAngelCartelCommanderBattleCruiser,
                                                                                                                              invConst.groupAsteroidAngelCartelCommanderCruiser,
                                                                                                                              invConst.groupAsteroidAngelCartelCommanderDestroyer,
                                                                                                                              invConst.groupAsteroidAngelCartelCommanderFrigate,
                                                                                                                              invConst.groupAsteroidBloodRaidersCommanderBattleCruiser,
                                                                                                                              invConst.groupAsteroidBloodRaidersCommanderCruiser,
                                                                                                                              invConst.groupAsteroidBloodRaidersCommanderDestroyer,
                                                                                                                              invConst.groupAsteroidBloodRaidersCommanderFrigate,
                                                                                                                              invConst.groupAsteroidGuristasCommanderBattleCruiser,
                                                                                                                              invConst.groupAsteroidGuristasCommanderCruiser,
                                                                                                                              invConst.groupAsteroidGuristasCommanderDestroyer,
                                                                                                                              invConst.groupAsteroidGuristasCommanderFrigate,
                                                                                                                              invConst.groupAsteroidRogueDroneBattleCruiser,
                                                                                                                              invConst.groupAsteroidRogueDroneBattleship,
                                                                                                                              invConst.groupAsteroidRogueDroneCruiser,
                                                                                                                              invConst.groupAsteroidRogueDroneDestroyer,
                                                                                                                              invConst.groupAsteroidRogueDroneFrigate,
                                                                                                                              invConst.groupAsteroidRogueDroneHauler,
                                                                                                                              invConst.groupAsteroidRogueDroneSwarm,
                                                                                                                              invConst.groupAsteroidRogueDroneOfficer,
                                                                                                                              invConst.groupAsteroidSanshasNationCommanderBattleCruiser,
                                                                                                                              invConst.groupAsteroidSanshasNationCommanderCruiser,
                                                                                                                              invConst.groupAsteroidSanshasNationCommanderDestroyer,
                                                                                                                              invConst.groupAsteroidSanshasNationCommanderFrigate,
                                                                                                                              invConst.groupAsteroidSerpentisCommanderBattleCruiser,
                                                                                                                              invConst.groupAsteroidSerpentisCommanderCruiser,
                                                                                                                              invConst.groupAsteroidSerpentisCommanderDestroyer,
                                                                                                                              invConst.groupAsteroidSerpentisCommanderFrigate,
                                                                                                                              invConst.groupDeadspaceRogueDroneBattleCruiser,
                                                                                                                              invConst.groupDeadspaceRogueDroneBattleship,
                                                                                                                              invConst.groupDeadspaceRogueDroneCruiser,
                                                                                                                              invConst.groupDeadspaceRogueDroneDestroyer,
                                                                                                                              invConst.groupDeadspaceRogueDroneFrigate,
                                                                                                                              invConst.groupDeadspaceRogueDroneSwarm,
                                                                                                                              invConst.groupDeadspaceOverseerFrigate,
                                                                                                                              invConst.groupDeadspaceOverseerCruiser,
                                                                                                                              invConst.groupDeadspaceOverseerBattleship,
                                                                                                                              invConst.groupAsteroidRogueDroneCommanderFrigate,
                                                                                                                              invConst.groupAsteroidRogueDroneCommanderDestroyer,
                                                                                                                              invConst.groupAsteroidRogueDroneCommanderCruiser,
                                                                                                                              invConst.groupAsteroidRogueDroneCommanderBattleCruiser,
                                                                                                                              invConst.groupAsteroidRogueDroneCommanderBattleship,
                                                                                                                              invConst.groupAsteroidAngelCartelCommanderBattleship,
                                                                                                                              invConst.groupAsteroidBloodRaidersCommanderBattleship,
                                                                                                                              invConst.groupAsteroidGuristasCommanderBattleship,
                                                                                                                              invConst.groupAsteroidSanshasNationCommanderBattleship,
                                                                                                                              invConst.groupAsteroidSerpentisCommanderBattleship,
                                                                                                                              invConst.groupMissionAmarrEmpireCarrier,
                                                                                                                              invConst.groupMissionCaldariStateCarrier,
                                                                                                                              invConst.groupMissionGallenteFederationCarrier,
                                                                                                                              invConst.groupMissionMinmatarRepublicCarrier,
                                                                                                                              invConst.groupMissionFighterDrone,
                                                                                                                              invConst.groupMissionGenericFreighters,
                                                                                                                              invConst.groupInvasionSanshaNationBattleship,
                                                                                                                              invConst.groupInvasionSanshaNationCapital,
                                                                                                                              invConst.groupInvasionSanshaNationCruiser,
                                                                                                                              invConst.groupInvasionSanshaNationFrigate,
                                                                                                                              invConst.groupInvasionSanshaNationIndustrial,
                                                                                                                              invConst.groupGhostSitesAngelCartelCruiser,
                                                                                                                              invConst.groupGhostSitesBloodRaidersCruiser,
                                                                                                                              invConst.groupGhostSitesGuristasCruiser,
                                                                                                                              invConst.groupGhostSitesSanshasCruiser,
                                                                                                                              invConst.groupGhostSitesSerpentisCruiser,
                                                                                                                              invConst.groupGhostSitesMordusLegion],
                                                                  GetByLabel('UI/Services/State/NonPlayerCharacter/Mission'): [invConst.groupMissionDrone,
                                                                                                                               invConst.groupStorylineBattleship,
                                                                                                                               invConst.groupStorylineFrigate,
                                                                                                                               invConst.groupStorylineCruiser,
                                                                                                                               invConst.groupStorylineMissionBattleship,
                                                                                                                               invConst.groupStorylineMissionFrigate,
                                                                                                                               invConst.groupStorylineMissionCruiser,
                                                                                                                               invConst.groupMissionGenericBattleships,
                                                                                                                               invConst.groupMissionGenericCruisers,
                                                                                                                               invConst.groupMissionGenericFrigates,
                                                                                                                               invConst.groupMissionThukkerBattlecruiser,
                                                                                                                               invConst.groupMissionThukkerBattleship,
                                                                                                                               invConst.groupMissionThukkerCruiser,
                                                                                                                               invConst.groupMissionThukkerDestroyer,
                                                                                                                               invConst.groupMissionThukkerFrigate,
                                                                                                                               invConst.groupMissionThukkerOther,
                                                                                                                               invConst.groupMissionGenericBattleCruisers,
                                                                                                                               invConst.groupMissionGenericDestroyers],
                                                                  GetByLabel('UI/Services/State/NonPlayerCharacter/Police'): [invConst.groupPoliceDrone],
                                                                  GetByLabel('UI/Services/State/NonPlayerCharacter/Concord'): [invConst.groupConcordDrone],
                                                                  GetByLabel('UI/Services/State/NonPlayerCharacter/Customs'): [invConst.groupCustomsOfficial],
                                                                  GetByLabel('UI/Services/State/NonPlayerCharacter/FactionNavy'): [invConst.groupFactionDrone]}}
    return npcGroups
