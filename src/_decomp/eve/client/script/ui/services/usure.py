#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\usure.py
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_SERVICE
from carbonui import uiconst
from locks import TempLock
from eve.client.script.ui.shared.messageboxWithTimeout import MessageBoxWithTimeout
DEFAULT_TIMEOUT = 20

class YouSureBoutThat(Service):
    __guid__ = 'svc.usure'
    __dependencies__ = []
    __notifyevents__ = []
    __startupdependencies__ = ['settings']
    __exportedcalls__ = {'ConfirmGeneric': [ROLE_SERVICE]}

    def __init__(self):
        super(self.__class__, self).__init__()
        self.suppressed = settings.user.suppress

    def ConfirmGeneric(self, msgKey, msgTimeout = DEFAULT_TIMEOUT, **msgKwArgs):
        response = self.suppressed.Get('suppress.' + msgKey, None)
        if response is None:
            suppress = cfg.GetSuppressValueForMessage(msgKey, msgKwArgs)
            if suppress not in (None, uiconst.ID_YES, uiconst.ID_NO):
                self.LogWarn('ConfirmGeneric expects suppressible messages to specify a value to suppress on. %s uses %s which is not supported by this function.' % (msgKey, suppress))
            with TempLock('%s_%s' % (msgKey, str(msgKwArgs))):
                msgBoxParams = {'timeout': msgTimeout}
                response = eve.Message(msgKey, msgKwArgs, uiconst.YESNO, suppress=suppress, customMsgBox=(MessageBoxWithTimeout, msgBoxParams))
        return response == uiconst.ID_YES
