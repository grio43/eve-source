#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\messageboxWithTimeout.py
import uthread
import blue
import log
from carbonui import uiconst
from eve.client.script.ui import eveColor
from eve.client.script.ui.control import eveLabel
from localization import GetByLabel
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.messagebox import MessageBox
from carbon.common.lib.const import SEC as SECONDS
from gametime import GetSimTime
DEFAULT_TIMEOUT = 20
MIN_TIMEOUT = 5
MAX_TIMEOUT = 60

class MessageBoxWithTimeout(MessageBox):
    __guid__ = 'form.MessageBoxWithTimeout'
    __nonpersistvars__ = ['suppress']

    def ApplyAttributes(self, attributes):
        MessageBox.ApplyAttributes(self, attributes)
        self.timeout = attributes.get('timeout', DEFAULT_TIMEOUT)
        if not MIN_TIMEOUT <= self.timeout < MAX_TIMEOUT:
            self.timeout = max(min(self.timeout, MAX_TIMEOUT), MIN_TIMEOUT)
            log.LogWarn('MessageBoxWithTimeout: %s specifies an unreasonable timeout value of %d. Capping it to %d.' % (self.msgKey, attributes.get('timeout', DEFAULT_TIMEOUT), self.timeout))

    def Execute(self, text, title, buttons, icon, suppText, customicon = None, height = None, default = None, modal = True, okLabel = None, cancelLabel = None, isClosable = True):
        MessageBox.Execute(self, text, title, buttons, icon, suppText, customicon, height, default, modal, okLabel, cancelLabel)
        self.timeoutLabel = eveLabel.EveLabelMedium(parent=self.sr.main, idx=1, align=uiconst.TOBOTTOM, text='', color=eveColor.DANGER_RED, padding=8)
        self.height += 20

    def ShowModal(self):
        uthread.new(self._TimeoutThread)
        return MessageBox.ShowModal(self)

    def _TimeoutThread(self):
        now = GetSimTime()
        timeoutAt = now + self.timeout * SECONDS
        while now < timeoutAt:
            self.timeoutLabel.SetText(GetByLabel('UI/Generic/OperationWillBeCanceledIn', time=timeoutAt - now))
            blue.pyos.synchro.SleepSim(450)
            now = GetSimTime()

        if self.IsOpen():
            self.CloseByUser()
