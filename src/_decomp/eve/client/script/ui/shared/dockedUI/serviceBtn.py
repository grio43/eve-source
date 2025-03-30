#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\serviceBtn.py
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from evestations.standingsrestriction import get_station_standings_restriction
from localization import GetByLabel

class StationServiceBtn(ButtonIcon):

    def __init__(self, serviceInfo, **kwargs):
        self.cmdStr = serviceInfo.command
        self.maskStationServiceIDs = serviceInfo.stationServiceIDs
        self.serviceID = serviceInfo.serviceID
        self.serviceStatus = GetByLabel('UI/Station/Lobby/Enabled')
        self.serviceEnabled = True
        self.disableIfServiceUnavailable = serviceInfo.disableButtonIfNotAvailable
        self.displayName = serviceInfo.label
        self.standingRestriction = None
        if hasattr(serviceInfo, 'iconID'):
            texturePath = serviceInfo.iconID
        else:
            texturePath = serviceInfo.texturePath
        self.standingsRestriction = None
        for serviceID in serviceInfo.stationServiceIDs:
            standingsRestriction = get_station_standings_restriction(serviceID, session.stationid, session.charid)
            if standingsRestriction:
                self.standingsRestriction = standingsRestriction
                break

        super(StationServiceBtn, self).__init__(texturePath=texturePath, **kwargs)

    def LoadTooltipPanel(self, panel, owner, *args):
        panel.LoadGeneric3ColumnTemplate()
        command = uicore.cmd.commandMap.GetCommandByName(self.cmdStr)
        panel.AddCommandTooltip(command)
        if not self.serviceEnabled:
            panel.AddLabelMedium(text=self.serviceStatus, color=eveColor.WARNING_ORANGE[:3], bold=True, colSpan=panel.columns)
        if self.standingsRestriction:
            panel.AddLabelMedium(text=GetByLabel('UI/Standings/Restricted', **self.standingsRestriction), color=eveColor.WARNING_ORANGE[:3], colSpan=panel.columns, wrapWidth=200)

    def UpdateState(self, isEnabled):
        if not isEnabled:
            self._SetDisabled(statusMessage=GetByLabel('UI/Station/Lobby/Disabled'))
        elif self.standingsRestriction:
            self._SetDisabled(statusMessage=GetByLabel('UI/Station/Lobby/Restricted'))
        else:
            self._SetEnabled()

    def _SetDisabled(self, statusMessage):
        if self.disableIfServiceUnavailable:
            self.Disable()
        self.serviceEnabled = False
        self.serviceStatus = statusMessage

    def _SetEnabled(self):
        self.Enable()
        self.serviceEnabled = True
        self.serviceStatus = GetByLabel('UI/Station/Lobby/Enabled')
