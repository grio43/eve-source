#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\quasarHijackWnd.py
import logging
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from httplib import BAD_REQUEST, UNAUTHORIZED, FORBIDDEN, NOT_FOUND, METHOD_NOT_ALLOWED, CONFLICT, PRECONDITION_FAILED, UNSUPPORTED_MEDIA_TYPE, INTERNAL_SERVER_ERROR
from stackless_response_router.exceptions import TimeoutException, UnpackException
LATENCY_OPTIONS = (0.0, 0.1, 0.5, 1.0, 5.0, 10.0)
ERROR_OPTIONS = [('None', None),
 ('TimeoutException', TimeoutException),
 ('UnpackException', UnpackException),
 ('Bad Request (400)', BAD_REQUEST),
 ('Unauthorized (401)', UNAUTHORIZED),
 ('Forbidden (403)', FORBIDDEN),
 ('Not Found (404)', NOT_FOUND),
 ('Method Not Allowed (405)', METHOD_NOT_ALLOWED),
 ('Conflict (409)', CONFLICT),
 ('Precondition Failed (412)', PRECONDITION_FAILED),
 ('Unsupported Media Type (415)', UNSUPPORTED_MEDIA_TYPE),
 ('Internal Error (500)', INTERNAL_SERVER_ERROR)]
logger = logging.getLogger(__name__)

class BaseQuasarHijackWindow(Window):
    default_fixedWidth = 300
    default_fixedHeight = 240
    hasWindowIcon = False
    TOOL_NAME = ''
    TOOL_TITLE = ''
    TOOL_DESCRIPTION = ''

    def ApplyAttributes(self, attributes):
        super(BaseQuasarHijackWindow, self).ApplyAttributes(attributes)
        self.LoadData()
        self.Layout()

    def LoadData(self):
        self.is_enabled = False
        self.error = None
        self.latency = None

    def Layout(self):
        self.mainCont = Container(name='mainCont', parent=self.sr.main, padding=10)
        self._LayoutSendRequestCheckbox()
        self._LayoutSendRequestContainer()

    def _LayoutSendRequestCheckbox(self):
        self.sendRequestCheckbox = Checkbox(parent=self.mainCont, checked=self.is_enabled, configName='%s_sendRequest' % self.TOOL_NAME, text=self.TOOL_TITLE, hint=self.TOOL_DESCRIPTION, callback=self.OnHijackSendRequestCheckbox, align=uiconst.TOTOP)

    def _LayoutSendRequestContainer(self):
        self.sendRequestCont = ContainerAutoSize(name='sendRequestCont', parent=self.mainCont, align=uiconst.TOTOP, bgColor=(1, 1, 1, 0.04), padTop=4)
        self._LayoutLatency()
        self._LayoutError()
        self.UpdateSendRequestContVisibility()

    def _LayoutLatency(self):
        self.latencyCombo = Combo(name='latencyCombo', parent=self.sendRequestCont, align=uiconst.TOTOP, prefskey='%s_latencyCombo' % self.TOOL_NAME, label='Latency (sec)', options=[ (str(val), val) for val in LATENCY_OPTIONS ], callback=self.OnLatencyCombo, padding=(4, 24, 4, 0))
        if self.latency:
            self.latencyCombo.SetValue(self.latency)

    def _LayoutError(self):
        self.errorCombo = Combo(name='errorCombo', parent=self.sendRequestCont, align=uiconst.TOTOP, prefskey='%s_errorCombo' % self.TOOL_NAME, label='Force Error', options=ERROR_OPTIONS, callback=self.OnErrorCombo, padding=(4, 24, 4, 10))
        if self.error:
            self.errorCombo.SetValue(self.error)

    def UpdateSendRequestContVisibility(self):
        isChecked = self.sendRequestCheckbox.GetValue()
        self.sendRequestCont.pickState = isChecked
        self.sendRequestCont.opacity = 1.0 if isChecked else 0.3

    def OnErrorCombo(self, *args):
        self.error = self.errorCombo.GetValue()
        self._UpdateHijacking()

    def OnLatencyCombo(self, *args):
        self.latency = self.latencyCombo.GetValue()
        self._UpdateHijacking()

    def OnHijackSendRequestCheckbox(self, *args):
        self._UpdateHijacking()
        self.UpdateSendRequestContVisibility()

    def _UpdateHijacking(self):
        if self.sendRequestCheckbox.GetValue():
            self.is_enabled = True
            self.EnableHijack()
        else:
            self.is_enabled = False
            self.DisableHijack()

    def DisableHijack(self):
        raise NotImplementedError('Must implement DisableHijack in derived class')

    def EnableHijack(self):
        raise NotImplementedError('Must implement EnableHijack in derived class')


class ServerRequestHijackWindow(BaseQuasarHijackWindow):
    TOOL_NAME = 'ServerRequestHijacker'
    TOOL_TITLE = "Hijack 'send_request()'"
    TOOL_DESCRIPTION = "Hijack and interfere with any requests sent through 'serviceGatewayMgr.send_request()' so we can introduce artificial lag and/or errors.\n\nPersisted only for this server node's session."
    default_windowID = 'serverRequestHijackWindow'
    default_caption = 'Server Request Hijacker'

    def LoadData(self):
        self.is_enabled = sm.RemoteSvc('serviceGatewayMgr').qa_is_hijack_mode_enabled()
        self.error = None
        self.latency = None

    def DisableHijack(self):
        logger.info('Quasar hijack mode DISABLED (eve)')
        sm.RemoteSvc('serviceGatewayMgr').qa_disable_hijack_mode()

    def EnableHijack(self):
        logger.info('Quasar hijack mode ENABLED (eve): error=%s, latency=%s', self.error, self.latency)
        sm.RemoteSvc('serviceGatewayMgr').qa_enable_hijack_mode(self.error, self.latency)


class ClientRequestHijackWindow(BaseQuasarHijackWindow):
    TOOL_NAME = 'ClientRequestHijacker'
    TOOL_TITLE = "Hijack 'send_request()'"
    TOOL_DESCRIPTION = "Hijack and interfere with any requests sent through 'publicGatewaySvc.send_request()' so we can introduce artificial lag and/or errors.\n\nPersisted via user settings."
    default_windowID = 'clientRequestHijackWindow'
    default_caption = 'Client Request Hijacker'

    def LoadData(self):
        self.is_enabled, self.error, self.latency = sm.GetService('publicGatewaySvc').qa_get_hijack_mode_data()

    def DisableHijack(self):
        logger.info('Quasar hijack mode DISABLED (eve_public)')
        sm.GetService('publicGatewaySvc').qa_disable_hijack_mode()

    def EnableHijack(self):
        logger.info('Quasar hijack mode ENABLED (eve_public): error=%s, latency=%s', self.error, self.latency)
        sm.GetService('publicGatewaySvc').qa_enable_hijack_mode(self.error, self.latency)
