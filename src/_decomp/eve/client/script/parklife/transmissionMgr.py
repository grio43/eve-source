#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\transmissionMgr.py
import sys
import carbonui.const as uiconst
import evelink
import localization
import log
from carbon.common.script.sys import service
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveEditPlainText, eveLabel
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.station.agents.agentTransmissionWindow import AgentTransmissionWindow
from fsdBuiltData.common.iconIDs import GetIconFile

class TransmissionSvc(service.Service):
    __guid__ = 'svc.transmission'
    __notifyevents__ = ['OnIncomingTransmission', 'OnIncomingAgentMessage']

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.delayedTransmission = None

    def Stop(self, stream):
        service.Service.Stop(self)
        self.Cleanup()

    def Cleanup(self):
        for each in uicore.layer.main.children[:]:
            if each.name == 'telecom':
                each.Close()

    def OnIncomingTransmission(self, transmission, isAgentMission = 0, *args):
        if transmission.header is not None:
            if isinstance(transmission.header, (int, long)):
                transmission.header = localization.GetByMessageID(transmission.header)
        if isinstance(transmission.text, (int, long)):
            transmission.text = localization.GetByMessageID(transmission.text)
        if transmission.header.startswith('[d]'):
            transmission.header = transmission.header[3:]
            self.delayedTransmission = transmission
        else:
            self.ShowTransmission(transmission)

    def ShowTransmission(self, transmission):
        wnd = Telecom.Open(transmission=transmission)
        if wnd:
            wnd.ShowMessage(transmission.header, transmission.text, transmission.icon)

    def CloseTransmission(self, *args):
        self.Cleanup()

    def StopWarpIndication(self):
        if self.delayedTransmission:
            self.ShowTransmission(self.delayedTransmission)
            self.delayedTransmission = None

    def OnIncomingAgentMessage(self, agentID, message):
        self.ShowAgentAlert(agentID, message)

    def ShowAgentAlert(self, agentID, message):
        windowID = 'agentalert_%s' % agentID
        wnd = AgentTransmissionWindow.GetIfOpen(windowID=windowID)
        if wnd and not wnd.destroyed:
            wnd.LoadWnd(agentID, message)
        else:
            AgentTransmissionWindow.Open(windowID=windowID, agentID=agentID, message=message)


class Telecom(Window):
    __guid__ = 'form.Telecom'
    default_windowID = 'telecom'
    default_scope = uiconst.SCOPE_INFLIGHT
    default_width = 400
    default_height = 400
    default_minSize = (360, 240)

    def ApplyAttributes(self, attributes):
        super(Telecom, self).ApplyAttributes(attributes)
        self.isDockWnd = 0
        transmission = attributes.transmission
        caption = getattr(transmission, 'caption', None) or localization.GetByLabel('UI/Generic/Information')
        hasDungeonWarp = getattr(transmission, 'hasDungeonWarp', False)
        try:
            self.isEscalation = transmission.rec.rec.pathStep
        except AttributeError:
            self.isEscalation = False

        self.sr.header = eveLabel.EveCaptionMedium(parent=self.content, align=uiconst.TOTOP)
        scrollCont = ScrollContainer(parent=self.content, padTop=8)
        self.label = eveLabel.EveLabelMedium(parent=scrollCont, align=uiconst.TOTOP)
        self.SetCaption(caption)
        if not hasDungeonWarp:
            self.DefineButtons(uiconst.OK, okLabel=localization.GetByLabel('UI/Generic/Close'), okFunc=self.Close)
        else:
            self.sr.instanceID = getattr(transmission.rec.rec, 'instanceID', 0)
            self.sr.solarSystemID = getattr(transmission.rec.rec, 'solarSystemID', 0)
            if self.sr.solarSystemID == session.solarsystemid:
                okLabel = localization.GetByLabel('UI/Commands/WarpTo')
                okFunc = self.WarpToEPLocation
            else:
                inFleet = bool(session.fleetid)
                isLeader = sm.GetService('menu').ImFleetLeaderOrCommander()
                if inFleet and isLeader:
                    okLabel = localization.GetByLabel('UI/Fleet/FleetBroadcast/Commands/BroadcastTravelTo')
                    okFunc = self.SetFleetDestination
                else:
                    okLabel = localization.GetByLabel('UI/Inflight/SetDestination')
                    okFunc = self.SetDestination
            if self.sr.instanceID and self.sr.solarSystemID:
                self.DefineButtons(uiconst.OKCANCEL, okLabel=okLabel, okFunc=okFunc, cancelLabel=localization.GetByLabel('UI/Generic/Close'), cancelFunc=self.Close)
            else:
                self.DefineButtons(uiconst.OK, okLabel=localization.GetByLabel('UI/Generic/Close'), okFunc=self.Close)

    def SetDestination(self, *args):
        sm.StartService('starmap').SetWaypoint(self.sr.solarSystemID, clearOtherWaypoints=True)
        self.Close()

    def SetFleetDestination(self, *args):
        sol = self.sr.solarSystemID
        sm.StartService('fleet').SendBroadcast_TravelTo(sol)
        self.SetDestination()

    def WarpToEPLocation(self, *args):
        if self.sr.instanceID is not None:
            sm.GetService('michelle').CmdWarpToStuff('epinstance', self.sr.instanceID)
        self.Close()

    def ShowMessage(self, header, text, icon):
        self.sr.header.text = header
        if icon:
            try:
                icon = GetIconFile(int(icon.split(' ', 1)[0]))
                self.icon = icon
            except:
                self.icon = 'res:/ui/Texture/WindowIcons/satellite.png'
                log.LogWarn('Failed adding ', icon, ' as icon in transmission window')
                sys.exc_clear()

        else:
            self.icon = 'res:/ui/Texture/WindowIcons/satellite.png'
        if self.isEscalation:
            text = u'{text}\n{link}'.format(text=text, link=evelink.local_service_link('AgencyOpenAndShow', localization.GetByLabel('UI/Agency/OpenAgencyForDetails'), contentGroupID=contentGroupConst.contentGroupEscalations))
        self.label.SetText(text)
