#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\disconnectNotice.py
import uthread2
from carbon.client.script.sys import appUtils
from carbon.common.script.net.ExceptionMappingGPCS import TRANSPORT_CLOSED_MESSAGES
import carbonui.primitives as uiprimitives
import localization
import carbonui.const as uiconst
import bluepy
from eve.client.script.ui.shared.messagebox import MessageBox
from carbonui.uicore import uicore
from monolithsentry.geoip2_tags import get_geoip_tags, COUNTRY_KEY, ASN_KEY, IP_ADDRESS_KEY
from clientevents.client.messenger import ClientEventsMessenger

class NoLog(object):

    def LogInfo(self):
        pass

    def LogError(self):
        pass


class DisconnectNotice(object):

    def __init__(self, logProvider):
        if logProvider is None:
            logProvider = NoLog()
        self.logProvider = logProvider
        self._eventMessenger = ClientEventsMessenger(sm.GetService('publicGatewaySvc'))

    def OnDisconnect(self, reason = 0, msg = '', title = None, icon = None):
        if msg in TRANSPORT_CLOSED_MESSAGES:
            msg_type = msg
            msg = localization.GetByLabel(TRANSPORT_CLOSED_MESSAGES[msg])
        else:
            self.logProvider.LogError('GameUI::OnDisconnect - Unknown msg=', msg)
            msg_type = 'No reason given'
            msg = None
        self.logProvider.LogInfo('Received OnDisconnect with reason=', reason, ' and msg=', msg)
        user_id = session.userid if session else None
        geo_tags = get_geoip_tags()
        country_code = geo_tags.get(COUNTRY_KEY, '') if geo_tags else ''
        asn = geo_tags.get(ASN_KEY, 0) if geo_tags else 0
        ip_address = geo_tags.get(IP_ADDRESS_KEY, None) if geo_tags else None
        self._eventMessenger.connection_lost(user_id, msg_type, country_code, asn, ip_address)
        if reason in (0, 1):
            self.logProvider.LogError('GameUI::OnDisconnect', reason, msg)
            self.ShowDisconnectNotice(notice=msg, title=title, icon=icon)

    def ShowDisconnectNotice(self, notice = None, title = None, icon = None):
        notice = notice or localization.GetByLabel('UI/Shared/GenericConnectionLost')
        msgbox = MessageBox.Open(windowID='DisconnectNotice', parent=uicore.desktop, idx=0)
        msgbox.MakeUnResizeable()
        msgbox.MakeUnKillable()
        canReboot = appUtils.CanReboot()
        okLabel = localization.GetByLabel('UI/Commands/CmdRestart') if canReboot else localization.GetByLabel('UI/Commands/CmdQuit')
        buttons = uiconst.OKCANCEL if canReboot else uiconst.OK
        cancelLabel = localization.GetByLabel('UI/Commands/CmdQuit') if canReboot else None
        msgbox.Execute(notice, title or self._GetWindowTitle(), buttons, icon or self._GetWindowIcon(), None, okLabel=okLabel, cancelLabel=cancelLabel)
        uicore.layer.hint.display = False
        blackOut = uiprimitives.fill.Fill(parent=uicore.layer.modal, color=(0, 0, 0, 0), idx=1)
        uicore.animations.MorphScalar(blackOut, 'opacity', startVal=0, endVal=0.75, duration=1.0)
        uthread2.Sleep(0.1)
        msgbox.SetText(notice)
        modalResult = msgbox.ShowModal()
        if canReboot and modalResult == uiconst.ID_OK:
            appUtils.Reboot('connection lost')
        else:
            bluepy.Terminate(0, 'User requesting close after client disconnect')

    def _GetWindowIcon(self):
        return uiconst.INFO

    def _GetWindowTitle(self):
        return localization.GetByLabel('UI/Shared/ConnectionLost')
