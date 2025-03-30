#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\zhReport\reportSvc.py
import log
from carbon.common.script.sys import service
from carbon.common.script.util.format import FmtDate
from eve.client.script.ui.shared.zhReport.reportWindow import ReportWindow, TYPE_EXPLOIT_ABUSE, TYPE_GAMBLING, TYPE_INAPPROPRIATE_CHARACTER_NAME, TYPE_INAPPROPRIATE_LANGUAGE, TYPE_MACRO_USE, TYPE_OFFENSIVE_MAIL, TYPE_OTHER, TYPE_QUESTIONABLE_TRANSACTION

class ReportService(service.Service):
    _exportedcalls = {}
    __guid__ = 'svc.reportClientSvc'
    __servicename__ = 'ReportSystemService'
    __displayname__ = 'Report System Client Service'

    def Report(self, charID, *args):
        wnd = ReportWindow.Open()
        wnd.SetReportedCharacter(charID)

    def SubmitReportInformation(self, charID, type, comments):
        if type == TYPE_INAPPROPRIATE_LANGUAGE:
            focus_window = sm.GetService('focus').GetFocusChannel()
            chat_time = ''
            chat_channel = sm.GetService('XmppChat').GetDisplayName(focus_window.GetChannelId())
            chat_content = ''
            log.LogInfo('reporting chat %s, %s' % (chat_time, chat_channel))
            for sender, text, timestamp, colorkey in focus_window.messages:
                if sender == charID:
                    chat_content += '[%s] %s> %s\n' % (FmtDate(timestamp), cfg.eveowners.Get(sender).name, text)
                    chat_time = FmtDate(timestamp)

            if chat_content == '':
                return 'No chat content to report'
            else:
                sm.RemoteSvc('ingamereport').report_inappropriate_language(charID, comments, chat_time, chat_channel, chat_content)
                return 'Report Success'
        elif type == TYPE_OFFENSIVE_MAIL:
            sm.RemoteSvc('ingamereport').report_offensive_mail(charID, comments)
        elif type == TYPE_MACRO_USE:
            sm.RemoteSvc('ingamereport').report_macro_use(charID, comments)
        elif type == TYPE_QUESTIONABLE_TRANSACTION:
            sm.RemoteSvc('ingamereport').report_questionable_transaction(charID, comments)
        elif type == TYPE_INAPPROPRIATE_CHARACTER_NAME:
            sm.RemoteSvc('ingamereport').report_inappropriate_character_name(charID, comments)
        elif type == TYPE_EXPLOIT_ABUSE:
            sm.RemoteSvc('ingamereport').report_exploit_abuse(charID, comments)
        elif type == TYPE_GAMBLING:
            sm.RemoteSvc('ingamereport').report_gambling(charID, comments)
        elif type == TYPE_OTHER:
            sm.RemoteSvc('ingamereport').report_other(charID, comments)
        return 'Report Success'
