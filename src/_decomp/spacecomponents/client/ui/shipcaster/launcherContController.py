#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\ui\shipcaster\launcherContController.py
import gametime
import logging
import traceback
from carbon.common.script.util.format import FmtDate
from carbonui import TextColor
from eve.client.script.ui import eveColor
from eveformat import client as eveformat
from localization import GetByLabel
from shipcaster.landingPadUtil import GetMaxLandingPadLinks
from spacecomponents.common.componentConst import SHIPCASTER_LAUNCHER
logger = logging.getLogger(__name__)

class LauncherContController(object):

    def __init__(self, itemID, typeID):
        self._itemID = itemID
        self._typeID = typeID
        self.fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        self.fwAdvantageSvc = sm.GetService('fwAdvantageSvc')
        self.fwVictoryPointSvc = sm.GetService('fwVictoryPointSvc')

    def _GetHeaderStatusAndAdjacenyState(self, slotIdx):
        headerText = GetByLabel('UI/FactionWarfare/ShipcasterUnlinked')
        timeText = GetByLabel('UI/FactionWarfare/ShipcasterNoSystemLinked')
        adjacencyState = None
        headerColor = TextColor.SECONDARY
        timeColor = TextColor.DISABLED
        timeGlow = False
        noResults = (headerText,
         timeText,
         adjacencyState,
         headerColor,
         timeColor,
         timeGlow)
        shipcasterLauncherComponent = self._GetShipCasterComponent()
        if not shipcasterLauncherComponent:
            return noResults
        targetSystemID, startTime, endTime = shipcasterLauncherComponent.GetTargetSystemAndTimingsForSlot(slotIdx)
        if targetSystemID is None:
            return noResults
        headerColor = TextColor.NORMAL
        headerText = u'{systemName} {securityStatus}'.format(systemName=cfg.evelocations.Get(targetSystemID).name, securityStatus=eveformat.solar_system_security_status(targetSystemID))
        now = gametime.GetWallclockTime()
        timeText = ''
        isFirstSlot = slotIdx == 0
        if startTime > now:
            timeText = GetByLabel('UI/Inflight/ShipcasterCharging', timeLeft=FmtDate(startTime - gametime.GetWallclockTime(), 'ns'))
            if isFirstSlot:
                timeColor = TextColor.NORMAL
        elif endTime > now:
            timeText = GetByLabel('UI/Inflight/ShipcasterActive', timeLeft=FmtDate(endTime - gametime.GetWallclockTime(), 'ns'))
            if isFirstSlot:
                timeColor = eveColor.CRYO_BLUE
                timeGlow = True
        adjacencyState = self.fwWarzoneSvc.GetAdjacencyState(targetSystemID)
        return (headerText,
         timeText,
         adjacencyState,
         headerColor,
         timeColor,
         timeGlow)

    def GetTargetOccuppierAndNetScore(self):
        targetSystemID = self.GetNextTargetSystemID()
        if targetSystemID is None:
            return (None, None, None, None)
        occupationState = self.fwWarzoneSvc.GetOccupationState(targetSystemID)
        if occupationState is None:
            return (None, None, None, None)
        advantageState = self.fwAdvantageSvc.GetAdvantageState(targetSystemID)
        netScore = advantageState.GetNetAdvantageScore(occupationState.occupierID, occupationState.attackerID)
        advantageWinner = None
        if netScore > 0:
            advantageWinner = occupationState.occupierID
        elif netScore < 0:
            advantageWinner = occupationState.attackerID
        return (occupationState.occupierID,
         occupationState.attackerID,
         netScore,
         advantageWinner)

    def GetContestedInfo(self):
        targetSystemID = self.GetNextTargetSystemID()
        if targetSystemID is None:
            return
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(targetSystemID)
        return victoryPointState

    def GetNextTargetSystemID(self):
        shipcasterLauncherComponent = self._GetShipCasterComponent()
        if not shipcasterLauncherComponent:
            return None
        targetSystemID = shipcasterLauncherComponent.nextTargetSolarsystemID
        return targetSystemID

    def _GetShipCasterComponent(self):
        try:
            bp = sm.GetService('michelle').GetBallpark()
            shipcasterLauncherComponent = bp.componentRegistry.GetComponentForItem(self._itemID, SHIPCASTER_LAUNCHER)
            return shipcasterLauncherComponent
        except AttributeError:
            logger.warning('Errored while getting ShipcasterLauncher component - %s', traceback.format_exc())
        except KeyError:
            pass

    def GetTargetAndFactionForDashboard(self):
        targetSystemID = self.GetNextTargetSystemID()
        if not targetSystemID:
            return (None, None)
        occupationState = self.fwWarzoneSvc.GetOccupationState(targetSystemID)
        if occupationState is None:
            return (targetSystemID, None)
        if session.warfactionid in (occupationState.occupierID, occupationState.attackerID):
            return (targetSystemID, session.warfactionid)
        return (targetSystemID, occupationState.occupierID)

    def GetKillsInTheLastHour(self, solarSystemID):
        history = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, 1)
        killsBySolarSystemID = history.Index('solarSystemID')
        return len(killsBySolarSystemID.get(solarSystemID, []))

    def GetMaxTargets(self):
        maxTargetLinks = GetMaxLandingPadLinks(self._typeID)
        return maxTargetLinks
