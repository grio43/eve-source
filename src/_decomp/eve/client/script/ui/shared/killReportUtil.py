#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\killReportUtil.py
from carbon.common.script.util.commonutils import StripTags
from carbonui import uiconst
from carbonui.uicore import uicore
SCHEME_KILL_REPORT = 'killReport'

def CleanKillMail(killMailText):
    ret = killMailText
    if '<localized' in ret:
        ret = ret.replace('*</localized>', '</localized>')
        ret = StripTags(ret, stripOnly=['localized'])
    return ret.replace('<br>', '\r\n').replace('<t>', '   ')


def OpenKillReport(kill, *args):
    if uicore.uilib.Key(uiconst.VK_SHIFT):
        windowID = 'KillReport_%i' % kill.killID
    else:
        windowID = 'KillReportWnd'
    from eve.client.script.ui.shared.killReport import KillReportWnd
    wnd = KillReportWnd.GetIfOpen(windowID)
    if wnd:
        wnd.LoadInfo(killmail=kill)
        wnd.Maximize()
    else:
        KillReportWnd.Open(create=1, killmail=kill, windowID=windowID)


def register_link_handlers(registry):
    registry.register(scheme=SCHEME_KILL_REPORT, handler=handle_kill_report_link, hint='UI/Corporations/Wars/Killmails/KillReport')


def handle_kill_report_link(url):
    kill_id, hash_value = parse_kill_report_url(url)
    kill = sm.RemoteSvc('warStatisticMgr').GetKillMail(kill_id, hash_value)
    if kill is not None:
        OpenKillReport(kill)


def parse_kill_report_url(url):
    _, kill_id, hash_value = url.split(':')
    return (int(kill_id), hash_value)


def format_kill_report_url(kill_id, hash_value):
    return u'{}:{}:{}'.format(SCHEME_KILL_REPORT, kill_id, hash_value)
