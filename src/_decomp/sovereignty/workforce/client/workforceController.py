#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\workforce\client\workforceController.py
import eveicon
from evelink.client import location_link
from localization import GetByLabel
from signals import Signal
from sovereignty.client.quasarCallWrapper import DATA_NOT_AVAILABLE
from sovereignty.client.sovHub.hubUtil import GetTexturePathForWorkforceMode
from sovereignty.workforce import workforceConst

class WorkforceController(object):

    def __init__(self, sovHubID, quasarCallWrapper, solarSystemID):
        self._sovHubID = sovHubID
        self._solarSystemID = solarSystemID
        self.quasarCallWrapper = quasarCallWrapper
        self._currentConfig = None
        self._currentState = None
        self.on_workforce_changed = Signal(signalName='on_workforce_changed')

    @property
    def sovHubID(self):
        return self._sovHubID

    @property
    def solarSystemID(self):
        return self._solarSystemID

    def GetModeComboOptions(self):
        options = workforceConst.LABELPATH_BY_MODE.copy()
        options.pop(workforceConst.MODE_IDLE)
        return [ (GetByLabel(labelPath), mode) for mode, labelPath in options.iteritems() ]

    def GetWorkforceTextsAndTexturePath(self):
        workforceConfig = self.workforceConfiguration
        if workforceConfig == DATA_NOT_AVAILABLE:
            return (DATA_NOT_AVAILABLE, False, eveicon.workforce)
        workforceMode = workforceConfig.get_mode()
        labelPath = workforceConst.LABELPATH_BY_MODE.get(workforceMode)
        texturePath = GetTexturePathForWorkforceMode(workforceMode)
        if labelPath:
            return (GetByLabel(labelPath, True), True, texturePath)
        return (GetByLabel('UI/Sovereignty/SovHub/UnknownWorkforceMode'), False, texturePath)

    @property
    def workforceConfiguration(self):
        if self._currentConfig is None:
            result = self.quasarCallWrapper.GetWorkforceConfiguration(self._sovHubID)
            if result == DATA_NOT_AVAILABLE:
                return DATA_NOT_AVAILABLE
            self._currentConfig = result
        return self._currentConfig

    @property
    def workforceState(self):
        if self._currentState is None:
            result = self.quasarCallWrapper.GetWorkforceState(self._sovHubID)
            if result == DATA_NOT_AVAILABLE:
                return DATA_NOT_AVAILABLE
            self._currentState = result
        return self._currentState

    @workforceState.setter
    def workforceState(self, value):
        self._currentState = value

    def UpdateWorkforceConfiguration(self, newConfig):
        self._currentConfig = newConfig
        self.on_workforce_changed()

    def UpdateWorkforceState(self, newState):
        self._currentState = newState
        self.on_workforce_changed()

    def SetWorkforceConfiguration(self, newConfig):
        result = self.quasarCallWrapper.SaveWorkforceConfiguration(self._sovHubID, newConfig)
        if result == DATA_NOT_AVAILABLE:
            print 'failed to set workforce'
            return
        self._currentConfig = newConfig
        self._currentState = None
        self.on_workforce_changed()
        sm.ScatterEvent('OnSovHubMarkersChanged')

    def GetWorkforceTransportDesc(self):
        workforceConfiguration = self.workforceConfiguration
        workforceState = self.workforceState
        if workforceConfiguration == DATA_NOT_AVAILABLE or workforceState == DATA_NOT_AVAILABLE:
            return ''
        mode = workforceConfiguration.get_mode()
        if mode == workforceConst.MODE_IDLE:
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/WorkforceTransportInactive')
        if mode == workforceConst.MODE_IMPORT:
            importState = workforceState.import_state
            amount = 0
            for iSystemID, iAmount in importState.amount_by_source_system_id.iteritems():
                amount += iAmount

            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/WorkforceTransportImport', amount=amount, solarSystemNames='')
        if mode == workforceConst.MODE_EXPORT:
            exportConfig = workforceConfiguration.export_configuration
            configDestID = exportConfig.destination_system_id
            exportState = workforceState.export_state
            stateAmount = exportState.amount
            stateDestID = exportState.destination_system_id
            if stateDestID:
                systemName = location_link(stateDestID)
                return GetByLabel('UI/Sovereignty/SovHub/Upgrades/WorkforceTransportExport', amount=stateAmount, solarSystemName=systemName)
            elif configDestID:
                systemName = location_link(configDestID)
                configAmount = exportConfig.amount
                return GetByLabel('UI/Sovereignty/SovHub/Upgrades/WorkforceTransportExportNoConnection', amount=configAmount, solarSystemName=systemName)
            else:
                return GetByLabel('UI/Sovereignty/SovHub/Upgrades/WorkforceTransportExportNotConfigured', amount=stateAmount)
        if mode == workforceConst.MODE_TRANSIT:
            return GetByLabel('UI/Sovereignty/SovHub/Upgrades/WorkforceTransportTransit')

    def GetWorkforceImportSystems(self):
        workforceConfiguration = self.workforceConfiguration
        workforceState = self.workforceState
        if workforceConfiguration == DATA_NOT_AVAILABLE or workforceState == DATA_NOT_AVAILABLE:
            return []
        mode = workforceConfiguration.get_mode()
        if mode == workforceConst.MODE_IMPORT:
            importConfig = workforceConfiguration.import_configuration
            importState = workforceState.import_state
            source_system_ids = importConfig.source_system_ids.copy()
            systemNameList = []
            for iSystemID, iAmount in importState.amount_by_source_system_id.iteritems():
                systemName = location_link(iSystemID)
                source_system_ids.discard(iSystemID)
                systemNameList.append((systemName, iAmount))

            for ssID in source_system_ids:
                systemNameList.append((location_link(ssID), None))

            return systemNameList
        return []

    def GetCurrentMode(self):
        workforceConfiguration = self.workforceConfiguration
        if workforceConfiguration == DATA_NOT_AVAILABLE:
            return ''
        return workforceConfiguration.get_mode()

    def GetImportedWorkforceFromState(self):
        workforceState = self.workforceState
        if workforceState.get_mode() == workforceConst.MODE_IMPORT:
            return sum(workforceState.import_state.amount_by_source_system_id.itervalues())
        return 0

    def GetExportedWorkforceFromState(self):
        workforceState = self.workforceState
        if workforceState.get_mode() == workforceConst.MODE_EXPORT:
            return workforceState.export_state.amount
        return 0

    def GetNetworkableHubs(self):
        networkableHubs = self.quasarCallWrapper.GetNetworkableHubs(self.sovHubID)
        return networkableHubs

    def GetSystemOptions(self, inImportingMode, otherSelectedSystems = ()):
        networkableHubs = self.GetNetworkableHubs()
        return self.GetSystemOptionsFromNetworkableHubs(inImportingMode, otherSelectedSystems, networkableHubs)

    def GetSystemOptionsFromNetworkableHubs(self, inImportingMode, otherSelectedSystems, networkableHubs):
        otherSelectedSystems = otherSelectedSystems or ()
        if networkableHubs == DATA_NOT_AVAILABLE:
            return []
        solarSystemIDs = [ x.system_id for x in networkableHubs ]
        cfg.evelocations.Prime(solarSystemIDs)
        options = []
        for hub in networkableHubs:
            if self._FilterOutHub(hub, inImportingMode):
                continue
            if hub.system_id in otherSelectedSystems:
                continue
            text = cfg.evelocations.Get(hub.system_id).name
            options.append((text, hub.system_id))

        options.insert(0, (GetByLabel('UI/Sovereignty/SovHub/HubWnd/SectionACLNotSet'), None))
        return options

    def _FilterOutHub(self, networkedHub, inImportingMode):
        inExportingMode = not inImportingMode
        hubState = networkedHub.state
        if hubState.inactive or hubState.transit_state:
            return True
        if inImportingMode and hubState.import_state:
            return True
        if inExportingMode and hubState.export_state:
            return True
        if inImportingMode and hubState.export_state.destination_system_id and hubState.export_state.destination_system_id != self.solarSystemID:
            return True
        if inExportingMode and len(hubState.import_state.amount_by_source_system_id) >= 3:
            if self.solarSystemID not in hubState.import_state.amount_by_source_system_id:
                return True
        return False
