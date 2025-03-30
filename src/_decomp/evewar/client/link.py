#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evewar\client\link.py
import evelink
import localization
SCHEME_WAR_NEGOTIATION = 'warNegotiation'
SCHEME_WAR_REPORT = 'warReport'

def register_link_handlers(registry):
    registry.register(SCHEME_WAR_NEGOTIATION, handle_war_negotiation_link, hint='UI/Corporations/Wars/SurrenderOffer')
    registry.register(SCHEME_WAR_REPORT, handle_war_report_link, hint='UI/Corporations/Wars/OpenWarReport')


def handle_war_negotiation_link(url):
    from eve.client.script.ui.shared.neocom.corporation.war.warWindows import WarSurrenderWnd
    war_negotiation_id = parse_war_negotiation_url(url)
    warNegotiation = sm.GetService('war').GetWarNegotiation(war_negotiation_id)
    WarSurrenderWnd.Open(warNegotiationID=war_negotiation_id, isRequest=False, warNegotiation=warNegotiation)


def handle_war_report_link(url):
    from eve.client.script.ui.shared.neocom.corporation.war.warReport import WarReportWnd
    war_id = parse_war_report_url(url)
    WarReportWnd.CloseIfOpen()
    WarReportWnd.Open(create=1, warID=war_id)


def parse_war_negotiation_url(url):
    war_negotiation_id = int(url.split(':')[1])
    return war_negotiation_id


def parse_war_report_url(url):
    war_id = int(url.split(':')[1])
    return war_id


def war_report_link(war_id, attacker_id, defender_id):
    attacker_name = cfg.eveowners.Get(attacker_id).name
    defender_name = cfg.eveowners.Get(defender_id).name
    text = localization.GetByLabel('UI/Corporations/Wars/WarReportLink', attackerName=attacker_name, defenderName=defender_name)
    return evelink.Link(url=format_war_report_url(war_id), text=text)


def format_war_report_url(war_id):
    return u'{}:{}'.format(SCHEME_WAR_REPORT, war_id)
