#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemap\workforceUtil.py
import eveicon
import telemetry
import uthread
from carbon.common.script.util.format import FmtAmt
from eve.client.script.ui import eveColor
from localization import GetByLabel
from sovereignty.client.sovHub.hubUtil import GetTexturePathForWorkforceMode
from sovereignty.workforce import workforceConst

def GetTexturePathAndColorFromMode(hubStateConfig):
    color = eveColor.SILVER_GREY
    config = hubStateConfig.hubConfig
    if config:
        currentMode = config.get_mode()
    else:
        currentMode = workforceConst.MODE_UNKNOWN
    if currentMode == workforceConst.MODE_UNKNOWN:
        texturePath = eveicon.difficulty
        return (texturePath, color)
    texturePath = GetTexturePathForWorkforceMode(currentMode)
    if currentMode == workforceConst.MODE_IMPORT:
        color = (191 / 255.0,
         0,
         207 / 255.0,
         1.0)
    elif currentMode == workforceConst.MODE_EXPORT:
        color = eveColor.FOCUS_BLUE
    elif currentMode == workforceConst.MODE_TRANSIT:
        color = eveColor.OMEGA_YELLOW
    return (texturePath, color)


@telemetry.ZONE_METHOD
def GetMySovHubsAndSystems(sovSvc):
    structuresPerSolarsystem = sovSvc.GetSovereigntyStructuresInfoForAlliance()
    tcuByItemID = {}
    hubsByItemID = {}
    solarSystemIDByItemID = {}
    for ssID, structureList in structuresPerSolarsystem.iteritems():
        for structure in structureList:
            if structure.typeID == const.typeInfrastructureHub:
                hubsByItemID[structure.itemID] = structure
                solarSystemIDByItemID[structure.itemID] = ssID
            elif structure.typeID == const.typeTerritorialClaimUnit:
                tcuByItemID[structure.itemID] = structure

    sovHubsByItemID = {itemID:hubInfo for itemID, hubInfo in hubsByItemID.iteritems() if itemID in tcuByItemID}
    solarSystemIDsWithSovHubs = {ssID for itemID, ssID in solarSystemIDByItemID.iteritems() if itemID in sovHubsByItemID}
    return (sovHubsByItemID, solarSystemIDsWithSovHubs)


@telemetry.ZONE_METHOD
def GetNetworkableHubsIfPossible(sovHubSvc, hubID, hubInfo):
    try:
        if hubInfo.corporationID != session.corpid:
            return None
        nHubs = sovHubSvc.GetNetworkableHubs(hubID)
        return (hubID, nHubs)
    except Exception as e:
        pass


@telemetry.ZONE_METHOD
def GetStateAndConfigByHubID(sovSvc, sovHubSvc):
    sovHubsByItemID, solarSystemIDs = GetMySovHubsAndSystems(sovSvc)
    if not sovHubsByItemID:
        return {}
    networkedHubByItemID = {}
    networkableCalls = [ (GetNetworkableHubsIfPossible, (sovHubSvc, hubID, hubInfo)) for hubID, hubInfo in sovHubsByItemID.iteritems() ]
    rets = uthread.parallel(networkableCalls)
    filteredRets = filter(None, rets)
    for hubID, nHubs in filteredRets:
        for nHub in nHubs:
            if nHub.hub_id in networkedHubByItemID:
                continue
            nHubInfo = sovHubsByItemID[nHub.hub_id]
            networkedHubByItemID[nHub.hub_id] = HubStateConfig(nHub.hub_id, nHub.system_id, nHubInfo.corporationID, nHub.state, nHub.configuration)

    for hubID, hubInfo in sovHubsByItemID.iteritems():
        if hubID in networkedHubByItemID:
            continue
        hubStateConfig = HubStateConfig(hubID, hubInfo.solarSystemID, hubInfo.corporationID)
        if hubInfo.corporationID == session.corpid:
            try:
                config = sovHubSvc.GetWorkforceConfiguration(hubID)
                hubStateConfig.hubConfig = config
                hubState = sovHubSvc.GetWorkforceState(hubID)
                hubStateConfig.hubState = hubState
            except Exception as e:
                pass

        networkedHubByItemID[hubID] = hubStateConfig

    return networkedHubByItemID


def GetOtherStateAndSystems(hubStateConfig):
    noResult = (None, None)
    hubState = hubStateConfig.hubState
    if hubState is None:
        return noResult
    hubStateMode = hubState.get_mode()
    if hubStateMode in (workforceConst.MODE_TRANSIT, workforceConst.MODE_IDLE):
        return noResult
    if hubStateMode == workforceConst.MODE_EXPORT:
        otherState = workforceConst.MODE_IMPORT
        if hubState.export_state.destination_system_id is None:
            return noResult
        solarSystemBsState = [hubState.export_state.destination_system_id]
    elif hubStateMode == workforceConst.MODE_IMPORT:
        otherState = workforceConst.MODE_EXPORT
        solarSystemBsState = list(hubState.import_state._amount_by_source_system_id.keys())
    else:
        return noResult
    return (otherState, solarSystemBsState)


def GetSystemsForConfigs(hubStateConfig):
    hubConfig = hubStateConfig.hubConfig
    if hubConfig is None:
        return
    hubConfigMode = hubConfig.get_mode()
    if hubConfigMode in (workforceConst.MODE_TRANSIT, workforceConst.MODE_IDLE):
        return
    elif hubConfigMode == workforceConst.MODE_EXPORT:
        if hubConfig.export_configuration.destination_system_id is None:
            return
        return [hubConfig.export_configuration.destination_system_id]
    elif hubConfigMode == workforceConst.MODE_IMPORT:
        return list(hubConfig.import_configuration.source_system_ids)
    else:
        return


class HubStateConfig(object):

    def __init__(self, hubID, systemID, corporationID, hubState = None, hubConfig = None):
        self.hubID = hubID
        self.solarSystemID = systemID
        self.corporationID = corporationID
        self.hubState = hubState
        self.hubConfig = hubConfig

    def GetConfigMode(self):
        if self.hubConfig is None:
            return workforceConst.MODE_UNKNOWN
        return self.hubConfig.get_mode()

    def IsConnected(self):
        configMode = self.GetConfigMode()
        if configMode is None:
            return False
        if configMode in (workforceConst.MODE_EXPORT, workforceConst.MODE_IMPORT):
            if not self.hubState:
                return False
            if configMode == workforceConst.MODE_EXPORT:
                return bool(self.hubState.export_state.destination_system_id)
            if configMode == workforceConst.MODE_IMPORT:
                return bool(self.hubState.import_state.amount_by_source_system_id)
        return True

    def GetImportExportInfoForTooltip(self):
        ret = []
        if self.hubConfig is None:
            return []
        if self.hubConfig.import_configuration:
            amtBySourceID = self.hubState.import_state.amount_by_source_system_id if self.hubState else {}
            for ssID in self.hubConfig.import_configuration.source_system_ids:
                if ssID in amtBySourceID:
                    opacity = 1.0
                    text = '%s (%s)' % (FmtAmt(amtBySourceID[ssID]), cfg.evelocations.Get(ssID).name)
                else:
                    opacity = 0.5
                    text = '- (%s)' % cfg.evelocations.Get(ssID).name
                ret.append([eveicon.link, opacity, text])

            while len(ret) < 3:
                ret.append([eveicon.link, 0.75, GetByLabel('UI/Sovereignty/FreeWorkforceImportSlot')])

        elif self.hubConfig.export_configuration:
            configDestID = self.hubConfig.export_configuration.destination_system_id
            configAmt = self.hubConfig.export_configuration.amount
            stateDestID = self.hubState.export_state.destination_system_id
            stateAmt = self.hubState.export_state.amount
            opacity = 1.0
            if stateDestID is None:
                opacity = 0.5
            destName = GetByLabel('UI/Sovereignty/WorkforceExportDestNotSet') if configDestID is None else cfg.evelocations.Get(configDestID).name
            if stateAmt == configAmt:
                amountText = FmtAmt(stateAmt)
            else:
                amountText = '%s / %s' % (FmtAmt(stateAmt), FmtAmt(configAmt))
            text = '%s (%s)' % (amountText, destName)
            ret.append([eveicon.link, opacity, text])
        return ret
