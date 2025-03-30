#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\sys\eveinit.py
import stackless
import sys
import traceback
import types
import blue
import localization
import log
import uthread
from carbonui import uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.control.message import ShowQuickMessage
from eveexceptions import UserError
from eveprefs import prefs
from stringutil import strx
from typeutils import metas

class Eve:
    __metaclass__ = metas.Singleton

    def __init__(self):
        self.session = None
        self.chooseWndMenu = None
        blue.pyos.exceptionHandler = self.ExceptionHandler

    def Message(self, *args, **kw):
        if args and args[0] == 'IgnoreToTop':
            return
        if not getattr(uicore, 'desktop', None):
            return
        curr = stackless.getcurrent()
        if curr.is_main:
            uthread.new(self._Message, *args, **kw).context = 'eve.Message'
        else:
            return self._Message(*args, **kw)

    def _Message(self, msgkey, params = None, buttons = None, suppress = None, default = None, modal = True, customMsgBox = None):
        if type(msgkey) not in types.StringTypes:
            raise RuntimeError('Invalid argument, msgkey must be a string', msgkey)
        msg = cfg.GetMessage(msgkey, params, onNotFound='raise')
        if msg.text and settings.public.generic.Get('showMessageId', 0):
            rawMsg = cfg.GetMessage(msgkey, None, onDictMissing=None)
            if rawMsg.text:
                newMsgText = '{message}<br>------------------<br>[Message ID: <b>{messageKey}</b>]<br>{rawMessage}'
                rawMsg.text = rawMsg.text.replace('<', '&lt;').replace('>', '&gt;')
                msg.text = newMsgText.format(message=msg.text, messageKey=msgkey, rawMessage=rawMsg.text)
        if uicore.desktop is None:
            try:
                log.general.Log("Some dude is trying to send a message with eve.Message before  it's ready.  %s,%s,%s,%s" % (strx(msgkey),
                 strx(params),
                 strx(buttons),
                 strx(suppress)), log.LGERR)
                blue.os.ShowErrorMessageBox(msg.title, msg.text)
            except:
                sys.exc_clear()

            return
        if buttons is not None and msg.type not in ('warning', 'question', 'fatal'):
            raise RuntimeError('Cannot override buttons except in warning, question and fatal messages', msg, buttons, msg.type)
        supp = settings.user.suppress.Get('suppress.' + msgkey, None)
        if supp is not None:
            if suppress is not None:
                return suppress
            message_suppression = cfg.GetSuppressValueForMessage(msgkey, params)
            if message_suppression is True or message_suppression is not False and supp == message_suppression:
                return supp
        if not msg.suppress and suppress is not None:
            txt = 'eve.Message() called with the suppress parameter without a suppression specified in the message itself - %s / %s'
            log.general.Log(txt % (msgkey, params), log.LGWARN)
        elif suppress in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
            txt = 'eve.Message() called with the suppress parameter of ID_CLOSE or ID_CANCEL which is not supported suppression - %s / %s'
            log.general.Log(txt % (msgkey, params), log.LGWARN)
        sm.GetService('audio').AudioMessage(msg, msgKey=msgkey)
        sm.ScatterEvent('OnEveMessage', msgkey, params)
        if uicore.uilib:
            gameui = sm.GetService('gameui')
        else:
            gameui = None
        if msg.type in ('hint', 'notify', 'warning', 'question', 'infomodal', 'info'):
            sm.GetService('logger').AddMessage(msg)
        if msg.type in ('info', 'infomodal', 'warning', 'question', 'error', 'fatal', 'windowhelp'):
            supptext = None
            if msg.suppress:
                if buttons in [None, uiconst.OK]:
                    supptext = localization.GetByLabel('/Carbon/UI/Common/DoNotShowAgain')
                else:
                    supptext = localization.GetByLabel('/Carbon/UI/Common/DoNotAskAgain')
            if gameui:
                if buttons is None:
                    buttons = uiconst.OK
                if msg.icon == '':
                    msg.icon = None
                icon = msg.icon
                if icon is None:
                    icon = {'info': uiconst.INFO,
                     'infomodal': uiconst.INFO,
                     'warning': uiconst.WARNING,
                     'question': uiconst.QUESTION,
                     'error': uiconst.ERROR,
                     'fatal': uiconst.FATAL}.get(msg.type, uiconst.ERROR)
                customicon = None
                if params:
                    customicon = params.get('customicon', None)
                msgtitle = msg.title
                if msg.title is None:
                    msgTitles = {'info': localization.GetByLabel('UI/Common/Information'),
                     'infomodal': localization.GetByLabel('UI/Common/Information'),
                     'warning': localization.GetByLabel('UI/Generic/Warning'),
                     'question': localization.GetByLabel('UI/Common/Question'),
                     'error': localization.GetByLabel('UI/Common/Error'),
                     'fatal': localization.GetByLabel('UI/Common/Fatal')}
                    msgtitle = msgTitles.get(msg.type, localization.GetByLabel('UI/Common/Information'))
                ret, supp = gameui.MessageBox(msg.text, msgtitle, buttons, icon, supptext, customicon, default=default, modal=modal, msgkey=msgkey, messageData=params, customMsgBox=customMsgBox, isClosable=msg.closable)
                if supp and ret not in (uiconst.ID_CLOSE, uiconst.ID_CANCEL):
                    if suppress is None:
                        suppress = cfg.GetSuppressValueForMessage(msgkey, params)
                    if ret == suppress or suppress is True:
                        settings.user.suppress.Set('suppress.' + msgkey, ret)
                        sm.GetService('settings').SaveSettings()
                return ret
        else:
            if msg.type in ('notify', 'hint', 'event'):
                return ShowQuickMessage(msg.text)
            if msg.type in ('audio',):
                pass
            elif msg.type == '':
                if msgkey in ('BrowseHtml', 'BrowseIGB'):
                    sm.GetService('ui').Browse(msgkey, params)
                elif msgkey == 'OwnerPopup':
                    sm.StartService('gameui').MessageBox(params.get('body', ''), params.get('title', ''), uiconst.OK, uiconst.INFO)
                else:
                    return msg
            else:
                raise RuntimeError('Unknown message type', msg)

    def IsDestroyedWindow(self, tb):
        try:
            argnames = tb.tb_frame.f_code.co_varnames[:tb.tb_frame.f_code.co_argcount + 1]
            locals_ = tb.tb_frame.f_locals.copy()
            if argnames:
                for each in argnames:
                    try:
                        theStr = repr(locals_[each])
                        if theStr and theStr.find('destroyed=1') != -1:
                            return theStr
                    except:
                        sys.exc_clear()

            return ''
        except AttributeError:
            sys.exc_clear()
            return ''

    def ExceptionHandler(self, exctype, exc, tb, message = ''):
        try:
            if isinstance(exc, UserError):
                self.Message(exc.msg, exc.dict)
            else:
                toMsgWindow = prefs.GetValue('showExceptions', 0)
                if isinstance(exc, RuntimeError) and len(exc.args) and exc.args[0] == 'ErrMessageNotFound':
                    if toMsgWindow:
                        self.Message('ErrMessageNotFound', exc.args[1])
                else:
                    if isinstance(exc, AttributeError):
                        deadWindowCheck = self.IsDestroyedWindow(tb)
                        if deadWindowCheck:
                            name = ''
                            try:
                                nameIdx = deadWindowCheck.find('name=')
                                if nameIdx != -1:
                                    nameIdx += 6
                                    endNameIdx = deadWindowCheck[nameIdx:].find('",')
                                    if endNameIdx != -1:
                                        name = deadWindowCheck[nameIdx:nameIdx + endNameIdx]
                            except:
                                sys.exc_clear()

                            log.LogWarn('Message sent to dead window:', name)
                            exctype = exc = tb = None
                            return
                    if getattr(exc, 'msg', None) == 'DisconnectedFromServer':
                        toMsgWindow = 0
                    severity = log.LGERR
                    extraText = '; caught by eve.ExceptionHandler'
                    if message:
                        extraText += '\nContext info: ' + message
                    return log.LogException(extraText=extraText, toMsgWindow=toMsgWindow, exctype=exctype, exc=exc, tb=tb, severity=severity)
        except:
            exctype = exc = tb = None
            traceback.print_exc()
            sys.exc_clear()
